import logging
import json
import os
from typing import Dict, Any, Optional, List 

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

LEAD_FILE_PATH = "captured_lead_data.json"

load_dotenv(".env.local")

# ✅ NEW COMPANY
COMPANY_NAME = "ExampleCorp"

# ✅ FAQ CONTENT FOR THE NEW COMPANY
FAQ_CONTENT = {
    "what_it_does": "ExampleCorp is a leading provider of cloud solutions, AI-driven analytics, and enterprise software tools.",
    "target_audience": "ExampleCorp serves businesses of all sizes that need cloud infrastructure, AI insights, and productivity solutions.",
    "pricing_basics": "Pricing depends on the solution and business size. Cloud subscriptions are tiered; AI tools have per-seat licensing; enterprise software is custom-quoted.",
    "key_benefits": "ExampleCorp provides scalable cloud solutions, AI-powered analytics, seamless integrations, and robust support.",
    "free_tier": "ExampleCorp offers a free tier for some cloud tools and AI trial solutions for evaluation purposes."
}

LEAD_FIELDS = ["Name", "Company", "Email", "Role", "Use case", "Team size", "Timeline"]

class SDRSessionState:
    def __init__(self):
        self.lead_data: Dict[str, Any] = {field: None for field in LEAD_FIELDS}
        self.current_question: Optional[str] = None
        self.conversation_transcript: List[str] = []
        self.faq_hits: List[str] = []

    def get_missing_lead_fields(self) -> List[str]:
        return [field for field, value in self.lead_data.items() if value is None]


class SDRScriptAgent(Agent):
    def __init__(self, userdata: SDRSessionState) -> None:
        self.state = userdata
        
        instructions = f"""You are the Sales Development Representative (SDR) for {COMPANY_NAME}.
Your primary goal is to qualify the visitor, answer their questions based *ONLY* on the provided FAQ, and capture lead information.

**SDR Persona Rules:**
1.  **Greet Warmly:** Start by greeting the user and asking what brought them here.
2.  **Use FAQ:** If the user asks a product, pricing, or company question, use the `answer_faq` tool. **DO NOT invent details.**
3.  **Capture Lead Data:** Interweave lead questions naturally during the conversation using the `capture_lead_data` tool. Ask for missing fields one by one.
4.  **End Call:** When the user indicates they are done (e.g., "that's all," "thanks," "bye"), use the `end_call_summary` tool immediately to finish the session.

**Available FAQ Keys:** {', '.join(FAQ_CONTENT.keys())}
"""
        super().__init__(instructions=instructions)

    @function_tool
    async def answer_faq(self, context: RunContext, topic: str) -> str:
        topic = topic.lower().replace(' ', '_').replace('-', '_')
        
        for key, answer in FAQ_CONTENT.items():
            if topic in key or key in topic:
                context.userdata.faq_hits.append(key)
                return f"Regarding {COMPANY_NAME}, {answer}"

        return f"I'm sorry, I don't have an approved answer for that in my {COMPANY_NAME} FAQ. Would you like to ask something else?"

    @function_tool
    async def capture_lead_data(self, context: RunContext, field_name: Optional[str] = None, value: Optional[str] = None) -> str:
        if field_name and value:
            field_name = field_name.title()
            if field_name in LEAD_FIELDS:
                context.userdata.lead_data[field_name] = value
                logger.info(f"Captured lead data: {field_name}={value}")
        
        missing = context.userdata.get_missing_lead_fields()
        
        if not missing:
            return "Thanks! I have all your details. How else can I help you today?"

        next_field = missing[0]
        context.userdata.current_question = next_field

        prompts = {
            "Name": "Before we proceed, may I have your name?",
            "Email": "Great! What email address can we use to follow up with you?",
            "Company": "Which company are you currently associated with?",
            "Role": "What is your role or designation at your company?",
            "Use case": f"What {COMPANY_NAME} product or solution are you most interested in?",
            "Team size": "Approximately how many team members will be using this solution?",
            "Timeline": "When are you planning to make a purchase or begin implementation?"
        }

        return prompts.get(next_field, "Thanks! Let me note that down.")

    @function_tool
    async def end_call_summary(self, context: RunContext) -> str:
        lead_data = context.userdata.lead_data
        
        name = lead_data.get("Name", "the visitor")
        company = lead_data.get("Company", "your organization")
        use_case = lead_data.get("Use case", "your interest in ExampleCorp solutions")
        timeline = lead_data.get("Timeline", "an unspecified timeline")

        summary_text = (
            f"Thank you, {name}. To summarize our conversation: you're interested in {use_case}, "
            f"representing {company}, and your estimated timeline is {timeline}. "
            f"One of our {COMPANY_NAME} specialists will get in touch with you soon."
        )

        try:
            if os.path.exists(LEAD_FILE_PATH):
                with open(LEAD_FILE_PATH, 'r') as f:
                    try:
                        leads = json.load(f)
                    except json.JSONDecodeError:
                        leads = []
            else:
                leads = []
            
            leads.append(lead_data)
            
            with open(LEAD_FILE_PATH, 'w') as f:
                json.dump(leads, f, indent=4)
            
            logger.info(f"Saved {COMPANY_NAME} lead data to {LEAD_FILE_PATH}")

        except Exception as e:
            logger.error(f"Failed to save {COMPANY_NAME} lead: {e}")
            summary_text += " (Note: Data saving issue occurred.)"

        return summary_text + f" Thank you for speaking with {COMPANY_NAME}!"

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    session_state = SDRSessionState()
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    session = AgentSession(
        userdata=session_state,
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew", 
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    await session.start(
        agent=SDRScriptAgent(userdata=session_state),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
