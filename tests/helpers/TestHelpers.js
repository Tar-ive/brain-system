const { v4: uuidv4 } = require('uuid');
const Dataset = require('../../src/models/Dataset');
const Correlation = require('../../src/models/Correlation');
const Validation = require('../../src/models/Validation');

class TestHelpers {
  /**
   * Generate test dataset data
   * @param {Object} overrides - Override default values
   * @returns {Object} Test dataset data
   */
  static generateTestDataset(overrides = {}) {
    const baseData = {
      name: 'Test Dataset',
      description: 'A test dataset for unit testing',
      type: 'structured',
      source: 'test',
      format: 'json',
      size: 1024,
      recordCount: 100,
      schema: {
        fields: [
          { name: 'id', type: 'string' },
          { name: 'name', type: 'string' },
          { name: 'value', type: 'number' }
        ]
      },
      tags: ['test', 'unit'],
      visibility: 'public'
    };

    return { ...baseData, ...overrides };
  }

  /**
   * Generate test correlation data
   * @param {string} sourceDatasetId - Source dataset ID
   * @param {string} targetDatasetId - Target dataset ID
   * @param {Object} overrides - Override default values
   * @returns {Object} Test correlation data
   */
  static generateTestCorrelation(sourceDatasetId, targetDatasetId, overrides = {}) {
    const baseData = {
      sourceDatasetId,
      targetDatasetId,
      type: 'one_to_many',
      parameters: {
        strength: 0.85,
        direction: 'positive',
        lag: 2
      },
      confidence: 0.85,
      validityScore: 0.78,
      description: 'Test correlation between datasets',
      status: 'validated',
      discoveryMethod: 'neural_network',
      tags: ['test', 'correlation']
    };

    return { ...baseData, ...overrides };
  }

  /**
   * Generate test validation data
   * @param {string} correlationId - Correlation ID
   * @param {Object} overrides - Override default values
   * @returns {Object} Test validation data
   */
  static generateTestValidation(correlationId, overrides = {}) {
    const baseData = {
      correlationId,
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
      sampleSize: 1000
    };

    return { ...baseData, ...overrides };
  }

  /**
   * Generate multiple test datasets
   * @param {number} count - Number of datasets to generate
   * @param {Object} baseOverrides - Base overrides to apply to all datasets
   * @returns {Array<Object>} Array of test dataset data
   */
  static generateTestDatasets(count = 3, baseOverrides = {}) {
    const datasets = [];

    for (let i = 0; i < count; i++) {
      const overrides = {
        ...baseOverrides,
        name: `Test Dataset ${i + 1}`,
        description: `Test dataset ${i + 1} for unit testing`,
        size: 1024 * (i + 1),
        recordCount: 100 * (i + 1),
        format: ['json', 'csv', 'xml'][i % 3],
        type: ['structured', 'unstructured'][i % 2]
      };

      datasets.push(this.generateTestDataset(overrides));
    }

    return datasets;
  }

  /**
   * Generate multiple test correlations
   * @param {Array<string>} datasetIds - Array of dataset IDs
   * @param {Object} baseOverrides - Base overrides to apply to all correlations
   * @returns {Array<Object>} Array of test correlation data
   */
  static generateTestCorrelations(datasetIds, baseOverrides = {}) {
    const correlations = [];
    const correlationTypes = [
      'one_to_one', 'one_to_many', 'many_to_one', 'many_to_many',
      'weighted_many_to_many', 'temporal', 'spatial', 'semantic'
    ];

    for (let i = 0; i < Math.min(datasetIds.length - 1, 5); i++) {
      for (let j = i + 1; j < Math.min(datasetIds.length, 6); j++) {
        const overrides = {
          ...baseOverrides,
          sourceDatasetId: datasetIds[i],
          targetDatasetId: datasetIds[j],
          type: correlationTypes[(i + j) % correlationTypes.length],
          confidence: 0.6 + (Math.random() * 0.3), // 0.6-0.9
          validityScore: 0.5 + (Math.random() * 0.4), // 0.5-0.9
          description: `Test correlation between dataset ${i + 1} and ${j + 1}`,
          discoveryMethod: ['neural_network', 'statistical', 'evolutionary'][(i + j) % 3]
        };

        correlations.push(this.generateTestCorrelation(
          overrides.sourceDatasetId,
          overrides.targetDatasetId,
          overrides
        ));
      }
    }

    return correlations;
  }

  /**
   * Generate multiple test validations
   * @param {Array<string>} correlationIds - Array of correlation IDs
   * @param {Object} baseOverrides - Base overrides to apply to all validations
   * @returns {Array<Object>} Array of test validation data
   */
  static generateTestValidations(correlationIds, baseOverrides = {}) {
    const validations = [];
    const validationMethods = ['statistical', 'semantic', 'structural', 'conservation', 'ensemble'];

    correlationIds.forEach((correlationId, index) => {
      const overrides = {
        ...baseOverrides,
        correlationId,
        validityScore: 0.6 + (Math.random() * 0.3), // 0.6-0.9
        statisticalScore: 0.5 + (Math.random() * 0.4),
        semanticScore: 0.5 + (Math.random() * 0.4),
        structuralScore: 0.5 + (Math.random() * 0.4),
        validationMethod: validationMethods[index % validationMethods.length],
        validationTime: 1000 + (Math.random() * 4000), // 1-5 seconds
        dataSize: 5000 + (Math.random() * 15000), // 5-20k records
        sampleSize: 100 + (Math.random() * 900) // 100-1000 samples
      };

      validations.push(this.generateTestValidation(correlationId, overrides));
    });

    return validations;
  }

  /**
   * Create a complete test dataset with correlations and validations
   * @param {number} datasetCount - Number of datasets to create
   * @returns {Promise<Object>} Object containing datasets, correlations, and validations
   */
  static async createCompleteTestData(datasetCount = 3) {
    const datasets = this.generateTestDatasets(datasetCount);
    const datasetIds = datasets.map(d => d.id);

    const correlations = this.generateTestCorrelations(datasetIds);
    const correlationIds = correlations.map(c => c.id);

    const validations = this.generateTestValidations(correlationIds);

    return {
      datasets,
      correlations,
      validations,
      datasetIds,
      correlationIds
    };
  }

  /**
   * Generate random UUID for testing
   * @returns {string} Random UUID
   */
  static generateUUID() {
    return uuidv4();
  }

  /**
   * Generate random test data with specified schema
   * @param {Object} schema - Data schema to generate
   * @param {number} count - Number of records to generate
   * @returns {Array<Object>} Generated test data
   */
  static generateRandomData(schema, count = 10) {
    const data = [];

    for (let i = 0; i < count; i++) {
      const record = {};

      Object.keys(schema).forEach(field => {
        const type = schema[field];

        switch (type) {
          case 'string':
            record[field] = `test_${field}_${i}`;
            break;
          case 'number':
            record[field] = Math.random() * 1000;
            break;
          case 'integer':
            record[field] = Math.floor(Math.random() * 1000);
            break;
          case 'boolean':
            record[field] = Math.random() > 0.5;
            break;
          case 'date':
            record[field] = new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString();
            break;
          case 'array':
            record[field] = Array.from({ length: 3 }, (_, j) => `item_${j}`);
            break;
          case 'object':
            record[field] = { nested: `value_${i}` };
            break;
          default:
            record[field] = null;
        }
      });

      data.push(record);
    }

    return data;
  }

  /**
   * Create test datasets with various characteristics
   * @returns {Array<Object>} Datasets with different characteristics
   */
  static createVariedTestDatasets() {
    return [
      // Large structured dataset
      this.generateTestDataset({
        name: 'Large Structured Dataset',
        type: 'structured',
        format: 'json',
        size: 1024 * 1024 * 10, // 10MB
        recordCount: 100000,
        tags: ['large', 'structured', 'production']
      }),

      // Small unstructured dataset
      this.generateTestDataset({
        name: 'Small Unstructured Dataset',
        type: 'unstructured',
        format: 'json',
        size: 1024, // 1KB
        recordCount: 10,
        tags: ['small', 'unstructured', 'test']
      }),

      // Medium CSV dataset
      this.generateTestDataset({
        name: 'Medium CSV Dataset',
        type: 'structured',
        format: 'csv',
        size: 1024 * 100, // 100KB
        recordCount: 5000,
        tags: ['medium', 'csv', 'structured']
      }),

      // Time series dataset
      this.generateTestDataset({
        name: 'Time Series Dataset',
        type: 'structured',
        format: 'json',
        size: 1024 * 500, // 500KB
        recordCount: 10000,
        tags: ['time-series', 'temporal', 'structured']
      }),

      // Geographic dataset
      this.generateTestDataset({
        name: 'Geographic Dataset',
        type: 'structured',
        format: 'json',
        size: 1024 * 200, // 200KB
        recordCount: 5000,
        tags: ['geographic', 'spatial', 'structured']
      })
    ];
  }

  /**
   * Create test correlations with different types and characteristics
   * @param {Array<string>} datasetIds - Array of dataset IDs
   * @returns {Array<Object>} Various test correlations
   */
  static createVariedTestCorrelations(datasetIds) {
    if (datasetIds.length < 2) return [];

    return [
      // High confidence one-to-one
      this.generateTestCorrelation(datasetIds[0], datasetIds[1], {
        type: 'one_to_one',
        confidence: 0.95,
        validityScore: 0.92,
        description: 'High confidence one-to-one mapping',
        discoveryMethod: 'neural_network'
      }),

      // Many-to-many with medium confidence
      this.generateTestCorrelation(datasetIds[1], datasetIds[2], {
        type: 'many_to_many',
        confidence: 0.75,
        validityScore: 0.70,
        description: 'Medium confidence many-to-many relationship',
        discoveryMethod: 'statistical'
      }),

      // Temporal correlation
      this.generateTestCorrelation(datasetIds[0], datasetIds[2], {
        type: 'temporal',
        confidence: 0.82,
        validityScore: 0.78,
        description: 'Temporal correlation with time lag',
        discoveryMethod: 'information_theory',
        parameters: {
          timeLag: 5,
          seasonality: true,
          trend: 'increasing'
        }
      }),

      // Spatial correlation
      this.generateTestCorrelation(datasetIds[1], datasetIds[3], {
        type: 'spatial',
        confidence: 0.88,
        validityScore: 0.85,
        description: 'Spatial geographic correlation',
        discoveryMethod: 'evolutionary',
        parameters: {
          distance: 100,
          spatialWeight: 0.7,
          clustering: true
        }
      }),

      // Semantic correlation
      this.generateTestCorrelation(datasetIds[2], datasetIds[4], {
        type: 'semantic',
        confidence: 0.79,
        validityScore: 0.76,
        description: 'Semantic similarity correlation',
        discoveryMethod: 'neural_network',
        parameters: {
          similarity: 0.85,
          embedding: 'word2vec',
          threshold: 0.7
        }
      })
    ];
  }

  /**
   * Wait for specified time (useful for testing timestamps)
   * @param {number} ms - Milliseconds to wait
   * @returns {Promise<void>}
   */
  static async wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Measure execution time of a function
   * @param {Function} fn - Function to measure
   * @returns {Promise<{result: any, time: number}>} Result and execution time
   */
  static async measureTime(fn) {
    const startTime = Date.now();
    const result = await fn();
    const endTime = Date.now();

    return {
      result,
      time: endTime - startTime
    };
  }

  /**
   * Create test data with invalid values for validation testing
   * @returns {Object} Invalid test data
   */
  static createInvalidTestData() {
    return {
      // Invalid datasets
      invalidDatasets: [
        {}, // Empty object
        { name: '' }, // Empty name
        { name: 'Test', type: 'invalid_type' }, // Invalid type
        { name: 'Test', type: 'structured', format: 'invalid_format' }, // Invalid format
        { name: 'Test', type: 'structured', format: 'json', size: -100 }, // Negative size
        { name: 'Test', type: 'structured', format: 'json', recordCount: -1 }, // Negative record count
      ],

      // Invalid correlations
      invalidCorrelations: [
        {}, // Empty object
        { sourceDatasetId: uuidv4() }, // Missing targetDatasetId
        { targetDatasetId: uuidv4() }, // Missing sourceDatasetId
        { sourceDatasetId: uuidv4(), targetDatasetId: uuidv4(), type: 'invalid_type' }, // Invalid type
        { sourceDatasetId: uuidv4(), targetDatasetId: uuidv4(), type: 'one_to_one', confidence: 1.5 }, // Invalid confidence
        { sourceDatasetId: uuidv4(), targetDatasetId: uuidv4(), type: 'one_to_one', confidence: -0.1 }, // Negative confidence
      ],

      // Invalid validations
      invalidValidations: [
        {}, // Empty object
        { correlationId: uuidv4() }, // Missing scores
        { correlationId: uuidv4(), validityScore: 1.5 }, // Invalid validity score
        { correlationId: uuidv4(), validityScore: -0.1 }, // Negative validity score
        { correlationId: uuidv4(), validityScore: 0.8, confidenceInterval: [0.9, 0.8] }, // Invalid confidence interval
      ]
    };
  }

  /**
   * Generate test data for performance benchmarks
   * @param {number} scale - Scale factor (1 = normal, 10 = 10x data)
   * @returns {Object} Performance test data
   */
  static generatePerformanceTestData(scale = 1) {
    const baseCount = 100 * scale;
    const datasets = [];
    const correlations = [];
    const validations = [];

    // Generate datasets
    for (let i = 0; i < baseCount; i++) {
      datasets.push(this.generateTestDataset({
        name: `Performance Dataset ${i}`,
        size: 1024 * (i + 1),
        recordCount: 100 * (i + 1),
        tags: [`perf_tag${i % 20}`, `category${i % 5}`]
      }));
    }

    const datasetIds = datasets.map(d => d.id);

    // Generate correlations (about 20% of possible pairs)
    for (let i = 0; i < datasetIds.length; i++) {
      for (let j = i + 1; j < Math.min(datasetIds.length, i + 10); j++) {
        if (Math.random() < 0.2) { // 20% chance
          correlations.push(this.generateTestCorrelation(datasetIds[i], datasetIds[j], {
            confidence: 0.5 + Math.random() * 0.4,
            validityScore: 0.4 + Math.random() * 0.5
          }));
        }
      }
    }

    // Generate validations for all correlations
    const correlationIds = correlations.map(c => c.id);
    correlationIds.forEach(correlationId => {
      validations.push(this.generateTestValidation(correlationId));
    });

    return {
      datasets,
      correlations,
      validations,
      scale
    };
  }
}

module.exports = TestHelpers;