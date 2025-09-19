const { expect } = require('chai');
const { v4: uuidv4 } = require('uuid');
const dbManager = require('../../src/utils/database');
const DatasetRepository = require('../../src/repositories/DatasetRepository');
const CorrelationRepository = require('../../src/repositories/CorrelationRepository');
const testDbManager = require('../database/TestDatabaseManager');

describe('Database Performance Tests', () => {
  let datasetRepository, correlationRepository;

  before(async () => {
    await testDbManager.connect();
    await testDbManager.clearAllTables();
    await testDbManager.setupTestDatabases();

    datasetRepository = new DatasetRepository(dbManager);
    correlationRepository = new CorrelationRepository(dbManager);
  });

  after(async () => {
    await testDbManager.disconnect();
  });

  beforeEach(async () => {
    await testDbManager.clearAllTables();
  });

  describe('Read Performance', () => {
    it('should handle high-frequency read operations efficiently', async () => {
      // Create test data
      const datasets = [];
      for (let i = 0; i < 100; i++) {
        const dataset = await datasetRepository.create({
          name: `Performance Dataset ${i}`,
          type: 'structured',
          format: 'json',
          size: 1024 * (i + 1),
          recordCount: 100 * (i + 1)
        });
        datasets.push(dataset);
      }

      // Create correlations
      for (let i = 0; i < datasets.length - 1; i++) {
        await correlationRepository.create({
          sourceDatasetId: datasets[i].id,
          targetDatasetId: datasets[i + 1].id,
          type: 'one_to_many',
          confidence: 0.5 + (i * 0.005)
        });
      }

      // Performance test for read operations
      const readOperations = 100;
      const readTimes = [];

      for (let i = 0; i < readOperations; i++) {
        const startTime = Date.now();

        // Random read operations
        const randomDatasetId = datasets[Math.floor(Math.random() * datasets.length)].id;
        await datasetRepository.findById(randomDatasetId);

        const endTime = Date.now();
        readTimes.push(endTime - startTime);
      }

      const avgReadTime = readTimes.reduce((sum, time) => sum + time, 0) / readTimes.length;
      const maxReadTime = Math.max(...readTimes);

      console.log(`Average read time: ${avgReadTime.toFixed(2)}ms`);
      console.log(`Max read time: ${maxReadTime.toFixed(2)}ms`);

      // Performance assertions
      expect(avgReadTime).to.be.lessThan(100); // Average should be under 100ms
      expect(maxReadTime).to.be.lessThan(500); // Max should be under 500ms
    });

    it('should handle complex query performance', async () => {
      // Create diverse test data
      const testDatasets = [];
      const types = ['structured', 'semi-structured', 'unstructured'];
      const formats = ['json', 'csv', 'xml', 'parquet'];

      for (let i = 0; i < 200; i++) {
        const dataset = await datasetRepository.create({
          name: `Complex Query Dataset ${i}`,
          type: types[i % types.length],
          format: formats[i % formats.length],
          size: Math.floor(Math.random() * 10000) + 1000,
          recordCount: Math.floor(Math.random() * 10000) + 100,
          tags: [`tag${i % 10}`, `category${i % 5}`]
        });
        testDatasets.push(dataset);
      }

      // Test complex filter performance
      const complexFilters = [
        { type: 'structured', format: 'json' },
        { size: { $gt: 5000 } },
        { recordCount: { $lt: 1000 } },
        { tags: { $in: ['tag0', 'tag1'] } }
      ];

      const filterTimes = [];

      for (const filter of complexFilters) {
        const startTime = Date.now();
        await datasetRepository.findAll({ filter });
        const endTime = Date.now();
        filterTimes.push(endTime - startTime);
      }

      const avgFilterTime = filterTimes.reduce((sum, time) => sum + time, 0) / filterTimes.length;
      console.log(`Average complex filter time: ${avgFilterTime.toFixed(2)}ms`);

      expect(avgFilterTime).to.be.lessThan(200); // Complex filters under 200ms
    });

    it('should handle pagination performance efficiently', async () => {
      // Create large dataset
      const largeDataset = [];
      for (let i = 0; i < 1000; i++) {
        const dataset = await datasetRepository.create({
          name: `Pagination Test Dataset ${i}`,
          type: 'structured',
          format: 'json',
          size: 1024 + i,
          recordCount: 100 + i
        });
        largeDataset.push(dataset);
      }

      // Test pagination performance
      const pageSizes = [10, 50, 100, 200];
      const paginationTimes = [];

      for (const pageSize of pageSizes) {
        const startTime = Date.now();
        const result = await datasetRepository.findAll({
          page: 1,
          limit: pageSize
        });
        const endTime = Date.now();

        expect(result.data).to.have.lengthOf(pageSize);
        expect(result.pagination).to.be.an('object');

        paginationTimes.push(endTime - startTime);
      }

      const avgPaginationTime = paginationTimes.reduce((sum, time) => sum + time, 0) / paginationTimes.length;
      console.log(`Average pagination time: ${avgPaginationTime.toFixed(2)}ms`);

      expect(avgPaginationTime).to.be.lessThan(150); // Pagination under 150ms
    });
  });

  describe('Write Performance', () => {
    it('should handle bulk insert operations efficiently', async () => {
      const bulkSizes = [10, 50, 100, 200];
      const bulkInsertTimes = [];

      for (const bulkSize of bulkSizes) {
        const startTime = Date.now();

        const datasets = [];
        for (let i = 0; i < bulkSize; i++) {
          const dataset = await datasetRepository.create({
            name: `Bulk Insert Dataset ${bulkSize}-${i}`,
            type: 'structured',
            format: 'json',
            size: 1024 + i,
            recordCount: 100 + i
          });
          datasets.push(dataset);
        }

        const endTime = Date.now();
        bulkInsertTimes.push({
          bulkSize,
          time: endTime - startTime,
          avgTimePerRecord: (endTime - startTime) / bulkSize
        });

        // Verify all records were inserted
        const count = await datasetRepository.count();
        expect(count).to.equal(datasets.reduce((sum, _, index) => sum + (index + 1), 0));

        // Clear for next test
        await testDbManager.clearAllTables();
      }

      console.log('Bulk insert performance:');
      bulkInsertTimes.forEach(({ bulkSize, time, avgTimePerRecord }) => {
        console.log(`  ${bulkSize} records: ${time}ms total, ${avgTimePerRecord.toFixed(2)}ms per record`);
      });

      // Performance assertions
      bulkInsertTimes.forEach(({ avgTimePerRecord }) => {
        expect(avgTimePerRecord).to.be.lessThan(50); // Less than 50ms per record
      });
    });

    it('should handle concurrent write operations', async () => {
      const concurrentWrites = 20;
      const writePromises = [];
      const writeStartTimes = [];
      const writeEndTimes = [];

      // Create concurrent write operations
      for (let i = 0; i < concurrentWrites; i++) {
        writeStartTimes.push(Date.now());

        const promise = datasetRepository.create({
          name: `Concurrent Write Dataset ${i}`,
          type: 'structured',
          format: 'json',
          size: 1024 + i,
          recordCount: 100 + i
        }).then(result => {
          writeEndTimes.push(Date.now());
          return result;
        });

        writePromises.push(promise);
      }

      // Wait for all writes to complete
      const results = await Promise.all(writePromises);

      // Verify all writes succeeded
      expect(results).to.have.lengthOf(concurrentWrites);
      results.forEach(result => {
        expect(result.id).to.be.a('string');
      });

      // Calculate performance metrics
      const writeTimes = writeEndTimes.map((endTime, index) => endTime - writeStartTimes[index]);
      const avgWriteTime = writeTimes.reduce((sum, time) => sum + time, 0) / writeTimes.length;
      const maxWriteTime = Math.max(...writeTimes);

      console.log(`Average concurrent write time: ${avgWriteTime.toFixed(2)}ms`);
      console.log(`Max concurrent write time: ${maxWriteTime.toFixed(2)}ms`);

      // Performance assertions
      expect(avgWriteTime).to.be.lessThan(200); // Average under 200ms
      expect(maxWriteTime).to.be.lessThan(1000); // Max under 1s
    });

    it('should handle update operations efficiently', async () => {
      // Create test data
      const datasets = [];
      for (let i = 0; i < 100; i++) {
        const dataset = await datasetRepository.create({
          name: `Update Test Dataset ${i}`,
          type: 'structured',
          format: 'json',
          size: 1024,
          recordCount: 100
        });
        datasets.push(dataset);
      }

      // Test update performance
      const updateOperations = 50;
      const updateTimes = [];

      for (let i = 0; i < updateOperations; i++) {
        const randomDataset = datasets[Math.floor(Math.random() * datasets.length)];
        const startTime = Date.now();

        await datasetRepository.update(randomDataset.id, {
          name: `Updated Dataset ${i}`,
          size: 2048 + i,
          recordCount: 200 + i
        });

        const endTime = Date.now();
        updateTimes.push(endTime - startTime);
      }

      const avgUpdateTime = updateTimes.reduce((sum, time) => sum + time, 0) / updateTimes.length;
      console.log(`Average update time: ${avgUpdateTime.toFixed(2)}ms`);

      expect(avgUpdateTime).to.be.lessThan(100); // Updates under 100ms
    });
  });

  describe('Memory Usage', () => {
    it('should manage memory efficiently during large operations', async () => {
      // This test monitors memory usage during large operations
      const initialMemory = process.memoryUsage();

      // Create large dataset
      const largeDataset = [];
      for (let i = 0; i < 500; i++) {
        const dataset = await datasetRepository.create({
          name: `Memory Test Dataset ${i}`,
          type: 'structured',
          format: 'json',
          size: 1024 + i,
          recordCount: 100 + i,
          metadata: {
            description: `This is a test dataset for memory testing with index ${i}`,
            tags: Array.from({ length: 10 }, (_, j) => `tag${j}`),
            nested: {
              level1: {
                level2: {
                  data: `nested data ${i}`
                }
              }
            }
          }
        });
        largeDataset.push(dataset);

        // Check memory every 100 operations
        if (i % 100 === 0) {
          const currentMemory = process.memoryUsage();
          const memoryIncrease = currentMemory.heapUsed - initialMemory.heapUsed;
          console.log(`Memory increase after ${i} operations: ${memoryIncrease / 1024 / 1024}MB`);
        }
      }

      const finalMemory = process.memoryUsage();
      const totalMemoryIncrease = finalMemory.heapUsed - initialMemory.heapUsed;

      console.log(`Total memory increase: ${totalMemoryIncrease / 1024 / 1024}MB`);

      // Memory should not increase excessively
      expect(totalMemoryIncrease).to.be.lessThan(100 * 1024 * 1024); // Less than 100MB increase
    });
  });

  describe('Connection Pool Performance', () => {
    it('should handle connection pool efficiently under load', async () => {
      const concurrentOperations = 30;
      const operationPromises = [];
      const operationTimes = [];

      // Create concurrent database operations
      for (let i = 0; i < concurrentOperations; i++) {
        const startTime = Date.now();

        const promise = (async () => {
          // Mix of read and write operations
          if (i % 2 === 0) {
            // Read operation
            await datasetRepository.findAll({ limit: 10 });
          } else {
            // Write operation
            await datasetRepository.create({
              name: `Pool Test Dataset ${i}`,
              type: 'structured',
              format: 'json',
              size: 1024 + i,
              recordCount: 100 + i
            });
          }
        })().then(() => {
          const endTime = Date.now();
          operationTimes.push(endTime - startTime);
        });

        operationPromises.push(promise);
      }

      // Wait for all operations to complete
      await Promise.all(operationPromises);

      const avgOperationTime = operationTimes.reduce((sum, time) => sum + time, 0) / operationTimes.length;
      const maxOperationTime = Math.max(...operationTimes);

      console.log(`Average pool operation time: ${avgOperationTime.toFixed(2)}ms`);
      console.log(`Max pool operation time: ${maxOperationTime.toFixed(2)}ms`);

      // Performance assertions
      expect(avgOperationTime).to.be.lessThan(300); // Average under 300ms
      expect(maxOperationTime).to.be.lessThan(2000); // Max under 2s
    });
  });

  describe('Query Optimization', () => {
    it('should benefit from database indexing', async () => {
      // Create test data with searchable fields
      const searchableDatasets = [];
      for (let i = 0; i < 1000; i++) {
        const dataset = await datasetRepository.create({
          name: `Indexed Dataset ${i}`,
          type: ['structured', 'unstructured'][i % 2],
          format: ['json', 'csv'][i % 2],
          size: 1024 * (i + 1),
          recordCount: 100 * (i + 1),
          tags: [`search_tag${i % 20}`, `category${i % 5}`]
        });
        searchableDatasets.push(dataset);
      }

      // Test indexed field queries
      const indexedQueries = [
        () => datasetRepository.findById(searchableDatasets[500].id),
        () => datasetRepository.findByTag('search_tag0'),
        () => datasetRepository.findByType('structured'),
        () => datasetRepository.findByFormat('json'),
        () => datasetRepository.search('Indexed Dataset')
      ];

      const queryTimes = [];

      for (const query of indexedQueries) {
        const startTime = Date.now();
        await query();
        const endTime = Date.now();
        queryTimes.push(endTime - startTime);
      }

      const avgQueryTime = queryTimes.reduce((sum, time) => sum + time, 0) / queryTimes.length;
      console.log(`Average indexed query time: ${avgQueryTime.toFixed(2)}ms`);

      expect(avgQueryTime).to.be.lessThan(50); // Indexed queries under 50ms
    });

    it('should handle complex join operations efficiently', async () => {
      // Create datasets and correlations for join testing
      const datasets = [];
      for (let i = 0; i < 100; i++) {
        const dataset = await datasetRepository.create({
          name: `Join Test Dataset ${i}`,
          type: 'structured',
          format: 'json',
          size: 1024 + i,
          recordCount: 100 + i
        });
        datasets.push(dataset);
      }

      // Create correlations between datasets
      for (let i = 0; i < datasets.length - 1; i++) {
        await correlationRepository.create({
          sourceDatasetId: datasets[i].id,
          targetDatasetId: datasets[i + 1].id,
          type: 'one_to_many',
          confidence: 0.5 + (i * 0.005)
        });
      }

      // Test complex join-like operations
      const startTime = Date.now();

      // Get all datasets with their correlations
      const allDatasets = await datasetRepository.findAll();
      const datasetCorrelations = [];

      for (const dataset of allDatasets.data) {
        const correlations = await correlationRepository.findAll({
          filter: {
            $or: [
              { sourceDatasetId: dataset.id },
              { targetDatasetId: dataset.id }
            ]
          }
        });
        datasetCorrelations.push({
          dataset,
          correlations: correlations.data
        });
      }

      const endTime = Date.now();
      const joinTime = endTime - startTime;

      console.log(`Complex join operation time: ${joinTime}ms`);
      console.log(`Processed ${datasetCorrelations.length} datasets`);

      expect(joinTime).to.be.lessThan(5000); // Join operations under 5s
      expect(datasetCorrelations.length).to.equal(datasets.length);
    });
  });

  describe('Scalability Tests', () => {
    it('should scale linearly with data volume', async () => {
      const testSizes = [100, 500, 1000];
      const scalabilityResults = [];

      for (const size of testSizes) {
        // Clear and create fresh data
        await testDbManager.clearAllTables();

        const createStartTime = Date.now();

        // Create datasets
        const datasets = [];
        for (let i = 0; i < size; i++) {
          const dataset = await datasetRepository.create({
            name: `Scalability Test Dataset ${i}`,
            type: 'structured',
            format: 'json',
            size: 1024 + i,
            recordCount: 100 + i
          });
          datasets.push(dataset);
        }

        const createEndTime = Date.now();
        const createTime = createEndTime - createStartTime;

        // Test query performance
        const queryStartTime = Date.now();
        await datasetRepository.findAll({ limit: 50 });
        const queryEndTime = Date.now();
        const queryTime = queryEndTime - queryStartTime;

        scalabilityResults.push({
          size,
          createTime,
          queryTime,
          createPerRecord: createTime / size
        });

        console.log(`Size ${size}: Create ${createTime}ms, Query ${queryTime}ms`);
      }

      // Verify linear scalability (time should not grow exponentially)
      const sizeRatio = testSizes[2] / testSizes[0]; // 1000/100 = 10
      const timeRatio = scalabilityResults[2].createTime / scalabilityResults[0].createTime;

      console.log(`Size ratio: ${sizeRatio}x, Time ratio: ${timeRatio.toFixed(2)}x`);

      // Time should scale linearly, not exponentially
      expect(timeRatio).to.be.lessThan(sizeRatio * 2); // Within 2x linear
    });
  });
});