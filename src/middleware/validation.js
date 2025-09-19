const Joi = require('joi');
const logger = require('../utils/logger');

// Generic validation middleware
const validate = (schema) => {
  return (req, res, next) => {
    const { error } = schema.validate(req.body, {
      abortEarly: false,
      allowUnknown: true,
      stripUnknown: false
    });

    if (error) {
      const errorMessage = error.details.map(detail => detail.message).join(', ');
      logger.warn(`Validation error: ${errorMessage}`, {
        path: req.path,
        method: req.method,
        body: req.body
      });

      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: error.details.map(detail => ({
          field: detail.path.join('.'),
          message: detail.message
        }))
      });
    }

    next();
  };
};

// Query parameter validation middleware
const validateQuery = (schema) => {
  return (req, res, next) => {
    const { error } = schema.validate(req.query, {
      abortEarly: false,
      allowUnknown: true,
      stripUnknown: false
    });

    if (error) {
      const errorMessage = error.details.map(detail => detail.message).join(', ');
      logger.warn(`Query validation error: ${errorMessage}`, {
        path: req.path,
        method: req.method,
        query: req.query
      });

      return res.status(400).json({
        success: false,
        message: 'Query validation failed',
        errors: error.details.map(detail => ({
          field: detail.path.join('.'),
          message: detail.message
        }))
      });
    }

    next();
  };
};

// Validation schemas
const schemas = {
  // User validation schemas
  user: {
    register: Joi.object({
      username: Joi.string()
        .alphanum()
        .min(3)
        .max(30)
        .required()
        .messages({
          'string.alphanum': 'Username must contain only alphanumeric characters',
          'string.min': 'Username must be at least 3 characters long',
          'string.max': 'Username must be at most 30 characters long',
          'any.required': 'Username is required'
        }),

      email: Joi.string()
        .email()
        .required()
        .messages({
          'string.email': 'Please provide a valid email address',
          'any.required': 'Email is required'
        }),

      password: Joi.string()
        .min(8)
        .max(128)
        .pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
        .required()
        .messages({
          'string.min': 'Password must be at least 8 characters long',
          'string.max': 'Password must be at most 128 characters long',
          'string.pattern.base': 'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character',
          'any.required': 'Password is required'
        }),

      firstName: Joi.string()
        .min(2)
        .max(50)
        .required()
        .messages({
          'string.min': 'First name must be at least 2 characters long',
          'string.max': 'First name must be at most 50 characters long',
          'any.required': 'First name is required'
        }),

      lastName: Joi.string()
        .min(2)
        .max(50)
        .required()
        .messages({
          'string.min': 'Last name must be at least 2 characters long',
          'string.max': 'Last name must be at most 50 characters long',
          'any.required': 'Last name is required'
        })
    }),

    login: Joi.object({
      email: Joi.string()
        .email()
        .required()
        .messages({
          'string.email': 'Please provide a valid email address',
          'any.required': 'Email is required'
        }),

      password: Joi.string()
        .required()
        .messages({
          'any.required': 'Password is required'
        })
    }),

    update: Joi.object({
      username: Joi.string()
        .alphanum()
        .min(3)
        .max(30)
        .messages({
          'string.alphanum': 'Username must contain only alphanumeric characters',
          'string.min': 'Username must be at least 3 characters long',
          'string.max': 'Username must be at most 30 characters long'
        }),

      email: Joi.string()
        .email()
        .messages({
          'string.email': 'Please provide a valid email address'
        }),

      firstName: Joi.string()
        .min(2)
        .max(50)
        .messages({
          'string.min': 'First name must be at least 2 characters long',
          'string.max': 'First name must be at most 50 characters long'
        }),

      lastName: Joi.string()
        .min(2)
        .max(50)
        .messages({
          'string.min': 'Last name must be at least 2 characters long',
          'string.max': 'Last name must be at most 50 characters long'
        }),

      profileImage: Joi.string().uri()
    }),

    changePassword: Joi.object({
      currentPassword: Joi.string()
        .required()
        .messages({
          'any.required': 'Current password is required'
        }),

      newPassword: Joi.string()
        .min(8)
        .max(128)
        .pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
        .required()
        .messages({
          'string.min': 'Password must be at least 8 characters long',
          'string.max': 'Password must be at most 128 characters long',
          'string.pattern.base': 'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character',
          'any.required': 'New password is required'
        })
    })
  },

  // Product validation schemas
  product: {
    create: Joi.object({
      name: Joi.string()
        .min(2)
        .max(200)
        .required()
        .messages({
          'string.min': 'Product name must be at least 2 characters long',
          'string.max': 'Product name must be at most 200 characters long',
          'any.required': 'Product name is required'
        }),

      description: Joi.string()
        .max(1000)
        .messages({
          'string.max': 'Description must be at most 1000 characters long'
        }),

      price: Joi.number()
        .positive()
        .precision(2)
        .required()
        .messages({
          'number.positive': 'Price must be a positive number',
          'number.precision': 'Price can have at most 2 decimal places',
          'any.required': 'Price is required'
        }),

      category: Joi.string()
        .max(50)
        .required()
        .messages({
          'string.max': 'Category must be at most 50 characters long',
          'any.required': 'Category is required'
        }),

      stock: Joi.number()
        .integer()
        .min(0)
        .default(0)
        .messages({
          'number.integer': 'Stock must be an integer',
          'number.min': 'Stock cannot be negative'
        }),

      sku: Joi.string()
        .alphanum()
        .max(50)
        .messages({
          'string.alphanum': 'SKU must contain only alphanumeric characters',
          'string.max': 'SKU must be at most 50 characters long'
        })
    }),

    update: Joi.object({
      name: Joi.string()
        .min(2)
        .max(200)
        .messages({
          'string.min': 'Product name must be at least 2 characters long',
          'string.max': 'Product name must be at most 200 characters long'
        }),

      description: Joi.string()
        .max(1000)
        .messages({
          'string.max': 'Description must be at most 1000 characters long'
        }),

      price: Joi.number()
        .positive()
        .precision(2)
        .messages({
          'number.positive': 'Price must be a positive number',
          'number.precision': 'Price can have at most 2 decimal places'
        }),

      category: Joi.string()
        .max(50)
        .messages({
          'string.max': 'Category must be at most 50 characters long'
        }),

      stock: Joi.number()
        .integer()
        .min(0)
        .messages({
          'number.integer': 'Stock must be an integer',
          'number.min': 'Stock cannot be negative'
        }),

      sku: Joi.string()
        .alphanum()
        .max(50)
        .messages({
          'string.alphanum': 'SKU must contain only alphanumeric characters',
          'string.max': 'SKU must be at most 50 characters long'
        })
    })
  },

  // Query parameter schemas
  query: {
    pagination: Joi.object({
      page: Joi.number()
        .integer()
        .min(1)
        .default(1)
        .messages({
          'number.integer': 'Page must be an integer',
          'number.min': 'Page must be at least 1'
        }),

      limit: Joi.number()
        .integer()
        .min(1)
        .max(100)
        .default(10)
        .messages({
          'number.integer': 'Limit must be an integer',
          'number.min': 'Limit must be at least 1',
          'number.max': 'Limit cannot exceed 100'
        })
    }),

    sort: Joi.object({
      sortBy: Joi.string()
        .default('createdAt')
        .messages({
          'string.base': 'Sort by must be a string'
        }),

      sortOrder: Joi.string()
        .valid('asc', 'desc')
        .default('desc')
        .messages({
          'any.only': 'Sort order must be either "asc" or "desc"'
        })
    }),

    search: Joi.object({
      search: Joi.string()
        .max(100)
        .messages({
          'string.max': 'Search term must be at most 100 characters long'
        })
    })
  }
};

module.exports = {
  validate,
  validateQuery,
  schemas
};