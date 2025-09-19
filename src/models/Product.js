const mongoose = require('mongoose');

const productSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Product name is required'],
    trim: true,
    minlength: [2, 'Product name must be at least 2 characters long'],
    maxlength: [200, 'Product name must be at most 200 characters long']
  },
  description: {
    type: String,
    trim: true,
    maxlength: [1000, 'Description must be at most 1000 characters long'],
    default: ''
  },
  price: {
    type: Number,
    required: [true, 'Price is required'],
    min: [0, 'Price must be a positive number'],
    validate: {
      validator: function(value) {
        return value >= 0;
      },
      message: 'Price must be a positive number'
    }
  },
  category: {
    type: String,
    required: [true, 'Category is required'],
    trim: true,
    maxlength: [50, 'Category must be at most 50 characters long']
  },
  stock: {
    type: Number,
    required: [true, 'Stock is required'],
    min: [0, 'Stock cannot be negative'],
    default: 0,
    validate: {
      validator: function(value) {
        return Number.isInteger(value);
      },
      message: 'Stock must be an integer'
    }
  },
  sku: {
    type: String,
    trim: true,
    maxlength: [50, 'SKU must be at most 50 characters long'],
    unique: true,
    sparse: true
  },
  images: [{
    type: String,
    validate: {
      validator: function(value) {
        // Basic URL validation
        return /^https?:\/\/.+\.(jpg|jpeg|png|gif|webp)$/i.test(value);
      },
      message: 'Please provide a valid image URL'
    }
  }],
  tags: [{
    type: String,
    trim: true,
    maxlength: [30, 'Tags must be at most 30 characters long']
  }],
  isActive: {
    type: Boolean,
    default: true
  },
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  updatedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  }
}, {
  timestamps: true,
  toJSON: {
    virtuals: true
  }
});

// Virtual for discounted price
productSchema.virtual('discountedPrice').get(function() {
  // This can be extended to include discount logic
  return this.price;
});

// Virtual for availability status
productSchema.virtual('isInStock').get(function() {
  return this.stock > 0;
});

// Virtual for popularity score (can be based on orders, views, etc.)
productSchema.virtual('popularityScore').get(function() {
  // This can be extended to include actual popularity calculation
  return 0;
});

// Method to update stock
productSchema.methods.updateStock = function(quantity) {
  this.stock += quantity;
  if (this.stock < 0) {
    this.stock = 0;
  }
  return this.save();
};

// Method to check if product can be purchased
productSchema.methods.canBePurchased = function(quantity) {
  return this.stock >= quantity && this.isActive;
};

// Static method to find active products
productSchema.statics.findActive = function() {
  return this.find({ isActive: true });
};

// Static method to find products by category
productSchema.statics.findByCategory = function(category) {
  return this.find({ category, isActive: true });
};

// Static method to search products
productSchema.statics.search = function(query) {
  return this.find({
    $or: [
      { name: { $regex: query, $options: 'i' } },
      { description: { $regex: query, $options: 'i' } },
      { category: { $regex: query, $options: 'i' } },
      { tags: { $in: [new RegExp(query, 'i')] } }
    ],
    isActive: true
  });
};

// Indexes for better performance
productSchema.index({ name: 'text', description: 'text', category: 'text', tags: 'text' });
productSchema.index({ price: 1 });
productSchema.index({ category: 1 });
productSchema.index({ stock: 1 });
productSchema.index({ isActive: 1 });
productSchema.index({ createdBy: 1 });
productSchema.index({ createdAt: -1 });

// Pre-save middleware to validate stock is integer
productSchema.pre('save', function(next) {
  if (this.stock !== undefined) {
    this.stock = Math.round(this.stock);
  }
  next();
});

const Product = mongoose.model('Product', productSchema);

module.exports = Product;