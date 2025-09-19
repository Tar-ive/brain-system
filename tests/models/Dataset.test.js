const { expect } = require('chai');
const { v4: uuidv4 } = require('uuid');
const Dataset = require('../../src/models/Dataset');
const ValidationUtils = require('../../src/utils/validation');

describe('Dataset Model', () => {
  let validDatasetData;

  beforeEach(() => {
    validDatasetData = {
      name: 'Test Dataset',
      description: 'A test dataset for unit testing',
      type: 'structured',
      source: 'test',
      format: 'json',
      size: 1024,
      recordCount: 100,
      schema: {
        fields: [
          { name: 'id', type: 'string' },
          { name: 'name', type: 'string' },
          { name: 'value', type: 'number' }
        ]
      },
      tags: ['test', 'unit'],
      visibility: 'public'
    };
  });

  describe('Constructor', () => {
    it('should create a dataset with valid data', () => {
      const dataset = new Dataset(validDatasetData);

      expect(dataset).to.be.an('object');
      expect(dataset.name).to.equal('Test Dataset');
      expect(dataset.type).to.equal('structured');
      expect(dataset.format).to.equal('json');
      expect(dataset.size).to.equal(1024);
      expect(dataset.recordCount).to.equal(100);
      expect(dataset.id).to.be.a('string');
      expect(dataset.createdAt).to.be.a('string');
      expect(dataset.updatedAt).to.be.a('string');
    });

    it('should generate UUID if not provided', () => {
      const dataset = new Dataset({ name: 'Test' });
      expect(dataset.id).to.be.a('string');
      expect(dataset.id).to.match(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    });

    it('should set default values', () => {
      const dataset = new Dataset({ name: 'Test' });
      expect(dataset.status).to.equal('active');
      expect(dataset.visibility).to.equal('private');
      expect(dataset.size).to.equal(0);
      expect(dataset.recordCount).to.equal(0);
      expect(dataset.metadata).to.deep.equal({});
      expect(dataset.tags).to.deep.equal([]);
    });

    it('should use provided ID if given', () => {
      const customId = uuidv4();
      const dataset = new Dataset({ id: customId, name: 'Test' });
      expect(dataset.id).to.equal(customId);
    });
  });

  describe('Validation', () => {
    it('should validate a correct dataset', () => {
      const dataset = new Dataset(validDatasetData);
      expect(() => dataset.validate()).to.not.throw();
    });

    it('should throw error for missing name', () => {
      const invalidData = { ...validDatasetData };
      delete invalidData.name;
      const dataset = new Dataset(invalidData);

      expect(() => dataset.validate()).to.throw('Dataset validation failed: "name" is required');
    });

    it('should throw error for invalid type', () => {
      const invalidData = { ...validDatasetData, type: 'invalid_type' };
      const dataset = new Dataset(invalidData);

      expect(() => dataset.validate()).to.throw('Dataset validation failed: "type" must be one of');
    });

    it('should throw error for invalid format', () => {
      const invalidData = { ...validDatasetData, format: 'invalid_format' };
      const dataset = new Dataset(invalidData);

      expect(() => dataset.validate()).to.throw('Dataset validation failed: "format" must be one of');
    });

    it('should throw error for negative size', () => {
      const invalidData = { ...validDatasetData, size: -100 };
      const dataset = new Dataset(invalidData);

      expect(() => dataset.validate()).to.throw('Dataset validation failed: "size" must be greater than or equal to 0');
    });

    it('should throw error for negative record count', () => {
      const invalidData = { ...validDatasetData, recordCount: -1 };
      const dataset = new Dataset(invalidData);

      expect(() => dataset.validate()).to.throw('Dataset validation failed: "record_count" must be greater than or equal to 0');
    });

    it('should validate with ValidationUtils', () => {
      const dataset = new Dataset(validDatasetData);
      const validated = ValidationUtils.validateDataset(dataset);

      expect(validated).to.be.an('object');
      expect(validated.name).to.equal('Test Dataset');
    });
  });

  describe('Serialization', () => {
    it('should serialize to JSON correctly', () => {
      const dataset = new Dataset(validDatasetData);
      const json = dataset.toJSON();

      expect(json).to.be.an('object');
      expect(json.name).to.equal('Test Dataset');
      expect(json.type).to.equal('structured');
      expect(json.format).to.equal('json');
      expect(json).to.have.all.keys([
        'id', 'name', 'description', 'type', 'source', 'format', 'size',
        'recordCount', 'schema', 'metadata', 'status', 'lastAccessed',
        'tags', 'visibility', 'ownerId', 'createdAt', 'updatedAt'
      ]);
    });

    it('should serialize to database format correctly', () => {
      const dataset = new Dataset(validDatasetData);
      const dbData = dataset.toDatabase();

      expect(dbData).to.be.an('object');
      expect(dbData.name).to.equal('Test Dataset');
      expect(dbData.type).to.equal('structured');
      expect(dbData.format).to.equal('json');
      expect(dbData.created_at).to.equal(dataset.createdAt);
      expect(dbData.updated_at).to.equal(dataset.updatedAt);
    });

    it('should deserialize from database format correctly', () => {
      const dbData = {
        id: uuidv4(),
        name: 'Test Dataset',
        description: 'Test description',
        type: 'structured',
        source: 'test',
        format: 'json',
        size: 1024,
        record_count: 100,
        schema: JSON.stringify({ fields: [{ name: 'id', type: 'string' }] }),
        metadata: JSON.stringify({ test: true }),
        status: 'active',
        last_accessed: new Date().toISOString(),
        tags: ['test', 'unit'],
        visibility: 'public',
        owner_id: uuidv4(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      const dataset = Dataset.fromDatabase(dbData);

      expect(dataset).to.be.an('object');
      expect(dataset.name).to.equal('Test Dataset');
      expect(dataset.type).to.equal('structured');
      expect(dataset.schema).to.deep.equal({ fields: [{ name: 'id', type: 'string' }] });
      expect(dataset.metadata).to.deep.equal({ test: true });
    });
  });

  describe('Utility Methods', () => {
    it('should track access correctly', () => {
      const dataset = new Dataset(validDatasetData);
      const originalLastAccessed = dataset.lastAccessed;

      // Wait a small amount to ensure timestamp difference
      setTimeout(() => {
        dataset.trackAccess();
        expect(dataset.lastAccessed).to.not.equal(originalLastAccessed);
        expect(dataset.lastAccessed).to.be.a('string');
      }, 10);
    });

    it('should add tags correctly', () => {
      const dataset = new Dataset(validDatasetData);
      dataset.addTag('new-tag');

      expect(dataset.tags).to.include('new-tag');
      expect(dataset.tags).to.have.lengthOf(3); // test, unit, new-tag
    });

    it('should not add duplicate tags', () => {
      const dataset = new Dataset(validDatasetData);
      dataset.addTag('test');

      expect(dataset.tags).to.deep.equal(['test', 'unit']);
      expect(dataset.tags).to.have.lengthOf(2);
    });

    it('should remove tags correctly', () => {
      const dataset = new Dataset(validDatasetData);
      dataset.removeTag('test');

      expect(dataset.tags).to.deep.equal(['unit']);
      expect(dataset.tags).to.have.lengthOf(1);
    });

    it('should check if has tag correctly', () => {
      const dataset = new Dataset(validDatasetData);

      expect(dataset.hasTag('test')).to.be.true;
      expect(dataset.hasTag('unit')).to.be.true;
      expect(dataset.hasTag('nonexistent')).to.be.false;
    });

    it('should get file extension from format', () => {
      const dataset = new Dataset({ ...validDatasetData, format: 'json' });
      expect(dataset.getFileExtension()).to.equal('.json');

      const csvDataset = new Dataset({ ...validDatasetData, format: 'csv' });
      expect(csvDataset.getFileExtension()).to.equal('.csv');
    });

    it('should return empty string for unknown format', () => {
      const dataset = new Dataset({ ...validDatasetData, format: 'unknown' });
      expect(dataset.getFileExtension()).to.equal('');
    });

    it('should calculate size in MB correctly', () => {
      const dataset = new Dataset({ ...validDatasetData, size: 1024 * 1024 }); // 1MB
      expect(dataset.getSizeInMB()).to.equal(1);

      const smallDataset = new Dataset({ ...validDatasetData, size: 512 * 1024 }); // 0.5MB
      expect(smallDataset.getSizeInMB()).to.equal(0.5);
    });

    it('should return 0 for size 0', () => {
      const dataset = new Dataset({ ...validDatasetData, size: 0 });
      expect(dataset.getSizeInMB()).to.equal(0);
    });

    it('should calculate record density correctly', () => {
      const dataset = new Dataset({ ...validDatasetData, size: 1024, recordCount: 100 });
      expect(dataset.getRecordDensity()).to.equal(100); // 100 records per KB

      const largeDataset = new Dataset({ ...validDatasetData, size: 2048, recordCount: 100 });
      expect(largeDataset.getRecordDensity()).to.equal(50); // 50 records per KB
    });

    it('should return 0 for record density when size is 0', () => {
      const dataset = new Dataset({ ...validDatasetData, size: 0, recordCount: 100 });
      expect(dataset.getRecordDensity()).to.equal(0);
    });

    it('should return human readable size correctly', () => {
      expect(Dataset.getHumanReadableSize(500)).to.equal('500 B');
      expect(Dataset.getHumanReadableSize(1024)).to.equal('1 KB');
      expect(Dataset.getHumanReadableSize(1024 * 1024)).to.equal('1 MB');
      expect(Dataset.getHumanReadableSize(1024 * 1024 * 1024)).to.equal('1 GB');
    });

    it('should check if dataset is expired correctly', () => {
      const dataset = new Dataset(validDatasetData);

      // Dataset without expiration date should not be expired
      expect(dataset.isExpired()).to.be.false;

      // Set expiration date in the past
      dataset.metadata.expirationDate = new Date(Date.now() - 1000).toISOString();
      expect(dataset.isExpired()).to.be.true;

      // Set expiration date in the future
      dataset.metadata.expirationDate = new Date(Date.now() + 100000).toISOString();
      expect(dataset.isExpired()).to.be.false;
    });
  });

  describe('Schema Static Methods', () => {
    it('should return correct Joi schema', () => {
      const schema = Dataset.schema;

      expect(schema).to.be.an('object');
      expect(schema.describe().type).to.equal('object');
    });

    it('should have required fields in schema', () => {
      const schema = Dataset.schema;
      const description = schema.describe();

      expect(description.keys).to.have.property('name');
      expect(description.keys).to.have.property('type');
      expect(description.keys).to.have.property('format');
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty object in constructor', () => {
      const dataset = new Dataset({});

      expect(dataset.id).to.be.a('string');
      expect(dataset.name).to.be.undefined;
      expect(dataset.type).to.be.undefined;
      expect(dataset.format).to.be.undefined;
      expect(dataset.createdAt).to.be.a('string');
      expect(dataset.updatedAt).to.be.a('string');
    });

    it('should handle null values in constructor', () => {
      const dataset = new Dataset(null);

      expect(dataset.id).to.be.a('string');
      expect(dataset.name).to.be.undefined;
      expect(dataset.createdAt).to.be.a('string');
      expect(dataset.updatedAt).to.be.a('string');
    });

    it('should handle undefined in constructor', () => {
      const dataset = new Dataset(undefined);

      expect(dataset.id).to.be.a('string');
      expect(dataset.name).to.be.undefined;
      expect(dataset.createdAt).to.be.a('string');
      expect(dataset.updatedAt).to.be.a('string');
    });
  });
});