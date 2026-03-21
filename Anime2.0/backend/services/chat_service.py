import json
from typing import Dict, Any, List
import random

class ChatService:
    def __init__(self):
        self.responses = [
            "I can help you create amazing anime content! Try generating an image or story.",
            "What kind of anime character would you like to create today?",
            "Let's create an anime story together! What's your idea?",
            "I can generate anime scenes and characters for you!",
            "Want to make an anime video? I can help with that too!",
            "Try our free anime generation tools - no API keys needed!",
            "What anime style do you prefer? Magical girl, action, romance?",
            "Let's create something amazing with Pollinations.ai!"
        ]
        
        self.suggestions = [
            "Generate anime character",
            "Create anime story", 
            "Make anime video",
            "Design anime scene",
            "Create magical girl",
            "Generate action scene"
        ]
    
    def chat(self, message: str) -> Dict[str, Any]:
        """
        Simple chat response for anime generation
        """
        try:
            # Check for specific keywords
            message_lower = message.lower()
            
            if "image" in message_lower or "character" in message_lower:
                response = "I can generate anime images for free! Try the image generation feature."
                suggestions = ["Generate anime girl", "Create anime boy", "Design magical girl"]
            elif "story" in message_lower or "narrative" in message_lower:
                response = "Let's create an amazing anime story! What's your story idea?"
                suggestions = ["Create adventure story", "Write romance story", "Make action story"]
            elif "video" in message_lower or "animation" in message_lower:
                response = "I can help create anime videos using image sequences!"
                suggestions = ["Generate character video", "Create scene video", "Make animation"]
            else:
                response = random.choice(self.responses)
                suggestions = random.sample(self.suggestions, 3)
            
            return {
                "success": True,
                "response": response,
                "suggestions": suggestions,
                "message": message
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_help(self) -> Dict[str, Any]:
        """
        Get help information
        """
        return {
            "success": True,
            "help": {
                "image_generation": "Generate anime images for free using Pollinations.ai",
                "story_generation": "Create anime stories with our AI writer",
                "video_generation": "Make anime videos from image sequences",
                "features": [
                    "100% free - no API keys needed",
                    "Multiple anime styles",
                    "Fast generation",
                    "High quality results"
                ]
            }
        }

# Global instance
chat_service = ChatService()
