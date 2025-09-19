const { v4: uuidv4 } = require('uuid');
const logger = require('../utils/logger');

// Request tracking middleware
const requestTracker = (req, res, next) => {
  // Generate unique request ID
  const requestId = uuidv4();

  // Add request ID to request object
  req.requestId = requestId;

  // Add request ID to response headers
  res.setHeader('X-Request-ID', requestId);

  // Track request start time
  req.startTime = Date.now();

  // Log request start
  logger.info('Request started', {
    requestId,
    method: req.method,
    url: req.originalUrl,
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    timestamp: new Date().toISOString()
  });

  // Override res.end to track response
  const originalEnd = res.end;
  res.end = function(chunk, encoding) {
    // Calculate request duration
    const duration = Date.now() - req.startTime;

    // Log request completion
    logger.info('Request completed', {
      requestId,
      method: req.method,
      url: req.originalUrl,
      statusCode: res.statusCode,
      duration: `${duration}ms`,
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      timestamp: new Date().toISOString()
    });

    // Call original end method
    originalEnd.call(this, chunk, encoding);
  };

  next();
};

// Rate limiter by IP with memory storage
const requestRateLimiter = (windowMs = 60000, maxRequests = 100) => {
  const requests = new Map();

  return (req, res, next) => {
    const ip = req.ip;
    const now = Date.now();
    const windowStart = now - windowMs;

    // Clean old requests
    if (!requests.has(ip)) {
      requests.set(ip, []);
    }

    const ipRequests = requests.get(ip);

    // Filter out old requests
    const validRequests = ipRequests.filter(time => time > windowStart);
    requests.set(ip, validRequests);

    // Check if limit exceeded
    if (validRequests.length >= maxRequests) {
      logger.warn('Rate limit exceeded', {
        ip,
        requests: validRequests.length,
        maxRequests,
        window: `${windowMs}ms`
      });

      return res.status(429).json({
        success: false,
        message: 'Too many requests. Please try again later.',
        retryAfter: Math.ceil(windowMs / 1000)
      });
    }

    // Add current request
    validRequests.push(now);
    requests.set(ip, validRequests);

    next();
  };
};

// Request logging middleware for development
const devRequestLogger = (req, res, next) => {
  if (process.env.NODE_ENV === 'development') {
    const start = Date.now();

    res.on('finish', () => {
      const duration = Date.now() - start;

      console.log(`${req.method} ${req.originalUrl} - ${res.statusCode} - ${duration}ms`);

      // Log request body for POST/PUT/PATCH
      if (['POST', 'PUT', 'PATCH'].includes(req.method) && req.body) {
        console.log('Request body:', JSON.stringify(req.body, null, 2));
      }
    });
  }

  next();
};

// Response time middleware
const responseTime = (req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - start;
    res.setHeader('X-Response-Time', `${duration}ms`);
  });

  next();
};

// Request body size limiter
const requestBodySizeLimit = (maxSize = '10mb') => {
  return (req, res, next) => {
    const contentLength = req.headers['content-length'];

    if (contentLength) {
      const size = parseInt(contentLength);
      const maxSizeBytes = maxSize === '10mb' ? 10 * 1024 * 1024 :
                          maxSize === '1mb' ? 1024 * 1024 :
                          parseInt(maxSize);

      if (size > maxSizeBytes) {
        logger.warn('Request body size limit exceeded', {
          ip: req.ip,
          size,
          maxSize: maxSizeBytes,
          url: req.originalUrl
        });

        return res.status(413).json({
          success: false,
          message: `Request body size exceeds limit of ${maxSize}`
        });
      }
    }

    next();
  };
};

module.exports = {
  requestTracker,
  requestRateLimiter,
  devRequestLogger,
  responseTime,
  requestBodySizeLimit
};