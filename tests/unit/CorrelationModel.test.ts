import { CorrelationModel, CorrelationType } from '../../src/models/Correlation';
import { generateTestCorrelation } from '../helpers/test-utils';

describe('CorrelationModel', () => {
  describe('create', () => {
    it('should create correlation with all required fields', () => {
      const data = {
        sourceDatasetId: 'source-1',
        targetDatasetId: 'target-1',
        correlationType: 'one_to_one' as CorrelationType,
        parameters: { keyColumn: 'id' },
        confidence: 0.95
      };

      const correlation = CorrelationModel.create(data);

      expect(correlation.id).toBeDefined();
      expect(correlation.sourceDatasetId).toBe('source-1');
      expect(correlation.targetDatasetId).toBe('target-1');
      expect(correlation.correlationType).toBe('one_to_one');
      expect(correlation.parameters).toEqual({ keyColumn: 'id' });
      expect(correlation.confidence).toBe(0.95);
      expect(correlation.discoveredAt).toBeDefined();
      expect(correlation.version).toBe(1);
    });

    it('should generate UUID when ID not provided', () => {
      const data = {
        sourceDatasetId: 'source-1',
        targetDatasetId: 'target-1',
        correlationType: 'one_to_one' as CorrelationType
      };

      const correlation = CorrelationModel.create(data);

      expect(correlation.id).toBeDefined();
      expect(correlation.id).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/);
    });

    it('should use provided ID when available', () => {
      const data = {
        id: 'custom-id',
        sourceDatasetId: 'source-1',
        targetDatasetId: 'target-1',
        correlationType: 'one_to_one' as CorrelationType
      };

      const correlation = CorrelationModel.create(data);

      expect(correlation.id).toBe('custom-id');
    });

    it('should set default values for optional fields', () => {
      const data = {
        sourceDatasetId: 'source-1',
        targetDatasetId: 'target-1',
        correlationType: 'one_to_one' as CorrelationType
      };

      const correlation = CorrelationModel.create(data);

      expect(correlation.confidence).toBe(0);
      expect(correlation.parameters).toEqual({});
      expect(correlation.version).toBe(1);
      expect(correlation.discoveredAt).toBeDefined();
    });

    it('should set default correlation type', () => {
      const data = {
        sourceDatasetId: 'source-1',
        targetDatasetId: 'target-1'
      };

      const correlation = CorrelationModel.create(data);

      expect(correlation.correlationType).toBe('one_to_one');
    });
  });

  describe('validate', () => {
    it('should return empty array for valid correlation', () => {
      const correlation = generateTestCorrelation();

      const errors = CorrelationModel.validate(correlation);

      expect(errors).toHaveLength(0);
    });

    it('should return error when source dataset ID is missing', () => {
      const correlation = generateTestCorrelation();
      delete correlation.sourceDatasetId;

      const errors = CorrelationModel.validate(correlation);

      expect(errors).toContain('Source dataset ID is required');
    });

    it('should return error when target dataset ID is missing', () => {
      const correlation = generateTestCorrelation();
      delete correlation.targetDatasetId;

      const errors = CorrelationModel.validate(correlation);

      expect(errors).toContain('Target dataset ID is required');
    });

    it('should return error when correlation type is missing', () => {
      const correlation = generateTestCorrelation();
      delete correlation.correlationType;

      const errors = CorrelationModel.validate(correlation);

      expect(errors).toContain('Correlation type is required');
    });

    it('should return error when confidence is not a number', () => {
      const correlation = generateTestCorrelation();
      correlation.confidence = 'invalid' as any;

      const errors = CorrelationModel.validate(correlation);

      expect(errors).toContain('Confidence must be a number between 0 and 1');
    });

    it('should return error when confidence is less than 0', () => {
      const correlation = generateTestCorrelation();
      correlation.confidence = -0.1;

      const errors = CorrelationModel.validate(correlation);

      expect(errors).toContain('Confidence must be a number between 0 and 1');
    });

    it('should return error when confidence is greater than 1', () => {
      const correlation = generateTestCorrelation();
      correlation.confidence = 1.1;

      const errors = CorrelationModel.validate(correlation);

      expect(errors).toContain('Confidence must be a number between 0 and 1');
    });

    it('should return multiple errors for multiple validation failures', () => {
      const correlation = {
        confidence: 1.5
      };

      const errors = CorrelationModel.validate(correlation);

      expect(errors.length).toBeGreaterThan(1);
      expect(errors).toContain('Source dataset ID is required');
      expect(errors).toContain('Target dataset ID is required');
      expect(errors).toContain('Correlation type is required');
      expect(errors).toContain('Confidence must be a number between 0 and 1');
    });

    it('should handle null and undefined values', () => {
      const correlation = null;

      const errors = CorrelationModel.validate(correlation as any);

      expect(errors.length).toBeGreaterThan(0);
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty string for dataset IDs', () => {
      const correlation = generateTestCorrelation();
      correlation.sourceDatasetId = '';
      correlation.targetDatasetId = '';

      const errors = CorrelationModel.validate(correlation);

      expect(errors).toContain('Source dataset ID is required');
      expect(errors).toContain('Target dataset ID is required');
    });

    it('should handle NaN confidence value', () => {
      const correlation = generateTestCorrelation();
      correlation.confidence = NaN;

      const errors = CorrelationModel.validate(correlation);

      expect(errors).toContain('Confidence must be a number between 0 and 1');
    });

    it('should handle infinity confidence value', () => {
      const correlation = generateTestCorrelation();
      correlation.confidence = Infinity;

      const errors = CorrelationModel.validate(correlation);

      expect(errors).toContain('Confidence must be a number between 0 and 1');
    });

    it('should handle confidence exactly at boundaries', () => {
      let correlation = generateTestCorrelation();
      correlation.confidence = 0;
      let errors = CorrelationModel.validate(correlation);
      expect(errors).not.toContain('Confidence must be a number between 0 and 1');

      correlation = generateTestCorrelation();
      correlation.confidence = 1;
      errors = CorrelationModel.validate(correlation);
      expect(errors).not.toContain('Confidence must be a number between 0 and 1');
    });

    it('should handle correlation type case sensitivity', () => {
      const correlation = generateTestCorrelation();
      correlation.correlationType = 'One_To_One' as CorrelationType;

      // Validation should not fail on case, but the type check is structural
      const errors = CorrelationModel.validate(correlation);
      expect(errors).toHaveLength(0);
    });
  });
});