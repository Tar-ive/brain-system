const express = require('express');
const router = express.Router();
const { authenticate, authorize } = require('../middleware/auth');
const { validate, validateQuery } = require('../middleware/validation');
const { schemas } = require('../middleware/validation');
const {
  getAllUsers,
  getUserById,
  updateUser,
  changePassword,
  deactivateUser,
  activateUser,
  deleteUser
} = require('../controllers/userController');

// Get all users (admin only)
router.get('/', authenticate, authorize('admin'), validateQuery(schemas.query.pagination), getAllUsers);

// Get user by ID
router.get('/:id', authenticate, getUserById);

// Update user profile
router.put('/:id', authenticate, validate(schemas.user.update), updateUser);

// Change password
router.post('/change-password', authenticate, validate(schemas.user.changePassword), changePassword);

// Deactivate user (admin only)
router.patch('/:id/deactivate', authenticate, authorize('admin'), deactivateUser);

// Activate user (admin only)
router.patch('/:id/activate', authenticate, authorize('admin'), activateUser);

// Delete user (admin only)
router.delete('/:id', authenticate, authorize('admin'), deleteUser);

module.exports = router;