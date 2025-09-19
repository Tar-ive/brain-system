const BaseModel = require('./BaseModel');
const Joi = require('joi');

class DatasetSignature extends BaseModel {
  constructor(data = {}) {
    super(data);
    this.datasetId = data.datasetId || '';
    this.statistical = data.statistical || {};
    this.semantic = data.semantic || {};
    this.structural = data.structural || {};
    this.temporal = data.temporal || {};
    this.spatial = data.spatial || {};
    this.version = data.version || 1;
    this.computedAt = data.computedAt || new Date().toISOString();
    this.expiresAt = data.expiresAt || null;
    this.metadata = data.metadata || {};
    this.computationTime = data.computationTime || 0;
    this.algorithm = data.algorithm || 'default';
    this.compressionRatio = data.compressionRatio || 0;
  }

  static get tableName() {
    return 'dataset_signatures';
  }

  static get schema() {
    return Joi.object({
      id: Joi.string().guid().default(() => require('uuid').v4()),
      datasetId: Joi.string().guid().required(),
      statistical: Joi.object({
        distributions: Joi.object().default({}),
        cardinality: Joi.object().default({}),
        correlations: Joi.object().default({}),
        informationMetrics: Joi.object().default({}),
        outliers: Joi.array().items(Joi.object()).default([])
      }).default({}),
      semantic: Joi.object({
        columnEmbeddings: Joi.object().default({}),
        valueEmbeddings: Joi.object().default({}),
        contextVector: Joi.array().items(Joi.number()).default([]),
        ontologyMappings: Joi.object().default({})
      }).default({}),
      structural: Joi.object({
        schemaGraph: Joi.object().default({}),
        constraints: Joi.array().items(Joi.object()).default([]),
        hierarchy: Joi.object().default({}),
        topology: Joi.object().default({})
      }).default({}),
      temporal: Joi.object({
        timeRange: Joi.object({
          start: Joi.date().iso(),
          end: Joi.date().iso()
        }).allow(null),
        patterns: Joi.array().items(Joi.object()).default([]),
        seasonality: Joi.object().default({}),
        trends: Joi.array().items(Joi.object()).default([])
      }).allow(null),
      spatial: Joi.object({
        bounds: Joi.object({
          north: Joi.number(),
          south: Joi.number(),
          east: Joi.number(),
          west: Joi.number()
        }).allow(null),
        patterns: Joi.array().items(Joi.object()).default([]),
        clusters: Joi.array().items(Joi.object()).default([])
      }).allow(null),
      version: Joi.number().integer().min(1).default(1),
      computedAt: Joi.date().iso().default(() => new Date().toISOString()),
      expiresAt: Joi.date().iso().allow(null),
      metadata: Joi.object().default({}),
      computationTime: Joi.number().integer().min(0).default(0),
      algorithm: Joi.string().valid('default', 'neural', 'statistical', 'hybrid').default('default'),
      compressionRatio: Joi.number().min(0).max(1).default(0),
      createdAt: Joi.date().iso().default(() => new Date().toISOString()),
      updatedAt: Joi.date().iso().default(() => new Date().toISOString())
    });
  }

  static get indexes() {
    return [
      { name: 'idx_signatures_dataset', columns: ['datasetId'] },
      { name: 'idx_signatures_version', columns: ['datasetId', 'version'] },
      { name: 'idx_signatures_expires', columns: ['expiresAt'] },
      { name: 'idx_signatures_computed', columns: ['computedAt'] },
      { name: 'idx_signatures_algorithm', columns: ['algorithm'] },
      { name: 'idx_signatures_compression', columns: ['compressionRatio'] }
    ];
  }

  validate() {
    super.validate();

    // Validate signature structure
    this.validateComponent('statistical', ['distributions', 'cardinality', 'correlations']);
    this.validateComponent('semantic', ['columnEmbeddings', 'contextVector']);
    this.validateComponent('structural', ['schemaGraph', 'constraints']);

    return true;
  }

  validateComponent(componentName, requiredKeys) {
    const component = this[componentName];
    if (!component || typeof component !== 'object') {
      throw new Error(`${componentName} signature must be an object`);
    }

    requiredKeys.forEach(key => {
      if (component[key] === undefined) {
        throw new Error(`${componentName} signature missing required key: ${key}`);
      }
    });
  }

  isExpired() {
    if (!this.expiresAt) return false;
    return new Date(this.expiresAt) < new Date();
  }

  updateStats(computationTime, compressionRatio) {
    this.computationTime = computationTime;
    this.compressionRatio = compressionRatio;
    this.computedAt = new Date().toISOString();
    this.updatedAt = new Date().toISOString();
    return this;
  }

  setExpiration(days = 30) {
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + days);
    this.expiresAt = expiresAt.toISOString();
    this.updatedAt = new Date().toISOString();
    return this;
  }

  incrementVersion() {
    this.version++;
    this.updatedAt = new Date().toISOString();
    return this;
  }

  getSize() {
    // Estimate size in bytes
    return JSON.stringify(this.toJSON()).length;
  }

  getCompressionInfo() {
    return {
      ratio: this.compressionRatio,
      originalSize: this.getSize(),
      compressedSize: Math.floor(this.getSize() * this.compressionRatio),
      savings: Math.floor(this.getSize() * (1 - this.compressionRatio))
    };
  }

  toJSON() {
    const json = super.toJSON();
    return {
      ...json,
      version: parseInt(json.version),
      computationTime: parseInt(json.computationTime),
      compressionRatio: parseFloat(json.compressionRatio),
      isExpired: this.isExpired(),
      compressionInfo: this.getCompressionInfo()
    };
  }
}

module.exports = DatasetSignature;