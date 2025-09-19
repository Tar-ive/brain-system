const BaseRepository = require('./BaseRepository');
const Correlation = require('../models/Correlation');

class CorrelationRepository extends BaseRepository {
  constructor() {
    super(Correlation);
  }

  async findByDatasets(sourceDatasetId, targetDatasetId) {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE source_dataset_id = $1 AND target_dataset_id = $2
        ORDER BY confidence DESC, created_at DESC
      `;
      const result = await this.db.getPool().query(query, [sourceDatasetId, targetDatasetId]);
      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error('Error finding correlations by datasets', {
        sourceDatasetId, targetDatasetId, error: error.message
      });
      throw error;
    }
  }

  async findByType(type) {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE type = $1
        ORDER BY confidence DESC
      `;
      const result = await this.db.getPool().query(query, [type]);
      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error('Error finding correlations by type', { type, error: error.message });
      throw error;
    }
  }

  async findByStatus(status) {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE status = $1
        ORDER BY created_at DESC
      `;
      const result = await this.db.getPool().query(query, [status]);
      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error('Error finding correlations by status', { status, error: error.message });
      throw error;
    }
  }

  async findValidated(minConfidence = 0.5) {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE status = 'validated' AND confidence >= $1
        ORDER BY confidence DESC
      `;
      const result = await this.db.getPool().query(query, [minConfidence]);
      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error('Error finding validated correlations', { minConfidence, error: error.message });
      throw error;
    }
  }

  async findSignificant(minConfidence = 0.7, minValidity = 0.6) {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE confidence >= $1 AND validity_score >= $2
        ORDER BY confidence DESC
      `;
      const result = await this.db.getPool().query(query, [minConfidence, minValidity]);
      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error('Error finding significant correlations', {
        minConfidence, minValidity, error: error.message
      });
      throw error;
    }
  }

  async findByDiscoveryMethod(method) {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE discovery_method = $1
        ORDER BY confidence DESC
      `;
      const result = await this.db.getPool().query(query, [method]);
      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error('Error finding correlations by discovery method', { method, error: error.message });
      throw error;
    }
  }

  async findByTags(tags) {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE tags && $1
        ORDER BY confidence DESC
      `;
      const result = await this.db.getPool().query(query, [tags]);
      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error('Error finding correlations by tags', { tags, error: error.message });
      throw error;
    }
  }

  async findChildren(parentCorrelationId) {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE parent_correlation_id = $1
        ORDER BY version DESC
      `;
      const result = await this.db.getPool().query(query, [parentCorrelationId]);
      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error('Error finding child correlations', { parentCorrelationId, error: error.message });
      throw error;
    }
  }

  async updateValidation(id, validityScore, status = null) {
    try {
      const setStatus = status ? `, status = $3` : '';
      const params = status ? [validityScore, status, id] : [validityScore, id];

      const query = `
        UPDATE ${this.tableName}
        SET
          validity_score = $1,
          last_validated = NOW(),
          updated_at = NOW()
          ${setStatus}
        WHERE id = $${params.length}
        RETURNING *
      `;

      const result = await this.db.getPool().query(query, params);

      if (result.rows.length === 0) {
        throw new Error('Correlation not found');
      }

      return this.model.fromDatabase(result.rows[0]);
    } catch (error) {
      this.logger.error('Error updating correlation validation', { id, error: error.message });
      throw error;
    }
  }

  async incrementVersion(id) {
    try {
      const query = `
        UPDATE ${this.tableName}
        SET
          version = version + 1,
          updated_at = NOW()
        WHERE id = $1
        RETURNING *
      `;
      const result = await this.db.getPool().query(query, [id]);

      if (result.rows.length === 0) {
        throw new Error('Correlation not found');
      }

      return this.model.fromDatabase(result.rows[0]);
    } catch (error) {
      this.logger.error('Error incrementing correlation version', { id, error: error.message });
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
        throw new Error('Correlation not found');
      }

      return this.model.fromDatabase(result.rows[0]);
    } catch (error) {
      this.logger.error('Error archiving correlation', { id, error: error.message });
      throw error;
    }
  }

  async getCorrelationTypes() {
    try {
      const query = `
        SELECT type, COUNT(*) as count, AVG(confidence) as avg_confidence
        FROM ${this.tableName}
        GROUP BY type
        ORDER BY count DESC
      `;
      const result = await this.db.getPool().query(query);
      return result.rows;
    } catch (error) {
      this.logger.error('Error getting correlation types', { error: error.message });
      throw error;
    }
  }

  async getDiscoveryMethods() {
    try {
      const query = `
        SELECT discovery_method, COUNT(*) as count, AVG(confidence) as avg_confidence
        FROM ${this.tableName}
        WHERE discovery_method IS NOT NULL
        GROUP BY discovery_method
        ORDER BY count DESC
      `;
      const result = await this.db.getPool().query(query);
      return result.rows;
    } catch (error) {
      this.logger.error('Error getting discovery methods', { error: error.message });
      throw error;
    }
  }

  async getValidationStats() {
    try {
      const query = `
        SELECT
          status,
          COUNT(*) as count,
          AVG(confidence) as avg_confidence,
          AVG(validity_score) as avg_validity,
          AVG(last_validated - created_at) as avg_validation_time
        FROM ${this.tableName}
        GROUP BY status
        ORDER BY count DESC
      `;
      const result = await this.db.getPool().query(query);
      return result.rows;
    } catch (error) {
      this.logger.error('Error getting validation stats', { error: error.message });
      throw error;
    }
  }

  async getCorrelationNetwork(sourceDatasetId) {
    try {
      const query = `
        WITH correlation_stats AS (
          SELECT
            target_dataset_id,
            COUNT(*) as correlation_count,
            AVG(confidence) as avg_confidence,
            MAX(confidence) as max_confidence,
            ARRAY_AGG(DISTINCT type) as types
          FROM ${this.tableName}
          WHERE source_dataset_id = $1 AND status = 'validated'
          GROUP BY target_dataset_id
        )
        SELECT
          ds.id,
          ds.name,
          ds.type,
          cs.correlation_count,
          cs.avg_confidence,
          cs.max_confidence,
          cs.types
        FROM correlation_stats cs
        JOIN datasets ds ON ds.id = cs.target_dataset_id
        ORDER BY cs.correlation_count DESC, cs.avg_confidence DESC
      `;
      const result = await this.db.getPool().query(query, [sourceDatasetId]);
      return result.rows;
    } catch (error) {
      this.logger.error('Error getting correlation network', { sourceDatasetId, error: error.message });
      throw error;
    }
  }

  async findSimilarCorrelations(correlationId, threshold = 0.8) {
    try {
      // First get the reference correlation
      const reference = await this.findById(correlationId);
      if (!reference) {
        throw new Error('Reference correlation not found');
      }

      const query = `
        SELECT * FROM ${this.tableName}
        WHERE
          id != $1 AND
          type = $2 AND
          ABS(confidence - $3) <= $4 AND
          (source_dataset_id = $5 OR target_dataset_id = $6)
        ORDER BY confidence DESC
        LIMIT 10
      `;
      const result = await this.db.getPool().query(query, [
        correlationId,
        reference.type,
        reference.confidence,
        threshold,
        reference.sourceDatasetId,
        reference.targetDatasetId
      ]);

      return result.rows.map(row => this.model.fromDatabase(row));
    } catch (error) {
      this.logger.error('Error finding similar correlations', { correlationId, error: error.message });
      throw error;
    }
  }

  async getCorrelationTimeline(datasetId, days = 30) {
    try {
      const query = `
        SELECT
          DATE(created_at) as date,
          COUNT(*) as count,
          AVG(confidence) as avg_confidence,
          AVG(validity_score) as avg_validity
        FROM ${this.tableName}
        WHERE
          (source_dataset_id = $1 OR target_dataset_id = $1) AND
          created_at >= NOW() - INTERVAL '${days} days'
        GROUP BY DATE(created_at)
        ORDER BY date
      `;
      const result = await this.db.getPool().query(query, [datasetId]);
      return result.rows;
    } catch (error) {
      this.logger.error('Error getting correlation timeline', { datasetId, days, error: error.message });
      throw error;
    }
  }
}

module.exports = CorrelationRepository;