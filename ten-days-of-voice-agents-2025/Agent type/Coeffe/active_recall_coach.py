import json
import logging
import os
import random
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Literal, Tuple

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

# Set up logging
logger = logging.getLogger("active_recall_coach")
load_dotenv(".env.local")

# Define learning modes as an Enum for better type safety and autocompletion
class LearningMode(str, Enum):
    LEARN = "learn"
    QUIZ = "quiz"
    TEACH_BACK = "teach_back"

# Define the concept data structure
@dataclass
class Concept:
    id: str
    title: str
    summary: str
    sample_question: str
    mastery_level: float = 0.0  # 0.0 to 1.0
    last_practiced: Optional[float] = None

@dataclass
class UserState:
    current_concept: Optional[Concept] = None
    learning_mode: Optional[LearningMode] = None
    concept_history: List[Tuple[str, LearningMode]] = field(default_factory=list)
    concept_mastery: Dict[str, float] = field(default_factory=dict)

class ActiveRecallCoach(Agent):
    def __init__(self, concepts_file: str) -> None:
        """
        Initialize the Active Recall Coach with concepts from the provided JSON file.
        """
        super().__init__(
            instructions="""You are an AI tutor that helps students learn through active recall. 
            You have three modes of operation:
            1. Learn mode - Explain concepts clearly and conversationally
            2. Quiz mode - Ask questions to test understanding
            3. Teach-back mode - Have the student explain concepts back to you
            
            Always be encouraging, patient, and adapt to the student's level. 
            Keep explanations clear and concise. In teach-back mode, provide gentle 
            corrections and ask follow-up questions to deepen understanding."""
        )
        
        # Load concepts from JSON file
        self.concepts = self._load_concepts(concepts_file)
        
        # Initialize voices for different modes
        self.voices = {
            LearningMode.LEARN: "en-US-matthew",
            LearningMode.QUIZ: "en-US-alicia",
            LearningMode.TEACH_BACK: "en-US-ken"
        }
    
    def _load_concepts(self, file_path: str) -> List[Concept]:
        """Load concepts from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                concepts_data = json.load(f)
            
            return [
                Concept(
                    id=concept["id"],
                    title=concept["title"],
                    summary=concept["summary"],
                    sample_question=concept["sample_question"]
                )
                for concept in concepts_data
            ]
        except Exception as e:
            logger.error(f"Error loading concepts: {e}")
            return []
    
    def get_concept_by_id(self, concept_id: str) -> Optional[Concept]:
        """Get a concept by its ID."""
        for concept in self.concepts:
            if concept.id == concept_id:
                return concept
        return None
    
    def get_random_concept(self) -> Optional[Concept]:
        """Get a random concept from the available concepts."""
        if not self.concepts:
            return None
        return random.choice(self.concepts)
    
    @function_tool
    async def set_learning_mode(
        self,
        context: RunContext,
        mode: str,
        concept_id: Optional[str] = None
    ) -> str:
        """
        Set the current learning mode and optionally select a concept.
        
        Args:
            mode: The learning mode to set (learn, quiz, or teach_back)
            concept_id: Optional ID of the concept to focus on
            
        Returns:
            Confirmation message about the mode and concept
        """
        # Initialize user state if it doesn't exist
        if not hasattr(context.user_data, 'state'):
            context.user_data.state = UserState()
        
        state = context.user_data.state
        
        # Validate and set the learning mode
        try:
            learning_mode = LearningMode(mode.lower())
        except ValueError:
            return "Invalid learning mode. Please choose from: learn, quiz, or teach_back."
        
        state.learning_mode = learning_mode
        
        # Set the concept if provided, otherwise keep the current one or pick a random one
        if concept_id:
            concept = self.get_concept_by_id(concept_id)
            if not concept:
                return f"Could not find concept with ID: {concept_id}"
            state.current_concept = concept
        elif not state.current_concept:
            state.current_concept = self.get_random_concept()
            if not state.current_concept:
                return "No concepts available. Please check the content file."
        
        # Update concept history
        if state.current_concept:
            state.concept_history.append((state.current_concept.id, learning_mode))
        
        # Get the appropriate response based on the mode
        if learning_mode == LearningMode.LEARN:
            return self._get_learn_response(state.current_concept)
        elif learning_mode == LearningMode.QUIZ:
            return self._get_quiz_response(state.current_concept)
        else:  # TEACH_BACK
            return self._get_teach_back_response(state.current_concept)
    
    def _get_learn_response(self, concept: Concept) -> str:
        """Generate a response for learn mode."""
        return f"Let's learn about {concept.title}. {concept.summary} Would you like me to explain anything in more detail?"
    
    def _get_quiz_response(self, concept: Concept) -> str:
        """Generate a response for quiz mode."""
        return f"Here's a question about {concept.title}: {concept.sample_question} Take your time to think about it, and let me know when you're ready to hear the answer or if you'd like a hint."
    
    def _get_teach_back_response(self, concept: Concept) -> str:
        """Generate a response for teach-back mode."""
        return f"Now it's your turn to teach me about {concept.title}. Please explain it to me as if I'm learning it for the first time. I'll listen carefully and provide feedback afterward."
    
    @function_tool
    async def list_concepts(self, context: RunContext) -> str:
        """List all available concepts with their IDs and titles."""
        if not self.concepts:
            return "No concepts available. Please check the content file."
        
        concept_list = "\n".join(
            f"- {concept.id}: {concept.title}" 
            for concept in self.concepts
        )
        return f"Here are the available concepts:\n{concept_list}\n\nYou can ask to learn about any of these by saying 'I want to learn about [concept_id]'."
    
    @function_tool
    async def provide_feedback(
        self,
        context: RunContext,
        feedback: str,
        is_correct: bool,
        concept_id: str
    ) -> str:
        """
        Provide feedback on a student's answer or explanation.
        
        Args:
            feedback: Specific feedback about the student's response
            is_correct: Whether the student's answer was correct
            concept_id: The ID of the concept being learned
            
        Returns:
            A response acknowledging the feedback
        """
        if not hasattr(context.user_data, 'state') or not context.user_data.state.current_concept:
            return "I'm not sure which concept we're working on. Please select a concept first."
        
        concept = self.get_concept_by_id(concept_id)
        if not concept:
            return f"Could not find concept with ID: {concept_id}"
        
        # Update mastery level based on correctness
        state = context.user_data.state
        if is_correct:
            state.concept_mastery[concept_id] = min(1.0, state.concept_mastery.get(concept_id, 0) + 0.2)
        else:
            state.concept_mastery[concept_id] = max(0.0, state.concept_mastery.get(concept_id, 0) - 0.1)
        
        return feedback

def prewarm(proc: JobProcess):
    """Preload any necessary models or resources."""
    # No specific prewarming needed for this agent
    pass

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
            voice="en-US-matthew",  # Default voice, will be overridden based on mode
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        ),
        preemptive_generation=True,
    )
    
    # Get the path to the concepts file
    concepts_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "shared-data",
        "day4_tutor_content.json"
    )
    
    # Create and set up the active recall coach
    agent = ActiveRecallCoach(concepts_file=concepts_file)
    
    # Set up the agent session
    await agent.start(
        ctx.room,
        ctx.chat_ctx,
        stt_ctx=session.stt_ctx,
        tts_ctx=session.tts_ctx,
        preemptive_generation=session.preemptive_generation,
    )
    
    # Initial greeting
    await agent.chat(
        "Hello! I'm your Active Recall Coach. I can help you learn through three modes:\n"
        "1. Learn mode - I'll explain concepts to you\n"
        "2. Quiz mode - I'll test your knowledge with questions\n"
        "3. Teach-back mode - You'll explain concepts back to me\n\n"
        "You can say things like:\n"
        "- 'Let's learn about variables'\n"
        "- 'Quiz me on loops'\n"
        "- 'I want to teach you about functions'\n"
        "- 'List available concepts'\n\n"
        "What would you like to do first?",
        voice="en-US-matthew"
    )
    
    # Keep the agent running
    try:
        await agent.wait_for_completion()
    finally:
        await agent.shutdown()

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
