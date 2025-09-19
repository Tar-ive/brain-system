import { Request, Response, NextFunction } from 'express';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { v4 as uuidv4 } from 'uuid';
import { logger } from '../utils/logger';

export interface SecurityRequest extends Request {
  requestId: string;
}

export class SecurityMiddleware {
  /**
   * Initialize security middleware
   */
  public static initialize() {
    return [
      helmet(), // Security headers
      this.cors(),
      this.requestId(),
      this.rateLimiter(),
      this.xssProtection(),
      this.noSniff(),
      this.frameguard(),
      this.hsts(),
      this.contentTypeOptions()
    ];
  }

  /**
   * CORS configuration
   */
  private static cors() {
    return (req: Request, res: Response, next: NextFunction) => {
      const allowedOrigins = process.env.ALLOWED_ORIGINS?.split(',') || [
        'http://localhost:3000',
        'https://example.com'
      ];

      const origin = req.headers.origin;

      if (origin && allowedOrigins.includes(origin)) {
        res.header('Access-Control-Allow-Origin', origin);
      }

      res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS');
      res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization, X-API-Key');
      res.header('Access-Control-Allow-Credentials', 'true');
      res.header('Access-Control-Max-Age', '86400'); // 24 hours

      if (req.method === 'OPTIONS') {
        res.sendStatus(200);
        return;
      }

      next();
    };
  }

  /**
   * Add unique request ID to each request
   */
  private static requestId() {
    return (req: SecurityRequest, res: Response, next: NextFunction) => {
      req.requestId = uuidv4();
      res.setHeader('X-Request-ID', req.requestId);
      next();
    };
  }

  /**
   * Rate limiting middleware
   */
  private static rateLimiter() {
    // General rate limiter
    const generalLimiter = rateLimit({
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 100, // limit each IP to 100 requests per windowMs
      message: {
        success: false,
        error: {
          code: 'TOO_MANY_REQUESTS',
          message: 'Too many requests from this IP, please try again later'
        },
        meta: {
          timestamp: new Date().toISOString(),
          request_id: uuidv4()
        }
      },
      standardHeaders: true,
      legacyHeaders: false,
      handler: (req, res) => {
        logger.warn('Rate limit exceeded', {
          ip: req.ip,
          path: req.path,
          userAgent: req.get('User-Agent')
        });

        res.status(429).json({
          success: false,
          error: {
            code: 'TOO_MANY_REQUESTS',
            message: 'Too many requests from this IP, please try again later'
          },
          meta: {
            timestamp: new Date().toISOString(),
            request_id: uuidv4()
          }
        });
      }
    });

    // Auth endpoints rate limiter (more strict)
    const authLimiter = rateLimit({
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 5, // limit each IP to 5 auth requests per windowMs
      message: {
        success: false,
        error: {
          code: 'TOO_MANY_REQUESTS',
          message: 'Too many authentication attempts, please try again later'
        },
        meta: {
          timestamp: new Date().toISOString(),
          request_id: uuidv4()
        }
      },
      skipSuccessfulRequests: true
    });

    return (req: Request, res: Response, next: NextFunction) => {
      // Apply stricter rate limiting to auth endpoints
      if (req.path.startsWith('/auth/') || req.path.startsWith('/api-keys/')) {
        return authLimiter(req, res, next);
      }

      return generalLimiter(req, res, next);
    };
  }

  /**
   * XSS Protection
   */
  private static xssProtection() {
    return (req: Request, res: Response, next: NextFunction) => {
      res.setHeader('X-XSS-Protection', '1; mode=block');
      next();
    };
  }

  /**
   * No Sniff
   */
  private static noSniff() {
    return (req: Request, res: Response, next: NextFunction) => {
      res.setHeader('X-Content-Type-Options', 'nosniff');
      next();
    };
  }

  /**
   * Frameguard
   */
  private static frameguard() {
    return (req: Request, res: Response, next: NextFunction) => {
      res.setHeader('X-Frame-Options', 'SAMEORIGIN');
      next();
    };
  }

  /**
   * HSTS
   */
  private static hsts() {
    return (req: Request, res: Response, next: NextFunction) => {
      if (req.secure) {
        res.setHeader(
          'Strict-Transport-Security',
          'max-age=31536000; includeSubDomains; preload'
        );
      }
      next();
    };
  }

  /**
   * Content Type Options
   */
  private static contentTypeOptions() {
    return (req: Request, res: Response, next: NextFunction) => {
      res.setHeader('X-Content-Type-Options', 'nosniff');
      next();
    };
  }

  /**
   * Input validation middleware
   */
  public static validateInput(schema: any) {
    return (req: Request, res: Response, next: NextFunction) => {
      try {
        // Validate request body
        if (req.body && Object.keys(req.body).length > 0) {
          const { error, value } = schema.validate(req.body, {
            abortEarly: false,
            stripUnknown: true
          });

          if (error) {
            res.status(400).json({
              success: false,
              error: {
                code: 'VALIDATION_ERROR',
                message: 'Input validation failed',
                details: error.details.map(detail => ({
                  field: detail.path.join('.'),
                  message: detail.message
                }))
              },
              meta: {
                timestamp: new Date().toISOString(),
                request_id: uuidv4()
              }
            });
            return;
          }

          req.body = value;
        }

        next();
      } catch (error) {
        logger.error('Input validation error', { error });
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
    };
  }

  /**
   * SQL Injection protection
   */
  public static sqlInjectionProtection() {
    return (req: Request, res: Response, next: NextFunction) => {
      const checkSqlInjection = (str: string): boolean => {
        const sqlPattern = /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|UNION|EXEC|EXECUTE|TRUNCATE)\b)|(''|"")|(\bor\b|\band\b|\blike\b)/i;
        return sqlPattern.test(str);
      };

      // Check query parameters
      for (const [key, value] of Object.entries(req.query)) {
        if (typeof value === 'string' && checkSqlInjection(value)) {
          logger.warn('Potential SQL injection attempt', {
            ip: req.ip,
            path: req.path,
            query: req.query,
            userAgent: req.get('User-Agent')
          });

          res.status(400).json({
            success: false,
            error: {
              code: 'VALIDATION_ERROR',
              message: 'Invalid input detected'
            },
            meta: {
              timestamp: new Date().toISOString(),
              request_id: uuidv4()
            }
          });
          return;
        }
      }

      // Check body parameters
      if (req.body && typeof req.body === 'object') {
        for (const [key, value] of Object.entries(req.body)) {
          if (typeof value === 'string' && checkSqlInjection(value)) {
            logger.warn('Potential SQL injection attempt', {
              ip: req.ip,
              path: req.path,
              body: req.body,
              userAgent: req.get('User-Agent')
            });

            res.status(400).json({
              success: false,
              error: {
                code: 'VALIDATION_ERROR',
                message: 'Invalid input detected'
              },
              meta: {
                timestamp: new Date().toISOString(),
                request_id: uuidv4()
              }
            });
            return;
          }
        }
      }

      next();
    };
  }

  /**
   * File upload security
   */
  public static fileUploadSecurity() {
    return (req: Request, res: Response, next: NextFunction) => {
      if (req.file) {
        const file = req.file;

        // Check file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
          res.status(400).json({
            success: false,
            error: {
              code: 'VALIDATION_ERROR',
              message: 'File size exceeds 10MB limit'
            },
            meta: {
              timestamp: new Date().toISOString(),
              request_id: uuidv4()
            }
          });
          return;
        }

        // Check file type
        const allowedMimeTypes = [
          'image/jpeg',
          'image/png',
          'image/gif',
          'image/webp',
          'application/pdf',
          'text/plain',
          'application/json'
        ];

        if (!allowedMimeTypes.includes(file.mimetype)) {
          res.status(400).json({
            success: false,
            error: {
              code: 'VALIDATION_ERROR',
              message: 'File type not allowed'
            },
            meta: {
              timestamp: new Date().toISOString(),
              request_id: uuidv4()
            }
          });
          return;
        }

        // Sanitize filename
        const sanitizedFilename = file.originalname
          .replace(/[^a-zA-Z0-9.-]/g, '_')
          .replace(/_+/g, '_');

        if (sanitizedFilename !== file.originalname) {
          logger.warn('Filename sanitized', {
            original: file.originalname,
            sanitized: sanitizedFilename,
            ip: req.ip
          });
        }

        file.originalname = sanitizedFilename;
      }

      next();
    };
  }

  /**
   * Request logging middleware
   */
  public static requestLogger() {
    return (req: SecurityRequest, res: Response, next: NextFunction) => {
      const start = Date.now();

      res.on('finish', () => {
        const duration = Date.now() - start;
        const { method, originalUrl, ip } = req;
        const { statusCode } = res;

        // Log successful requests
        if (statusCode < 400) {
          logger.info('Request completed', {
            requestId: req.requestId,
            method,
            url: originalUrl,
            statusCode,
            duration,
            ip,
            userAgent: req.get('User-Agent')
          });
        } else {
          // Log error requests
          logger.error('Request failed', {
            requestId: req.requestId,
            method,
            url: originalUrl,
            statusCode,
            duration,
            ip,
            userAgent: req.get('User-Agent')
          });
        }
      });

      next();
    };
  }
}