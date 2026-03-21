import logging
import os
import random
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pymongo import MongoClient

# Modular imports
from app.api.router import api_router
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.models.schemas import GenerateRequest, GenerateResponse

# Initialize Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ANIMEFLIX Production API",
    description="Full-stack Backend for Anime Streaming & AI Generation",
    version="2.0.0"
)

# 1. CORS CONFIGURATION (Full Support for Mobile & Web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. MONGODB INTEGRATION (Robust & Persistent)
MONGO_URL = os.getenv("MONGO_URL") or os.getenv("MONGO_URI")
users_col = None

if MONGO_URL:
    try:
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        client.server_info() # Test connection
        db = client["animeflix"]
        users_col = db["users"]
        logger.info("✅ MongoDB connected successfully to 'animeflix' database")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")

# 3. MODELS
class UserAuth(BaseModel):
    email: str
    password: str

# 4. AUTHENTICATION ENDPOINTS (Root Level for /docs Visibility)
@app.post("/signup", tags=["Authentication"])
async def signup(user: UserAuth):
    if users_col is None:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    if users_col.find_one({"email": user.email}):
        return {"success": False, "message": "User already exists"}
    
    users_col.insert_one({"email": user.email, "password": user.password, "created_at": datetime.utcnow()})
    return {"success": True, "message": "Signup successful"}

@app.post("/login", tags=["Authentication"])
async def login(user: UserAuth):
    if users_col is None:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    db_user = users_col.find_one({"email": user.email, "password": user.password})
    if not db_user:
        return {"success": False, "message": "Invalid credentials"}
    
    return {"success": True, "message": "Login successful"}

# 5. CORE ENDPOINTS
@app.get("/", tags=["General"])
async def root():
    return {
        "status": "online",
        "message": "Welcome to ANIMEFLIX API",
        "timestamp": datetime.utcnow()
    }

@app.get("/health", tags=["General"])
async def health():
    return {"status": "healthy", "database": "connected" if users_col else "disconnected"}

@app.post("/generate", tags=["AI Generation"])
async def generate_root(request: GenerateRequest):
    """Exposed at root for easy access/docs"""
    try:
        from app.services.ai import create_anime_video, generate_scene_image
        video_url = await create_anime_video(request.prompt)
        image_url = await generate_scene_image(request.prompt)
        
        return {
            "success": True,
            "video_url": video_url,
            "image_url": image_url,
            "prompt": request.prompt
        }
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", tags=["AI Chat"])
async def chat(request: dict):
    responses = [
        "I can help you generate amazing anime scenes!",
        "What's your favorite anime style?",
        "Try prompting me with a cyberpunk samurai story!"
    ]
    return {"success": True, "response": random.choice(responses)}

# 6. MODULAR API ROUTES (for Mobile App compatibility)
app.include_router(api_router, prefix="/api")

# 7. STATIC FILES (Video storage)
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 8. STARTUP/SHUTDOWN
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo() # Async client for modular routes

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
