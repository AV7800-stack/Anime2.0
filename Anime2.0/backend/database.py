# MongoDB Database Support (Optional)
# Using correct motor import for async MongoDB

from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db: AsyncIOMotorDatabase = None
        self.mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        self.db_name = os.getenv("DB_NAME", "anime2")
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client[self.db_name]
            print("✅ Connected to MongoDB")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection error: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("✅ Disconnected from MongoDB")
    
    async def save_generation(self, data: dict):
        """Save generation data to MongoDB"""
        try:
            if not self.db:
                return None
            
            collection = self.db.generations
            result = await collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Save error: {e}")
            return None
    
    async def get_generations(self, limit: int = 10):
        """Get recent generations from MongoDB"""
        try:
            if not self.db:
                return []
            
            collection = self.db.generations
            cursor = collection.find().sort("_id", -1).limit(limit)
            generations = await cursor.to_list(length=limit)
            return generations
        except Exception as e:
            print(f"❌ Get error: {e}")
            return []

# Global instance
mongodb = MongoDB()
