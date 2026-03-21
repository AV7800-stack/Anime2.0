import requests
import json
from typing import Dict, Any
import os

class StoryGenerator:
    def __init__(self):
        # Pollinations.ai - 100% Free, No API Key Required
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
            
            response = requests.get(story_url, timeout=30)
            
            if response.status_code == 200:
                story = response.text
            else:
                # Fallback story
                story = f"""Anime {genre} Story: {prompt}

Once upon a time in a world of anime, a great adventure began. The characters faced many challenges and discovered their true strength. Through courage and friendship, they overcame all obstacles and found happiness. This is their story...

The journey was filled with excitement, danger, and moments of pure joy. Each character grew and learned something valuable about themselves and their friends. In the end, they realized that the real treasure was the bonds they formed along the way.

And so, their adventure continued, with new challenges and new friendships waiting just beyond the horizon."""
            
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
                "error": str(e),
                "fallback_story": f"Anime {genre} Story: {prompt}\n\nIn a world filled with magic and adventure, our heroes embark on an incredible journey. Through trials and triumphs, they discover the true meaning of friendship and courage."
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
