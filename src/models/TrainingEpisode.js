const BaseModel = require('./BaseModel');
const Joi = require('joi');

class TrainingEpisode extends BaseModel {
  constructor(data = {}) {
    super(data);
    this.episodeId = data.episodeId || '';
    this.stepNumber = data.stepNumber || 0;
    this.state = data.state || {};
    this.action = data.action || {};
    this.reward = data.reward || 0;
    this.nextState = data.nextState || {};
    this.done = data.done || false;
    this.priority = data.priority || 1.0;
    this.generatorModel = data.generatorModel || '';
    this.validatorModel = data.validatorModel || '';
    this.algorithm = data.algorithm || '';
    this.environment = data.environment || {};
    this.metrics = data.metrics || {};
    this.metadata = data.metadata || {};
    this.experienceType = data.experienceType || 'exploration';
  }

  static get tableName() {
    return 'training_episodes';
  }

  static get schema() {
    return Joi.object({
      id: Joi.string().guid().default(() => require('uuid').v4()),
      episodeId: Joi.string().guid().required(),
      stepNumber: Joi.number().integer().min(0).default(0),
      state: Joi.object({
        sourceDatasetId: Joi.string().guid().required(),
        targetDatasetId: Joi.string().guid().required(),
        availableSignatures: Joi.array().items(Joi.string().guid()).default([]),
        proposedCorrelations: Joi.array().items(Joi.object()).default([]),
        validationHistory: Joi.array().items(Joi.object()).default([]),
        currentScore: Joi.number().min(0).max(1).default(0)
      }).required(),
      action: Joi.object({
        correlationType: Joi.string().required(),
        parameters: Joi.object().default({}),
        confidence: Joi.number().min(0).max(1).default(0),
        method: Joi.string().required(),
        reasoning: Joi.string().allow(''),
        computationalCost: Joi.number().min(0).default(0)
      }).required(),
      reward: Joi.number().default(0),
      nextState: Joi.object({
        sourceDatasetId: Joi.string().guid().required(),
        targetDatasetId: Joi.string().guid().required(),
        availableSignatures: Joi.array().items(Joi.string().guid()).default([]),
        proposedCorrelations: Joi.array().items(Joi.object()).default([]),
        validationHistory: Joi.array().items(Joi.object()).default([]),
        currentScore: Joi.number().min(0).max(1).default(0)
      }).required(),
      done: Joi.boolean().default(false),
      priority: Joi.number().min(0).default(1.0),
      generatorModel: Joi.string().guid().allow(''),
      validatorModel: Joi.string().guid().allow(''),
      algorithm: Joi.string().valid('mcts', 'evolutionary', 'neural', 'ensemble').allow(''),
      environment: Joi.object({
        difficulty: Joi.number().min(0).max(1).default(0.5),
        complexity: Joi.number().min(0).max(1).default(0.5),
        datasetComplexity: Joi.object({
          source: Joi.number().min(0).max(1).default(0.5),
          target: Joi.number().min(0).max(1).default(0.5)
        }).default()
      }).default(),
      metrics: Joi.object({
        episodeReward: Joi.number().default(0),
        episodeLength: Joi.number().integer().min(0).default(0),
        successRate: Joi.number().min(0).max(1).default(0),
        explorationRate: Joi.number().min(0).max(1).default(0),
        validationAccuracy: Joi.number().min(0).max(1).default(0),
        computationTime: Joi.number().min(0).default(0)
      }).default(),
      metadata: Joi.object({
        experimentId: Joi.string().guid().allow(''),
        hyperparameters: Joi.object().default({}),
        seed: Joi.number().integer().allow(null),
        tags: Joi.array().items(Joi.string()).default([])
      }).default(),
      experienceType: Joi.string().valid('exploration', 'exploitation', 'training', 'evaluation').default('exploration'),
      createdAt: Joi.date().iso().default(() => new Date().toISOString()),
      updatedAt: Joi.date().iso().default(() => new Date().toISOString())
    });
  }

  static get indexes() {
    return [
      { name: 'idx_episodes_episode', columns: ['episodeId'] },
      { name: 'idx_episodes_step', columns: ['episodeId', 'stepNumber'] },
      { name: 'idx_episodes_reward', columns: ['reward'] },
      { name: 'idx_episodes_priority', columns: ['priority'] },
      { name: 'idx_episodes_type', columns: ['experienceType'] },
      { name: 'idx_episodes_algorithm', columns: ['algorithm'] },
      { name: 'idx_episodes_done', columns: ['done'] },
      { name: 'idx_episodes_created', columns: ['createdAt'] },
      { name: 'idx_episodes_models', columns: ['generatorModel', 'validatorModel'] }
    ];
  }

  validate() {
    super.validate();

    // Validate state structure
    this.validateStateStructure(this.state);
    this.validateStateStructure(this.nextState);

    // Validate episode consistency
    if (this.done && this.stepNumber === 0) {
      throw new Error('Episode cannot be done at step 0');
    }

    return true;
  }

  validateStateStructure(state) {
    if (!state.sourceDatasetId || !state.targetDatasetId) {
      throw new Error('State must have source and target dataset IDs');
    }

    if (typeof state.currentScore !== 'number' || state.currentScore < 0 || state.currentScore > 1) {
      throw new Error('State currentScore must be a number between 0 and 1');
    }
  }

  updatePriority(newPriority) {
    this.priority = Math.max(0, newPriority);
    this.updatedAt = new Date().toISOString();
    return this;
  }

  updateMetrics(metrics) {
    Object.keys(metrics).forEach(key => {
      if (this.metrics[key] !== undefined) {
        this.metrics[key] = metrics[key];
      }
    });
    this.updatedAt = new Date().toISOString();
    return this;
  }

  updateReward(reward) {
    this.reward = reward;
    this.updatedAt = new Date().toISOString();
    return this;
  }

  isTerminal() {
    return this.done;
  }

  isExploration() {
    return this.experienceType === 'exploration';
  }

  isExploitation() {
    return this.experienceType === 'exploitation';
  }

  getActionComplexity() {
    // Estimate action complexity based on parameters and type
    const paramCount = Object.keys(this.action.parameters || {}).length;
    const baseComplexity = this.action.correlationType === 'weighted_many_to_many' ? 3 : 1;
    return baseComplexity + paramCount;
  }

  getStateComplexity() {
    // Estimate state complexity based on available data
    const signatureCount = (this.state.availableSignatures || []).length;
    const correlationCount = (this.state.proposedCorrelations || []).length;
    const validationCount = (this.state.validationHistory || []).length;

    return signatureCount * 0.3 + correlationCount * 0.5 + validationCount * 0.2;
  }

  calculateTDTarget(reward, nextStep, gamma = 0.99) {
    // Calculate temporal difference target
    if (nextStep && !nextStep.done) {
      return reward + gamma * nextStep.metrics.episodeReward;
    }
    return reward;
  }

  calculateAdvantage(value, nextValue, gamma = 0.99) {
    // Calculate advantage estimate
    const target = this.calculateTDTarget(this.reward, nextStep, gamma);
    return target - value;
  }

  addTag(tag) {
    if (!this.metadata.tags) {
      this.metadata.tags = [];
    }
    if (!this.metadata.tags.includes(tag)) {
      this.metadata.tags.push(tag);
      this.updatedAt = new Date().toISOString();
    }
    return this;
  }

  removeTag(tag) {
    if (this.metadata.tags) {
      this.metadata.tags = this.metadata.tags.filter(t => t !== tag);
      this.updatedAt = new Date().toISOString();
    }
    return this;
  }

  toJSON() {
    const json = super.toJSON();
    return {
      ...json,
      stepNumber: parseInt(json.stepNumber),
      reward: parseFloat(json.reward),
      priority: parseFloat(json.priority),
      done: Boolean(json.done),
      isTerminal: this.isTerminal(),
      isExploration: this.isExploration(),
      isExploitation: this.isExploitation(),
      actionComplexity: this.getActionComplexity(),
      stateComplexity: this.getStateComplexity()
    };
  }
}

module.exports = TrainingEpisode;