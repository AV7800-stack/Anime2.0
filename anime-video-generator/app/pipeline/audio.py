import os
# import edge_tts

def generate_audio(story: dict, output_dir: str):
    paths = []
    for scene in story["scenes"]:
        audio_path = f"{output_dir}/scene_{scene['scene_num']}.mp3"
        # MOCK IMPLEMENTATION
        # Real implementation would use edge-tts or ElevenLabs
        # For now, returning None to let video assembler know to skip audio or use silence
        paths.append(None)
    return paths
