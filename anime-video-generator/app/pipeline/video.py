import os
from moviepy.editor import ImageClip, concatenate_videoclips

def assemble_video(image_paths: list, audio_paths: list, output_dir: str):
    clips = []
    for img_path in image_paths:
        # 3 seconds per scene for basic implementation
        clip = ImageClip(img_path).set_duration(3)
        clips.append(clip)
        
    final_clip = concatenate_videoclips(clips, method="compose")
    output_path = f"{output_dir}/final_video.mp4"
    # Write video. fps=24 is standard for anime.
    final_clip.write_videofile(output_path, fps=24, codec="libx264")
    return output_path
