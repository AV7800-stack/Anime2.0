from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import uvicorn
from datetime import datetime

# Import our modules safely
from database import MongoDB, get_database
from services.story_generator import StoryGenerator
from services.image_generator import ImageGenerator
from services.video_generator import VideoGenerator

# Import cloudinary_service safely to prevent ImportError
try:
    from services.cloudinary_service import cloudinary_service
except ImportError:
    cloudinary_service = None
    print("⚠️ Warning: cloudinary_service could not be imported.")

app = FastAPI(
    title="AI Anime Generator API",
    description="Backend API for generating anime stories, images, and videos (Production Ready)",
    version="1.0.1"
)

# Configure CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Pydantic models (Keep standard)
class StoryRequest(BaseModel):
    prompt: str
    style: Optional[str] = "anime"
    length: Optional[str] = "medium"

class ImageRequest(BaseModel):
    prompt: str
    style: Optional[str] = "anime"
    size: Optional[str] = "1024x1024"

class VideoRequest(BaseModel):
    prompt: str
    style: Optional[str] = "anime"
    duration: Optional[int] = 10

class GenerationResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str

# Dependencies for safe service instantiation
def get_story_generator(): return StoryGenerator()
def get_image_generator(): return ImageGenerator()
def get_video_generator(): return VideoGenerator()

# Render Health Check (Mandatory)
@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "cloudinary": "configured" if os.environ.get("CLOUDINARY_API_KEY") else "not_configured",
            "openai": "configured" if os.environ.get("OPENAI_API_KEY") else "not_configured",
            "mongodb": "configured" if os.environ.get("MONGO_URL") else "not_configured"
        }
    }

# API Test Route
@app.get("/test")
async def test_api():
    return {
        "success": True,
        "message": "AI Anime API is online!",
        "port": os.environ.get("PORT", "8000")
    }

# Main Generation Endpoints
@app.post("/generate-story", response_model=GenerationResponse)
async def generate_story(
    request: StoryRequest,
    db: MongoDB = Depends(get_database),
    story_gen: StoryGenerator = Depends(get_story_generator)
):
    try:
        story_data = await story_gen.generate_story(
            prompt=request.prompt,
            style=request.style,
            length=request.length
        )
        await db.save_generation(type="story", prompt=request.prompt, result=story_data)
        return GenerationResponse(success=True, data=story_data, message="Story generated")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-image", response_model=GenerationResponse)
async def generate_image(
    request: ImageRequest,
    db: MongoDB = Depends(get_database),
    image_gen: ImageGenerator = Depends(get_image_generator)
):
    try:
        image_data = await image_gen.generate_image(
            prompt=request.prompt,
            style=request.style,
            size=request.size
        )
        await db.save_generation(type="image", prompt=request.prompt, result=image_data)
        return GenerationResponse(success=True, data=image_data, message="Image generated")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Entry point for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
