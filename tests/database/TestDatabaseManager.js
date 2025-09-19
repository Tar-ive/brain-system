const { Pool } = require('pg');
const { MongoClient } = require('mongodb');
const dbManager = require('../../src/utils/database');
const logger = require('../../src/utils/logger');

class TestDatabaseManager {
  constructor() {
    this.testPostgresPool = null;
    this.testMongoClient = null;
    this.testMongoDb = null;
    this.testDatabases = {
      postgres: 'test_correlation_discovery',
      mongo: 'test_correlation_discovery'
    };
  }

  async connect() {
    const connections = [];

    // Connect to test PostgreSQL database
    try {
      this.testPostgresPool = new Pool({
        host: process.env.TEST_DB_HOST || 'localhost',
        port: parseInt(process.env.TEST_DB_PORT) || 5433,
        database: this.testDatabases.postgres,
        user: process.env.TEST_DB_USER || 'test_user',
        password: process.env.TEST_DB_PASSWORD || 'test_password',
        max: 5,
        idleTimeoutMillis: 30000,
        connectionTimeoutMillis: 2000
      });

      const client = await this.testPostgresPool.connect();
      await client.query('SELECT NOW()');
      client.release();

      logger.info('Test PostgreSQL connected successfully');
      connections.push({ type: 'postgres', success: true });
    } catch (error) {
      logger.warn('Test PostgreSQL connection failed:', error.message);
      connections.push({ type: 'postgres', success: false, error: error.message });
    }

    // Connect to test MongoDB database
    try {
      this.testMongoClient = new MongoClient(
        process.env.TEST_MONGODB_URI || 'mongodb://localhost:27018',
        {
          maxPoolSize: 5,
          serverSelectionTimeoutMS: 5000,
          socketTimeoutMS: 45000,
          connectTimeoutMS: 10000
        }
      );

      await this.testMongoClient.connect();
      this.testMongoDb = this.testMongoClient.db(this.testDatabases.mongo);

      logger.info('Test MongoDB connected successfully');
      connections.push({ type: 'mongo', success: true });
    } catch (error) {
      logger.warn('Test MongoDB connection failed:', error.message);
      connections.push({ type: 'mongo', success: false, error: error.message });
    }

    return connections;
  }

  async disconnect() {
    const disconnections = [];

    if (this.testPostgresPool) {
      try {
        await this.testPostgresPool.end();
        logger.info('Test PostgreSQL disconnected');
        disconnections.push({ type: 'postgres', success: true });
      } catch (error) {
        disconnections.push({ type: 'postgres', success: false, error: error.message });
      }
    }

    if (this.testMongoClient) {
      try {
        await this.testMongoClient.close();
        logger.info('Test MongoDB disconnected');
        disconnections.push({ type: 'mongo', success: true });
      } catch (error) {
        disconnections.push({ type: 'mongo', success: false, error: error.message });
      }
    }

    return disconnections;
  }

  async clearAllTables() {
    const results = {};

    // Clear PostgreSQL tables
    if (this.testPostgresPool) {
      try {
        const tables = [
          'validations',
          'training_episodes',
          'evolution_records',
          'performance_metrics',
          'dataset_signatures',
          'correlations',
          'datasets'
        ];

        for (const table of tables) {
          await this.testPostgresPool.query(`TRUNCATE TABLE ${table} CASCADE`);
        }

        results.postgres = { success: true, clearedTables: tables };
        logger.info('Test PostgreSQL tables cleared');
      } catch (error) {
        results.postgres = { success: false, error: error.message };
        logger.error('Failed to clear test PostgreSQL tables:', error.message);
      }
    }

    // Clear MongoDB collections
    if (this.testMongoClient) {
      try {
        const collections = await this.testMongoDb.listCollections().toArray();
        const collectionNames = collections.map(col => col.name);

        for (const collectionName of collectionNames) {
          await this.testMongoDb.collection(collectionName).deleteMany({});
        }

        results.mongo = { success: true, clearedCollections: collectionNames };
        logger.info('Test MongoDB collections cleared');
      } catch (error) {
        results.mongo = { success: false, error: error.message };
        logger.error('Failed to clear test MongoDB collections:', error.message);
      }
    }

    return results;
  }

  async setupTestDatabases() {
    const results = {};

    // Setup test PostgreSQL database
    if (this.testPostgresPool) {
      try {
        // Run migration scripts for test database
        const migrationFile = require('../../migrations/001_create_tables.sql');
        const fs = require('fs');
        const path = require('path');
        const sql = fs.readFileSync(path.join(__dirname, '..', '..', 'migrations', '001_create_tables.sql'), 'utf8');
        await this.testPostgresPool.query(sql);

        results.postgres = { success: true };
        logger.info('Test PostgreSQL database setup completed');
      } catch (error) {
        results.postgres = { success: false, error: error.message };
        logger.error('Failed to setup test PostgreSQL database:', error.message);
      }
    }

    // Setup test MongoDB database
    if (this.testMongoClient) {
      try {
        const { createCollections } = require('../../migrations/002_create_mongo_collections');
        await createCollections();

        results.mongo = { success: true };
        logger.info('Test MongoDB database setup completed');
      } catch (error) {
        results.mongo = { success: false, error: error.message };
        logger.error('Failed to setup test MongoDB database:', error.message);
      }
    }

    return results;
  }

  async seedTestData(data = {}) {
    const results = {};

    // Seed test data
    const datasets = data.datasets || this.generateTestDatasets();
    const correlations = data.correlations || this.generateTestCorrelations(datasets);
    const validations = data.validations || this.generateTestValidations(correlations);

    // Insert into PostgreSQL
    if (this.testPostgresPool) {
      try {
        for (const dataset of datasets) {
          await this.testPostgresPool.query(`
            INSERT INTO datasets (id, name, description, type, format, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
          `, [
            dataset.id, dataset.name, dataset.description, dataset.type, dataset.format,
            dataset.createdAt, dataset.updatedAt
          ]);
        }

        for (const correlation of correlations) {
          await this.testPostgresPool.query(`
            INSERT INTO correlations (id, source_dataset_id, target_dataset_id, type, confidence, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
          `, [
            correlation.id, correlation.sourceDatasetId, correlation.targetDatasetId,
            correlation.type, correlation.confidence, correlation.createdAt, correlation.updatedAt
          ]);
        }

        results.postgres = { success: true };
        logger.info('Test PostgreSQL data seeded');
      } catch (error) {
        results.postgres = { success: false, error: error.message };
        logger.error('Failed to seed test PostgreSQL data:', error.message);
      }
    }

    // Insert into MongoDB
    if (this.testMongoClient) {
      try {
        await this.testMongoDb.collection('datasets').insertMany(datasets);
        await this.testMongoDb.collection('correlations').insertMany(correlations);
        await this.testMongoDb.collection('validations').insertMany(validations);

        results.mongo = { success: true };
        logger.info('Test MongoDB data seeded');
      } catch (error) {
        results.mongo = { success: false, error: error.message };
        logger.error('Failed to seed test MongoDB data:', error.message);
      }
    }

    return results;
  }

  generateTestDatasets() {
    const { v4: uuidv4 } = require('uuid');
    const now = new Date().toISOString();

    return [
      {
        id: uuidv4(),
        name: 'Test Dataset 1',
        description: 'Test dataset for unit testing',
        type: 'structured',
        format: 'json',
        createdAt: now,
        updatedAt: now
      },
      {
        id: uuidv4(),
        name: 'Test Dataset 2',
        description: 'Another test dataset',
        type: 'structured',
        format: 'csv',
        createdAt: now,
        updatedAt: now
      },
      {
        id: uuidv4(),
        name: 'Test Dataset 3',
        description: 'Third test dataset',
        type: 'unstructured',
        format: 'json',
        createdAt: now,
        updatedAt: now
      }
    ];
  }

  generateTestCorrelations(datasets) {
    const { v4: uuidv4 } = require('uuid');
    const now = new Date().toISOString();

    return [
      {
        id: uuidv4(),
        sourceDatasetId: datasets[0].id,
        targetDatasetId: datasets[1].id,
        type: 'one_to_one',
        confidence: 0.85,
        createdAt: now,
        updatedAt: now
      },
      {
        id: uuidv4(),
        sourceDatasetId: datasets[1].id,
        targetDatasetId: datasets[2].id,
        type: 'many_to_many',
        confidence: 0.72,
        createdAt: now,
        updatedAt: now
      }
    ];
  }

  generateTestValidations(correlations) {
    const { v4: uuidv4 } = require('uuid');
    const now = new Date().toISOString();

    return [
      {
        id: uuidv4(),
        correlationId: correlations[0].id,
        validityScore: 0.88,
        statisticalScore: 0.85,
        semanticScore: 0.90,
        structuralScore: 0.87,
        createdAt: now,
        updatedAt: now
      },
      {
        id: uuidv4(),
        correlationId: correlations[1].id,
        validityScore: 0.75,
        statisticalScore: 0.70,
        semanticScore: 0.78,
        structuralScore: 0.77,
        createdAt: now,
        updatedAt: now
      }
    ];
  }

  async getTestStats() {
    const stats = {};

    // PostgreSQL stats
    if (this.testPostgresPool) {
      try {
        const datasetCount = await this.testPostgresPool.query('SELECT COUNT(*) FROM datasets');
        const correlationCount = await this.testPostgresPool.query('SELECT COUNT(*) FROM correlations');
        const validationCount = await this.testPostgresPool.query('SELECT COUNT(*) FROM validations');

        stats.postgres = {
          datasets: parseInt(datasetCount.rows[0].count),
          correlations: parseInt(correlationCount.rows[0].count),
          validations: parseInt(validationCount.rows[0].count)
        };
      } catch (error) {
        stats.postgres = { error: error.message };
      }
    }

    // MongoDB stats
    if (this.testMongoClient) {
      try {
        const datasetCount = await this.testMongoDb.collection('datasets').countDocuments();
        const correlationCount = await this.testMongoDb.collection('correlations').countDocuments();
        const validationCount = await this.testMongoDb.collection('validations').countDocuments();

        stats.mongo = {
          datasets: datasetCount,
          correlations: correlationCount,
          validations: validationCount
        };
      } catch (error) {
        stats.mongo = { error: error.message };
      }
    }

    return stats;
  }

  async runHealthCheck() {
    const health = {};

    // PostgreSQL health check
    if (this.testPostgresPool) {
      try {
        const start = Date.now();
        const client = await this.testPostgresPool.connect();
        await client.query('SELECT 1');
        client.release();
        const latency = Date.now() - start;

        health.postgres = { connected: true, latency, error: null };
      } catch (error) {
        health.postgres = { connected: false, latency: null, error: error.message };
      }
    }

    // MongoDB health check
    if (this.testMongoClient) {
      try {
        const start = Date.now();
        await this.testMongoDb.command({ ping: 1 });
        const latency = Date.now() - start;

        health.mongo = { connected: true, latency, error: null };
      } catch (error) {
        health.mongo = { connected: false, latency: null, error: error.message };
      }
    }

    return health;
  }
}

// Create singleton instance
const testDbManager = new TestDatabaseManager();

module.exports = testDbManager;