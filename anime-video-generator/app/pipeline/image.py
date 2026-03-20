import os
from PIL import Image, ImageDraw, ImageFont
# In production, import diffusers here

def generate_images(story: dict, style: str, output_dir: str, low_end_mode: bool):
    paths = []
    for scene in story["scenes"]:
        img_path = f"{output_dir}/scene_{scene['scene_num']}.png"
        # MOCK IMPLEMENTATION: Create dummy images to avoid heavy downloads initially
        # Real implementation would load StableDiffusionPipeline here using diffusers
        width, height = (800, 450) if low_end_mode else (1920, 1080)
        img = Image.new('RGB', (width, height), color = (20, 20, 30))
        d = ImageDraw.Draw(img)
        d.text((50, height//2), f"Scene {scene['scene_num']}\nStyle: {style}\nPrompt: {scene['prompt'][:40]}...", fill=(255,200,0))
        img.save(img_path)
        paths.append(img_path)
        print(f"Generated image: {img_path}")
    return paths
