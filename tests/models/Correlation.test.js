const { expect } = require('chai');
const { v4: uuidv4 } = require('uuid');
const Correlation = require('../../src/models/Correlation');
const ValidationUtils = require('../../src/utils/validation');

describe('Correlation Model', () => {
  let sourceDatasetId, targetDatasetId;
  let validCorrelationData;

  beforeEach(() => {
    sourceDatasetId = uuidv4();
    targetDatasetId = uuidv4();

    validCorrelationData = {
      sourceDatasetId,
      targetDatasetId,
      type: 'one_to_many',
      parameters: {
        strength: 0.85,
        direction: 'positive',
        lag: 2
      },
      confidence: 0.85,
      validityScore: 0.78,
      description: 'Test correlation between datasets',
      status: 'validated',
      discoveryMethod: 'neural_network',
      tags: ['test', 'correlation']
    };
  });

  describe('Constructor', () => {
    it('should create a correlation with valid data', () => {
      const correlation = new Correlation(validCorrelationData);

      expect(correlation).to.be.an('object');
      expect(correlation.sourceDatasetId).to.equal(sourceDatasetId);
      expect(correlation.targetDatasetId).to.equal(targetDatasetId);
      expect(correlation.type).to.equal('one_to_many');
      expect(correlation.confidence).to.equal(0.85);
      expect(correlation.validityScore).to.equal(0.78);
      expect(correlation.id).to.be.a('string');
      expect(correlation.createdAt).to.be.a('string');
      expect(correlation.updatedAt).to.be.a('string');
    });

    it('should generate UUID if not provided', () => {
      const correlation = new Correlation({ sourceDatasetId, targetDatasetId, type: 'one_to_one' });
      expect(correlation.id).to.be.a('string');
      expect(correlation.id).to.match(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    });

    it('should set default values', () => {
      const correlation = new Correlation({ sourceDatasetId, targetDatasetId, type: 'one_to_one' });
      expect(correlation.status).to.equal('proposed');
      expect(correlation.confidence).to.equal(0);
      expect(correlation.validityScore).to.equal(0);
      expect(correlation.parameters).to.deep.equal({});
      expect(correlation.metadata).to.deep.equal({});
      expect(correlation.tags).to.deep.equal([]);
      expect(correlation.version).to.equal(1);
    });

    it('should use provided ID if given', () => {
      const customId = uuidv4();
      const correlation = new Correlation({ id: customId, sourceDatasetId, targetDatasetId, type: 'one_to_one' });
      expect(correlation.id).to.equal(customId);
    });
  });

  describe('Validation', () => {
    it('should validate a correct correlation', () => {
      const correlation = new Correlation(validCorrelationData);
      expect(() => correlation.validate()).to.not.throw();
    });

    it('should throw error for missing sourceDatasetId', () => {
      const invalidData = { ...validCorrelationData };
      delete invalidData.sourceDatasetId;
      const correlation = new Correlation(invalidData);

      expect(() => correlation.validate()).to.throw('Correlation validation failed: "sourceDatasetId" is required');
    });

    it('should throw error for missing targetDatasetId', () => {
      const invalidData = { ...validCorrelationData };
      delete invalidData.targetDatasetId;
      const correlation = new Correlation(invalidData);

      expect(() => correlation.validate()).to.throw('Correlation validation failed: "targetDatasetId" is required');
    });

    it('should throw error for missing type', () => {
      const invalidData = { ...validCorrelationData };
      delete invalidData.type;
      const correlation = new Correlation(invalidData);

      expect(() => correlation.validate()).to.throw('Correlation validation failed: "type" is required');
    });

    it('should throw error for invalid type', () => {
      const invalidData = { ...validCorrelationData, type: 'invalid_type' };
      const correlation = new Correlation(invalidData);

      expect(() => correlation.validate()).to.throw('Correlation validation failed: "type" must be one of');
    });

    it('should throw error for invalid confidence range', () => {
      const invalidData = { ...validCorrelationData, confidence: 1.5 };
      const correlation = new Correlation(invalidData);

      expect(() => correlation.validate()).to.throw('Correlation validation failed: "confidence" must be less than or equal to 1');
    });

    it('should throw error for negative confidence', () => {
      const invalidData = { ...validCorrelationData, confidence: -0.1 };
      const correlation = new Correlation(invalidData);

      expect(() => correlation.validate()).to.throw('Correlation validation failed: "confidence" must be greater than or equal to 0');
    });

    it('should throw error for same source and target dataset', () => {
      const invalidData = { ...validCorrelationData, targetDatasetId: sourceDatasetId };
      const correlation = new Correlation(invalidData);

      expect(() => correlation.validate()).to.throw('Source and target datasets cannot be the same');
    });

    it('should validate with ValidationUtils', () => {
      const correlation = new Correlation(validCorrelationData);
      const validated = ValidationUtils.validateCorrelation(correlation);

      expect(validated).to.be.an('object');
      expect(validated.sourceDatasetId).to.equal(sourceDatasetId);
      expect(validated.targetDatasetId).to.equal(targetDatasetId);
    });
  });

  describe('Serialization', () => {
    it('should serialize to JSON correctly', () => {
      const correlation = new Correlation(validCorrelationData);
      const json = correlation.toJSON();

      expect(json).to.be.an('object');
      expect(json.sourceDatasetId).to.equal(sourceDatasetId);
      expect(json.targetDatasetId).to.equal(targetDatasetId);
      expect(json.type).to.equal('one_to_many');
      expect(json.confidence).to.equal(0.85);
      expect(json).to.have.all.keys([
        'id', 'sourceDatasetId', 'targetDatasetId', 'type', 'parameters',
        'confidence', 'validityScore', 'description', 'status', 'parentCorrelationId',
        'version', 'tags', 'metadata', 'discoveryMethod', 'lastValidated',
        'createdAt', 'updatedAt'
      ]);
    });

    it('should serialize to database format correctly', () => {
      const correlation = new Correlation(validCorrelationData);
      const dbData = correlation.toDatabase();

      expect(dbData).to.be.an('object');
      expect(dbData.source_dataset_id).to.equal(sourceDatasetId);
      expect(dbData.target_dataset_id).to.equal(targetDatasetId);
      expect(dbData.type).to.equal('one_to_many');
      expect(dbData.confidence).to.equal(0.85);
      expect(dbData.created_at).to.equal(correlation.createdAt);
      expect(dbData.updated_at).to.equal(correlation.updatedAt);
    });

    it('should deserialize from database format correctly', () => {
      const dbData = {
        id: uuidv4(),
        source_dataset_id: sourceDatasetId,
        target_dataset_id: targetDatasetId,
        type: 'one_to_many',
        parameters: JSON.stringify({ strength: 0.85, direction: 'positive' }),
        confidence: 0.85,
        validity_score: 0.78,
        description: 'Test correlation',
        status: 'validated',
        parent_correlation_id: uuidv4(),
        version: 2,
        tags: ['test', 'correlation'],
        metadata: JSON.stringify({ test: true }),
        discovery_method: 'neural_network',
        last_validated: new Date().toISOString(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      const correlation = Correlation.fromDatabase(dbData);

      expect(correlation).to.be.an('object');
      expect(correlation.sourceDatasetId).to.equal(sourceDatasetId);
      expect(correlation.targetDatasetId).to.equal(targetDatasetId);
      expect(correlation.type).to.equal('one_to_many');
      expect(correlation.parameters).to.deep.equal({ strength: 0.85, direction: 'positive' });
      expect(correlation.metadata).to.deep.equal({ test: true });
    });
  });

  describe('Utility Methods', () => {
    it('should update validity score correctly', () => {
      const correlation = new Correlation(validCorrelationData);
      const originalUpdatedAt = correlation.updatedAt;

      setTimeout(() => {
        correlation.updateValidityScore(0.95);
        expect(correlation.validityScore).to.equal(0.95);
        expect(correlation.updatedAt).to.not.equal(originalUpdatedAt);
      }, 10);
    });

    it('should not update validity score with invalid value', () => {
      const correlation = new Correlation(validCorrelationData);
      const originalScore = correlation.validityScore;

      expect(() => correlation.updateValidityScore(1.5)).to.throw('Validity score must be between 0 and 1');
      expect(correlation.validityScore).to.equal(originalScore);
    });

    it('should update confidence correctly', () => {
      const correlation = new Correlation(validCorrelationData);
      const originalUpdatedAt = correlation.updatedAt;

      setTimeout(() => {
        correlation.updateConfidence(0.92);
        expect(correlation.confidence).to.equal(0.92);
        expect(correlation.updatedAt).to.not.equal(originalUpdatedAt);
      }, 10);
    });

    it('should not update confidence with invalid value', () => {
      const correlation = new Correlation(validCorrelationData);
      const originalConfidence = correlation.confidence;

      expect(() => correlation.updateConfidence(-0.1)).to.throw('Confidence must be between 0 and 1');
      expect(correlation.confidence).to.equal(originalConfidence);
    });

    it('should mark as validated correctly', () => {
      const correlation = new Correlation(validCorrelationData);
      const originalUpdatedAt = correlation.updatedAt;

      setTimeout(() => {
        correlation.markAsValidated();
        expect(correlation.status).to.equal('validated');
        expect(correlation.lastValidated).to.be.a('string');
        expect(correlation.updatedAt).to.not.equal(originalUpdatedAt);
      }, 10);
    });

    it('should mark as invalidated correctly', () => {
      const correlation = new Correlation(validCorrelationData);
      correlation.markAsInvalidated();

      expect(correlation.status).to.equal('invalidated');
    });

    it('should add tag correctly', () => {
      const correlation = new Correlation(validCorrelationData);
      correlation.addTag('new-tag');

      expect(correlation.tags).to.include('new-tag');
      expect(correlation.tags).to.have.lengthOf(3);
    });

    it('should not add duplicate tags', () => {
      const correlation = new Correlation(validCorrelationData);
      correlation.addTag('test');

      expect(correlation.tags).to.deep.equal(['test', 'correlation']);
      expect(correlation.tags).to.have.lengthOf(2);
    });

    it('should remove tag correctly', () => {
      const correlation = new Correlation(validCorrelationData);
      correlation.removeTag('test');

      expect(correlation.tags).to.deep.equal(['correlation']);
      expect(correlation.tags).to.have.lengthOf(1);
    });

    it('should check if has tag correctly', () => {
      const correlation = new Correlation(validCorrelationData);

      expect(correlation.hasTag('test')).to.be.true;
      expect(correlation.hasTag('correlation')).to.be.true;
      expect(correlation.hasTag('nonexistent')).to.be.false;
    });

    it('should increment version correctly', () => {
      const correlation = new Correlation(validCorrelationData);
      const originalVersion = correlation.version;

      correlation.incrementVersion();
      expect(correlation.version).to.equal(originalVersion + 1);
    });

    it('should set parameter correctly', () => {
      const correlation = new Correlation(validCorrelationData);
      correlation.setParameter('new_param', 'new_value');

      expect(correlation.parameters.new_param).to.equal('new_value');
    });

    it('should get parameter correctly', () => {
      const correlation = new Correlation(validCorrelationData);
      correlation.parameters.strength = 0.9;

      expect(correlation.getParameter('strength')).to.equal(0.9);
      expect(correlation.getParameter('nonexistent')).to.be.undefined;
    });

    it('should check if is temporal correctly', () => {
      const temporalCorrelation = new Correlation({ ...validCorrelationData, type: 'temporal' });
      expect(temporalCorrelation.isTemporal()).to.be.true;

      const nonTemporalCorrelation = new Correlation({ ...validCorrelationData, type: 'one_to_one' });
      expect(nonTemporalCorrelation.isTemporal()).to.be.false;
    });

    it('should check if is spatial correctly', () => {
      const spatialCorrelation = new Correlation({ ...validCorrelationData, type: 'spatial' });
      expect(spatialCorrelation.isSpatial()).to.be.true;

      const nonSpatialCorrelation = new Correlation({ ...validCorrelationData, type: 'one_to_one' });
      expect(nonSpatialCorrelation.isSpatial()).to.be.false;
    });

    it('should check if is semantic correctly', () => {
      const semanticCorrelation = new Correlation({ ...validCorrelationData, type: 'semantic' });
      expect(semanticCorrelation.isSemantic()).to.be.true;

      const nonSemanticCorrelation = new Correlation({ ...validCorrelationData, type: 'one_to_one' });
      expect(nonSemanticCorrelation.isSemantic()).to.be.false;
    });

    it('should check if is weighted correctly', () => {
      const weightedCorrelation = new Correlation({ ...validCorrelationData, type: 'weighted_many_to_many' });
      expect(weightedCorrelation.isWeighted()).to.be.true;

      const nonWeightedCorrelation = new Correlation({ ...validCorrelationData, type: 'one_to_one' });
      expect(nonWeightedCorrelation.isWeighted()).to.be.false;
    });

    it('should check if is valid correctly', () => {
      const validCorrelation = new Correlation({ ...validCorrelationData, status: 'validated' });
      expect(validCorrelation.isValid()).to.be.true;

      const proposedCorrelation = new Correlation({ ...validCorrelationData, status: 'proposed' });
      expect(proposedCorrelation.isValid()).to.be.false;

      const invalidatedCorrelation = new Correlation({ ...validCorrelationData, status: 'invalidated' });
      expect(invalidatedCorrelation.isValid()).to.be.false;
    });

    it('should get confidence level correctly', () => {
      const highConfidenceCorrelation = new Correlation({ ...validCorrelationData, confidence: 0.9 });
      expect(highConfidenceCorrelation.getConfidenceLevel()).to.equal('high');

      const mediumConfidenceCorrelation = new Correlation({ ...validCorrelationData, confidence: 0.7 });
      expect(mediumConfidenceCorrelation.getConfidenceLevel()).to.equal('medium');

      const lowConfidenceCorrelation = new Correlation({ ...validCorrelationData, confidence: 0.4 });
      expect(lowConfidenceCorrelation.getConfidenceLevel()).to.equal('low');
    });

    it('should get age in days correctly', () => {
      const correlation = new Correlation(validCorrelationData);
      const ageInDays = correlation.getAgeInDays();

      expect(ageInDays).to.be.a('number');
      expect(ageInDays).to.be.at.least(0);
    });
  });

  describe('Schema Static Methods', () => {
    it('should return correct Joi schema', () => {
      const schema = Correlation.schema;

      expect(schema).to.be.an('object');
      expect(schema.describe().type).to.equal('object');
    });

    it('should have required fields in schema', () => {
      const schema = Correlation.schema;
      const description = schema.describe();

      expect(description.keys).to.have.property('sourceDatasetId');
      expect(description.keys).to.have.property('targetDatasetId');
      expect(description.keys).to.have.property('type');
    });

    it('should support all valid correlation types', () => {
      const schema = Correlation.schema;
      const validTypes = [
        'one_to_one', 'one_to_many', 'many_to_one', 'many_to_many',
        'weighted_many_to_many', 'temporal', 'spatial', 'semantic',
        'statistical', 'structural', 'functional', 'causal'
      ];

      validTypes.forEach(type => {
        const result = schema.validate({ sourceDatasetId, targetDatasetId, type });
        expect(result.error).to.be.null;
      });
    });

    it('should reject invalid correlation types', () => {
      const schema = Correlation.schema;
      const invalidTypes = ['invalid', 'wrong_type', ''];

      invalidTypes.forEach(type => {
        const result = schema.validate({ sourceDatasetId, targetDatasetId, type });
        expect(result.error).to.not.be.null;
      });
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty object in constructor', () => {
      const correlation = new Correlation({});

      expect(correlation.id).to.be.a('string');
      expect(correlation.sourceDatasetId).to.be.undefined;
      expect(correlation.targetDatasetId).to.be.undefined;
      expect(correlation.createdAt).to.be.a('string');
      expect(correlation.updatedAt).to.be.a('string');
    });

    it('should handle null values in constructor', () => {
      const correlation = new Correlation(null);

      expect(correlation.id).to.be.a('string');
      expect(correlation.sourceDatasetId).to.be.undefined;
      expect(correlation.createdAt).to.be.a('string');
      expect(correlation.updatedAt).to.be.a('string');
    });

    it('should handle undefined in constructor', () => {
      const correlation = new Correlation(undefined);

      expect(correlation.id).to.be.a('string');
      expect(correlation.sourceDatasetId).to.be.undefined;
      expect(correlation.createdAt).to.be.a('string');
      expect(correlation.updatedAt).to.be.a('string');
    });

    it('should handle boundary values for confidence', () => {
      const minConfidence = new Correlation({ ...validCorrelationData, confidence: 0 });
      expect(() => minConfidence.validate()).to.not.throw();

      const maxConfidence = new Correlation({ ...validCorrelationData, confidence: 1 });
      expect(() => maxConfidence.validate()).to.not.throw();
    });

    it('should handle boundary values for validity score', () => {
      const minValidity = new Correlation({ ...validCorrelationData, validityScore: 0 });
      expect(() => minValidity.validate()).to.not.throw();

      const maxValidity = new Correlation({ ...validCorrelationData, validityScore: 1 });
      expect(() => maxValidity.validate()).to.not.throw();
    });
  });
});