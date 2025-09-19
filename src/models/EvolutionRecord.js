const BaseModel = require('./BaseModel');
const Joi = require('joi');

class EvolutionRecord extends BaseModel {
  constructor(data = {}) {
    super(data);
    this.generation = data.generation || 0;
    this.individualId = data.individualId || '';
    this.genome = data.genome || {};
    this.fitness = data.fitness || 0;
    this.parent1Id = data.parent1Id || null;
    this.parent2Id = data.parent2Id || null;
    this.mutationInfo = data.mutationInfo || {};
    this.crossoverInfo = data.crossoverInfo || {};
    this.populationId = data.populationId || '';
    this.species = data.species || '';
    this.noveltyScore = data.noveltyScore || 0;
    this.complexity = data.complexity || 0;
    this.diversity = data.diversity || 0;
    this.evaluationTime = data.evaluationTime || 0;
    this.algorithm = data.algorithm || '';
    this.parameters = data.parameters || {};
    this.metadata = data.metadata || {};
  }

  static get tableName() {
    return 'evolution_records';
  }

  static get schema() {
    return Joi.object({
      id: Joi.string().guid().default(() => require('uuid').v4()),
      generation: Joi.number().integer().min(0).default(0),
      individualId: Joi.string().guid().required(),
      genome: Joi.object({
        correlationType: Joi.string().required(),
        parameters: Joi.object().default({}),
        transformations: Joi.array().items(Joi.object()).default([]),
        weights: Joi.array().items(Joi.number()).default([]),
        activationFunctions: Joi.array().items(Joi.string()).default([]),
        structure: Joi.object().default({})
      }).required(),
      fitness: Joi.number().default(0),
      parent1Id: Joi.string().guid().allow(null),
      parent2Id: Joi.string().guid().allow(null),
      mutationInfo: Joi.object({
        type: Joi.string().valid('point', 'insert', 'delete', 'swap', 'crossover', 'none').default('none'),
        rate: Joi.number().min(0).max(1).default(0),
        strength: Joi.number().min(0).default(0),
        locations: Joi.array().items(Joi.number()).default([]),
        changes: Joi.array().items(Joi.object()).default([])
      }).default({}),
      crossoverInfo: Joi.object({
        type: Joi.string().valid('single_point', 'multi_point', 'uniform', 'none').default('none'),
        points: Joi.array().items(Joi.number()).default([]),
        parent1Contribution: Joi.number().min(0).max(1).default(0.5),
        parent2Contribution: Joi.number().min(0).max(1).default(0.5)
      }).default({}),
      populationId: Joi.string().guid().required(),
      species: Joi.string().max(100).allow(''),
      noveltyScore: Joi.number().min(0).default(0),
      complexity: Joi.number().min(0).default(0),
      diversity: Joi.number().min(0).max(1).default(0),
      evaluationTime: Joi.number().integer().min(0).default(0),
      algorithm: Joi.string().valid('genetic_programming', 'cma_es', 'nsga2', 'spea2', 'custom').allow(''),
      parameters: Joi.object({
        populationSize: Joi.number().integer().min(1).default(100),
        mutationRate: Joi.number().min(0).max(1).default(0.1),
        crossoverRate: Joi.number().min(0).max(1).default(0.8),
        tournamentSize: Joi.number().integer().min(1).default(5),
        elitismCount: Joi.number().integer().min(0).default(1),
        selectionMethod: Joi.string().valid('tournament', 'roulette', 'rank', 'uniform').default('tournament')
      }).default({}),
      metadata: Joi.object({
        experimentId: Joi.string().guid().allow(''),
        objectiveWeights: Joi.object().default({}),
        constraints: Joi.array().items(Joi.object()).default([]),
        dominance: Joi.array().items(Joi.string().guid()).default([]),
        crowdingDistance: Joi.number().min(0).default(0),
        rank: Joi.number().integer().min(0).default(0)
      }).default({}),
      createdAt: Joi.date().iso().default(() => new Date().toISOString()),
      updatedAt: Joi.date().iso().default(() => new Date().toISOString())
    });
  }

  static get indexes() {
    return [
      { name: 'idx_evolution_generation', columns: ['generation'] },
      { name: 'idx_evolution_fitness', columns: ['fitness'] },
      { name: 'idx_evolution_individual', columns: ['individualId'] },
      { name: 'idx_evolution_parents', columns: ['parent1Id', 'parent2Id'] },
      { name: 'idx_evolution_population', columns: ['populationId'] },
      { name: 'idx_evolution_species', columns: ['species'] },
      { name: 'idx_evolution_novelty', columns: ['noveltyScore'] },
      { name: 'idx_evolution_complexity', columns: ['complexity'] },
      { name: 'idx_evolution_diversity', columns: ['diversity'] },
      { name: 'idx_evolution_algorithm', columns: ['algorithm'] },
      { name: 'idx_evolution_generation_fitness', columns: ['generation', 'fitness'] }
    ];
  }

  validate() {
    super.validate();

    // Validate genome structure
    if (!this.genome.correlationType) {
      throw new Error('Genome must specify correlation type');
    }

    // Validate mutation info consistency
    if (this.mutationInfo.type === 'none' && this.mutationInfo.rate > 0) {
      throw new Error('Mutation rate must be 0 for no mutation type');
    }

    // Validate crossover info
    if (this.parent1Id && this.parent2Id && this.crossoverInfo.type === 'none') {
      throw new Error('Crossover type cannot be none when both parents exist');
    }

    return true;
  }

  updateFitness(newFitness) {
    this.fitness = newFitness;
    this.updatedAt = new Date().toISOString();
    return this;
  }

  addMutation(type, rate, strength, locations = [], changes = []) {
    this.mutationInfo = {
      type,
      rate,
      strength,
      locations,
      changes
    };
    this.updatedAt = new Date().toISOString();
    return this;
  }

  addCrossover(type, points, parent1Contribution = 0.5, parent2Contribution = 0.5) {
    this.crossoverInfo = {
      type,
      points,
      parent1Contribution,
      parent2Contribution
    };
    this.updatedAt = new Date().toISOString();
    return this;
  }

  updateNoveltyScore(score) {
    this.noveltyScore = Math.max(0, score);
    this.updatedAt = new Date().toISOString();
    return this;
  }

  updateComplexity(complexity) {
    this.complexity = Math.max(0, complexity);
    this.updatedAt = new Date().toISOString();
    return this;
  }

  updateDiversity(diversity) {
    this.diversity = Math.max(0, Math.min(1, diversity));
    this.updatedAt = new Date().toISOString();
    return this;
  }

  updateEvaluationTime(timeMs) {
    this.evaluationTime = timeMs;
    this.updatedAt = new Date().toISOString();
    return this;
  }

  isElite() {
    return this.metadata && this.metadata.rank === 0;
  }

  isDominatedBy(other) {
    if (!this.metadata || !other.metadata) return false;
    return this.metadata.dominance && this.metadata.dominance.includes(other.id);
  }

  getParetoRank() {
    return this.metadata ? this.metadata.rank : Infinity;
  }

  getCrowdingDistance() {
    return this.metadata ? this.metadata.crowdingDistance : 0;
  }

  getMutationCount() {
    return this.mutationInfo.changes ? this.mutationInfo.changes.length : 0;
  }

  getCrossoverPoints() {
    return this.crossoverInfo.points ? this.crossoverInfo.points.length : 0;
  }

  getParentContribution() {
    if (!this.parent1Id && !this.parent2Id) return 0;
    if (this.parent1Id && !this.parent2Id) return 1; // Cloning
    if (!this.parent1Id && this.parent2Id) return 1; // Cloning
    return this.crossoverInfo.parent1Contribution + this.crossoverInfo.parent2Contribution;
  }

  calculateAge(currentGeneration) {
    return currentGeneration - this.generation;
  }

  isFromSameParents(other) {
    if (!this.parent1Id || !this.parent2Id) return false;
    if (!other.parent1Id || !other.parent2Id) return false;

    const parents1 = [this.parent1Id, this.parent2Id].sort();
    const parents2 = [other.parent1Id, other.parent2Id].sort();

    return parents1[0] === parents2[0] && parents1[1] === parents2[1];
  }

  toJSON() {
    const json = super.toJSON();
    return {
      ...json,
      generation: parseInt(json.generation),
      fitness: parseFloat(json.fitness),
      noveltyScore: parseFloat(json.noveltyScore),
      complexity: parseFloat(json.complexity),
      diversity: parseFloat(json.diversity),
      evaluationTime: parseInt(json.evaluationTime),
      isElite: this.isElite(),
      paretoRank: this.getParetoRank(),
      crowdingDistance: this.getCrowdingDistance(),
      mutationCount: this.getMutationCount(),
      crossoverPoints: this.getCrossoverPoints(),
      parentContribution: this.getParentContribution()
    };
  }
}

module.exports = EvolutionRecord;