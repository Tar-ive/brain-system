import Joi from 'joi';

export const correlationDiscoverySchema = Joi.object({
  sourceDatasetId: Joi.string().required(),
  targetDatasetId: Joi.string().required(),
  correlationType: Joi.string()
    .valid('one_to_one', 'one_to_many', 'many_to_one', 'many_to_many', 'weighted_many_to_many', 'temporal', 'spatial', 'semantic')
    .default('one_to_one'),
  parameters: Joi.object({
    keyColumn: Joi.string().optional(),
    joinType: Joi.string().valid('inner', 'left', 'right', 'full').default('inner'),
    weightColumn: Joi.string().optional(),
    lagDays: Joi.number().min(0).max(365).optional(),
    aggregation: Joi.string().valid('sum', 'avg', 'count', 'max', 'min').optional(),
    spatialRelation: Joi.string().valid('contains', 'intersects', 'within').optional(),
    threshold: Joi.number().min(0).max(1).optional()
  }).default(),
  auxiliaryData: Joi.object().optional()
});

export const correlationQuerySchema = Joi.object({
  sourceDatasetId: Joi.string().optional(),
  targetDatasetId: Joi.string().optional(),
  correlationType: Joi.string()
    .valid('one_to_one', 'one_to_many', 'many_to_one', 'many_to_many', 'weighted_many_to_many', 'temporal', 'spatial', 'semantic')
    .optional(),
  minConfidence: Joi.number().min(0).max(1).optional(),
  limit: Joi.number().min(1).max(100).default(10),
  offset: Joi.number().min(0).default(0)
});

export const idParamSchema = Joi.object({
  id: Joi.string().required()
});

export const datasetSchema = Joi.object({
  name: Joi.string().required().min(1).max(255),
  description: Joi.string().optional().max(1000),
  columns: Joi.array().items(Joi.string()).required().min(1),
  rowCount: Joi.number().min(0).required(),
  metadata: Joi.object().optional()
});