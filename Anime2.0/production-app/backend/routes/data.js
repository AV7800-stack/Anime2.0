const express = require('express');
const mongoose = require('mongoose');
const { authenticate, optionalAuth } = require('../middleware/auth');

const router = express.Router();

// Sample data schema for demonstration
const DataSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true,
    trim: true
  },
  description: {
    type: String,
    required: true
  },
  category: {
    type: String,
    enum: ['anime', 'manga', 'character', 'story', 'video'],
    required: true
  },
  tags: [String],
  imageUrl: String,
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  isPublic: {
    type: Boolean,
    default: true
  },
  likes: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  }],
  views: {
    type: Number,
    default: 0
  }
}, {
  timestamps: true
});

const Data = mongoose.model('Data', DataSchema);

// @route   GET /api/data
// @desc    Get all data with pagination and filtering
// @access   Public
router.get('/', optionalAuth, async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;
    const { category, search, sortBy } = req.query;
    
    // Build query
    const query = { isPublic: true };
    
    if (category) {
      query.category = category;
    }
    
    if (search) {
      query.$or = [
        { title: { $regex: search, $options: 'i' } },
        { description: { $regex: search, $options: 'i' } },
        { tags: { $in: [new RegExp(search, 'i')] } }
      ];
    }
    
    // Build sort
    let sort = { createdAt: -1 };
    if (sortBy === 'popular') {
      sort = { likes: -1, views: -1 };
    } else if (sortBy === 'views') {
      sort = { views: -1 };
    }
    
    const data = await Data.find(query)
      .populate('createdBy', 'name avatar')
      .sort(sort)
      .skip(skip)
      .limit(limit);
    
    const total = await Data.countDocuments(query);
    
    res.json({
      success: true,
      data: {
        items: data,
        pagination: {
          page,
          limit,
          total,
          pages: Math.ceil(total / limit)
        }
      }
    });
    
  } catch (error) {
    console.error('Get data error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
});

// @route   GET /api/data/:id
// @desc    Get single data item
// @access   Public
router.get('/:id', optionalAuth, async (req, res) => {
  try {
    const data = await Data.findById(req.params.id)
      .populate('createdBy', 'name avatar')
      .populate('likes', 'name avatar');
    
    if (!data) {
      return res.status(404).json({
        success: false,
        message: 'Data not found'
      });
    }
    
    // Increment views
    data.views += 1;
    await data.save();
    
    res.json({
      success: true,
      data: { item: data }
    });
    
  } catch (error) {
    console.error('Get data item error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
});

// @route   POST /api/data
// @desc    Create new data item
// @access   Private
router.post('/', authenticate, async (req, res) => {
  try {
    const { title, description, category, tags, imageUrl, isPublic } = req.body;
    
    // Validation
    if (!title || !description || !category) {
      return res.status(400).json({
        success: false,
        message: 'Title, description, and category are required'
      });
    }
    
    const newItem = new Data({
      title,
      description,
      category,
      tags: tags || [],
      imageUrl,
      isPublic: isPublic !== undefined ? isPublic : true,
      createdBy: req.user._id
    });
    
    await newItem.save();
    
    const populatedItem = await Data.findById(newItem._id)
      .populate('createdBy', 'name avatar');
    
    res.status(201).json({
      success: true,
      message: 'Data created successfully',
      data: { item: populatedItem }
    });
    
  } catch (error) {
    console.error('Create data error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
});

// @route   PUT /api/data/:id
// @desc    Update data item
// @access   Private
router.put('/:id', authenticate, async (req, res) => {
  try {
    const data = await Data.findById(req.params.id);
    
    if (!data) {
      return res.status(404).json({
        success: false,
        message: 'Data not found'
      });
    }
    
    // Check ownership
    if (data.createdBy.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
      return res.status(403).json({
        success: false,
        message: 'Access denied'
      });
    }
    
    const { title, description, category, tags, imageUrl, isPublic } = req.body;
    
    // Update fields
    if (title) data.title = title;
    if (description) data.description = description;
    if (category) data.category = category;
    if (tags) data.tags = tags;
    if (imageUrl !== undefined) data.imageUrl = imageUrl;
    if (isPublic !== undefined) data.isPublic = isPublic;
    
    await data.save();
    
    const updatedData = await Data.findById(data._id)
      .populate('createdBy', 'name avatar');
    
    res.json({
      success: true,
      message: 'Data updated successfully',
      data: { item: updatedData }
    });
    
  } catch (error) {
    console.error('Update data error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
});

// @route   DELETE /api/data/:id
// @desc    Delete data item
// @access   Private
router.delete('/:id', authenticate, async (req, res) => {
  try {
    const data = await Data.findById(req.params.id);
    
    if (!data) {
      return res.status(404).json({
        success: false,
        message: 'Data not found'
      });
    }
    
    // Check ownership
    if (data.createdBy.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
      return res.status(403).json({
        success: false,
        message: 'Access denied'
      });
    }
    
    await Data.findByIdAndDelete(req.params.id);
    
    res.json({
      success: true,
      message: 'Data deleted successfully'
    });
    
  } catch (error) {
    console.error('Delete data error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
});

// @route   POST /api/data/:id/like
// @desc    Like/unlike data item
// @access   Private
router.post('/:id/like', authenticate, async (req, res) => {
  try {
    const data = await Data.findById(req.params.id);
    
    if (!data) {
      return res.status(404).json({
        success: false,
        message: 'Data not found'
      });
    }
    
    const userId = req.user._id;
    const isLiked = data.likes.includes(userId);
    
    if (isLiked) {
      // Unlike
      data.likes.pull(userId);
    } else {
      // Like
      data.likes.push(userId);
    }
    
    await data.save();
    
    res.json({
      success: true,
      message: isLiked ? 'Unliked successfully' : 'Liked successfully',
      data: {
        isLiked: !isLiked,
        likesCount: data.likes.length
      }
    });
    
  } catch (error) {
    console.error('Like data error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
});

// @route   GET /api/data/categories
// @desc    Get all categories
// @access   Public
router.get('/categories/all', async (req, res) => {
  try {
    const categories = await Data.distinct('category');
    
    res.json({
      success: true,
      data: { categories }
    });
    
  } catch (error) {
    console.error('Get categories error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
});

module.exports = router;
