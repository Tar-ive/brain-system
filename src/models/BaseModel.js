const { v4: uuidv4 } = require('uuid');
const Joi = require('joi');
const moment = require('moment');
const _ = require('lodash');

class BaseModel {
  constructor(data = {}) {
    this.id = data.id || uuidv4();
    this.createdAt = data.createdAt || new Date().toISOString();
    this.updatedAt = data.updatedAt || new Date().toISOString();

    // Copy properties from data
    Object.assign(this, data);
  }

  static get tableName() {
    throw new Error('tableName must be implemented by subclass');
  }

  static get schema() {
    throw new Error('schema must be implemented by subclass');
  }

  static get indexes() {
    return [];
  }

  validate() {
    const { error, value } = this.constructor.schema.validate(this, {
      stripUnknown: true,
      abortEarly: false,
      allowUnknown: true
    });

    if (error) {
      throw new Error(`Validation failed: ${error.details.map(d => d.message).join(', ')}`);
    }

    return value;
  }

  toJSON() {
    const json = {};
    const schema = this.constructor.schema.describe();

    Object.keys(schema.keys).forEach(key => {
      if (this[key] !== undefined) {
        json[key] = this[key];
      }
    });

    return json;
  }

  toDatabase() {
    const data = this.toJSON();

    // Convert Date objects to ISO strings
    Object.keys(data).forEach(key => {
      if (data[key] instanceof Date) {
        data[key] = data[key].toISOString();
      }
    });

    return data;
  }

  static fromDatabase(data) {
    if (!data) return null;
    return new this(data);
  }

  update(data) {
    const keys = Object.keys(this.constructor.schema.describe().keys);

    keys.forEach(key => {
      if (data[key] !== undefined) {
        this[key] = data[key];
      }
    });

    this.updatedAt = new Date().toISOString();
    return this;
  }

  static createValidationSchema(fields) {
    const schema = {};

    fields.forEach(field => {
      let joiField = Joi;

      // Handle type conversion
      switch (field.type) {
        case 'uuid':
          joiField = joiField.string().guid({ version: 'uuidv4' });
          break;
        case 'string':
          joiField = joiField.string();
          break;
        case 'integer':
          joiField = joiField.number().integer();
          break;
        case 'float':
        case 'decimal':
          joiField = joiField.number();
          break;
        case 'boolean':
          joiField = joiField.boolean();
          break;
        case 'json':
        case 'jsonb':
          joiField = joiField.object();
          break;
        case 'date':
        case 'timestamp':
          joiField = joiField.date().iso();
          break;
        case 'array':
          joiField = joiField.array();
          break;
        default:
          joiField = joiField.any();
      }

      // Apply constraints
      if (field.required) {
        joiField = joiField.required();
      } else {
        joiField = joiField.optional().allow(null);
      }

      if (field.defaultValue !== undefined) {
        joiField = joiField.default(field.defaultValue);
      }

      if (field.min !== undefined) {
        joiField = joiField.min(field.min);
      }

      if (field.max !== undefined) {
        joiField = joiField.max(field.max);
      }

      if (field.pattern) {
        joiField = joiField.pattern(new RegExp(field.pattern));
      }

      if (field.enum) {
        joiField = joiField.valid(...field.enum);
      }

      schema[field.name] = joiField;
    });

    return Joi.object(schema);
  }

  static generateSQLSchema() {
    const columns = [];
    const fields = this.constructor.schema.describe().keys;

    Object.entries(fields).forEach(([name, field]) => {
      let columnType = this.getSQLType(field);
      let constraints = [];

      if (field.flags?.presence === 'required') {
        constraints.push('NOT NULL');
      }

      if (field.flags?.default !== undefined) {
        const defaultValue = this.getSQLDefaultValue(field.flags.default);
        if (defaultValue !== null) {
          constraints.push(`DEFAULT ${defaultValue}`);
        }
      }

      columns.push(`${name} ${columnType}${constraints.length > 0 ? ' ' + constraints.join(' ') : ''}`);
    });

    return columns.join(',\n    ');
  }

  static getSQLType(field) {
    const type = field.type;
    const rules = field.rules;

    switch (type) {
      case 'string':
        const maxLength = rules?.find(r => r.name === 'max')?.args?.[0] || 255;
        return `VARCHAR(${maxLength})`;
      case 'number':
        if (rules?.find(r => r.name === 'integer')) {
          return 'INTEGER';
        }
        return 'DECIMAL(20, 10)';
      case 'boolean':
        return 'BOOLEAN';
      case 'date':
        return 'TIMESTAMP';
      case 'array':
        return 'JSONB';
      case 'object':
        return 'JSONB';
      default:
        return 'TEXT';
    }
  }

  static getSQLDefaultValue(defaultValue) {
    if (defaultValue === null) return 'NULL';
    if (typeof defaultValue === 'string') return `'${defaultValue}'`;
    if (typeof defaultValue === 'number') return defaultValue.toString();
    if (typeof defaultValue === 'boolean') return defaultValue ? 'TRUE' : 'FALSE';
    return null;
  }
}

module.exports = BaseModel;