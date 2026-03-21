import subprocess
import os
import json
from typing import Dict, Any, List
import tempfile
import requests

class VideoGenerator:
    def __init__(self):
        self.temp_dir = "/tmp"
    
    def generate_video(self, prompt: str, duration: int = 5) -> Dict[str, Any]:
        """
        Generate anime video using FFmpeg subprocess only
        """
        try:
            # Generate frames using Pollinations.ai
            from .image_generator import image_generator
            frames_result = image_generator.generate_multiple_frames(prompt, min(duration, 5))
            
            if not frames_result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to generate frames: {frames_result.get('error', 'Unknown error')}"
                }
            
            frame_urls = frames_result["frame_urls"]
            
            # Download frames to temp directory
            frame_paths = []
            for i, url in enumerate(frame_urls):
                try:
                    response = requests.get(url, timeout=30)
                    if response.status_code == 200:
                        frame_path = os.path.join(self.temp_dir, f"frame_{i:04d}.jpg")
                        with open(frame_path, 'wb') as f:
                            f.write(response.content)
                        frame_paths.append(frame_path)
                except Exception as e:
                    print(f"Failed to download frame {i}: {e}")
            
            if len(frame_paths) < 2:
                return {
                    "success": False,
                    "error": "Not enough frames downloaded for video creation"
                }
            
            # Create video using FFmpeg
            output_path = os.path.join(self.temp_dir, f"video_{os.getpid()}.mp4")
            
            # FFmpeg command
            cmd = [
                'ffmpeg',
                '-y',  # Overwrite output file
                '-framerate', '2',  # 2 frames per second
                '-i', os.path.join(self.temp_dir, 'frame_%04d.jpg'),  # Input pattern
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
                # Clean up frame files
                for frame_path in frame_paths:
                    try:
                        os.remove(frame_path)
                    except:
                        pass
                
                return {
                    "success": True,
                    "video_path": output_path,
                    "prompt": prompt,
                    "duration": duration,
                    "frames": len(frame_paths),
                    "service": "ffmpeg"
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
                "error": str(e)
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
    
    def create_video_from_images(self, image_paths: List[str], output_path: str = None, duration: int = 5) -> Dict[str, Any]:
        """
        Create video from existing images
        """
        try:
            if not output_path:
                output_path = os.path.join(self.temp_dir, f"custom_video_{os.getpid()}.mp4")
            
            if len(image_paths) < 2:
                return {
                    "success": False,
                    "error": "Need at least 2 images to create video"
                }
            
            # FFmpeg command for custom images
            cmd = [
                'ffmpeg',
                '-y',
                '-framerate', '2',
                '-i', image_paths[0],  # First image
                '-i', image_paths[1],  # Second image
                '-filter_complex', '[0:v][1:v]concat=n=2:v=1[out]',
                '-map', '[out]',
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
                    "images": len(image_paths)
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

# Global instance
video_generator = VideoGenerator()
