import openai
import replicate
import asyncio
import os
import uuid
import requests
import logging
import json
import random
from typing import List, Dict
from app.core.config import settings
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip, vfx, ColorClip
from PIL import Image
import numpy as np
import io

logger = logging.getLogger(__name__)
openai.api_key = settings.OPENAI_API_KEY

# Self-healing retry decorator
def self_healing_api(retries=3, fallback_value=None):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"API Error in {func.__name__} (Attempt {i+1}/{retries}): {e}")
                    if i == retries - 1:
                        if fallback_value is not None:
                            return fallback_value
                        raise e
                    await asyncio.sleep(2 ** i) # Exponential backoff
        return wrapper
    return decorator

@self_healing_api(fallback_value={"scenes": [{"description": "A beautiful anime landscape", "dialogue": "Welcome to the world of anime."}]})
async def breakdown_script(script: str) -> Dict:
    """Uses GPT-4 to break script into scenes with visual prompts and dialogues."""
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a professional anime director. Convert the user's script into 3 distinct cinematic scenes. For each scene, provide: 1. 'description' (Visual prompt for AI image gen, anime style), 2. 'dialogue' (Short spoken line). Return valid JSON with a 'scenes' list."},
            {"role": "user", "content": script}
        ],
        response_format={ "type": "json_object" }
    )
    return json.loads(response.choices[0].message.content)

@self_healing_api()
async def generate_scene_image(prompt: str) -> str:
    """Generates an anime-style image for a scene."""
    # Try Replicate Anything-v3 (Classic Anime)
    try:
        output = replicate.run(
            "cjwbw/anything-v3-better-vae:09a5805203f4c12da649ec1923bbd0295ce8ed4c8afb6c6b22ebdb12952ee066",
            input={
                "prompt": f"masterpiece, best quality, anime style, highres, {prompt}",
                "negative_prompt": "lowres, text, error, cropped, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, out of frame, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck",
                "width": 768,
                "height": 512
            }
        )
        return output[0] if isinstance(output, list) else output
    except Exception:
        # Fallback to OpenAI DALL-E 3 if Replicate fails
        response = openai.images.generate(
            model="dall-e-3",
            prompt=f"Anime style illustration, high quality, vibrant colors: {prompt}",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url

@self_healing_api()
async def generate_tts(text: str, filename: str) -> str:
    """Generates speech using OpenAI TTS."""
    response = openai.audio.speech.create(
        model="tts-1",
        voice="nova", # Professional anime-style female voice
        input=text
    )
    response.stream_to_file(filename)
    return filename

def zoom_in_effect(clip, zoom_ratio=0.04):
    """Adds a smooth cinematic zoom-in effect to a static image clip."""
    def effect(get_frame, t):
        img = Image.fromarray(get_frame(t))
        base_size = img.size
        new_size = [
            int(base_size[0] * (1 + (zoom_ratio * t / clip.duration))),
            int(base_size[1] * (1 + (zoom_ratio * t / clip.duration)))
        ]
        img = img.resize(new_size, Image.LANCZOS)
        # Crop back to original size (center crop)
        left = (img.size[0] - base_size[0]) / 2
        top = (img.size[1] - base_size[1]) / 2
        right = (img.size[0] + base_size[0]) / 2
        bottom = (img.size[1] + base_size[1]) / 2
        return np.array(img.crop((left, top, right, bottom)))
    return clip.fl(effect)

async def create_anime_video(script: str) -> str:
    """Full pipeline: Script -> Scenes -> Images -> TTS -> Video."""
    job_id = str(uuid.uuid4())
    temp_dir = f"temp_{job_id}"
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # 1. Breakdown
        data = await breakdown_script(script)
        scenes = data.get("scenes", [])[:3] # Limit to 3 scenes for speed
        
        video_clips = []
        
        for i, scene in enumerate(scenes):
            img_url = await generate_scene_image(scene['description'])
            img_path = os.path.join(temp_dir, f"img_{i}.jpg")
            audio_path = os.path.join(temp_dir, f"audio_{i}.mp3")
            
            # Download Image
            img_data = requests.get(img_url).content
            with open(img_path, 'wb') as f:
                with Image.open(io.BytesIO(img_data)) as img:
                    img.convert("RGB").save(f, "JPEG")
            
            # Generate TTS
            await generate_tts(scene['dialogue'], audio_path)
            
            # Create Clip
            audio_clip = AudioFileClip(audio_path)
            # Duration is audio length + 1s buffer
            duration = max(audio_clip.duration + 1.0, 3.0)
            
            img_clip = ImageClip(img_path).set_duration(duration)
            img_clip = zoom_in_effect(img_clip)
            img_clip = img_clip.set_audio(audio_clip)
            
            # Add fade transition
            img_clip = img_clip.crossfadein(0.5).crossfadeout(0.5)
            
            video_clips.append(img_clip)
        
        # Concatenate
        final_clip = concatenate_videoclips(video_clips, method="compose")
        
        # Add Background Music
        bgm_path = "app/assets/bgm.mp3"
        if os.path.exists(bgm_path) and os.path.getsize(bgm_path) > 0:
            bgm = AudioFileClip(bgm_path).volumex(0.1).set_duration(final_clip.duration)
            final_audio = CompositeAudioClip([final_clip.audio, bgm])
            final_clip = final_clip.set_audio(final_audio)
            
        output_filename = f"static/gen_{job_id}.mp4"
        os.makedirs("static", exist_ok=True)
        
        # Write File
        final_clip.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac", threads=4, logger=None)
        
        # Return public URL (Update with your real domain in prod)
        return f"/static/gen_{job_id}.mp4"
        
    finally:
        # Cleanup temp files (keep static output)
        import shutil
        # shutil.rmtree(temp_dir, ignore_errors=True) 
        pass # Keep for debugging if needed, but prod should cleanup
