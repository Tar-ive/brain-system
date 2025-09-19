const { expect } = require('chai');
const { v4: uuidv4 } = require('uuid');
const Dataset = require('../../src/models/Dataset');
const DatasetRepository = require('../../src/repositories/DatasetRepository');
const dbManager = require('../../src/utils/database');
const testDbManager = require('../database/TestDatabaseManager');

describe('DatasetRepository', () => {
  let repository;
  let testData = [];

  before(async () => {
    // Setup test database
    await testDbManager.connect();
    await testDbManager.clearAllTables();
    await testDbManager.setupTestDatabases();

    // Create test data
    testData = testDbManager.generateTestDatasets();
  });

  after(async () => {
    await testDbManager.disconnect();
  });

  beforeEach(async () => {
    // Clear tables and seed fresh data
    await testDbManager.clearAllTables();
    await testDbManager.seedTestData({ datasets: testData });

    // Create repository instance
    repository = new DatasetRepository(dbManager);
  });

  describe('Constructor', () => {
    it('should create repository with database manager', () => {
      expect(repository).to.be.an('object');
      expect(repository.db).to.equal(dbManager);
      expect(repository.tableName).to.equal('datasets');
      expect(repository.model).to.equal(Dataset);
    });

    it('should throw error without database manager', () => {
      expect(() => new DatasetRepository()).to.throw('Database manager is required');
    });
  });

  describe('Create Operations', () => {
    it('should create a new dataset', async () => {
      const newDatasetData = {
        name: 'New Test Dataset',
        description: 'A newly created test dataset',
        type: 'structured',
        source: 'test',
        format: 'json',
        size: 2048,
        recordCount: 200,
        schema: {
          fields: [
            { name: 'id', type: 'string' },
            { name: 'name', type: 'string' }
          ]
        },
        tags: ['new', 'test']
      };

      const createdDataset = await repository.create(newDatasetData);

      expect(createdDataset).to.be.an('object');
      expect(createdDataset.name).to.equal('New Test Dataset');
      expect(createdDataset.type).to.equal('structured');
      expect(createdDataset.format).to.equal('json');
      expect(createdDataset.id).to.be.a('string');
      expect(createdDataset.createdAt).to.be.a('string');
    });

    it('should validate data before creation', async () => {
      const invalidData = {
        name: '', // Invalid: empty name
        type: 'invalid_type' // Invalid type
      };

      await expect(repository.create(invalidData)).to.be.rejectedWith('Dataset validation failed');
    });

    it('should generate ID if not provided', async () => {
      const datasetData = {
        name: 'Auto ID Dataset',
        type: 'structured',
        format: 'json'
      };

      const createdDataset = await repository.create(datasetData);

      expect(createdDataset.id).to.be.a('string');
      expect(createdDataset.id).to.match(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    });
  });

  describe('Read Operations', () => {
    it('should find dataset by ID', async () => {
      const testDataset = testData[0];
      const foundDataset = await repository.findById(testDataset.id);

      expect(foundDataset).to.be.an('object');
      expect(foundDataset.id).to.equal(testDataset.id);
      expect(foundDataset.name).to.equal(testDataset.name);
      expect(foundDataset.type).to.equal(testDataset.type);
    });

    it('should return null for non-existent ID', async () => {
      const nonExistentId = uuidv4();
      const foundDataset = await repository.findById(nonExistentId);

      expect(foundDataset).to.be.null;
    });

    it('should find all datasets', async () => {
      const allDatasets = await repository.findAll();

      expect(allDatasets).to.be.an('array');
      expect(allDatasets).to.have.lengthOf(testData.length);

      // Check that all test datasets are present
      const datasetNames = allDatasets.map(d => d.name);
      testData.forEach(dataset => {
        expect(datasetNames).to.include(dataset.name);
      });
    });

    it('should find datasets with pagination', async () => {
      const page = 1;
      const limit = 2;
      const result = await repository.findAll({ page, limit });

      expect(result).to.be.an('object');
      expect(result.data).to.be.an('array');
      expect(result.data).to.have.lengthOf.at.most(limit);
      expect(result.pagination).to.be.an('object');
      expect(result.pagination.page).to.equal(page);
      expect(result.pagination.limit).to.equal(limit);
      expect(result.pagination.total).to.equal(testData.length);
      expect(result.pagination.totalPages).to.equal(Math.ceil(testData.length / limit));
    });

    it('should find datasets with filters', async () => {
      const filter = { type: 'structured' };
      const filteredDatasets = await repository.findAll({ filter });

      expect(filteredDatasets).to.be.an('array');
      filteredDatasets.forEach(dataset => {
        expect(dataset.type).to.equal('structured');
      });
    });

    it('should find datasets by tags', async () => {
      // Add a dataset with specific tag
      const taggedDataset = await repository.create({
        name: 'Tagged Dataset',
        type: 'structured',
        format: 'json',
        tags: ['special', 'unique']
      });

      const foundDatasets = await repository.findByTag('special');

      expect(foundDatasets).to.be.an('array');
      expect(foundDatasets.some(d => d.id === taggedDataset.id)).to.be.true;
    });

    it('should return empty array for non-existent tag', async () => {
      const foundDatasets = await repository.findByTag('nonexistent-tag');

      expect(foundDatasets).to.be.an('array');
      expect(foundDatasets).to.have.lengthOf(0);
    });

    it('should search datasets by name', async () => {
      const searchTerm = 'Test Dataset 1';
      const searchResults = await repository.search(searchTerm);

      expect(searchResults).to.be.an('array');
      expect(searchResults.some(d => d.name.includes('Test Dataset 1'))).to.be.true;
    });

    it('should search datasets by description', async () => {
      const searchTerm = 'test dataset';
      const searchResults = await repository.search(searchTerm);

      expect(searchResults).to.be.an('array');
      expect(searchResults.length).to.be.greaterThan(0);
    });

    it('should return empty array for no search results', async () => {
      const searchTerm = 'nonexistent dataset name xyz123';
      const searchResults = await repository.search(searchTerm);

      expect(searchResults).to.be.an('array');
      expect(searchResults).to.have.lengthOf(0);
    });
  });

  describe('Update Operations', () => {
    it('should update a dataset', async () => {
      const testDataset = testData[0];
      const updateData = {
        name: 'Updated Dataset Name',
        description: 'Updated description',
        size: 3000
      };

      const updatedDataset = await repository.update(testDataset.id, updateData);

      expect(updatedDataset).to.be.an('object');
      expect(updatedDataset.id).to.equal(testDataset.id);
      expect(updatedDataset.name).to.equal('Updated Dataset Name');
      expect(updatedDataset.description).to.equal('Updated description');
      expect(updatedDataset.size).to.equal(3000);
      expect(updatedDataset.updatedAt).to.not.equal(testDataset.updatedAt);
    });

    it('should add tags to dataset', async () => {
      const testDataset = testData[0];
      const tagsToAdd = ['new-tag-1', 'new-tag-2'];

      const updatedDataset = await repository.addTags(testDataset.id, tagsToAdd);

      expect(updatedDataset.tags).to.include.members(tagsToAdd);
      expect(updatedDataset.updatedAt).to.not.equal(testDataset.updatedAt);
    });

    it('should remove tags from dataset', async () => {
      const testDataset = testData[0];
      const originalTags = [...testDataset.tags];
      const tagToRemove = originalTags[0];

      const updatedDataset = await repository.removeTags(testDataset.id, [tagToRemove]);

      expect(updatedDataset.tags).to.not.include(tagToRemove);
      expect(updatedDataset.updatedAt).to.not.equal(testDataset.updatedAt);
    });

    it('should track dataset access', async () => {
      const testDataset = testData[0];
      const originalLastAccessed = testDataset.lastAccessed;

      await new Promise(resolve => setTimeout(resolve, 10)); // Small delay

      const updatedDataset = await repository.trackAccess(testDataset.id);

      expect(updatedDataset.lastAccessed).to.not.equal(originalLastAccessed);
      expect(updatedDataset.updatedAt).to.not.equal(testDataset.updatedAt);
    });

    it('should update dataset stats', async () => {
      const testDataset = testData[0];
      const stats = {
        size: 5000,
        recordCount: 500
      };

      const updatedDataset = await repository.updateStats(testDataset.id, stats);

      expect(updatedDataset.size).to.equal(5000);
      expect(updatedDataset.recordCount).to.equal(500);
      expect(updatedDataset.updatedAt).to.not.equal(testDataset.updatedAt);
    });

    it('should throw error for non-existent dataset update', async () => {
      const nonExistentId = uuidv4();
      const updateData = { name: 'Updated Name' };

      await expect(repository.update(nonExistentId, updateData)).to.be.rejectedWith('Dataset not found');
    });
  });

  describe('Delete Operations', () => {
    it('should delete a dataset', async () => {
      const testDataset = testData[0];
      const deleted = await repository.delete(testDataset.id);

      expect(deleted).to.be.true;

      // Verify dataset is deleted
      const foundDataset = await repository.findById(testDataset.id);
      expect(foundDataset).to.be.null;
    });

    it('should return false for non-existent dataset deletion', async () => {
      const nonExistentId = uuidv4();
      const deleted = await repository.delete(nonExistentId);

      expect(deleted).to.be.false;
    });
  });

  describe('Count Operations', () => {
    it('should count all datasets', async () => {
      const count = await repository.count();

      expect(count).to.be.a('number');
      expect(count).to.equal(testData.length);
    });

    it('should count datasets with filters', async () => {
      const filter = { type: 'structured' };
      const count = await repository.count(filter);

      const structuredDatasets = testData.filter(d => d.type === 'structured');
      expect(count).to.equal(structuredDatasets.length);
    });

    it('should count datasets by type', async () => {
      const counts = await repository.countByType();

      expect(counts).to.be.an('object');
      expect(counts.structured).to.be.a('number');
      expect(counts.unstructured).to.be.a('number');

      // Verify counts match test data
      const structuredCount = testData.filter(d => d.type === 'structured').length;
      const unstructuredCount = testData.filter(d => d.type === 'unstructured').length;

      expect(counts.structured).to.equal(structuredCount);
      expect(counts.unstructured).to.equal(unstructuredCount);
    });

    it('should count datasets by format', async () => {
      const counts = await repository.countByFormat();

      expect(counts).to.be.an('object');
      expect(counts.json).to.be.a('number');
      expect(counts.csv).to.be.a('number');

      // Verify counts match test data
      const jsonCount = testData.filter(d => d.format === 'json').length;
      const csvCount = testData.filter(d => d.format === 'csv').length;

      expect(counts.json).to.equal(jsonCount);
      expect(counts.csv).to.equal(csvCount);
    });
  });

  describe('Statistics Operations', () => {
    it('should get dataset statistics', async () => {
      const stats = await repository.getStatistics();

      expect(stats).to.be.an('object');
      expect(stats.totalCount).to.be.a('number');
      expect(stats.totalSize).to.be.a('number');
      expect(stats.totalRecords).to.be.a('number');
      expect(stats.averageSize).to.be.a('number');
      expect(stats.averageRecordCount).to.be.a('number');
      expect(stats.byType).to.be.an('object');
      expect(stats.byFormat).to.be.an('object');
    });

    it('should calculate correct statistics from test data', async () => {
      const stats = await repository.getStatistics();

      expect(stats.totalCount).to.equal(testData.length);

      const totalSize = testData.reduce((sum, d) => sum + d.size, 0);
      expect(stats.totalSize).to.equal(totalSize);

      const totalRecords = testData.reduce((sum, d) => sum + d.recordCount, 0);
      expect(stats.totalRecords).to.equal(totalRecords);

      expect(stats.averageSize).to.equal(totalSize / testData.length);
      expect(stats.averageRecordCount).to.equal(totalRecords / testData.length);
    });
  });

  describe('Error Handling', () => {
    it('should handle database connection errors gracefully', async () => {
      // Simulate database connection error
      const originalQuery = dbManager.query;
      dbManager.query = () => { throw new Error('Connection failed'); };

      await expect(repository.findById(testData[0].id)).to.be.rejectedWith('Connection failed');

      // Restore original method
      dbManager.query = originalQuery;
    });

    it('should handle invalid UUID format', async () => {
      await expect(repository.findById('invalid-uuid')).to.be.rejected;
    });

    it('should handle empty update data', async () => {
      const testDataset = testData[0];
      const updatedDataset = await repository.update(testDataset.id, {});

      expect(updatedDataset).to.be.an('object');
      expect(updatedDataset.id).to.equal(testDataset.id);
      // updatedAt should not change if no actual update
    });
  });

  describe('Transaction Support', () => {
    it('should create and update within transaction', async () => {
      const transactionResult = await dbManager.transaction(async (client) => {
        // Create dataset within transaction
        const newDatasetData = {
          name: 'Transaction Test Dataset',
          type: 'structured',
          format: 'json'
        };

        const created = await repository.create(newDatasetData, { client });

        // Update dataset within transaction
        const updated = await repository.update(created.id, {
          name: 'Updated Transaction Dataset'
        }, { client });

        return { created, updated };
      });

      expect(transactionResult.created).to.be.an('object');
      expect(transactionResult.updated).to.be.an('object');
      expect(transactionResult.updated.name).to.equal('Updated Transaction Dataset');
    });

    it('should rollback transaction on error', async () => {
      let transactionFailed = false;

      try {
        await dbManager.transaction(async (client) => {
          // Create dataset
          const newDatasetData = {
            name: 'Rollback Test Dataset',
            type: 'structured',
            format: 'json'
          };

          const created = await repository.create(newDatasetData, { client });

          // Force an error
          throw new Error('Forced error for rollback test');
        });
      } catch (error) {
        transactionFailed = true;
      }

      expect(transactionFailed).to.be.true;

      // Verify dataset was not created
      const foundDataset = await repository.findByName('Rollback Test Dataset');
      expect(foundDataset).to.be.null;
    });
  });

  describe('Additional Utility Methods', () => {
    it('should find dataset by name', async () => {
      const testDataset = testData[0];
      const foundDataset = await repository.findByName(testDataset.name);

      expect(foundDataset).to.be.an('object');
      expect(foundDataset.id).to.equal(testDataset.id);
      expect(foundDataset.name).to.equal(testDataset.name);
    });

    it('should return null for non-existent name', async () => {
      const foundDataset = await repository.findByName('Non-existent Dataset Name');

      expect(foundDataset).to.be.null;
    });

    it('should find datasets by visibility', async () => {
      // Create datasets with different visibility
      await repository.create({
        name: 'Public Dataset',
        type: 'structured',
        format: 'json',
        visibility: 'public'
      });

      await repository.create({
        name: 'Private Dataset',
        type: 'structured',
        format: 'json',
        visibility: 'private'
      });

      const publicDatasets = await repository.findByVisibility('public');
      const privateDatasets = await repository.findByVisibility('private');

      expect(publicDatasets).to.be.an('array');
      expect(privateDatasets).to.be.an('array');

      expect(publicDatasets.some(d => d.name === 'Public Dataset')).to.be.true;
      expect(privateDatasets.some(d => d.name === 'Private Dataset')).to.be.true;
    });

    it('should get dataset size distribution', async () => {
      const distribution = await repository.getSizeDistribution();

      expect(distribution).to.be.an('object');
      expect(distribution.small).to.be.a('number');
      expect(distribution.medium).to.be.a('number');
      expect(distribution.large).to.be.a('number');
      expect(distribution.total).to.be.a('number');
    });
  });
});