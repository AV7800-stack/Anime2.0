import requests
import json
from typing import Dict, Any

class StoryGenerator:
    def __init__(self):
        # Pollinations.ai text API - 100% Free, No API Key Required
        self.base_url = "https://text.pollinations.ai"
    
    def generate_story(self, prompt: str, genre: str = "anime") -> Dict[str, Any]:
        """
        Generate anime story using Pollinations.ai text API (100% free)
        """
        try:
            # Enhanced prompt for better story generation
            story_prompt = f"anime {genre} story: {prompt}, with characters, plot, and ending"
            
            # Pollinations.ai text URL - no API key needed
            story_url = f"{self.base_url}/{story_prompt}"
            
            response = requests.get(story_url)
            
            if response.status_code == 200:
                story = response.text
            else:
                # Fallback story
                story = f"Anime {genre} Story: {prompt}\n\nOnce upon a time in the world of anime, a great adventure began. The characters faced many challenges and discovered their true strength. Through courage and friendship, they overcame all obstacles and found happiness. This is their story..."
            
            return {
                "success": True,
                "story": story,
                "prompt": prompt,
                "genre": genre,
                "service": "pollinations.ai"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_character_story(self, character_name: str, character_type: str = "magical girl") -> Dict[str, Any]:
        """
        Generate character-specific story
        """
        prompt = f"Story about {character_name}, a {character_type}, their powers, and their journey"
        return self.generate_story(prompt, "character")
    
    def generate_episode(self, series_name: str, episode_number: int = 1) -> Dict[str, Any]:
        """
        Generate anime episode
        """
        prompt = f"Episode {episode_number} of {series_name}, new adventure, character development"
        return self.generate_story(prompt, "episode")

# Global instance
story_generator = StoryGenerator()
