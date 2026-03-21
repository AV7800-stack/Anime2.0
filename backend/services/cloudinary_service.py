import cloudinary
import cloudinary.uploader
import os
from typing import Dict, Any, Optional
import uuid

def get_cloudinary_config():
    """Helper to get config only when needed, following production best practices."""
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
    api_key = os.environ.get("CLOUDINARY_API_KEY")
    api_secret = os.environ.get("CLOUDINARY_API_SECRET")
    
    if not all([cloud_name, api_key, api_secret]):
        return None
        
    return {
        "cloud_name": cloud_name,
        "api_key": api_key,
        "api_secret": api_secret
    }

async def upload_image_from_url(image_url: str, folder: str = "anime-generator") -> Dict[str, Any]:
    """Uploads an image from a URL to Cloudinary with on-demand config."""
    config = get_cloudinary_config()
    if not config:
        print("⚠️ Cloudinary not configured. Skipping upload.")
        return {"success": False, "error": "Cloudinary credentials missing"}

    try:
        cloudinary.config(**config)
        filename = f"anime_{uuid.uuid4().hex[:8]}"
        
        upload_result = cloudinary.uploader.upload(
            image_url,
            public_id=f"{folder}/{filename}",
            folder=folder,
            resource_type="image",
            format="webp",
            quality="auto"
        )
        
        return {
            "success": True,
            "url": upload_result["secure_url"],
            "public_id": upload_result["public_id"],
            "width": upload_result.get("width"),
            "height": upload_result.get("height"),
            "format": upload_result.get("format"),
            "size": upload_result.get("bytes")
        }
    except Exception as e:
        print(f"❌ Cloudinary Upload Error: {str(e)}")
        return {"success": False, "error": str(e)}

class CloudinaryService:
    async def upload_image_from_url(self, image_url: str, folder: str = "anime-characters"):
        return await upload_image_from_url(image_url, folder)
    
    async def upload_image_from_bytes(self, image_bytes: bytes, filename: str, folder: str = "anime-generator"):
        config = get_cloudinary_config()
        if not config: return {"success": False, "error": "Not configured"}
        cloudinary.config(**config)
        result = cloudinary.uploader.upload(image_bytes, folder=folder, public_id=filename)
        return {"success": True, "url": result["secure_url"], "public_id": result["public_id"]}

    def get_optimized_url(self, public_id: str, width: int = 800, height: int = 800):
        cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
        return f"https://res.cloudinary.com/{cloud_name}/image/upload/w_{width},h_{height},c_fill/{public_id}"

    def __getattr__(self, name):
        def dummy(*args, **kwargs):
            print(f"⚠️ Cloudinary method {name} called but not fully implemented")
            return {"success": False, "error": f"Method {name} fallback"}
        return dummy

# This is the exact name main.py is trying to import
cloudinary_service = CloudinaryService()
