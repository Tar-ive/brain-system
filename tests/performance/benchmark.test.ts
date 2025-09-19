import request from 'supertest';
import app from '../../src/index';
import { CorrelationService } from '../../src/services/CorrelationService';
import { generateLargeDataset } from '../helpers/test-utils';

describe('Performance Benchmarks', () => {
  let correlationService: CorrelationService;
  let testDatasetIds: string[] = [];

  beforeAll(async () => {
    correlationService = new CorrelationService();

    // Create test datasets of different sizes
    const sizes = [1000, 10000, 100000];
    for (let i = 0; i < sizes.length; i++) {
      const dataset = await correlationService.addDataset({
        id: `benchmark-dataset-${i}`,
        name: `Benchmark Dataset ${i + 1}`,
        description: `Dataset with ${sizes[i]} rows`,
        columns: ['id', 'name', 'value', 'category', 'timestamp'],
        rowCount: sizes[i],
        metadata: { benchmark: true, size: sizes[i] },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      });
      testDatasetIds.push(dataset.id);
    }
  });

  describe('Correlation Discovery Benchmark', () => {
    it('should benchmark correlation discovery across different dataset sizes', async () => {
      const benchmarks = [];

      for (let i = 0; i < testDatasetIds.length; i++) {
        const datasetId = testDatasetIds[i];
        const iterations = 10;
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
          const duration = Number(endTime - startTime) / 1000000; // Convert to ms
          durations.push(duration);
        }

        const avgDuration = durations.reduce((sum, d) => sum + d, 0) / durations.length;
        const minDuration = Math.min(...durations);
        const maxDuration = Math.max(...durations);

        benchmarks.push({
          datasetSize: i === 0 ? '1K' : i === 1 ? '10K' : '100K',
          avgDuration,
          minDuration,
          maxDuration,
          iterations
        });

        // Performance assertions
        expect(avgDuration).toBeLessThan(i === 0 ? 100 : i === 1 ? 200 : 500);
        expect(maxDuration).toBeLessThan(i === 0 ? 200 : i === 2 ? 500 : 1000);
      }

      // Log benchmark results
      console.log('\nCorrelation Discovery Benchmark Results:');
      console.log('==========================================');
      benchmarks.forEach(b => {
        console.log(`${b.datasetSize} rows:`);
        console.log(`  Average: ${b.avgDuration.toFixed(2)}ms`);
        console.log(`  Min: ${b.minDuration.toFixed(2)}ms`);
        console.log(`  Max: ${b.maxDuration.toFixed(2)}ms`);
        console.log(`  Iterations: ${b.iterations}`);
        console.log('');
      });

      // Verify scalability
      expect(benchmarks[1].avgDuration / benchmarks[0].avgDuration).toBeLessThan(3); // 10x data should be < 3x slower
      expect(benchmarks[2].avgDuration / benchmarks[1].avgDuration).toBeLessThan(3); // 10x data should be < 3x slower
    });

    it('should benchmark different correlation types', async () => {
      const correlationTypes = ['one_to_one', 'one_to_many', 'many_to_many', 'temporal'];
      const benchmarks = [];

      for (const type of correlationTypes) {
        const iterations = 20;
        const durations = [];

        for (let i = 0; i < iterations; i++) {
          const startTime = process.hrtime.bigint();

          await request(app)
            .post('/api/correlations/discover')
            .send({
              sourceDatasetId: testDatasetIds[1], // Use 10K dataset
              targetDatasetId: testDatasetIds[1],
              correlationType: type,
              parameters: type === 'temporal' ? {
                lagDays: 30,
                aggregation: 'sum'
              } : {
                keyColumn: 'id',
                joinType: 'inner'
              }
            })
            .expect(201);

          const endTime = process.hrtime.bigint();
          const duration = Number(endTime - startTime) / 1000000;
          durations.push(duration);
        }

        const avgDuration = durations.reduce((sum, d) => sum + d, 0) / durations.length;
        const minDuration = Math.min(...durations);
        const maxDuration = Math.max(...durations);

        benchmarks.push({
          type,
          avgDuration,
          minDuration,
          maxDuration,
          iterations
        });

        // Performance assertions
        expect(avgDuration).toBeLessThan(300);
        expect(maxDuration).toBeLessThan(1000);
      }

      // Log benchmark results
      console.log('\nCorrelation Type Benchmark Results:');
      console.log('====================================');
      benchmarks.forEach(b => {
        console.log(`${b.type}:`);
        console.log(`  Average: ${b.avgDuration.toFixed(2)}ms`);
        console.log(`  Min: ${b.minDuration.toFixed(2)}ms`);
        console.log(`  Max: ${b.maxDuration.toFixed(2)}ms`);
        console.log(`  Iterations: ${b.iterations}`);
        console.log('');
      });
    });
  });

  describe('Query Performance Benchmark', () => {
    beforeEach(async () => {
      // Create test correlations for benchmarking
      for (let i = 0; i < 100; i++) {
        await request(app)
          .post('/api/correlations/discover')
          .send({
            sourceDatasetId: testDatasetIds[1],
            targetDatasetId: testDatasetIds[1],
            correlationType: ['one_to_one', 'many_to_many', 'temporal'][i % 3],
            confidence: 0.5 + (Math.random() * 0.5)
          })
          .expect(201);
      }
    });

    it('should benchmark correlation listing performance', async () => {
      const benchmarks = [
        { name: 'No filters', query: {} },
        { name: 'Source filter', query: { sourceDatasetId: testDatasetIds[1] } },
        { name: 'Type filter', query: { correlationType: 'one_to_one' } },
        { name: 'Confidence filter', query: { minConfidence: 0.8 } },
        { name: 'Combined filters', query: {
          sourceDatasetId: testDatasetIds[1],
          correlationType: 'one_to_one',
          minConfidence: 0.8
        }}
      ];

      for (const benchmark of benchmarks) {
        const iterations = 30;
        const durations = [];

        for (let i = 0; i < iterations; i++) {
          const startTime = process.hrtime.bigint();

          await request(app)
            .get('/api/correlations')
            .query(benchmark.query)
            .expect(200);

          const endTime = process.hrtime.bigint();
          const duration = Number(endTime - startTime) / 1000000;
          durations.push(duration);
        }

        const avgDuration = durations.reduce((sum, d) => sum + d, 0) / durations.length;
        const minDuration = Math.min(...durations);
        const maxDuration = Math.max(...durations);

        // Performance assertions
        expect(avgDuration).toBeLessThan(100);
        expect(maxDuration).toBeLessThan(500);

        console.log(`${benchmark.name}:`);
        console.log(`  Average: ${avgDuration.toFixed(2)}ms`);
        console.log(`  Min: ${minDuration.toFixed(2)}ms`);
        console.log(`  Max: ${maxDuration.toFixed(2)}ms`);
        console.log('');
      }
    });

    it('should benchmark pagination performance', async () => {
      const pageSizes = [10, 25, 50, 100];
      const benchmarks = [];

      for (const pageSize of pageSizes) {
        const iterations = 20;
        const durations = [];

        for (let i = 0; i < iterations; i++) {
          const startTime = process.hrtime.bigint();

          await request(app)
            .get('/api/correlations')
            .query({
              sourceDatasetId: testDatasetIds[1],
              limit: pageSize,
              offset: Math.floor(Math.random() * 50) // Random offset
            })
            .expect(200);

          const endTime = process.hrtime.bigint();
          const duration = Number(endTime - startTime) / 1000000;
          durations.push(duration);
        }

        const avgDuration = durations.reduce((sum, d) => sum + d, 0) / durations.length;
        const minDuration = Math.min(...durations);
        const maxDuration = Math.max(...durations);

        benchmarks.push({
          pageSize,
          avgDuration,
          minDuration,
          maxDuration,
          iterations
        });

        // Performance assertions
        expect(avgDuration).toBeLessThan(100);
      }

      // Log benchmark results
      console.log('\nPagination Benchmark Results:');
      console.log('================================');
      benchmarks.forEach(b => {
        console.log(`${b.pageSize} items per page:`);
        console.log(`  Average: ${b.avgDuration.toFixed(2)}ms`);
        console.log(`  Min: ${b.minDuration.toFixed(2)}ms`);
        console.log(`  Max: ${b.maxDuration.toFixed(2)}ms`);
        console.log('');
      });
    });
  });

  describe('Validation Performance Benchmark', () => {
    it('should benchmark correlation validation performance', async () => {
      // Create test correlations
      const correlationIds = [];
      for (let i = 0; i < 20; i++) {
        const response = await request(app)
          .post('/api/correlations/discover')
          .send({
            sourceDatasetId: testDatasetIds[1],
            targetDatasetId: testDatasetIds[1],
            correlationType: 'one_to_one'
          })
          .expect(201);

        correlationIds.push(response.body.data.id);
      }

      const iterations = correlationIds.length;
      const durations = [];

      for (const correlationId of correlationIds) {
        const startTime = process.hrtime.bigint();

        await request(app)
          .post(`/api/correlations/${correlationId}/validate`)
          .expect(200);

        const endTime = process.hrtime.bigint();
        const duration = Number(endTime - startTime) / 1000000;
        durations.push(duration);
      }

      const avgDuration = durations.reduce((sum, d) => sum + d, 0) / durations.length;
      const minDuration = Math.min(...durations);
      const maxDuration = Math.max(...durations);

      // Performance assertions
      expect(avgDuration).toBeLessThan(200);
      expect(maxDuration).toBeLessThan(1000);

      console.log('\nValidation Benchmark Results:');
      console.log('===============================');
      console.log(`Average: ${avgDuration.toFixed(2)}ms`);
      console.log(`Min: ${minDuration.toFixed(2)}ms`);
      console.log(`Max: ${maxDuration.toFixed(2)}ms`);
      console.log(`Iterations: ${iterations}`);
      console.log('');
    });
  });

  describe('Memory Efficiency Benchmark', () => {
    it('should benchmark memory usage during operations', async () => {
      const initialMemory = process.memoryUsage();
      const operations = 100;

      // Perform operations
      for (let i = 0; i < operations; i++) {
        await request(app)
          .post('/api/correlations/discover')
          .send({
            sourceDatasetId: testDatasetIds[0],
            targetDatasetId: testDatasetIds[0],
            correlationType: 'one_to_one'
          })
          .expect(201);

        await request(app)
          .get('/api/correlations/statistics')
          .expect(200);
      }

      const finalMemory = process.memoryUsage();
      const memoryIncrease = {
        heapUsed: finalMemory.heapUsed - initialMemory.heapUsed,
        heapTotal: finalMemory.heapTotal - initialMemory.heapTotal,
        external: finalMemory.external - initialMemory.external,
        rss: finalMemory.rss - initialMemory.rss
      };

      // Memory assertions
      expect(memoryIncrease.heapUsed).toBeLessThan(50 * 1024 * 1024); // < 50MB increase
      expect(memoryIncrease.rss).toBeLessThan(100 * 1024 * 1024); // < 100MB RSS increase

      console.log('\nMemory Usage Benchmark Results:');
      console.log('==================================');
      console.log(`Heap used increase: ${(memoryIncrease.heapUsed / 1024 / 1024).toFixed(2)}MB`);
      console.log(`Heap total increase: ${(memoryIncrease.heapTotal / 1024 / 1024).toFixed(2)}MB`);
      console.log(`External increase: ${(memoryIncrease.external / 1024 / 1024).toFixed(2)}MB`);
      console.log(`RSS increase: ${(memoryIncrease.rss / 1024 / 1024).toFixed(2)}MB`);
      console.log(`Operations: ${operations}`);
      console.log(`Memory per operation: ${(memoryIncrease.heapUsed / operations / 1024).toFixed(2)}KB`);
      console.log('');
    });
  });

  describe('Throughput Benchmark', () => {
    it('should measure maximum throughput', async () => {
      const testDuration = 10000; // 10 seconds
      const startTime = Date.now();
      let successfulRequests = 0;
      let totalRequests = 0;

      // Launch concurrent requests
      const runRequest = async () => {
        while (Date.now() - startTime < testDuration) {
          totalRequests++;
          try {
            await request(app)
              .get('/api/correlations/statistics')
              .expect(200);

            successfulRequests++;
          } catch (error) {
            // Request failed
          }
        }
      };

      // Run multiple concurrent workers
      const numWorkers = 10;
      const workers = [];
      for (let i = 0; i < numWorkers; i++) {
        workers.push(runRequest());
      }

      await Promise.all(workers);

      const actualDuration = Date.now() - startTime;
      const throughput = successfulRequests / (actualDuration / 1000); // requests per second
      const successRate = (successfulRequests / totalRequests) * 100;

      // Throughput assertions
      expect(throughput).toBeGreaterThan(50); // > 50 requests per second
      expect(successRate).toBeGreaterThan(95); // > 95% success rate

      console.log('\nThroughput Benchmark Results:');
      console.log('===============================');
      console.log(`Duration: ${actualDuration}ms`);
      console.log(`Total requests: ${totalRequests}`);
      console.log(`Successful requests: ${successfulRequests}`);
      console.log(`Throughput: ${throughput.toFixed(2)} requests/second`);
      console.log(`Success rate: ${successRate.toFixed(2)}%`);
      console.log(`Workers: ${numWorkers}`);
      console.log('');
    });
  });
});