// MongoDB initialization script
db = db.getSiblingDB('rest_api_db');

// Create collections with validation rules
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["username", "email", "password", "firstName", "lastName"],
      properties: {
        username: {
          bsonType: "string",
          description: "must be a string and is required"
        },
        email: {
          bsonType: "string",
          pattern: "^.+@.+\..+$",
          description: "must be a valid email address and is required"
        },
        password: {
          bsonType: "string",
          description: "must be a string and is required"
        },
        firstName: {
          bsonType: "string",
          description: "must be a string and is required"
        },
        lastName: {
          bsonType: "string",
          description: "must be a string and is required"
        },
        role: {
          bsonType: "string",
          enum: ["user", "admin", "moderator"],
          description: "can only be one of the enum values and is not required"
        },
        isActive: {
          bsonType: "bool",
          description: "must be a boolean and is not required"
        }
      }
    }
  }
});

db.createCollection('products', {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "price", "category", "stock", "createdBy", "updatedBy"],
      properties: {
        name: {
          bsonType: "string",
          description: "must be a string and is required"
        },
        description: {
          bsonType: "string",
          description: "must be a string and is not required"
        },
        price: {
          bsonType: "decimal",
          minimum: 0,
          description: "must be a positive number and is required"
        },
        category: {
          bsonType: "string",
          description: "must be a string and is required"
        },
        stock: {
          bsonType: "int",
          minimum: 0,
          description: "must be a non-negative integer and is required"
        },
        sku: {
          bsonType: "string",
          description: "must be a string and is not required"
        },
        images: {
          bsonType: "array",
          items: {
            bsonType: "string"
          },
          description: "must be an array of strings and is not required"
        },
        tags: {
          bsonType: "array",
          items: {
            bsonType: "string"
          },
          description: "must be an array of strings and is not required"
        },
        isActive: {
          bsonType: "bool",
          description: "must be a boolean and is not required"
        },
        createdBy: {
          bsonType: "objectId",
          description: "must be an objectId and is required"
        },
        updatedBy: {
          bsonType: "objectId",
          description: "must be an objectId and is required"
        }
      }
    }
  }
});

// Create indexes for better performance
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ username: 1 }, { unique: true });
db.users.createIndex({ role: 1 });
db.users.createIndex({ isActive: 1 });

db.products.createIndex({ name: "text", description: "text", category: "text", tags: "text" });
db.products.createIndex({ price: 1 });
db.products.createIndex({ category: 1 });
db.products.createIndex({ stock: 1 });
db.products.createIndex({ isActive: 1 });
db.products.createIndex({ createdBy: 1 });
db.products.createIndex({ createdAt: -1 });

print('Database initialization completed successfully');