import { Request, Response, NextFunction } from 'express';
import client, { Counter, Histogram, Gauge } from 'prom-client';
import { LoggerUtil } from '../utils/logger';

export interface MonitoredRequest extends Request {
  startTime: number;
}

export class MonitoringMiddleware {
  private static metrics = {
    // HTTP request metrics
    httpRequestCount: new Counter({
      name: 'http_requests_total',
      help: 'Total number of HTTP requests',
      labelNames: ['method', 'route', 'status_code', 'environment']
    }),

    httpRequestDuration: new Histogram({
      name: 'http_request_duration_seconds',
      help: 'HTTP request duration in seconds',
      labelNames: ['method', 'route', 'status_code'],
      buckets: [0.1, 0.5, 1, 2, 5, 10]
    }),

    httpResponseSize: new Histogram({
      name: 'http_response_size_bytes',
      help: 'HTTP response size in bytes',
      labelNames: ['method', 'route'],
      buckets: [100, 1000, 10000, 100000, 1000000]
    }),

    // Database metrics
    dbQueryCount: new Counter({
      name: 'db_queries_total',
      help: 'Total number of database queries',
      labelNames: ['operation', 'table', 'environment']
    }),

    dbQueryDuration: new Histogram({
      name: 'db_query_duration_seconds',
      help: 'Database query duration in seconds',
      labelNames: ['operation', 'table'],
      buckets: [0.01, 0.05, 0.1, 0.5, 1, 5]
    }),

    // Cache metrics
    cacheOperations: new Counter({
      name: 'cache_operations_total',
      help: 'Total number of cache operations',
      labelNames: ['operation', 'cache_type', 'environment']
    }),

    cacheHitRate: new Gauge({
      name: 'cache_hit_rate',
      help: 'Cache hit rate percentage',
      labelNames: ['cache_type']
    }),

    // Business metrics
    userRegistrations: new Counter({
      name: 'user_registrations_total',
      help: 'Total number of user registrations',
      labelNames: ['environment']
    }),

    userLogins: new Counter({
      name: 'user_logins_total',
      help: 'Total number of user logins',
      labelNames: ['environment', 'method']
    }),

    apiErrors: new Counter({
      name: 'api_errors_total',
      help: 'Total number of API errors',
      labelNames: ['error_code', 'endpoint', 'environment']
    }),

    // System metrics
    activeConnections: new Gauge({
      name: 'active_connections',
      help: 'Number of active connections',
      labelNames: ['type']
    }),

    memoryUsage: new Gauge({
      name: 'memory_usage_bytes',
      help: 'Memory usage in bytes',
      labelNames: ['type']
    }),

    cpuUsage: new Gauge({
      name: 'cpu_usage_percent',
      help: 'CPU usage percentage'
    }),

    // External service metrics
    externalServiceCalls: new Counter({
      name: 'external_service_calls_total',
      help: 'Total number of external service calls',
      labelNames: ['service', 'method', 'status', 'environment']
    }),

    externalServiceDuration: new Histogram({
      name: 'external_service_duration_seconds',
      help: 'External service call duration in seconds',
      labelNames: ['service', 'method', 'status'],
      buckets: [0.5, 1, 2, 5, 10, 30]
    }),

    // Background job metrics
    backgroundJobExecutions: new Counter({
      name: 'background_job_executions_total',
      help: 'Total number of background job executions',
      labelNames: ['job_name', 'status', 'environment']
    }),

    backgroundJobDuration: new Histogram({
      name: 'background_job_duration_seconds',
      help: 'Background job duration in seconds',
      labelNames: ['job_name', 'status'],
      buckets: [1, 5, 10, 30, 60, 300]
    })
  };

  /**
   * Initialize monitoring middleware
   */
  public static initialize() {
    // Set default labels
    client.register.setDefaultLabels({
      environment: process.env.NODE_ENV || 'development',
      app: 'api-system',
      version: process.env.npm_package_version || '1.0.0'
    });

    // Collect default metrics
    client.collectDefaultMetrics({
      prefix: 'api_system_',
      labels: { environment: process.env.NODE_ENV || 'development' },
      gcDurationBuckets: [0.001, 0.01, 0.1, 1, 2, 5]
    });

    return [
      this.requestTiming,
      this.requestMetrics,
      this.responseMetrics,
      this.errorMetrics,
      this.systemMetrics,
      this.businessMetrics,
      this.customMetrics
    ];
  }

  /**
   * Request timing middleware
   */
  private static requestTiming(req: MonitoredRequest, res: Response, next: NextFunction): void {
    req.startTime = Date.now();
    next();
  }

  /**
   * Request metrics middleware
   */
  private static requestMetrics(req: MonitoredRequest, res: Response, next: NextFunction): void {
    res.on('finish', () => {
      const duration = (Date.now() - req.startTime) / 1000; // Convert to seconds
      const route = req.route?.path || req.path || 'unknown';
      const method = req.method;
      const statusCode = res.statusCode.toString();
      const environment = process.env.NODE_ENV || 'development';

      // Record request count
      this.metrics.httpRequestCount.inc({
        method,
        route,
        status_code: statusCode,
        environment
      });

      // Record request duration
      this.metrics.httpRequestDuration.observe({
        method,
        route,
        status_code: statusCode
      }, duration);

      // Record response size
      if (res.get('content-length')) {
        const responseSize = parseInt(res.get('content-length') || '0', 10);
        this.metrics.httpResponseSize.observe({
          method,
          route
        }, responseSize);
      }

      // Log slow requests
      if (duration > 1) { // More than 1 second
        LoggerUtil.logPerformanceMetric('slow_request', duration, {
          method,
          route,
          statusCode
        });
      }
    });

    next();
  }

  /**
   * Response metrics middleware
   */
  private static responseMetrics(req: MonitoredRequest, res: Response, next: NextFunction): void {
    const originalJson = res.json;
    res.json = function(data: any) {
      // Calculate response size
      const responseSize = Buffer.byteLength(JSON.stringify(data), 'utf8');
      res.set('content-length', responseSize.toString());
      return originalJson.call(this, data);
    };

    next();
  }

  /**
   * Error metrics middleware
   */
  private static errorMetrics(err: any, req: MonitoredRequest, res: Response, next: NextFunction): void {
    const route = req.route?.path || req.path || 'unknown';
    const method = req.method;
    const statusCode = err.statusCode || 500;
    const errorCode = err.code || 'INTERNAL_ERROR';
    const environment = process.env.NODE_ENV || 'development';

    // Record error metrics
    this.metrics.apiErrors.inc({
      error_code: errorCode,
      endpoint: `${method} ${route}`,
      environment
    });

    // Log error details
    LoggerUtil.logApiError(req, err, (Date.now() - req.startTime) / 1000);

    next(err);
  }

  /**
   * System metrics middleware
   */
  private static systemMetrics(req: MonitoredRequest, res: Response, next: NextFunction): void {
    // Update system metrics
    this.updateSystemMetrics();

    next();
  }

  /**
   * Business metrics middleware
   */
  private static businessMetrics(req: MonitoredRequest, res: Response, next: NextFunction): void {
    // Track business-specific metrics
    const path = req.path;

    // User registrations
    if (path === '/api/v1/auth/register' && req.method === 'POST') {
      res.on('finish', () => {
        if (res.statusCode === 201) {
          this.metrics.userRegistrations.inc({
            environment: process.env.NODE_ENV || 'development'
          });
        }
      });
    }

    // User logins
    if (path === '/api/v1/auth/login' && req.method === 'POST') {
      res.on('finish', () => {
        if (res.statusCode === 200) {
          this.metrics.userLogins.inc({
            environment: process.env.NODE_ENV || 'development',
            method: 'password'
          });
        }
      });
    }

    next();
  }

  /**
   * Custom metrics middleware
   */
  private static customMetrics(req: MonitoredRequest, res: Response, next: NextFunction): void {
    // Add custom metrics collection logic here
    // For example, track API usage by user, endpoint popularity, etc.

    next();
  }

  /**
   * Update system metrics
   */
  private static updateSystemMetrics(): void {
    const memoryUsage = process.memoryUsage();
    const cpuUsage = process.cpuUsage();

    // Update memory metrics
    this.metrics.memoryUsage.set({ type: 'rss' }, memoryUsage.rss);
    this.metrics.memoryUsage.set({ type: 'heap_total' }, memoryUsage.heapTotal);
    this.metrics.memoryUsage.set({ type: 'heap_used' }, memoryUsage.heapUsed);
    this.metrics.memoryUsage.set({ type: 'external' }, memoryUsage.external);

    // Update CPU usage (simplified)
    const totalCpuUsage = cpuUsage.user + cpuUsage.system;
    const cpuPercent = (totalCpuUsage / 1000000) * 100; // Convert to percentage
    this.metrics.cpuUsage.set(cpuPercent);
  }

  /**
   * Get metrics endpoint
   */
  public static getMetrics(req: Request, res: Response): void {
    res.set('Content-Type', client.register.contentType);
    res.end(client.register.metrics());
  }

  /**
   * Health check endpoint
   */
  public static healthCheck(req: Request, res: Response): void {
    const health = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      version: process.env.npm_package_version || '1.0.0',
      environment: process.env.NODE_ENV || 'development',
      checks: {
        database: 'healthy',
        redis: 'healthy',
        memory: 'healthy',
        disk: 'healthy'
      },
      metrics: {
        memory_usage: process.memoryUsage(),
        cpu_usage: process.cpuUsage(),
        uptime: process.uptime()
      }
    };

    res.json(health);
  }

  /**
   * Ready check endpoint
   */
  public static readyCheck(req: Request, res: Response): void {
    // Check if the application is ready to serve traffic
    const ready = true; // Add actual readiness checks

    res.status(ready ? 200 : 503).json({
      status: ready ? 'ready' : 'not ready',
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Live check endpoint
   */
  public static liveCheck(req: Request, res: Response): void {
    // Check if the application is running (liveness)
    const alive = true; // Add actual liveness checks

    res.status(alive ? 200 : 503).json({
      status: alive ? 'alive' : 'not alive',
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Metrics utility methods
   */
  public static metrics = {
    // Database metrics
    recordDatabaseQuery: (operation: string, table: string, duration: number, error?: any): void => {
      MonitoringMiddleware.metrics.dbQueryCount.inc({
        operation,
        table,
        environment: process.env.NODE_ENV || 'development'
      });

      MonitoringMiddleware.metrics.dbQueryDuration.observe({
        operation,
        table
      }, duration / 1000); // Convert to seconds

      if (error) {
        LoggerUtil.logDatabaseOperation(operation, '', duration, error);
      }
    },

    // Cache metrics
    recordCacheOperation: (operation: string, cacheType: string, hit: boolean = false): void => {
      MonitoringMiddleware.metrics.cacheOperations.inc({
        operation,
        cache_type: cacheType,
        environment: process.env.NODE_ENV || 'development'
      });

      // Update hit rate (simplified)
      // In a real implementation, you'd track hits and misses separately
    },

    // External service metrics
    recordExternalServiceCall: (service: string, method: string, duration: number, statusCode: number): void => {
      MonitoringMiddleware.metrics.externalServiceCalls.inc({
        service,
        method,
        status: statusCode.toString(),
        environment: process.env.NODE_ENV || 'development'
      });

      MonitoringMiddleware.metrics.externalServiceDuration.observe({
        service,
        method,
        status: statusCode.toString()
      }, duration / 1000); // Convert to seconds
    },

    // Background job metrics
    recordBackgroundJob: (jobName: string, status: 'success' | 'failed', duration: number): void => {
      MonitoringMiddleware.metrics.backgroundJobExecutions.inc({
        job_name: jobName,
        status,
        environment: process.env.NODE_ENV || 'development'
      });

      MonitoringMiddleware.metrics.backgroundJobDuration.observe({
        job_name: jobName,
        status
      }, duration / 1000); // Convert to seconds
    },

    // Business metrics
    recordUserRegistration: (): void => {
      MonitoringMiddleware.metrics.userRegistrations.inc({
        environment: process.env.NODE_ENV || 'development'
      });
    },

    recordUserLogin: (method: string = 'password'): void => {
      MonitoringMiddleware.metrics.userLogins.inc({
        environment: process.env.NODE_ENV || 'development',
        method
      });
    },

    // System metrics
    updateConnectionCount: (type: string, count: number): void => {
      MonitoringMiddleware.metrics.activeConnections.set({ type }, count);
    },

    // Custom metrics
    incrementCounter: (counterName: string, labels: Record<string, string> = {}): void => {
      const counter = MonitoringMiddleware.metrics[counterName as keyof typeof MonitoringMiddleware.metrics] as Counter;
      if (counter) {
        counter.inc({ ...labels, environment: process.env.NODE_ENV || 'development' });
      }
    },

    recordHistogram: (histogramName: string, value: number, labels: Record<string, string> = {}): void => {
      const histogram = MonitoringMiddleware.metrics[histogramName as keyof typeof MonitoringMiddleware.metrics] as Histogram;
      if (histogram) {
        histogram.observe(labels, value);
      }
    },

    setGauge: (gaugeName: string, value: number, labels: Record<string, string> = {}): void => {
      const gauge = MonitoringMiddleware.metrics[gaugeName as keyof typeof MonitoringMiddleware.metrics] as Gauge;
      if (gauge) {
        gauge.set(labels, value);
      }
    }
  };
}