import { v4 as uuidv4 } from 'uuid';

export const generateTestCorrelation = (overrides = {}) => ({
  id: uuidv4(),
  sourceDatasetId: 'test-source-1',
  targetDatasetId: 'test-target-1',
  correlationType: 'one_to_one',
  parameters: {
    keyColumn: 'id',
    joinType: 'inner'
  },
  confidence: 0.95,
  discoveredAt: new Date().toISOString(),
  version: 1,
  ...overrides
});

export const generateTestDataset = (overrides = {}) => ({
  id: uuidv4(),
  name: 'Test Dataset',
  description: 'Test dataset for correlation discovery',
  columns: ['id', 'name', 'value'],
  rowCount: 1000,
  metadata: {},
  createdAt: new Date().toISOString(),
  ...overrides
});

export const generateTestValidation = (overrides = {}) => ({
  id: uuidv4(),
  correlationId: uuidv4(),
  validityScore: 0.85,
  statisticalScore: 0.9,
  semanticScore: 0.8,
  structuralScore: 0.85,
  conservationError: 0.05,
  testAccuracy: 0.88,
  counterExamples: [],
  validatedAt: new Date().toISOString(),
  ...overrides
});

export const mockApiResponse = (data: any, status = 200) => ({
  status,
  data,
  message: 'Success'
});

export const mockApiError = (message: string, status = 400) => ({
  status,
  error: message,
  timestamp: new Date().toISOString()
});

export const createMockRequest = (overrides = {}) => ({
  body: {},
  params: {},
  query: {},
  headers: {},
  user: null,
  ...overrides
});

export const createMockResponse = () => {
  const res: any = {};
  res.status = jest.fn().mockReturnThis();
  res.json = jest.fn().mockReturnThis();
  res.send = jest.fn().mockReturnThis();
  res.setHeader = jest.fn().mockReturnThis();
  res.end = jest.fn().mockReturnThis();
  return res;
};

export const waitFor = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const generateLargeDataset = (size: number) => {
  const data = [];
  for (let i = 0; i < size; i++) {
    data.push({
      id: i,
      name: `Item ${i}`,
      value: Math.random() * 100,
      category: `Category ${Math.floor(Math.random() * 5)}`
    });
  }
  return data;
};