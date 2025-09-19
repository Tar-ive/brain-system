const { MongoClient } = require('mongodb');
const { v4: uuidv4 } = require('uuid');

// MongoDB connection configuration
const MONGO_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017';
const DB_NAME = process.env.MONGODB_DB_NAME || 'correlation_discovery';

// Collection schemas
const collectionSchemas = {
  datasets: {
    validator: {
      $jsonSchema: {
        bsonType: "object",
        required: ["name", "type", "format"],
        properties: {
          _id: { bsonType: "string" },
          id: { bsonType: "string" },
          name: { bsonType: "string", description: "Dataset name" },
          description: { bsonType: "string" },
          schema: { bsonType: "object" },
          type: {
            bsonType: "string",
            enum: ["structured", "semi-structured", "unstructured"]
          },
          source: { bsonType: "string" },
          format: {
            bsonType: "string",
            enum: ["json", "csv", "parquet", "xml", "avro", "binary"]
          },
          size: { bsonType: "long", minimum: 0 },
          recordCount: { bsonType: "long", minimum: 0 },
          metadata: { bsonType: "object" },
          status: {
            bsonType: "string",
            enum: ["active", "archived", "processing", "error"]
          },
          lastAccessed: { bsonType: "date" },
          tags: { bsonType: "array", items: { bsonType: "string" } },
          visibility: {
            bsonType: "string",
            enum: ["private", "public", "shared"]
          },
          ownerId: { bsonType: "string" },
          createdAt: { bsonType: "date" },
          updatedAt: { bsonType: "date" }
        }
      }
    }
  },
  correlations: {
    validator: {
      $jsonSchema: {
        bsonType: "object",
        required: ["sourceDatasetId", "targetDatasetId", "type"],
        properties: {
          _id: { bsonType: "string" },
          id: { bsonType: "string" },
          sourceDatasetId: { bsonType: "string" },
          targetDatasetId: { bsonType: "string" },
          type: {
            bsonType: "string",
            enum: [
              "one_to_one", "one_to_many", "many_to_one", "many_to_many",
              "weighted_many_to_many", "temporal", "spatial", "semantic",
              "statistical", "structural", "functional", "causal"
            ]
          },
          parameters: { bsonType: "object" },
          confidence: { bsonType: "double", minimum: 0, maximum: 1 },
          validityScore: { bsonType: "double", minimum: 0, maximum: 1 },
          description: { bsonType: "string" },
          status: {
            bsonType: "string",
            enum: ["proposed", "validated", "invalidated", "archived"]
          },
          parentCorrelationId: { bsonType: "string" },
          version: { bsonType: "int", minimum: 1 },
          tags: { bsonType: "array", items: { bsonType: "string" } },
          metadata: { bsonType: "object" },
          discoveryMethod: {
            bsonType: "string",
            enum: [
              "neural_network", "mcts", "evolutionary", "statistical",
              "information_theory", "manual", "hybrid"
            ]
          },
          lastValidated: { bsonType: "date" },
          createdAt: { bsonType: "date" },
          updatedAt: { bsonType: "date" }
        }
      }
    }
  },
  dataset_signatures: {
    validator: {
      $jsonSchema: {
        bsonType: "object",
        required: ["datasetId", "statistical", "semantic", "structural"],
        properties: {
          _id: { bsonType: "string" },
          id: { bsonType: "string" },
          datasetId: { bsonType: "string" },
          statistical: { bsonType: "object" },
          semantic: { bsonType: "object" },
          structural: { bsonType: "object" },
          temporal: { bsonType: "object" },
          spatial: { bsonType: "object" },
          version: { bsonType: "int", minimum: 1 },
          computedAt: { bsonType: "date" },
          expiresAt: { bsonType: "date" },
          metadata: { bsonType: "object" },
          computationTime: { bsonType: "long", minimum: 0 },
          algorithm: {
            bsonType: "string",
            enum: ["default", "neural", "statistical", "hybrid"]
          },
          compressionRatio: { bsonType: "double", minimum: 0, maximum: 1 },
          createdAt: { bsonType: "date" },
          updatedAt: { bsonType: "date" }
        }
      }
    }
  },
  validations: {
    validator: {
      $jsonSchema: {
        bsonType: "object",
        required: ["correlationId", "validityScore"],
        properties: {
          _id: { bsonType: "string" },
          id: { bsonType: "string" },
          correlationId: { bsonType: "string" },
          validityScore: { bsonType: "double", minimum: 0, maximum: 1 },
          statisticalScore: { bsonType: "double", minimum: 0, maximum: 1 },
          semanticScore: { bsonType: "double", minimum: 0, maximum: 1 },
          structuralScore: { bsonType: "double", minimum: 0, maximum: 1 },
          conservationError: { bsonType: "double", minimum: 0 },
          testAccuracy: { bsonType: "double", minimum: 0, maximum: 1 },
          confidenceInterval: { bsonType: "array", items: { bsonType: "double" } },
          counterExamples: { bsonType: "array" },
          validationMethod: {
            bsonType: "string",
            enum: ["statistical", "semantic", "structural", "conservation", "ensemble", "cross_validation"]
          },
          testCases: { bsonType: "array" },
          failureModes: { bsonType: "array" },
          metadata: { bsonType: "object" },
          validationTime: { bsonType: "long", minimum: 0 },
          dataSize: { bsonType: "long", minimum: 0 },
          sampleSize: { bsonType: "long", minimum: 0 },
          createdAt: { bsonType: "date" },
          updatedAt: { bsonType: "date" }
        }
      }
    }
  },
  training_episodes: {
    validator: {
      $jsonSchema: {
        bsonType: "object",
        required: ["episodeId", "stepNumber", "state", "action", "nextState"],
        properties: {
          _id: { bsonType: "string" },
          id: { bsonType: "string" },
          episodeId: { bsonType: "string" },
          stepNumber: { bsonType: "int", minimum: 0 },
          state: { bsonType: "object" },
          action: { bsonType: "object" },
          reward: { bsonType: "double" },
          nextState: { bsonType: "object" },
          done: { bsonType: "bool" },
          priority: { bsonType: "double", minimum: 0 },
          generatorModel: { bsonType: "string" },
          validatorModel: { bsonType: "string" },
          algorithm: {
            bsonType: "string",
            enum: ["mcts", "evolutionary", "neural", "ensemble"]
          },
          environment: { bsonType: "object" },
          metrics: { bsonType: "object" },
          metadata: { bsonType: "object" },
          experienceType: {
            bsonType: "string",
            enum: ["exploration", "exploitation", "training", "evaluation"]
          },
          createdAt: { bsonType: "date" },
          updatedAt: { bsonType: "date" }
        }
      }
    }
  },
  evolution_records: {
    validator: {
      $jsonSchema: {
        bsonType: "object",
        required: ["generation", "individualId", "genome", "populationId"],
        properties: {
          _id: { bsonType: "string" },
          id: { bsonType: "string" },
          generation: { bsonType: "int", minimum: 0 },
          individualId: { bsonType: "string" },
          genome: { bsonType: "object" },
          fitness: { bsonType: "double" },
          parent1Id: { bsonType: "string" },
          parent2Id: { bsonType: "string" },
          mutationInfo: { bsonType: "object" },
          crossoverInfo: { bsonType: "object" },
          populationId: { bsonType: "string" },
          species: { bsonType: "string" },
          noveltyScore: { bsonType: "double", minimum: 0 },
          complexity: { bsonType: "double", minimum: 0 },
          diversity: { bsonType: "double", minimum: 0, maximum: 1 },
          evaluationTime: { bsonType: "long", minimum: 0 },
          algorithm: {
            bsonType: "string",
            enum: ["genetic_programming", "cma_es", "nsga2", "spea2", "custom"]
          },
          parameters: { bsonType: "object" },
          metadata: { bsonType: "object" },
          createdAt: { bsonType: "date" },
          updatedAt: { bsonType: "date" }
        }
      }
    }
  },
  performance_metrics: {
    validator: {
      $jsonSchema: {
        bsonType: "object",
        required: ["metricType", "metricValue", "recordedAt"],
        properties: {
          _id: { bsonType: "string" },
          id: { bsonType: "string" },
          metricType: { bsonType: "string" },
          metricValue: { bsonType: "double" },
          metadata: { bsonType: "object" },
          recordedAt: { bsonType: "date" }
        }
      }
    }
  }
};

// Index definitions
const indexDefinitions = {
  datasets: [
    { name: "name", key: { name: 1 } },
    { name: "type", key: { type: 1 } },
    { name: "status", key: { status: 1 } },
    { name: "owner", key: { ownerId: 1 } },
    { name: "visibility", key: { visibility: 1 } },
    { name: "lastAccessed", key: { lastAccessed: -1 } },
    { name: "tags", key: { tags: 1 } },
    { name: "compound_search", key: { name: "text", description: "text" } }
  ],
  correlations: [
    { name: "source_target", key: { sourceDatasetId: 1, targetDatasetId: 1 } },
    { name: "type", key: { type: 1 } },
    { name: "confidence", key: { confidence: -1 } },
    { name: "status", key: { status: 1 } },
    { name: "validity", key: { validityScore: -1 } },
    { name: "parent", key: { parentCorrelationId: 1 } },
    { name: "method", key: { discoveryMethod: 1 } },
    { name: "created", key: { createdAt: -1 } },
    { name: "tags", key: { tags: 1 } }
  ],
  dataset_signatures: [
    { name: "dataset", key: { datasetId: 1 } },
    { name: "version", key: { datasetId: 1, version: 1 } },
    { name: "expires", key: { expiresAt: 1 } },
    { name: "computed", key: { computedAt: -1 } },
    { name: "algorithm", key: { algorithm: 1 } },
    { name: "compression", key: { compressionRatio: 1 } }
  ],
  validations: [
    { name: "correlation", key: { correlationId: 1 } },
    { name: "validity", key: { validityScore: -1 } },
    { name: "statistical", key: { statisticalScore: -1 } },
    { name: "semantic", key: { semanticScore: -1 } },
    { name: "structural", key: { structuralScore: -1 } },
    { name: "conservation", key: { conservationError: 1 } },
    { name: "accuracy", key: { testAccuracy: -1 } },
    { name: "method", key: { validationMethod: 1 } },
    { name: "created", key: { createdAt: -1 } }
  ],
  training_episodes: [
    { name: "episode", key: { episodeId: 1 } },
    { name: "step", key: { episodeId: 1, stepNumber: 1 } },
    { name: "reward", key: { reward: -1 } },
    { name: "priority", key: { priority: -1 } },
    { name: "type", key: { experienceType: 1 } },
    { name: "algorithm", key: { algorithm: 1 } },
    { name: "done", key: { done: 1 } },
    { name: "created", key: { createdAt: -1 } },
    { name: "models", key: { generatorModel: 1, validatorModel: 1 } }
  ],
  evolution_records: [
    { name: "generation", key: { generation: 1 } },
    { name: "fitness", key: { fitness: -1 } },
    { name: "individual", key: { individualId: 1 } },
    { name: "parents", key: { parent1Id: 1, parent2Id: 1 } },
    { name: "population", key: { populationId: 1 } },
    { name: "species", key: { species: 1 } },
    { name: "novelty", key: { noveltyScore: -1 } },
    { name: "complexity", key: { complexity: -1 } },
    { name: "diversity", key: { diversity: 1 } },
    { name: "algorithm", key: { algorithm: 1 } },
    { name: "generation_fitness", key: { generation: 1, fitness: -1 } }
  ],
  performance_metrics: [
    { name: "type_time", key: { metricType: 1, recordedAt: -1 } }
  ]
};

async function createCollections() {
  const client = new MongoClient(MONGO_URI);

  try {
    await client.connect();
    console.log('Connected to MongoDB');

    const db = client.db(DB_NAME);

    // Create collections with validators
    for (const [collectionName, schema] of Object.entries(collectionSchemas)) {
      try {
        await db.createCollection(collectionName, schema);
        console.log(`Created collection: ${collectionName}`);
      } catch (error) {
        if (error.code === 48) { // Collection already exists
          console.log(`Collection ${collectionName} already exists`);
        } else {
          throw error;
        }
      }
    }

    // Create indexes
    for (const [collectionName, indexes] of Object.entries(indexDefinitions)) {
      const collection = db.collection(collectionName);

      for (const index of indexes) {
        try {
          await collection.createIndex(index.key, {
            name: index.name,
            background: true,
            ...index.options
          });
          console.log(`Created index ${index.name} on ${collectionName}`);
        } catch (error) {
          console.warn(`Index ${index.name} on ${collectionName} already exists or failed:`, error.message);
        }
      }
    }

    // Create unique indexes
    await db.collection('correlations').createIndex(
      { sourceDatasetId: 1, targetDatasetId: 1, version: 1 },
      { unique: true, name: "unique_source_target_version" }
    );

    await db.collection('dataset_signatures').createIndex(
      { datasetId: 1, version: 1 },
      { unique: true, name: "unique_dataset_version" }
    );

    console.log('MongoDB collections and indexes created successfully');

  } catch (error) {
    console.error('Error creating MongoDB collections:', error);
    throw error;
  } finally {
    await client.close();
  }
}

// Run if called directly
if (require.main === module) {
  createCollections()
    .then(() => {
      console.log('Migration completed successfully');
      process.exit(0);
    })
    .catch(error => {
      console.error('Migration failed:', error);
      process.exit(1);
    });
}

module.exports = { createCollections, collectionSchemas, indexDefinitions };