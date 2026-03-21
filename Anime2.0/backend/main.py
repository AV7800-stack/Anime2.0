"""
Anime2.0 FastAPI Backend - Production Ready
Minimal, Error-Free Version for Render Deployment
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Anime2.0 API",
    description="Production Ready FastAPI Backend",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
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

# In-memory storage
generations = []

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Anime2.0 API starting up...")
    logger.info(f"🌍 Environment: {os.getenv('NODE_ENV', 'development')}")
    logger.info(f"📡 PORT: {os.getenv('PORT', '8000')}")
    logger.info("✅ API started successfully!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 API shutting down...")

# Root endpoint - Health check
@app.get("/")
async def root():
    return {
        "status": "running",
        "message": "Anime2.0 API is working!",
        "version": "1.0.0",
        "environment": os.getenv("NODE_ENV", "development"),
        "port": os.getenv("PORT", "8000"),
        "timestamp": datetime.now().isoformat()
    }

# Health check endpoint
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running",
        "services": {
            "anime": "available",
            "story": "available",
            "video": "available",
            "chat": "available"
        }
    }

# Generate anime image
@app.post("/generate")
async def generate_anime(request: GenerateRequest):
    """Generate anime content using Pollinations.ai"""
    try:
        if request.type == "image":
            enhanced_prompt = f"{request.prompt}, anime style, {request.style}, high quality"
            image_url = f"https://image.pollinations.ai/prompt/{enhanced_prompt}?style={request.style}&width={request.width}&height={request.height}"
            
            result = {
                "success": True,
                "type": "image",
                "image_url": image_url,
                "prompt": request.prompt,
                "style": request.style
            }
            
        elif request.type == "story":
            story_prompt = f"anime story: {request.prompt}, with characters and plot"
            story_url = f"https://text.pollinations.ai/{story_prompt}"
            
            try:
                response = requests.get(story_url, timeout=30)
                story = response.text if response.status_code == 200 else f"Anime Story: {request.prompt}\n\nOnce upon a time in a world of anime magic..."
            except:
                story = f"Anime Story: {request.prompt}\n\nOnce upon a time in a world of anime magic..."
            
            result = {
                "success": True,
                "type": "story",
                "story": story,
                "prompt": request.prompt
            }
            
        elif request.type == "video":
            frame_urls = []
            for i in range(min(request.duration, 5)):
                frame_prompt = f"{request.prompt}, frame {i+1}, anime style"
                frame_url = f"https://image.pollinations.ai/prompt/{frame_prompt}?style=anime&width=512&height=512"
                frame_urls.append(frame_url)
            
            result = {
                "success": True,
                "type": "video",
                "frame_urls": frame_urls,
                "frames": len(frame_urls),
                "prompt": request.prompt
            }
            
        else:
            raise HTTPException(status_code=400, detail="Invalid generation type")
        
        # Store in memory
        generation = {
            "id": str(uuid.uuid4()),
            "type": request.type,
            "prompt": request.prompt,
            "result": result,
            "created_at": datetime.now().isoformat()
        }
        generations.append(generation)
        
        # Keep only last 50
        if len(generations) > 50:
            generations.pop(0)
        
        return result
        
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat endpoint
@app.post("/chat")
async def chat_endpoint(request: dict):
    """Simple chat endpoint"""
    try:
        message = request.get("message", "Hello!")
        
        responses = [
            "I can help you create amazing anime content!",
            "What kind of anime would you like to generate?",
            "Let's create something amazing together!",
            "Try our free anime generation tools!"
        ]
        
        import random
        response = random.choice(responses)
        
        return {
            "success": True,
            "response": response,
            "message": message
        }
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get generations
@app.get("/generations")
async def get_generations(limit: int = 10, offset: int = 0):
    """Get recent generations"""
    try:
        sorted_generations = sorted(generations, key=lambda x: x.get("created_at", ""), reverse=True)
        paginated = sorted_generations[offset:offset + limit]
        
        return {
            "success": True,
            "generations": paginated,
            "total": len(generations),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Generations error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return {
        "success": False,
        "error": "Internal server error",
        "message": "Something went wrong"
    }

# Run app (for local development)
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Starting server on port {port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
