# Caching Strategy and Performance Optimization

## Caching Architecture Overview

### Multi-Layer Caching Strategy

```
┌─────────────────────────────────────────────────────────┐
│                     CDN Layer                            │
│                (Static Assets, API)                     │
├─────────────────────────────────────────────────────────┤
│                   Redis Cache                           │
│            (Application-level Caching)                 │
├─────────────────────────────────────────────────────────┤
│                 Database Cache                          │
│            (PostgreSQL Query Cache)                    │
├─────────────────────────────────────────────────────────┤
│               File System Cache                        │
│             (Generated Files, Logs)                    │
└─────────────────────────────────────────────────────────┘
```

## Redis Cache Implementation

### Cache Keys Structure

```
user:{userId}                    - User profile data
user:permissions:{userId}        - User permissions
session:{sessionId}              - User session data
api_key:{apiKeyId}              - API key details
item:{itemId}                    - Item details
item:list:{page}:{filters}       - Paginated item lists
category:{categoryId}           - Category details
category:tree                   - Category hierarchy
search:{query}:{page}           - Search results
stats:daily:{date}              - Daily statistics
rate_limit:{ip}:{endpoint}      - Rate limiting counters
```

### Cache TTL (Time To Live) Strategy

| Cache Type | TTL | Description |
|------------|-----|-------------|
| User Session | 30 days | User authentication sessions |
| User Profile | 1 hour | User profile data |
| Permissions | 30 minutes | User permissions and roles |
| API Keys | 5 minutes | API key validation |
| Items | 15 minutes | Item details and content |
| Item Lists | 5 minutes | Paginated lists and filters |
| Categories | 1 hour | Category data (changes infrequently) |
| Search Results | 10 minutes | Search query results |
| Statistics | 5 minutes | System statistics and metrics |
| Rate Limits | 15 minutes | Rate limiting counters |

## Performance Optimization Techniques

### 1. Database Query Optimization

```typescript
// Optimized queries with proper indexing
const optimizedQuery = `
  SELECT
    i.id, i.title, i.excerpt, i.created_at,
    u.username, u.avatar_url,
    c.name as category_name,
    COUNT(DISTINCT l.id) as like_count,
    COUNT(DISTINCT cm.id) as comment_count
  FROM items i
  LEFT JOIN users u ON i.author_id = u.id
  LEFT JOIN categories c ON i.category_id = c.id
  LEFT JOIN likes l ON i.id = l.item_id
  LEFT JOIN comments cm ON i.id = cm.item_id AND cm.is_approved = true
  WHERE i.status = 'published'
    AND i.visibility = 'public'
    AND i.created_at > $1
  GROUP BY i.id, u.username, u.avatar_url, c.name
  ORDER BY i.created_at DESC
  LIMIT $2 OFFSET $3
`;
```

### 2. Connection Pooling

```typescript
// Database connection pool configuration
const poolConfig = {
  max: 20,                  // Maximum connections
  min: 5,                   // Minimum connections
  idleTimeoutMillis: 30000, // Close idle connections after 30 seconds
  connectionTimeoutMillis: 2000, // Return error after 2 seconds if connection not available
  maxUses: 7500,            // Close a connection after it has been used 7500 times
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
};
```

### 3. Query Result Caching

```typescript
// Cache query results with automatic invalidation
async function getCachedItems(filters: ItemFilters, page: number = 1, limit: number = 20) {
  const cacheKey = `items:list:${page}:${JSON.stringify(filters)}`;
  const cached = await cacheService.get(cacheKey);

  if (cached) {
    return cached;
  }

  const items = await itemService.getItems(filters, page, limit);

  // Cache with shorter TTL for frequently changing data
  await cacheService.set(cacheKey, items, 300); // 5 minutes

  return items;
}
```

### 4. Pagination Optimization

```typescript
// Efficient pagination with cursor-based approach for large datasets
async function getItemsWithCursor(cursor?: string, limit: number = 20) {
  let query = `
    SELECT id, title, created_at
    FROM items
    WHERE status = 'published'
  `;

  const params: any[] = [limit];

  if (cursor) {
    query += ' AND created_at < $2';
    params.push(decodeCursor(cursor));
  }

  query += ' ORDER BY created_at DESC LIMIT $1';

  const items = await database.query(query, params);

  // Encode next cursor if there are more items
  const nextCursor = items.length === limit ? encodeCursor(items[items.length - 1].created_at) : null;

  return { items, nextCursor };
}
```

## Caching Patterns

### 1. Cache-Aside Pattern

```typescript
async function getItem(itemId: string) {
  const cacheKey = `item:${itemId}`;

  // Try cache first
  let item = await cacheService.get(cacheKey);

  if (item) {
    return item;
  }

  // Cache miss - get from database
  item = await database.query('SELECT * FROM items WHERE id = $1', [itemId]);

  if (item) {
    // Cache the result
    await cacheService.set(cacheKey, item, 900); // 15 minutes
  }

  return item;
}
```

### 2. Write-Through Pattern

```typescript
async function updateItem(itemId: string, updates: any) {
  // Update database
  const item = await database.query(
    'UPDATE items SET ... WHERE id = $1 RETURNING *',
    [itemId, ...Object.values(updates)]
  );

  // Update cache immediately
  const cacheKey = `item:${itemId}`;
  await cacheService.set(cacheKey, item, 900);

  // Invalidate related caches
  await invalidateRelatedCaches(itemId);

  return item;
}
```

### 3. Cache Invalidation Strategies

```typescript
async function invalidateRelatedCaches(itemId: string) {
  const invalidationKeys = [
    `item:${itemId}`,
    `item:related:${itemId}`,
    `items:list:*`, // Pattern matching for list caches
    `search:*`,
    `stats:daily:${new Date().toISOString().split('T')[0]}`
  ];

  // Use Redis pattern matching for bulk invalidation
  for (const pattern of invalidationKeys) {
    if (pattern.includes('*')) {
      const keys = await cacheService.keys(pattern);
      if (keys.length > 0) {
        await cacheService.del(...keys);
      }
    } else {
      await cacheService.del(pattern);
    }
  }
}
```

## Rate Limiting Implementation

### Token Bucket Algorithm

```typescript
class RateLimiter {
  private redis: Redis;
  private capacity: number;
  private refillRate: number;

  constructor(redis: Redis, capacity: number, refillRate: number) {
    this.redis = redis;
    this.capacity = capacity;
    this.refillRate = refillRate;
  }

  async isAllowed(key: string): Promise<boolean> {
    const now = Math.floor(Date.now() / 1000);
    const luaScript = `
      local key = KEYS[1]
      local capacity = tonumber(ARGV[1])
      local refillRate = tonumber(ARGV[2])
      local now = tonumber(ARGV[3])

      local bucket = redis.call('HMGET', key, 'tokens', 'lastRefill')

      local tokens = tonumber(bucket[1]) or capacity
      local lastRefill = tonumber(bucket[2]) or now

      -- Refill tokens based on elapsed time
      local elapsed = now - lastRefill
      tokens = math.min(capacity, tokens + (elapsed * refillRate))

      if tokens >= 1 then
        tokens = tokens - 1
        redis.call('HMSET', key, 'tokens', tokens, 'lastRefill', now)
        redis.call('EXPIRE', key, 3600)
        return 1
      else
        return 0
      end
    `;

    const result = await this.redis.eval(
      luaScript,
      1,
      key,
      this.capacity,
      this.refillRate,
      now
    );

    return result === 1;
  }
}
```

## Performance Monitoring

### Response Time Tracking

```typescript
// Middleware to track response times
app.use((req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - start;
    const endpoint = `${req.method} ${req.route?.path || req.path}`;

    // Track in Prometheus/monitoring system
    metrics.recordResponseTime(endpoint, duration, res.statusCode);

    // Log slow requests
    if (duration > 1000) { // 1 second threshold
      logger.warn('Slow request detected', {
        endpoint,
        duration,
        statusCode: res.statusCode,
        ip: req.ip
      });
    }
  });

  next();
});
```

### Database Query Monitoring

```typescript
// Database query interceptor
const originalQuery = database.query;
database.query = async function(...args: any[]) {
  const start = Date.now();

  try {
    const result = await originalQuery.apply(this, args);
    const duration = Date.now() - start;

    // Track query performance
    metrics.recordQueryDuration(args[0], duration);

    // Log slow queries
    if (duration > 500) { // 500ms threshold
      logger.warn('Slow query detected', {
        query: args[0],
        duration,
        params: args[1]
      });
    }

    return result;
  } catch (error) {
    const duration = Date.now() - start;
    metrics.recordQueryError(args[0], duration, error);
    throw error;
  }
};
```

## Compression and Minification

### Response Compression

```typescript
import compression from 'compression';

// Configure compression middleware
app.use(compression({
  level: 6, // Compression level (1-9)
  threshold: 1024, // Only compress responses larger than 1KB
  filter: (req, res) => {
    // Don't compress images or already compressed content
    if (req.headers['x-no-compression']) {
      return false;
    }

    const type = res.getHeader('Content-Type') as string;
    return !type || !type.includes('image');
  }
}));
```

### Static Asset Optimization

```typescript
// Serve static assets with optimization
app.use(express.static('public', {
  maxAge: '1y', // Cache for 1 year
  etag: true,
  lastModified: true,
  setHeaders: (res, path) => {
    if (path.endsWith('.js')) {
      res.setHeader('Content-Type', 'application/javascript');
    } else if (path.endsWith('.css')) {
      res.setHeader('Content-Type', 'text/css');
    }
  }
}));
```

## Load Balancing and Scaling

### Horizontal Scaling

```typescript
// Application clustering for multi-core utilization
import cluster from 'cluster';
import os from 'os';

if (cluster.isMaster) {
  const cpuCount = os.cpus().length;

  // Fork workers
  for (let i = 0; i < cpuCount; i++) {
    cluster.fork();
  }

  cluster.on('exit', (worker, code, signal) => {
    logger.info(`Worker ${worker.process.pid} died. Restarting...`);
    cluster.fork();
  });
} else {
  // Worker process
  const app = express();
  // ... application setup
  app.listen(process.env.PORT || 3000);
}
```

### Database Read Replicas

```typescript
// Read/write splitting for database scaling
class DatabaseManager {
  private primaryPool: Pool;
  private replicaPools: Pool[];

  constructor() {
    this.primaryPool = createPrimaryPool();
    this.replicaPools = createReplicaPools();
  }

  getPool(isWrite: boolean = false): Pool {
    if (isWrite) {
      return this.primaryPool;
    }

    // Round-robin selection for read replicas
    const index = Math.floor(Math.random() * this.replicaPools.length);
    return this.replicaPools[index];
  }
}
```

## CDN Integration

### Static Asset CDN

```typescript
// CDN URL generation for static assets
function getCdnUrl(path: string): string {
  if (process.env.NODE_ENV === 'development') {
    return `/assets/${path}`;
  }

  const cdnUrl = process.env.CDN_URL || 'https://cdn.example.com';
  const version = process.env.ASSET_VERSION || 'latest';

  return `${cdnUrl}/${version}/${path}`;
}
```

This comprehensive caching strategy and performance optimization approach ensures:
- **High Performance**: Multi-layer caching reduces database load
- **Scalability**: Horizontal scaling and read replicas handle growth
- **Reliability**: Proper error handling and monitoring
- **Cost Efficiency**: Optimized resource usage and reduced infrastructure costs
- **User Experience**: Fast response times and smooth interactions