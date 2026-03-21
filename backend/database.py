from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import AsyncMongoClient
from pymongo.errors import ConnectionFailure
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    def __init__(self):
        self.client: Optional[AsyncMongoClient] = None
        self.database = None
        self.collection = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
            self.client = AsyncMongoClient(mongo_url)
            
            # Test the connection
            await self.client.admin.command('ping')
            
            self.database = self.client.anime_generator
            self.collection = self.database.generations
            
            print("✅ Connected to MongoDB")
            
        except ConnectionFailure as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            print(f"❌ MongoDB connection error: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("✅ Disconnected from MongoDB")
    
    async def save_generation(self, type: str, prompt: str, result: Dict[str, Any]) -> str:
        """Save a generation to the database"""
        try:
            document = {
                "type": type,
                "prompt": prompt,
                "result": result,
                "created_at": datetime.utcnow(),
                "status": "completed"
            }
            
            result = await self.collection.insert_one(document)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Error saving generation: {e}")
            raise
    
    async def get_generations(self, limit: int = 10, type_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent generations from the database"""
        try:
            query = {}
            if type_filter:
                query["type"] = type_filter
            
            cursor = self.collection.find(query).sort("created_at", -1).limit(limit)
            generations = []
            
            async for document in cursor:
                # Convert ObjectId to string and handle datetime
                document["_id"] = str(document["_id"])
                if "created_at" in document:
                    document["created_at"] = document["created_at"].isoformat()
                generations.append(document)
            
            return generations
            
        except Exception as e:
            print(f"❌ Error retrieving generations: {e}")
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get generation statistics"""
        try:
            pipeline = [
                {"$group": {"_id": "$type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            type_stats = []
            async for document in self.collection.aggregate(pipeline):
                type_stats.append({
                    "type": document["_id"],
                    "count": document["count"]
                })
            
            total_generations = await self.collection.count_documents({})
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_generations = await self.collection.count_documents({
                "created_at": {"$gte": today}
            })
            
            return {
                "total_generations": total_generations,
                "today_generations": today_generations,
                "type_breakdown": type_stats
            }
            
        except Exception as e:
            print(f"❌ Error retrieving stats: {e}")
            raise

# Global database instance
db_instance = MongoDB()

async def get_database() -> MongoDB:
    """Dependency function to get database instance"""
    if not db_instance.client:
        await db_instance.connect()
    return db_instance
