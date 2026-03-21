# 🌸 AI Anime Generator

A complete production-ready web application for generating anime stories, characters, and videos using artificial intelligence. Built with Next.js frontend, FastAPI backend, and MongoDB database.

## ✨ Features

- 🎨 **Generate Anime Stories** - Create compelling anime narratives with AI
- 🖼️ **Create Anime Characters** - Generate stunning anime character images
- 🎬 **Produce Anime Scenes** - Generate animated anime video content
- 📱 **Modern UI/UX** - Netflix-inspired interface with dark theme
- ⚡ **Real-time Generation** - Fast AI-powered content creation
- 📊 **Content Storage** - Save and manage your creations
- 🔍 **Smart Search** - Find your generated content easily

## 🏗️ Architecture

```
ai-anime-generator/
├── frontend/          # Next.js 14 application
│   ├── app/          # App router pages
│   ├── components/   # Reusable components
│   └── ...           # Config files
├── backend/           # FastAPI Python server
│   ├── services/     # AI generation services
│   ├── database.py   # MongoDB integration
│   └── main.py       # API endpoints
└── README.md         # This file
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- Python 3.8+
- MongoDB (local or cloud)
- OpenAI API key

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-anime-generator

# Setup Frontend
cd frontend
npm install
cp .env.example .env.local

# Setup Backend
cd ../backend
pip install -r requirements.txt
cp .env.example .env
```

### 2. Configure API Keys

**Backend (.env):**
```env
OPENAI_API_KEY=your_openai_api_key_here
MONGO_URL=mongodb://localhost:27017
REPLICATE_API_TOKEN=your_replicate_api_token_here  # Optional
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start Development

```bash
# Start Backend (Terminal 1)
cd backend
uvicorn main:app --reload

# Start Frontend (Terminal 2)
cd frontend
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) to see the app!

## 📱 Frontend Features

- **Home Page**: Featured anime creations and navigation
- **Generate Page**: Create stories, images, or videos with AI
- **Result Page**: View and share generated content
- **Responsive Design**: Works perfectly on mobile and desktop
- **Modern UI**: Dark theme with anime-inspired aesthetics
- **Loading States**: Beautiful animations during generation

## 🔧 Backend API

### Core Endpoints

- `POST /generate-story` - Generate anime stories
- `POST /generate-image` - Generate anime images  
- `POST /generate-video` - Generate anime videos
- `GET /generations` - Retrieve saved creations
- `GET /stats` - Get generation statistics
- `GET /health` - Health check endpoint

### AI Services

- **Story Generator**: Uses OpenAI GPT for narrative creation
- **Image Generator**: Uses OpenAI DALL-E for character art
- **Video Generator**: Uses Replicate for animated scenes
- **Database**: MongoDB for content storage and retrieval

## 🌐 Deployment

### Frontend (Vercel)

1. Push frontend code to GitHub
2. Connect to Vercel
3. Set environment variable: `NEXT_PUBLIC_API_URL`
4. Deploy!

### Backend (Render)

1. Push backend code to GitHub  
2. Connect to Render
3. Set environment variables:
   - `OPENAI_API_KEY`
   - `MONGO_URL`
   - `REPLICATE_API_TOKEN` (optional)
4. Deploy!

### Database (MongoDB Atlas)

1. Create free MongoDB Atlas account
2. Create cluster and database
3. Get connection string
4. Add to environment variables

## 🔑 Environment Variables

| Variable | Frontend/Backend | Required | Description |
|----------|------------------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Frontend | Yes | Backend API URL |
| `OPENAI_API_KEY` | Backend | Yes | OpenAI API key |
| `MONGO_URL` | Backend | Yes | MongoDB connection |
| `REPLICATE_API_TOKEN` | Backend | No | Video generation |

## 🛠️ Technologies Used

### Frontend
- **Next.js 14** - React framework
- **Tailwind CSS** - Styling framework
- **Lucide React** - Icon library
- **Axios** - HTTP client
- **TypeScript** - Type safety

### Backend
- **FastAPI** - Python web framework
- **OpenAI** - AI models (GPT, DALL-E)
- **MongoDB** - NoSQL database
- **Motor** - Async MongoDB driver
- **Replicate** - Video generation
- **Pydantic** - Data validation

## 💡 Usage Examples

### Generate an Anime Story
```javascript
const response = await fetch('/api/generate-story', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: "A magical girl who fights demons with music in modern Tokyo",
    style: "anime",
    length: "medium"
  })
})
```

### Generate an Anime Character
```javascript
const response = await fetch('/api/generate-image', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: "Blue-haired anime warrior with glowing sword",
    style: "anime",
    size: "1024x1024"
  })
})
```

## 🎨 Customization

### Adding New Styles
Edit the style dictionaries in the generator services to add new anime styles:

```python
# In story_generator.py
style_modifiers = {
    "anime": "anime style, manga art",
    "studio_ghibli": "Studio Ghibli style",
    "your_new_style": "your description"
}
```

### Custom UI Themes
Modify `tailwind.config.js` to add new color schemes and animations.

## 🔒 Security Notes

- API keys are stored in environment variables
- CORS is configured for production domains
- Input validation on all endpoints
- Error handling prevents information leakage

## 📈 Scaling

- Frontend: Vercel automatically scales
- Backend: Render handles scaling automatically  
- Database: MongoDB Atlas scales with usage
- AI APIs: Consider rate limiting for high traffic

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter issues:

1. Check environment variables are set correctly
2. Verify API keys have sufficient credits
3. Ensure MongoDB connection is working
4. Check browser console for frontend errors
5. Review backend logs for API errors

## 🎉 Enjoy Creating!

Start generating amazing anime content with AI! Whether you're creating stories, characters, or animated scenes, this app provides all the tools you need to bring your anime ideas to life.
