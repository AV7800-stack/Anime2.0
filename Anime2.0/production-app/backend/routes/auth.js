const express = require('express');
const jwt = require('jsonwebtoken');
const validator = require('validator');
const User = require('../models/User');
const { authenticate } = require('../middleware/auth');

const router = express.Router();

// Helper function to generate JWT token
const generateToken = (id) => {
  return jwt.sign({ id }, process.env.JWT_SECRET, {
    expiresIn: '30d'
  });
};

// Helper function to validate input
const validateInput = (data, required) => {
  const errors = [];
  
  for (const field of required) {
    if (!data[field]) {
      errors.push(`${field} is required`);
    } else {
      // Email validation
      if (field === 'email' && !validator.isEmail(data[field])) {
        errors.push('Please provide a valid email');
      }
      // Password validation
      if (field === 'password' && data[field].length < 6) {
        errors.push('Password must be at least 6 characters');
      }
      // Name validation
      if (field === 'name' && data[field].length < 2) {
        errors.push('Name must be at least 2 characters');
      }
    }
  }
  
  return errors;
};

// @route   POST /api/auth/register
// @desc    Register a new user
// @access   Public
router.post('/register', async (req, res) => {
  try {
    const { name, email, password } = req.body;
    
    // Validate input
    const validationErrors = validateInput(req.body, ['name', 'email', 'password']);
    if (validationErrors.length > 0) {
      return res.status(400).json({
        success: false,
        message: 'Validation Error',
        errors: validationErrors
      });
    }
    
    // Check if user already exists
    const existingUser = await User.findByEmail(email);
    if (existingUser) {
      return res.status(400).json({
        success: false,
        message: 'User with this email already exists'
      });
    }
    
    // Create new user
    const user = new User({
      name,
      email,
      password
    });
    
    await user.save();
    
    // Generate token
    const token = generateToken(user._id);
    
    res.status(201).json({
      success: true,
      message: 'User registered successfully',
      data: {
        user: {
          id: user._id,
          name: user.name,
          email: user.email,
          role: user.role,
          avatar: user.avatar
        },
        token
      }
    });
    
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error during registration'
    });
  }
});

// @route   POST /api/auth/login
// @desc    Login user
// @access   Public
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Validate input
    const validationErrors = validateInput(req.body, ['email', 'password']);
    if (validationErrors.length > 0) {
      return res.status(400).json({
        success: false,
        message: 'Validation Error',
        errors: validationErrors
      });
    }
    
    // Check if user exists
    const user = await User.findByEmail(email);
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Invalid email or password'
      });
    }
    
    // Check if account is active
    if (!user.isActive) {
      return res.status(401).json({
        success: false,
        message: 'Account is deactivated. Please contact support.'
      });
    }
    
    // Check password
    const isMatch = await user.comparePassword(password);
    if (!isMatch) {
      return res.status(401).json({
        success: false,
        message: 'Invalid email or password'
      });
    }
    
    // Update last login
    user.lastLogin = new Date();
    await user.save();
    
    // Generate token
    const token = generateToken(user._id);
    
    res.json({
      success: true,
      message: 'Login successful',
      data: {
        user: {
          id: user._id,
          name: user.name,
          email: user.email,
          role: user.role,
          avatar: user.avatar,
          lastLogin: user.lastLogin
        },
        token
      }
    });
    
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error during login'
    });
  }
});

// @route   GET /api/auth/me
// @desc    Get current user
// @access   Private
router.get('/me', authenticate, async (req, res) => {
  try {
    res.json({
      success: true,
      data: {
        user: {
          id: req.user._id,
          name: req.user.name,
          email: req.user.email,
          role: req.user.role,
          avatar: req.user.avatar,
          lastLogin: req.user.lastLogin,
          createdAt: req.user.createdAt
        }
      }
    });
  } catch (error) {
    console.error('Get user error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
});

// @route   PUT /api/auth/profile
// @desc    Update user profile
// @access   Private
router.put('/profile', authenticate, async (req, res) => {
  try {
    const { name, avatar } = req.body;
    const updateData = {};
    
    if (name) {
      if (name.length < 2) {
        return res.status(400).json({
          success: false,
          message: 'Name must be at least 2 characters'
        });
      }
      updateData.name = name;
    }
    
    if (avatar) {
      updateData.avatar = avatar;
    }
    
    const user = await User.findByIdAndUpdate(
      req.user._id,
      updateData,
      { new: true, runValidators: true }
    );
    
    res.json({
      success: true,
      message: 'Profile updated successfully',
      data: {
        user: {
          id: user._id,
          name: user.name,
          email: user.email,
          role: user.role,
          avatar: user.avatar
        }
      }
    });
    
  } catch (error) {
    console.error('Profile update error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error during profile update'
    });
  }
});

// @route   POST /api/auth/logout
// @desc    Logout user (client-side token removal)
// @access   Private
router.post('/logout', authenticate, async (req, res) => {
  try {
    // In a real-world app, you might want to implement token blacklisting
    // For now, we'll just return success as token removal is handled client-side
    res.json({
      success: true,
      message: 'Logout successful'
    });
  } catch (error) {
    console.error('Logout error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error during logout'
    });
  }
});

module.exports = router;
