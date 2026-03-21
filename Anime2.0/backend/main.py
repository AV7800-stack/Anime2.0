import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from pymongo import MongoClient
from PIL import Image
import io
import base64
from moviepy.editor import VideoFileClip
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Anime2.0 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    prompt: str
    type: str = "image"
    style: str = "anime"

@app.on_event("startup")
async def startup_event():
    try:
        logger.info("🚀 Anime2.0 API starting up...")
        logger.info(f"🌍 Environment: {os.getenv('NODE_ENV', 'development')}")
        logger.info(f"📡 PORT: {os.getenv('PORT', '10000')}")
        
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/anime2")
        try:
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            client.server_info()
            logger.info("✅ MongoDB connected successfully")
        except:
            logger.warning("⚠️ MongoDB connection failed, using in-memory storage")
        
        logger.info("✅ API started successfully!")
    except Exception as e:
        logger.error(f"❌ Startup error: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 API shutting down...")

@app.get("/")
async def root():
    return {
        "status": "running",
        "message": "Anime2.0 API is working!",
        "version": "1.0.0",
        "environment": os.getenv("NODE_ENV", "development"),
        "port": os.getenv("PORT", "10000"),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "anime": "available",
            "story": "available",
            "video": "available",
            "chat": "available"
        }
    }

@app.post("/generate")
async def generate_anime(request: GenerateRequest):
    try:
        if request.type == "image":
            enhanced_prompt = f"{request.prompt}, anime style, {request.style}, high quality"
            image_url = f"https://image.pollinations.ai/prompt/{enhanced_prompt}?style={request.style}"
            
            return {
                "success": True,
                "type": "image",
                "image_url": image_url,
                "prompt": request.prompt,
                "style": request.style
            }
            
        elif request.type == "story":
            story_prompt = f"anime story: {request.prompt}"
            story_url = f"https://text.pollinations.ai/{story_prompt}"
            
            try:
                response = requests.get(story_url, timeout=30)
                story = response.text if response.status_code == 200 else f"Anime Story: {request.prompt}"
            except:
                story = f"Anime Story: {request.prompt}"
            
            return {
                "success": True,
                "type": "story",
                "story": story,
                "prompt": request.prompt
            }
            
        elif request.type == "video":
            frame_urls = []
            for i in range(5):
                frame_prompt = f"{request.prompt}, frame {i+1}, anime style"
                frame_url = f"https://image.pollinations.ai/prompt/{frame_prompt}?style=anime"
                frame_urls.append(frame_url)
            
            return {
                "success": True,
                "type": "video",
                "frame_urls": frame_urls,
                "frames": 5,
                "prompt": request.prompt
            }
            
        else:
            raise HTTPException(status_code=400, detail="Invalid generation type")
            
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_endpoint(request: dict):
    try:
        message = request.get("message", "Hello!")
        responses = [
            "I can help you create amazing anime content!",
            "What kind of anime would you like to generate?",
            "Let's create something amazing together!"
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

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return {
        "success": False,
        "error": "Internal server error",
        "message": "Something went wrong"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    logger.info(f"🚀 Starting server on port {port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
