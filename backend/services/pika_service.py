import os
import requests
import asyncio
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class PikaService:
    def __init__(self):
        self.api_key = os.getenv("PIKA_API_KEY")
        self.base_url = "https://api.pika.art/v1"
        
        if self.api_key:
            self.pika_available = True
            print("✅ Pika API configured for video generation")
        else:
            self.pika_available = False
            print("⚠️ Pika API key not configured")
    
    async def generate_video(self, prompt: str, style: str = "anime", duration: int = 10) -> Dict[str, Any]:
        """
        Generate video using Pika API
        """
        if not self.pika_available:
            return {
                "success": False,
                "error": "Pika API not configured",
                "pika_available": False
            }
        
        try:
            # Enhance prompt for anime style
            enhanced_prompt = self._enhance_prompt_for_anime(prompt, style)
            
            # Prepare the request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "prompt": enhanced_prompt,
                "model": "pika-1.5",  # Latest Pika model
                "duration": duration,
                "aspect_ratio": "16:9",
                "quality": "high",
                "style": style if style in ["anime", "cinematic", "artistic"] else "anime"
            }
            
            # Submit video generation request
            response = requests.post(
                f"{self.base_url}/generate",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                video_id = result.get("id")
                
                # Poll for completion
                video_url = await self._poll_video_completion(video_id)
                
                if video_url:
                    return {
                        "success": True,
                        "video_url": video_url,
                        "video_id": video_id,
                        "style": style,
                        "duration": duration,
                        "pika_available": True,
                        "model": "pika-1.5"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Video generation timed out or failed",
                        "pika_available": True
                    }
            else:
                return {
                    "success": False,
                    "error": f"Pika API error: {response.status_code} - {response.text}",
                    "pika_available": True
                }
                
        except Exception as e:
            print(f"❌ Pika video generation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "pika_available": True
            }
    
    async def _poll_video_completion(self, video_id: str, max_wait_time: int = 300) -> Optional[str]:
        """
        Poll for video completion
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < max_wait_time:
            try:
                response = requests.get(
                    f"{self.base_url}/status/{video_id}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    status = response.json()
                    video_status = status.get("status")
                    
                    if video_status == "completed":
                        return status.get("video_url")
                    elif video_status == "failed":
                        print(f"❌ Video generation failed: {status.get('error')}")
                        return None
                    elif video_status == "processing":
                        # Still processing, wait and poll again
                        await asyncio.sleep(5)
                    else:
                        await asyncio.sleep(5)
                else:
                    print(f"❌ Status check error: {response.status_code}")
                    await asyncio.sleep(5)
                    
            except Exception as e:
                print(f"❌ Polling error: {e}")
                await asyncio.sleep(5)
        
        print("❌ Video generation timed out")
        return None
    
    def _enhance_prompt_for_anime(self, prompt: str, style: str) -> str:
        """Enhance prompt for Pika anime video generation"""
        style_modifiers = {
            "anime": "anime style, Japanese animation, manga art, vibrant colors",
            "cinematic": "cinematic anime, high quality, detailed animation",
            "artistic": "artistic anime, beautiful animation, stylized",
            "ghibli": "Studio Ghibli style, Hayao Miyazaki aesthetic",
            "shonen": "shonen anime, action-packed, dynamic",
            "shojo": "shojo anime, elegant, flowing animation"
        }
        
        base_modifier = style_modifiers.get(style, style_modifiers["anime"])
        
        # Add anime-specific enhancements
        anime_enhancements = [
            "smooth animation",
            "detailed character design",
            "dynamic camera work",
            "vivid color palette",
            "professional anime quality",
            "fluid motion",
            "expressive characters"
        ]
        
        enhanced_prompt = f"{prompt}, {base_modifier}, {', '.join(anime_enhancements)}"
        
        return enhanced_prompt
    
    async def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """Get information about a generated video"""
        if not self.pika_available:
            return {"error": "Pika API not configured"}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.base_url}/status/{video_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API error: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}

# Global instance
pika_service = PikaService()
