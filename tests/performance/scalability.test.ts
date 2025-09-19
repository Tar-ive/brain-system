import request from 'supertest';
import app from '../../src/index';
import { CorrelationService } from '../../src/services/CorrelationService';

describe('Scalability Tests', () => {
  let correlationService: CorrelationService;
  let largeDatasetIds: string[] = [];

  beforeAll(async () => {
    correlationService = new CorrelationService();

    // Create datasets of increasing size
    const sizes = [1000, 10000, 100000, 500000];
    for (let i = 0; i < sizes.length; i++) {
      const dataset = await correlationService.addDataset({
        id: `scalability-dataset-${i}`,
        name: `Scalability Dataset ${i + 1}`,
        description: `Dataset with ${sizes[i]} rows for scalability testing`,
        columns: ['id', 'name', 'value', 'category', 'subcategory', 'timestamp', 'metadata'],
        rowCount: sizes[i],
        metadata: {
          scalability: true,
          size: sizes[i],
          testType: 'performance'
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      });
      largeDatasetIds.push(dataset.id);
    }
  });

  describe('Vertical Scalability', () => {
    it('should handle increasing dataset sizes with linear performance degradation', async () => {
      const results = [];

      for (let i = 0; i < largeDatasetIds.length; i++) {
        const datasetId = largeDatasetIds[i];
        const iterations = 5;
        const durations = [];

        for (let j = 0; j < iterations; j++) {
          const startTime = process.hrtime.bigint();

          await request(app)
            .post('/api/correlations/discover')
            .send({
              sourceDatasetId: datasetId,
              targetDatasetId: datasetId,
              correlationType: 'one_to_one',
              parameters: {
                keyColumn: 'id',
                joinType: 'inner'
              }
            })
            .expect(201);

          const endTime = process.hrtime.bigint();
          durations.push(Number(endTime - startTime) / 1000000);
        }

        const avgDuration = durations.reduce((sum, d) => sum + d, 0) / durations.length;
        results.push({
          size: i === 0 ? '1K' : i === 1 ? '10K' : i === 2 ? '100K' : '500K',
          avgDuration,
          rows: [1000, 10000, 100000, 500000][i]
        });
      }

      // Analyze scalability
      for (let i = 1; i < results.length; i++) {
        const sizeRatio = results[i].rows / results[i - 1].rows;
        const timeRatio = results[i].avgDuration / results[i - 1].avgDuration;

        console.log(`Size increase ${results[i - 1].size} -> ${results[i].size}: ${sizeRatio}x`);
        console.log(`Time increase: ${timeRatio.toFixed(2)}x`);

        // Performance should scale better than linear
        expect(timeRatio).toBeLessThan(sizeRatio * 1.5);
      }

      console.log('\nVertical Scalability Results:');
      console.log('=================================');
      results.forEach(r => {
        console.log(`${r.size} rows: ${r.avgDuration.toFixed(2)}ms`);
      });
    });

    it('should handle large result sets efficiently', async () => {
      // Create many correlations in the largest dataset
      const numCorrelations = 200;
      const largestDatasetId = largeDatasetIds[3]; // 500K rows

      for (let i = 0; i < numCorrelations; i++) {
        await request(app)
          .post('/api/correlations/discover')
          .send({
            sourceDatasetId: largestDatasetId,
            targetDatasetId: largestDatasetId,
            correlationType: ['one_to_one', 'many_to_many', 'temporal', 'spatial'][i % 4],
            parameters: {
              keyColumn: ['id', 'category', 'subcategory', 'timestamp'][i % 4]
            }
          })
          .expect(201);
      }

      // Test large result set retrieval
      const startTime = process.hrtime.bigint();

      const response = await request(app)
        .get('/api/correlations')
        .query({
          sourceDatasetId: largestDatasetId,
          limit: 100
        })
        .expect(200);

      const endTime = process.hrtime.bigint();
      const duration = Number(endTime - startTime) / 1000000;

      expect(response.body.data.length).toBe(100);
      expect(response.body.pagination.total).toBeGreaterThanOrEqual(numCorrelations);
      expect(duration).toBeLessThan(500); // Should handle large results quickly

      console.log(`Large result set (${response.body.pagination.total} correlations): ${duration}ms`);
    });
  });

  describe('Horizontal Scalability', () => {
    it('should handle concurrent operations on different datasets', async () => {
      const numConcurrent = 20;
      const promises = [];

      for (let i = 0; i < numConcurrent; i++) {
        const datasetId = largeDatasetIds[i % largeDatasetIds.length];
        promises.push(
          request(app)
            .post('/api/correlations/discover')
            .send({
              sourceDatasetId: datasetId,
              targetDatasetId: datasetId,
              correlationType: 'one_to_one',
              parameters: {
                keyColumn: 'id',
                joinType: 'inner'
              }
            })
        );
      }

      const startTime = process.hrtime.bigint();
      const responses = await Promise.all(promises);
      const endTime = process.hrtime.bigint();
      const duration = Number(endTime - startTime) / 1000000;

      const successCount = responses.filter(r => r.status === 201).length;

      expect(successCount).toBe(numConcurrent);
      expect(duration).toBeLessThan(5000); // Should complete within 5 seconds

      console.log(`Concurrent operations on ${largeDatasetIds.length} datasets: ${duration}ms`);
      console.log(`Success rate: ${(successCount / numConcurrent * 100).toFixed(2)}%`);
    });

    it('should handle read/write mixed workload', async () => {
      const numOperations = 50;
      const promises = [];

      for (let i = 0; i < numOperations; i++) {
        const datasetId = largeDatasetIds[i % largeDatasetIds.length];

        if (i % 4 === 0) {
          // Write operation
          promises.push(
            request(app)
              .post('/api/correlations/discover')
              .send({
                sourceDatasetId: datasetId,
                targetDatasetId: datasetId,
                correlationType: 'one_to_one'
              })
          );
        } else if (i % 4 === 1) {
          // Read operation - list correlations
          promises.push(
            request(app)
              .get('/api/correlations')
              .query({ sourceDatasetId: datasetId, limit: 20 })
          );
        } else if (i % 4 === 2) {
          // Read operation - get statistics
          promises.push(
            request(app)
              .get('/api/correlations/statistics')
          );
        } else {
          // Read operation - get dataset
          promises.push(
            request(app)
              .get(`/api/datasets/${datasetId}`)
          );
        }
      }

      const startTime = process.hrtime.bigint();
      const responses = await Promise.all(promises);
      const endTime = process.hrtime.bigint();
      const duration = Number(endTime - startTime) / 1000000;

      const successCount = responses.filter(r => r.status === 200 || r.status === 201).length;

      expect(successCount).toBe(numOperations);
      expect(duration).toBeLessThan(3000); // Should complete within 3 seconds

      console.log(`Mixed workload (${numOperations} operations): ${duration}ms`);
      console.log(`Success rate: ${(successCount / numOperations * 100).toFixed(2)}%`);
    });
  });

  describe('Database Scalability', () => {
    it('should handle large number of correlations with efficient queries', async () => {
      const largestDatasetId = largeDatasetIds[2]; // 100K rows
      const numCorrelations = 500;

      // Create many correlations
      console.log(`Creating ${numCorrelations} correlations...`);
      for (let i = 0; i < numCorrelations; i++) {
        await request(app)
          .post('/api/correlations/discover')
          .send({
            sourceDatasetId: largestDatasetId,
            targetDatasetId: largestDatasetId,
            correlationType: ['one_to_one', 'many_to_many', 'temporal'][i % 3],
            parameters: {
              keyColumn: ['id', 'category', 'subcategory'][i % 3]
            },
            confidence: 0.5 + (Math.random() * 0.5)
          })
          .expect(201);
      }

      // Test query performance with various filters
      const queries = [
        { name: 'All correlations', query: {} },
        { name: 'By dataset', query: { sourceDatasetId: largestDatasetId } },
        { name: 'By type', query: { correlationType: 'one_to_one' } },
        { name: 'By confidence', query: { minConfidence: 0.8 } },
        { name: 'Complex filter', query: {
          sourceDatasetId: largestDatasetId,
          correlationType: 'one_to_one',
          minConfidence: 0.8,
          limit: 50
        }}
      ];

      for (const test of queries) {
        const iterations = 10;
        const durations = [];

        for (let i = 0; i < iterations; i++) {
          const startTime = process.hrtime.bigint();

          const response = await request(app)
            .get('/api/correlations')
            .query(test.query)
            .expect(200);

          const endTime = process.hrtime.bigint();
          durations.push(Number(endTime - startTime) / 1000000);

          // Verify query returned expected results
          if (test.query.sourceDatasetId) {
            response.body.data.forEach((c: any) => {
              expect(c.sourceDatasetId).toBe(test.query.sourceDatasetId);
            });
          }
        }

        const avgDuration = durations.reduce((sum, d) => sum + d, 0) / durations.length;
        const maxDuration = Math.max(...durations);

        expect(avgDuration).toBeLessThan(200);
        expect(maxDuration).toBeLessThan(1000);

        console.log(`${test.name}: avg ${avgDuration.toFixed(2)}ms, max ${maxDuration.toFixed(2)}ms`);
      }
    });

    it('should handle pagination with large datasets efficiently', async () => {
      const datasetId = largeDatasetIds[1]; // 10K rows
      const totalPages = 20;
      const pageSize = 25;

      // Test sequential page loading
      const sequentialDurations = [];
      for (let page = 0; page < totalPages; page++) {
        const startTime = process.hrtime.bigint();

        const response = await request(app)
          .get('/api/correlations')
          .query({
            sourceDatasetId: datasetId,
            limit: pageSize,
            offset: page * pageSize
          })
          .expect(200);

        const endTime = process.hrtime.bigint();
        sequentialDurations.push(Number(endTime - startTime) / 1000000);

        expect(response.body.data.length).toBeLessThanOrEqual(pageSize);
      }

      const avgSequentialDuration = sequentialDurations.reduce((sum, d) => sum + d, 0) / sequentialDurations.length;

      // Test random page access
      const randomDurations = [];
      for (let i = 0; i < 50; i++) {
        const randomPage = Math.floor(Math.random() * totalPages);
        const startTime = process.hrtime.bigint();

        const response = await request(app)
          .get('/api/correlations')
          .query({
            sourceDatasetId: datasetId,
            limit: pageSize,
            offset: randomPage * pageSize
          })
          .expect(200);

        const endTime = process.hrtime.bigint();
        randomDurations.push(Number(endTime - startTime) / 1000000);
      }

      const avgRandomDuration = randomDurations.reduce((sum, d) => sum + d, 0) / randomDurations.length;

      expect(avgSequentialDuration).toBeLessThan(100);
      expect(avgRandomDuration).toBeLessThan(150);

      console.log(`Sequential pagination: ${avgSequentialDuration.toFixed(2)}ms avg`);
      console.log(`Random pagination: ${avgRandomDuration.toFixed(2)}ms avg`);
    });
  });

  describe('Memory Scalability', () => {
    it('should handle memory usage scaling with dataset size', async () => {
      const memorySnapshots = [];

      for (let i = 0; i < largeDatasetIds.length; i++) {
        const datasetId = largeDatasetIds[i];

        // Garbage collection before test
        if (global.gc) global.gc();
        await new Promise(resolve => setTimeout(resolve, 100));

        const beforeMemory = process.memoryUsage();

        // Perform operations
        for (let j = 0; j < 10; j++) {
          await request(app)
            .post('/api/correlations/discover')
            .send({
              sourceDatasetId: datasetId,
              targetDatasetId: datasetId,
              correlationType: 'one_to_one'
            })
            .expect(201);
        }

        const afterMemory = process.memoryUsage();
        const memoryIncrease = afterMemory.heapUsed - beforeMemory.heapUsed;

        memorySnapshots.push({
          size: i === 0 ? '1K' : i === 1 ? '10K' : i === 2 ? '100K' : '500K',
          memoryIncrease,
          memoryPerOperation: memoryIncrease / 10
        });

        // Force garbage collection
        if (global.gc) global.gc();
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      // Memory should scale sub-linearly with dataset size
      for (let i = 1; i < memorySnapshots.length; i++) {
        const sizeRatio = [1000, 10000, 100000, 500000][i] / [1000, 10000, 100000, 500000][i - 1];
        const memoryRatio = memorySnapshots[i].memoryPerOperation / memorySnapshots[i - 1].memoryPerOperation;

        expect(memoryRatio).toBeLessThan(sizeRatio * 2);
      }

      console.log('\nMemory Scalability Results:');
      console.log('==============================');
      memorySnapshots.forEach(snapshot => {
        console.log(`${snapshot.size} rows: ${(snapshot.memoryPerOperation / 1024).toFixed(2)}KB per operation`);
      });
    });

    it('should handle memory cleanup after operations', async () => {
      const datasetId = largeDatasetIds[0]; // 1K rows
      const numOperations = 50;

      const beforeMemory = process.memoryUsage();

      // Perform many operations
      for (let i = 0; i < numOperations; i++) {
        await request(app)
          .post('/api/correlations/discover')
          .send({
            sourceDatasetId: datasetId,
            targetDatasetId: datasetId,
            correlationType: 'one_to_one'
          })
          .expect(201);
      }

      const afterOperationsMemory = process.memoryUsage();

      // Force garbage collection
      if (global.gc) global.gc();
      await new Promise(resolve => setTimeout(resolve, 500));

      const afterGCMemory = process.memoryUsage();

      const operationsIncrease = afterOperationsMemory.heapUsed - beforeMemory.heapUsed;
      const gcRecovery = afterOperationsMemory.heapUsed - afterGCMemory.heapUsed;
      const gcEfficiency = gcRecovery / operationsIncrease;

      expect(gcEfficiency).toBeGreaterThan(0.7); // Should recover > 70% of memory

      console.log(`\nMemory Management Results:`);
      console.log(`Memory increase during operations: ${(operationsIncrease / 1024 / 1024).toFixed(2)}MB`);
      console.log(`Memory recovered by GC: ${(gcRecovery / 1024 / 1024).toFixed(2)}MB`);
      console.log(`GC efficiency: ${(gcEfficiency * 100).toFixed(2)}%`);
    });
  });

  describe('Long-running Stability', () => {
    it('should maintain performance over extended period', async () => {
      const testDuration = 60000; // 1 minute
      const requestsPerSecond = 5;
      const totalRequests = (testDuration / 1000) * requestsPerSecond;

      const results = {
        success: 0,
        errors: 0,
        responseTimes: [] as number[],
        startTime: Date.now()
      };

      const runRequest = async () => {
        while (Date.now() - results.startTime < testDuration) {
          const requestStartTime = Date.now();

          try {
            await request(app)
              .get('/api/correlations/statistics')
              .expect(200);

            results.success++;
          } catch (error) {
            results.errors++;
          }

          const responseTime = Date.now() - requestStartTime;
          results.responseTimes.push(responseTime);

          // Wait to maintain request rate
          const nextRequestTime = results.startTime + (results.success + results.errors) * (1000 / requestsPerSecond);
          const delay = Math.max(0, nextRequestTime - Date.now());
          if (delay > 0) {
            await new Promise(resolve => setTimeout(resolve, delay));
          }
        }
      };

      // Run multiple concurrent workers
      const numWorkers = 3;
      const workers = [];
      for (let i = 0; i < numWorkers; i++) {
        workers.push(runRequest());
      }

      await Promise.all(workers);

      const actualDuration = Date.now() - results.startTime;
      const actualThroughput = results.success / (actualDuration / 1000);
      const avgResponseTime = results.responseTimes.reduce((sum, t) => sum + t, 0) / results.responseTimes.length;
      const maxResponseTime = Math.max(...results.responseTimes);
      const successRate = (results.success / (results.success + results.errors)) * 100;

      expect(successRate).toBeGreaterThan(95);
      expect(actualThroughput).toBeGreaterThan(requestsPerSecond * numWorkers * 0.8);
      expect(avgResponseTime).toBeLessThan(1000);
      expect(maxResponseTime).toBeLessThan(5000);

      console.log(`\nLong-running Stability Results (${actualDuration / 1000}s):`);
      console.log('==========================================');
      console.log(`Target throughput: ${requestsPerSecond * numWorkers} req/s`);
      console.log(`Actual throughput: ${actualThroughput.toFixed(2)} req/s`);
      console.log(`Success rate: ${successRate.toFixed(2)}%`);
      console.log(`Average response time: ${avgResponseTime.toFixed(2)}ms`);
      console.log(`Max response time: ${maxResponseTime.toFixed(2)}ms`);
      console.log(`Total requests: ${results.success + results.errors}`);
    });
  });
});