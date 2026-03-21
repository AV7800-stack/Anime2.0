# AI Anime Generator - Backend

A FastAPI backend for generating anime stories, images, and videos with AI.

## Features

- 🤖 AI-powered story generation (OpenAI GPT)
- 🎨 Anime image generation (OpenAI DALL-E)
- 🎬 Video scene generation (Replicate)
- 📊 MongoDB integration for storing generations
- 🚀 Fast and async API endpoints
- 📝 Comprehensive error handling

## Getting Started

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
```

3. Configure your API keys in `.env`:
   - `OPENAI_API_KEY`: Get from [OpenAI](https://platform.openai.com/)
   - `MONGO_URL`: Your MongoDB connection string
   - `REPLICATE_API_TOKEN`: Optional, for video generation

4. Start the server:
```bash
uvicorn main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000)

## API Documentation

Once the server is running, visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API documentation.

## API Endpoints

### Story Generation
```http
POST /generate-story
Content-Type: application/json

{
  "prompt": "A magical girl who fights demons with music",
  "style": "anime",
  "length": "medium"
}
```

### Image Generation
```http
POST /generate-image
Content-Type: application/json

{
  "prompt": "Anime character with blue hair and sword",
  "style": "anime",
  "size": "1024x1024"
}
```

### Video Generation
```http
POST /generate-video
Content-Type: application/json

{
  "prompt": "Dynamic fight scene in cyberpunk Tokyo",
  "style": "anime",
  "duration": 10
}
```

### Other Endpoints
- `GET /health` - Health check
- `GET /generations` - Get recent generations
- `GET /stats` - Generation statistics

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for story and image generation |
| `MONGO_URL` | Yes | MongoDB connection string |
| `REPLICATE_API_TOKEN` | No | Replicate API token for video generation |
| `ENVIRONMENT` | No | Environment (development/production) |

## Project Structure

```
backend/
├── main.py                 # FastAPI application
├── database.py             # MongoDB connection and operations
├── services/
│   ├── story_generator.py # Story generation service
│   ├── image_generator.py # Image generation service
│   └── video_generator.py # Video generation service
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Deployment

### Render Deployment

1. Push your code to GitHub
2. Connect your repository to Render
3. Set environment variables in Render dashboard
4. Deploy!

### Required Environment Variables on Render:
- `OPENAI_API_KEY`
- `MONGO_URL`
- `REPLICATE_API_TOKEN` (optional)

## Technologies Used

- **FastAPI**: Modern Python web framework
- **OpenAI**: AI models for generation
- **MongoDB**: Database for storage
- **Motor**: Async MongoDB driver
- **Replicate**: Video generation platform
- **Pydantic**: Data validation
