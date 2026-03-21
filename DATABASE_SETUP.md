# 🗄️ Database Setup Guide

Your MongoDB Atlas connection is now configured! Here's what you need to know:

## ✅ Current Configuration

**MongoDB Atlas Connection:**
- Cluster: `anime-generator.mongodb.net`
- Database: `anime_generator`
- Connection string configured in `.env`

## 🔧 Database Collections

The app will automatically create these collections:

### `generations`
Stores all your AI-generated content:
```javascript
{
  "_id": ObjectId,
  "type": "story|image|video",
  "prompt": "user input prompt",
  "result": {
    // Generated content (story, image URL, etc.)
  },
  "created_at": ISODate,
  "status": "completed"
}
```

## 🚀 Testing Database Connection

1. **Start the backend:**
```bash
cd backend
uvicorn main:app --reload
```

2. **Test health endpoint:**
Visit http://localhost:8000/health

3. **Generate content:**
Use the frontend to create a story or image - it will automatically save to MongoDB!

## 📊 Database Features

### Automatic Operations
- ✅ Content saved on every generation
- ✅ Automatic timestamping
- ✅ Error handling and logging
- ✅ Connection pooling

### Available Endpoints
- `GET /generations` - Retrieve recent creations
- `GET /stats` - Generation statistics
- Database operations are handled automatically

## 🔍 MongoDB Atlas Dashboard

1. Visit [MongoDB Atlas](https://cloud.mongodb.com)
2. Login to your account
3. Navigate to your `anime-generator` cluster
4. Monitor:
   - Database usage
   - Collection sizes
   - Performance metrics
   - Query statistics

## 📈 Scaling Considerations

### Free Tier Limits (M0)
- **Storage**: 512MB
- **Connections**: 500 connections
- **Bandwidth**: 1GB/month

### When to Upgrade
- More than 10,000 generations per month
- Large image storage (though images go to Cloudinary)
- High concurrent user traffic

## 🔒 Security Notes

### ✅ Already Secured
- Connection uses TLS/SSL
- Username/password authentication
- Network access controls in Atlas

### 🛡️ Recommended
- Enable database backups in Atlas
- Monitor for unusual activity
- Set up alerts for usage spikes

## 🛠️ Troubleshooting

### Connection Issues
```bash
# Test connection manually
mongosh "mongodb+srv://al-Ot-CCOaWl5gn9bZ1hsrhAiWUK0OI5eFDSYO9_gXQDO4@anime-generator.mongodb.net/anime_generator"
```

### Common Errors
- **Authentication failed**: Check username/password
- **Network timeout**: Verify IP whitelist in Atlas
- **Connection refused**: Ensure cluster is running

## 📝 Query Examples

### Get Recent Stories
```javascript
db.generations.find({"type": "story"}).sort({"created_at": -1}).limit(10)
```

### Get Image Stats
```javascript
db.generations.aggregate([
  {"$match": {"type": "image"}},
  {"$group": {"_id": "$style", "count": {"$sum": 1}}}
])
```

### Get Daily Generation Count
```javascript
db.generations.aggregate([
  {"$group": {
    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
    "count": {"$sum": 1}
  }},
  {"$sort": {"_id": -1}}
])
```

## 🎯 Next Steps

1. **Test the connection** by generating some content
2. **Monitor usage** in MongoDB Atlas dashboard
3. **Set up backups** for data protection
4. **Consider scaling** when traffic increases

Your database is ready to store all your amazing anime creations! 🎨✨
