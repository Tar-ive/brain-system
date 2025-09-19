import { Request, Response } from 'express';
import { CorrelationService } from '../services/CorrelationService';
import { asyncHandler } from '../middleware/ErrorHandler';
import { Logger } from '../utils/Logger';

const correlationService = new CorrelationService();
const logger = new Logger('CorrelationController');

export class CorrelationController {
  discoverCorrelation = asyncHandler(async (req: Request, res: Response) => {
    const { sourceDatasetId, targetDatasetId, correlationType, parameters, auxiliaryData } = req.body;

    logger.info('Discovering correlation', {
      sourceDatasetId,
      targetDatasetId,
      correlationType,
      userId: req.user?.id
    });

    const correlation = await correlationService.discoverCorrelation(
      sourceDatasetId,
      targetDatasetId,
      { correlationType, parameters, auxiliaryData }
    );

    res.status(201).json({
      success: true,
      data: correlation,
      message: 'Correlation discovered successfully'
    });
  });

  getCorrelation = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;

    logger.info('Getting correlation', { correlationId: id });

    const correlation = await correlationService.getCorrelation(id);

    if (!correlation) {
      return res.status(404).json({
        success: false,
        error: 'Correlation not found'
      });
    }

    res.json({
      success: true,
      data: correlation
    });
  });

  getCorrelations = asyncHandler(async (req: Request, res: Response) => {
    const filters = req.query;

    logger.info('Getting correlations', { filters });

    const result = await correlationService.getCorrelations({
      sourceDatasetId: filters.sourceDatasetId as string,
      targetDatasetId: filters.targetDatasetId as string,
      correlationType: filters.correlationType as any,
      minConfidence: filters.minConfidence ? parseFloat(filters.minConfidence as string) : undefined,
      limit: filters.limit ? parseInt(filters.limit as string) : undefined,
      offset: filters.offset ? parseInt(filters.offset as string) : undefined
    });

    res.json({
      success: true,
      data: result.correlations,
      pagination: {
        total: result.total,
        limit: parseInt(filters.limit as string) || 10,
        offset: parseInt(filters.offset as string) || 0
      }
    });
  });

  getValidation = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;

    logger.info('Getting validation', { correlationId: id });

    const validation = await correlationService.getValidation(id);

    if (!validation) {
      return res.status(404).json({
        success: false,
        error: 'Validation not found'
      });
    }

    res.json({
      success: true,
      data: validation
    });
  });

  validateCorrelation = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;

    logger.info('Validating correlation', { correlationId: id });

    const validation = await correlationService.validateCorrelation(id);

    res.json({
      success: true,
      data: validation,
      message: 'Correlation validated successfully'
    });
  });

  deleteCorrelation = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;

    logger.info('Deleting correlation', { correlationId: id });

    const deleted = await correlationService.deleteCorrelation(id);

    if (!deleted) {
      return res.status(404).json({
        success: false,
        error: 'Correlation not found'
      });
    }

    res.json({
      success: true,
      message: 'Correlation deleted successfully'
    });
  });

  getStatistics = asyncHandler(async (req: Request, res: Response) => {
    logger.info('Getting statistics');

    const stats = await correlationService.getStatistics();

    res.json({
      success: true,
      data: stats
    });
  });

  addDataset = asyncHandler(async (req: Request, res: Response) => {
    const datasetData = req.body;

    logger.info('Adding dataset', { name: datasetData.name });

    const dataset = await correlationService.addDataset({
      id: `dataset_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      ...datasetData,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    });

    res.status(201).json({
      success: true,
      data: dataset,
      message: 'Dataset added successfully'
    });
  });

  getDataset = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;

    logger.info('Getting dataset', { datasetId: id });

    const dataset = await correlationService.getDataset(id);

    if (!dataset) {
      return res.status(404).json({
        success: false,
        error: 'Dataset not found'
      });
    }

    res.json({
      success: true,
      data: dataset
    });
  });

  getDatasets = asyncHandler(async (req: Request, res: Response) => {
    logger.info('Getting all datasets');

    const datasets = await correlationService.getDatasets();

    res.json({
      success: true,
      data: datasets
    });
  });
}