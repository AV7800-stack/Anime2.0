from motor.motor_asyncio import AsyncIOMotorClient
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db_manager = MongoDB()

async def connect_to_mongo():
    if not settings.MONGO_URL:
        logger.error("MONGO_URL environment variable not set.")
        raise Exception("MONGO_URL not configured. Cannot connect to database.")
    
    try:
        db_manager.client = AsyncIOMotorClient(settings.MONGO_URL)
        db_manager.db = db_manager.client.get_database("anime_netflix_db")
        # Test connection
        await db_manager.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    if db_manager.client:
        db_manager.client.close()
        logger.info("MongoDB connection closed.")

def get_db():
    if db_manager.db is None:
        raise Exception("Database not initialized")
    return db_manager.db