"""
Pure LLM Comparator
Single-shot LLM generation without evolutionary optimization
Tests raw spatial reasoning capabilities for correlation discovery
"""

import numpy as np
import pandas as pd
import geopandas as gpd
from typing import Dict, List, Tuple, Optional, Any
import libpysal as lps
from esda.moran import Moran, Moran_Local
from esda.getisord import G, G_Local
import warnings
from dataclasses import dataclass
import time
import json
import re
from scipy import stats


@dataclass
class PureLLMConfig:
    """Configuration for Pure LLM approach"""
    model_name: str = "advanced_spatial_llm"  # Placeholder for actual model
    context_window: int = 8192
    generation_strategy: str = "single_shot"
    max_attempts: int = 3  # For few-shot learning
    discovery_target: int = 200  # correlations per hour (higher due to speed)
    conservation_error_threshold: float = 0.05  # More lenient
    temperature: float = 0.7
    confidence_threshold: float = 0.7


class SpatialPromptTemplates:
    """Prompt templates for spatial correlation discovery"""

    @staticmethod
    def correlation_discovery_prompt(context: Dict) -> str:
        """Generate prompt for correlation discovery"""
        return f"""
You are an expert in spatial data analysis and correlation discovery. Given the following spatial dataset characteristics, propose spatial correlations that could exist between the source and target variables.

Dataset Context:
- Number of spatial units (ZCTAs): {context['n_observations']}
- Geographic region: {context['region']}
- Source variable statistics: mean={context['source_mean']:.2f}, std={context['source_std']:.2f}
- Target variable: {context['target_name']}
- Spatial configuration: {context['spatial_config']}

Based on spatial analysis principles (Tobler's First Law, spatial autocorrelation, distance decay), propose:

1. A spatial weight specification (Queen, Rook, Distance-based, or K-nearest neighbors)
2. A spatial metric to calculate (Moran's I, Getis-Ord G*, Local Moran's I)
3. Any data transformations needed (log, sqrt, z-score normalization)
4. An aggregation method if needed (weighted mean, spatial interpolation)
5. The expected correlation strength and direction

Format your response as a structured JSON object with the following fields:
{{
    "weight_type": "queen|rook|distance|knn",
    "weight_params": {{"k": 5, "distance_threshold": 10000}},
    "spatial_metric": "moran_i|getis_ord|local_moran",
    "transformation": "none|log|sqrt|zscore",
    "aggregation": "mean|weighted_mean|sum",
    "expected_correlation": 0.0 to 1.0,
    "reasoning": "Brief explanation of spatial logic"
}}

Consider that health and vulnerability metrics typically show positive spatial clustering with Moran's I values between 0.174-0.264 according to literature.
"""

    @staticmethod
    def few_shot_prompt(context: Dict, examples: List[Dict]) -> str:
        """Generate few-shot learning prompt with examples"""
        examples_text = "\n".join([
            f"Example {i+1}: Input: {ex['input']} -> Output: {ex['output']} (Correlation: {ex['correlation']:.3f})"
            for i, ex in enumerate(examples)
        ])

        return f"""
Based on these successful correlation examples:
{examples_text}

Now propose a spatial correlation for:
{SpatialPromptTemplates.correlation_discovery_prompt(context)}

Learn from the patterns in the examples to propose an even better correlation hypothesis.
"""

    @staticmethod
    def validation_prompt(hypothesis: Dict, result: Dict) -> str:
        """Generate prompt for validating correlation hypothesis"""
        return f"""
Evaluate the following spatial correlation hypothesis and its results:

Hypothesis:
- Weight type: {hypothesis['weight_type']}
- Spatial metric: {hypothesis['spatial_metric']}
- Transformation: {hypothesis['transformation']}

Results:
- Correlation coefficient: {result['correlation']:.3f}
- P-value: {result['p_value']:.4f}
- Conservation error: {result['conservation_error']:.2%}
- Spatial autocorrelation: {result['spatial_autocorr']:.3f}

Does this represent a valid and meaningful spatial correlation? Consider:
1. Statistical significance (p < 0.05)
2. Conservation law compliance (error < 1%)
3. Spatial clustering consistency
4. Practical interpretability

Provide a confidence score (0-1) and brief reasoning.
"""


class PureLLMComparator:
    """
    Pure LLM approach for spatial correlation discovery
    Single-shot generation without evolutionary optimization
    """

    def __init__(self, config: PureLLMConfig = None):
        self.config = config or PureLLMConfig()
        self.prompt_templates = SpatialPromptTemplates()
        self.discovered_correlations = []
        self.generation_history = []
        self.validation_cache = {}
        self.start_time = None

    def discover_correlations(self,
                             source_data: gpd.GeoDataFrame,
                             target_data: pd.DataFrame,
                             cbsa_info: pd.DataFrame) -> Dict:
        """
        Main correlation discovery using pure LLM approach

        Parameters:
            source_data: GeoDataFrame with ZCTA geometries and metrics
            target_data: DataFrame with target variables
            cbsa_info: DataFrame with CBSA metadata

        Returns:
            Dictionary with discovered correlations and performance metrics
        """
        self.start_time = time.time()

        # Prepare context for LLM
        context = self._prepare_llm_context(source_data, target_data, cbsa_info)

        # Zero-shot attempts
        print("Starting zero-shot correlation discovery...")
        zero_shot_results = self._zero_shot_discovery(context, source_data, target_data)

        # Few-shot learning with successful examples
        if self.discovered_correlations:
            print("Attempting few-shot improvement...")
            few_shot_results = self._few_shot_discovery(context, source_data, target_data)
        else:
            few_shot_results = []

        # Batch generation for speed
        print("Batch generating correlation hypotheses...")
        batch_results = self._batch_generation(context, source_data, target_data, batch_size=20)

        # Compile and validate all results
        final_results = self._compile_results(zero_shot_results, few_shot_results, batch_results)

        return final_results

    def _prepare_llm_context(self, source_data: gpd.GeoDataFrame,
                            target_data: pd.DataFrame,
                            cbsa_info: pd.DataFrame) -> Dict:
        """Prepare context for LLM prompts"""
        numeric_cols = source_data.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) > 0:
            source_values = source_data[numeric_cols[0]].values
            source_mean = np.mean(source_values)
            source_std = np.std(source_values)
        else:
            source_mean = 0
            source_std = 1

        # Determine spatial configuration
        n_obs = len(source_data)
        if n_obs < 100:
            spatial_config = "small_scale_local"
        elif n_obs < 1000:
            spatial_config = "medium_scale_regional"
        else:
            spatial_config = "large_scale_national"

        context = {
            'n_observations': n_obs,
            'region': cbsa_info['CBSA_NAME'].iloc[0] if not cbsa_info.empty else "Unknown",
            'source_mean': source_mean,
            'source_std': source_std,
            'target_name': target_data.columns[0] if not target_data.empty else "target_variable",
            'spatial_config': spatial_config,
            'n_cbsas': len(cbsa_info['CBSA'].unique()) if 'CBSA' in cbsa_info.columns else 1
        }

        return context

    def _zero_shot_discovery(self, context: Dict,
                           source_data: gpd.GeoDataFrame,
                           target_data: pd.DataFrame) -> List[Dict]:
        """Zero-shot correlation discovery"""
        results = []

        for attempt in range(self.config.max_attempts):
            # Generate hypothesis using LLM (simulated)
            hypothesis = self._generate_hypothesis(context, examples=None)

            # Apply hypothesis to data
            correlation_result = self._apply_hypothesis(hypothesis, source_data, target_data)

            if correlation_result:
                results.append(correlation_result)

                # Check if valid correlation
                if correlation_result['correlation'] > 0.5 and \
                   correlation_result['conservation_error'] < self.config.conservation_error_threshold:
                    self.discovered_correlations.append(correlation_result)

        return results

    def _few_shot_discovery(self, context: Dict,
                          source_data: gpd.GeoDataFrame,
                          target_data: pd.DataFrame) -> List[Dict]:
        """Few-shot learning with examples"""
        results = []

        # Use best discovered correlations as examples
        examples = sorted(self.discovered_correlations,
                         key=lambda x: x['correlation'],
                         reverse=True)[:3]

        for attempt in range(self.config.max_attempts):
            # Generate hypothesis with examples
            hypothesis = self._generate_hypothesis(context, examples=examples)

            # Apply and validate
            correlation_result = self._apply_hypothesis(hypothesis, source_data, target_data)

            if correlation_result:
                results.append(correlation_result)

                # Learn from result
                if correlation_result['correlation'] > 0.6:
                    self.discovered_correlations.append(correlation_result)
                    # Update examples for next iteration
                    examples.append(correlation_result)
                    examples = sorted(examples, key=lambda x: x['correlation'], reverse=True)[:3]

        return results

    def _batch_generation(self, context: Dict,
                        source_data: gpd.GeoDataFrame,
                        target_data: pd.DataFrame,
                        batch_size: int = 20) -> List[Dict]:
        """Batch generation for efficiency"""
        results = []

        # Generate multiple hypotheses at once
        hypotheses = self._generate_batch_hypotheses(context, batch_size)

        for hypothesis in hypotheses:
            correlation_result = self._apply_hypothesis(hypothesis, source_data, target_data)

            if correlation_result:
                results.append(correlation_result)

                if self._is_valid_correlation(correlation_result):
                    self.discovered_correlations.append(correlation_result)

        return results

    def _generate_hypothesis(self, context: Dict, examples: Optional[List[Dict]] = None) -> Dict:
        """
        Generate correlation hypothesis using LLM
        Note: This is a simulation - in production would call actual LLM
        """

        # Simulate LLM response based on context
        if examples:
            # Learn from examples (few-shot)
            weight_types = [ex.get('hypothesis', {}).get('weight_type', 'queen')
                           for ex in examples if 'hypothesis' in ex]
            weight_type = max(set(weight_types), key=weight_types.count) if weight_types else 'queen'
        else:
            # Zero-shot generation
            if context['spatial_config'] == 'small_scale_local':
                weight_type = np.random.choice(['queen', 'rook'])
            else:
                weight_type = np.random.choice(['distance', 'knn'])

        # Generate hypothesis based on spatial principles
        hypothesis = {
            'weight_type': weight_type,
            'weight_params': {
                'k': np.random.randint(3, 8),
                'distance_threshold': np.random.uniform(5000, 20000)
            },
            'spatial_metric': np.random.choice(['moran_i', 'getis_ord', 'local_moran']),
            'transformation': np.random.choice(['none', 'log', 'sqrt', 'zscore']),
            'aggregation': 'weighted_mean' if weight_type in ['distance', 'knn'] else 'mean',
            'expected_correlation': np.random.uniform(0.174, 0.264),  # Literature range
            'reasoning': f"Based on {context['spatial_config']} configuration with {context['n_observations']} observations",
            'generation_time': time.time() - self.start_time
        }

        return hypothesis

    def _generate_batch_hypotheses(self, context: Dict, batch_size: int) -> List[Dict]:
        """Generate multiple hypotheses in batch"""
        hypotheses = []

        # Systematic generation covering different approaches
        weight_types = ['queen', 'rook', 'distance', 'knn']
        metrics = ['moran_i', 'getis_ord', 'local_moran']
        transforms = ['none', 'log', 'sqrt', 'zscore']

        for i in range(batch_size):
            hypothesis = {
                'weight_type': weight_types[i % len(weight_types)],
                'weight_params': {
                    'k': 3 + (i % 8),
                    'distance_threshold': 5000 + (i * 1000)
                },
                'spatial_metric': metrics[i % len(metrics)],
                'transformation': transforms[i % len(transforms)],
                'aggregation': 'weighted_mean',
                'expected_correlation': 0.174 + (i / batch_size) * (0.264 - 0.174),
                'reasoning': f"Batch hypothesis {i+1} for systematic exploration",
                'generation_time': time.time() - self.start_time
            }
            hypotheses.append(hypothesis)

        return hypotheses

    def _apply_hypothesis(self, hypothesis: Dict,
                        source_data: gpd.GeoDataFrame,
                        target_data: pd.DataFrame) -> Optional[Dict]:
        """Apply LLM-generated hypothesis to data"""
        try:
            # Create spatial weights
            weights = self._create_weights(hypothesis['weight_type'],
                                          hypothesis['weight_params'],
                                          source_data)

            if weights is None:
                return None

            # Get data values
            numeric_cols = source_data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                return None

            values = source_data[numeric_cols[0]].values

            # Apply transformation
            values = self._apply_transformation(values, hypothesis['transformation'])

            # Calculate spatial metric
            spatial_result = self._calculate_spatial_metric(values, weights, hypothesis['spatial_metric'])

            if spatial_result is None:
                return None

            # Calculate correlation with target
            target_values = target_data.iloc[:, 0].values
            if len(spatial_result) != len(target_values):
                return None

            correlation = np.corrcoef(spatial_result, target_values)[0, 1]

            # Check conservation
            conservation_error = self._check_conservation(spatial_result, source_data)

            # Calculate spatial autocorrelation
            try:
                mi = Moran(spatial_result, weights, permutations=99)
                spatial_autocorr = mi.I
                p_value = mi.p_norm
            except:
                spatial_autocorr = 0
                p_value = 1

            result = {
                'hypothesis': hypothesis,
                'correlation': abs(correlation),
                'conservation_error': conservation_error,
                'spatial_autocorr': spatial_autocorr,
                'p_value': p_value,
                'timestamp': time.time() - self.start_time,
                'method': 'pure_llm'
            }

            return result

        except Exception as e:
            return None

    def _create_weights(self, weight_type: str, params: Dict,
                       data: gpd.GeoDataFrame) -> Optional[lps.weights.W]:
        """Create spatial weights matrix"""
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")

                if weight_type == 'queen':
                    return lps.weights.Queen.from_dataframe(data, silence_warnings=True)
                elif weight_type == 'rook':
                    return lps.weights.Rook.from_dataframe(data, silence_warnings=True)
                elif weight_type == 'distance':
                    threshold = params.get('distance_threshold', 10000)
                    return lps.weights.DistanceBand.from_dataframe(
                        data, threshold=threshold, silence_warnings=True
                    )
                elif weight_type == 'knn':
                    k = params.get('k', 5)
                    return lps.weights.KNN.from_dataframe(
                        data, k=k, silence_warnings=True
                    )
        except:
            return None

    def _apply_transformation(self, values: np.ndarray, transformation: str) -> np.ndarray:
        """Apply data transformation"""
        if transformation == 'log':
            return np.log1p(np.abs(values))
        elif transformation == 'sqrt':
            return np.sqrt(np.abs(values))
        elif transformation == 'zscore':
            return stats.zscore(values)
        else:
            return values

    def _calculate_spatial_metric(self, values: np.ndarray, weights: lps.weights.W,
                                 metric: str) -> Optional[np.ndarray]:
        """Calculate spatial metric"""
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")

                if metric == 'moran_i':
                    mi = Moran(values, weights, permutations=99)
                    # Return spatial lag for correlation calculation
                    return lps.weights.lag_spatial(weights, values)

                elif metric == 'getis_ord':
                    g_local = G_Local(values, weights, permutations=99)
                    return g_local.Gs

                elif metric == 'local_moran':
                    lm = Moran_Local(values, weights, permutations=99)
                    return lm.Is

                else:
                    return None
        except:
            return None

    def _check_conservation(self, result: np.ndarray, data: gpd.GeoDataFrame) -> float:
        """Check conservation law compliance"""
        if 'population' in data.columns:
            original_sum = data['population'].sum()
            result_sum = np.sum(result)

            if original_sum > 0:
                error = abs(result_sum - original_sum) / original_sum
                return min(error, 1.0)

        return 0.0

    def _is_valid_correlation(self, result: Dict) -> bool:
        """Check if correlation is valid"""
        return (result['correlation'] > 0.5 and
                result['conservation_error'] < self.config.conservation_error_threshold and
                result['p_value'] < 0.05)

    def _compile_results(self, zero_shot: List[Dict], few_shot: List[Dict],
                       batch: List[Dict]) -> Dict:
        """Compile final results"""
        elapsed_time = time.time() - self.start_time

        all_results = zero_shot + few_shot + batch

        # Calculate performance metrics
        valid_correlations = [r for r in all_results if self._is_valid_correlation(r)]

        # Comparison metrics
        zero_shot_accuracy = sum(1 for r in zero_shot if self._is_valid_correlation(r)) / max(len(zero_shot), 1)
        few_shot_accuracy = sum(1 for r in few_shot if self._is_valid_correlation(r)) / max(len(few_shot), 1)

        return {
            'method': 'Pure LLM',
            'configuration': {
                'model_name': self.config.model_name,
                'context_window': self.config.context_window,
                'generation_strategy': self.config.generation_strategy,
                'max_attempts': self.config.max_attempts
            },
            'performance': {
                'total_correlations_discovered': len(self.discovered_correlations),
                'discovery_rate': len(self.discovered_correlations) / (elapsed_time / 3600),
                'processing_time_seconds': elapsed_time,
                'total_hypotheses_generated': len(all_results),
                'valid_correlation_ratio': len(valid_correlations) / max(len(all_results), 1)
            },
            'accuracy_comparison': {
                'zero_shot_accuracy': zero_shot_accuracy,
                'few_shot_accuracy': few_shot_accuracy,
                'few_shot_improvement': few_shot_accuracy - zero_shot_accuracy
            },
            'best_correlations': sorted(valid_correlations,
                                      key=lambda x: x['correlation'],
                                      reverse=True)[:5],
            'speed_advantage': {
                'hypotheses_per_second': len(all_results) / elapsed_time,
                'estimated_correlations_per_hour': (len(self.discovered_correlations) / elapsed_time) * 3600
            },
            'spatial_reasoning_quality': {
                'mean_correlation': np.mean([r['correlation'] for r in valid_correlations]) if valid_correlations else 0,
                'mean_conservation_error': np.mean([r['conservation_error'] for r in valid_correlations]) if valid_correlations else 0,
                'mean_spatial_autocorr': np.mean([r['spatial_autocorr'] for r in valid_correlations]) if valid_correlations else 0
            }
        }

    def save_results(self, results: Dict, filepath: str):
        """Save results to JSON file"""
        with open(filepath, 'w') as f:
            json_results = json.loads(json.dumps(results, default=str))
            json.dump(json_results, f, indent=2)


if __name__ == "__main__":
    # Example usage
    print("Pure LLM Comparator Implementation")
    print("=" * 50)

    # Initialize configuration
    config = PureLLMConfig(
        model_name="advanced_spatial_llm",
        context_window=8192,
        max_attempts=3,
        discovery_target=200
    )

    # Create comparator instance
    comparator = PureLLMComparator(config)

    print(f"Configuration:")
    print(f"  Model: {config.model_name}")
    print(f"  Context Window: {config.context_window}")
    print(f"  Generation Strategy: {config.generation_strategy}")
    print(f"  Discovery Target: {config.discovery_target} correlations/hour")
    print(f"  Conservation Error Threshold: {config.conservation_error_threshold * 100}%")

    print("\nCapabilities:")
    print("  - Zero-shot spatial correlation discovery")
    print("  - Few-shot learning from successful examples")
    print("  - Batch hypothesis generation")
    print("  - Single-shot generation without iteration")

    print("\nReady for spatial correlation discovery using Pure LLM approach")
    print("Tests raw spatial reasoning capabilities without evolution")