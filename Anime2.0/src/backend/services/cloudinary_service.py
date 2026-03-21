import os
import json
import aiofiles
from typing import Dict, Any, Optional
import uuid
from datetime import datetime

class LocalStorageService:
    def __init__(self):
        self.temp_dir = "/tmp"
        self.data_file = os.path.join(self.temp_dir, "data.json")
        self.ensure_temp_dir()
    
    def ensure_temp_dir(self):
        """Ensure temp directory exists"""
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir, exist_ok=True)
    
    async def save_file(self, file_data: bytes, filename: str = None) -> Dict[str, Any]:
        """
        Save file to local /tmp/ folder
        """
        try:
            if not filename:
                filename = f"file_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
            
            # Add extension if not present
            if not '.' in filename:
                filename += ".bin"
            
            file_path = os.path.join(self.temp_dir, filename)
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_data)
            
            return {
                "success": True,
                "file_path": file_path,
                "filename": filename,
                "size": len(file_data),
                "service": "local_storage"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def save_image(self, image_data: bytes, filename: str = None) -> Dict[str, Any]:
        """
        Save image to local /tmp/ folder
        """
        if not filename:
            filename = f"image_{uuid.uuid4().hex[:8]}.jpg"
        
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            filename += '.jpg'
        
        return await self.save_file(image_data, filename)
    
    async def save_video(self, video_data: bytes, filename: str = None) -> Dict[str, Any]:
        """
        Save video to local /tmp/ folder
        """
        if not filename:
            filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
        
        if not filename.lower().endswith(('.mp4', '.avi', '.mov', '.webm')):
            filename += '.mp4'
        
        return await self.save_file(video_data, filename)
    
    def get_file_url(self, filename: str) -> str:
        """
        Get local file URL (for development)
        """
        file_path = os.path.join(self.temp_dir, filename)
        if os.path.exists(file_path):
            return f"file://{file_path}"
        return None
    
    async def delete_file(self, filename: str) -> Dict[str, Any]:
        """
        Delete file from local storage
        """
        try:
            file_path = os.path.join(self.temp_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return {
                    "success": True,
                    "message": f"File {filename} deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "File not found"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_files(self, extension: str = None) -> Dict[str, Any]:
        """
        List files in temp directory
        """
        try:
            files = []
            for filename in os.listdir(self.temp_dir):
                if extension and not filename.lower().endswith(extension.lower()):
                    continue
                
                file_path = os.path.join(self.temp_dir, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    files.append({
                        "filename": filename,
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "path": file_path
                    })
            
            return {
                "success": True,
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get storage information
        """
        try:
            total_size = 0
            file_count = 0
            
            for filename in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, filename)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
                    file_count += 1
            
            return {
                "success": True,
                "service": "local_storage",
                "temp_dir": self.temp_dir,
                "file_count": file_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Global instance (replacing cloudinary_service)
local_storage_service = LocalStorageService()
cloudinary_service = local_storage_service
