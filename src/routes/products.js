const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/auth');
const { validate, validateQuery } = require('../middleware/validation');
const { schemas } = require('../middleware/validation');
const {
  createProduct,
  getAllProducts,
  getProductById,
  updateProduct,
  deleteProduct,
  updateStock,
  getProductsByCategory,
  searchProducts
} = require('../controllers/productController');

// Create new product
router.post('/', authenticate, validate(schemas.product.create), createProduct);

// Get all products with filtering, pagination, and sorting
router.get('/', validateQuery({...schemas.query.pagination, ...schemas.query.sort, ...schemas.query.search}), getAllProducts);

// Get product by ID
router.get('/:id', getProductById);

// Update product
router.put('/:id', authenticate, validate(schemas.product.update), updateProduct);

// Delete product (soft delete)
router.delete('/:id', authenticate, deleteProduct);

// Update product stock
router.patch('/:id/stock', authenticate, updateStock);

// Get products by category
router.get('/category/:category', getProductsByCategory);

// Search products
router.get('/search', searchProducts);

module.exports = router;