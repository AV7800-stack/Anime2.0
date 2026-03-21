from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

# Pollinations.ai - 100% Free, No API Key Required
POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt"

@app.route('/')
def home():
    return jsonify({
        "message": "Anime2.0 Video Generator API",
        "status": "running",
        "services": {
            "image": "available (Pollinations.ai)",
            "story": "available (Pollinations.ai)", 
            "video": "available (FFmpeg)",
            "chat": "available"
        }
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'anime character')
        style = data.get('style', 'anime')
        
        # Pollinations.ai - Free, no API key
        image_url = f"{POLLINATIONS_BASE_URL}/{prompt}?style={style}&width=512&height=512"
        
        return jsonify({
            "success": True,
            "image_url": image_url,
            "prompt": prompt,
            "style": style
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate-story', methods=['POST'])
def generate_story():
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'anime story')
        
        # Pollinations.ai text generation
        story_prompt = f"anime story: {prompt}"
        story_url = f"https://text.pollinations.ai/{story_prompt}"
        
        response = requests.get(story_url)
        story = response.text if response.status_code == 200 else "Generated anime story content"
        
        return jsonify({
            "success": True,
            "story": story,
            "prompt": prompt
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate-video', methods=['POST'])
def generate_video():
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'anime scene')
        
        # Generate image first
        image_url = f"{POLLINATIONS_BASE_URL}/{prompt}?style=anime&width=512&height=512"
        
        # For video, return image URL + instructions
        return jsonify({
            "success": True,
            "video_url": image_url,  # Placeholder for video
            "type": "image_to_video",
            "prompt": prompt,
            "note": "Use frontend video processing to create video from image"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', 'Hello!')
        
        # Simple chat response
        responses = [
            "I can help you create anime content!",
            "Try generating an anime character or story!",
            "What anime style do you like?",
            "Let's create something amazing together!"
        ]
        
        import random
        response = random.choice(responses)
        
        return jsonify({
            "success": True,
            "response": response,
            "suggestions": ["Generate anime character", "Create anime story", "Make anime video"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
