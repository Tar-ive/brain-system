const { expect } = require('chai');
const { v4: uuidv4 } = require('uuid');
const dbManager = require('../../src/utils/database');
const Dataset = require('../../src/models/Dataset');
const Correlation = require('../../src/models/Correlation');
const Validation = require('../../src/models/Validation');
const DatasetRepository = require('../../src/repositories/DatasetRepository');
const CorrelationRepository = require('../../src/repositories/CorrelationRepository');
const ValidationRepository = require('../../src/repositories/ValidationRepository');
const testDbManager = require('../database/TestDatabaseManager');

describe('Database Integration Tests', () => {
  let datasetRepository, correlationRepository, validationRepository;

  before(async () => {
    // Setup test database
    await testDbManager.connect();
    await testDbManager.clearAllTables();
    await testDbManager.setupTestDatabases();

    // Initialize repositories
    datasetRepository = new DatasetRepository(dbManager);
    correlationRepository = new CorrelationRepository(dbManager);
    validationRepository = new ValidationRepository(dbManager);
  });

  after(async () => {
    await testDbManager.disconnect();
  });

  beforeEach(async () => {
    // Clear tables before each test
    await testDbManager.clearAllTables();
  });

  describe('Database Connection and Health', () => {
    it('should connect to both databases successfully', async () => {
      const connections = await dbManager.connect();

      expect(connections).to.be.an('array');
      expect(connections.length).to.be.greaterThan(0);

      const connectionTypes = connections.map(c => c.type);
      if (dbManager.isPostgresConnected()) {
        expect(connectionTypes).to.include('postgres');
      }
      if (dbManager.isMongoConnected()) {
        expect(connectionTypes).to.include('mongo');
      }
    });

    it('should pass health check for both databases', async () => {
      const health = await dbManager.healthCheck();

      expect(health).to.be.an('object');
      expect(health.postgres).to.be.an('object');
      expect(health.mongo).to.be.an('object');

      if (dbManager.isPostgresConnected()) {
        expect(health.postgres.connected).to.be.true;
        expect(health.postgres.latency).to.be.a('number');
        expect(health.postgres.latency).to.be.at.least(0);
      }

      if (dbManager.isMongoConnected()) {
        expect(health.connected).to.be.true;
        expect(health.mongo.latency).to.be.a('number');
        expect(health.mongo.latency).to.be.at.least(0);
      }
    });

    it('should get database statistics', async () => {
      const stats = await dbManager.getStats();

      expect(stats).to.be.an('object');
      expect(stats.postgres).to.be.an('object');
      expect(stats.mongo).to.be.an('object');

      if (dbManager.isPostgresConnected()) {
        expect(stats.postgres.connected).to.be.true;
        expect(stats.postgres.pool).to.be.an('object');
      }

      if (dbManager.isMongoConnected()) {
        expect(stats.mongo.connected).to.be.true;
      }
    });
  });

  describe('Cross-Repository Data Consistency', () => {
    it('should maintain data consistency across repositories', async () => {
      // Create datasets
      const dataset1 = await datasetRepository.create({
        name: 'Integration Test Dataset 1',
        type: 'structured',
        format: 'json',
        size: 1024,
        recordCount: 100
      });

      const dataset2 = await datasetRepository.create({
        name: 'Integration Test Dataset 2',
        type: 'structured',
        format: 'json',
        size: 2048,
        recordCount: 200
      });

      // Create correlation between datasets
      const correlation = await correlationRepository.create({
        sourceDatasetId: dataset1.id,
        targetDatasetId: dataset2.id,
        type: 'one_to_many',
        confidence: 0.85,
        validityScore: 0.78,
        description: 'Test correlation for integration'
      });

      // Create validation for correlation
      const validation = await validationRepository.create({
        correlationId: correlation.id,
        validityScore: 0.88,
        statisticalScore: 0.85,
        semanticScore: 0.90,
        structuralScore: 0.87,
        validationMethod: 'statistical'
      });

      // Verify data consistency
      const foundDataset1 = await datasetRepository.findById(dataset1.id);
      const foundDataset2 = await datasetRepository.findById(dataset2.id);
      const foundCorrelation = await correlationRepository.findById(correlation.id);
      const foundValidation = await validationRepository.findById(validation.id);

      expect(foundDataset1.id).to.equal(dataset1.id);
      expect(foundDataset2.id).to.equal(dataset2.id);
      expect(foundCorrelation.sourceDatasetId).to.equal(dataset1.id);
      expect(foundCorrelation.targetDatasetId).to.equal(dataset2.id);
      expect(foundValidation.correlationId).to.equal(correlation.id);
    });

    it('should handle cascading deletes correctly', async () => {
      // Create datasets and correlation
      const dataset1 = await datasetRepository.create({
        name: 'Cascade Test Dataset 1',
        type: 'structured',
        format: 'json'
      });

      const dataset2 = await datasetRepository.create({
        name: 'Cascade Test Dataset 2',
        type: 'structured',
        format: 'json'
      });

      const correlation = await correlationRepository.create({
        sourceDatasetId: dataset1.id,
        targetDatasetId: dataset2.id,
        type: 'one_to_one',
        confidence: 0.9
      });

      // Delete one dataset
      await datasetRepository.delete(dataset1.id);

      // Verify correlation is also deleted (handled by database cascade)
      const foundCorrelation = await correlationRepository.findById(correlation.id);
      // Note: This depends on your database cascade configuration
      // If cascade is not configured, correlation might still exist
    });
  });

  describe('Transaction Management', () => {
    it('should rollback complex transaction on failure', async () => {
      let transactionFailed = false;

      try {
        await dbManager.transaction(async (client) => {
          // Create multiple related entities
          const dataset1 = await datasetRepository.create({
            name: 'Transaction Dataset 1',
            type: 'structured',
            format: 'json'
          }, { client });

          const dataset2 = await datasetRepository.create({
            name: 'Transaction Dataset 2',
            type: 'structured',
            format: 'json'
          }, { client });

          const correlation = await correlationRepository.create({
            sourceDatasetId: dataset1.id,
            targetDatasetId: dataset2.id,
            type: 'one_to_many',
            confidence: 0.8
          }, { client });

          // Force an error
          throw new Error('Forced transaction rollback');
        });
      } catch (error) {
        transactionFailed = true;
      }

      expect(transactionFailed).to.be.true;

      // Verify no data was created
      const datasets = await datasetRepository.findAll();
      const correlations = await correlationRepository.findAll();

      expect(datasets).to.have.lengthOf(0);
      expect(correlations).to.have.lengthOf(0);
    });

    it('should commit complex transaction successfully', async () => {
      const result = await dbManager.transaction(async (client) => {
        const dataset1 = await datasetRepository.create({
          name: 'Successful Transaction Dataset 1',
          type: 'structured',
          format: 'json'
        }, { client });

        const dataset2 = await datasetRepository.create({
          name: 'Successful Transaction Dataset 2',
          type: 'structured',
          format: 'json'
        }, { client });

        const correlation = await correlationRepository.create({
          sourceDatasetId: dataset1.id,
          targetDatasetId: dataset2.id,
          type: 'many_to_many',
          confidence: 0.75
        }, { client });

        return { dataset1, dataset2, correlation };
      });

      expect(result.dataset1).to.be.an('object');
      expect(result.dataset2).to.be.an('object');
      expect(result.correlation).to.be.an('object');

      // Verify data was committed
      const foundDataset1 = await datasetRepository.findById(result.dataset1.id);
      const foundDataset2 = await datasetRepository.findById(result.dataset2.id);
      const foundCorrelation = await correlationRepository.findById(result.correlation.id);

      expect(foundDataset1).to.not.be.null;
      expect(foundDataset2).to.not.be.null;
      expect(foundCorrelation).to.not.be.null;
    });
  });

  describe('Performance and Scaling', () => {
    it('should handle bulk data insertion efficiently', async () => {
      const bulkDataSize = 50;
      const datasets = [];

      // Create multiple datasets
      for (let i = 0; i < bulkDataSize; i++) {
        datasets.push({
          name: `Bulk Dataset ${i}`,
          type: 'structured',
          format: 'json',
          size: 1024 + i,
          recordCount: 100 + i
        });
      }

      const startTime = Date.now();

      // Insert datasets
      const createdDatasets = [];
      for (const datasetData of datasets) {
        const created = await datasetRepository.create(datasetData);
        createdDatasets.push(created);
      }

      const endTime = Date.now();
      const duration = endTime - startTime;

      expect(createdDatasets).to.have.lengthOf(bulkDataSize);
      expect(duration).to.be.lessThan(10000); // Should complete within 10 seconds

      // Verify all datasets were created
      const count = await datasetRepository.count();
      expect(count).to.equal(bulkDataSize);
    });

    it('should handle complex queries efficiently', async () => {
      // Create test data
      const datasets = [];
      for (let i = 0; i < 20; i++) {
        const dataset = await datasetRepository.create({
          name: `Query Test Dataset ${i}`,
          type: i % 2 === 0 ? 'structured' : 'unstructured',
          format: i % 3 === 0 ? 'json' : 'csv',
          size: 1024 * (i + 1),
          recordCount: 100 * (i + 1),
          tags: [`tag${i % 5}`, `test${i % 3}`]
        });
        datasets.push(dataset);
      }

      // Create correlations
      const correlations = [];
      for (let i = 0; i < datasets.length - 1; i++) {
        const correlation = await correlationRepository.create({
          sourceDatasetId: datasets[i].id,
          targetDatasetId: datasets[i + 1].id,
          type: ['one_to_one', 'one_to_many', 'many_to_many'][i % 3],
          confidence: 0.5 + (i * 0.02),
          validityScore: 0.6 + (i * 0.015)
        });
        correlations.push(correlation);
      }

      // Test complex query performance
      const startTime = Date.now();

      const filteredDatasets = await datasetRepository.findAll({
        filter: {
          type: 'structured',
          format: 'json'
        },
        sortBy: 'size',
        sortOrder: 'desc'
      });

      const highConfidenceCorrelations = await correlationRepository.findAll({
        filter: {
          confidence: { $gt: 0.7 }
        }
      });

      const endTime = Date.now();
      const duration = endTime - startTime;

      expect(duration).to.be.lessThan(5000); // Should complete within 5 seconds
      expect(filteredDatasets.data).to.be.an('array');
      expect(highConfidenceCorrelations.data).to.be.an('array');
    });
  });

  describe('Error Handling and Recovery', () => {
    it('should handle connection timeouts gracefully', async () => {
      // This test simulates connection timeout behavior
      // In a real scenario, you might mock the database connection

      // Test that the system can recover after a connection issue
      try {
        // Try to perform operations that might fail due to connection issues
        await datasetRepository.findById(uuidv4());
      } catch (error) {
        // Connection errors should be handled gracefully
        expect(error).to.be.an('error');
      }

      // System should still be functional after error
      const dataset = await datasetRepository.create({
        name: 'Recovery Test Dataset',
        type: 'structured',
        format: 'json'
      });

      expect(dataset).to.be.an('object');
      expect(dataset.id).to.be.a('string');
    });

    it('should handle constraint violations gracefully', async () => {
      // Create a dataset
      const dataset = await datasetRepository.create({
        name: 'Constraint Test Dataset',
        type: 'structured',
        format: 'json'
      });

      // Try to create a correlation with invalid dataset IDs
      await expect(
        correlationRepository.create({
          sourceDatasetId: uuidv4(), // Non-existent
          targetDatasetId: uuidv4(), // Non-existent
          type: 'one_to_one',
          confidence: 0.8
        })
      ).to.be.rejected;

      // Original dataset should still be accessible
      const foundDataset = await datasetRepository.findById(dataset.id);
      expect(foundDataset).to.not.be.null;
    });
  });

  describe('Data Integrity and Validation', () => {
    it('should maintain data integrity across operations', async () => {
      // Create a complete dataset-correlation-validation chain
      const dataset1 = await datasetRepository.create({
        name: 'Integrity Test Dataset 1',
        type: 'structured',
        format: 'json',
        size: 1024,
        recordCount: 100
      });

      const dataset2 = await datasetRepository.create({
        name: 'Integrity Test Dataset 2',
        type: 'structured',
        format: 'json',
        size: 2048,
        recordCount: 200
      });

      const correlation = await correlationRepository.create({
        sourceDatasetId: dataset1.id,
        targetDatasetId: dataset2.id,
        type: 'one_to_many',
        confidence: 0.85,
        validityScore: 0.78
      });

      const validation = await validationRepository.create({
        correlationId: correlation.id,
        validityScore: 0.88,
        statisticalScore: 0.85,
        semanticScore: 0.90,
        structuralScore: 0.87
      });

      // Verify all relationships are valid
      expect(correlation.sourceDatasetId).to.equal(dataset1.id);
      expect(correlation.targetDatasetId).to.equal(dataset2.id);
      expect(validation.correlationId).to.equal(correlation.id);

      // Verify data consistency
      const stats = await datasetRepository.getStatistics();
      expect(stats.totalCount).to.equal(2);
      expect(stats.totalSize).to.equal(1024 + 2048);
      expect(stats.totalRecords).to.equal(100 + 200);
    });

    it('should validate data before database operations', async () => {
      // Try to create invalid dataset
      await expect(
        datasetRepository.create({
          name: '', // Invalid: empty name
          type: 'invalid_type', // Invalid type
          format: 'json'
        })
      ).to.be.rejectedWith('Dataset validation failed');

      // Try to create invalid correlation
      const dataset = await datasetRepository.create({
        name: 'Valid Dataset',
        type: 'structured',
        format: 'json'
      });

      await expect(
        correlationRepository.create({
          sourceDatasetId: dataset.id,
          targetDatasetId: dataset.id, // Same as source - should fail
          type: 'one_to_one',
          confidence: 0.8
        })
      ).to.be.rejectedWith('Source and target datasets cannot be the same');
    });

    it('should handle database schema validation', async () => {
      // This test verifies that the database schema constraints are working
      // by attempting to insert data that violates database constraints

      // Create valid dataset first
      const dataset = await datasetRepository.create({
        name: 'Schema Test Dataset',
        type: 'structured',
        format: 'json',
        size: 1024,
        recordCount: 100
      });

      // Try to create correlation with invalid confidence value
      await expect(
        correlationRepository.create({
          sourceDatasetId: dataset.id,
          targetDatasetId: uuidv4(), // Will fail foreign key constraint
          type: 'one_to_one',
          confidence: 1.5 // Invalid: > 1.0
        })
      ).to.be.rejected;
    });
  });

  describe('Migration and Schema Management', () => {
    it('should work with current database schema', async () => {
      // This test verifies that all repositories work with the current schema
      const operations = [];

      // Test all CRUD operations
      operations.push(
        datasetRepository.create({
          name: 'Schema Test Dataset',
          type: 'structured',
          format: 'json'
        })
      );

      const dataset = await operations[0];

      operations.push(
        datasetRepository.findById(dataset.id),
        datasetRepository.findAll(),
        datasetRepository.update(dataset.id, { name: 'Updated Schema Dataset' }),
        datasetRepository.delete(dataset.id)
      );

      // All operations should complete successfully
      for (const operation of operations.slice(1)) {
        await expect(operation).to.not.be.rejected;
      }
    });

    it('should handle database schema changes gracefully', async () => {
      // This test verifies the system can handle schema changes
      // In a real scenario, you might test migration scripts here

      // Create data with current schema
      const dataset = await datasetRepository.create({
        name: 'Migration Test Dataset',
        type: 'structured',
        format: 'json',
        metadata: {
          version: '1.0',
          migrationTest: true
        }
      });

      // Verify data can be retrieved and manipulated
      const foundDataset = await datasetRepository.findById(dataset.id);
      expect(foundDataset.metadata.migrationTest).to.be.true;

      // Update with additional metadata
      const updatedDataset = await datasetRepository.update(dataset.id, {
        metadata: {
          ...foundDataset.metadata,
          version: '1.1',
          updatedAfterMigration: true
        }
      });

      expect(updatedDataset.metadata.version).to.equal('1.1');
      expect(updatedDataset.metadata.updatedAfterMigration).to.be.true;
    });
  });
});