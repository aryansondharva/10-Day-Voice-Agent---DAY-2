import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Literal
<<<<<<< HEAD

=======
>>>>>>> dbd3176c29c6123b9f99665b77648ee690cb4847
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    tokenize,
    function_tool,
    RunContext,
    ToolError
)
from livekit.plugins import murf, deepgram, google
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("coffee_shop_agent")
load_dotenv(".env.local")

# Define the order state structure
@dataclass
class OrderState:
    drink_type: str = ""
    size: str = ""
    milk: str = ""
    extras: List[str] = None
    name: str = ""

    def is_complete(self) -> bool:
        return all([
            self.drink_type,
            self.size,
            self.milk is not None,  # Can be empty string for black coffee
            self.name
        ])

    def to_dict(self):
        return {
            "drink_type": self.drink_type,
            "size": self.size,
            "milk": self.milk,
            "extras": self.extras if self.extras else [],
            "name": self.name,
            "timestamp": datetime.now().isoformat()
        }


class CoffeeShopAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly coffee shop barista at a cafe called "Brew Haven". 
            Your job is to take customer orders for coffee and other drinks. 
            Always be polite, friendly, and enthusiastic about coffee.
            
            Follow these steps for each order:
            1. Greet the customer and ask for their name
            2. Ask what type of drink they'd like (espresso, latte, cappuccino, americano, etc.)
            3. Ask what size they'd like (small, medium, large)
            4. Ask what kind of milk they prefer (whole, skim, almond, oat, soy, or none for black)
            5. Ask if they'd like any extras (sugar, caramel, vanilla, cinnamon, whipped cream, etc.)
            6. Repeat the order back to them to confirm
            7. Thank them and let them know their order will be ready soon
            
            Keep your responses concise and natural-sounding for a voice conversation.
            Don't list options unless the customer asks for them.
            If the customer doesn't specify something, ask follow-up questions.""",
        )

    @function_tool
    async def update_order(
        self,
        context: RunContext,
        drink_type: Optional[str] = None,
        size: Optional[Literal["small", "medium", "large"]] = None,
        milk: Optional[str] = None,
        extras: Optional[List[str]] = None,
        name: Optional[str] = None
    ) -> str:
        """
        Update the customer's order with the provided details.
        Call this when the customer provides information about their order.
        """
        if not hasattr(context.user_data, 'order_state'):
            context.user_data.order_state = OrderState()
            
        order = context.user_data.order_state
        
        if drink_type:
            order.drink_type = drink_type.lower()
        if size:
            order.size = size.lower()
        if milk is not None:  # Could be empty string for black coffee
            order.milk = milk.lower() if milk else ""
        if extras:
            if order.extras is None:
                order.extras = []
            order.extras.extend([e.lower() for e in extras if e.lower() not in order.extras])
        if name:
            order.name = name.strip()
            
        # If order is complete, save it
        if order.is_complete():
            return await self._save_order(context)
            
        # Otherwise, ask for the next piece of information
        return self._get_next_question(order)
    
    async def _save_order(self, context: RunContext) -> str:
        """Save the completed order to a JSON file and return a confirmation message."""
        order = context.user_data.order_state
        order_dict = order.to_dict()
        
        # Create orders directory if it doesn't exist
        os.makedirs("orders", exist_ok=True)
        
        # Save order to a file
        filename = f"orders/order_{order.name.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}.json"
        with open(filename, 'w') as f:
            json.dump(order_dict, f, indent=2)
        
        # Clear the order state for the next customer
        del context.user_data.order_state
        
        # Return confirmation message
        extras = f" with {', '.join(order.extras)}" if order.extras else ""
        milk = f" with {order.milk} milk" if order.milk else " black"
        return f"Got it, {order.name}! Your {order.size} {order.drink_type}{milk}{extras} will be ready in just a few minutes. Thank you for choosing Brew Haven!"
    
    def _get_next_question(self, order: OrderState) -> str:
        """Determine what question to ask next based on the current order state."""
        if not order.name:
            return "May I have your name for the order, please?"
        elif not order.drink_type:
            return f"What would you like to order today, {order.name}? We have espresso, latte, cappuccino, americano, and more!"
        elif not order.size:
            return f"What size would you like for your {order.drink_type}? We have small, medium, and large."
        elif order.milk is None:  # Explicitly check for None to allow empty string for black coffee
            return "What kind of milk would you like? We have whole, skim, almond, oat, and soy. Or say 'black' for no milk."
        else:
            return "Would you like to add any extras like sugar, caramel, vanilla, or whipped cream?"


def prewarm(proc: JobProcess):
    """Preload any necessary models or resources."""
    proc.userdata["vad"] = MultilingualModel()


async def entrypoint(ctx: JobContext):
    """Entry point for the worker."""
    # Set up logging context
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Initialize the agent with voice pipeline
    session = AgentSession(
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
    
    # Create and set up the coffee shop agent
    agent = CoffeeShopAgent()
    
    # Set up the agent session
    await agent.start(
        ctx.room,
        ctx.chat_ctx,
        stt_ctx=session.stt_ctx,
        tts_ctx=session.tts_ctx,
        turn_detector=session.turn_detector,
        vad=session.vad,
        preemptive_generation=session.preemptive_generation,
    )
    
    # Keep the agent running
    try:
        await agent.wait_for_completion()
    finally:
        await agent.shutdown()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
