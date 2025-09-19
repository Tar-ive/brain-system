const BaseModel = require('./BaseModel');
const Joi = require('joi');

class Validation extends BaseModel {
  constructor(data = {}) {
    super(data);
    this.correlationId = data.correlationId || '';
    this.validityScore = data.validityScore || 0;
    this.statisticalScore = data.statisticalScore || 0;
    this.semanticScore = data.semanticScore || 0;
    this.structuralScore = data.structuralScore || 0;
    this.conservationError = data.conservationError || 0;
    this.testAccuracy = data.testAccuracy || 0;
    this.confidenceInterval = data.confidenceInterval || [0, 1];
    this.counterExamples = data.counterExamples || [];
    this.validationMethod = data.validationMethod || '';
    this.testCases = data.testCases || [];
    this.failureModes = data.failureModes || [];
    this.metadata = data.metadata || {};
    this.validationTime = data.validationTime || 0;
    this.dataSize = data.dataSize || 0;
    this.sampleSize = data.sampleSize || 0;
  }

  static get tableName() {
    return 'validations';
  }

  static get schema() {
    return Joi.object({
      id: Joi.string().guid().default(() => require('uuid').v4()),
      correlationId: Joi.string().guid().required(),
      validityScore: Joi.number().min(0).max(1).default(0),
      statisticalScore: Joi.number().min(0).max(1).default(0),
      semanticScore: Joi.number().min(0).max(1).default(0),
      structuralScore: Joi.number().min(0).max(1).default(0),
      conservationError: Joi.number().min(0).default(0),
      testAccuracy: Joi.number().min(0).max(1).default(0),
      confidenceInterval: Joi.array().items(Joi.number().min(0).max(1)).length(2).default([0, 1]),
      counterExamples: Joi.array().items(Joi.object({
        input: Joi.object().required(),
        expected: Joi.object().required(),
        actual: Joi.object().required(),
        error: Joi.string().required(),
        severity: Joi.string().valid('low', 'medium', 'high', 'critical').default('medium')
      })).default([]),
      validationMethod: Joi.string().valid(
        'statistical', 'semantic', 'structural', 'conservation', 'ensemble', 'cross_validation'
      ).allow(''),
      testCases: Joi.array().items(Joi.object({
        id: Joi.string().required(),
        input: Joi.object().required(),
        expected: Joi.object().required(),
        actual: Joi.object().required(),
        passed: Joi.boolean().required(),
        executionTime: Joi.number().min(0).default(0)
      })).default([]),
      failureModes: Joi.array().items(Joi.object({
        type: Joi.string().required(),
        description: Joi.string().required(),
        frequency: Joi.number().min(0).max(1).default(0),
        severity: Joi.string().valid('low', 'medium', 'high', 'critical').default('medium'),
        examples: Joi.array().items(Joi.object()).default([])
      })).default([]),
      metadata: Joi.object().default({}),
      validationTime: Joi.number().integer().min(0).default(0),
      dataSize: Joi.number().integer().min(0).default(0),
      sampleSize: Joi.number().integer().min(0).default(0),
      createdAt: Joi.date().iso().default(() => new Date().toISOString()),
      updatedAt: Joi.date().iso().default(() => new Date().toISOString())
    });
  }

  static get indexes() {
    return [
      { name: 'idx_validations_correlation', columns: ['correlationId'] },
      { name: 'idx_validations_validity', columns: ['validityScore'] },
      { name: 'idx_validations_statistical', columns: ['statisticalScore'] },
      { name: 'idx_validations_semantic', columns: ['semanticScore'] },
      { name: 'idx_validations_structural', columns: ['structuralScore'] },
      { name: 'idx_validations_conservation', columns: ['conservationError'] },
      { name: 'idx_validations_accuracy', columns: ['testAccuracy'] },
      { name: 'idx_validations_method', columns: ['validationMethod'] },
      { name: 'idx_validations_created', columns: ['createdAt'] }
    ];
  }

  validate() {
    super.validate();

    // Validate confidence interval
    const [lower, upper] = this.confidenceInterval;
    if (lower > upper) {
      throw new Error('Confidence interval lower bound must be less than or equal to upper bound');
    }

    // Validate scores
    const scores = [this.validityScore, this.statisticalScore, this.semanticScore, this.structuralScore];
    scores.forEach(score => {
      if (score < 0 || score > 1) {
        throw new Error('All scores must be between 0 and 1');
      }
    });

    return true;
  }

  updateScores(scores) {
    Object.keys(scores).forEach(key => {
      if (this[key] !== undefined && typeof scores[key] === 'number') {
        this[key] = Math.max(0, Math.min(1, scores[key]));
      }
    });
    this.updatedAt = new Date().toISOString();
    return this;
  }

  addCounterExample(input, expected, actual, error, severity = 'medium') {
    this.counterExamples.push({
      id: require('uuid').v4(),
      input,
      expected,
      actual,
      error,
      severity
    });
    this.updatedAt = new Date().toISOString();
    return this;
  }

  addTestCase(input, expected, actual, passed, executionTime = 0) {
    this.testCases.push({
      id: require('uuid').v4(),
      input,
      expected,
      actual,
      passed,
      executionTime
    });
    this.updatedAt = new Date().toISOString();
    return this;
  }

  addFailureMode(type, description, frequency = 0, severity = 'medium', examples = []) {
    this.failureModes.push({
      type,
      description,
      frequency: Math.max(0, Math.min(1, frequency)),
      severity,
      examples
    });
    this.updatedAt = new Date().toISOString();
    return this;
  }

  isValid() {
    return this.validityScore >= 0.5;
  }

  isReliable() {
    return this.validityScore >= 0.7 &&
           this.testAccuracy >= 0.8 &&
           this.conservationError <= 0.1;
  }

  getPassRate() {
    if (this.testCases.length === 0) return 0;
    const passed = this.testCases.filter(tc => tc.passed).length;
    return passed / this.testCases.length;
  }

  getCriticalFailures() {
    return this.failureModes.filter(fm => fm.severity === 'critical');
  }

  getHighSeverityCounterExamples() {
    return this.counterExamples.filter(ce => ce.severity === 'high' || ce.severity === 'critical');
  }

  calculateConfidence() {
    // Calculate overall confidence based on multiple factors
    const baseScore = this.validityScore;
    const accuracyBonus = this.testAccuracy * 0.2;
    const conservationPenalty = Math.min(0.3, this.conservationError);
    const counterExamplePenalty = Math.min(0.2, this.counterExamples.length * 0.05);

    return Math.max(0, Math.min(1, baseScore + accuracyBonus - conservationPenalty - counterExamplePenalty));
  }

  updateValidationTime(timeMs) {
    this.validationTime = timeMs;
    this.updatedAt = new Date().toISOString();
    return this;
  }

  toJSON() {
    const json = super.toJSON();
    return {
      ...json,
      validityScore: parseFloat(json.validityScore),
      statisticalScore: parseFloat(json.statisticalScore),
      semanticScore: parseFloat(json.semanticScore),
      structuralScore: parseFloat(json.structuralScore),
      conservationError: parseFloat(json.conservationError),
      testAccuracy: parseFloat(json.testAccuracy),
      confidenceInterval: json.confidenceInterval.map(parseFloat),
      validationTime: parseInt(json.validationTime),
      dataSize: parseInt(json.dataSize),
      sampleSize: parseInt(json.sampleSize),
      isValid: this.isValid(),
      isReliable: this.isReliable(),
      passRate: this.getPassRate(),
      criticalFailures: this.getCriticalFailures().length,
      confidence: this.calculateConfidence()
    };
  }
}

module.exports = Validation;