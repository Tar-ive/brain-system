import request from 'supertest';
import app from '../../src/index';

describe('Health Endpoint Integration Tests', () => {
  describe('GET /health', () => {
    it('should return health status', async () => {
      const response = await request(app)
        .get('/health')
        .expect(200);

      expect(response.body.status).toBe('healthy');
      expect(response.body.timestamp).toBeDefined();
      expect(response.body.version).toBeDefined();
    });

    it('should return current timestamp', () => {
      const before = new Date().toISOString();

      return request(app)
        .get('/health')
        .expect(200)
        .then(response => {
          const timestamp = response.body.timestamp;
          expect(new Date(timestamp).getTime()).toBeGreaterThanOrEqual(new Date(before).getTime());
        });
    });

    it('should return correct version format', async () => {
      const response = await request(app)
        .get('/health')
        .expect(200);

      expect(response.body.version).toMatch(/^\d+\.\d+\.\d+$/);
    });

    it('should handle CORS headers', async () => {
      const response = await request(app)
        .get('/health')
        .expect(200);

      expect(response.headers['access-control-allow-origin']).toBeDefined();
      expect(response.headers['access-control-allow-methods']).toBeDefined();
      expect(response.headers['access-control-allow-headers']).toBeDefined();
    });

    it('should include security headers', async () => {
      const response = await request(app)
        .get('/health')
        .expect(200);

      expect(response.headers['x-content-type-options']).toBe('nosniff');
      expect(response.headers['x-frame-options']).toBeDefined();
      expect(response.headers['x-xss-protection']).toBeDefined();
      expect(response.headers['strict-transport-security']).toBeDefined();
    });

    it('should not be rate limited', async () => {
      // Make many requests to health endpoint
      const promises = [];
      for (let i = 0; i < 20; i++) {
        promises.push(
          request(app)
            .get('/health')
            .expect(200)
        );
      }

      const responses = await Promise.all(promises);
      responses.forEach(response => {
        expect(response.body.status).toBe('healthy');
      });
    });
  });

  describe('Health Endpoint with Different Methods', () => {
    it('should handle OPTIONS method', async () => {
      const response = await request(app)
        .options('/health')
        .expect(204);

      expect(response.headers['access-control-allow-methods']).toContain('GET');
      expect(response.headers['access-control-allow-methods']).toContain('OPTIONS');
    });

    it('should reject POST method', async () => {
      const response = await request(app)
        .post('/health')
        .expect(404);

      expect(response.body.error).toBe('Route not found');
      expect(response.body.method).toBe('POST');
      expect(response.body.path).toBe('/health');
    });

    it('should reject PUT method', async () => {
      const response = await request(app)
        .put('/health')
        .expect(404);

      expect(response.body.error).toBe('Route not found');
      expect(response.body.method).toBe('PUT');
      expect(response.body.path).toBe('/health');
    });

    it('should reject DELETE method', async () => {
      const response = await request(app)
        .delete('/health')
        .expect(404);

      expect(response.body.error).toBe('Route not found');
      expect(response.body.method).toBe('DELETE');
      expect(response.body.path).toBe('/health');
    });
  });

  describe('Health Endpoint with Headers', () => {
    it('should handle custom user agent', async () => {
      const response = await request(app)
        .get('/health')
        .set('User-Agent', 'Test-Agent/1.0')
        .expect(200);

      expect(response.body.status).toBe('healthy');
    });

    it('should handle custom headers', async () => {
      const response = await request(app)
        .get('/health')
        .set('X-Custom-Header', 'test-value')
        .set('Authorization', 'Bearer test-token')
        .expect(200);

      expect(response.body.status).toBe('healthy');
    });

    it('should handle request ID header', async () => {
      const response = await request(app)
        .get('/health')
        .set('X-Request-ID', 'test-request-id')
        .expect(200);

      expect(response.body.status).toBe('healthy');
    });
  });

  describe('Health Endpoint Performance', () => {
    it('should respond quickly', async () => {
      const startTime = process.hrtime.bigint();

      await request(app)
        .get('/health')
        .expect(200);

      const endTime = process.hrtime.bigint();
      const duration = Number(endTime - startTime) / 1000000; // Convert to milliseconds

      expect(duration).toBeLessThan(100); // Should respond within 100ms
    });

    it('should handle concurrent requests', async () => {
      const numRequests = 50;
      const promises = [];

      for (let i = 0; i < numRequests; i++) {
        promises.push(
          request(app)
            .get('/health')
            .expect(200)
        );
      }

      const startTime = process.hrtime.bigint();
      const responses = await Promise.all(promises);
      const endTime = process.hrtime.bigint();

      const totalDuration = Number(endTime - startTime) / 1000000;
      const avgDuration = totalDuration / numRequests;

      expect(responses.length).toBe(numRequests);
      responses.forEach(response => {
        expect(response.body.status).toBe('healthy');
      });

      expect(avgDuration).toBeLessThan(50); // Average should be under 50ms
    });
  });

  describe('Health Endpoint Edge Cases', () => {
    it('should handle query parameters', async () => {
      const response = await request(app)
        .get('/health?verbose=true&debug=false')
        .expect(200);

      expect(response.body.status).toBe('healthy');
    });

    it('should handle empty query parameters', async () => {
      const response = await request(app)
        .get('/health?')
        .expect(200);

      expect(response.body.status).toBe('healthy');
    });

    it('should handle malformed query parameters', async () => {
      const response = await request(app)
        .get('/health?malformed=value&another')
        .expect(200);

      expect(response.body.status).toBe('healthy');
    });
  });
});