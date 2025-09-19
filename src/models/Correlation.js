const BaseModel = require('./BaseModel');
const Joi = require('joi');

class Correlation extends BaseModel {
  constructor(data = {}) {
    super(data);
    this.sourceDatasetId = data.sourceDatasetId || '';
    this.targetDatasetId = data.targetDatasetId || '';
    this.type = data.type || '';
    this.parameters = data.parameters || {};
    this.confidence = data.confidence || 0;
    this.validityScore = data.validityScore || 0;
    this.description = data.description || '';
    this.status = data.status || 'proposed';
    this.parentCorrelationId = data.parentCorrelationId || null;
    this.version = data.version || 1;
    this.tags = data.tags || [];
    this.metadata = data.metadata || {};
    this.discoveryMethod = data.discoveryMethod || '';
    this.lastValidated = data.lastValidated || null;
  }

  static get tableName() {
    return 'correlations';
  }

  static get schema() {
    return Joi.object({
      id: Joi.string().guid().default(() => require('uuid').v4()),
      sourceDatasetId: Joi.string().guid().required(),
      targetDatasetId: Joi.string().guid().required(),
      type: Joi.string().valid(
        'one_to_one', 'one_to_many', 'many_to_one', 'many_to_many',
        'weighted_many_to_many', 'temporal', 'spatial', 'semantic',
        'statistical', 'structural', 'functional', 'causal'
      ).required(),
      parameters: Joi.object().default({}),
      confidence: Joi.number().min(0).max(1).default(0),
      validityScore: Joi.number().min(0).max(1).default(0),
      description: Joi.string().max(2000).allow(''),
      status: Joi.string().valid('proposed', 'validated', 'invalidated', 'archived').default('proposed'),
      parentCorrelationId: Joi.string().guid().allow(null),
      version: Joi.number().integer().min(1).default(1),
      tags: Joi.array().items(Joi.string().max(50)).default([]),
      metadata: Joi.object().default({}),
      discoveryMethod: Joi.string().valid(
        'neural_network', 'mcts', 'evolutionary', 'statistical',
        'information_theory', 'manual', 'hybrid'
      ).allow(''),
      lastValidated: Joi.date().iso().allow(null),
      createdAt: Joi.date().iso().default(() => new Date().toISOString()),
      updatedAt: Joi.date().iso().default(() => new Date().toISOString())
    });
  }

  static get indexes() {
    return [
      { name: 'idx_correlations_source_target', columns: ['sourceDatasetId', 'targetDatasetId'] },
      { name: 'idx_correlations_type', columns: ['type'] },
      { name: 'idx_correlations_confidence', columns: ['confidence'] },
      { name: 'idx_correlations_status', columns: ['status'] },
      { name: 'idx_correlations_validity', columns: ['validityScore'] },
      { name: 'idx_correlations_parent', columns: ['parentCorrelationId'] },
      { name: 'idx_correlations_method', columns: ['discoveryMethod'] },
      { name: 'idx_correlations_created', columns: ['createdAt'] },
      { name: 'idx_correlations_tags', columns: ['tags'], using: 'gin' }
    ];
  }

  validate() {
    super.validate();

    // Validate correlation-specific rules
    if (this.sourceDatasetId === this.targetDatasetId) {
      throw new Error('Source and target datasets cannot be the same');
    }

    if (this.confidence < 0 || this.confidence > 1) {
      throw new Error('Confidence must be between 0 and 1');
    }

    if (this.validityScore < 0 || this.validityScore > 1) {
      throw new Error('Validity score must be between 0 and 1');
    }

    return true;
  }

  updateValidation(validityScore, status = null) {
    this.validityScore = validityScore;
    this.lastValidated = new Date().toISOString();
    if (status) {
      this.status = status;
    }
    this.updatedAt = new Date().toISOString();
    return this;
  }

  incrementVersion() {
    this.version++;
    this.updatedAt = new Date().toISOString();
    return this;
  }

  archive() {
    this.status = 'archived';
    this.updatedAt = new Date().toISOString();
    return this;
  }

  isValid() {
    return this.validityScore >= 0.5 && this.status === 'validated';
  }

  isSignificant() {
    return this.confidence >= 0.7 && this.validityScore >= 0.6;
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

  toJSON() {
    const json = super.toJSON();
    return {
      ...json,
      confidence: parseFloat(json.confidence),
      validityScore: parseFloat(json.validityScore),
      version: parseInt(json.version),
      isValid: this.isValid(),
      isSignificant: this.isSignificant()
    };
  }
}

module.exports = Correlation;