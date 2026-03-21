import os
import json
import aiofiles
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

class JsonDatabase:
    def __init__(self):
        self.temp_dir = "/tmp"
        self.data_file = os.path.join(self.temp_dir, "data.json")
        self.ensure_data_file()
    
    def ensure_data_file(self):
        """Ensure data file exists"""
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir, exist_ok=True)
        
        if not os.path.exists(self.data_file):
            initial_data = {
                "generations": [],
                "users": [],
                "settings": {},
                "created_at": datetime.now().isoformat()
            }
            with open(self.data_file, 'w') as f:
                json.dump(initial_data, f, indent=2)
    
    async def load_data(self) -> Dict[str, Any]:
        """Load data from JSON file"""
        try:
            async with aiofiles.open(self.data_file, 'r') as f:
                content = await f.read()
                return json.loads(content) if content else {"generations": [], "users": [], "settings": {}}
        except Exception as e:
            print(f"Error loading data: {e}")
            return {"generations": [], "users": [], "settings": {}}
    
    async def save_data(self, data: Dict[str, Any]) -> bool:
        """Save data to JSON file"""
        try:
            async with aiofiles.open(self.data_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    async def save_generation(self, generation_data: Dict[str, Any]) -> Optional[str]:
        """Save generation data"""
        try:
            data = await self.load_data()
            
            generation = {
                "id": str(uuid.uuid4()),
                "type": generation_data.get("type", "unknown"),
                "prompt": generation_data.get("prompt", ""),
                "result": generation_data.get("result", {}),
                "created_at": datetime.now().isoformat(),
                "status": generation_data.get("status", "completed")
            }
            
            data["generations"].append(generation)
            
            success = await self.save_data(data)
            return generation["id"] if success else None
            
        except Exception as e:
            print(f"Error saving generation: {e}")
            return None
    
    async def get_generations(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Get generations with pagination"""
        try:
            data = await self.load_data()
            generations = data.get("generations", [])
            
            # Sort by created_at descending
            generations.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            # Apply pagination
            return generations[offset:offset + limit]
            
        except Exception as e:
            print(f"Error getting generations: {e}")
            return []
    
    async def get_generation_by_id(self, generation_id: str) -> Optional[Dict[str, Any]]:
        """Get specific generation by ID"""
        try:
            data = await self.load_data()
            generations = data.get("generations", [])
            
            for generation in generations:
                if generation.get("id") == generation_id:
                    return generation
            
            return None
            
        except Exception as e:
            print(f"Error getting generation: {e}")
            return None
    
    async def delete_generation(self, generation_id: str) -> bool:
        """Delete generation by ID"""
        try:
            data = await self.load_data()
            generations = data.get("generations", [])
            
            # Filter out the generation to delete
            data["generations"] = [g for g in generations if g.get("id") != generation_id]
            
            return await self.save_data(data)
            
        except Exception as e:
            print(f"Error deleting generation: {e}")
            return False
    
    async def save_user(self, user_data: Dict[str, Any]) -> Optional[str]:
        """Save user data"""
        try:
            data = await self.load_data()
            
            user = {
                "id": str(uuid.uuid4()),
                "name": user_data.get("name", ""),
                "email": user_data.get("email", ""),
                "created_at": datetime.now().isoformat(),
                "settings": user_data.get("settings", {})
            }
            
            data["users"].append(user)
            
            success = await self.save_data(data)
            return user["id"] if success else None
            
        except Exception as e:
            print(f"Error saving user: {e}")
            return None
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            data = await self.load_data()
            generations = data.get("generations", [])
            users = data.get("users", [])
            
            # Count by type
            type_counts = {}
            for gen in generations:
                gen_type = gen.get("type", "unknown")
                type_counts[gen_type] = type_counts.get(gen_type, 0) + 1
            
            return {
                "total_generations": len(generations),
                "total_users": len(users),
                "type_counts": type_counts,
                "data_file": self.data_file,
                "file_size_bytes": os.path.getsize(self.data_file) if os.path.exists(self.data_file) else 0
            }
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {"error": str(e)}
    
    async def cleanup_old_generations(self, days: int = 30) -> int:
        """Clean up old generations"""
        try:
            data = await self.load_data()
            generations = data.get("generations", [])
            
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            original_count = len(generations)
            data["generations"] = [
                gen for gen in generations 
                if datetime.fromisoformat(gen.get("created_at", "")).timestamp() > cutoff_date
            ]
            
            await self.save_data(data)
            
            return original_count - len(data["generations"])
            
        except Exception as e:
            print(f"Error cleaning up: {e}")
            return 0

# Global instance (replacing MongoDB)
json_db = JsonDatabase()
