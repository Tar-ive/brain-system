import request from 'supertest';
import app from '../../src/index';
import { CorrelationService } from '../../src/services/CorrelationService';
import { generateLargeDataset } from '../helpers/test-utils';

describe('Load and Performance Tests', () => {
  let correlationService: CorrelationService;
  let testDatasetId: string;

  beforeAll(async () => {
    correlationService = new CorrelationService();

    // Create a large test dataset
    const dataset = await correlationService.addDataset({
      id: 'large-test-dataset',
      name: 'Large Test Dataset',
      description: 'Dataset for load testing',
      columns: ['id', 'name', 'value', 'category', 'timestamp'],
      rowCount: 100000,
      metadata: { test: true, size: 'large' },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    });

    testDatasetId = dataset.id;
  });

  describe('Concurrent Request Handling', () => {
    it('should handle 100 concurrent correlation discoveries', async () => {
      const numRequests = 100;
      const promises = [];

      // Create concurrent requests
      for (let i = 0; i < numRequests; i++) {
        promises.push(
          request(app)
            .post('/api/correlations/discover')
            .send({
              sourceDatasetId: testDatasetId,
              targetDatasetId: testDatasetId,
              correlationType: 'one_to_one',
              parameters: {
                keyColumn: 'id',
                joinType: 'inner'
              }
            })
        );
      }

      const startTime = process.hrtime.bigint();

      // Execute all requests concurrently
      const responses = await Promise.all(promises);

      const endTime = process.hrtime.bigint();
      const duration = Number(endTime - startTime) / 1000000; // Convert to milliseconds

      // Verify all requests succeeded
      const successCount = responses.filter(r => r.status === 201).length;
      expect(successCount).toBe(numRequests);

      // Performance assertions
      expect(duration).toBeLessThan(10000); // Should complete within 10 seconds
      expect(duration / numRequests).toBeLessThan(200); // Average per request < 200ms

      console.log(`Concurrent discoveries: ${numRequests} in ${duration}ms`);
      console.log(`Average per request: ${duration / numRequests}ms`);
    });

    it('should handle mixed read/write operations concurrently', async () => {
      const numOperations = 50;
      const promises = [];

      // Create mixed operations
      for (let i = 0; i < numOperations; i++) {
        if (i % 3 === 0) {
          // Write operation - create correlation
          promises.push(
            request(app)
              .post('/api/correlations/discover')
              .send({
                sourceDatasetId: testDatasetId,
                targetDatasetId: testDatasetId,
                correlationType: 'one_to_one'
              })
          );
        } else if (i % 3 === 1) {
          // Read operation - get correlations
          promises.push(
            request(app)
              .get('/api/correlations')
              .query({ limit: 20 })
          );
        } else {
          // Read operation - get statistics
          promises.push(
            request(app)
              .get('/api/correlations/statistics')
          );
        }
      }

      const startTime = process.hrtime.bigint();
      const responses = await Promise.all(promises);
      const endTime = process.hrtime.bigint();

      const duration = Number(endTime - startTime) / 1000000;

      // Verify all operations succeeded
      const successCount = responses.filter(r => r.status === 200 || r.status === 201).length;
      expect(successCount).toBe(numOperations);

      console.log(`Mixed operations: ${numOperations} in ${duration}ms`);
      console.log(`Average per operation: ${duration / numOperations}ms`);
    });
  });

  describe('Memory Usage Under Load', () => {
    it('should handle large dataset correlations without memory leaks', async () => {
      const initialMemory = process.memoryUsage().heapUsed;

      // Perform many correlation discoveries
      for (let i = 0; i < 50; i++) {
        await request(app)
          .post('/api/correlations/discover')
          .send({
            sourceDatasetId: testDatasetId,
            targetDatasetId: testDatasetId,
            correlationType: 'many_to_many',
            parameters: {
              keyColumn: 'category'
            }
          })
          .expect(201);
      }

      // Force garbage collection if available
      if (global.gc) {
        global.gc();
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      const finalMemory = process.memoryUsage().heapUsed;
      const memoryIncrease = finalMemory - initialMemory;

      // Memory increase should be reasonable (< 50MB)
      expect(memoryIncrease).toBeLessThan(50 * 1024 * 1024);

      console.log(`Memory increase: ${(memoryIncrease / 1024 / 1024).toFixed(2)}MB`);
    });

    it('should handle large response payloads', async () => {
      // Create many correlations first
      for (let i = 0; i < 100; i++) {
        await request(app)
          .post('/api/correlations/discover')
          .send({
            sourceDatasetId: testDatasetId,
            targetDatasetId: testDatasetId,
            correlationType: 'one_to_one'
          })
          .expect(201);
      }

      // Request large payload
      const response = await request(app)
        .get('/api/correlations')
        .query({ limit: 100 })
        .expect(200);

      expect(response.body.data.length).toBeGreaterThan(0);
      expect(response.body.pagination.total).toBeGreaterThan(0);

      const responseSize = JSON.stringify(response.body).length;
      expect(responseSize).toBeLessThan(1024 * 1024); // Less than 1MB

      console.log(`Large response size: ${(responseSize / 1024).toFixed(2)}KB`);
    });
  });

  describe('Rate Limiting', () => {
    it('should enforce rate limits on API endpoints', async () => {
      const numRequests = 110; // Exceed default limit of 100
      const promises = [];

      for (let i = 0; i < numRequests; i++) {
        promises.push(
          request(app)
            .get('/api/correlations/statistics')
        );
      }

      const responses = await Promise.all(promises);

      const successResponses = responses.filter(r => r.status === 200);
      const rateLimitedResponses = responses.filter(r => r.status === 429);

      expect(rateLimitedResponses.length).toBeGreaterThan(0);
      expect(successResponses.length + rateLimitedResponses.length).toBe(numRequests);

      console.log(`Rate limited: ${rateLimitedResponses.length} out of ${numRequests}`);
    });

    it('should allow requests after rate limit window', async () => {
      // First, trigger rate limiting
      const promises = [];
      for (let i = 0; i < 105; i++) {
        promises.push(
          request(app)
            .get('/api/correlations/statistics')
        );
      }

      await Promise.all(promises);

      // Wait for rate limit window to reset (15 minutes in real scenario, but our test uses shorter window)
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Should be able to make requests again
      const response = await request(app)
        .get('/api/correlations/statistics')
        .expect(200);

      expect(response.body.success).toBe(true);
    });
  });

  describe('Database Performance', () => {
    it('should handle large number of correlations in database', async () => {
      const numCorrelations = 200;
      const correlationIds = [];

      // Create many correlations
      for (let i = 0; i < numCorrelations; i++) {
        const response = await request(app)
          .post('/api/correlations/discover')
          .send({
            sourceDatasetId: testDatasetId,
            targetDatasetId: testDatasetId,
            correlationType: ['one_to_one', 'many_to_many', 'temporal'][i % 3],
            parameters: {
              keyColumn: i % 2 === 0 ? 'id' : 'category'
            }
          })
          .expect(201);

        correlationIds.push(response.body.data.id);
      }

      // Test query performance with filters
      const startTime = process.hrtime.bigint();

      const response = await request(app)
        .get('/api/correlations')
        .query({
          sourceDatasetId: testDatasetId,
          limit: 50
        })
        .expect(200);

      const endTime = process.hrtime.bigint();
      const duration = Number(endTime - startTime) / 1000000;

      expect(response.body.data.length).toBeGreaterThan(0);
      expect(response.body.pagination.total).toBeGreaterThanOrEqual(numCorrelations);
      expect(duration).toBeLessThan(100); // Query should be fast

      console.log(`Query with ${numCorrelations} correlations: ${duration}ms`);
      console.log(`Returned ${response.body.data.length} correlations`);
    });

    it('should handle complex filtering efficiently', async () => {
      const startTime = process.hrtime.bigint();

      const response = await request(app)
        .get('/api/correlations')
        .query({
          sourceDatasetId: testDatasetId,
          targetDatasetId: testDatasetId,
          correlationType: 'one_to_one',
          minConfidence: 0.8,
          limit: 20,
          offset: 10
        })
        .expect(200);

      const endTime = process.hrtime.bigint();
      const duration = Number(endTime - startTime) / 1000000;

      expect(response.body.success).toBe(true);
      expect(duration).toBeLessThan(100);

      // Verify filters are applied
      response.body.data.forEach((correlation: any) => {
        expect(correlation.sourceDatasetId).toBe(testDatasetId);
        expect(correlation.targetDatasetId).toBe(testDatasetId);
        expect(correlation.correlationType).toBe('one_to_one');
        expect(correlation.confidence).toBeGreaterThanOrEqual(0.8);
      });

      console.log(`Complex filtered query: ${duration}ms`);
    });
  });

  describe('Stress Testing', () => {
    it('should handle sustained load over time', async () => {
      const duration = 30000; // 30 seconds
      const requestsPerSecond = 10;
      const totalRequests = (duration / 1000) * requestsPerSecond;
      const promises = [];

      const startTime = Date.now();

      // Launch sustained requests
      for (let i = 0; i < totalRequests; i++) {
        const delay = (i / requestsPerSecond) * 1000;
        promises.push(
          new Promise(resolve => {
            setTimeout(async () => {
              try {
                const response = await request(app)
                  .post('/api/correlations/discover')
                  .send({
                    sourceDatasetId: testDatasetId,
                    targetDatasetId: testDatasetId,
                    correlationType: 'one_to_one'
                  });

                resolve({
                  success: response.status === 201,
                  duration: Date.now() - (startTime + delay)
                });
              } catch (error) {
                resolve({
                  success: false,
                  duration: Date.now() - (startTime + delay),
                  error: error.message
                });
              }
            }, delay);
          })
        );
      }

      const results = await Promise.all(promises);
      const endTime = Date.now();
      const actualDuration = endTime - startTime;

      // Analyze results
      const successCount = results.filter((r: any) => r.success).length;
      const failureCount = results.filter((r: any) => !r.success).length;
      const avgResponseTime = results.reduce((sum: number, r: any) => sum + r.duration, 0) / results.length;

      expect(successCount).toBeGreaterThan(totalRequests * 0.95); // 95% success rate
      expect(failureCount).toBeLessThan(totalRequests * 0.05); // < 5% failure rate
      expect(avgResponseTime).toBeLessThan(1000); // Average response time < 1s

      console.log(`Sustained load test completed:`);
      console.log(`- Duration: ${actualDuration}ms`);
      console.log(`- Requests: ${totalRequests}`);
      console.log(`- Success rate: ${(successCount / totalRequests * 100).toFixed(2)}%`);
      console.log(`- Average response time: ${avgResponseTime.toFixed(2)}ms`);
    });

    it('should handle burst traffic', async () => {
      const burstSize = 50;
      const numBursts = 5;
      const burstInterval = 1000; // 1 second between bursts

      for (let burst = 0; burst < numBursts; burst++) {
        const startTime = process.hrtime.bigint();
        const promises = [];

        // Create burst of requests
        for (let i = 0; i < burstSize; i++) {
          promises.push(
            request(app)
              .post('/api/correlations/discover')
              .send({
                sourceDatasetId: testDatasetId,
                targetDatasetId: testDatasetId,
                correlationType: 'one_to_one'
              })
          );
        }

        const responses = await Promise.all(promises);
        const endTime = process.hrtime.bigint();
        const duration = Number(endTime - startTime) / 1000000;

        const successCount = responses.filter(r => r.status === 201).length;

        expect(successCount).toBe(burstSize);
        expect(duration).toBeLessThan(2000); // Each burst should complete within 2s

        console.log(`Burst ${burst + 1}: ${burstSize} requests in ${duration}ms`);

        // Wait between bursts
        if (burst < numBursts - 1) {
          await new Promise(resolve => setTimeout(resolve, burstInterval));
        }
      }
    });
  });

  describe('Performance Monitoring', () => {
    it('should track performance metrics', async () => {
      const metrics = {
        totalRequests: 0,
        totalDuration: 0,
        minDuration: Infinity,
        maxDuration: 0,
        errors: 0
      };

      const numTestRequests = 20;

      for (let i = 0; i < numTestRequests; i++) {
        const startTime = process.hrtime.bigint();

        try {
          const response = await request(app)
            .get('/api/correlations/statistics');

          const endTime = process.hrtime.bigint();
          const duration = Number(endTime - startTime) / 1000000;

          metrics.totalRequests++;
          metrics.totalDuration += duration;
          metrics.minDuration = Math.min(metrics.minDuration, duration);
          metrics.maxDuration = Math.max(metrics.maxDuration, duration);

          expect(response.status).toBe(200);
        } catch (error) {
          metrics.errors++;
        }
      }

      const avgDuration = metrics.totalDuration / metrics.totalRequests;

      expect(metrics.errors).toBe(0);
      expect(avgDuration).toBeLessThan(100);
      expect(metrics.maxDuration).toBeLessThan(500);

      console.log(`Performance metrics:`);
      console.log(`- Total requests: ${metrics.totalRequests}`);
      console.log(`- Average duration: ${avgDuration.toFixed(2)}ms`);
      console.log(`- Min duration: ${metrics.minDuration.toFixed(2)}ms`);
      console.log(`- Max duration: ${metrics.maxDuration.toFixed(2)}ms`);
      console.log(`- Errors: ${metrics.errors}`);
    });
  });
});