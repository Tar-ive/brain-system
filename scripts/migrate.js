#!/usr/bin/env node

const { Pool } = require('pg');
const { MongoClient } = require('mongodb');
const fs = require('fs');
const path = require('path');
const winston = require('winston');

// Configure logging
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'logs/migration.log' })
  ]
});

// Database configuration
const config = {
  postgres: {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT) || 5432,
    database: process.env.DB_NAME || 'correlation_discovery',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD || 'password'
  },
  mongo: {
    uri: process.env.MONGODB_URI || 'mongodb://localhost:27017',
    dbName: process.env.MONGODB_DB_NAME || 'correlation_discovery'
  }
};

class MigrationManager {
  constructor() {
    this.migrationsDir = path.join(__dirname, '..', 'migrations');
    this.postgresPool = null;
    this.mongoClient = null;
  }

  async initialize() {
    // Create logs directory if it doesn't exist
    const logsDir = path.join(__dirname, '..', 'logs');
    if (!fs.existsSync(logsDir)) {
      fs.mkdirSync(logsDir, { recursive: true });
    }
  }

  async connectPostgres() {
    try {
      this.postgresPool = new Pool(config.postgres);
      await this.postgresPool.query('SELECT NOW()');
      logger.info('Connected to PostgreSQL');
    } catch (error) {
      logger.error('PostgreSQL connection failed:', error);
      throw error;
    }
  }

  async connectMongo() {
    try {
      this.mongoClient = new MongoClient(config.mongo.uri);
      await this.mongoClient.connect();
      logger.info('Connected to MongoDB');
    } catch (error) {
      logger.error('MongoDB connection failed:', error);
      throw error;
    }
  }

  async disconnect() {
    if (this.postgresPool) {
      await this.postgresPool.end();
    }
    if (this.mongoClient) {
      await this.mongoClient.close();
    }
  }

  async runPostgresMigration() {
    try {
      const migrationFile = path.join(this.migrationsDir, '001_create_tables.sql');
      if (!fs.existsSync(migrationFile)) {
        logger.warn('PostgreSQL migration file not found:', migrationFile);
        return;
      }

      const sql = fs.readFileSync(migrationFile, 'utf8');
      await this.postgresPool.query(sql);
      logger.info('PostgreSQL migration completed successfully');
    } catch (error) {
      logger.error('PostgreSQL migration failed:', error);
      throw error;
    }
  }

  async runMongoMigration() {
    try {
      const migrationFile = path.join(this.migrationsDir, '002_create_mongo_collections.js');
      if (!fs.existsSync(migrationFile)) {
        logger.warn('MongoDB migration file not found:', migrationFile);
        return;
      }

      // Clear require cache to ensure fresh import
      delete require.cache[require.resolve(migrationFile)];
      const { createCollections } = require(migrationFile);
      await createCollections();
      logger.info('MongoDB migration completed successfully');
    } catch (error) {
      logger.error('MongoDB migration failed:', error);
      throw error;
    }
  }

  async checkMigrationStatus() {
    const status = {
      postgres: false,
      mongo: false,
      postgres_tables: [],
      mongo_collections: []
    };

    // Check PostgreSQL
    try {
      if (this.postgresPool) {
        const result = await this.postgresPool.query(`
          SELECT table_name
          FROM information_schema.tables
          WHERE table_schema = 'public'
          AND table_name IN (
            'datasets', 'correlations', 'dataset_signatures', 'validations',
            'training_episodes', 'evolution_records', 'performance_metrics'
          )
        `);
        status.postgres = result.rows.length > 0;
        status.postgres_tables = result.rows.map(row => row.table_name);
      }
    } catch (error) {
      logger.warn('PostgreSQL status check failed:', error.message);
    }

    // Check MongoDB
    try {
      if (this.mongoClient) {
        const db = this.mongoClient.db(config.mongo.dbName);
        const collections = await db.listCollections().toArray();
        status.mongo = collections.length > 0;
        status.mongo_collections = collections.map(col => col.name);
      }
    } catch (error) {
      logger.warn('MongoDB status check failed:', error.message);
    }

    return status;
  }

  async createMigrationTable() {
    try {
      await this.postgresPool.query(`
        CREATE TABLE IF NOT EXISTS schema_migrations (
          version VARCHAR(255) PRIMARY KEY,
          applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          description TEXT
        )
      `);
      logger.info('Migration table created/verified');
    } catch (error) {
      logger.error('Failed to create migration table:', error);
      throw error;
    }
  }

  async recordMigration(version, description) {
    try {
      await this.postgresPool.query(`
        INSERT INTO schema_migrations (version, description)
        VALUES ($1, $2)
        ON CONFLICT (version) DO UPDATE
        SET applied_at = CURRENT_TIMESTAMP
      `, [version, description]);
      logger.info(`Migration ${version} recorded`);
    } catch (error) {
      logger.error(`Failed to record migration ${version}:`, error);
      throw error;
    }
  }

  async getAppliedMigrations() {
    try {
      const result = await this.postgresPool.query(`
        SELECT version, applied_at, description
        FROM schema_migrations
        ORDER BY applied_at
      `);
      return result.rows;
    } catch (error) {
      logger.warn('Failed to get applied migrations:', error.message);
      return [];
    }
  }

  async rollback(version) {
    logger.warn('Rollback functionality not implemented');
    throw new Error('Rollback not implemented in this version');
  }

  async run() {
    try {
      await this.initialize();
      logger.info('Starting database migration');

      // Check database connections
      try {
        await this.connectPostgres();
      } catch (error) {
        logger.warn('PostgreSQL not available, skipping');
      }

      try {
        await this.connectMongo();
      } catch (error) {
        logger.warn('MongoDB not available, skipping');
      }

      // Check current status
      const status = await this.checkMigrationStatus();
      logger.info('Current database status:', status);

      // Create migration tracking table (PostgreSQL only)
      if (this.postgresPool) {
        await this.createMigrationTable();
      }

      // Run migrations
      if (this.postgresPool && !status.postgres) {
        logger.info('Running PostgreSQL migration...');
        await this.runPostgresMigration();
        await this.recordMigration('001', 'Create core tables');
      }

      if (this.mongoClient && !status.mongo) {
        logger.info('Running MongoDB migration...');
        await this.runMongoMigration();
        // Record MongoDB migration in PostgreSQL for tracking
        if (this.postgresPool) {
          await this.recordMigration('002', 'Create MongoDB collections');
        }
      }

      // Final status check
      const finalStatus = await this.checkMigrationStatus();
      logger.info('Final database status:', finalStatus);

      const appliedMigrations = this.postgresPool ? await this.getAppliedMigrations() : [];
      logger.info('Applied migrations:', appliedMigrations);

      logger.info('Migration completed successfully');

    } catch (error) {
      logger.error('Migration failed:', error);
      throw error;
    } finally {
      await this.disconnect();
    }
  }
}

// Command line interface
async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'up';

  const migrator = new MigrationManager();

  try {
    switch (command) {
      case 'up':
        await migrator.run();
        break;
      case 'status':
        await migrator.initialize();
        await migrator.connectPostgres();
        await migrator.connectMongo();
        const status = await migrator.checkMigrationStatus();
        console.log(JSON.stringify(status, null, 2));
        break;
      case 'rollback':
        const version = args[1];
        if (!version) {
          console.error('Version required for rollback');
          process.exit(1);
        }
        await migrator.initialize();
        await migrator.connectPostgres();
        await migrator.rollback(version);
        break;
      default:
        console.error('Unknown command:', command);
        console.log('Available commands: up, status, rollback <version>');
        process.exit(1);
    }
  } catch (error) {
    logger.error('Migration script failed:', error);
    process.exit(1);
  }
}

// Export for programmatic use
module.exports = { MigrationManager };

// Run if called directly
if (require.main === module) {
  main();
}