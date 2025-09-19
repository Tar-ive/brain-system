import dotenv from 'dotenv';
import { z } from 'zod';

// Load environment variables
dotenv.config();

// Environment validation schema
const envSchema = z.object({
  // Application
  NODE_ENV: z.enum(['development', 'staging', 'production']).default('development'),
  PORT: z.coerce.number().default(3000),
  HOST: z.string().default('0.0.0.0'),

  // Database
  DB_HOST: z.string().default('localhost'),
  DB_PORT: z.coerce.number().default(5432),
  DB_NAME: z.string().default('api_system'),
  DB_USER: z.string().default('postgres'),
  DB_PASSWORD: z.string().default('password'),
  DB_SSL: z.coerce.boolean().default(false),
  DB_POOL_MIN: z.coerce.number().default(2),
  DB_POOL_MAX: z.coerce.number().default(10),
  DB_POOL_IDLE: z.coerce.number().default(30000),
  DB_POOL_ACQUIRE: z.coerce.number().default(2000),

  // Redis
  REDIS_HOST: z.string().default('localhost'),
  REDIS_PORT: z.coerce.number().default(6379),
  REDIS_PASSWORD: z.string().optional(),
  REDIS_DB: z.coerce.number().default(0),
  REDIS_TLS: z.coerce.boolean().default(false),

  // JWT
  JWT_SECRET: z.string().min(32),
  JWT_REFRESH_SECRET: z.string().min(32),
  JWT_ACCESS_EXPIRES_IN: z.string().default('1h'),
  JWT_REFRESH_EXPIRES_IN: z.string().default('7d'),

  // Security
  BCRYPT_ROUNDS: z.coerce.number().min(4).max(12).default(12),
  RATE_LIMIT_WINDOW_MS: z.coerce.number().default(900000), // 15 minutes
  RATE_LIMIT_MAX_REQUESTS: z.coerce.number().default(100),
  RATE_LIMIT_AUTH_WINDOW_MS: z.coerce.number().default(900000), // 15 minutes
  RATE_LIMIT_AUTH_MAX_REQUESTS: z.coerce.number().default(5),

  // File Upload
  UPLOAD_MAX_SIZE: z.coerce.number().default(10 * 1024 * 1024), // 10MB
  UPLOAD_ALLOWED_TYPES: z.string().default('image/jpeg,image/png,image/gif,image/webp,application/pdf'),
  UPLOAD_PATH: z.string().default('./uploads'),

  // Email
  EMAIL_SERVICE: z.enum(['sendgrid', 'ses', 'smtp', 'console']).default('console'),
  EMAIL_FROM: z.string().default('noreply@example.com'),
  EMAIL_SENDGRID_API_KEY: z.string().optional(),
  EMAIL_SES_REGION: z.string().optional(),
  EMAIL_SMTP_HOST: z.string().optional(),
  EMAIL_SMTP_PORT: z.coerce.number().optional(),
  EMAIL_SMTP_USER: z.string().optional(),
  EMAIL_SMTP_PASS: z.string().optional(),

  // CORS
  ALLOWED_ORIGINS: z.string().default('http://localhost:3000'),

  // Logging
  LOG_LEVEL: z.enum(['error', 'warn', 'info', 'debug']).default('info'),
  LOG_FORMAT: z.enum(['json', 'pretty']).default('json'),

  // Monitoring
  MONITORING_ENABLED: z.coerce.boolean().default(true),
  ERROR_MONITORING_ENABLED: z.coerce.boolean().default(false),
  SENTRY_DSN: z.string().optional(),

  // CDN
  CDN_URL: z.string().optional(),
  ASSET_VERSION: z.string().default('latest'),

  // External Services
  EXTERNAL_API_TIMEOUT: z.coerce.number().default(5000),

  // Development
  DEV_AUTO_RELOAD: z.coerce.boolean().default(true),
  DEV_CORS_ORIGIN: z.string().default('http://localhost:3000'),

  // Security Headers
  HELMET_CSP_ENABLED: z.coerce.boolean().default(true),
  HELMET_CSP_DIRECTIVES: z.string().default("default-src 'self'"),
  HELMET_HSTS_ENABLED: z.coerce.boolean().default(true),
  HELMET_HSTS_MAX_AGE: z.coerce.number().default(31536000), // 1 year
  HELMET_HSTS_INCLUDE_SUBDOMAINS: z.coerce.boolean().default(true),
  HELMET_HSTS_PRELOAD: z.coerce.boolean().default(true),

  // Session
  SESSION_SECRET: z.string().min(32),
  SESSION_COOKIE_NAME: z.string().default('session'),
  SESSION_COOKIE_SECURE: z.coerce.boolean().default(true),
  SESSION_COOKIE_SAME_SITE: z.enum(['strict', 'lax', 'none']).default('strict'),
  SESSION_MAX_AGE: z.coerce.number().default(86400000), // 24 hours

  // Cache
  CACHE_DEFAULT_TTL: z.coerce.number().default(3600), // 1 hour
  CACHE_USER_TTL: z.coerce.number().default(1800), // 30 minutes
  CACHE_ITEM_TTL: z.coerce.number().default(900), // 15 minutes
  CACHE_STATS_TTL: z.coerce.number().default(300), // 5 minutes

  // API
  API_VERSION: z.string().default('v1'),
  API_PREFIX: z.string().default('/api'),
  API_DOCS_ENABLED: z.coerce.boolean().default(true),
  API_RATE_LIMIT_ENABLED: z.coerce.boolean().default(true),

  // Features
  FEATURE_REGISTRATION: z.coerce.boolean().default(true),
  FEATURE_EMAIL_VERIFICATION: z.coerce.boolean().default(true),
  FEATURE_PASSWORD_RESET: z.coerce.boolean().default(true),
  FEATURE_SOCIAL_LOGIN: z.coerce.boolean().default(false),
  FEATURE_API_KEYS: z.coerce.boolean().default(true),
  FEATURE_FILE_UPLOAD: z.coerce.boolean().default(true),
  FEATURE_COMMENTS: z.coerce.boolean().default(true),
  FEATURE_LIKES: z.coerce.boolean().default(true),
  FEATURE_SEARCH: z.coerce.boolean().default(true),
  FEATURE_CATEGORIES: z.coerce.boolean().default(true),
  FEATURE_TAGS: z.coerce.boolean().default(true),
  FEATURE_WEBHOOKS: z.coerce.boolean().default(false),
  FEATURE_ANALYTICS: z.coerce.boolean().default(true),

  // Health Check
  HEALTH_CHECK_ENABLED: z.coerce.boolean().default(true),
  HEALTH_CHECK_PATH: z.string().default('/health'),

  // Backup
  BACKUP_ENABLED: z.coerce.boolean().default(false),
  BACKUP_SCHEDULE: z.string().default('0 2 * * *'), // 2 AM daily
  BACKUP_RETENTION_DAYS: z.coerce.number().default(30),
  BACKUP_S3_BUCKET: z.string().optional(),
  BACKUP_S3_REGION: z.string().optional(),
  BACKUP_S3_ACCESS_KEY: z.string().optional(),
  BACKUP_S3_SECRET_KEY: z.string().optional(),

  // Webhooks
  WEBHOOK_SECRET: z.string().min(32).optional(),
  WEBHOOK_TIMEOUT: z.coerce.number().default(5000),
  WEBHOOK_MAX_RETRIES: z.coerce.number().default(3),

  // Social Login (if enabled)
  GOOGLE_CLIENT_ID: z.string().optional(),
  GOOGLE_CLIENT_SECRET: z.string().optional(),
  FACEBOOK_APP_ID: z.string().optional(),
  FACEBOOK_APP_SECRET: z.string().optional(),
  GITHUB_CLIENT_ID: z.string().optional(),
  GITHUB_CLIENT_SECRET: z.string().optional(),

  // Storage
  STORAGE_TYPE: z.enum(['local', 's3', 'gcs', 'azure']).default('local'),
  STORAGE_S3_BUCKET: z.string().optional(),
  STORAGE_S3_REGION: z.string().optional(),
  STORAGE_S3_ACCESS_KEY: z.string().optional(),
  STORAGE_S3_SECRET_KEY: z.string().optional(),
  STORAGE_GCS_BUCKET: z.string().optional(),
  STORAGE_GCS_PROJECT_ID: z.string().optional(),
  STORAGE_GCS_KEY_FILE: z.string().optional(),
  STORAGE_AZURE_CONNECTION_STRING: z.string().optional(),
  STORAGE_AZURE_CONTAINER: z.string().optional(),

  // AI/ML Features
  AI_ENABLED: z.coerce.boolean().default(false),
  AI_API_KEY: z.string().optional(),
  AI_MODEL: z.string().default('gpt-3.5-turbo'),
  AI_MAX_TOKENS: z.coerce.number().default(1000),
  AI_TEMPERATURE: z.coerce.number().min(0).max(2).default(0.7),

  // Performance
  PERFORMANCE_MONITORING_ENABLED: z.coerce.boolean().default(true),
  PERFORMANCE_SAMPLING_RATE: z.coerce.number().min(0).max(1).default(0.1),
  PERFORMANCE_SLOW_THRESHOLD_MS: z.coerce.number().default(1000),

  // Testing
  TEST_DB_NAME: z.string().default('api_system_test'),
  TEST_REDIS_DB: z.coerce.number().default(1),
  TEST_JWT_SECRET: z.string().min(32).default('test-jwt-secret-key-for-testing-only'),

  // Deployment
  DEPLOY_ENV: z.enum(['local', 'staging', 'production']).default('local'),
  DEPLOY_VERSION: z.string().default('latest'),
  DEPLOY_COMMIT_SHA: z.string().optional(),
  DEPLOY_TIMESTAMP: z.string().default(new Date().toISOString()),

  // Analytics
  ANALYTICS_ENABLED: z.coerce.boolean().default(false),
  ANALYTICS_API_KEY: z.string().optional(),
  ANALYTICS_HOST: z.string().optional(),
});

// Validate environment variables
const env = envSchema.safeParse(process.env);

if (!env.success) {
  console.error('❌ Invalid environment variables:');
  console.error(env.error.errors);
  process.exit(1);
}

export const config = env.data;

// Export derived configurations
export const appConfig = {
  isDevelopment: config.NODE_ENV === 'development',
  isStaging: config.NODE_ENV === 'staging',
  isProduction: config.NODE_ENV === 'production',
  isTest: process.env.NODE_ENV === 'test',

  port: config.PORT,
  host: config.HOST,

  api: {
    version: config.API_VERSION,
    prefix: config.API_PREFIX,
    docsEnabled: config.API_DOCS_ENABLED,
    rateLimitEnabled: config.API_RATE_LIMIT_ENABLED,
    timeout: config.EXTERNAL_API_TIMEOUT,
  },

  database: {
    host: config.DB_HOST,
    port: config.DB_PORT,
    name: config.DB_NAME,
    user: config.DB_USER,
    password: config.DB_PASSWORD,
    ssl: config.DB_SSL,
    pool: {
      min: config.DB_POOL_MIN,
      max: config.DB_POOL_MAX,
      idle: config.DB_POOL_IDLE,
      acquire: config.DB_POOL_ACQUIRE,
    },
  },

  redis: {
    host: config.REDIS_HOST,
    port: config.REDIS_PORT,
    password: config.REDIS_PASSWORD,
    db: config.REDIS_DB,
    tls: config.REDIS_TLS,
  },

  jwt: {
    secret: config.JWT_SECRET,
    refreshSecret: config.JWT_REFRESH_SECRET,
    accessExpiresIn: config.JWT_ACCESS_EXPIRES_IN,
    refreshExpiresIn: config.JWT_REFRESH_EXPIRES_IN,
  },

  security: {
    bcryptRounds: config.BCRYPT_ROUNDS,
    rateLimit: {
      windowMs: config.RATE_LIMIT_WINDOW_MS,
      maxRequests: config.RATE_LIMIT_MAX_REQUESTS,
      authWindowMs: config.RATE_LIMIT_AUTH_WINDOW_MS,
      authMaxRequests: config.RATE_LIMIT_AUTH_MAX_REQUESTS,
    },
    session: {
      secret: config.SESSION_SECRET,
      cookieName: config.SESSION_COOKIE_NAME,
      cookieSecure: config.SESSION_COOKIE_SECURE,
      cookieSameSite: config.SESSION_COOKIE_SAME_SITE,
      maxAge: config.SESSION_MAX_AGE,
    },
    helmet: {
      cspEnabled: config.HELMET_CSP_ENABLED,
      cspDirectives: config.HELMET_CSP_DIRECTIVES,
      hstsEnabled: config.HELMET_HSTS_ENABLED,
      hstsMaxAge: config.HELMET_HSTS_MAX_AGE,
      hstsIncludeSubDomains: config.HELMET_HSTS_INCLUDE_SUBDOMAINS,
      hstsPreload: config.HELMET_HSTS_PRELOAD,
    },
  },

  upload: {
    maxSize: config.UPLOAD_MAX_SIZE,
    allowedTypes: config.UPLOAD_ALLOWED_TYPES.split(','),
    path: config.UPLOAD_PATH,
  },

  email: {
    service: config.EMAIL_SERVICE,
    from: config.EMAIL_FROM,
    sendgrid: {
      apiKey: config.EMAIL_SENDGRID_API_KEY,
    },
    ses: {
      region: config.EMAIL_SES_REGION,
    },
    smtp: {
      host: config.EMAIL_SMTP_HOST,
      port: config.EMAIL_SMTP_PORT,
      user: config.EMAIL_SMTP_USER,
      pass: config.EMAIL_SMTP_PASS,
    },
  },

  cors: {
    allowedOrigins: config.ALLOWED_ORIGINS.split(','),
  },

  logging: {
    level: config.LOG_LEVEL,
    format: config.LOG_FORMAT,
  },

  monitoring: {
    enabled: config.MONITORING_ENABLED,
    errorMonitoringEnabled: config.ERROR_MONITORING_ENABLED,
    sentryDsn: config.SENTRY_DSN,
    performanceMonitoringEnabled: config.PERFORMANCE_MONITORING_ENABLED,
    samplingRate: config.PERFORMANCE_SAMPLING_RATE,
    slowThresholdMs: config.PERFORMANCE_SLOW_THRESHOLD_MS,
  },

  cdn: {
    url: config.CDN_URL,
    assetVersion: config.ASSET_VERSION,
  },

  cache: {
    defaultTtl: config.CACHE_DEFAULT_TTL,
    userTtl: config.CACHE_USER_TTL,
    itemTtl: config.CACHE_ITEM_TTL,
    statsTtl: config.CACHE_STATS_TTL,
  },

  features: {
    registration: config.FEATURE_REGISTRATION,
    emailVerification: config.FEATURE_EMAIL_VERIFICATION,
    passwordReset: config.FEATURE_PASSWORD_RESET,
    socialLogin: config.FEATURE_SOCIAL_LOGIN,
    apiKeys: config.FEATURE_API_KEYS,
    fileUpload: config.FEATURE_FILE_UPLOAD,
    comments: config.FEATURE_COMMENTS,
    likes: config.FEATURE_LIKES,
    search: config.FEATURE_SEARCH,
    categories: config.FEATURE_CATEGORIES,
    tags: config.FEATURE_TAGS,
    webhooks: config.FEATURE_WEBHOOKS,
    analytics: config.FEATURE_ANALYTICS,
  },

  healthCheck: {
    enabled: config.HEALTH_CHECK_ENABLED,
    path: config.HEALTH_CHECK_PATH,
  },

  backup: {
    enabled: config.BACKUP_ENABLED,
    schedule: config.BACKUP_SCHEDULE,
    retentionDays: config.BACKUP_RETENTION_DAYS,
    s3: {
      bucket: config.BACKUP_S3_BUCKET,
      region: config.BACKUP_S3_REGION,
      accessKey: config.BACKUP_S3_ACCESS_KEY,
      secretKey: config.BACKUP_S3_SECRET_KEY,
    },
  },

  webhooks: {
    secret: config.WEBHOOK_SECRET,
    timeout: config.WEBHOOK_TIMEOUT,
    maxRetries: config.WEBHOOK_MAX_RETRIES,
  },

  social: {
    google: {
      clientId: config.GOOGLE_CLIENT_ID,
      clientSecret: config.GOOGLE_CLIENT_SECRET,
    },
    facebook: {
      appId: config.FACEBOOK_APP_ID,
      appSecret: config.FACEBOOK_APP_SECRET,
    },
    github: {
      clientId: config.GITHUB_CLIENT_ID,
      clientSecret: config.GITHUB_CLIENT_SECRET,
    },
  },

  storage: {
    type: config.STORAGE_TYPE,
    s3: {
      bucket: config.STORAGE_S3_BUCKET,
      region: config.STORAGE_S3_REGION,
      accessKey: config.STORAGE_S3_ACCESS_KEY,
      secretKey: config.STORAGE_S3_SECRET_KEY,
    },
    gcs: {
      bucket: config.STORAGE_GCS_BUCKET,
      projectId: config.STORAGE_GCS_PROJECT_ID,
      keyFile: config.STORAGE_GCS_KEY_FILE,
    },
    azure: {
      connectionString: config.STORAGE_AZURE_CONNECTION_STRING,
      container: config.STORAGE_AZURE_CONTAINER,
    },
  },

  ai: {
    enabled: config.AI_ENABLED,
    apiKey: config.AI_API_KEY,
    model: config.AI_MODEL,
    maxTokens: config.AI_MAX_TOKENS,
    temperature: config.AI_TEMPERATURE,
  },

  testing: {
    dbName: config.TEST_DB_NAME,
    redisDb: config.TEST_REDIS_DB,
    jwtSecret: config.TEST_JWT_SECRET,
  },

  deployment: {
    env: config.DEPLOY_ENV,
    version: config.DEPLOY_VERSION,
    commitSha: config.DEPLOY_COMMIT_SHA,
    timestamp: config.DEPLOY_TIMESTAMP,
  },

  analytics: {
    enabled: config.ANALYTICS_ENABLED,
    apiKey: config.ANALYTICS_API_KEY,
    host: config.ANALYTICS_HOST,
  },
};

export default appConfig;