const { Product } = require('../models/Product');
const logger = require('../utils/logger');

// Create new product
const createProduct = async (req, res) => {
  try {
    const { name, description, price, category, stock, sku, images, tags } = req.body;

    const product = new Product({
      name,
      description,
      price,
      category,
      stock: stock || 0,
      sku,
      images: images || [],
      tags: tags || [],
      createdBy: req.user.id,
      updatedBy: req.user.id
    });

    await product.save();

    logger.info(`Product created: ${product.name} by ${req.user.email}`);

    res.status(201).json({
      success: true,
      message: 'Product created successfully',
      data: {
        product
      }
    });

  } catch (error) {
    logger.error('Create product error:', error);

    // Handle duplicate SKU error
    if (error.code === 11000 && error.keyPattern?.sku) {
      return res.status(400).json({
        success: false,
        message: 'SKU already exists'
      });
    }

    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

// Get all products with filtering, pagination, and sorting
const getAllProducts = async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;
    const sortBy = req.query.sortBy || 'createdAt';
    const sortOrder = req.query.sortOrder === 'asc' ? 1 : -1;

    // Build query
    let query = { isActive: true };

    // Search functionality
    if (req.query.search) {
      query = Product.find({
        $and: [
          { isActive: true },
          {
            $or: [
              { name: { $regex: req.query.search, $options: 'i' } },
              { description: { $regex: req.query.search, $options: 'i' } },
              { category: { $regex: req.query.search, $options: 'i' } },
              { tags: { $in: [new RegExp(req.query.search, 'i')] } }
            ]
          }
        ]
      });
    } else {
      query = Product.find(query);
    }

    // Filter by category
    if (req.query.category) {
      query = query.where('category', new RegExp(req.query.category, 'i'));
    }

    // Filter by price range
    if (req.query.minPrice || req.query.maxPrice) {
      if (req.query.minPrice) {
        query = query.where('price').gte(parseFloat(req.query.minPrice));
      }
      if (req.query.maxPrice) {
        query = query.where('price').lte(parseFloat(req.query.maxPrice));
      }
    }

    // Filter by in stock
    if (req.query.inStock === 'true') {
      query = query.where('stock').gt(0);
    }

    // Filter by tags
    if (req.query.tags) {
      const tagsArray = req.query.tags.split(',');
      query = query.where('tags').in(tagsArray);
    }

    // Apply sorting
    query = query.sort({ [sortBy]: sortOrder });

    // Apply pagination
    query = query.skip(skip).limit(limit);

    // Populate created by and updated by
    query = query.populate('createdBy', 'username firstName lastName')
      .populate('updatedBy', 'username firstName lastName');

    const products = await query;
    const total = await Product.countDocuments({ isActive: true });

    res.status(200).json({
      success: true,
      data: {
        products,
        pagination: {
          page,
          limit,
          total,
          pages: Math.ceil(total / limit)
        },
        filters: {
          search: req.query.search,
          category: req.query.category,
          minPrice: req.query.minPrice,
          maxPrice: req.query.maxPrice,
          inStock: req.query.inStock,
          tags: req.query.tags,
          sortBy,
          sortOrder: req.query.sortOrder || 'desc'
        }
      }
    });

  } catch (error) {
    logger.error('Get all products error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

// Get product by ID
const getProductById = async (req, res) => {
  try {
    const product = await Product.findById(req.params.id)
      .populate('createdBy', 'username firstName lastName')
      .populate('updatedBy', 'username firstName lastName');

    if (!product) {
      return res.status(404).json({
        success: false,
        message: 'Product not found'
      });
    }

    res.status(200).json({
      success: true,
      data: {
        product
      }
    });

  } catch (error) {
    logger.error('Get product by ID error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

// Update product
const updateProduct = async (req, res) => {
  try {
    const { name, description, price, category, stock, sku, images, tags } = req.body;

    const product = await Product.findById(req.params.id);

    if (!product) {
      return res.status(404).json({
        success: false,
        message: 'Product not found'
      });
    }

    // Check if SKU already exists (if changing)
    if (sku && sku !== product.sku) {
      const existingProduct = await Product.findOne({ sku });
      if (existingProduct) {
        return res.status(400).json({
          success: false,
          message: 'SKU already exists'
        });
      }
    }

    // Update product fields
    if (name) product.name = name;
    if (description !== undefined) product.description = description;
    if (price !== undefined) product.price = price;
    if (category) product.category = category;
    if (stock !== undefined) product.stock = stock;
    if (sku !== undefined) product.sku = sku;
    if (images) product.images = images;
    if (tags) product.tags = tags;

    product.updatedBy = req.user.id;
    await product.save();

    logger.info(`Product updated: ${product.name} by ${req.user.email}`);

    res.status(200).json({
      success: true,
      message: 'Product updated successfully',
      data: {
        product
      }
    });

  } catch (error) {
    logger.error('Update product error:', error);

    // Handle duplicate SKU error
    if (error.code === 11000 && error.keyPattern?.sku) {
      return res.status(400).json({
        success: false,
        message: 'SKU already exists'
      });
    }

    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

// Delete product
const deleteProduct = async (req, res) => {
  try {
    const product = await Product.findById(req.params.id);

    if (!product) {
      return res.status(404).json({
        success: false,
        message: 'Product not found'
      });
    }

    // Soft delete by setting isActive to false
    product.isActive = false;
    product.updatedBy = req.user.id;
    await product.save();

    logger.info(`Product deleted (soft): ${product.name} by ${req.user.email}`);

    res.status(200).json({
      success: true,
      message: 'Product deleted successfully'
    });

  } catch (error) {
    logger.error('Delete product error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

// Update product stock
const updateStock = async (req, res) => {
  try {
    const { quantity } = req.body;

    const product = await Product.findById(req.params.id);

    if (!product) {
      return res.status(404).json({
        success: false,
        message: 'Product not found'
      });
    }

    const newStock = product.stock + quantity;
    if (newStock < 0) {
      return res.status(400).json({
        success: false,
        message: 'Insufficient stock'
      });
    }

    product.stock = newStock;
    product.updatedBy = req.user.id;
    await product.save();

    logger.info(`Product stock updated: ${product.name} by ${req.user.email} (${quantity > 0 ? '+' : ''}${quantity})`);

    res.status(200).json({
      success: true,
      message: 'Stock updated successfully',
      data: {
        product
      }
    });

  } catch (error) {
    logger.error('Update stock error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

// Get products by category
const getProductsByCategory = async (req, res) => {
  try {
    const { category } = req.params;
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;

    const products = await Product.find({
      category: { $regex: category, $options: 'i' },
      isActive: true
    })
      .populate('createdBy', 'username firstName lastName')
      .populate('updatedBy', 'username firstName lastName')
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit);

    const total = await Product.countDocuments({
      category: { $regex: category, $options: 'i' },
      isActive: true
    });

    res.status(200).json({
      success: true,
      data: {
        products,
        category,
        pagination: {
          page,
          limit,
          total,
          pages: Math.ceil(total / limit)
        }
      }
    });

  } catch (error) {
    logger.error('Get products by category error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

// Search products
const searchProducts = async (req, res) => {
  try {
    const { q: query } = req.query;

    if (!query) {
      return res.status(400).json({
        success: false,
        message: 'Search query is required'
      });
    }

    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;

    const products = await Product.find({
      $or: [
        { name: { $regex: query, $options: 'i' } },
        { description: { $regex: query, $options: 'i' } },
        { category: { $regex: query, $options: 'i' } },
        { tags: { $in: [new RegExp(query, 'i')] } }
      ],
      isActive: true
    })
      .populate('createdBy', 'username firstName lastName')
      .populate('updatedBy', 'username firstName lastName')
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit);

    const total = await Product.countDocuments({
      $or: [
        { name: { $regex: query, $options: 'i' } },
        { description: { $regex: query, $options: 'i' } },
        { category: { $regex: query, $options: 'i' } },
        { tags: { $in: [new RegExp(query, 'i')] } }
      ],
      isActive: true
    });

    res.status(200).json({
      success: true,
      data: {
        products,
        searchQuery: query,
        pagination: {
          page,
          limit,
          total,
          pages: Math.ceil(total / limit)
        }
      }
    });

  } catch (error) {
    logger.error('Search products error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

module.exports = {
  createProduct,
  getAllProducts,
  getProductById,
  updateProduct,
  deleteProduct,
  updateStock,
  getProductsByCategory,
  searchProducts
};