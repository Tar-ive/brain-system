import { Router } from 'express';
import { CorrelationController } from '../controllers/CorrelationController';
import { validate, validateQuery, validateParams } from '../middleware/Validation';
import {
  correlationDiscoverySchema,
  correlationQuerySchema,
  idParamSchema,
  datasetSchema
} from '../schemas/validation';

const router = Router();
const controller = new CorrelationController();

// Correlation endpoints
router.post('/correlations/discover', validate(correlationDiscoverySchema), controller.discoverCorrelation);
router.get('/correlations', validateQuery(correlationQuerySchema), controller.getCorrelations);
router.get('/correlations/:id', validateParams(idParamSchema), controller.getCorrelation);
router.get('/correlations/:id/validation', validateParams(idParamSchema), controller.getValidation);
router.post('/correlations/:id/validate', validateParams(idParamSchema), controller.validateCorrelation);
router.delete('/correlations/:id', validateParams(idParamSchema), controller.deleteCorrelation);
router.get('/correlations/statistics', controller.getStatistics);

// Dataset endpoints
router.post('/datasets', validate(datasetSchema), controller.addDataset);
router.get('/datasets', controller.getDatasets);
router.get('/datasets/:id', validateParams(idParamSchema), controller.getDataset);

export default router;