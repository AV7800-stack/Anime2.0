import openai
import os
from typing import Dict, Any
from dotenv import load_dotenv
from .cloudinary_service import cloudinary_service

load_dotenv()

class ImageGenerator:
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def generate_image(self, prompt: str, style: str = "anime", size: str = "1024x1024") -> Dict[str, Any]:
        """
        Generate an anime image based on the given prompt and upload to Cloudinary.
        """
        try:
            # Enhance the prompt for anime style
            enhanced_prompt = self._enhance_prompt_for_anime(prompt, style)
            
            # Generate the image
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size=size,
                quality="standard",
                n=1,
                style="vivid"
            )
            
            image_url = response.data[0].url
            revised_prompt = response.data[0].revised_prompt
            
            # Upload to Cloudinary for permanent storage
            cloudinary_result = await cloudinary_service.upload_image_from_url(
                image_url, 
                folder="anime-characters"
            )
            
            if not cloudinary_result["success"]:
                print("⚠️ Failed to upload to Cloudinary, using original URL")
                final_image_url = image_url
                cloudinary_data = {}
            else:
                final_image_url = cloudinary_result["url"]
                cloudinary_data = {
                    "cloudinary_public_id": cloudinary_result["public_id"],
                    "cloudinary_width": cloudinary_result["width"],
                    "cloudinary_height": cloudinary_result["height"],
                    "cloudinary_size": cloudinary_result["size"]
                }
            
            # Generate a character description
            character_description = await self._generate_character_description(prompt)
            
            return {
                "type": "image",
                "title": self._generate_title(prompt),
                "content": character_description,
                "image_url": final_image_url,
                "original_image_url": image_url,
                "revised_prompt": revised_prompt,
                "style": style,
                "size": size,
                "cloudinary_data": cloudinary_data,
                "generated_at": str(openai.datetime.datetime.utcnow())
            }
            
        except Exception as e:
            print(f"❌ Error generating image: {e}")
            raise Exception(f"Failed to generate image: {str(e)}")
    
    def _enhance_prompt_for_anime(self, prompt: str, style: str) -> str:
        """Enhance the prompt to generate better anime-style images"""
        style_modifiers = {
            "anime": "anime style, manga art, Japanese animation style",
            "studio_ghibli": "Studio Ghibli style, Hayao Miyazaki art style",
            "shonen": "shonen anime style, action-oriented, dynamic",
            "shojo": "shojo anime style, romantic, delicate features",
            "seinen": "seinen anime style, mature, detailed"
        }
        
        base_prompt = f"{prompt}, {style_modifiers.get(style, style_modifiers['anime'])}"
        
        # Add quality and detail modifiers
        quality_modifiers = [
            "high quality, masterpiece",
            "vibrant colors, clean line art",
            "professional anime illustration",
            "detailed character design",
            "dynamic pose, expressive emotions",
            "cinematic lighting, dramatic atmosphere"
        ]
        
        enhanced_prompt = f"{base_prompt}, {', '.join(quality_modifiers)}"
        
        return enhanced_prompt
    
    async def _generate_character_description(self, prompt: str) -> str:
        """Generate a detailed character description"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an anime character designer. Write detailed, vivid descriptions of anime characters based on prompts."
                    },
                    {
                        "role": "user",
                        "content": f"Write a detailed anime character description based on this prompt: {prompt}. Include appearance, personality, and background story."
                    }
                ],
                max_tokens=300,
                temperature=0.8
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Error generating character description: {e}")
            return f"A unique anime character inspired by: {prompt}"
    
    def _generate_title(self, prompt: str) -> str:
        """Generate a title for the character"""
        words = prompt.split()[:4]
        base_title = " ".join(words).title()
        return f"Character: {base_title}"
