from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import json
import re
from datetime import datetime

from livekit import rtc
from livekit.agents import (
    JobContext,
    JobRequest,
    WorkerOptions,
    cli,
)
from livekit.agents.llm import ChatContext, ChatMessage
from livekit.agents.voice_assistant import VoiceAssistantAgent
from livekit.plugins import silero, whisper, openai, elevenlabs

from .base_agent import BaseAgent, AgentConfig

WELLNESS_LOG_FILE = "wellness_log.json"

class WellnessConfig(AgentConfig):
    """Configuration for the Wellness Agent"""
    def __init__(self):
        system_prompt = """
        You are a supportive health and wellness companion. Your role is to help users reflect on their 
        well-being and set positive intentions for their day. Be warm, empathetic, and encouraging.

        ## Conversation Flow
        1. Greet the user and ask about their current mood and energy level
        2. Ask about 1-3 specific objectives or goals for the day
        3. Offer simple, practical wellness suggestions based on their responses
        4. Summarize the check-in and confirm with the user
        5. End with an encouraging note

        ## Guidelines
        - Keep responses concise and conversational (1-2 sentences max)
        - Ask one question at a time
        - Validate the user's feelings without judgment
        - Suggest small, actionable wellness tips
        - Never provide medical advice or make diagnoses
        - Help break down larger goals into smaller, manageable steps
        - Be positive and encouraging
        - If the user shares something concerning, suggest they speak with a healthcare professional
        """
        super().__init__(
            name="Wellness Companion",
            system_prompt=system_prompt,
            voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice
            model="gpt-4-turbo-preview"
        )

class WellnessAgent(BaseAgent):
    """A voice agent focused on health and wellness check-ins"""
    
    def __init__(self):
        config = WellnessConfig()
        super().__init__(config)
        self.va = VoiceAssistantAgent(
            chat_ctx=self.chat_ctx,
            vad=silero.VAD(),
            stt=whisper.STT(),
            tts=elevenlabs.TTS(
                model="eleven_multilingual_v2",
                voice_id=self.config.voice_id,
            ),
            llm=openai.LLM(model=self.config.model),
        )
        
        # Load previous wellness data
        self.wellness_data = self._load_wellness_data()
    
    def _load_wellness_data(self) -> List[Dict]:
        """Load wellness data from JSON file or create new if doesn't exist"""
        return self._load_conversation(WELLNESS_LOG_FILE) or []
    
    def _save_wellness_data(self, entry: Dict) -> None:
        """Save new wellness entry to JSON file"""
        self._save_conversation(entry, WELLNESS_LOG_FILE)
    
    def _get_previous_context(self) -> str:
        """Get context from previous check-ins"""
        if not self.wellness_data:
            return ""
            
        last_entry = self.wellness_data[-1]
        context = []
        
        if 'mood' in last_entry:
            context.append(f"Last time, you mentioned feeling {last_entry['mood']}.")
        
        if 'objectives' in last_entry and last_entry['objectives']:
            context.append(f"Your objectives were: {', '.join(last_entry['objectives'])}.")
        
        if 'summary' in last_entry:
            context.append(f"We discussed: {last_entry['summary']}")
        
        return " ".join(context) if context else ""
    
    async def start(self, ctx: JobContext) -> None:
        """Handle a new voice session"""
        await ctx.recording.started.wait()
        
        # Initialize conversation data
        current_data = {
            'timestamp': datetime.now().isoformat(),
            'mood': None,
            'energy': None,
            'objectives': [],
            'summary': ''
        }
        
        # Add context from previous check-ins
        prev_context = self._get_previous_context()
        if prev_context:
            self.va.chat_ctx.messages.append(
                ChatMessage(role="system", 
                          name="context",
                          text=f"Previous check-in context: {prev_context}")
            )
        
        # Start the voice assistant
        await self.va.start(
            ctx.room,
            ctx.participant,
            playback_id=ctx.job_id,
        )
        
        # Process the conversation
        conversation_history = []
        
        try:
            while True:
                event = await self.va.next_event()
                
                if isinstance(event, VoiceAssistantAgent.Events.LLMResponse):
                    conversation_history.append({"role": "assistant", "content": event.text})
                    
                    # Extract data from user's previous response
                    if len(conversation_history) >= 2 and conversation_history[-2]["role"] == "user":
                        user_text = conversation_history[-2]["content"].lower()
                        
                        if not current_data['mood'] and any(q in event.text.lower() for q in ["how are you feeling", "how do you feel"]):
                            current_data['mood'] = self._extract_mood(user_text)
                        
                        if not current_data['energy'] and any(q in event.text.lower() for q in ["energy level", "how's your energy"]):
                            current_data['energy'] = self._extract_energy_level(user_text)
                        
                        if any(q in event.text.lower() for q in ["objectives", "goals"]):
                            current_data['objectives'] = self._extract_objectives(user_text)
                    
                    # Save data when agent summarizes
                    if any(phrase in event.text.lower() for phrase in ["to recap", "does this sound right"]):
                        current_data['summary'] = self._generate_summary(conversation_history)
                        self._save_wellness_data(current_data)
                
                elif isinstance(event, VoiceAssistantAgent.Events.UserUtterance):
                    conversation_history.append({"role": "user", "content": event.text})
                        
        except Exception as e:
            print(f"Error in wellness session: {e}")
        finally:
            if not current_data.get('summary') and conversation_history:
                current_data['summary'] = self._generate_summary(conversation_history)
                self._save_wellness_data(current_data)
            
            await self.va.shutdown()
    
    def _extract_mood(self, text: str) -> str:
        """Extract mood from user's text"""
        mood_keywords = {
            'happy': ['happy', 'good', 'great', 'wonderful', 'amazing'],
            'neutral': ['ok', 'okay', 'fine', 'alright', 'so-so'],
            'sad': ['sad', 'down', 'low', 'unhappy', 'depressed'],
            'anxious': ['anxious', 'stressed', 'worried', 'nervous'],
            'angry': ['angry', 'frustrated', 'mad', 'irritated']
        }
        
        text_lower = text.lower()
        for mood, keywords in mood_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return mood
        return 'neutral'
    
    def _extract_energy_level(self, text: str) -> int:
        """Extract energy level from 1-5 from user's text"""
        numbers = re.findall(r'\b[1-5]\b', text)
        if numbers:
            return int(numbers[0])
            
        if any(word in text.lower() for word in ['high', 'energetic']):
            return 5
        elif any(word in text.lower() for word in ['good', 'well']):
            return 4
        elif any(word in text.lower() for word in ['ok', 'okay']):
            return 3
        elif any(word in text.lower() for word in ['low', 'tired']):
            return 2
        elif any(word in text.lower() for word in ['exhausted', 'terrible']):
            return 1
            
        return 3  # Default to neutral
    
    def _extract_objectives(self, text: str) -> List[str]:
        """Extract objectives/goals from user's text"""
        objectives = []
        for obj in re.split(r'[,\n]', text):
            obj = obj.strip()
            if obj and len(obj) > 3:
                objectives.append(obj)
        return objectives[:3]
    
    def _generate_summary(self, conversation: List[Dict[str, str]]) -> str:
        """Generate a summary of the conversation"""
        user_messages = [msg['content'] for msg in conversation if msg['role'] == 'user']
        return user_messages[0][:150] + "..." if user_messages else "Wellness check-in completed."
