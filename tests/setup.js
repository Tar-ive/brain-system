const chai = require('chai');
const chaiHttp = require('chai-http');
const { MongoMemoryServer } = require('mongodb-memory-server');
const testDbManager = require('./database/TestDatabaseManager');

// Configure chai
chai.use(chaiHttp);
global.expect = chai.expect;

// Test configuration
global.testConfig = {
  // Test database settings
  testDatabases: {
    postgres: {
      host: process.env.TEST_DB_HOST || 'localhost',
      port: parseInt(process.env.TEST_DB_PORT) || 5433,
      database: 'test_correlation_discovery',
      user: process.env.TEST_DB_USER || 'test_user',
      password: process.env.TEST_DB_PASSWORD || 'test_password'
    },
    mongo: {
      uri: process.env.TEST_MONGODB_URI || 'mongodb://localhost:27018',
      database: 'test_correlation_discovery'
    }
  },

  // Test timeouts
  timeouts: {
    connection: 10000,
    query: 5000,
    test: 30000
  },

  // Test data sizes
  testDataSizes: {
    small: 10,
    medium: 50,
    large: 100,
    xlarge: 1000
  }
};

// Global test hooks
let mongoServer;

// Before all tests
before(async function() {
  this.timeout(testConfig.timeouts.connection);

  try {
    // Setup in-memory MongoDB for testing if not using external test database
    if (!process.env.TEST_MONGODB_URI) {
      mongoServer = await MongoMemoryServer.create();
      const mongoUri = mongoServer.getUri();
      process.env.TEST_MONGODB_URI = mongoUri;
      console.log(`MongoDB Memory Server started at: ${mongoUri}`);
    }

    // Initialize test database manager
    await testDbManager.connect();
    console.log('Test database manager connected');

    // Setup test databases
    await testDbManager.setupTestDatabases();
    console.log('Test databases setup completed');

  } catch (error) {
    console.error('Test setup failed:', error);
    throw error;
  }
});

// After all tests
after(async function() {
  this.timeout(testConfig.timeouts.connection);

  try {
    // Cleanup test databases
    await testDbManager.clearAllTables();
    console.log('Test databases cleared');

    // Disconnect from test databases
    await testDbManager.disconnect();
    console.log('Test database manager disconnected');

    // Shutdown MongoDB Memory Server
    if (mongoServer) {
      await mongoServer.stop();
      console.log('MongoDB Memory Server stopped');
    }

  } catch (error) {
    console.error('Test cleanup failed:', error);
    throw error;
  }
});

// Before each test
beforeEach(async function() {
  this.timeout(testConfig.timeouts.query);

  try {
    // Clear all test tables before each test
    await testDbManager.clearAllTables();
  } catch (error) {
    console.error('BeforeEach cleanup failed:', error);
    throw error;
  }
});

// After each test
afterEach(async function() {
  try {
    // Optional: Run health check after each test
    const health = await testDbManager.runHealthCheck();

    // Log any connection issues
    if (health.postgres && !health.postgres.connected) {
      console.warn('PostgreSQL connection issue detected after test');
    }
    if (health.mongo && !health.mongo.connected) {
      console.warn('MongoDB connection issue detected after test');
    }
  } catch (error) {
    console.error('AfterEach health check failed:', error);
    // Don't throw error here to avoid failing tests due to health check issues
  }
});

// Global test utilities
global.testUtils = {
  /**
   * Wait for specified time
   * @param {number} ms - Milliseconds to wait
   */
  wait: (ms) => new Promise(resolve => setTimeout(resolve, ms)),

  /**
   * Measure execution time
   * @param {Function} fn - Function to measure
   * @returns {Promise<{result: any, time: number}>}
   */
  measureTime: async (fn) => {
    const start = Date.now();
    const result = await fn();
    const end = Date.now();
    return { result, time: end - start };
  },

  /**
   * Generate test data
   * @param {string} type - Type of test data ('dataset', 'correlation', 'validation')
   * @param {Object} overrides - Override values
   * @returns {Object} Generated test data
   */
  generateTestData: (type, overrides = {}) => {
    const { v4: uuidv4 } = require('uuid');
    const now = new Date().toISOString();

    switch (type) {
      case 'dataset':
        return {
          name: 'Test Dataset',
          description: 'Test description',
          type: 'structured',
          source: 'test',
          format: 'json',
          size: 1024,
          recordCount: 100,
          schema: { fields: [{ name: 'id', type: 'string' }] },
          tags: ['test'],
          visibility: 'public',
          createdAt: now,
          updatedAt: now,
          ...overrides
        };

      case 'correlation':
        return {
          sourceDatasetId: uuidv4(),
          targetDatasetId: uuidv4(),
          type: 'one_to_many',
          confidence: 0.85,
          validityScore: 0.78,
          description: 'Test correlation',
          status: 'validated',
          discoveryMethod: 'neural_network',
          parameters: {},
          tags: ['test'],
          createdAt: now,
          updatedAt: now,
          ...overrides
        };

      case 'validation':
        return {
          correlationId: uuidv4(),
          validityScore: 0.88,
          statisticalScore: 0.85,
          semanticScore: 0.90,
          structuralScore: 0.87,
          conservationError: 0.05,
          testAccuracy: 0.92,
          confidenceInterval: [0.85, 0.95],
          validationMethod: 'statistical',
          validationTime: 1500,
          dataSize: 10000,
          sampleSize: 1000,
          createdAt: now,
          updatedAt: now,
          ...overrides
        };

      default:
        throw new Error(`Unknown test data type: ${type}`);
    }
  },

  /**
   * Create test data with relationships
   * @param {number} datasetCount - Number of datasets to create
   * @returns {Promise<Object>} Related test data
   */
  createRelatedTestData: async (datasetCount = 3) => {
    const DatasetRepository = require('../src/repositories/DatasetRepository');
    const CorrelationRepository = require('../src/repositories/CorrelationRepository');
    const ValidationRepository = require('../src/repositories/ValidationRepository');
    const dbManager = require('../src/utils/database');

    const datasetRepo = new DatasetRepository(dbManager);
    const correlationRepo = new CorrelationRepository(dbManager);
    const validationRepo = new ValidationRepository(dbManager);

    const datasets = [];
    const correlations = [];
    const validations = [];

    // Create datasets
    for (let i = 0; i < datasetCount; i++) {
      const dataset = await datasetRepo.create({
        name: `Related Dataset ${i + 1}`,
        type: 'structured',
        format: 'json',
        size: 1024 * (i + 1),
        recordCount: 100 * (i + 1)
      });
      datasets.push(dataset);
    }

    // Create correlations between datasets
    for (let i = 0; i < datasets.length - 1; i++) {
      const correlation = await correlationRepo.create({
        sourceDatasetId: datasets[i].id,
        targetDatasetId: datasets[i + 1].id,
        type: 'one_to_many',
        confidence: 0.8 - (i * 0.1),
        validityScore: 0.75 - (i * 0.05)
      });
      correlations.push(correlation);

      // Create validation for each correlation
      const validation = await validationRepo.create({
        correlationId: correlation.id,
        validityScore: 0.8 - (i * 0.05),
        statisticalScore: 0.75 - (i * 0.03),
        semanticScore: 0.85 - (i * 0.02),
        structuralScore: 0.8 - (i * 0.04)
      });
      validations.push(validation);
    }

    return {
      datasets,
      correlations,
      validations,
      datasetRepo,
      correlationRepo,
      validationRepo
    };
  },

  /**
   * Verify database state after operations
   * @param {Object} expectedCounts - Expected counts for each entity type
   * @returns {Promise<Object>} Actual counts
   */
  verifyDatabaseState: async (expectedCounts = {}) => {
    const DatasetRepository = require('../src/repositories/DatasetRepository');
    const CorrelationRepository = require('../src/repositories/CorrelationRepository');
    const ValidationRepository = require('../src/repositories/ValidationRepository');
    const dbManager = require('../src/utils/database');

    const datasetRepo = new DatasetRepository(dbManager);
    const correlationRepo = new CorrelationRepository(dbManager);
    const validationRepo = new ValidationRepository(dbManager);

    const actualCounts = {
      datasets: await datasetRepo.count(),
      correlations: await correlationRepo.count(),
      validations: await validationRepo.count()
    };

    // Verify expected counts if provided
    Object.keys(expectedCounts).forEach(entity => {
      if (expectedCounts[entity] !== undefined) {
        expect(actualCounts[entity]).to.equal(
          expectedCounts[entity],
          `Expected ${expectedCounts[entity]} ${entity}, but found ${actualCounts[entity]}`
        );
      }
    });

    return actualCounts;
  },

  /**
   * Clean up test data
   * @param {Array<string>} ids - Array of IDs to clean up
   * @param {string} type - Type of entity to clean up
   */
  cleanupTestData: async (ids, type) => {
    try {
      if (!ids || ids.length === 0) return;

      const dbManager = require('../src/utils/database');

      switch (type) {
        case 'dataset':
          const DatasetRepository = require('../src/repositories/DatasetRepository');
          const datasetRepo = new DatasetRepository(dbManager);
          for (const id of ids) {
            await datasetRepo.delete(id);
          }
          break;

        case 'correlation':
          const CorrelationRepository = require('../src/repositories/CorrelationRepository');
          const correlationRepo = new CorrelationRepository(dbManager);
          for (const id of ids) {
            await correlationRepo.delete(id);
          }
          break;

        case 'validation':
          const ValidationRepository = require('../src/repositories/ValidationRepository');
          const validationRepo = new ValidationRepository(dbManager);
          for (const id of ids) {
            await validationRepo.delete(id);
          }
          break;
      }
    } catch (error) {
      console.error(`Cleanup failed for ${type}:`, error);
      // Don't throw error to avoid failing tests due to cleanup issues
    }
  }
};

// Console output helpers
global.testOutput = {
  /**
   * Log test start with separator
   * @param {string} testName - Name of the test
   */
  testStart: (testName) => {
    console.log('\n' + '='.repeat(60));
    console.log(`🧪 Starting Test: ${testName}`);
    console.log('='.repeat(60));
  },

  /**
   * Log test completion
   * @param {string} testName - Name of the test
   * @param {number} duration - Test duration in ms
   */
  testComplete: (testName, duration) => {
    console.log('✅'.repeat(15));
    console.log(`✅ Test Completed: ${testName} (${duration}ms)`);
    console.log('✅'.repeat(15));
  },

  /**
   * Log test section
   * @param {string} sectionName - Name of the section
   */
  section: (sectionName) => {
    console.log('\n' + '-'.repeat(40));
    console.log(`📋 ${sectionName}`);
    console.log('-'.repeat(40));
  },

  /**
   * Log performance metrics
   * @param {string} operation - Operation name
   * @param {number} time - Execution time in ms
   * @param {Object} additional - Additional metrics
   */
  performance: (operation, time, additional = {}) => {
    console.log(`⚡ ${operation}: ${time}ms`);
    Object.keys(additional).forEach(key => {
      console.log(`   - ${key}: ${additional[key]}`);
    });
  }
};

// Error handling helpers
global.testErrors = {
  /**
   * Expect error with specific message
   * @param {Promise} promise - Promise that should reject
   * @param {string|RegExp} expectedMessage - Expected error message
   */
  expectError: async (promise, expectedMessage) => {
    try {
      await promise;
      expect.fail('Expected promise to reject, but it resolved');
    } catch (error) {
      if (typeof expectedMessage === 'string') {
        expect(error.message).to.include(expectedMessage);
      } else if (expectedMessage instanceof RegExp) {
        expect(error.message).to.match(expectedMessage);
      }
    }
  },

  /**
   * Expect validation error
   * @param {Promise} promise - Promise that should reject with validation error
   * @param {string} expectedField - Expected field that failed validation
   */
  expectValidationError: async (promise, expectedField) => {
    try {
      await promise;
      expect.fail('Expected validation error, but promise resolved');
    } catch (error) {
      expect(error.message).to.include('validation failed');
      if (expectedField) {
        expect(error.message).to.include(expectedField);
      }
    }
  }
};

console.log('🧪 Test environment initialized');
console.log(`📊 Test config: ${JSON.stringify(testConfig, null, 2)}`);