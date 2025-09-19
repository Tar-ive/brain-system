const { Pool } = require('pg');
const { MongoClient } = require('mongodb');
const { v4: uuidv4 } = require('uuid');
const logger = require('./logger');

class DatabaseManager {
  constructor() {
    this.postgresPool = null;
    this.mongoClient = null;
    this.mongoDb = null;
    this.isConnected = {
      postgres: false,
      mongo: false
    };
  }

  async connectPostgres(config = {}) {
    try {
      const pgConfig = {
        host: config.host || process.env.DB_HOST || 'localhost',
        port: parseInt(config.port || process.env.DB_PORT) || 5432,
        database: config.database || process.env.DB_NAME || 'correlation_discovery',
        user: config.user || process.env.DB_USER || 'postgres',
        password: config.password || process.env.DB_PASSWORD || 'password',
        max: parseInt(config.maxConnections || process.env.DB_MAX_CONNECTIONS) || 20,
        idleTimeoutMillis: parseInt(config.idleTimeout || process.env.DB_IDLE_TIMEOUT) || 30000,
        connectionTimeoutMillis: parseInt(config.connectionTimeout || process.env.DB_CONNECTION_TIMEOUT) || 2000,
        ssl: config.ssl || (process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : false)
      };

      this.postgresPool = new Pool(pgConfig);

      // Test connection
      const client = await this.postgresPool.connect();
      await client.query('SELECT NOW()');
      client.release();

      this.isConnected.postgres = true;
      logger.info('PostgreSQL connected successfully', {
        host: pgConfig.host,
        database: pgConfig.database,
        maxConnections: pgConfig.max
      });

      return this.postgresPool;
    } catch (error) {
      logger.error('PostgreSQL connection failed', { error: error.message });
      throw error;
    }
  }

  async connectMongo(config = {}) {
    try {
      const mongoConfig = {
        uri: config.uri || process.env.MONGODB_URI || 'mongodb://localhost:27017',
        dbName: config.dbName || process.env.MONGODB_DB_NAME || 'correlation_discovery',
        options: {
          maxPoolSize: config.maxPoolSize || parseInt(process.env.MONGO_MAX_POOL_SIZE) || 10,
          serverSelectionTimeoutMS: config.serverSelectionTimeoutMS || parseInt(process.env.MONGO_SERVER_SELECTION_TIMEOUT) || 5000,
          socketTimeoutMS: config.socketTimeoutMS || parseInt(process.env.MONGO_SOCKET_TIMEOUT) || 45000,
          connectTimeoutMS: config.connectTimeoutMS || parseInt(process.env.MONGO_CONNECT_TIMEOUT) || 10000,
          ...config.options
        }
      };

      this.mongoClient = new MongoClient(mongoConfig.uri, mongoConfig.options);
      await this.mongoClient.connect();
      this.mongoDb = this.mongoClient.db(mongoConfig.dbName);

      this.isConnected.mongo = true;
      logger.info('MongoDB connected successfully', {
        uri: mongoConfig.uri,
        database: mongoConfig.dbName
      });

      return this.mongoClient;
    } catch (error) {
      logger.error('MongoDB connection failed', { error: error.message });
      throw error;
    }
  }

  async connect(config = {}) {
    const connections = [];

    try {
      if (config.postgres !== false) {
        const pgConnection = await this.connectPostgres(config.postgres);
        connections.push({ type: 'postgres', connection: pgConnection });
      }
    } catch (error) {
      logger.warn('PostgreSQL connection failed, continuing without it');
    }

    try {
      if (config.mongo !== false) {
        const mongoConnection = await this.connectMongo(config.mongo);
        connections.push({ type: 'mongo', connection: mongoConnection });
      }
    } catch (error) {
      logger.warn('MongoDB connection failed, continuing without it');
    }

    if (connections.length === 0) {
      throw new Error('No database connections could be established');
    }

    logger.info('Database connections established', {
      postgres: this.isConnected.postgres,
      mongo: this.isConnected.mongo
    });

    return connections;
  }

  async disconnect() {
    const disconnections = [];

    if (this.postgresPool) {
      try {
        await this.postgresPool.end();
        this.isConnected.postgres = false;
        disconnections.push({ type: 'postgres', success: true });
        logger.info('PostgreSQL disconnected');
      } catch (error) {
        disconnections.push({ type: 'postgres', success: false, error: error.message });
        logger.error('PostgreSQL disconnection failed', { error: error.message });
      }
    }

    if (this.mongoClient) {
      try {
        await this.mongoClient.close();
        this.isConnected.mongo = false;
        disconnections.push({ type: 'mongo', success: true });
        logger.info('MongoDB disconnected');
      } catch (error) {
        disconnections.push({ type: 'mongo', success: false, error: error.message });
        logger.error('MongoDB disconnection failed', { error: error.message });
      }
    }

    return disconnections;
  }

  async healthCheck() {
    const health = {
      postgres: { connected: false, latency: null, error: null },
      mongo: { connected: false, latency: null, error: null }
    };

    // Check PostgreSQL
    if (this.postgresPool) {
      try {
        const start = Date.now();
        const client = await this.postgresPool.connect();
        await client.query('SELECT 1');
        client.release();
        const latency = Date.now() - start;

        health.postgres = { connected: true, latency, error: null };
      } catch (error) {
        health.postgres = { connected: false, latency: null, error: error.message };
      }
    }

    // Check MongoDB
    if (this.mongoClient) {
      try {
        const start = Date.now();
        await this.mongoDb.command({ ping: 1 });
        const latency = Date.now() - start;

        health.mongo = { connected: true, latency, error: null };
      } catch (error) {
        health.mongo = { connected: false, latency: null, error: error.message };
      }
    }

    return health;
  }

  // PostgreSQL specific methods
  async query(sql, params = []) {
    if (!this.isConnected.postgres) {
      throw new Error('PostgreSQL not connected');
    }

    const start = Date.now();
    try {
      const result = await this.postgresPool.query(sql, params);
      const duration = Date.now() - start;
      logger.query(sql, params, duration);
      return result;
    } catch (error) {
      logger.dbError(error, sql, params);
      throw error;
    }
  }

  async transaction(callback) {
    if (!this.isConnected.postgres) {
      throw new Error('PostgreSQL not connected');
    }

    const client = await this.postgresPool.connect();
    try {
      await client.query('BEGIN');
      const result = await callback(client);
      await client.query('COMMIT');
      return result;
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  // MongoDB specific methods
  getCollection(name) {
    if (!this.isConnected.mongo) {
      throw new Error('MongoDB not connected');
    }
    return this.mongoDb.collection(name);
  }

  async insertOne(collectionName, document) {
    if (!this.isConnected.mongo) {
      throw new Error('MongoDB not connected');
    }

    const collection = this.getCollection(collectionName);
    const start = Date.now();
    try {
      const result = await collection.insertOne(document);
      const duration = Date.now() - start;
      logger.query(`insertOne ${collectionName}`, [document], duration);
      return result;
    } catch (error) {
      logger.dbError(error, `insertOne ${collectionName}`, [document]);
      throw error;
    }
  }

  async findMany(collectionName, filter = {}, options = {}) {
    if (!this.isConnected.mongo) {
      throw new Error('MongoDB not connected');
    }

    const collection = this.getCollection(collectionName);
    const start = Date.now();
    try {
      const result = await collection.find(filter, options).toArray();
      const duration = Date.now() - start;
      logger.query(`findMany ${collectionName}`, [filter, options], duration);
      return result;
    } catch (error) {
      logger.dbError(error, `findMany ${collectionName}`, [filter, options]);
      throw error;
    }
  }

  async updateOne(collectionName, filter, update, options = {}) {
    if (!this.isConnected.mongo) {
      throw new Error('MongoDB not connected');
    }

    const collection = this.getCollection(collectionName);
    const start = Date.now();
    try {
      const result = await collection.updateOne(filter, update, options);
      const duration = Date.now() - start;
      logger.query(`updateOne ${collectionName}`, [filter, update], duration);
      return result;
    } catch (error) {
      logger.dbError(error, `updateOne ${collectionName}`, [filter, update]);
      throw error;
    }
  }

  async deleteOne(collectionName, filter, options = {}) {
    if (!this.isConnected.mongo) {
      throw new Error('MongoDB not connected');
    }

    const collection = this.getCollection(collectionName);
    const start = Date.now();
    try {
      const result = await collection.deleteOne(filter, options);
      const duration = Date.now() - start;
      logger.query(`deleteOne ${collectionName}`, [filter], duration);
      return result;
    } catch (error) {
      logger.dbError(error, `deleteOne ${collectionName}`, [filter]);
      throw error;
    }
  }

  // Utility methods
  generateUUID() {
    return uuidv4();
  }

  isPostgresConnected() {
    return this.isConnected.postgres;
  }

  isMongoConnected() {
    return this.isConnected.mongo;
  }

  getStats() {
    return {
      postgres: {
        connected: this.isConnected.postgres,
        pool: this.postgresPool ? {
          total: this.postgresPool.totalCount,
          idle: this.postgresPool.idleCount,
          waiting: this.postgresPool.waitingCount
        } : null
      },
      mongo: {
        connected: this.isConnected.mongo,
        client: this.mongoClient ? {
          topology: this.mongoClient.topology ? this.mongoClient.topology.description : null
        } : null
      }
    };
  }
}

// Create singleton instance
const dbManager = new DatabaseManager();

module.exports = dbManager;