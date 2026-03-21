from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    email: EmailStr
    uid: str
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    created_at: datetime

class GenerateRequest(BaseModel):
    prompt: str

class GenerateResponse(BaseModel):
    id: str
    user_id: str
    prompt: str
    story_breakdown: str
    scene_prompt: str
    character_design: str
    image_url: str
    video_url: str
    created_at: datetime