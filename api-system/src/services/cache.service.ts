import { createClient } from 'redis';
import { logger } from '../utils/logger';

export class CacheService {
  private client: any;
  private isConnected: boolean = false;

  constructor() {
    this.initializeRedis();
  }

  /**
   * Initialize Redis connection
   */
  private async initializeRedis(): Promise<void> {
    try {
      const redisUrl = process.env.REDIS_URL || 'redis://localhost:6379';

      this.client = createClient({
        url: redisUrl,
        socket: {
          reconnectStrategy: (retries: number) => {
            if (retries > 10) {
              logger.error('Redis reconnection failed after 10 attempts');
              return new Error('Redis reconnection failed');
            }
            return Math.min(retries * 50, 500);
          }
        }
      });

      this.client.on('error', (err: Error) => {
        logger.error('Redis client error', { error: err.message });
        this.isConnected = false;
      });

      this.client.on('connect', () => {
        logger.info('Redis client connected');
        this.isConnected = true;
      });

      this.client.on('ready', () => {
        logger.info('Redis client ready');
        this.isConnected = true;
      });

      this.client.on('end', () => {
        logger.info('Redis client disconnected');
        this.isConnected = false;
      });

      await this.client.connect();
      this.isConnected = true;

      logger.info('Redis connection established successfully');
    } catch (error) {
      logger.error('Failed to initialize Redis connection', { error });
      this.isConnected = false;
    }
  }

  /**
   * Check if Redis is connected
   */
  public isHealthy(): boolean {
    return this.isConnected;
  }

  /**
   * Get value from cache
   */
  public async get(key: string): Promise<any> {
    try {
      if (!this.isConnected) {
        return null;
      }

      const value = await this.client.get(key);
      if (!value) {
        return null;
      }

      try {
        return JSON.parse(value);
      } catch {
        return value;
      }
    } catch (error) {
      logger.error('Cache get error', { key, error: error.message });
      return null;
    }
  }

  /**
   * Set value in cache with TTL
   */
  public async set(key: string, value: any, ttlSeconds: number = 3600): Promise<boolean> {
    try {
      if (!this.isConnected) {
        return false;
      }

      const serializedValue = typeof value === 'string' ? value : JSON.stringify(value);
      await this.client.setEx(key, ttlSeconds, serializedValue);
      return true;
    } catch (error) {
      logger.error('Cache set error', { key, error: error.message });
      return false;
    }
  }

  /**
   * Delete key from cache
   */
  public async del(key: string): Promise<boolean> {
    try {
      if (!this.isConnected) {
        return false;
      }

      await this.client.del(key);
      return true;
    } catch (error) {
      logger.error('Cache delete error', { key, error: error.message });
      return false;
    }
  }

  /**
   * Delete multiple keys from cache
   */
  public async delMultiple(keys: string[]): Promise<boolean> {
    try {
      if (!this.isConnected || keys.length === 0) {
        return false;
      }

      await this.client.del(keys);
      return true;
    } catch (error) {
      logger.error('Cache delete multiple error', { keys, error: error.message });
      return false;
    }
  }

  /**
   * Check if key exists
   */
  public async exists(key: string): Promise<boolean> {
    try {
      if (!this.isConnected) {
        return false;
      }

      const result = await this.client.exists(key);
      return result === 1;
    } catch (error) {
      logger.error('Cache exists error', { key, error: error.message });
      return false;
    }
  }

  /**
   * Set expiration time for key
   */
  public async expire(key: string, ttlSeconds: number): Promise<boolean> {
    try {
      if (!this.isConnected) {
        return false;
      }

      await this.client.expire(key, ttlSeconds);
      return true;
    } catch (error) {
      logger.error('Cache expire error', { key, error: error.message });
      return false;
    }
  }

  /**
   * Get key TTL
   */
  public async ttl(key: string): Promise<number> {
    try {
      if (!this.isConnected) {
        return -1;
      }

      return await this.client.ttl(key);
    } catch (error) {
      logger.error('Cache TTL error', { key, error: error.message });
      return -1;
    }
  }

  /**
   * Increment value
   */
  public async incr(key: string, increment: number = 1): Promise<number> {
    try {
      if (!this.isConnected) {
        return 0;
      }

      return await this.client.incrBy(key, increment);
    } catch (error) {
      logger.error('Cache increment error', { key, error: error.message });
      return 0;
    }
  }

  /**
   * Decrement value
   */
  public async decr(key: string, decrement: number = 1): Promise<number> {
    try {
      if (!this.isConnected) {
        return 0;
      }

      return await this.client.decrBy(key, decrement);
    } catch (error) {
      logger.error('Cache decrement error', { key, error: error.message });
      return 0;
    }
  }

  /**
   * Get all keys matching pattern
   */
  public async keys(pattern: string): Promise<string[]> {
    try {
      if (!this.isConnected) {
        return [];
      }

      return await this.client.keys(pattern);
    } catch (error) {
      logger.error('Cache keys error', { pattern, error: error.message });
      return [];
    }
  }

  /**
   * Hash operations
   */
  public async hget(key: string, field: string): Promise<any> {
    try {
      if (!this.isConnected) {
        return null;
      }

      const value = await this.client.hGet(key, field);
      if (!value) {
        return null;
      }

      try {
        return JSON.parse(value);
      } catch {
        return value;
      }
    } catch (error) {
      logger.error('Cache hget error', { key, field, error: error.message });
      return null;
    }
  }

  public async hset(key: string, field: string, value: any): Promise<boolean> {
    try {
      if (!this.isConnected) {
        return false;
      }

      const serializedValue = typeof value === 'string' ? value : JSON.stringify(value);
      await this.client.hSet(key, field, serializedValue);
      return true;
    } catch (error) {
      logger.error('Cache hset error', { key, field, error: error.message });
      return false;
    }
  }

  public async hgetall(key: string): Promise<Record<string, any>> {
    try {
      if (!this.isConnected) {
        return {};
      }

      const hash = await this.client.hGetAll(key);
      const result: Record<string, any> = {};

      for (const [field, value] of Object.entries(hash)) {
        try {
          result[field] = JSON.parse(value);
        } catch {
          result[field] = value;
        }
      }

      return result;
    } catch (error) {
      logger.error('Cache hgetall error', { key, error: error.message });
      return {};
    }
  }

  public async hdel(key: string, field: string): Promise<boolean> {
    try {
      if (!this.isConnected) {
        return false;
      }

      await this.client.hDel(key, field);
      return true;
    } catch (error) {
      logger.error('Cache hdel error', { key, field, error: error.message });
      return false;
    }
  }

  /**
   * List operations
   */
  public async lpush(key: string, ...values: any[]): Promise<number> {
    try {
      if (!this.isConnected) {
        return 0;
      }

      const serializedValues = values.map(v => typeof v === 'string' ? v : JSON.stringify(v));
      return await this.client.lPush(key, serializedValues);
    } catch (error) {
      logger.error('Cache lpush error', { key, error: error.message });
      return 0;
    }
  }

  public async rpush(key: string, ...values: any[]): Promise<number> {
    try {
      if (!this.isConnected) {
        return 0;
      }

      const serializedValues = values.map(v => typeof v === 'string' ? v : JSON.stringify(v));
      return await this.client.rPush(key, serializedValues);
    } catch (error) {
      logger.error('Cache rpush error', { key, error: error.message });
      return 0;
    }
  }

  public async lpop(key: string): Promise<any> {
    try {
      if (!this.isConnected) {
        return null;
      }

      const value = await this.client.lPop(key);
      if (!value) {
        return null;
      }

      try {
        return JSON.parse(value);
      } catch {
        return value;
      }
    } catch (error) {
      logger.error('Cache lpop error', { key, error: error.message });
      return null;
    }
  }

  public async rpop(key: string): Promise<any> {
    try {
      if (!this.isConnected) {
        return null;
      }

      const value = await this.client.rPop(key);
      if (!value) {
        return null;
      }

      try {
        return JSON.parse(value);
      } catch {
        return value;
      }
    } catch (error) {
      logger.error('Cache rpop error', { key, error: error.message });
      return null;
    }
  }

  public async llen(key: string): Promise<number> {
    try {
      if (!this.isConnected) {
        return 0;
      }

      return await this.client.lLen(key);
    } catch (error) {
      logger.error('Cache llen error', { key, error: error.message });
      return 0;
    }
  }

  /**
   * Set operations
   */
  public async sadd(key: string, ...members: any[]): Promise<number> {
    try {
      if (!this.isConnected) {
        return 0;
      }

      const serializedMembers = members.map(m => typeof m === 'string' ? m : JSON.stringify(m));
      return await this.client.sAdd(key, serializedMembers);
    } catch (error) {
      logger.error('Cache sadd error', { key, error: error.message });
      return 0;
    }
  }

  public async srem(key: string, ...members: any[]): Promise<number> {
    try {
      if (!this.isConnected) {
        return 0;
      }

      const serializedMembers = members.map(m => typeof m === 'string' ? m : JSON.stringify(m));
      return await this.client.sRem(key, serializedMembers);
    } catch (error) {
      logger.error('Cache srem error', { key, error: error.message });
      return 0;
    }
  }

  public async smembers(key: string): Promise<any[]> {
    try {
      if (!this.isConnected) {
        return [];
      }

      const members = await this.client.sMembers(key);
      return members.map(member => {
        try {
          return JSON.parse(member);
        } catch {
          return member;
        }
      });
    } catch (error) {
      logger.error('Cache smembers error', { key, error: error.message });
      return [];
    }
  }

  /**
   * Cache invalidation utilities
   */
  public async invalidatePattern(pattern: string): Promise<void> {
    try {
      if (!this.isConnected) {
        return;
      }

      const keys = await this.keys(pattern);
      if (keys.length > 0) {
        await this.delMultiple(keys);
        logger.info(`Cache pattern invalidated`, { pattern, keysCount: keys.length });
      }
    } catch (error) {
      logger.error('Cache invalidation error', { pattern, error: error.message });
    }
  }

  /**
   * Cache warming (pre-populate frequently accessed data)
   */
  public async warmCache(keys: Array<{ key: string; value: any; ttl: number }>): Promise<void> {
    try {
      if (!this.isConnected) {
        return;
      }

      const pipeline = this.client.multi();

      for (const { key, value, ttl } of keys) {
        const serializedValue = typeof value === 'string' ? value : JSON.stringify(value);
        pipeline.setEx(key, ttl, serializedValue);
      }

      await pipeline.exec();
      logger.info(`Cache warmed`, { keysCount: keys.length });
    } catch (error) {
      logger.error('Cache warming error', { error: error.message });
    }
  }

  /**
   * Cache statistics
   */
  public async getStats(): Promise<{
    connected: boolean;
    memoryUsed?: number;
    memoryPeak?: number;
    keyCount?: number;
    uptime?: number;
  }> {
    try {
      if (!this.isConnected) {
        return { connected: false };
      }

      const [info, dbsize] = await Promise.all([
        this.client.info('memory'),
        this.client.dbSize()
      ]);

      const memoryUsed = this.parseRedisInfo(info, 'used_memory');
      const memoryPeak = this.parseRedisInfo(info, 'used_memory_peak');
      const uptime = this.parseRedisInfo(info, 'uptime_in_seconds');

      return {
        connected: true,
        memoryUsed,
        memoryPeak,
        keyCount: dbsize,
        uptime
      };
    } catch (error) {
      logger.error('Cache stats error', { error: error.message });
      return { connected: false };
    }
  }

  private parseRedisInfo(info: string, key: string): number | undefined {
    const line = info.split('\n').find(line => line.startsWith(`${key}:`));
    return line ? parseInt(line.split(':')[1]) : undefined;
  }

  /**
   * Close Redis connection
   */
  public async close(): Promise<void> {
    try {
      if (this.client) {
        await this.client.quit();
        this.isConnected = false;
        logger.info('Redis connection closed');
      }
    } catch (error) {
      logger.error('Error closing Redis connection', { error: error.message });
    }
  }
}

// Export singleton instance
export const cacheService = new CacheService();