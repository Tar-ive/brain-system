import request from 'supertest';
import app from '../../src/index';
import { CorrelationService } from '../../src/services/CorrelationService';
import { waitFor } from '../helpers/test-utils';

describe('Correlation Workflow End-to-End Tests', () => {
  let correlationService: CorrelationService;
  let authToken: string;

  beforeAll(async () => {
    correlationService = new CorrelationService();
  });

  describe('Complete Correlation Discovery Workflow', () => {
    let dataset1Id: string;
    let dataset2Id: string;
    let correlationId: string;

    it('should setup test datasets', async () => {
      // Create first dataset
      const dataset1Response = await request(app)
        .post('/api/datasets')
        .send({
          name: 'Customer Data',
          description: 'Customer information dataset',
          columns: ['customer_id', 'name', 'email', 'age', 'city'],
          rowCount: 5000,
          metadata: { source: 'CRM', year: 2023 }
        })
        .expect(201);

      expect(dataset1Response.body.success).toBe(true);
      dataset1Id = dataset1Response.body.data.id;

      // Create second dataset
      const dataset2Response = await request(app)
        .post('/api/datasets')
        .send({
          name: 'Order Data',
          description: 'Order transaction dataset',
          columns: ['order_id', 'customer_id', 'product_id', 'amount', 'date'],
          rowCount: 15000,
          metadata: { source: 'ERP', year: 2023 }
        })
        .expect(201);

      expect(dataset2Response.body.success).toBe(true);
      dataset2Id = dataset2Response.body.data.id;
    });

    it('should discover correlation between datasets', async () => {
      const correlationResponse = await request(app)
        .post('/api/correlations/discover')
        .send({
          sourceDatasetId: dataset1Id,
          targetDatasetId: dataset2Id,
          correlationType: 'one_to_many',
          parameters: {
            keyColumn: 'customer_id',
            joinType: 'left'
          }
        })
        .expect(201);

      expect(correlationResponse.body.success).toBe(true);
      correlationId = correlationResponse.body.data.id;

      // Verify correlation properties
      const correlation = correlationResponse.body.data;
      expect(correlation.sourceDatasetId).toBe(dataset1Id);
      expect(correlation.targetDatasetId).toBe(dataset2Id);
      expect(correlation.correlationType).toBe('one_to_many');
      expect(correlation.confidence).toBeGreaterThan(0.7);
      expect(correlation.parameters.keyColumn).toBe('customer_id');
    });

    it('should retrieve the discovered correlation', async () => {
      const getResponse = await request(app)
        .get(`/api/correlations/${correlationId}`)
        .expect(200);

      expect(getResponse.body.success).toBe(true);
      const correlation = getResponse.body.data;
      expect(correlation.id).toBe(correlationId);
      expect(correlation.sourceDatasetId).toBe(dataset1Id);
      expect(correlation.targetDatasetId).toBe(dataset2Id);
    });

    it('should validate the correlation', async () => {
      const validationResponse = await request(app)
        .post(`/api/correlations/${correlationId}/validate`)
        .expect(200);

      expect(validationResponse.body.success).toBe(true);
      const validation = validationResponse.body.data;
      expect(validation.correlationId).toBe(correlationId);
      expect(validation.validityScore).toBeGreaterThan(0.7);
      expect(validation.statisticalScore).toBeDefined();
      expect(validation.semanticScore).toBeDefined();
      expect(validation.structuralScore).toBeDefined();
      expect(validation.conservationError).toBeLessThan(0.05);
      expect(validation.testAccuracy).toBeGreaterThan(0.8);
    });

    it('should retrieve validation results', async () => {
      const getValidationResponse = await request(app)
        .get(`/api/correlations/${correlationId}/validation`)
        .expect(200);

      expect(getValidationResponse.body.success).toBe(true);
      const validation = getValidationResponse.body.data;
      expect(validation.correlationId).toBe(correlationId);
      expect(validation.validityScore).toBeDefined();
    });

    it('should list correlations with filters', async () => {
      const listResponse = await request(app)
        .get('/api/correlations')
        .query({
          sourceDatasetId: dataset1Id,
          targetDatasetId: dataset2Id,
          correlationType: 'one_to_many',
          minConfidence: 0.8
        })
        .expect(200);

      expect(listResponse.body.success).toBe(true);
      const { data, pagination } = listResponse.body;
      expect(data.length).toBeGreaterThan(0);
      expect(pagination.total).toBeGreaterThan(0);

      // Verify all correlations match filters
      data.forEach((correlation: any) => {
        expect(correlation.sourceDatasetId).toBe(dataset1Id);
        expect(correlation.targetDatasetId).toBe(dataset2Id);
        expect(correlation.correlationType).toBe('one_to_many');
        expect(correlation.confidence).toBeGreaterThanOrEqual(0.8);
      });
    });

    it('should get system statistics', async () => {
      const statsResponse = await request(app)
        .get('/api/correlations/statistics')
        .expect(200);

      expect(statsResponse.body.success).toBe(true);
      const stats = statsResponse.body.data;
      expect(stats.totalCorrelations).toBeGreaterThan(0);
      expect(stats.totalValidations).toBeGreaterThan(0);
      expect(stats.averageConfidence).toBeGreaterThan(0);
      expect(stats.correlationTypes).toBeDefined();
      expect(typeof stats.correlationTypes).toBe('object');
    });

    it('should verify datasets exist', async () => {
      const dataset1Response = await request(app)
        .get(`/api/datasets/${dataset1Id}`)
        .expect(200);

      expect(dataset1Response.body.success).toBe(true);
      expect(dataset1Response.body.data.id).toBe(dataset1Id);
      expect(dataset1Response.body.data.name).toBe('Customer Data');

      const dataset2Response = await request(app)
        .get(`/api/datasets/${dataset2Id}`)
        .expect(200);

      expect(dataset2Response.body.success).toBe(true);
      expect(dataset2Response.body.data.id).toBe(dataset2Id);
      expect(dataset2Response.body.data.name).toBe('Order Data');
    });

    it('should list all datasets', async () => {
      const datasetsResponse = await request(app)
        .get('/api/datasets')
        .expect(200);

      expect(datasetsResponse.body.success).toBe(true);
      const datasets = datasetsResponse.body.data;
      expect(datasets.length).toBeGreaterThan(0);

      // Verify our test datasets are in the list
      const datasetIds = datasets.map((d: any) => d.id);
      expect(datasetIds).toContain(dataset1Id);
      expect(datasetIds).toContain(dataset2Id);
    });
  });

  describe('Multiple Correlations Workflow', () => {
    let customerDatasetId: string;
    let productDatasetId: string;
    let orderDatasetId: string;
    let correlations: string[] = [];

    it('should setup multiple datasets', async () => {
      // Customer dataset
      const customerResponse = await request(app)
        .post('/api/datasets')
        .send({
          name: 'Customers',
          description: 'Customer master data',
          columns: ['customer_id', 'name', 'segment', 'region'],
          rowCount: 1000
        })
        .expect(201);

      customerDatasetId = customerResponse.body.data.id;

      // Product dataset
      const productResponse = await request(app)
        .post('/api/datasets')
        .send({
          name: 'Products',
          description: 'Product catalog',
          columns: ['product_id', 'name', 'category', 'price'],
          rowCount: 500
        })
        .expect(201);

      productDatasetId = productResponse.body.data.id;

      // Order dataset
      const orderResponse = await request(app)
        .post('/api/datasets')
        .send({
          name: 'Orders',
          description: 'Sales orders',
          columns: ['order_id', 'customer_id', 'product_id', 'quantity', 'date'],
          rowCount: 10000
        })
        .expect(201);

      orderDatasetId = orderResponse.body.data.id;
    });

    it('should discover multiple correlations', async () => {
      // Customer to Orders correlation
      const customerOrderResponse = await request(app)
        .post('/api/correlations/discover')
        .send({
          sourceDatasetId: customerDatasetId,
          targetDatasetId: orderDatasetId,
          correlationType: 'one_to_many',
          parameters: {
            keyColumn: 'customer_id',
            joinType: 'left'
          }
        })
        .expect(201);

      correlations.push(customerOrderResponse.body.data.id);

      // Product to Orders correlation
      const productOrderResponse = await request(app)
        .post('/api/correlations/discover')
        .send({
          sourceDatasetId: productDatasetId,
          targetDatasetId: orderDatasetId,
          correlationType: 'one_to_many',
          parameters: {
            keyColumn: 'product_id',
            joinType: 'left'
          }
        })
        .expect(201);

      correlations.push(productOrderResponse.body.data.id);

      // Customer to Product temporal correlation
      const temporalResponse = await request(app)
        .post('/api/correlations/discover')
        .send({
          sourceDatasetId: customerDatasetId,
          targetDatasetId: productDatasetId,
          correlationType: 'temporal',
          parameters: {
            lagDays: 30,
            aggregation: 'count'
          }
        })
        .expect(201);

      correlations.push(temporalResponse.body.data.id);

      expect(correlations.length).toBe(3);
    });

    it('should validate all correlations', async () => {
      for (const correlationId of correlations) {
        const validationResponse = await request(app)
          .post(`/api/correlations/${correlationId}/validate`)
          .expect(200);

        expect(validationResponse.body.success).toBe(true);
        const validation = validationResponse.body.data;
        expect(validation.validityScore).toBeGreaterThan(0.7);
      }
    });

    it('should retrieve all correlations for a dataset', async () => {
      const customerCorrelationsResponse = await request(app)
        .get('/api/correlations')
        .query({ sourceDatasetId: customerDatasetId })
        .expect(200);

      expect(customerCorrelationsResponse.body.success).toBe(true);
      const customerCorrelations = customerCorrelationsResponse.body.data;
      expect(customerCorrelations.length).toBe(2); // customer->orders, customer->products
    });

    it('should get comprehensive statistics', async () => {
      const statsResponse = await request(app)
        .get('/api/correlations/statistics')
        .expect(200);

      expect(statsResponse.body.success).toBe(true);
      const stats = statsResponse.body.data;
      expect(stats.totalCorrelations).toBeGreaterThanOrEqual(3);
      expect(stats.correlationTypes.one_to_many).toBeGreaterThan(0);
      expect(stats.correlationTypes.temporal).toBeGreaterThan(0);
    });
  });

  describe('Error Handling Workflow', () => {
    it('should handle correlation discovery with invalid datasets', async () => {
      const response = await request(app)
        .post('/api/correlations/discover')
        .send({
          sourceDatasetId: 'invalid-dataset',
          targetDatasetId: 'another-invalid-dataset'
        })
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('Source or target dataset not found');
    });

    it('should handle correlation retrieval with invalid ID', async () => {
      const response = await request(app)
        .get('/api/correlations/invalid-correlation-id')
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('Correlation not found');
    });

    it('should handle validation of non-existent correlation', async () => {
      const response = await request(app)
        .post('/api/correlations/invalid-correlation-id/validate')
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('Correlation not found');
    });

    it('should handle dataset retrieval with invalid ID', async () => {
      const response = await request(app)
        .get('/api/datasets/invalid-dataset-id')
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('Dataset not found');
    });
  });

  describe('Performance Workflow', () => {
    it('should handle multiple concurrent correlation discoveries', async () => {
      // Create test dataset
      const datasetResponse = await request(app)
        .post('/api/datasets')
        .send({
          name: 'Performance Test Dataset',
          description: 'Dataset for performance testing',
          columns: ['id', 'value', 'category'],
          rowCount: 100000
        })
        .expect(201);

      const datasetId = datasetResponse.body.data.id;

      // Create multiple correlation discovery requests concurrently
      const promises = [];
      for (let i = 0; i < 10; i++) {
        promises.push(
          request(app)
            .post('/api/correlations/discover')
            .send({
              sourceDatasetId: datasetId,
              targetDatasetId: datasetId,
              correlationType: 'one_to_one'
            })
        );
      }

      const startTime = Date.now();
      const responses = await Promise.all(promises);
      const endTime = Date.now();

      // All requests should succeed
      responses.forEach(response => {
        expect(response.status).toBe(201);
        expect(response.body.success).toBe(true);
      });

      // Should complete within reasonable time
      expect(endTime - startTime).toBeLessThan(5000);
    });

    it('should handle pagination with large datasets', async () => {
      // Create many correlations
      const datasetResponse = await request(app)
        .post('/api/datasets')
        .send({
          name: 'Large Test Dataset',
          description: 'Dataset for pagination testing',
          columns: ['id', 'data'],
          rowCount: 1000
        })
        .expect(201);

      const datasetId = datasetResponse.body.data.id;

      // Create 25 correlations
      const correlationIds = [];
      for (let i = 0; i < 25; i++) {
        const response = await request(app)
          .post('/api/correlations/discover')
          .send({
            sourceDatasetId: datasetId,
            targetDatasetId: datasetId,
            correlationType: 'one_to_one'
          })
          .expect(201);

        correlationIds.push(response.body.data.id);
      }

      // Test pagination
      const page1Response = await request(app)
        .get('/api/correlations')
        .query({ sourceDatasetId: datasetId, limit: 10, offset: 0 })
        .expect(200);

      expect(page1Response.body.success).toBe(true);
      expect(page1Response.body.data.length).toBe(10);
      expect(page1Response.body.pagination.total).toBe(25);
      expect(page1Response.body.pagination.limit).toBe(10);
      expect(page1Response.body.pagination.offset).toBe(0);

      const page2Response = await request(app)
        .get('/api/correlations')
        .query({ sourceDatasetId: datasetId, limit: 10, offset: 10 })
        .expect(200);

      expect(page2Response.body.success).toBe(true);
      expect(page2Response.body.data.length).toBe(10);
      expect(page2Response.body.pagination.total).toBe(25);
      expect(page2Response.body.pagination.offset).toBe(10);

      const page3Response = await request(app)
        .get('/api/correlations')
        .query({ sourceDatasetId: datasetId, limit: 10, offset: 20 })
        .expect(200);

      expect(page3Response.body.success).toBe(true);
      expect(page3Response.body.data.length).toBe(5);
      expect(page3Response.body.pagination.total).toBe(25);
      expect(page3Response.body.pagination.offset).toBe(20);

      // Verify no duplicates across pages
      const allIds = [
        ...page1Response.body.data.map((c: any) => c.id),
        ...page2Response.body.data.map((c: any) => c.id),
        ...page3Response.body.data.map((c: any) => c.id)
      ];

      expect(new Set(allIds).size).toBe(25);
    });
  });

  describe('Cleanup Workflow', () => {
    let testCorrelationId: string;

    it('should create test correlation for cleanup', async () => {
      const datasetResponse = await request(app)
        .post('/api/datasets')
        .send({
          name: 'Cleanup Test Dataset',
          description: 'Dataset for cleanup testing',
          columns: ['id', 'data'],
          rowCount: 100
        })
        .expect(201);

      const datasetId = datasetResponse.body.data.id;

      const correlationResponse = await request(app)
        .post('/api/correlations/discover')
        .send({
          sourceDatasetId: datasetId,
          targetDatasetId: datasetId,
          correlationType: 'one_to_one'
        })
        .expect(201);

      testCorrelationId = correlationResponse.body.data.id;
    });

    it('should delete correlation', async () => {
      const deleteResponse = await request(app)
        .delete(`/api/correlations/${testCorrelationId}`)
        .expect(200);

      expect(deleteResponse.body.success).toBe(true);
      expect(deleteResponse.body.message).toBe('Correlation deleted successfully');
    });

    it('should verify correlation is deleted', async () => {
      const getResponse = await request(app)
        .get(`/api/correlations/${testCorrelationId}`)
        .expect(404);

      expect(getResponse.body.success).toBe(false);
      expect(getResponse.body.error).toBe('Correlation not found');
    });

    it('should handle deletion of non-existent correlation', async () => {
      const response = await request(app)
        .delete('/api/correlations/non-existent-id')
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('Correlation not found');
    });
  });
});