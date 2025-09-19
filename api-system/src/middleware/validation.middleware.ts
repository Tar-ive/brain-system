import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { logger } from '../utils/logger';
import { ValidationError } from './error.middleware';

export interface ValidationRule {
  required?: boolean;
  type?: 'string' | 'number' | 'boolean' | 'email' | 'url' | 'uuid' | 'date' | 'array' | 'object';
  min?: number;
  max?: number;
  pattern?: RegExp;
  enum?: any[];
  custom?: (value: any) => boolean | string;
  sanitize?: (value: any) => any;
}

export interface ValidationSchema {
  [key: string]: ValidationRule;
}

export class ValidationMiddleware {
  /**
   * Validate request body against schema
   */
  public static validateBody(schema: ValidationSchema) {
    return (req: Request, res: Response, next: NextFunction): void => {
      try {
        const errors = this.validate(req.body, schema);

        if (errors.length > 0) {
          throw new ValidationError('Input validation failed', { errors });
        }

        // Sanitize data
        this.sanitize(req.body, schema);

        next();
      } catch (error) {
        if (error instanceof ValidationError) {
          res.status(400).json({
            success: false,
            error: {
              code: 'VALIDATION_ERROR',
              message: error.message,
              details: error.details
            },
            meta: {
              timestamp: new Date().toISOString(),
              request_id: uuidv4()
            }
          });
        } else {
          this.handleUnexpectedError(error, res);
        }
      }
    };
  }

  /**
   * Validate request query parameters
   */
  public static validateQuery(schema: ValidationSchema) {
    return (req: Request, res: Response, next: NextFunction): void => {
      try {
        const errors = this.validate(req.query, schema);

        if (errors.length > 0) {
          throw new ValidationError('Query validation failed', { errors });
        }

        // Sanitize data
        this.sanitize(req.query, schema);

        next();
      } catch (error) {
        if (error instanceof ValidationError) {
          res.status(400).json({
            success: false,
            error: {
              code: 'VALIDATION_ERROR',
              message: error.message,
              details: error.details
            },
            meta: {
              timestamp: new Date().toISOString(),
              request_id: uuidv4()
            }
          });
        } else {
          this.handleUnexpectedError(error, res);
        }
      }
    };
  }

  /**
   * Validate request parameters
   */
  public static validateParams(schema: ValidationSchema) {
    return (req: Request, res: Response, next: NextFunction): void => {
      try {
        const errors = this.validate(req.params, schema);

        if (errors.length > 0) {
          throw new ValidationError('Parameter validation failed', { errors });
        }

        // Sanitize data
        this.sanitize(req.params, schema);

        next();
      } catch (error) {
        if (error instanceof ValidationError) {
          res.status(400).json({
            success: false,
            error: {
              code: 'VALIDATION_ERROR',
              message: error.message,
              details: error.details
            },
            meta: {
              timestamp: new Date().toISOString(),
              request_id: uuidv4()
            }
          });
        } else {
          this.handleUnexpectedError(error, res);
        }
      }
    };
  }

  /**
   * Validate data against schema
   */
  private static validate(data: any, schema: ValidationSchema): Array<{ field: string; message: string }> {
    const errors: Array<{ field: string; message: string }> = [];

    for (const [field, rules] of Object.entries(schema)) {
      const value = data[field];
      const fieldPath = field;

      // Check required fields
      if (rules.required && (value === undefined || value === null || value === '')) {
        errors.push({ field: fieldPath, message: `${field} is required` });
        continue;
      }

      // Skip validation for optional fields that are not provided
      if (!rules.required && (value === undefined || value === null)) {
        continue;
      }

      // Type validation
      if (rules.type && !this.validateType(value, rules.type)) {
        errors.push({ field: fieldPath, message: `${field} must be of type ${rules.type}` });
        continue;
      }

      // String validations
      if (rules.type === 'string' && typeof value === 'string') {
        if (rules.min !== undefined && value.length < rules.min) {
          errors.push({ field: fieldPath, message: `${field} must be at least ${rules.min} characters long` });
        }
        if (rules.max !== undefined && value.length > rules.max) {
          errors.push({ field: fieldPath, message: `${field} must be no more than ${rules.max} characters long` });
        }
        if (rules.pattern && !rules.pattern.test(value)) {
          errors.push({ field: fieldPath, message: `${field} format is invalid` });
        }
      }

      // Number validations
      if (rules.type === 'number' && typeof value === 'number') {
        if (rules.min !== undefined && value < rules.min) {
          errors.push({ field: fieldPath, message: `${field} must be at least ${rules.min}` });
        }
        if (rules.max !== undefined && value > rules.max) {
          errors.push({ field: fieldPath, message: `${field} must be no more than ${rules.max}` });
        }
      }

      // Array validations
      if (rules.type === 'array' && Array.isArray(value)) {
        if (rules.min !== undefined && value.length < rules.min) {
          errors.push({ field: fieldPath, message: `${field} must have at least ${rules.min} items` });
        }
        if (rules.max !== undefined && value.length > rules.max) {
          errors.push({ field: fieldPath, message: `${field} must have no more than ${rules.max} items` });
        }
      }

      // Enum validation
      if (rules.enum && !rules.enum.includes(value)) {
        errors.push({ field: fieldPath, message: `${field} must be one of: ${rules.enum.join(', ')}` });
      }

      // Custom validation
      if (rules.custom) {
        const customResult = rules.custom(value);
        if (customResult !== true) {
          errors.push({ field: fieldPath, message: customResult || `${field} is invalid` });
        }
      }
    }

    return errors;
  }

  /**
   * Validate specific data types
   */
  private static validateType(value: any, type: string): boolean {
    switch (type) {
      case 'string':
        return typeof value === 'string';
      case 'number':
        return typeof value === 'number' && !isNaN(value);
      case 'boolean':
        return typeof value === 'boolean';
      case 'email':
        return typeof value === 'string' && this.validateEmail(value);
      case 'url':
        return typeof value === 'string' && this.validateUrl(value);
      case 'uuid':
        return typeof value === 'string' && this.validateUUID(value);
      case 'date':
        return typeof value === 'string' && !isNaN(Date.parse(value));
      case 'array':
        return Array.isArray(value);
      case 'object':
        return typeof value === 'object' && value !== null && !Array.isArray(value);
      default:
        return true;
    }
  }

  /**
   * Validate email format
   */
  private static validateEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  /**
   * Validate URL format
   */
  private static validateUrl(url: string): boolean {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Validate UUID format
   */
  private static validateUUID(uuid: string): boolean {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    return uuidRegex.test(uuid);
  }

  /**
   * Sanitize data according to schema rules
   */
  private static sanitize(data: any, schema: ValidationSchema): void {
    for (const [field, rules] of Object.entries(schema)) {
      if (data[field] !== undefined && rules.sanitize) {
        data[field] = rules.sanitize(data[field]);
      }
    }
  }

  /**
   * Handle unexpected validation errors
   */
  private static handleUnexpectedError(error: any, res: Response): void {
    logger.error('Unexpected validation error', { error });

    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: 'Validation service unavailable'
      },
      meta: {
        timestamp: new Date().toISOString(),
        request_id: uuidv4()
      }
    });
  }

  /**
   * Common validation schemas
   */
  public static schemas = {
    user: {
      email: {
        required: true,
        type: 'email'
      },
      username: {
        required: true,
        type: 'string',
        min: 3,
        max: 50,
        pattern: /^[a-zA-Z0-9_]+$/
      },
      password: {
        required: true,
        type: 'string',
        min: 8,
        max: 100,
        pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/
      },
      firstName: {
        required: false,
        type: 'string',
        max: 100
      },
      lastName: {
        required: false,
        type: 'string',
        max: 100
      },
      phone: {
        required: false,
        type: 'string',
        pattern: /^\+?[1-9]\d{1,14}$/
      }
    },

    item: {
      title: {
        required: true,
        type: 'string',
        min: 1,
        max: 255
      },
      description: {
        required: false,
        type: 'string',
        max: 5000
      },
      content: {
        required: false,
        type: 'string',
        max: 100000
      },
      categoryId: {
        required: false,
        type: 'uuid'
      },
      status: {
        required: false,
        type: 'string',
        enum: ['draft', 'published', 'archived']
      },
      visibility: {
        required: false,
        type: 'string',
        enum: ['public', 'private', 'protected']
      }
    },

    pagination: {
      page: {
        required: false,
        type: 'number',
        min: 1,
        custom: (value) => value === Math.floor(value) || 'Page must be an integer'
      },
      limit: {
        required: false,
        type: 'number',
        min: 1,
        max: 100,
        custom: (value) => value === Math.floor(value) || 'Limit must be an integer'
      }
    },

    search: {
      q: {
        required: true,
        type: 'string',
        min: 1,
        max: 100
      },
      page: {
        required: false,
        type: 'number',
        min: 1
      },
      limit: {
        required: false,
        type: 'number',
        min: 1,
        max: 100
      }
    },

    comment: {
      content: {
        required: true,
        type: 'string',
        min: 1,
        max: 5000
      },
      parentId: {
        required: false,
        type: 'uuid'
      }
    },

    apiKey: {
      name: {
        required: true,
        type: 'string',
        min: 1,
        max: 100
      },
      permissions: {
        required: true,
        type: 'array',
        min: 1
      },
      rateLimit: {
        required: false,
        type: 'number',
        min: 1,
        max: 10000
      },
      expiresAt: {
        required: false,
        type: 'date'
      }
    }
  };

  /**
   * File upload validation
   */
  public static validateFileUpload(options: {
    allowedMimeTypes?: string[];
    maxSize?: number;
    maxFiles?: number;
    requiredFields?: string[];
  } = {}) {
    const {
      allowedMimeTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
      maxSize = 10 * 1024 * 1024, // 10MB
      maxFiles = 1,
      requiredFields = []
    } = options;

    return (req: Request, res: Response, next: NextFunction): void => {
      try {
        if (!req.file && !req.files) {
          if (requiredFields.length > 0) {
            throw new ValidationError('File upload is required', {
              required: requiredFields
            });
          }
          next();
          return;
        }

        const files = req.files || (req.file ? [req.file] : []);

        // Check number of files
        if (files.length > maxFiles) {
          throw new ValidationError(`Maximum ${maxFiles} files allowed`, {
            uploaded: files.length,
            maxAllowed: maxFiles
          });
        }

        // Validate each file
        for (const file of files) {
          // Check file size
          if (file.size > maxSize) {
            throw new ValidationError(`File size exceeds ${maxSize / (1024 * 1024)}MB limit`, {
              fileSize: file.size,
              maxSize: maxSize
            });
          }

          // Check MIME type
          if (!allowedMimeTypes.includes(file.mimetype)) {
            throw new ValidationError('File type not allowed', {
              mimeTypes: allowedMimeTypes,
              provided: file.mimetype
            });
          }
        }

        next();
      } catch (error) {
        if (error instanceof ValidationError) {
          res.status(400).json({
            success: false,
            error: {
              code: 'VALIDATION_ERROR',
              message: error.message,
              details: error.details
            },
            meta: {
              timestamp: new Date().toISOString(),
              request_id: uuidv4()
            }
          });
        } else {
          this.handleUnexpectedError(error, res);
        }
      }
    };
  }
}