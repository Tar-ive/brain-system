import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { v4 as uuidv4 } from 'uuid';
import { UserService } from '../services/user.service';
import { ApiKeyService } from '../services/api-key.service';
import { logger } from '../utils/logger';

export interface AuthenticatedRequest extends Request {
  user?: {
    id: string;
    email: string;
    username: string;
    roles: string[];
    permissions: string[];
  };
  apiKey?: {
    id: string;
    name: string;
    permissions: string[];
    rateLimit: number;
  };
}

export class AuthMiddleware {
  private userService: UserService;
  private apiKeyService: ApiKeyService;

  constructor() {
    this.userService = new UserService();
    this.apiKeyService = new ApiKeyService();
  }

  /**
   * JWT Authentication Middleware
   */
  public authenticate = async (
    req: AuthenticatedRequest,
    res: Response,
    next: NextFunction
  ): Promise<void> => {
    try {
      const authHeader = req.headers.authorization;
      const token = authHeader?.startsWith('Bearer ') ? authHeader.slice(7) : null;

      if (!token) {
        res.status(401).json({
          success: false,
          error: {
            code: 'UNAUTHORIZED',
            message: 'Access token required'
          },
          meta: {
            timestamp: new Date().toISOString(),
            request_id: uuidv4()
          }
        });
        return;
      }

      // Verify JWT token
      const decoded = jwt.verify(token, process.env.JWT_SECRET!) as {
        userId: string;
        type: 'access' | 'refresh';
        sessionId: string;
      };

      if (decoded.type !== 'access') {
        res.status(401).json({
          success: false,
          error: {
            code: 'UNAUTHORIZED',
            message: 'Invalid token type'
          },
          meta: {
            timestamp: new Date().toISOString(),
            request_id: uuidv4()
          }
        });
        return;
      }

      // Get user with roles and permissions
      const user = await this.userService.getUserWithPermissions(decoded.userId);

      if (!user) {
        res.status(401).json({
          success: false,
          error: {
            code: 'UNAUTHORIZED',
            message: 'User not found'
          },
          meta: {
            timestamp: new Date().toISOString(),
            request_id: uuidv4()
          }
        });
        return;
      }

      if (!user.isActive) {
        res.status(401).json({
          success: false,
          error: {
            code: 'UNAUTHORIZED',
            message: 'User account is deactivated'
          },
          meta: {
            timestamp: new Date().toISOString(),
            request_id: uuidv4()
          }
        });
        return;
      }

      // Attach user to request
      req.user = {
        id: user.id,
        email: user.email,
        username: user.username,
        roles: user.roles,
        permissions: user.permissions
      };

      // Log authentication
      logger.info('User authenticated', {
        userId: user.id,
        email: user.email,
        sessionId: decoded.sessionId,
        ip: req.ip,
        userAgent: req.get('User-Agent')
      });

      next();
    } catch (error) {
      if (error instanceof jwt.JsonWebTokenError) {
        res.status(401).json({
          success: false,
          error: {
            code: 'UNAUTHORIZED',
            message: 'Invalid token'
          },
          meta: {
            timestamp: new Date().toISOString(),
            request_id: uuidv4()
          }
        });
        return;
      }

      logger.error('Authentication error', { error, ip: req.ip });
      res.status(500).json({
        success: false,
        error: {
          code: 'INTERNAL_ERROR',
          message: 'Authentication service unavailable'
        },
        meta: {
          timestamp: new Date().toISOString(),
          request_id: uuidv4()
        }
      });
    }
  };

  /**
   * API Key Authentication Middleware
   */
  public authenticateApiKey = async (
    req: AuthenticatedRequest,
    res: Response,
    next: NextFunction
  ): Promise<void> => {
    try {
      const apiKey = req.headers['x-api-key'] as string;

      if (!apiKey) {
        res.status(401).json({
          success: false,
          error: {
            code: 'UNAUTHORIZED',
            message: 'API key required'
          },
          meta: {
            timestamp: new Date().toISOString(),
            request_id: uuidv4()
          }
        });
        return;
      }

      // Get API key details
      const keyDetails = await this.apiKeyService.validateApiKey(apiKey);

      if (!keyDetails) {
        res.status(401).json({
          success: false,
          error: {
            code: 'UNAUTHORIZED',
            message: 'Invalid API key'
          },
          meta: {
            timestamp: new Date().toISOString(),
            request_id: uuidv4()
          }
        });
        return;
      }

      // Attach API key to request
      req.apiKey = {
        id: keyDetails.id,
        name: keyDetails.name,
        permissions: keyDetails.permissions,
        rateLimit: keyDetails.rateLimit
      };

      // Log API key usage
      logger.info('API key authenticated', {
        apiKeyId: keyDetails.id,
        apiKeyName: keyDetails.name,
        ip: req.ip,
        userAgent: req.get('User-Agent')
      });

      next();
    } catch (error) {
      logger.error('API key authentication error', { error, ip: req.ip });
      res.status(500).json({
        success: false,
        error: {
          code: 'INTERNAL_ERROR',
          message: 'Authentication service unavailable'
        },
        meta: {
          timestamp: new Date().toISOString(),
          request_id: uuidv4()
        }
      });
    }
  };

  /**
   * Role-based Authorization Middleware
   */
  public requireRoles = (roles: string[]) => {
    return (req: AuthenticatedRequest, res: Response, next: NextFunction): void => {
      if (!req.user) {
        res.status(401).json({
          success: false,
          error: {
            code: 'UNAUTHORIZED',
            message: 'Authentication required'
          },
          meta: {
            timestamp: new Date().toISOString(),
            request_id: uuidv4()
          }
        });
        return;
      }

      const hasRequiredRole = roles.some(role => req.user!.roles.includes(role));

      if (!hasRequiredRole) {
        res.status(403).json({
          success: false,
          error: {
            code: 'FORBIDDEN',
            message: 'Insufficient permissions'
          },
          meta: {
            timestamp: new Date().toISOString(),
            request_id: uuidv4()
          }
        });
        return;
      }

      next();
    };
  };

  /**
   * Permission-based Authorization Middleware
   */
  public requirePermissions = (permissions: string[]) => {
    return (req: AuthenticatedRequest, res: Response, next: NextFunction): void => {
      // Check both user permissions and API key permissions
      const userPermissions = req.user?.permissions || [];
      const apiKeyPermissions = req.apiKey?.permissions || [];
      const allPermissions = [...userPermissions, ...apiKeyPermissions];

      const hasRequiredPermissions = permissions.every(permission =>
        allPermissions.includes(permission)
      );

      if (!hasRequiredPermissions) {
        res.status(403).json({
          success: false,
          error: {
            code: 'FORBIDDEN',
            message: 'Insufficient permissions',
            details: {
              required: permissions,
              available: allPermissions
            }
          },
          meta: {
            timestamp: new Date().toISOString(),
            request_id: uuidv4()
          }
        });
        return;
      }

      next();
    };
  };

  /**
   * Optional Authentication Middleware
   */
  public optionalAuth = async (
    req: AuthenticatedRequest,
    res: Response,
    next: NextFunction
  ): Promise<void> => {
    try {
      const authHeader = req.headers.authorization;
      const token = authHeader?.startsWith('Bearer ') ? authHeader.slice(7) : null;

      if (token) {
        const decoded = jwt.verify(token, process.env.JWT_SECRET!) as {
          userId: string;
          type: 'access' | 'refresh';
        };

        if (decoded.type === 'access') {
          const user = await this.userService.getUserWithPermissions(decoded.userId);
          if (user && user.isActive) {
            req.user = {
              id: user.id,
              email: user.email,
              username: user.username,
              roles: user.roles,
              permissions: user.permissions
            };
          }
        }
      }

      next();
    } catch (error) {
      // Continue without authentication for optional auth
      next();
    }
  };

  /**
   * Resource Ownership Middleware
   */
  public requireOwnership = (resourceUserId?: string) => {
    return (req: AuthenticatedRequest, res: Response, next: NextFunction): void => {
      if (!req.user) {
        res.status(401).json({
          success: false,
          error: {
            code: 'UNAUTHORIZED',
            message: 'Authentication required'
          },
          meta: {
            timestamp: new Date().toISOString(),
            request_id: uuidv4()
          }
        });
        return;
      }

      // Check if user is admin or resource owner
      const isAdmin = req.user.roles.includes('admin');
      const isOwner = resourceUserId === req.user.id;

      if (!isAdmin && !isOwner) {
        res.status(403).json({
          success: false,
          error: {
            code: 'FORBIDDEN',
            message: 'You can only access your own resources'
          },
          meta: {
            timestamp: new Date().toISOString(),
            request_id: uuidv4()
          }
        });
        return;
      }

      next();
    };
  };
}