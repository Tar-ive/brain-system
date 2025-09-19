import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { logger } from '../utils/logger';

export interface ErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: any;
    stack?: string;
  };
  meta: {
    timestamp: string;
    request_id: string;
  };
}

export class AppError extends Error {
  public statusCode: number;
  public code: string;
  public details?: any;

  constructor(message: string, statusCode: number = 500, code: string = 'INTERNAL_ERROR', details?: any) {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
    this.details = details;
    this.name = this.constructor.name;
    Error.captureStackTrace(this, this.constructor);
  }
}

export class ValidationError extends AppError {
  constructor(message: string, details?: any) {
    super(message, 400, 'VALIDATION_ERROR', details);
  }
}

export class UnauthorizedError extends AppError {
  constructor(message: string = 'Unauthorized') {
    super(message, 401, 'UNAUTHORIZED');
  }
}

export class ForbiddenError extends AppError {
  constructor(message: string = 'Forbidden') {
    super(message, 403, 'FORBIDDEN');
  }
}

export class NotFoundError extends AppError {
  constructor(message: string = 'Resource not found') {
    super(message, 404, 'NOT_FOUND');
  }
}

export class ConflictError extends AppError {
  constructor(message: string = 'Resource conflict') {
    super(message, 409, 'CONFLICT');
  }
}

export class RateLimitError extends AppError {
  constructor(message: string = 'Too many requests') {
    super(message, 429, 'TOO_MANY_REQUESTS');
  }
}

export class DatabaseError extends AppError {
  constructor(message: string, details?: any) {
    super(message, 500, 'DATABASE_ERROR', details);
  }
}

export class ExternalServiceError extends AppError {
  constructor(message: string, serviceName: string, details?: any) {
    super(message, 502, 'EXTERNAL_SERVICE_ERROR', { ...details, serviceName });
  }
}

export class ErrorMiddleware {
  /**
   * Global error handling middleware
   */
  public static handleError = (
    error: Error,
    req: Request,
    res: Response,
    next: NextFunction
  ): void => {
    const requestId = (req as any).requestId || uuidv4();

    // Log the error
    ErrorMiddleware.logError(error, req, requestId);

    // Handle different types of errors
    if (error instanceof AppError) {
      ErrorMiddleware.handleAppError(error, res, requestId);
    } else if (error.name === 'ValidationError') {
      ErrorMiddleware.handleValidationError(error, res, requestId);
    } else if (error.name === 'CastError') {
      ErrorMiddleware.handleCastError(error, res, requestId);
    } else if (error.name === 'SyntaxError') {
      ErrorMiddleware.handleSyntaxError(error, res, requestId);
    } else if (error.name === 'MulterError') {
      ErrorMiddleware.handleMulterError(error, res, requestId);
    } else {
      ErrorMiddleware.handleGenericError(error, res, requestId);
    }
  };

  /**
   * Handle application-specific errors
   */
  private static handleAppError(error: AppError, res: Response, requestId: string): void {
    const response: ErrorResponse = {
      success: false,
      error: {
        code: error.code,
        message: error.message,
        details: error.details
      },
      meta: {
        timestamp: new Date().toISOString(),
        request_id: requestId
      }
    };

    // Include stack trace in development
    if (process.env.NODE_ENV === 'development') {
      response.error.stack = error.stack;
    }

    res.status(error.statusCode).json(response);
  }

  /**
   * Handle validation errors
   */
  private static handleValidationError(error: any, res: Response, requestId: string): void {
    const response: ErrorResponse = {
      success: false,
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Input validation failed',
        details: error.details || error.errors || error.message
      },
      meta: {
        timestamp: new Date().toISOString(),
        request_id: requestId
      }
    };

    res.status(400).json(response);
  }

  /**
   * Handle cast errors (Mongoose/Database)
   */
  private static handleCastError(error: any, res: Response, requestId: string): void {
    const response: ErrorResponse = {
      success: false,
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Invalid ID format',
        details: {
          field: error.path,
          value: error.value
        }
      },
      meta: {
        timestamp: new Date().toISOString(),
        request_id: requestId
      }
    };

    res.status(400).json(response);
  }

  /**
   * Handle syntax errors
   */
  private static handleSyntaxError(error: any, res: Response, requestId: string): void {
    const response: ErrorResponse = {
      success: false,
      error: {
        code: 'INVALID_JSON',
        message: 'Invalid JSON syntax',
        details: {
          position: error.message.match(/position (\d+)/)?.[1]
        }
      },
      meta: {
        timestamp: new Date().toISOString(),
        request_id: requestId
      }
    };

    res.status(400).json(response);
  }

  /**
   * Handle Multer (file upload) errors
   */
  private static handleMulterError(error: any, res: Response, requestId: string): void {
    let message = 'File upload error';
    let code = 'FILE_UPLOAD_ERROR';

    switch (error.code) {
      case 'LIMIT_FILE_SIZE':
        message = 'File size exceeds limit';
        code = 'FILE_TOO_LARGE';
        break;
      case 'LIMIT_FILE_COUNT':
        message = 'Too many files uploaded';
        code = 'TOO_MANY_FILES';
        break;
      case 'LIMIT_UNEXPECTED_FILE':
        message = 'Unexpected file field';
        code = 'UNEXPECTED_FILE';
        break;
      case 'LIMIT_FIELD_KEY':
        message = 'Field name too long';
        code = 'FIELD_NAME_TOO_LONG';
        break;
      case 'LIMIT_FIELD_VALUE':
        message = 'Field value too long';
        code = 'FIELD_VALUE_TOO_LONG';
        break;
      case 'LIMIT_FIELD_COUNT':
        message = 'Too many form fields';
        code = 'TOO_MANY_FIELDS';
        break;
      case 'LIMIT_PART_COUNT':
        message = 'Too many form parts';
        code = 'TOO_MANY_PARTS';
        break;
    }

    const response: ErrorResponse = {
      success: false,
      error: {
        code,
        message,
        details: {
          field: error.field,
          originalCode: error.code
        }
      },
      meta: {
        timestamp: new Date().toISOString(),
        request_id: requestId
      }
    };

    res.status(400).json(response);
  }

  /**
   * Handle generic/unknown errors
   */
  private static handleGenericError(error: Error, res: Response, requestId: string): void {
    const response: ErrorResponse = {
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: process.env.NODE_ENV === 'production'
          ? 'Internal server error'
          : error.message,
        details: process.env.NODE_ENV === 'development' ? error.stack : undefined
      },
      meta: {
        timestamp: new Date().toISOString(),
        request_id: requestId
      }
    };

    res.status(500).json(response);
  }

  /**
   * Log errors with appropriate level and context
   */
  private static logError(error: Error, req: Request, requestId: string): void {
    const errorData = {
      requestId,
      method: req.method,
      url: req.originalUrl,
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      body: req.body,
      query: req.query,
      params: req.params,
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack
      }
    };

    // Determine log level based on error type
    if (error instanceof AppError) {
      if (error.statusCode >= 500) {
        logger.error('Application error', errorData);
      } else if (error.statusCode >= 400) {
        logger.warn('Client error', errorData);
      }
    } else {
      logger.error('Unhandled error', errorData);
    }

    // Send error to monitoring service (if configured)
    if (process.env.ERROR_MONITORING_ENABLED === 'true') {
      ErrorMiddleware.sendToMonitoring(error, errorData);
    }
  }

  /**
   * Send error to monitoring service
   */
  private static sendToMonitoring(error: Error, errorData: any): void {
    // This could integrate with services like Sentry, Rollbar, etc.
    // For now, we'll just log it
    logger.info('Error sent to monitoring', {
      error: error.name,
      message: error.message,
      requestId: errorData.requestId
    });
  }

  /**
   * Async error handler wrapper
   */
  public static asyncHandler = (
    fn: (req: Request, res: Response, next: NextFunction) => Promise<any>
  ) => {
    return (req: Request, res: Response, next: NextFunction) => {
      fn(req, res, next).catch(next);
    };
  };

  /**
   * 404 handler for routes that don't exist
   */
  public static notFound = (req: Request, res: Response): void => {
    const requestId = (req as any).requestId || uuidv4();

    const response: ErrorResponse = {
      success: false,
      error: {
        code: 'NOT_FOUND',
        message: `Route ${req.originalUrl} not found`,
        details: {
          method: req.method,
          path: req.originalUrl
        }
      },
      meta: {
        timestamp: new Date().toISOString(),
        request_id: requestId
      }
    };

    res.status(404).json(response);
  };

  /**
   * Health check endpoint
   */
  public static healthCheck = (req: Request, res: Response): void => {
    const requestId = (req as any).requestId || uuidv4();

    res.status(200).json({
      success: true,
      data: {
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: process.env.npm_package_version || '1.0.0',
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        environment: process.env.NODE_ENV || 'development'
      },
      meta: {
        timestamp: new Date().toISOString(),
        request_id: requestId
      }
    });
  };

  /**
   * Circuit breaker for external services
   */
  public static circuitBreaker = (options: {
    timeout?: number;
    errorThreshold?: number;
    resetTimeout?: number;
  } = {}) => {
    const {
      timeout = 5000,
      errorThreshold = 5,
      resetTimeout = 30000
    } = options;

    let state = 'CLOSED';
    let failureCount = 0;
    let lastFailureTime = 0;

    return async (
      req: Request,
      res: Response,
      next: NextFunction,
      serviceCall: () => Promise<any>
    ): Promise<any> => {
      if (state === 'OPEN') {
        if (Date.now() - lastFailureTime > resetTimeout) {
          state = 'HALF_OPEN';
          failureCount = 0;
        } else {
          throw new AppError('Service temporarily unavailable', 503, 'SERVICE_UNAVAILABLE');
        }
      }

      try {
        const result = await Promise.race([
          serviceCall(),
          new Promise((_, reject) =>
            setTimeout(() => reject(new Error('Service timeout')), timeout)
          )
        ]);

        // Reset on success
        if (state === 'HALF_OPEN') {
          state = 'CLOSED';
          failureCount = 0;
        }

        return result;
      } catch (error) {
        failureCount++;

        if (failureCount >= errorThreshold) {
          state = 'OPEN';
          lastFailureTime = Date.now();
        }

        throw error;
      }
    };
  };
}