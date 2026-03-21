# 🚀 Quick Start Guide

Ready to run your AI Anime Generator locally? Follow these steps:

## 📋 Prerequisites

- Node.js 18+ installed
- Python 3.8+ installed
- MongoDB Atlas connection (already configured!)

## 🔧 Setup Steps

### 1. Start Backend

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --reload
```

The backend will be running at: **http://localhost:8000**

### 2. Start Frontend

```bash
# Open a new terminal window
cd frontend

# Install Node.js dependencies
npm install

# Start the Next.js development server
npm run dev
```

The frontend will be running at: **http://localhost:3000**

## 🎯 Test Your Setup

1. **Backend Health Check**: Visit http://localhost:8000/health
2. **Frontend**: Visit http://localhost:3000
3. **Generate Content**: Try creating an anime story!

## 🎨 What You Can Do

- ✅ Generate anime stories with AI
- ✅ Create anime character images (stored in Cloudinary)
- ✅ Generate anime video scenes (placeholder)
- ✅ Save all creations to MongoDB Atlas
- ✅ Beautiful Netflix-style interface

## 🔑 API Keys Already Configured

Your services are ready:
- ✅ OpenAI API key configured
- ✅ MongoDB Atlas connection configured
- ✅ Cloudinary configured (need API secret)

**⚠️ Important**: 
- Add your Cloudinary API secret to `backend/.env`
- Never commit `.env` files to Git or share them!

## 🛠️ Troubleshooting

### Backend Issues
- Make sure Python 3.8+ is installed
- Check if all dependencies installed: `pip install -r requirements.txt`
- Verify MongoDB Atlas connection in `.env`

### Frontend Issues
- Ensure Node.js 18+ is installed
- Check dependencies: `npm install`
- Clear cache: `rm -rf .next && npm run dev`

### Database Issues
- Check MongoDB Atlas cluster is running
- Verify IP whitelist includes your location
- Monitor Atlas dashboard for connection status

### API Issues
- Check OpenAI API key has credits
- Monitor usage at: https://platform.openai.com/usage
- Verify backend logs for API errors

## 🌐 Next Steps

Once everything is working locally:

1. **Deploy to Production**: Follow `DEPLOYMENT.md`
2. **Add Cloudinary Secret**: Complete image storage setup
3. **Configure Video Generation**: Add Replicate API token
4. **Customize Styles**: Modify UI themes and prompts

## 🎉 Enjoy Creating!

Your AI Anime Generator is ready to use with:
- 🤖 AI-powered content generation
- 🖼️ Cloudinary image storage
- 🗄️ MongoDB Atlas database
- 🎨 Professional UI/UX

Start creating amazing anime content with AI!

---

**Need Help?** Check the full documentation:
- `README.md` - Complete overview
- `DEPLOYMENT.md` - Production deployment
- `DATABASE_SETUP.md` - Database configuration
