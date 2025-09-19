const winston = require('winston');
const { v4: uuidv4 } = require('uuid');
const DatabaseConfig = require('../config/database');

class BaseRepository {
  constructor(model, logger = null) {
    this.model = model;
    this.tableName = model.tableName;
    this.db = new DatabaseConfig();
    this.logger = logger || winston.createLogger({
      level: 'info',
      format: winston.format.json(),
      transports: [new winston.transports.Console()]
    });
  }

  async connect() {
    try {
      await this.db.connect();
      this.logger.info(`Connected to ${this.tableName} repository`);
    } catch (error) {
      this.logger.error(`Failed to connect to ${this.tableName} repository`, { error: error.message });
      throw error;
    }
  }

  async disconnect() {
    try {
      await this.db.disconnect();
      this.logger.info(`Disconnected from ${this.tableName} repository`);
    } catch (error) {
      this.logger.error(`Failed to disconnect from ${this.tableName} repository`, { error: error.message });
      throw error;
    }
  }

  async findById(id) {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE id = $1
        LIMIT 1
      `;
      const result = await this.db.getPool().query(query, [id]);

      if (result.rows.length === 0) {
        return null;
      }

      return this.model.fromDatabase(result.rows[0]);
    } catch (error) {
      this.logger.error(`Error finding ${this.tableName} by ID`, { id, error: error.message });
      throw error;
    }
  }

  async findAll(options = {}) {
    try {
      const { limit = 50, offset = 0, orderBy = 'createdAt', order = 'DESC', where = {} } = options;

      let query = `SELECT * FROM ${this.tableName}`;
      const params = [];
      let paramIndex = 1;

      // Build WHERE clause
      const whereConditions = Object.entries(where).map(([key, value]) => {
        if (Array.isArray(value)) {
          params.push(...value);
          return `${key} = ANY($${paramIndex++})::uuid[]`;
        } else if (value instanceof Date) {
          params.push(value.toISOString());
          return `${key} = $${paramIndex++}`;
        } else {
          params.push(value);
          return `${key} = $${paramIndex++}`;
        }
      });

      if (whereConditions.length > 0) {
        query += ' WHERE ' + whereConditions.join(' AND ');
      }

      // Add ORDER BY
      query += ` ORDER BY ${orderBy} ${order}`;

      // Add LIMIT and OFFSET
      query += ` LIMIT $${paramIndex++} OFFSET $${paramIndex++}`;
      params.push(limit, offset);

      const result = await this.db.getPool().query(query, params);

      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error(`Error finding all ${this.tableName}`, { error: error.message });
      throw error;
    }
  }

  async create(data) {
    try {
      const instance = new this.model(data);
      instance.validate();

      const columns = Object.keys(instance.toDatabase()).filter(key => key !== 'id');
      const values = columns.map((col, index) => `$${index + 1}`);
      const query = `
        INSERT INTO ${this.tableName} (${columns.join(', ')})
        VALUES (${values.join(', ')})
        RETURNING *
      `;

      const params = columns.map(col => instance[col]);
      const result = await this.db.getPool().query(query, params);

      this.logger.info(`Created ${this.tableName}`, { id: result.rows[0].id });
      return this.model.fromDatabase(result.rows[0]);
    } catch (error) {
      this.logger.error(`Error creating ${this.tableName}`, { error: error.message });
      throw error;
    }
  }

  async update(id, data) {
    try {
      const existing = await this.findById(id);
      if (!existing) {
        throw new Error(`${this.tableName} not found`);
      }

      existing.update(data);
      existing.validate();

      const columns = Object.keys(existing.toDatabase()).filter(key => key !== 'id');
      const setClause = columns.map((col, index) => `${col} = $${index + 1}`).join(', ');
      const query = `
        UPDATE ${this.tableName}
        SET ${setClause}
        WHERE id = $${columns.length + 1}
        RETURNING *
      `;

      const params = [...columns.map(col => existing[col]), id];
      const result = await this.db.getPool().query(query, params);

      this.logger.info(`Updated ${this.tableName}`, { id });
      return this.model.fromDatabase(result.rows[0]);
    } catch (error) {
      this.logger.error(`Error updating ${this.tableName}`, { id, error: error.message });
      throw error;
    }
  }

  async delete(id) {
    try {
      const query = `
        DELETE FROM ${this.tableName}
        WHERE id = $1
        RETURNING *
      `;
      const result = await this.db.getPool().query(query, [id]);

      if (result.rows.length === 0) {
        return false;
      }

      this.logger.info(`Deleted ${this.tableName}`, { id });
      return true;
    } catch (error) {
      this.logger.error(`Error deleting ${this.tableName}`, { id, error: error.message });
      throw error;
    }
  }

  async count(where = {}) {
    try {
      let query = `SELECT COUNT(*) as count FROM ${this.tableName}`;
      const params = [];
      let paramIndex = 1;

      const whereConditions = Object.entries(where).map(([key, value]) => {
        if (Array.isArray(value)) {
          params.push(...value);
          return `${key} = ANY($${paramIndex++})::uuid[]`;
        } else {
          params.push(value);
          return `${key} = $${paramIndex++}`;
        }
      });

      if (whereConditions.length > 0) {
        query += ' WHERE ' + whereConditions.join(' AND ');
      }

      const result = await this.db.getPool().query(query, params);
      return parseInt(result.rows[0].count);
    } catch (error) {
      this.logger.error(`Error counting ${this.tableName}`, { error: error.message });
      throw error;
    }
  }

  async exists(id) {
    try {
      const query = `SELECT EXISTS(SELECT 1 FROM ${this.tableName} WHERE id = $1)`;
      const result = await this.db.getPool().query(query, [id]);
      return result.rows[0].exists;
    } catch (error) {
      this.logger.error(`Error checking existence of ${this.tableName}`, { id, error: error.message });
      throw error;
    }
  }

  async findMany(ids) {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE id = ANY($1)
      `;
      const result = await this.db.getPool().query(query, [ids]);
      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error(`Error finding multiple ${this.tableName}`, { error: error.message });
      throw error;
    }
  }

  async createMany(dataArray) {
    try {
      const instances = dataArray.map(data => new this.model(data));
      instances.forEach(instance => instance.validate());

      const columns = Object.keys(instances[0].toDatabase()).filter(key => key !== 'id');
      const placeholders = instances.map((_, index) =>
        columns.map((_, colIndex) => `$${index * columns.length + colIndex + 1}`)
      ).map(placeholders => `(${placeholders.join(', ')})`);

      const query = `
        INSERT INTO ${this.tableName} (${columns.join(', ')})
        VALUES ${placeholders.join(', ')}
        RETURNING *
      `;

      const params = instances.flatMap(instance =>
        columns.map(col => instance[col])
      );

      const result = await this.db.getPool().query(query, params);

      this.logger.info(`Created ${instances.length} ${this.tableName} records`);
      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error(`Error creating multiple ${this.tableName}`, { error: error.message });
      throw error;
    }
  }

  async transaction(callback) {
    return this.db.transaction(callback);
  }

  // Utility methods
  async paginate(options = {}) {
    const { page = 1, limit = 50, ...queryOptions } = options;
    const offset = (page - 1) * limit;

    const [data, total] = await Promise.all([
      this.findAll({ ...queryOptions, limit, offset }),
      this.count(queryOptions.where || {})
    ]);

    return {
      data,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit),
        hasNext: page < Math.ceil(total / limit),
        hasPrev: page > 1
      }
    };
  }

  async search(searchTerm, fields = ['name'], options = {}) {
    try {
      const searchConditions = fields.map(field => {
        return `${field}::text ILIKE $1`;
      }).join(' OR ');

      const query = `
        SELECT * FROM ${this.tableName}
        WHERE ${searchConditions}
        ORDER BY similarity(${fields[0]}::text, $1) DESC
        LIMIT $2
      `;

      const result = await this.db.getPool().query(query, [`%${searchTerm}%`, options.limit || 50]);
      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error(`Error searching ${this.tableName}`, { searchTerm, error: error.message });
      throw error;
    }
  }

  async getStats() {
    try {
      const query = `
        SELECT
          COUNT(*) as total,
          COUNT(DISTINCT id) as unique_ids,
          COUNT(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as last_24h,
          COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as last_7d,
          COUNT(CASE WHEN created_at >= NOW() - INTERVAL '30 days' THEN 1 END) as last_30d
        FROM ${this.tableName}
      `;

      const result = await this.db.getPool().query(query);
      return result.rows[0];
    } catch (error) {
      this.logger.error(`Error getting stats for ${this.tableName}`, { error: error.message });
      throw error;
    }
  }
}

module.exports = BaseRepository;