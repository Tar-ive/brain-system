const winston = require('winston');
const path = require('path');
const fs = require('fs');

// Create logs directory if it doesn't exist
const logsDir = path.join(__dirname, '..', '..', 'logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir, { recursive: true });
}

// Custom format for console output
const consoleFormat = winston.format.combine(
  winston.format.colorize(),
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.printf(({ timestamp, level, message, ...meta }) => {
    let msg = `${timestamp} [${level}]: ${message}`;
    if (Object.keys(meta).length > 0) {
      msg += ` ${JSON.stringify(meta)}`;
    }
    return msg;
  })
);

// JSON format for file output
const fileFormat = winston.format.combine(
  winston.format.timestamp(),
  winston.format.errors({ stack: true }),
  winston.format.json()
);

// Create logger instance
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: fileFormat,
  defaultMeta: { service: 'correlation-discovery' },
  transports: [
    // Write all logs to console
    new winston.transports.Console({
      format: consoleFormat,
      level: process.env.NODE_ENV === 'production' ? 'warn' : 'debug'
    }),

    // Write all logs to combined.log
    new winston.transports.File({
      filename: path.join(logsDir, 'combined.log'),
      maxsize: 5242880, // 5MB
      maxFiles: 5,
      tailable: true
    }),

    // Write error logs to error.log
    new winston.transports.File({
      filename: path.join(logsDir, 'error.log'),
      level: 'error',
      maxsize: 5242880, // 5MB
      maxFiles: 5,
      tailable: true
    })
  ]
});

// HTTP request logging middleware
const requestLogger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({
      filename: path.join(logsDir, 'http.log'),
      maxsize: 5242880, // 5MB
      maxFiles: 5,
    })
  ]
});

// Create a stream object for Morgan HTTP request logging
logger.stream = {
  write: (message) => {
    logger.info(message.trim());
  }
};

// Database query logger
logger.query = (query, params = [], duration = 0) => {
  if (process.env.LOG_DB_QUERIES === 'true') {
    logger.debug('Database Query', {
      query: query.trim(),
      params,
      duration: `${duration}ms`
    });
  }
};

// Database error logger
logger.dbError = (error, query, params = []) => {
  logger.error('Database Error', {
    error: error.message,
    stack: error.stack,
    query: query ? query.trim() : undefined,
    params
  });
};

// Migration logger
logger.migration = (message, meta = {}) => {
  logger.info(`Migration: ${message}`, meta);
};

// Performance logger
logger.performance = (operation, duration, meta = {}) => {
  logger.info('Performance', {
    operation,
    duration: `${duration}ms`,
    ...meta
  });
};

// Security logger
logger.security = (event, meta = {}) => {
  logger.warn('Security Event', {
    event,
    ...meta
  });
};

// Audit logger
logger.audit = (action, user, resource, meta = {}) => {
  logger.info('Audit', {
    action,
    user,
    resource,
    timestamp: new Date().toISOString(),
    ...meta
  });
};

module.exports = logger;
module.exports.requestLogger = requestLogger;