const BaseModel = require('./BaseModel');
const Joi = require('joi');

class Dataset extends BaseModel {
  constructor(data = {}) {
    super(data);
    this.name = data.name || '';
    this.description = data.description || '';
    this.schema = data.schema || {};
    this.type = data.type || 'structured';
    this.source = data.source || '';
    this.format = data.format || 'json';
    this.size = data.size || 0;
    this.recordCount = data.recordCount || 0;
    this.metadata = data.metadata || {};
    this.status = data.status || 'active';
    this.lastAccessed = data.lastAccessed || new Date().toISOString();
    this.tags = data.tags || [];
    this.visibility = data.visibility || 'private';
    this.ownerId = data.ownerId || null;
  }

  static get tableName() {
    return 'datasets';
  }

  static get schema() {
    return Joi.object({
      id: Joi.string().guid().default(() => require('uuid').v4()),
      name: Joi.string().required().min(1).max(255),
      description: Joi.string().max(5000).allow(''),
      schema: Joi.object().default({}),
      type: Joi.string().valid('structured', 'semi-structured', 'unstructured').default('structured'),
      source: Joi.string().max(1000).allow(''),
      format: Joi.string().valid('json', 'csv', 'parquet', 'xml', 'avro', 'binary').default('json'),
      size: Joi.number().integer().min(0).default(0),
      recordCount: Joi.number().integer().min(0).default(0),
      metadata: Joi.object().default({}),
      status: Joi.string().valid('active', 'archived', 'processing', 'error').default('active'),
      lastAccessed: Joi.date().iso().default(() => new Date().toISOString()),
      tags: Joi.array().items(Joi.string().max(50)).default([]),
      visibility: Joi.string().valid('private', 'public', 'shared').default('private'),
      ownerId: Joi.string().guid().allow(null),
      createdAt: Joi.date().iso().default(() => new Date().toISOString()),
      updatedAt: Joi.date().iso().default(() => new Date().toISOString())
    });
  }

  static get indexes() {
    return [
      { name: 'idx_datasets_name', columns: ['name'] },
      { name: 'idx_datasets_type', columns: ['type'] },
      { name: 'idx_datasets_status', columns: ['status'] },
      { name: 'idx_datasets_owner', columns: ['ownerId'] },
      { name: 'idx_datasets_visibility', columns: ['visibility'] },
      { name: 'idx_datasets_last_accessed', columns: ['lastAccessed'] },
      { name: 'idx_datasets_tags', columns: ['tags'], using: 'gin' }
    ];
  }

  incrementAccessCount() {
    this.lastAccessed = new Date().toISOString();
    if (!this.metadata.accessCount) {
      this.metadata.accessCount = 0;
    }
    this.metadata.accessCount++;
    return this;
  }

  updateStats(recordCount, size) {
    this.recordCount = recordCount;
    this.size = size;
    this.updatedAt = new Date().toISOString();
    return this;
  }

  addTag(tag) {
    if (!this.tags.includes(tag)) {
      this.tags.push(tag);
      this.updatedAt = new Date().toISOString();
    }
    return this;
  }

  removeTag(tag) {
    this.tags = this.tags.filter(t => t !== tag);
    this.updatedAt = new Date().toISOString();
    return this;
  }

  archive() {
    this.status = 'archived';
    this.updatedAt = new Date().toISOString();
    return this;
  }

  activate() {
    this.status = 'active';
    this.updatedAt = new Date().toISOString();
    return this;
  }

  validateSchema() {
    if (!this.schema || typeof this.schema !== 'object') {
      throw new Error('Schema must be a valid object');
    }

    // Basic schema validation
    if (this.schema.fields && !Array.isArray(this.schema.fields)) {
      throw new Error('Schema fields must be an array');
    }

    if (this.schema.fields) {
      this.schema.fields.forEach(field => {
        if (!field.name || !field.type) {
          throw new Error('Each schema field must have name and type');
        }
      });
    }

    return true;
  }

  toJSON() {
    const json = super.toJSON();
    return {
      ...json,
      recordCount: parseInt(json.recordCount),
      size: parseInt(json.size)
    };
  }
}

module.exports = Dataset;