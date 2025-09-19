const Joi = require('joi');
const logger = require('./logger');

class ValidationUtils {
  // Common validation schemas
  static schemas = {
    uuid: Joi.string().guid({ version: 'uuidv4' }),
    email: Joi.string().email(),
    url: Joi.string().uri(),
    positiveInteger: Joi.number().integer().positive(),
    nonNegativeInteger: Joi.number().integer().min(0),
    probability: Joi.number().min(0).max(1),
    timestamp: Joi.date().iso(),
    jsonArray: Joi.array().items(Joi.object()),
    nonEmptyString: Joi.string().min(1),
    percentage: Joi.number().min(0).max(100),
    coordinate: Joi.number().min(-180).max(180)
  };

  // Dataset validation
  static validateDataset(dataset) {
    const schema = Joi.object({
      id: this.schemas.uuid,
      name: this.schemas.nonEmptyString.max(255).required(),
      description: Joi.string().max(5000).allow(''),
      type: Joi.string().valid('structured', 'semi-structured', 'unstructured').required(),
      source: Joi.string().max(1000).allow(''),
      format: Joi.string().valid('json', 'csv', 'parquet', 'xml', 'avro', 'binary').required(),
      size: this.schemas.nonNegativeInteger.default(0),
      recordCount: this.schemas.nonNegativeInteger.default(0),
      metadata: Joi.object().default({}),
      status: Joi.string().valid('active', 'archived', 'processing', 'error').default('active'),
      lastAccessed: this.schemas.timestamp.default(() => new Date().toISOString()),
      tags: Joi.array().items(Joi.string().max(50)).default([]),
      visibility: Joi.string().valid('private', 'public', 'shared').default('private'),
      ownerId: this.schemas.uuid.allow(null),
      createdAt: this.schemas.timestamp.default(() => new Date().toISOString()),
      updatedAt: this.schemas.timestamp.default(() => new Date().toISOString())
    });

    return this.validate(schema, dataset, 'Dataset');
  }

  // Correlation validation
  static validateCorrelation(correlation) {
    const schema = Joi.object({
      id: this.schemas.uuid,
      sourceDatasetId: this.schemas.uuid.required(),
      targetDatasetId: this.schemas.uuid.required(),
      type: Joi.string().valid(
        'one_to_one', 'one_to_many', 'many_to_one', 'many_to_many',
        'weighted_many_to_many', 'temporal', 'spatial', 'semantic',
        'statistical', 'structural', 'functional', 'causal'
      ).required(),
      parameters: Joi.object().default({}),
      confidence: this.schemas.probability.default(0),
      validityScore: this.schemas.probability.default(0),
      description: Joi.string().max(2000).allow(''),
      status: Joi.string().valid('proposed', 'validated', 'invalidated', 'archived').default('proposed'),
      parentCorrelationId: this.schemas.uuid.allow(null),
      version: Joi.number().integer().min(1).default(1),
      tags: Joi.array().items(Joi.string().max(50)).default([]),
      metadata: Joi.object().default({}),
      discoveryMethod: Joi.string().valid(
        'neural_network', 'mcts', 'evolutionary', 'statistical',
        'information_theory', 'manual', 'hybrid'
      ).allow(''),
      lastValidated: this.schemas.timestamp.allow(null),
      createdAt: this.schemas.timestamp.default(() => new Date().toISOString()),
      updatedAt: this.schemas.timestamp.default(() => new Date().toISOString())
    });

    const validated = this.validate(schema, correlation, 'Correlation');

    // Additional business logic validation
    if (validated.sourceDatasetId === validated.targetDatasetId) {
      throw new Error('Source and target datasets cannot be the same');
    }

    return validated;
  }

  // Validation result validation
  static validateValidation(validation) {
    const schema = Joi.object({
      id: this.schemas.uuid,
      correlationId: this.schemas.uuid.required(),
      validityScore: this.schemas.probability.default(0),
      statisticalScore: this.schemas.probability.default(0),
      semanticScore: this.schemas.probability.default(0),
      structuralScore: this.schemas.probability.default(0),
      conservationError: Joi.number().min(0).default(0),
      testAccuracy: this.schemas.probability.default(0),
      confidenceInterval: Joi.array().items(this.schemas.probability).length(2).default([0, 1]),
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
        id: this.schemas.uuid.required(),
        input: Joi.object().required(),
        expected: Joi.object().required(),
        actual: Joi.object().required(),
        passed: Joi.boolean().required(),
        executionTime: Joi.number().min(0).default(0)
      })).default([]),
      failureModes: Joi.array().items(Joi.object({
        type: Joi.string().required(),
        description: Joi.string().required(),
        frequency: this.schemas.probability.default(0),
        severity: Joi.string().valid('low', 'medium', 'high', 'critical').default('medium'),
        examples: Joi.array().items(Joi.object()).default([])
      })).default([]),
      metadata: Joi.object().default({}),
      validationTime: this.schemas.nonNegativeInteger.default(0),
      dataSize: this.schemas.nonNegativeInteger.default(0),
      sampleSize: this.schemas.nonNegativeInteger.default(0),
      createdAt: this.schemas.timestamp.default(() => new Date().toISOString()),
      updatedAt: this.schemas.timestamp.default(() => new Date().toISOString())
    });

    const validated = this.validate(schema, validation, 'Validation');

    // Validate confidence interval
    const [lower, upper] = validated.confidenceInterval;
    if (lower > upper) {
      throw new Error('Confidence interval lower bound must be less than or equal to upper bound');
    }

    return validated;
  }

  // Training episode validation
  static validateTrainingEpisode(episode) {
    const schema = Joi.object({
      id: this.schemas.uuid,
      episodeId: this.schemas.uuid.required(),
      stepNumber: this.schemas.nonNegativeInteger.default(0),
      state: Joi.object({
        sourceDatasetId: this.schemas.uuid.required(),
        targetDatasetId: this.schemas.uuid.required(),
        availableSignatures: Joi.array().items(this.schemas.uuid).default([]),
        proposedCorrelations: Joi.array().items(Joi.object()).default([]),
        validationHistory: Joi.array().items(Joi.object()).default([]),
        currentScore: this.schemas.probability.default(0)
      }).required(),
      action: Joi.object({
        correlationType: Joi.string().required(),
        parameters: Joi.object().default({}),
        confidence: this.schemas.probability.default(0),
        method: Joi.string().required(),
        reasoning: Joi.string().allow(''),
        computationalCost: Joi.number().min(0).default(0)
      }).required(),
      reward: Joi.number().default(0),
      nextState: Joi.object({
        sourceDatasetId: this.schemas.uuid.required(),
        targetDatasetId: this.schemas.uuid.required(),
        availableSignatures: Joi.array().items(this.schemas.uuid).default([]),
        proposedCorrelations: Joi.array().items(Joi.object()).default([]),
        validationHistory: Joi.array().items(Joi.object()).default([]),
        currentScore: this.schemas.probability.default(0)
      }).required(),
      done: Joi.boolean().default(false),
      priority: Joi.number().min(0).default(1.0),
      generatorModel: this.schemas.uuid.allow(''),
      validatorModel: this.schemas.uuid.allow(''),
      algorithm: Joi.string().valid('mcts', 'evolutionary', 'neural', 'ensemble').allow(''),
      environment: Joi.object({
        difficulty: this.schemas.probability.default(0.5),
        complexity: this.schemas.probability.default(0.5),
        datasetComplexity: Joi.object({
          source: this.schemas.probability.default(0.5),
          target: this.schemas.probability.default(0.5)
        }).default()
      }).default(),
      metrics: Joi.object({
        episodeReward: Joi.number().default(0),
        episodeLength: this.schemas.nonNegativeInteger.default(0),
        successRate: this.schemas.probability.default(0),
        explorationRate: this.schemas.probability.default(0),
        validationAccuracy: this.schemas.probability.default(0),
        computationTime: Joi.number().min(0).default(0)
      }).default(),
      metadata: Joi.object({
        experimentId: this.schemas.uuid.allow(''),
        hyperparameters: Joi.object().default({}),
        seed: Joi.number().integer().allow(null),
        tags: Joi.array().items(Joi.string()).default([])
      }).default(),
      experienceType: Joi.string().valid('exploration', 'exploitation', 'training', 'evaluation').default('exploration'),
      createdAt: this.schemas.timestamp.default(() => new Date().toISOString()),
      updatedAt: this.schemas.timestamp.default(() => new Date().toISOString())
    });

    const validated = this.validate(schema, episode, 'TrainingEpisode');

    // Additional business logic validation
    this.validateStateStructure(validated.state);
    this.validateStateStructure(validated.nextState);

    if (validated.done && validated.stepNumber === 0) {
      throw new Error('Episode cannot be done at step 0');
    }

    return validated;
  }

  // Helper method to validate state structure
  static validateStateStructure(state) {
    if (!state.sourceDatasetId || !state.targetDatasetId) {
      throw new Error('State must have source and target dataset IDs');
    }

    if (typeof state.currentScore !== 'number' || state.currentScore < 0 || state.currentScore > 1) {
      throw new Error('State currentScore must be a number between 0 and 1');
    }
  }

  // Generic validation method
  static validate(schema, data, entityName = 'Entity') {
    const { error, value } = schema.validate(data, {
      stripUnknown: true,
      abortEarly: false,
      allowUnknown: true
    });

    if (error) {
      const errorMessage = error.details.map(d => d.message).join(', ');
      logger.error(`${entityName} validation failed`, { error: errorMessage, data });
      throw new Error(`${entityName} validation failed: ${errorMessage}`);
    }

    logger.debug(`${entityName} validation passed`, { id: value.id });
    return value;
  }

  // Batch validation
  static validateBatch(schema, dataArray, entityName = 'Entity') {
    const results = [];
    const errors = [];

    dataArray.forEach((item, index) => {
      try {
        const validated = this.validate(schema, item, `${entityName}[${index}]`);
        results.push(validated);
      } catch (error) {
        errors.push({
          index,
          error: error.message,
          data: item
        });
      }
    });

    if (errors.length > 0) {
      logger.warn(`${entityName} batch validation has errors`, {
        total: dataArray.length,
        valid: results.length,
        invalid: errors.length
      });
    }

    return {
      valid: results,
      invalid: errors,
      totalValid: results.length,
      totalInvalid: errors.length
    };
  }

  // Query parameter validation
  static validateQueryParams(params, schema) {
    return this.validate(schema, params, 'Query Parameters');
  }

  // Common query schemas
  static querySchemas = {
    pagination: Joi.object({
      page: Joi.number().integer().min(1).default(1),
      limit: Joi.number().integer().min(1).max(1000).default(50),
      offset: Joi.number().integer().min(0).default(0)
    }),
    sorting: Joi.object({
      sortBy: Joi.string().default('createdAt'),
      sortOrder: Joi.string().valid('asc', 'desc', 'ASC', 'DESC').default('desc')
    }),
    filtering: Joi.object({
      status: Joi.string(),
      type: Joi.string(),
      startDate: this.schemas.timestamp,
      endDate: this.schemas.timestamp,
      tags: Joi.array().items(Joi.string())
    }),
    search: Joi.object({
      q: Joi.string().min(1).max(100),
      searchFields: Joi.array().items(Joi.string()).default(['name', 'description'])
    })
  };
}

module.exports = ValidationUtils;