from dataclasses import dataclass, field
from typing import Dict, List, Optional, Type, TypeVar, Any
import json
import os
from datetime import datetime

from livekit.agents.llm import ChatContext, ChatMessage

T = TypeVar('T', bound='BaseAgent')

@dataclass
class AgentConfig:
    """Base configuration for all agents"""
    name: str
    system_prompt: str
    voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Default voice
    model: str = "gpt-4-turbo-preview"

class BaseAgent:
    """Base class for all voice agents"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.chat_ctx = ChatContext()
        self.chat_ctx.messages = [
            ChatMessage(role="system", content=config.system_prompt)
        ]
    
    async def process_message(self, text: str) -> str:
        """Process incoming message and return response"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def _save_conversation(self, data: Dict[str, Any], filename: str) -> None:
        """Save conversation data to a JSON file"""
        data['timestamp'] = datetime.now().isoformat()
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving conversation data: {e}")
    
    def _load_conversation(self, filename: str) -> Dict[str, Any]:
        """Load conversation data from a JSON file"""
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading conversation data: {e}")
        return {}
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent"""
        return {
            "name": self.config.name,
            "voice_id": self.config.voice_id,
            "model": self.config.model
        }
