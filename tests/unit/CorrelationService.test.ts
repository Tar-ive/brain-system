import { CorrelationService } from '../../src/services/CorrelationService';
import {
  generateTestCorrelation,
  generateTestDataset,
  generateTestValidation,
  generateLargeDataset,
  waitFor
} from '../helpers/test-utils';
import { CorrelationType } from '../../src/models/Correlation';

describe('CorrelationService', () => {
  let correlationService: CorrelationService;

  beforeEach(() => {
    correlationService = new CorrelationService();
  });

  describe('discoverCorrelation', () => {
    it('should discover correlation successfully with valid datasets', async () => {
      // Setup test datasets
      const sourceDataset = generateTestDataset({ id: 'source-1' });
      const targetDataset = generateTestDataset({ id: 'target-1' });

      await correlationService.addDataset(sourceDataset);
      await correlationService.addDataset(targetDataset);

      const correlation = await correlationService.discoverCorrelation(
        'source-1',
        'target-1',
        {
          correlationType: 'one_to_one',
          parameters: { keyColumn: 'id' }
        }
      );

      expect(correlation).toBeDefined();
      expect(correlation.sourceDatasetId).toBe('source-1');
      expect(correlation.targetDatasetId).toBe('target-1');
      expect(correlation.correlationType).toBe('one_to_one');
      expect(correlation.confidence).toBeGreaterThanOrEqual(0.7);
      expect(correlation.confidence).toBeLessThanOrEqual(1.0);
      expect(correlation.discoveredAt).toBeDefined();
    });

    it('should throw error when source dataset does not exist', async () => {
      const targetDataset = generateTestDataset({ id: 'target-1' });
      await correlationService.addDataset(targetDataset);

      await expect(
        correlationService.discoverCorrelation('non-existent', 'target-1')
      ).rejects.toThrow('Source or target dataset not found');
    });

    it('should throw error when target dataset does not exist', async () => {
      const sourceDataset = generateTestDataset({ id: 'source-1' });
      await correlationService.addDataset(sourceDataset);

      await expect(
        correlationService.discoverCorrelation('source-1', 'non-existent')
      ).rejects.toThrow('Source or target dataset not found');
    });

    it('should use default correlation type when not specified', async () => {
      const sourceDataset = generateTestDataset({ id: 'source-1' });
      const targetDataset = generateTestDataset({ id: 'target-1' });

      await correlationService.addDataset(sourceDataset);
      await correlationService.addDataset(targetDataset);

      const correlation = await correlationService.discoverCorrelation(
        'source-1',
        'target-1'
      );

      expect(correlation.correlationType).toBe('one_to_one');
    });

    it('should automatically validate discovered correlation', async () => {
      const sourceDataset = generateTestDataset({ id: 'source-1' });
      const targetDataset = generateTestDataset({ id: 'target-1' });

      await correlationService.addDataset(sourceDataset);
      await correlationService.addDataset(targetDataset);

      const correlation = await correlationService.discoverCorrelation(
        'source-1',
        'target-1'
      );

      const validation = await correlationService.getValidation(correlation.id);
      expect(validation).toBeDefined();
      expect(validation?.correlationId).toBe(correlation.id);
      expect(validation?.validityScore).toBeGreaterThanOrEqual(0.7);
    });

    it('should handle auxiliary data parameter', async () => {
      const sourceDataset = generateTestDataset({ id: 'source-1' });
      const targetDataset = generateTestDataset({ id: 'target-1' });
      const auxiliaryData = { weights: [0.5, 0.3, 0.2] };

      await correlationService.addDataset(sourceDataset);
      await correlationService.addDataset(targetDataset);

      const correlation = await correlationService.discoverCorrelation(
        'source-1',
        'target-1',
        { auxiliaryData }
      );

      expect(correlation).toBeDefined();
    });
  });

  describe('validateCorrelation', () => {
    it('should validate existing correlation successfully', async () => {
      // Setup correlation
      const correlation = generateTestCorrelation();
      const correlationMap = (correlationService as any).correlations as Map<string, any>;
      correlationMap.set(correlation.id, correlation);

      const validation = await correlationService.validateCorrelation(correlation.id);

      expect(validation).toBeDefined();
      expect(validation.correlationId).toBe(correlation.id);
      expect(validation.validityScore).toBeGreaterThanOrEqual(0.7);
      expect(validation.validityScore).toBeLessThanOrEqual(1.0);
      expect(validation.statisticalScore).toBeDefined();
      expect(validation.semanticScore).toBeDefined();
      expect(validation.structuralScore).toBeDefined();
      expect(validation.conservationError).toBeGreaterThanOrEqual(0);
      expect(validation.conservationError).toBeLessThanOrEqual(0.05);
      expect(validation.testAccuracy).toBeGreaterThanOrEqual(0.8);
      expect(validation.testAccuracy).toBeLessThanOrEqual(1.0);
    });

    it('should throw error when correlation does not exist', async () => {
      await expect(
        correlationService.validateCorrelation('non-existent')
      ).rejects.toThrow('Correlation not found');
    });

    it('should store validation result', async () => {
      const correlation = generateTestCorrelation();
      const correlationMap = (correlationService as any).correlations as Map<string, any>;
      correlationMap.set(correlation.id, correlation);

      const validation = await correlationService.validateCorrelation(correlation.id);
      const validationMap = (correlationService as any).validations as Map<string, any>;

      expect(validationMap.has(validation.id)).toBe(true);
    });
  });

  describe('getCorrelation', () => {
    it('should return existing correlation', async () => {
      const correlation = generateTestCorrelation();
      const correlationMap = (correlationService as any).correlations as Map<string, any>;
      correlationMap.set(correlation.id, correlation);

      const result = await correlationService.getCorrelation(correlation.id);

      expect(result).toEqual(correlation);
    });

    it('should return null for non-existent correlation', async () => {
      const result = await correlationService.getCorrelation('non-existent');

      expect(result).toBeNull();
    });
  });

  describe('getCorrelations', () => {
    beforeEach(async () => {
      // Add test correlations
      const correlationMap = (correlationService as any).correlations as Map<string, any>;

      for (let i = 0; i < 15; i++) {
        const correlation = generateTestCorrelation({
          sourceDatasetId: `source-${i % 3}`,
          targetDatasetId: `target-${i % 3}`,
          correlationType: ['one_to_one', 'many_to_many', 'temporal'][i % 3] as CorrelationType,
          confidence: 0.6 + (i * 0.03)
        });
        correlationMap.set(correlation.id, correlation);
      }
    });

    it('should return all correlations without filters', async () => {
      const result = await correlationService.getCorrelations();

      expect(result.correlations.length).toBe(10); // Default limit
      expect(result.total).toBe(15);
    });

    it('should filter by source dataset', async () => {
      const result = await correlationService.getCorrelations({
        sourceDatasetId: 'source-0'
      });

      expect(result.correlations.length).toBe(5); // source-0 has 5 correlations
      expect(result.total).toBe(5);
      result.correlations.forEach(c => {
        expect(c.sourceDatasetId).toBe('source-0');
      });
    });

    it('should filter by target dataset', async () => {
      const result = await correlationService.getCorrelations({
        targetDatasetId: 'target-1'
      });

      expect(result.correlations.length).toBe(5);
      expect(result.total).toBe(5);
      result.correlations.forEach(c => {
        expect(c.targetDatasetId).toBe('target-1');
      });
    });

    it('should filter by correlation type', async () => {
      const result = await correlationService.getCorrelations({
        correlationType: 'one_to_one'
      });

      expect(result.correlations.length).toBe(5);
      expect(result.total).toBe(5);
      result.correlations.forEach(c => {
        expect(c.correlationType).toBe('one_to_one');
      });
    });

    it('should filter by minimum confidence', async () => {
      const result = await correlationService.getCorrelations({
        minConfidence: 0.8
      });

      expect(result.correlations.length).toBeGreaterThan(0);
      result.correlations.forEach(c => {
        expect(c.confidence).toBeGreaterThanOrEqual(0.8);
      });
    });

    it('should handle pagination', async () => {
      const result1 = await correlationService.getCorrelations({ limit: 5, offset: 0 });
      const result2 = await correlationService.getCorrelations({ limit: 5, offset: 5 });

      expect(result1.correlations.length).toBe(5);
      expect(result2.correlations.length).toBe(5);
      expect(result1.correlations[0].id).not.toBe(result2.correlations[0].id);
    });

    it('should return empty array when no correlations match filters', async () => {
      const result = await correlationService.getCorrelations({
        sourceDatasetId: 'non-existent'
      });

      expect(result.correlations).toHaveLength(0);
      expect(result.total).toBe(0);
    });
  });

  describe('getValidation', () => {
    it('should return validation for existing correlation', async () => {
      const correlation = generateTestCorrelation();
      const correlationMap = (correlationService as any).correlations as Map<string, any>;
      correlationMap.set(correlation.id, correlation);

      const validation = generateTestValidation({ correlationId: correlation.id });
      const validationMap = (correlationService as any).validations as Map<string, any>;
      validationMap.set(validation.id, validation);

      const result = await correlationService.getValidation(correlation.id);

      expect(result).toEqual(validation);
    });

    it('should return null when no validation exists', async () => {
      const correlation = generateTestCorrelation();
      const correlationMap = (correlationService as any).correlations as Map<string, any>;
      correlationMap.set(correlation.id, correlation);

      const result = await correlationService.getValidation(correlation.id);

      expect(result).toBeNull();
    });

    it('should return null when correlation does not exist', async () => {
      const result = await correlationService.getValidation('non-existent');

      expect(result).toBeNull();
    });
  });

  describe('Dataset Management', () => {
    it('should add dataset successfully', async () => {
      const dataset = generateTestDataset();

      const result = await correlationService.addDataset(dataset);

      expect(result).toEqual(dataset);
    });

    it('should retrieve dataset by ID', async () => {
      const dataset = generateTestDataset();
      await correlationService.addDataset(dataset);

      const result = await correlationService.getDataset(dataset.id);

      expect(result).toEqual(dataset);
    });

    it('should return null for non-existent dataset', async () => {
      const result = await correlationService.getDataset('non-existent');

      expect(result).toBeNull();
    });

    it('should return all datasets', async () => {
      const datasets = [
        generateTestDataset({ id: 'dataset-1' }),
        generateTestDataset({ id: 'dataset-2' }),
        generateTestDataset({ id: 'dataset-3' })
      ];

      for (const dataset of datasets) {
        await correlationService.addDataset(dataset);
      }

      const result = await correlationService.getDatasets();

      expect(result.length).toBe(3);
      expect(result).toEqual(expect.arrayContaining(datasets));
    });
  });

  describe('deleteCorrelation', () => {
    it('should delete existing correlation', async () => {
      const correlation = generateTestCorrelation();
      const correlationMap = (correlationService as any).correlations as Map<string, any>;
      correlationMap.set(correlation.id, correlation);

      // Add validation
      const validation = generateTestValidation({ correlationId: correlation.id });
      const validationMap = (correlationService as any).validations as Map<string, any>;
      validationMap.set(validation.id, validation);

      const result = await correlationService.deleteCorrelation(correlation.id);

      expect(result).toBe(true);
      expect(correlationMap.has(correlation.id)).toBe(false);
      expect(validationMap.has(validation.id)).toBe(false);
    });

    it('should return false for non-existent correlation', async () => {
      const result = await correlationService.deleteCorrelation('non-existent');

      expect(result).toBe(false);
    });
  });

  describe('getStatistics', () => {
    beforeEach(async () => {
      // Add test data
      const correlationMap = (correlationService as any).correlations as Map<string, any>;
      const validationMap = (correlationService as any).validations as Map<string, any>;

      // Add correlations
      for (let i = 0; i < 10; i++) {
        const correlation = generateTestCorrelation({
          confidence: 0.7 + (i * 0.03),
          correlationType: ['one_to_one', 'many_to_many', 'temporal'][i % 3] as CorrelationType
        });
        correlationMap.set(correlation.id, correlation);

        // Add validation
        const validation = generateTestValidation({ correlationId: correlation.id });
        validationMap.set(validation.id, validation);
      }
    });

    it('should return correct statistics', async () => {
      const stats = await correlationService.getStatistics();

      expect(stats.totalCorrelations).toBe(10);
      expect(stats.totalValidations).toBe(10);
      expect(stats.averageConfidence).toBeGreaterThan(0.7);
      expect(stats.averageConfidence).toBeLessThan(1.0);
      expect(stats.correlationTypes).toEqual({
        one_to_one: 4,
        many_to_many: 3,
        temporal: 3
      });
    });

    it('should handle empty statistics', async () => {
      // Clear correlations
      const correlationMap = (correlationService as any).correlations as Map<string, any>;
      correlationMap.clear();

      const stats = await correlationService.getStatistics();

      expect(stats.totalCorrelations).toBe(0);
      expect(stats.totalValidations).toBe(0);
      expect(stats.averageConfidence).toBe(0);
      expect(stats.correlationTypes).toEqual({});
    });
  });

  describe('Performance Tests', () => {
    it('should handle large number of correlations efficiently', async () => {
      const correlationMap = (correlationService as any).correlations as Map<string, any>;
      const startTime = Date.now();

      // Add 1000 correlations
      for (let i = 0; i < 1000; i++) {
        const correlation = generateTestCorrelation({
          sourceDatasetId: `source-${i % 10}`,
          targetDatasetId: `target-${i % 10}`,
          confidence: Math.random()
        });
        correlationMap.set(correlation.id, correlation);
      }

      const addTime = Date.now() - startTime;
      expect(addTime).toBeLessThan(100); // Should be fast

      // Test retrieval performance
      const queryStartTime = Date.now();
      const result = await correlationService.getCorrelations({
        sourceDatasetId: 'source-0',
        limit: 100
      });
      const queryTime = Date.now() - queryStartTime;

      expect(queryTime).toBeLessThan(50); // Should be fast
      expect(result.correlations.length).toBe(100);
    });

    it('should handle concurrent requests', async () => {
      const sourceDataset = generateTestDataset({ id: 'source-1' });
      const targetDataset = generateTestDataset({ id: 'target-1' });

      await correlationService.addDataset(sourceDataset);
      await correlationService.addDataset(targetDataset);

      // Create 50 concurrent discovery requests
      const promises = [];
      for (let i = 0; i < 50; i++) {
        promises.push(
          correlationService.discoverCorrelation('source-1', 'target-1')
        );
      }

      const startTime = Date.now();
      const results = await Promise.all(promises);
      const endTime = Date.now();

      expect(endTime - startTime).toBeLessThan(1000); // Should complete within 1 second
      expect(results.length).toBe(50);
      results.forEach(result => {
        expect(result).toBeDefined();
        expect(result.sourceDatasetId).toBe('source-1');
        expect(result.targetDatasetId).toBe('target-1');
      });
    });
  });
});