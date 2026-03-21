from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.schemas import GenerateResponse
from app.core.security import verify_token
from app.db.mongodb import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[GenerateResponse])
async def get_history(user: dict = Depends(verify_token)):
    try:
        uid = user.get("uid")
        db = get_db()
        
        cursor = db.history.find({"user_id": uid}).sort("created_at", -1)
        history = await cursor.to_list(length=50)
        
        # Ensure older items don't break if they lack the new fields
        for item in history:
            item.setdefault("story_breakdown", "Legacy generation")
            item.setdefault("scene_prompt", "Legacy generation")
            item.setdefault("character_design", "Legacy generation")
            
        return [GenerateResponse(**item) for item in history]
    except Exception as e:
        logger.error(f"Failed to fetch history: {e}")
        raise HTTPException(status_code=500, detail="Database error during history fetch")