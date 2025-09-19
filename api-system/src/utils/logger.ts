import winston from 'winston';
import morgan from 'morgan';
import { format } from 'winston/lib/log/formats';

// Custom log format for structured logging
const logFormat = format.combine(
  format.timestamp(),
  format.errors({ stack: true }),
  format.json(),
  format.prettyPrint()
);

// Create Winston logger
export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: logFormat,
  defaultMeta: {
    service: 'api-system',
    environment: process.env.NODE_ENV || 'development',
    version: process.env.npm_package_version || '1.0.0'
  },
  transports: [
    // Console transport
    new winston.transports.Console({
      format: process.env.LOG_FORMAT === 'pretty'
        ? format.combine(
            format.colorize(),
            format.simple(),
            format.printf(({ timestamp, level, message, service, ...meta }) => {
              return `${timestamp} [${service}] ${level}: ${message} ${
                Object.keys(meta).length ? JSON.stringify(meta, null, 2) : ''
              }`;
            })
          )
        : logFormat
    }),

    // File transport for all logs
    new winston.transports.File({
      filename: 'logs/combined.log',
      maxsize: 5242880, // 5MB
      maxFiles: 5,
      tailable: true
    }),

    // File transport for error logs only
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error',
      maxsize: 5242880, // 5MB
      maxFiles: 5,
      tailable: true
    })
  ]
});

// Create Morgan HTTP request logger
export const httpLogger = morgan(
  process.env.LOG_FORMAT === 'pretty'
    ? ':method :url :status :response-time ms - :res[content-length]'
    : JSON.stringify({
        method: ':method',
        url: ':url',
        status: ':status',
        responseTime: ':response-time',
        contentLength: ':res[content-length]',
        userAgent: ':user-agent',
        ip: ':remote-addr'
      }, null, 2),
  {
    stream: {
      write: (message: string) => {
        if (process.env.LOG_FORMAT === 'pretty') {
          logger.info('HTTP Request', { request: message.trim() });
        } else {
          try {
            const logData = JSON.parse(message);
            logger.info('HTTP Request', logData);
          } catch (error) {
            logger.info('HTTP Request', { request: message.trim() });
          }
        }
      }
    }
  }
);

// Logger utility methods
export class LoggerUtil {
  /**
   * Log API request
   */
  static logApiRequest(req: any, res: any, duration: number): void {
    logger.info('API Request', {
      method: req.method,
      url: req.originalUrl,
      statusCode: res.statusCode,
      duration,
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      userId: req.user?.id,
      apiKeyId: req.apiKey?.id,
      requestId: req.requestId
    });
  }

  /**
   * Log API error
   */
  static logApiError(req: any, error: any, duration: number): void {
    logger.error('API Error', {
      method: req.method,
      url: req.originalUrl,
      statusCode: error.statusCode || 500,
      duration,
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      userId: req.user?.id,
      apiKeyId: req.apiKey?.id,
      requestId: req.requestId,
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack,
        code: error.code
      }
    });
  }

  /**
   * Log database operation
   */
  static logDatabaseOperation(operation: string, query: string, duration: number, error?: any): void {
    const logData = {
      operation,
      query: query.substring(0, 500), // Truncate long queries
      duration,
      timestamp: new Date().toISOString()
    };

    if (error) {
      logger.error('Database Error', { ...logData, error: error.message });
    } else {
      logger.debug('Database Operation', logData);
    }
  }

  /**
   * Log cache operation
   */
  static logCacheOperation(operation: string, key: string, duration: number, error?: any): void {
    const logData = {
      operation,
      key: key.substring(0, 100), // Truncate long keys
      duration,
      timestamp: new Date().toISOString()
    };

    if (error) {
      logger.error('Cache Error', { ...logData, error: error.message });
    } else {
      logger.debug('Cache Operation', logData);
    }
  }

  /**
   * Log authentication event
   */
  static logAuthEvent(event: string, userId?: string, details?: any): void {
    logger.info('Authentication Event', {
      event,
      userId,
      timestamp: new Date().toISOString(),
      ...details
    });
  }

  /**
   * Log security event
   */
  static logSecurityEvent(event: string, level: 'warn' | 'error' = 'warn', details: any): void {
    const logMethod = level === 'error' ? logger.error : logger.warn;

    logMethod('Security Event', {
      event,
      timestamp: new Date().toISOString(),
      ...details
    });
  }

  /**
   * Log performance metrics
   */
  static logPerformanceMetric(metric: string, value: number, tags: Record<string, string> = {}): void {
    logger.info('Performance Metric', {
      metric,
      value,
      tags,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Log business event
   */
  static logBusinessEvent(event: string, userId?: string, data?: any): void {
    logger.info('Business Event', {
      event,
      userId,
      data,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Log system event
   */
  static logSystemEvent(event: string, level: 'info' | 'warn' | 'error' = 'info', details?: any): void {
    const logMethod = level === 'error' ? logger.error : level === 'warn' ? logger.warn : logger.info;

    logMethod('System Event', {
      event,
      timestamp: new Date().toISOString(),
      ...details
    });
  }

  /**
   * Log external service call
   */
  static logExternalServiceCall(service: string, endpoint: string, method: string, duration: number, statusCode: number, error?: any): void {
    const logData = {
      service,
      endpoint,
      method,
      duration,
      statusCode,
      timestamp: new Date().toISOString()
    };

    if (error) {
      logger.error('External Service Error', { ...logData, error: error.message });
    } else {
      logger.debug('External Service Call', logData);
    }
  }

  /**
   * Log webhook event
   */
  static logWebhookEvent(event: string, webhookId: string, url: string, statusCode: number, duration: number, error?: any): void {
    const logData = {
      event,
      webhookId,
      url,
      statusCode,
      duration,
      timestamp: new Date().toISOString()
    };

    if (error) {
      logger.error('Webhook Error', { ...logData, error: error.message });
    } else {
      logger.info('Webhook Event', logData);
    }
  }

  /**
   * Log background job
   */
  static logBackgroundJob(job: string, status: 'started' | 'completed' | 'failed', duration?: number, error?: any): void {
    const logData = {
      job,
      status,
      duration,
      timestamp: new Date().toISOString()
    };

    if (error) {
      logger.error('Background Job Failed', { ...logData, error: error.message });
    } else {
      logger.info('Background Job', logData);
    }
  }

  /**
   * Log user activity
   */
  static logUserActivity(userId: string, action: string, resource?: string, metadata?: any): void {
    logger.info('User Activity', {
      userId,
      action,
      resource,
      metadata,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Log audit trail
   */
  static logAuditTrail(userId: string, action: string, resourceType: string, resourceId: string, changes?: any): void {
    logger.info('Audit Trail', {
      userId,
      action,
      resourceType,
      resourceId,
      changes,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Log health check
   */
  static logHealthCheck(service: string, status: 'healthy' | 'unhealthy', details?: any): void {
    const logMethod = status === 'healthy' ? logger.info : logger.warn;

    logMethod('Health Check', {
      service,
      status,
      details,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Create child logger with context
   */
  static createChildLogger(context: Record<string, any>): winston.Logger {
    return logger.child(context);
  }

  /**
   * Log with custom level and context
   */
  static log(level: string, message: string, meta?: any): void {
    logger.log(level, message, meta);
  }
}

// Export default logger instance
export default logger;