import json
import os
# Use OpenAI if key exists, else fallback to a basic mock

def generate_story(prompt: str):
    print(f"Generating story for: {prompt}")
    # Mocking for immediate runnability without API keys
    return {
        "title": "Generated Story",
        "scenes": [
            {
                "scene_num": 1,
                "description": "Opening establishing shot based on the prompt.",
                "narration": f"It begins here: {prompt}",
                "prompt": f"{prompt}, highly detailed, anime style, cinematic lighting"
            },
            {
                "scene_num": 2,
                "description": "Close up action shot.",
                "narration": "The journey continues.",
                "prompt": "close up, action pose, dynamic angle, anime style, 8k"
            }
        ]
    }
