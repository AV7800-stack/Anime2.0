import os
import json
import time
from .story import generate_story
from .image import generate_images
from .audio import generate_audio
from .video import assemble_video

def run_pipeline(job_id: str, prompt: str, style: str, low_end_mode: bool):
    job_dir = f"output/{job_id}"
    os.makedirs(job_dir, exist_ok=True)
    print(f"[{job_id}] Starting pipeline for prompt: {prompt}")
    
    try:
        # 1. Story
        story = generate_story(prompt)
        with open(f"{job_dir}/story.json", "w") as f:
            json.dump(story, f, indent=4)
            
        # 2. Images
        image_paths = generate_images(story, style, job_dir, low_end_mode)
        
        # 3. Audio
        audio_paths = generate_audio(story, job_dir)
        
        # 4. Video
        final_video = assemble_video(image_paths, audio_paths, job_dir)
        print(f"[{job_id}] Finished! Video saved at {final_video}")
    except Exception as e:
        print(f"[{job_id}] Error during pipeline: {e}")
        with open(f"{job_dir}/error.log", "w") as f:
            f.write(str(e))
