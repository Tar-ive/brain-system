-- Ever-Expanding Dataset Database Schema
-- Migration 001: Create core tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Datasets table
CREATE TABLE datasets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    schema JSONB DEFAULT '{}',
    type VARCHAR(50) NOT NULL DEFAULT 'structured'
        CHECK (type IN ('structured', 'semi-structured', 'unstructured')),
    source VARCHAR(1000) DEFAULT '',
    format VARCHAR(50) NOT NULL DEFAULT 'json'
        CHECK (format IN ('json', 'csv', 'parquet', 'xml', 'avro', 'binary')),
    size BIGINT DEFAULT 0 CHECK (size >= 0),
    record_count BIGINT DEFAULT 0 CHECK (record_count >= 0),
    metadata JSONB DEFAULT '{}',
    status VARCHAR(50) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'archived', 'processing', 'error')),
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags TEXT[] DEFAULT '{}',
    visibility VARCHAR(50) NOT NULL DEFAULT 'private'
        CHECK (visibility IN ('private', 'public', 'shared')),
    owner_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Correlations table
CREATE TABLE correlations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_dataset_id UUID NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    target_dataset_id UUID NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL CHECK (
        type IN (
            'one_to_one', 'one_to_many', 'many_to_one', 'many_to_many',
            'weighted_many_to_many', 'temporal', 'spatial', 'semantic',
            'statistical', 'structural', 'functional', 'causal'
        )
    ),
    parameters JSONB DEFAULT '{}',
    confidence DECIMAL(5,4) DEFAULT 0 CHECK (confidence >= 0 AND confidence <= 1),
    validity_score DECIMAL(5,4) DEFAULT 0 CHECK (validity_score >= 0 AND validity_score <= 1),
    description TEXT DEFAULT '',
    status VARCHAR(50) NOT NULL DEFAULT 'proposed'
        CHECK (status IN ('proposed', 'validated', 'invalidated', 'archived')),
    parent_correlation_id UUID REFERENCES correlations(id) ON DELETE SET NULL,
    version INTEGER DEFAULT 1 CHECK (version >= 1),
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    discovery_method VARCHAR(100) CHECK (
        discovery_method IN (
            'neural_network', 'mcts', 'evolutionary', 'statistical',
            'information_theory', 'manual', 'hybrid'
        )
    ),
    last_validated TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_source_target UNIQUE (source_dataset_id, target_dataset_id, version)
);

-- Dataset signatures table
CREATE TABLE dataset_signatures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id UUID NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    statistical JSONB NOT NULL DEFAULT '{}',
    semantic JSONB NOT NULL DEFAULT '{}',
    structural JSONB NOT NULL DEFAULT '{}',
    temporal JSONB,
    spatial JSONB,
    version INTEGER DEFAULT 1 CHECK (version >= 1),
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    computation_time INTEGER DEFAULT 0 CHECK (computation_time >= 0),
    algorithm VARCHAR(100) DEFAULT 'default'
        CHECK (algorithm IN ('default', 'neural', 'statistical', 'hybrid')),
    compression_ratio DECIMAL(5,4) DEFAULT 0 CHECK (compression_ratio >= 0 AND compression_ratio <= 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_dataset_version UNIQUE (dataset_id, version)
);

-- Validations table
CREATE TABLE validations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    correlation_id UUID NOT NULL REFERENCES correlations(id) ON DELETE CASCADE,
    validity_score DECIMAL(5,4) DEFAULT 0 CHECK (validity_score >= 0 AND validity_score <= 1),
    statistical_score DECIMAL(5,4) DEFAULT 0 CHECK (statistical_score >= 0 AND statistical_score <= 1),
    semantic_score DECIMAL(5,4) DEFAULT 0 CHECK (semantic_score >= 0 AND semantic_score <= 1),
    structural_score DECIMAL(5,4) DEFAULT 0 CHECK (structural_score >= 0 AND structural_score <= 1),
    conservation_error DECIMAL(10,6) DEFAULT 0 CHECK (conservation_error >= 0),
    test_accuracy DECIMAL(5,4) DEFAULT 0 CHECK (test_accuracy >= 0 AND test_accuracy <= 1),
    confidence_interval DECIMAL(5,4)[] DEFAULT ARRAY[0, 1],
    counter_examples JSONB DEFAULT '[]',
    validation_method VARCHAR(100) CHECK (
        validation_method IN (
            'statistical', 'semantic', 'structural', 'conservation', 'ensemble', 'cross_validation'
        )
    ),
    test_cases JSONB DEFAULT '[]',
    failure_modes JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    validation_time INTEGER DEFAULT 0 CHECK (validation_time >= 0),
    data_size BIGINT DEFAULT 0 CHECK (data_size >= 0),
    sample_size INTEGER DEFAULT 0 CHECK (sample_size >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Training episodes table
CREATE TABLE training_episodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    episode_id UUID NOT NULL,
    step_number INTEGER DEFAULT 0 CHECK (step_number >= 0),
    state JSONB NOT NULL,
    action JSONB NOT NULL,
    reward DECIMAL(10,6) DEFAULT 0,
    next_state JSONB NOT NULL,
    done BOOLEAN DEFAULT FALSE,
    priority DECIMAL(5,4) DEFAULT 1.0 CHECK (priority >= 0),
    generator_model UUID,
    validator_model UUID,
    algorithm VARCHAR(100) CHECK (
        algorithm IN ('mcts', 'evolutionary', 'neural', 'ensemble')
    ),
    environment JSONB DEFAULT '{}',
    metrics JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    experience_type VARCHAR(50) DEFAULT 'exploration'
        CHECK (experience_type IN ('exploration', 'exploitation', 'training', 'evaluation')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Evolution records table
CREATE TABLE evolution_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    generation INTEGER DEFAULT 0 CHECK (generation >= 0),
    individual_id UUID NOT NULL,
    genome JSONB NOT NULL,
    fitness DECIMAL(10,6) DEFAULT 0,
    parent1_id UUID,
    parent2_id UUID,
    mutation_info JSONB DEFAULT '{}',
    crossover_info JSONB DEFAULT '{}',
    population_id UUID NOT NULL,
    species VARCHAR(100) DEFAULT '',
    novelty_score DECIMAL(10,6) DEFAULT 0 CHECK (novelty_score >= 0),
    complexity DECIMAL(10,6) DEFAULT 0 CHECK (complexity >= 0),
    diversity DECIMAL(5,4) DEFAULT 0 CHECK (diversity >= 0 AND diversity <= 1),
    evaluation_time INTEGER DEFAULT 0 CHECK (evaluation_time >= 0),
    algorithm VARCHAR(100) CHECK (
        algorithm IN ('genetic_programming', 'cma_es', 'nsga2', 'spea2', 'custom')
    ),
    parameters JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance metrics table
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_type VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,6) NOT NULL,
    metadata JSONB DEFAULT '{}',
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_datasets_name ON datasets(name);
CREATE INDEX idx_datasets_type ON datasets(type);
CREATE INDEX idx_datasets_status ON datasets(status);
CREATE INDEX idx_datasets_owner ON datasets(owner_id);
CREATE INDEX idx_datasets_visibility ON datasets(visibility);
CREATE INDEX idx_datasets_last_accessed ON datasets(last_accessed DESC);
CREATE INDEX idx_datasets_tags ON datasets USING GIN(tags);

CREATE INDEX idx_correlations_source_target ON correlations(source_dataset_id, target_dataset_id);
CREATE INDEX idx_correlations_type ON correlations(type);
CREATE INDEX idx_correlations_confidence ON correlations(confidence DESC);
CREATE INDEX idx_correlations_status ON correlations(status);
CREATE INDEX idx_correlations_validity ON correlations(validity_score);
CREATE INDEX idx_correlations_parent ON correlations(parent_correlation_id);
CREATE INDEX idx_correlations_method ON correlations(discovery_method);
CREATE INDEX idx_correlations_created ON correlations(created_at DESC);
CREATE INDEX idx_correlations_tags ON correlations USING GIN(tags);

CREATE INDEX idx_signatures_dataset ON dataset_signatures(dataset_id);
CREATE INDEX idx_signatures_version ON dataset_signatures(dataset_id, version);
CREATE INDEX idx_signatures_expires ON dataset_signatures(expires_at);
CREATE INDEX idx_signatures_computed ON dataset_signatures(computed_at DESC);
CREATE INDEX idx_signatures_algorithm ON dataset_signatures(algorithm);
CREATE INDEX idx_signatures_compression ON dataset_signatures(compression_ratio);

CREATE INDEX idx_validations_correlation ON validations(correlation_id);
CREATE INDEX idx_validations_validity ON validations(validity_score);
CREATE INDEX idx_validations_statistical ON validations(statistical_score);
CREATE INDEX idx_validations_semantic ON validations(semantic_score);
CREATE INDEX idx_validations_structural ON validations(structural_score);
CREATE INDEX idx_validations_conservation ON validations(conservation_error);
CREATE INDEX idx_validations_accuracy ON validations(test_accuracy);
CREATE INDEX idx_validations_method ON validations(validation_method);
CREATE INDEX idx_validations_created ON validations(created_at DESC);

CREATE INDEX idx_episodes_episode ON training_episodes(episode_id);
CREATE INDEX idx_episodes_step ON training_episodes(episode_id, step_number);
CREATE INDEX idx_episodes_reward ON training_episodes(reward DESC);
CREATE INDEX idx_episodes_priority ON training_episodes(priority DESC);
CREATE INDEX idx_episodes_type ON training_episodes(experience_type);
CREATE INDEX idx_episodes_algorithm ON training_episodes(algorithm);
CREATE INDEX idx_episodes_done ON training_episodes(done);
CREATE INDEX idx_episodes_created ON training_episodes(created_at DESC);
CREATE INDEX idx_episodes_models ON training_episodes(generator_model, validator_model);

CREATE INDEX idx_evolution_generation ON evolution_records(generation);
CREATE INDEX idx_evolution_fitness ON evolution_records(fitness DESC);
CREATE INDEX idx_evolution_individual ON evolution_records(individual_id);
CREATE INDEX idx_evolution_parents ON evolution_records(parent1_id, parent2_id);
CREATE INDEX idx_evolution_population ON evolution_records(population_id);
CREATE INDEX idx_evolution_species ON evolution_records(species);
CREATE INDEX idx_evolution_novelty ON evolution_records(novelty_score);
CREATE INDEX idx_evolution_complexity ON evolution_records(complexity);
CREATE INDEX idx_evolution_diversity ON evolution_records(diversity);
CREATE INDEX idx_evolution_algorithm ON evolution_records(algorithm);
CREATE INDEX idx_evolution_generation_fitness ON evolution_records(generation, fitness DESC);

CREATE INDEX idx_metrics_type_time ON performance_metrics(metric_type, recorded_at DESC);

-- Create functions for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create timestamp triggers
CREATE TRIGGER update_datasets_updated_at BEFORE UPDATE ON datasets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_correlations_updated_at BEFORE UPDATE ON correlations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_signatures_updated_at BEFORE UPDATE ON dataset_signatures
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_validations_updated_at BEFORE UPDATE ON validations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_episodes_updated_at BEFORE UPDATE ON training_episodes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_evolution_updated_at BEFORE UPDATE ON evolution_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE datasets IS 'Stores dataset metadata and configuration';
COMMENT ON TABLE correlations IS 'Stores discovered correlations between datasets';
COMMENT ON TABLE dataset_signatures IS 'Cached abstract representations of datasets';
COMMENT ON TABLE validations IS 'Validation results for correlations';
COMMENT ON TABLE training_episodes IS 'Experience replay buffer for reinforcement learning';
COMMENT ON TABLE evolution_records IS 'Evolutionary algorithm population tracking';
COMMENT ON TABLE performance_metrics IS 'System performance monitoring';