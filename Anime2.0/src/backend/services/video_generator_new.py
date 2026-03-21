import subprocess
import os
import json
from typing import Dict, Any, List
import tempfile

class VideoGenerator:
    def __init__(self):
        self.temp_dir = "/tmp"
    
    def generate_video(self, prompt: str, duration: int = 5) -> Dict[str, Any]:
        """
        Generate anime video using FFmpeg subprocess only
        """
        try:
            # Generate frames using Pollinations.ai URLs directly
            frame_urls = []
            for i in range(min(duration, 5)):
                frame_prompt = f"{prompt}, frame {i+1}, anime style, consistent character"
                frame_url = f"https://image.pollinations.ai/prompt/{frame_prompt}?style=anime&width=512&height=512&seed={i}"
                frame_urls.append(frame_url)
            
            # Create simple video using FFmpeg with test pattern
            output_path = os.path.join(self.temp_dir, f"video_{os.getpid()}.mp4")
            
            # FFmpeg command to create a simple animation
            cmd = [
                'ffmpeg',
                '-y',  # Overwrite output file
                '-f', 'lavfi',  # Use libavfilter
                '-i', f'testsrc=duration={duration}:size=512x512:rate=2',  # Generate test pattern
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-r', '30',  # Output framerate
                '-t', str(duration),  # Duration
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                return {
                    "success": True,
                    "video_path": output_path,
                    "prompt": prompt,
                    "duration": duration,
                    "frames": len(frame_urls),
                    "frame_urls": frame_urls,
                    "service": "ffmpeg",
                    "note": "FFmpeg test pattern generated. Use frame_urls for actual images."
                }
            else:
                return {
                    "success": False,
                    "error": f"FFmpeg error: {result.stderr}",
                    "frame_urls": frame_urls
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "note": "FFmpeg not available on this system"
            }
    
    def generate_character_video(self, character_name: str, action: str = "standing") -> Dict[str, Any]:
        """
        Generate character animation video
        """
        prompt = f"{character_name}, anime character, {action}, multiple poses, consistent design"
        return self.generate_video(prompt, 5)
    
    def generate_scene_video(self, scene_description: str) -> Dict[str, Any]:
        """
        Generate animated scene
        """
        prompt = f"anime scene, {scene_description}, background, characters, animation frames"
        return self.generate_video(prompt, 8)
    
    def create_video_from_images(self, image_urls: List[str], output_path: str = None, duration: int = 5) -> Dict[str, Any]:
        """
        Create video from image URLs (would need download step in real implementation)
        """
        try:
            if not output_path:
                output_path = os.path.join(self.temp_dir, f"custom_video_{os.getpid()}.mp4")
            
            if len(image_urls) < 2:
                return {
                    "success": False,
                    "error": "Need at least 2 images to create video"
                }
            
            # For now, create a test video since we can't download images
            cmd = [
                'ffmpeg',
                '-y',
                '-f', 'lavfi',
                '-i', f'testsrc=duration={duration}:size=512x512:rate=2',
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-r', '30',
                '-t', str(duration),
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                return {
                    "success": True,
                    "video_path": output_path,
                    "duration": duration,
                    "images": len(image_urls),
                    "note": "Test video created. Use actual image download for production."
                }
            else:
                return {
                    "success": False,
                    "error": f"FFmpeg error: {result.stderr}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_ffmpeg_available(self) -> Dict[str, Any]:
        """
        Check if FFmpeg is available
        """
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            if result.returncode == 0:
                return {
                    "success": True,
                    "available": True,
                    "version": result.stdout.split('\n')[0] if result.stdout else "Unknown"
                }
            else:
                return {
                    "success": True,
                    "available": False,
                    "error": "FFmpeg not found"
                }
        except FileNotFoundError:
            return {
                "success": True,
                "available": False,
                "error": "FFmpeg not installed"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
video_generator = VideoGenerator()
