const express = require('express');
const router = express.Router();
const { validate } = require('../middleware/validation');
const { authenticate } = require('../middleware/auth');
const { schemas } = require('../middleware/validation');
const {
  register,
  login,
  refreshToken,
  logout,
  getCurrentUser
} = require('../controllers/authController');

// Register new user
router.post('/register', validate(schemas.user.register), register);

// Login user
router.post('/login', validate(schemas.user.login), login);

// Refresh access token
router.post('/refresh', refreshToken);

// Logout user
router.post('/logout', authenticate, logout);

// Get current user profile
router.get('/me', authenticate, getCurrentUser);

module.exports = router;