import request from 'supertest';
import app from '../../src/index';
import { CorrelationService } from '../../src/services/CorrelationService';
import { generateTestDataset } from '../helpers/test-utils';

describe('Correlation API Integration Tests', () => {
  let correlationService: CorrelationService;
  let testDataset1: any;
  let testDataset2: any;

  beforeAll(async () => {
    correlationService = new CorrelationService();

    // Setup test datasets
    testDataset1 = await correlationService.addDataset({
      id: 'test-dataset-1',
      name: 'Test Dataset 1',
      description: 'First test dataset',
      columns: ['id', 'name', 'value'],
      rowCount: 1000,
      metadata: {},
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    });

    testDataset2 = await correlationService.addDataset({
      id: 'test-dataset-2',
      name: 'Test Dataset 2',
      description: 'Second test dataset',
      columns: ['id', 'category', 'score'],
      rowCount: 500,
      metadata: {},
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    });
  });

  describe('POST /api/correlations/discover', () => {
    it('should discover correlation with valid data', async () => {
      const correlationData = {
        sourceDatasetId: 'test-dataset-1',
        targetDatasetId: 'test-dataset-2',
        correlationType: 'one_to_one',
        parameters: {
          keyColumn: 'id',
          joinType: 'inner'
        }
      };

      const response = await request(app)
        .post('/api/correlations/discover')
        .send(correlationData)
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toBeDefined();
      expect(response.body.data.sourceDatasetId).toBe('test-dataset-1');
      expect(response.body.data.targetDatasetId).toBe('test-dataset-2');
      expect(response.body.data.correlationType).toBe('one_to_one');
      expect(response.body.data.confidence).toBeGreaterThanOrEqual(0.7);
      expect(response.body.data.discoveredAt).toBeDefined();
    });

    it('should return 400 for missing required fields', async () => {
      const invalidData = {
        sourceDatasetId: 'test-dataset-1'
        // Missing targetDatasetId
      };

      const response = await request(app)
        .post('/api/correlations/discover')
        .send(invalidData)
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('Validation error');
    });

    it('should return 400 for invalid correlation type', async () => {
      const invalidData = {
        sourceDatasetId: 'test-dataset-1',
        targetDatasetId: 'test-dataset-2',
        correlationType: 'invalid_type'
      };

      const response = await request(app)
        .post('/api/correlations/discover')
        .send(invalidData)
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('Validation error');
    });

    it('should return 404 for non-existent dataset', async () => {
      const invalidData = {
        sourceDatasetId: 'non-existent',
        targetDatasetId: 'test-dataset-2'
      };

      const response = await request(app)
        .post('/api/correlations/discover')
        .send(invalidData)
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('Source or target dataset not found');
    });

    it('should handle optional parameters correctly', async () => {
      const minimalData = {
        sourceDatasetId: 'test-dataset-1',
        targetDatasetId: 'test-dataset-2'
      };

      const response = await request(app)
        .post('/api/correlations/discover')
        .send(minimalData)
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.data.correlationType).toBe('one_to_one'); // Default value
    });

    it('should handle auxiliary data', async () => {
      const correlationData = {
        sourceDatasetId: 'test-dataset-1',
        targetDatasetId: 'test-dataset-2',
        auxiliaryData: {
          weights: [0.5, 0.3, 0.2],
          config: { threshold: 0.8 }
        }
      };

      const response = await request(app)
        .post('/api/correlations/discover')
        .send(correlationData)
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toBeDefined();
    });
  });

  describe('GET /api/correlations', () => {
    beforeEach(async () => {
      // Add some test correlations
      await correlationService.discoverCorrelation('test-dataset-1', 'test-dataset-2', {
        correlationType: 'one_to_one'
      });
      await correlationService.discoverCorrelation('test-dataset-1', 'test-dataset-2', {
        correlationType: 'many_to_many'
      });
      await correlationService.discoverCorrelation('test-dataset-2', 'test-dataset-1', {
        correlationType: 'temporal'
      });
    });

    it('should return correlations with default pagination', async () => {
      const response = await request(app)
        .get('/api/correlations')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toBeDefined();
      expect(Array.isArray(response.body.data)).toBe(true);
      expect(response.body.pagination).toBeDefined();
      expect(response.body.pagination.total).toBeGreaterThanOrEqual(3);
      expect(response.body.pagination.limit).toBe(10);
      expect(response.body.pagination.offset).toBe(0);
    });

    it('should filter by source dataset', async () => {
      const response = await request(app)
        .get('/api/correlations?sourceDatasetId=test-dataset-1')
        .expect(200);

      expect(response.body.success).toBe(true);
      response.body.data.forEach((correlation: any) => {
        expect(correlation.sourceDatasetId).toBe('test-dataset-1');
      });
    });

    it('should filter by target dataset', async () => {
      const response = await request(app)
        .get('/api/correlations?targetDatasetId=test-dataset-2')
        .expect(200);

      expect(response.body.success).toBe(true);
      response.body.data.forEach((correlation: any) => {
        expect(correlation.targetDatasetId).toBe('test-dataset-2');
      });
    });

    it('should filter by correlation type', async () => {
      const response = await request(app)
        .get('/api/correlations?correlationType=one_to_one')
        .expect(200);

      expect(response.body.success).toBe(true);
      response.body.data.forEach((correlation: any) => {
        expect(correlation.correlationType).toBe('one_to_one');
      });
    });

    it('should filter by minimum confidence', async () => {
      const response = await request(app)
        .get('/api/correlations?minConfidence=0.8')
        .expect(200);

      expect(response.body.success).toBe(true);
      response.body.data.forEach((correlation: any) => {
        expect(correlation.confidence).toBeGreaterThanOrEqual(0.8);
      });
    });

    it('should handle pagination parameters', async () => {
      const response = await request(app)
        .get('/api/correlations?limit=5&offset=1')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.length).toBeLessThanOrEqual(5);
      expect(response.body.pagination.limit).toBe(5);
      expect(response.body.pagination.offset).toBe(1);
    });

    it('should handle empty results', async () => {
      const response = await request(app)
        .get('/api/correlations?sourceDatasetId=non-existent')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveLength(0);
      expect(response.body.pagination.total).toBe(0);
    });
  });

  describe('GET /api/correlations/:id', () => {
    let testCorrelation: any;

    beforeEach(async () => {
      testCorrelation = await correlationService.discoverCorrelation(
        'test-dataset-1',
        'test-dataset-2',
        { correlationType: 'one_to_one' }
      );
    });

    it('should return correlation by ID', async () => {
      const response = await request(app)
        .get(`/api/correlations/${testCorrelation.id}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toBeDefined();
      expect(response.body.data.id).toBe(testCorrelation.id);
    });

    it('should return 404 for non-existent correlation', async () => {
      const response = await request(app)
        .get('/api/correlations/non-existent-id')
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('Correlation not found');
    });

    it('should handle invalid ID format', async () => {
      const response = await request(app)
        .get('/api/correlations/invalid-id-format')
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('Validation error');
    });
  });

  describe('GET /api/correlations/:id/validation', () => {
    let testCorrelation: any;

    beforeEach(async () => {
      testCorrelation = await correlationService.discoverCorrelation(
        'test-dataset-1',
        'test-dataset-2',
        { correlationType: 'one_to_one' }
      );
    });

    it('should return validation for correlation', async () => {
      const response = await request(app)
        .get(`/api/correlations/${testCorrelation.id}/validation`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toBeDefined();
      expect(response.body.data.correlationId).toBe(testCorrelation.id);
      expect(response.body.data.validityScore).toBeDefined();
    });

    it('should return 404 for non-existent correlation validation', async () => {
      const response = await request(app)
        .get('/api/correlations/non-existent-id/validation')
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('Validation not found');
    });
  });

  describe('POST /api/correlations/:id/validate', () => {
    let testCorrelation: any;

    beforeEach(async () => {
      testCorrelation = await correlationService.discoverCorrelation(
        'test-dataset-1',
        'test-dataset-2',
        { correlationType: 'one_to_one' }
      );
    });

    it('should validate correlation successfully', async () => {
      const response = await request(app)
        .post(`/api/correlations/${testCorrelation.id}/validate`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toBeDefined();
      expect(response.body.data.correlationId).toBe(testCorrelation.id);
      expect(response.body.data.validityScore).toBeGreaterThanOrEqual(0.7);
    });

    it('should return 404 for non-existent correlation', async () => {
      const response = await request(app)
        .post('/api/correlations/non-existent-id/validate')
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('Correlation not found');
    });
  });

  describe('DELETE /api/correlations/:id', () => {
    let testCorrelation: any;

    beforeEach(async () => {
      testCorrelation = await correlationService.discoverCorrelation(
        'test-dataset-1',
        'test-dataset-2',
        { correlationType: 'one_to_one' }
      );
    });

    it('should delete correlation successfully', async () => {
      const response = await request(app)
        .delete(`/api/correlations/${testCorrelation.id}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.message).toBe('Correlation deleted successfully');

      // Verify correlation is deleted
      const getResponse = await request(app)
        .get(`/api/correlations/${testCorrelation.id}`)
        .expect(404);
    });

    it('should return 404 for non-existent correlation', async () => {
      const response = await request(app)
        .delete('/api/correlations/non-existent-id')
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('Correlation not found');
    });
  });

  describe('GET /api/correlations/statistics', () => {
    beforeEach(async () => {
      // Add test correlations
      await correlationService.discoverCorrelation('test-dataset-1', 'test-dataset-2', {
        correlationType: 'one_to_one'
      });
      await correlationService.discoverCorrelation('test-dataset-1', 'test-dataset-2', {
        correlationType: 'many_to_many'
      });
    });

    it('should return statistics', async () => {
      const response = await request(app)
        .get('/api/correlations/statistics')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toBeDefined();
      expect(response.body.data.totalCorrelations).toBeGreaterThanOrEqual(2);
      expect(response.body.data.totalValidations).toBeGreaterThanOrEqual(2);
      expect(response.body.data.averageConfidence).toBeGreaterThanOrEqual(0);
      expect(response.body.data.correlationTypes).toBeDefined();
    });
  });

  describe('Dataset Endpoints', () => {
    describe('POST /api/datasets', () => {
      it('should create dataset successfully', async () => {
        const datasetData = {
          name: 'New Test Dataset',
          description: 'A new test dataset',
          columns: ['id', 'name', 'value'],
          rowCount: 100,
          metadata: { source: 'test' }
        };

        const response = await request(app)
          .post('/api/datasets')
          .send(datasetData)
          .expect(201);

        expect(response.body.success).toBe(true);
        expect(response.body.data).toBeDefined();
        expect(response.body.data.name).toBe('New Test Dataset');
        expect(response.body.data.columns).toEqual(['id', 'name', 'value']);
        expect(response.body.data.rowCount).toBe(100);
      });

      it('should return 400 for invalid dataset data', async () => {
        const invalidData = {
          name: '',
          columns: []
        };

        const response = await request(app)
          .post('/api/datasets')
          .send(invalidData)
          .expect(400);

        expect(response.body.success).toBe(false);
        expect(response.body.error).toContain('Validation error');
      });
    });

    describe('GET /api/datasets', () => {
      it('should return all datasets', async () => {
        const response = await request(app)
          .get('/api/datasets')
          .expect(200);

        expect(response.body.success).toBe(true);
        expect(response.body.data).toBeDefined();
        expect(Array.isArray(response.body.data)).toBe(true);
        expect(response.body.data.length).toBeGreaterThanOrEqual(2); // We have 2 test datasets
      });
    });

    describe('GET /api/datasets/:id', () => {
      it('should return dataset by ID', async () => {
        const response = await request(app)
          .get(`/api/datasets/${testDataset1.id}`)
          .expect(200);

        expect(response.body.success).toBe(true);
        expect(response.body.data).toBeDefined();
        expect(response.body.data.id).toBe(testDataset1.id);
        expect(response.body.data.name).toBe('Test Dataset 1');
      });

      it('should return 404 for non-existent dataset', async () => {
        const response = await request(app)
          .get('/api/datasets/non-existent-id')
          .expect(404);

        expect(response.body.success).toBe(false);
        expect(response.body.error).toBe('Dataset not found');
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle malformed JSON', async () => {
      const response = await request(app)
        .post('/api/correlations/discover')
        .set('Content-Type', 'application/json')
        .send('invalid json')
        .expect(400);

      expect(response.body.success).toBe(false);
    });

    it('should handle large payload', async () => {
      const largePayload = {
        sourceDatasetId: 'test-dataset-1',
        targetDatasetId: 'test-dataset-2',
        auxiliaryData: { data: 'x'.repeat(1000000) } // 1MB of data
      };

      const response = await request(app)
        .post('/api/correlations/discover')
        .send(largePayload)
        .expect(201);

      expect(response.body.success).toBe(true);
    });
  });
});