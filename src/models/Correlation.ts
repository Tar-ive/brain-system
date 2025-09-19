import { v4 as uuidv4 } from 'uuid';

export interface Correlation {
  id: string;
  sourceDatasetId: string;
  targetDatasetId: string;
  correlationType: CorrelationType;
  parameters: CorrelationParameters;
  confidence: number;
  discoveredAt: string;
  version: number;
  parentCorrelationId?: string;
}

export type CorrelationType =
  | 'one_to_one'
  | 'one_to_many'
  | 'many_to_one'
  | 'many_to_many'
  | 'weighted_many_to_many'
  | 'temporal'
  | 'spatial'
  | 'semantic';

export interface CorrelationParameters {
  keyColumn?: string;
  joinType?: 'inner' | 'left' | 'right' | 'full';
  weightColumn?: string;
  lagDays?: number;
  aggregation?: 'sum' | 'avg' | 'count' | 'max' | 'min';
  spatialRelation?: 'contains' | 'intersects' | 'within';
  threshold?: number;
  [key: string]: any;
}

export interface ValidationResult {
  id: string;
  correlationId: string;
  validityScore: number;
  statisticalScore?: number;
  semanticScore?: number;
  structuralScore?: number;
  conservationError?: number;
  testAccuracy?: number;
  counterExamples?: any[];
  validatedAt: string;
}

export interface Dataset {
  id: string;
  name: string;
  description: string;
  columns: string[];
  rowCount: number;
  metadata: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

export class CorrelationModel {
  static create(data: Partial<Correlation>): Correlation {
    return {
      id: data.id || uuidv4(),
      sourceDatasetId: data.sourceDatasetId || '',
      targetDatasetId: data.targetDatasetId || '',
      correlationType: data.correlationType || 'one_to_one',
      parameters: data.parameters || {},
      confidence: data.confidence || 0,
      discoveredAt: data.discoveredAt || new Date().toISOString(),
      version: data.version || 1,
      parentCorrelationId: data.parentCorrelationId
    };
  }

  static validate(correlation: Partial<Correlation>): string[] {
    const errors: string[] = [];

    if (!correlation.sourceDatasetId) {
      errors.push('Source dataset ID is required');
    }

    if (!correlation.targetDatasetId) {
      errors.push('Target dataset ID is required');
    }

    if (!correlation.correlationType) {
      errors.push('Correlation type is required');
    }

    if (typeof correlation.confidence !== 'number' || correlation.confidence < 0 || correlation.confidence > 1) {
      errors.push('Confidence must be a number between 0 and 1');
    }

    return errors;
  }
}