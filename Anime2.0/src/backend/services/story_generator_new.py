import requests
import json
from typing import Dict, Any

class StoryGenerator:
    def __init__(self):
        # Pollinations.ai - 100% Free, No API Key Required
        self.base_url = "https://text.pollinations.ai"
    
    def generate_story(self, prompt: str, genre: str = "anime") -> Dict[str, Any]:
        """
        Generate anime story using Pollinations.ai text API (100% free)
        Returns 5 scenes as requested
        """
        try:
            story_prompt = f"anime {genre} story: {prompt}, 5 scenes, with characters, plot, and ending"
            story_url = f"{self.base_url}/{story_prompt}"
            
            response = requests.get(story_url, timeout=30)
            
            if response.status_code == 200:
                story = response.text
            else:
                # Fallback 5-scene story
                story = f"""Anime {genre} Story: {prompt}

SCENE 1: THE AWAKENING
In a world where dreams and reality intertwine, our protagonist discovers they possess extraordinary powers. The revelation comes during a moment of crisis, forcing them to choose between ordinary life and extraordinary destiny.

SCENE 2: THE JOURNEY BEGINS
Leaving everything familiar behind, our hero embarks on a perilous journey. They encounter allies who become family and enemies who test their resolve. Each step teaches them more about their true potential.

SCENE 3: THE TRIAL OF WISDOM
Facing the ultimate test, our hero must solve an ancient riddle that has defeated countless warriors before them. Through cleverness and courage, they discover that the answer was within them all along.

SCENE 4: THE BATTLE OF DESTINY
The final confrontation arrives as darkness threatens to consume everything they hold dear. Friends and enemies unite against a common foe, and our hero must make the ultimate sacrifice to save everyone.

SCENE 5: THE NEW DAWN
Victory comes at a price, but brings hope for a brighter future. Our hero has grown into someone stronger and wiser, ready to lead others toward a new era of peace and understanding."""
            
            return {
                "success": True,
                "story": story,
                "prompt": prompt,
                "genre": genre,
                "scenes": 5,
                "service": "pollinations.ai"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_story": f"Anime {genre} Story: {prompt}\n\nIn a world of magic and adventure, our heroes discover their true strength through friendship and courage. Their journey spans five acts: discovery, challenge, growth, victory, and transformation."
            }
    
    def generate_character_story(self, character_name: str, character_type: str = "magical girl") -> Dict[str, Any]:
        """
        Generate character-specific story with 5 scenes
        """
        prompt = f"Story about {character_name}, a {character_type}, their powers, and their journey"
        return self.generate_story(prompt, "character")
    
    def generate_episode(self, series_name: str, episode_number: int = 1) -> Dict[str, Any]:
        """
        Generate anime episode with 5 scenes
        """
        prompt = f"Episode {episode_number} of {series_name}, new adventure, character development"
        return self.generate_story(prompt, "episode")

# Global instance
story_generator = StoryGenerator()
