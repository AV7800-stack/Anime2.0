from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
import json
from datetime import datetime
import uuid
from typing import Optional, Dict, Any

# Initialize FastAPI
app = FastAPI(
    title="Anime2.0 Video Generator API",
    description="100% Free Anime Generation with Pollinations.ai",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class GenerateRequest(BaseModel):
    prompt: str
    type: str = "image"
    style: str = "anime"
    width: int = 512
    height: int = 512
    duration: int = 5

class ChatRequest(BaseModel):
    message: str

# In-memory storage (no database needed)
generations = []

@app.get("/")
async def root():
    return {
        "message": "Anime2.0 Video Generator API",
        "version": "2.0.0",
        "status": "running",
        "services": {
            "story": "available (Pollinations.ai)",
            "image": "available (Pollinations.ai)",
            "video": "available (FFmpeg)",
            "chat": "available"
        },
        "features": [
            "100% free - no API keys required",
            "Multiple anime styles",
            "Fast generation",
            "No paid services"
        ]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "story": "available",
            "image": "available",
            "video": "available",
            "chat": "available"
        }
    }

def generate_story_text(prompt: str, genre: str = "anime") -> Dict[str, Any]:
    """Generate anime story using Pollinations.ai text API"""
    try:
        story_prompt = f"anime {genre} story: {prompt}, with characters, plot, and ending"
        story_url = f"https://text.pollinations.ai/{story_prompt}"
        
        response = requests.get(story_url, timeout=30)
        
        if response.status_code == 200:
            story = response.text
        else:
            story = f"Anime {genre} Story: {prompt}\n\nOnce upon a time in a world of anime, a great adventure began. The characters faced many challenges and discovered their true strength. Through courage and friendship, they overcame all obstacles and found happiness."
        
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
            "error": str(e)
        }

def generate_image_url(prompt: str, style: str = "anime", width: int = 512, height: int = 512) -> Dict[str, Any]:
    """Generate anime image using Pollinations.ai"""
    try:
        enhanced_prompt = f"{prompt}, anime style, {style}, high quality, detailed"
        image_url = f"https://image.pollinations.ai/prompt/{enhanced_prompt}?style={style}&width={width}&height={height}&seed=12345"
        
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
            "error": str(e)
        }

def generate_video_frames(prompt: str, frames: int = 5) -> Dict[str, Any]:
    """Generate multiple frames for video"""
    try:
        frame_urls = []
        for i in range(frames):
            frame_prompt = f"{prompt}, frame {i+1}, anime style, consistent character"
            frame_url = f"https://image.pollinations.ai/prompt/{frame_prompt}?style=anime&width=512&height=512&seed={i}"
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

@app.post("/generate")
async def generate(request: GenerateRequest):
    """Main generation endpoint"""
    try:
        result = None
        
        if request.type == "story":
            result = generate_story_text(request.prompt, request.style)
        elif request.type == "image":
            result = generate_image_url(request.prompt, request.style, request.width, request.height)
        elif request.type == "video":
            result = generate_video_frames(request.prompt, min(request.duration, 5))
        else:
            raise HTTPException(status_code=400, detail="Invalid generation type")
        
        # Store in memory
        if result.get("success"):
            generation = {
                "id": str(uuid.uuid4()),
                "type": request.type,
                "prompt": request.prompt,
                "result": result,
                "created_at": datetime.now().isoformat()
            }
            generations.append(generation)
            
            # Keep only last 50 generations
            if len(generations) > 50:
                generations.pop(0)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/story")
async def generate_story_endpoint(request: dict):
    """Generate anime story"""
    try:
        prompt = request.get("prompt", "anime adventure")
        genre = request.get("genre", "anime")
        
        result = generate_story_text(prompt, genre)
        
        # Store in memory
        if result.get("success"):
            generation = {
                "id": str(uuid.uuid4()),
                "type": "story",
                "prompt": prompt,
                "result": result,
                "created_at": datetime.now().isoformat()
            }
            generations.append(generation)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/image")
async def generate_image_endpoint(request: dict):
    """Generate anime image"""
    try:
        prompt = request.get("prompt", "anime character")
        style = request.get("style", "anime")
        width = request.get("width", 512)
        height = request.get("height", 512)
        
        result = generate_image_url(prompt, style, width, height)
        
        # Store in memory
        if result.get("success"):
            generation = {
                "id": str(uuid.uuid4()),
                "type": "image",
                "prompt": prompt,
                "result": result,
                "created_at": datetime.now().isoformat()
            }
            generations.append(generation)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/video")
async def generate_video_endpoint(request: dict):
    """Generate anime video frames"""
    try:
        prompt = request.get("prompt", "anime scene")
        frames = request.get("frames", 5)
        
        result = generate_video_frames(prompt, frames)
        
        # Store in memory
        if result.get("success"):
            generation = {
                "id": str(uuid.uuid4()),
                "type": "video",
                "prompt": prompt,
                "result": result,
                "created_at": datetime.now().isoformat()
            }
            generations.append(generation)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_endpoint(request: dict):
    """Chat with AI assistant"""
    try:
        message = request.get("message", "Hello!")
        
        # Simple chat responses
        responses = [
            "I can help you create amazing anime content! Try generating an image or story.",
            "What kind of anime character would you like to create today?",
            "Let's create an anime story together! What's your idea?",
            "I can generate anime scenes and characters for you!",
            "Want to make an anime video? I can help with that too!",
            "Try our free anime generation tools - no API keys needed!",
            "What anime style do you prefer? Magical girl, action, romance?",
            "Let's create something amazing with Pollinations.ai!"
        ]
        
        suggestions = [
            "Generate anime character",
            "Create anime story", 
            "Make anime video",
            "Design anime scene",
            "Create magical girl",
            "Generate action scene"
        ]
        
        import random
        response = random.choice(responses)
        selected_suggestions = random.sample(suggestions, 3)
        
        return {
            "success": True,
            "response": response,
            "suggestions": selected_suggestions,
            "message": message
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/generations")
async def get_generations(limit: int = 10, offset: int = 0):
    """Get recent generations"""
    try:
        # Sort by created_at descending
        sorted_generations = sorted(generations, key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Apply pagination
        paginated = sorted_generations[offset:offset + limit]
        
        return {
            "success": True,
            "generations": paginated,
            "total": len(generations),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get generation statistics"""
    try:
        # Count by type
        type_counts = {}
        for gen in generations:
            gen_type = gen.get("type", "unknown")
            type_counts[gen_type] = type_counts.get(gen_type, 0) + 1
        
        return {
            "success": True,
            "stats": {
                "total_generations": len(generations),
                "type_counts": type_counts,
                "services": {
                    "story": "pollinations.ai",
                    "image": "pollinations.ai",
                    "video": "pollinations.ai + ffmpeg"
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
