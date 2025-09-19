const BaseRepository = require('./BaseRepository');
const Dataset = require('../models/Dataset');

class DatasetRepository extends BaseRepository {
  constructor() {
    super(Dataset);
  }

  async findBySource(source) {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE source = $1
        ORDER BY last_accessed DESC
      `;
      const result = await this.db.getPool().query(query, [source]);
      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error('Error finding datasets by source', { source, error: error.message });
      throw error;
    }
  }

  async findByType(type) {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE type = $1
        ORDER BY created_at DESC
      `;
      const result = await this.db.getPool().query(query, [type]);
      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error('Error finding datasets by type', { type, error: error.message });
      throw error;
    }
  }

  async findByOwner(ownerId) {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE owner_id = $1
        ORDER BY last_accessed DESC
      `;
      const result = await this.db.getPool().query(query, [ownerId]);
      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error('Error finding datasets by owner', { ownerId, error: error.message });
      throw error;
    }
  }

  async findByTags(tags) {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE tags && $1
        ORDER BY last_accessed DESC
      `;
      const result = await this.db.getPool().query(query, [tags]);
      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error('Error finding datasets by tags', { tags, error: error.message });
      throw error;
    }
  }

  async findActiveDatasets() {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE status = 'active'
        ORDER BY last_accessed DESC
      `;
      const result = await this.db.getPool().query(query);
      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error('Error finding active datasets', { error: error.message });
      throw error;
    }
  }

  async findRecentlyAccessed(days = 7) {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE last_accessed >= NOW() - INTERVAL '${days} days'
        ORDER BY last_accessed DESC
      `;
      const result = await this.db.getPool().query(query);
      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error('Error finding recently accessed datasets', { days, error: error.message });
      throw error;
    }
  }

  async findPublicDatasets() {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE visibility = 'public' AND status = 'active'
        ORDER BY created_at DESC
      `;
      const result = await this.db.getPool().query(query);
      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error('Error finding public datasets', { error: error.message });
      throw error;
    }
  }

  async updateStats(id, recordCount, size) {
    try {
      const query = `
        UPDATE ${this.tableName}
        SET record_count = $1, size = $2, updated_at = NOW()
        WHERE id = $3
        RETURNING *
      `;
      const result = await this.db.getPool().query(query, [recordCount, size, id]);

      if (result.rows.length === 0) {
        throw new Error('Dataset not found');
      }

      return this.model.fromDatabase(result.rows[0]);
    } catch (error) {
      this.logger.error('Error updating dataset stats', { id, error: error.message });
      throw error;
    }
  }

  async incrementAccessCount(id) {
    try {
      const query = `
        UPDATE ${this.tableName}
        SET
          last_accessed = NOW(),
          metadata = jsonb_set(
            COALESCE(metadata, '{}'),
            '{accessCount}',
            COALESCE((metadata->>'accessCount')::int, 0) + 1
          ),
          updated_at = NOW()
        WHERE id = $1
        RETURNING *
      `;
      const result = await this.db.getPool().query(query, [id]);

      if (result.rows.length === 0) {
        throw new Error('Dataset not found');
      }

      return this.model.fromDatabase(result.rows[0]);
    } catch (error) {
      this.logger.error('Error incrementing dataset access count', { id, error: error.message });
      throw error;
    }
  }

  async addTag(id, tag) {
    try {
      const query = `
        UPDATE ${this.tableName}
        SET
          tags = CASE
            WHEN $2 = ANY(tags) THEN tags
            ELSE array_append(tags, $2)
          END,
          updated_at = NOW()
        WHERE id = $1
        RETURNING *
      `;
      const result = await this.db.getPool().query(query, [id, tag]);

      if (result.rows.length === 0) {
        throw new Error('Dataset not found');
      }

      return this.model.fromDatabase(result.rows[0]);
    } catch (error) {
      this.logger.error('Error adding tag to dataset', { id, tag, error: error.message });
      throw error;
    }
  }

  async removeTag(id, tag) {
    try {
      const query = `
        UPDATE ${this.tableName}
        SET
          tags = array_remove(tags, $2),
          updated_at = NOW()
        WHERE id = $1
        RETURNING *
      `;
      const result = await this.db.getPool().query(query, [id, tag]);

      if (result.rows.length === 0) {
        throw new Error('Dataset not found');
      }

      return this.model.fromDatabase(result.rows[0]);
    } catch (error) {
      this.logger.error('Error removing tag from dataset', { id, tag, error: error.message });
      throw error;
    }
  }

  async archive(id) {
    try {
      const query = `
        UPDATE ${this.tableName}
        SET status = 'archived', updated_at = NOW()
        WHERE id = $1
        RETURNING *
      `;
      const result = await this.db.getPool().query(query, [id]);

      if (result.rows.length === 0) {
        throw new Error('Dataset not found');
      }

      return this.model.fromDatabase(result.rows[0]);
    } catch (error) {
      this.logger.error('Error archiving dataset', { id, error: error.message });
      throw error;
    }
  }

  async activate(id) {
    try {
      const query = `
        UPDATE ${this.tableName}
        SET status = 'active', updated_at = NOW()
        WHERE id = $1
        RETURNING *
      `;
      const result = await this.db.getPool().query(query, [id]);

      if (result.rows.length === 0) {
        throw new Error('Dataset not found');
      }

      return this.model.fromDatabase(result.rows[0]);
    } catch (error) {
      this.logger.error('Error activating dataset', { id, error: error.message });
      throw error;
    }
  }

  async getDatasetTypes() {
    try {
      const query = `
        SELECT type, COUNT(*) as count
        FROM ${this.tableName}
        WHERE status = 'active'
        GROUP BY type
        ORDER BY count DESC
      `;
      const result = await this.db.getPool().query(query);
      return result.rows;
    } catch (error) {
      this.logger.error('Error getting dataset types', { error: error.message });
      throw error;
    }
  }

  async getDatasetFormats() {
    try {
      const query = `
        SELECT format, COUNT(*) as count
        FROM ${this.tableName}
        WHERE status = 'active'
        GROUP BY format
        ORDER BY count DESC
      `;
      const result = await this.db.getPool().query(query);
      return result.rows;
    } catch (error) {
      this.logger.error('Error getting dataset formats', { error: error.message });
      throw error;
    }
  }

  async getSizeDistribution() {
    try {
      const query = `
        SELECT
          CASE
            WHEN size < 1024 THEN 'small'
            WHEN size < 1048576 THEN 'medium'
            WHEN size < 1073741824 THEN 'large'
            ELSE 'huge'
          END as size_category,
          COUNT(*) as count,
          AVG(size) as avg_size
        FROM ${this.tableName}
        WHERE status = 'active'
        GROUP BY size_category
        ORDER BY size_category
      `;
      const result = await this.db.getPool().query(query);
      return result.rows;
    } catch (error) {
      this.logger.error('Error getting size distribution', { error: error.message });
      throw error;
    }
  }

  async getPopularTags(limit = 20) {
    try {
      const query = `
        SELECT UNNEST(tags) as tag, COUNT(*) as count
        FROM ${this.tableName}
        WHERE status = 'active'
        GROUP BY tag
        ORDER BY count DESC
        LIMIT $1
      `;
      const result = await this.db.getPool().query(query, [limit]);
      return result.rows;
    } catch (error) {
      this.logger.error('Error getting popular tags', { error: error.message });
      throw error;
    }
  }

  async searchByDescription(searchTerm) {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE
          status = 'active' AND
          (name ILIKE $1 OR description ILIKE $1)
        ORDER BY
          similarity(name, $1) DESC,
          similarity(description, $1) DESC
        LIMIT 50
      `;
      const result = await this.db.getPool().query(query, [`%${searchTerm}%`]);
      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error('Error searching datasets by description', { searchTerm, error: error.message });
      throw error;
    }
  }
}

module.exports = DatasetRepository;