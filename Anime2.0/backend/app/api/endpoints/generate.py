from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.schemas import GenerateRequest, GenerateResponse
from app.core.security import verify_token
from app.db.mongodb import get_db
from app.services.ai import breakdown_script, generate_scene_image, create_anime_video
from datetime import datetime
import uuid
import logging
import os

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest, user: dict = Depends(verify_token)):
    try:
        uid = user.get("uid")
        
        # 1. Self-Healing AI Pipeline
        # Get structured story breakdown
        story_data = await breakdown_script(request.prompt)
        scenes = story_data.get("scenes", [])
        
        story_breakdown = "\n".join([s.get("dialogue", "") for s in scenes])
        scene_prompt = scenes[0].get("description", "Anime scene") if scenes else "Anime scene"
        character_design = "High quality anime character" # Default or extracted
        
        # 2. Generate the actual video file via FFmpeg pipeline
        video_path_relative = await create_anime_video(request.prompt)
        
        # Base URL for static files (in production this should be your Render URL)
        # We use relative URL for easier portability, frontend prepends host
        video_url = video_path_relative 
        
        # Thumbnail is just the first scene's image
        # In a real app, you'd save this to S3/Cloudinary, but here we store it in static/ too if needed.
        # For now, let's just use the first generated scene image URL as a placeholder or regenerate it.
        image_url = await generate_scene_image(scene_prompt)
        
        # 3. Save to MongoDB
        db = get_db()
        doc_id = str(uuid.uuid4())
        
        new_generation = {
            "id": doc_id,
            "user_id": uid,
            "prompt": request.prompt,
            "story_breakdown": story_breakdown,
            "scene_prompt": scene_prompt,
            "character_design": character_design,
            "image_url": image_url,
            "video_url": video_url,
            "created_at": datetime.utcnow()
        }
        
        await db.history.insert_one(new_generation)
        return GenerateResponse(**new_generation)
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
