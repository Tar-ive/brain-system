#!/usr/bin/env node

const { v4: uuidv4 } = require('uuid');
const winston = require('winston');
const path = require('path');

// Import database utilities
const dbManager = require('../src/utils/database');
const ValidationUtils = require('../src/utils/validation');

// Configure logging
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    })
  ]
});

class DatabaseSeeder {
  constructor() {
    this.seedData = {
      datasets: [],
      correlations: [],
      validations: []
    };
  }

  async connect() {
    try {
      await dbManager.connect();
      logger.info('Database connected for seeding');
    } catch (error) {
      logger.error('Failed to connect to database for seeding:', error);
      throw error;
    }
  }

  async disconnect() {
    try {
      await dbManager.disconnect();
      logger.info('Database disconnected after seeding');
    } catch (error) {
      logger.error('Failed to disconnect from database:', error);
    }
  }

  generateSampleDatasets() {
    const datasets = [
      {
        name: 'Customer Demographics',
        description: 'Customer demographic data including age, income, and location',
        type: 'structured',
        source: 'internal',
        format: 'json',
        size: 1024000,
        recordCount: 10000,
        schema: {
          fields: [
            { name: 'customer_id', type: 'string' },
            { name: 'age', type: 'integer' },
            { name: 'income', type: 'decimal' },
            { name: 'location', type: 'string' },
            { name: 'signup_date', type: 'date' }
          ]
        },
        tags: ['customer', 'demographics', 'sales'],
        visibility: 'public'
      },
      {
        name: 'Product Sales',
        description: 'Product sales data with transaction details',
        type: 'structured',
        source: 'internal',
        format: 'csv',
        size: 2048000,
        recordCount: 50000,
        schema: {
          fields: [
            { name: 'transaction_id', type: 'string' },
            { name: 'product_id', type: 'string' },
            { name: 'quantity', type: 'integer' },
            { name: 'price', type: 'decimal' },
            { name: 'sale_date', type: 'date' }
          ]
        },
        tags: ['sales', 'products', 'transactions'],
        visibility: 'public'
      },
      {
        name: 'Geographic Coordinates',
        description: 'Geographic coordinate data for locations',
        type: 'structured',
        source: 'external',
        format: 'json',
        size: 512000,
        recordCount: 5000,
        schema: {
          fields: [
            { name: 'location_id', type: 'string' },
            { name: 'latitude', type: 'decimal' },
            { name: 'longitude', type: 'decimal' },
            { name: 'country', type: 'string' },
            { name: 'region', type: 'string' }
          ]
        },
        tags: ['geographic', 'coordinates', 'locations'],
        visibility: 'public'
      },
      {
        name: 'Time Series Data',
        description: 'Historical time series data for analysis',
        type: 'structured',
        source: 'internal',
        format: 'json',
        size: 1536000,
        recordCount: 25000,
        schema: {
          fields: [
            { name: 'timestamp', type: 'datetime' },
            { name: 'value', type: 'decimal' },
            { name: 'metric_type', type: 'string' },
            { name: 'category', type: 'string' }
          ]
        },
        tags: ['time-series', 'historical', 'analytics'],
        visibility: 'shared'
      },
      {
        name: 'Unstructured Text Data',
        description: 'Collection of unstructured text documents',
        type: 'unstructured',
        source: 'external',
        format: 'json',
        size: 5120000,
        recordCount: 1000,
        schema: {
          fields: [
            { name: 'document_id', type: 'string' },
            { name: 'content', type: 'text' },
            { name: 'language', type: 'string' },
            { name: 'category', type: 'string' }
          ]
        },
        tags: ['text', 'unstructured', 'documents'],
        visibility: 'private'
      }
    ];

    return datasets.map(dataset => ({
      ...dataset,
      id: uuidv4(),
      metadata: {
        generated: true,
        seedData: true,
        generatedAt: new Date().toISOString()
      }
    }));
  }

  generateSampleCorrelations(datasets) {
    const correlations = [];

    if (datasets.length < 2) return correlations;

    // Create various types of correlations
    const correlationTypes = [
      { type: 'one_to_many', confidence: 0.85, discoveryMethod: 'statistical' },
      { type: 'many_to_one', confidence: 0.72, discoveryMethod: 'neural_network' },
      { type: 'many_to_many', confidence: 0.68, discoveryMethod: 'evolutionary' },
      { type: 'weighted_many_to_many', confidence: 0.91, discoveryMethod: 'mcts' },
      { type: 'temporal', confidence: 0.76, discoveryMethod: 'information_theory' }
    ];

    for (let i = 0; i < Math.min(datasets.length, 3); i++) {
      for (let j = i + 1; j < Math.min(datasets.length, 4); j++) {
        const correlationType = correlationTypes[Math.floor(Math.random() * correlationTypes.length)];

        correlations.push({
          sourceDatasetId: datasets[i].id,
          targetDatasetId: datasets[j].id,
          type: correlationType.type,
          confidence: Math.random() * 0.3 + 0.6, // Random confidence between 0.6-0.9
          validityScore: Math.random() * 0.3 + 0.5, // Random validity between 0.5-0.8
          description: `Discovered ${correlationType.type} correlation between ${datasets[i].name} and ${datasets[j].name}`,
          status: Math.random() > 0.3 ? 'validated' : 'proposed',
          parameters: {
            strength: Math.random(),
            direction: Math.random() > 0.5 ? 'positive' : 'negative',
            lag: Math.floor(Math.random() * 10)
          },
          discoveryMethod: correlationType.discoveryMethod,
          tags: [correlationType.type, correlationType.discoveryMethod],
          metadata: {
            generated: true,
            seedData: true,
            discoveryAccuracy: Math.random()
          }
        });
      }
    }

    return correlations.map(correlation => ({
      ...correlation,
      id: uuidv4()
    }));
  }

  generateSampleValidations(correlations) {
    const validations = [];

    correlations.forEach(correlation => {
      const validationMethods = ['statistical', 'semantic', 'structural', 'conservation', 'ensemble'];
      const method = validationMethods[Math.floor(Math.random() * validationMethods.length)];

      validations.push({
        correlationId: correlation.id,
        validityScore: Math.random() * 0.4 + 0.4, // Random validity between 0.4-0.8
        statisticalScore: Math.random() * 0.4 + 0.4,
        semanticScore: Math.random() * 0.4 + 0.4,
        structuralScore: Math.random() * 0.4 + 0.4,
        conservationError: Math.random() * 0.15, // Random error between 0-0.15
        testAccuracy: Math.random() * 0.3 + 0.6, // Random accuracy between 0.6-0.9
        confidenceInterval: [Math.random() * 0.2, Math.random() * 0.3 + 0.7],
        validationMethod: method,
        validationTime: Math.floor(Math.random() * 5000) + 1000, // Random time between 1-6 seconds
        dataSize: Math.floor(Math.random() * 10000) + 1000,
        sampleSize: Math.floor(Math.random() * 1000) + 100,
        metadata: {
          generated: true,
          seedData: true,
          validationDepth: Math.random()
        }
      });
    });

    return validations.map(validation => ({
      ...validation,
      id: uuidv4()
    }));
  }

  async seedPostgres() {
    if (!dbManager.isPostgresConnected()) {
      logger.warn('PostgreSQL not connected, skipping PostgreSQL seeding');
      return;
    }

    logger.info('Seeding PostgreSQL database');

    try {
      // Clear existing data (optional, for development)
      await dbManager.query('TRUNCATE TABLE validations, correlations, datasets CASCADE');

      // Seed datasets
      const datasets = this.generateSampleDatasets();
      for (const dataset of datasets) {
        await dbManager.query(`
          INSERT INTO datasets (
            id, name, description, type, source, format, size, record_count,
            schema, metadata, tags, visibility, created_at, updated_at
          ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
        `, [
          dataset.id, dataset.name, dataset.description, dataset.type, dataset.source,
          dataset.format, dataset.size, dataset.recordCount, JSON.stringify(dataset.schema),
          JSON.stringify(dataset.metadata), dataset.tags, dataset.visibility,
          dataset.metadata.generatedAt, dataset.metadata.generatedAt
        ]);
      }

      logger.info(`Seeded ${datasets.length} datasets in PostgreSQL`);

      // Seed correlations
      const correlations = this.generateSampleCorrelations(datasets);
      for (const correlation of correlations) {
        await dbManager.query(`
          INSERT INTO correlations (
            id, source_dataset_id, target_dataset_id, type, parameters, confidence,
            validity_score, description, status, discovery_method, tags, metadata,
            created_at, updated_at
          ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
        `, [
          correlation.id, correlation.sourceDatasetId, correlation.targetDatasetId,
          correlation.type, JSON.stringify(correlation.parameters), correlation.confidence,
          correlation.validityScore, correlation.description, correlation.status,
          correlation.discoveryMethod, correlation.tags, JSON.stringify(correlation.metadata),
          correlation.metadata.generatedAt, correlation.metadata.generatedAt
        ]);
      }

      logger.info(`Seeded ${correlations.length} correlations in PostgreSQL`);

      // Seed validations
      const validations = this.generateSampleValidations(correlations);
      for (const validation of validations) {
        await dbManager.query(`
          INSERT INTO validations (
            id, correlation_id, validity_score, statistical_score, semantic_score,
            structural_score, conservation_error, test_accuracy, confidence_interval,
            validation_method, validation_time, data_size, sample_size, metadata,
            created_at, updated_at
          ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
        `, [
          validation.id, validation.correlationId, validation.validityScore,
          validation.statisticalScore, validation.semanticScore, validation.structuralScore,
          validation.conservationError, validation.testAccuracy,
          JSON.stringify(validation.confidenceInterval), validation.validationMethod,
          validation.validationTime, validation.dataSize, validation.sampleSize,
          JSON.stringify(validation.metadata), validation.metadata.generatedAt,
          validation.metadata.generatedAt
        ]);
      }

      logger.info(`Seeded ${validations.length} validations in PostgreSQL`);

    } catch (error) {
      logger.error('PostgreSQL seeding failed:', error);
      throw error;
    }
  }

  async seedMongoDB() {
    if (!dbManager.isMongoConnected()) {
      logger.warn('MongoDB not connected, skipping MongoDB seeding');
      return;
    }

    logger.info('Seeding MongoDB database');

    try {
      // Clear existing data (optional, for development)
      await dbManager.getCollection('validations').deleteMany({});
      await dbManager.getCollection('correlations').deleteMany({});
      await dbManager.getCollection('datasets').deleteMany({});

      // Seed datasets
      const datasets = this.generateSampleDatasets();
      await dbManager.getCollection('datasets').insertMany(datasets);
      logger.info(`Seeded ${datasets.length} datasets in MongoDB`);

      // Seed correlations
      const correlations = this.generateSampleCorrelations(datasets);
      await dbManager.getCollection('correlations').insertMany(correlations);
      logger.info(`Seeded ${correlations.length} correlations in MongoDB`);

      // Seed validations
      const validations = this.generateSampleValidations(correlations);
      await dbManager.getCollection('validations').insertMany(validations);
      logger.info(`Seeded ${validations.length} validations in MongoDB`);

    } catch (error) {
      logger.error('MongoDB seeding failed:', error);
      throw error;
    }
  }

  async validateSeedData() {
    logger.info('Validating seed data');

    const datasets = this.generateSampleDatasets();
    const correlations = this.generateSampleCorrelations(datasets);
    const validations = this.generateSampleValidations(correlations);

    // Validate datasets
    const datasetValidation = ValidationUtils.validateBatch(
      ValidationUtils.schemas.dataset || ValidationUtils.validateDataset,
      datasets,
      'Dataset'
    );

    // Validate correlations
    const correlationValidation = ValidationUtils.validateBatch(
      ValidationUtils.schemas.correlation || ValidationUtils.validateCorrelation,
      correlations,
      'Correlation'
    );

    // Validate validations
    const validationValidation = ValidationUtils.validateBatch(
      ValidationUtils.schemas.validation || ValidationUtils.validateValidation,
      validations,
      'Validation'
    );

    const validationResults = {
      datasets: datasetValidation,
      correlations: correlationValidation,
      validations: validationValidation
    };

    logger.info('Seed data validation results', validationResults);

    if (validationResults.datasets.totalInvalid > 0 ||
        validationResults.correlations.totalInvalid > 0 ||
        validationResults.validations.totalInvalid > 0) {
      throw new Error('Seed data validation failed');
    }

    return validationResults;
  }

  async run(options = {}) {
    try {
      logger.info('Starting database seeding');

      if (options.validate !== false) {
        await this.validateSeedData();
      }

      await this.connect();

      if (options.postgres !== false) {
        await this.seedPostgres();
      }

      if (options.mongo !== false) {
        await this.seedMongoDB();
      }

      logger.info('Database seeding completed successfully');

    } catch (error) {
      logger.error('Database seeding failed:', error);
      throw error;
    } finally {
      await this.disconnect();
    }
  }
}

// Command line interface
async function main() {
  const args = process.argv.slice(2);
  const options = {};

  args.forEach(arg => {
    if (arg === '--no-validation') options.validate = false;
    if (arg === '--no-postgres') options.postgres = false;
    if (arg === '--no-mongo') options.mongo = false;
    if (arg === '--force') options.force = true;
  });

  const seeder = new DatabaseSeeder();

  try {
    await seeder.run(options);
    logger.info('Seeding completed successfully');
    process.exit(0);
  } catch (error) {
    logger.error('Seeding failed:', error);
    process.exit(1);
  }
}

// Export for programmatic use
module.exports = DatabaseSeeder;

// Run if called directly
if (require.main === module) {
  main();
}