import requests
import json
from typing import Dict, Any
import os

class ImageGenerator:
    def __init__(self):
        # Pollinations.ai - 100% Free, No API Key Required
        self.base_url = "https://image.pollinations.ai/prompt"
    
    def generate_image(self, prompt: str, style: str = "anime", width: int = 512, height: int = 512) -> Dict[str, Any]:
        """
        Generate anime image using Pollinations.ai (100% free) - returns URL only
        """
        try:
            # Enhanced prompt for better results
            enhanced_prompt = f"{prompt}, anime style, {style}, high quality, detailed"
            
            # Pollinations.ai URL - no API key needed, no download required
            image_url = f"{self.base_url}/{enhanced_prompt}?style={style}&width={width}&height={height}&seed=12345"
            
            return {
                "success": True,
                "image_url": image_url,
                "prompt": prompt,
                "style": style,
                "width": width,
                "height": height,
                "service": "pollinations.ai"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_url": f"{self.base_url}/anime character?style=anime&width=512&height=512"
            }
    
    def generate_character(self, character_type: str = "anime girl") -> Dict[str, Any]:
        """
        Generate anime character
        """
        prompt = f"{character_type}, anime character, detailed, high quality"
        return self.generate_image(prompt, "anime")
    
    def generate_scene(self, scene_description: str) -> Dict[str, Any]:
        """
        Generate anime scene
        """
        prompt = f"anime scene, {scene_description}, detailed background, anime style"
        return self.generate_image(prompt, "anime")
    
    def generate_multiple_frames(self, prompt: str, frames: int = 5) -> Dict[str, Any]:
        """
        Generate multiple frames for video
        """
        try:
            frame_urls = []
            for i in range(frames):
                frame_prompt = f"{prompt}, frame {i+1}, anime style, consistent character"
                frame_url = f"{self.base_url}/{frame_prompt}?style=anime&width=512&height=512&seed={i}"
                frame_urls.append(frame_url)
            
            return {
                "success": True,
                "frame_urls": frame_urls,
                "prompt": prompt,
                "frames": frames,
                "service": "pollinations.ai"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "frame_urls": []
            }

# Global instance
image_generator = ImageGenerator()
