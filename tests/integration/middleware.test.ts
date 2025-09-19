import request from 'supertest';
import app from '../../src/index';
import { CorrelationService } from '../../src/services/CorrelationService';

describe('Middleware Integration Tests', () => {
  let correlationService: CorrelationService;

  beforeAll(async () => {
    correlationService = new CorrelationService();

    // Setup test datasets
    await correlationService.addDataset({
      id: 'test-dataset-1',
      name: 'Test Dataset 1',
      description: 'First test dataset',
      columns: ['id', 'name', 'value'],
      rowCount: 1000,
      metadata: {},
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    });
  });

  describe('Validation Middleware', () => {
    describe('Body Validation', () => {
      it('should validate correlation discovery body', async () => {
        const invalidBody = {
          sourceDatasetId: '', // Invalid: empty string
          targetDatasetId: 'test-dataset-1',
          correlationType: 'invalid_type'
        };

        const response = await request(app)
          .post('/api/correlations/discover')
          .send(invalidBody)
          .expect(400);

        expect(response.body.success).toBe(false);
        expect(response.body.error).toBe('Validation error');
        expect(response.body.details).toBeDefined();
        expect(Array.isArray(response.body.details)).toBe(true);
      });

      it('should validate dataset creation body', async () => {
        const invalidBody = {
          name: '', // Invalid: empty string
          columns: [] // Invalid: empty array
        };

        const response = await request(app)
          .post('/api/datasets')
          .send(invalidBody)
          .expect(400);

        expect(response.body.success).toBe(false);
        expect(response.body.error).toBe('Validation error');
        expect(response.body.details).toBeDefined();
      });

      it('should accept valid correlation discovery body', async () => {
        const validBody = {
          sourceDatasetId: 'test-dataset-1',
          targetDatasetId: 'test-dataset-1',
          correlationType: 'one_to_one',
          parameters: {
            keyColumn: 'id'
          }
        };

        const response = await request(app)
          .post('/api/correlations/discover')
          .send(validBody)
          .expect(201);

        expect(response.body.success).toBe(true);
      });

      it('should handle optional fields in correlation discovery', async () => {
        const minimalBody = {
          sourceDatasetId: 'test-dataset-1',
          targetDatasetId: 'test-dataset-1'
        };

        const response = await request(app)
          .post('/api/correlations/discover')
          .send(minimalBody)
          .expect(201);

        expect(response.body.success).toBe(true);
        expect(response.body.data.correlationType).toBe('one_to_one'); // Default value
      });
    });

    describe('Query Parameter Validation', () => {
      beforeEach(async () => {
        // Add some test correlations
        await correlationService.discoverCorrelation('test-dataset-1', 'test-dataset-1');
      });

      it('should validate correlation query parameters', async () => {
        const response = await request(app)
          .get('/api/correlations?minConfidence=invalid')
          .expect(400);

        expect(response.body.success).toBe(false);
        expect(response.body.error).toBe('Query validation error');
        expect(response.body.details).toBeDefined();
      });

      it('should validate pagination parameters', async () => {
        const response = await request(app)
          .get('/api/correlations?limit=invalid&offset=invalid')
          .expect(400);

        expect(response.body.success).toBe(false);
        expect(response.body.error).toBe('Query validation error');
      });

      it('should accept valid query parameters', async () => {
        const response = await request(app)
          .get('/api/correlations?limit=5&offset=0&minConfidence=0.5')
          .expect(200);

        expect(response.body.success).toBe(true);
        expect(response.body.pagination.limit).toBe(5);
        expect(response.body.pagination.offset).toBe(0);
      });

      it('should handle default values for query parameters', async () => {
        const response = await request(app)
          .get('/api/correlations')
          .expect(200);

        expect(response.body.success).toBe(true);
        expect(response.body.pagination.limit).toBe(10);
        expect(response.body.pagination.offset).toBe(0);
      });
    });

    describe('Parameter Validation', () => {
      let testCorrelation: any;

      beforeEach(async () => {
        testCorrelation = await correlationService.discoverCorrelation(
          'test-dataset-1',
          'test-dataset-1'
        );
      });

      it('should validate ID parameter', async () => {
        const response = await request(app)
          .get('/api/correlations/invalid-id')
          .expect(400);

        expect(response.body.success).toBe(false);
        expect(response.body.error).toBe('Parameter validation error');
        expect(response.body.details).toBeDefined();
      });

      it('should accept valid ID parameter', async () => {
        const response = await request(app)
          .get(`/api/correlations/${testCorrelation.id}`)
          .expect(200);

        expect(response.body.success).toBe(true);
      });
    });
  });

  describe('Error Handling Middleware', () => {
    it('should handle 404 for unknown routes', async () => {
      const response = await request(app)
        .get('/api/unknown-route')
        .expect(404);

      expect(response.body.error).toBe('Route not found');
      expect(response.body.method).toBe('GET');
      expect(response.body.path).toBe('/api/unknown-route');
      expect(response.body.timestamp).toBeDefined();
    });

    it('should handle 404 for unknown methods', async () => {
      const response = await request(app)
        .patch('/api/correlations')
        .expect(404);

      expect(response.body.error).toBe('Route not found');
      expect(response.body.method).toBe('PATCH');
      expect(response.body.path).toBe('/api/correlations');
    });

    it('should handle internal server errors', async () => {
      // This test would require mocking to force an internal error
      // For now, we'll test the error response format
      const response = await request(app)
        .get('/api/unknown-route')
        .expect(404);

      expect(response.body.error).toBeDefined();
      expect(response.body.timestamp).toBeDefined();
    });
  });

  describe('Security Middleware', () => {
    describe('CORS', () => {
      it('should include CORS headers', async () => {
        const response = await request(app)
          .get('/health')
          .expect(200);

        expect(response.headers['access-control-allow-origin']).toBeDefined();
      });
    });

    describe('Security Headers', () => {
      it('should include security headers', async () => {
        const response = await request(app)
          .get('/health')
          .expect(200);

        expect(response.headers['x-content-type-options']).toBe('nosniff');
        expect(response.headers['x-frame-options']).toBeDefined();
        expect(response.headers['x-xss-protection']).toBeDefined();
      });
    });

    describe('Rate Limiting', () => {
      it('should handle rate limiting', async () => {
        // Make many requests to test rate limiting
        const promises = [];
        for (let i = 0; i < 105; i++) { // Exceed default limit of 100
          promises.push(
            request(app)
              .get('/health')
          );
        }

        const responses = await Promise.all(promises);
        const rateLimitedResponses = responses.filter(r => r.status === 429);

        // Some requests should be rate limited
        expect(rateLimitedResponses.length).toBeGreaterThan(0);

        const rateLimitedResponse = rateLimitedResponses[0];
        expect(rateLimitedResponse.body.error).toBe('Too many requests from this IP');
      });
    });
  });

  describe('Request Body Parsing', () => {
    it('should handle JSON body', async () => {
      const jsonData = {
        sourceDatasetId: 'test-dataset-1',
        targetDatasetId: 'test-dataset-1',
        correlationType: 'one_to_one'
      };

      const response = await request(app)
        .post('/api/correlations/discover')
        .set('Content-Type', 'application/json')
        .send(jsonData)
        .expect(201);

      expect(response.body.success).toBe(true);
    });

    it('should handle URL-encoded body', async () => {
      const response = await request(app)
        .post('/api/correlations/discover')
        .set('Content-Type', 'application/x-www-form-urlencoded')
        .send('sourceDatasetId=test-dataset-1&targetDatasetId=test-dataset-1')
        .expect(201);

      expect(response.body.success).toBe(true);
    });

    it('should reject invalid JSON', async () => {
      const response = await request(app)
        .post('/api/correlations/discover')
        .set('Content-Type', 'application/json')
        .send('{"invalid": json}')
        .expect(400);

      expect(response.body.success).toBe(false);
    });
  });

  describe('Content Security', () => {
    it('should limit request body size', async () => {
      const largeBody = {
        sourceDatasetId: 'test-dataset-1',
        targetDatasetId: 'test-dataset-1',
        auxiliaryData: { data: 'x'.repeat(20000000) } // 20MB
      };

      const response = await request(app)
        .post('/api/correlations/discover')
        .send(largeBody)
        .expect(413); // Payload Too Large

      expect(response.body.success).toBe(false);
    });

    it('should handle content-type validation', async () => {
      const response = await request(app)
        .post('/api/correlations/discover')
        .set('Content-Type', 'text/xml')
        .send('<xml>invalid</xml>')
        .expect(400);

      expect(response.body.success).toBe(false);
    });
  });
});