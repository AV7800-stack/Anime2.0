# 🚀 Deployment Guide

Complete step-by-step guide to deploy your AI Anime Generator to production.

## 📋 Prerequisites

Before starting, make sure you have:

- GitHub account
- OpenAI API key with credits
- MongoDB Atlas account (free tier available)
- Vercel account (for frontend)
- Render account (for backend)

## 🗄️ Database Setup (MongoDB Atlas)

### 1. Create MongoDB Atlas Account

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up for a free account
3. Create a new organization and project

### 2. Create Cluster

1. Click "Build a Database"
2. Choose **M0 Sandbox** (free tier)
3. Select a cloud provider and region (choose one close to your users)
4. Leave cluster name as default or change to `anime-generator-cluster`
5. Click "Create Cluster"

### 3. Configure Network Access

1. Go to "Network Access" in the left sidebar
2. Click "Add IP Address"
3. Select "Allow Access from Anywhere" (0.0.0.0/0) for development
4. For production, add your Vercel and Render IP ranges

### 4. Create Database User

1. Go to "Database Access" in the left sidebar
2. Click "Add New Database User"
3. Username: `animeuser`
4. Password: Generate a strong password (save it!)
5. Grant "Read and write to any database"
6. Click "Add User"

### 5. Get Connection String

1. Go to your cluster overview
2. Click "Connect"
3. Choose "Connect your application"
4. Copy the connection string
5. Replace `<password>` with your user password
6. Save this for later

## 🔧 Backend Deployment (Render)

### 1. Prepare Backend Code

1. Ensure your backend code is pushed to GitHub
2. Verify `.env.example` exists in the repo
3. Make sure `requirements.txt` is complete

### 2. Create Render Service

1. Go to [Render](https://render.com)
2. Sign up and connect your GitHub account
3. Click "New +" → "Web Service"
4. Select your repository
5. Configure service:
   - **Name**: `ai-anime-generator-api`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. Set Environment Variables

In Render dashboard, add these environment variables:

```env
OPENAI_API_KEY=sk-your-openai-key-here
MONGO_URL=mongodb+srv://animeuser:your-password@cluster.mongodb.net/anime_generator?retryWrites=true&w=majority
REPLICATE_API_TOKEN=r8-your-replicate-token-here  # Optional
ENVIRONMENT=production
```

### 4. Deploy

1. Click "Create Web Service"
2. Wait for deployment to complete
3. Test the API by visiting `https://your-service-name.onrender.com/health`
4. Save the deployed URL for frontend configuration

## 🎨 Frontend Deployment (Vercel)

### 1. Prepare Frontend Code

1. Ensure frontend code is in the same GitHub repository
2. Verify `.env.example` exists
3. Check `package.json` build scripts

### 2. Create Vercel Project

1. Go to [Vercel](https://vercel.com)
2. Sign up and connect your GitHub account
3. Click "New Project"
4. Select your repository
5. Configure project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend` (if frontend is in subfolder)
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### 3. Set Environment Variables

In Vercel dashboard, add this environment variable:

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
```

### 4. Deploy

1. Click "Deploy"
2. Wait for deployment to complete
3. Test the application by visiting the deployed URL
4. Verify API connectivity by trying to generate content

## 🔍 Testing Your Deployment

### 1. Backend Health Check

Visit `https://your-backend.onrender.com/health`

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "services": {
    "story": "available",
    "image": "available", 
    "video": "available"
  }
}
```

### 2. Frontend Functionality

1. Visit your Vercel deployment URL
2. Navigate to the Generate page
3. Try generating a story (quickest test)
4. Check if results appear correctly

### 3. API Documentation

Visit `https://your-backend.onrender.com/docs` to test API endpoints directly.

## 🛠️ Common Issues & Solutions

### Issue: CORS Errors

**Problem**: Frontend can't connect to backend

**Solution**:
1. In backend `main.py`, update CORS origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.vercel.app"],  # Your Vercel URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Issue: Database Connection

**Problem**: Backend can't connect to MongoDB

**Solution**:
1. Verify IP whitelist in MongoDB Atlas
2. Check connection string format
3. Ensure database user has correct permissions

### Issue: OpenAI API Errors

**Problem**: Generation fails with API errors

**Solution**:
1. Verify OpenAI API key has credits
2. Check API key is correctly set in environment variables
3. Monitor OpenAI usage dashboard

### Issue: Build Failures

**Problem**: Deployment fails during build

**Solution**:
1. Check build logs for specific errors
2. Verify all dependencies are in requirements.txt/package.json
3. Ensure environment variables are set correctly

## 📊 Monitoring & Maintenance

### 1. Backend Monitoring

- Render provides basic metrics and logs
- Check error logs regularly
- Monitor API usage and costs

### 2. Frontend Monitoring

- Vercel Analytics for user metrics
- Monitor build and deployment success
- Check Core Web Vitals

### 3. Database Monitoring

- MongoDB Atlas provides free monitoring
- Monitor storage usage
- Check query performance

## 🔒 Security Best Practices

### 1. API Keys

- Never commit API keys to Git
- Use environment variables for all secrets
- Rotate API keys regularly

### 2. Database Security

- Use strong database passwords
- Limit IP access in production
- Enable database authentication

### 3. Rate Limiting

- Consider implementing rate limiting on backend
- Monitor for unusual API usage patterns
- Set up alerts for high traffic

## 💰 Cost Management

### 1. OpenAI API

- Monitor usage in OpenAI dashboard
- Set usage alerts and limits
- Consider costs per generation type

### 2. MongoDB Atlas

- M0 tier is free (512MB storage)
- Monitor storage usage
- Upgrade if needed

### 3. Hosting Costs

- Vercel: Free tier available
- Render: Free tier available
- Consider upgrade for higher traffic

## 🔄 Updates & Maintenance

### 1. Updating Dependencies

Regularly update dependencies:
```bash
# Backend
pip install --upgrade -r requirements.txt

# Frontend  
npm update
```

### 2. Database Backups

- Enable automated backups in MongoDB Atlas
- Test restore process periodically
- Document backup procedures

### 3. Performance Optimization

- Monitor API response times
- Optimize database queries
- Consider caching for frequently requested content

## 🎉 Success Checklist

Before going live, verify:

- [ ] Backend health endpoint responds correctly
- [ ] Frontend loads without errors
- [ ] Story generation works
- [ ] Image generation works  
- [ ] Video generation works (if configured)
- [ ] Database connection is stable
- [ ] Environment variables are set
- [ ] CORS is properly configured
- [ ] Error handling is working
- [ ] Mobile responsiveness is good

## 🆘 Support Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Render Documentation](https://render.com/docs)
- [MongoDB Atlas Docs](https://docs.mongodb.com/atlas)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Next.js Deployment Guide](https://nextjs.org/docs/deployment)

---

Your AI Anime Generator is now live! 🎉 Users can visit your Vercel URL and start creating amazing anime content with AI.
