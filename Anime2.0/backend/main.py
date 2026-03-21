import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pymongo import MongoClient
from app.api.router import api_router
from app.db.mongodb import connect_to_mongo, close_mongo_connection
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ANIMEFLIX API",
    description="Production-ready FastAPI with MongoDB and Custom JWT Auth",
    version="1.0.0"
)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- USER REQUESTED CODE START ---
# MongoDB connect (Using pymongo as requested)
# We initialize this globally but connect safely
mongo_url = os.getenv("MONGO_URL")
if not mongo_url:
    # Fallback to MONGO_URI if MONGO_URL is missing
    mongo_url = os.getenv("MONGO_URI", "mongodb://localhost:27017")

try:
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
    # Trigger a connection check
    client.server_info()
    db = client["animeflix"]
    users_col = db["users"]
    logger.info("✅ User-requested MongoDB (pymongo) connected successfully")
except Exception as e:
    logger.error(f"❌ User-requested MongoDB connection failed: {e}")
    # We define dummies to prevent NameErrors in the routes below
    client = None
    db = None
    users_col = None

class User(BaseModel):
    email: str
    password: str

# SIGNUP
@app.post("/signup")
def signup(user: User):
    if users_col is None:
        return {"message": "Database not connected"}
    if users_col.find_one({"email": user.email}):
        return {"message": "User already exists"}
    
    users_col.insert_one(user.dict())
    return {"message": "Signup successful"}

# LOGIN
@app.post("/login")
def login(user: User):
    if users_col is None:
        return {"message": "Database not connected"}
    db_user = users_col.find_one({"email": user.email, "password": user.password})
    
    if not db_user:
        return {"message": "Invalid credentials"}
    
    return {"message": "Login successful"}
# --- USER REQUESTED CODE END ---

# Mount static files for generated videos
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# Existing modular API routes (using /api prefix)
app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"status": "ok", "message": "ANIMEFLIX API is running"}
