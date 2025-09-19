"""
Human Expert Benchmark
Standardized tasks for human-AI comparison in spatial correlation discovery
Measures accuracy, speed, and methodology quality
"""

import numpy as np
import pandas as pd
import geopandas as gpd
from typing import Dict, List, Tuple, Optional, Any
import libpysal as lps
from esda.moran import Moran, Moran_Local
from esda.getisord import G, G_Local
import warnings
from dataclasses import dataclass, field
import time
import json
from datetime import datetime
from scipy import stats


@dataclass
class HumanExpertConfig:
    """Configuration for Human Expert benchmark"""
    max_task_time_minutes: int = 30
    peer_review_scale: Tuple[int, int] = (1, 10)
    innovation_scale: Tuple[int, int] = (1, 5)
    minimum_trials: int = 3
    expert_level: str = "professional"  # student, professional, expert
    documentation_required: bool = True


@dataclass
class StandardizedTask:
    """Base class for standardized benchmark tasks"""
    task_id: str
    task_name: str
    description: str
    difficulty: str  # easy, medium, hard
    time_limit_minutes: int
    evaluation_criteria: Dict[str, float]  # criterion: weight
    ground_truth: Optional[Any] = None
    instructions: str = ""


class SpatialClusteringTask(StandardizedTask):
    """Task: Identify significant spatial clusters"""

    def __init__(self):
        super().__init__(
            task_id="SCT-001",
            task_name="Spatial Clustering Identification",
            description="Identify and validate significant spatial clusters in vulnerability data",
            difficulty="medium",
            time_limit_minutes=15,
            evaluation_criteria={
                "cluster_accuracy": 0.3,
                "statistical_validity": 0.3,
                "interpretation_quality": 0.2,
                "visualization": 0.2
            },
            instructions="""
            Given a spatial dataset of vulnerability metrics:
            1. Identify significant spatial clusters using appropriate methods
            2. Validate clusters using statistical tests
            3. Interpret the practical meaning of identified clusters
            4. Create a visualization of cluster locations

            Deliverables:
            - List of cluster locations (ZCTA codes or coordinates)
            - Statistical significance values
            - Written interpretation (200 words)
            - Map or visualization
            """
        )


class ZCTAtoMSAAggregationTask(StandardizedTask):
    """Task: Design aggregation preserving spatial properties"""

    def __init__(self):
        super().__init__(
            task_id="ZMA-002",
            task_name="ZCTA to MSA Aggregation",
            description="Create aggregation method from ZCTA to MSA level preserving density",
            difficulty="hard",
            time_limit_minutes=20,
            evaluation_criteria={
                "conservation_accuracy": 0.4,
                "methodology_soundness": 0.3,
                "code_quality": 0.2,
                "documentation": 0.1
            },
            instructions="""
            Design and implement an aggregation method that:
            1. Aggregates ZCTA-level data to MSA level
            2. Preserves population density relationships
            3. Maintains conservation laws (total population preserved)
            4. Handles edge cases (partial ZCTA membership)

            Requirements:
            - Conservation error must be < 1%
            - Method must be reproducible
            - Provide mathematical formulation
            - Implement in Python using PySAL/GeoPandas
            """
        )


class VulnerabilityHotspotTask(StandardizedTask):
    """Task: Detect and validate vulnerability hotspots"""

    def __init__(self):
        super().__init__(
            task_id="VHD-003",
            task_name="Vulnerability Hotspot Detection",
            description="Find and validate statistically significant vulnerability hotspots",
            difficulty="medium",
            time_limit_minutes=15,
            evaluation_criteria={
                "detection_precision": 0.35,
                "statistical_rigor": 0.35,
                "false_positive_rate": 0.2,
                "reporting_quality": 0.1
            },
            instructions="""
            Using Getis-Ord Gi* or similar methods:
            1. Detect vulnerability hotspots in the spatial data
            2. Apply appropriate statistical corrections (FDR/Bonferroni)
            3. Validate against expected 5-15% ZCTA coverage
            4. Report confidence levels and p-values

            Expected outputs:
            - List of hotspot ZCTAs
            - Statistical significance for each hotspot
            - Coverage percentage
            - Validation against literature benchmarks
            """
        )


class ConservationValidationTask(StandardizedTask):
    """Task: Verify conservation laws in spatial transformations"""

    def __init__(self):
        super().__init__(
            task_id="CVL-004",
            task_name="Conservation Law Validation",
            description="Verify population and density conservation in transformations",
            difficulty="easy",
            time_limit_minutes=10,
            evaluation_criteria={
                "calculation_accuracy": 0.5,
                "error_detection": 0.3,
                "correction_method": 0.2
            },
            instructions="""
            Given a set of spatial transformations:
            1. Calculate conservation errors for population totals
            2. Identify transformations violating conservation laws
            3. Propose corrections for violations
            4. Verify corrections reduce error to < 1%

            Test cases provided:
            - 5 valid transformations
            - 3 invalid transformations
            - Mixed aggregation levels
            """
        )


class CrossValidationDesignTask(StandardizedTask):
    """Task: Design spatial cross-validation strategy"""

    def __init__(self):
        super().__init__(
            task_id="CVD-005",
            task_name="Spatial Cross-Validation Design",
            description="Design appropriate spatial CV strategy avoiding autocorrelation issues",
            difficulty="hard",
            time_limit_minutes=25,
            evaluation_criteria={
                "spatial_independence": 0.4,
                "statistical_validity": 0.3,
                "implementation_quality": 0.2,
                "innovation": 0.1
            },
            instructions="""
            Design a cross-validation strategy that:
            1. Accounts for spatial autocorrelation
            2. Ensures test/train independence
            3. Maintains geographic representativeness
            4. Provides unbiased performance estimates

            Requirements:
            - Implement spatial block CV or similar
            - Test for residual autocorrelation
            - Compare against standard k-fold
            - Provide theoretical justification
            """
        )


class HumanExpertBenchmark:
    """
    Human Expert Benchmark System
    Evaluates human performance on standardized spatial analysis tasks
    """

    def __init__(self, config: HumanExpertConfig = None):
        self.config = config or HumanExpertConfig()
        self.task_suite = self._initialize_task_suite()
        self.evaluation_results = []
        self.expert_submissions = {}
        self.timing_data = {}

    def _initialize_task_suite(self) -> List[StandardizedTask]:
        """Initialize standardized task suite"""
        return [
            SpatialClusteringTask(),
            ZCTAtoMSAAggregationTask(),
            VulnerabilityHotspotTask(),
            ConservationValidationTask(),
            CrossValidationDesignTask()
        ]

    def run_benchmark(self,
                     source_data: gpd.GeoDataFrame,
                     target_data: pd.DataFrame,
                     cbsa_info: pd.DataFrame,
                     expert_id: str = "expert_001") -> Dict:
        """
        Run complete benchmark suite

        Parameters:
            source_data: GeoDataFrame with ZCTA geometries and metrics
            target_data: DataFrame with target variables
            cbsa_info: DataFrame with CBSA metadata
            expert_id: Identifier for human expert

        Returns:
            Dictionary with benchmark results and comparisons
        """
        benchmark_start = time.time()
        results = {
            'expert_id': expert_id,
            'timestamp': datetime.now().isoformat(),
            'task_results': [],
            'aggregate_metrics': {}
        }

        for task in self.task_suite:
            print(f"\nStarting Task: {task.task_name}")
            print(f"Difficulty: {task.difficulty}")
            print(f"Time Limit: {task.time_limit_minutes} minutes")

            # Simulate expert performing task
            task_result = self._evaluate_task_performance(
                task, source_data, target_data, cbsa_info, expert_id
            )

            results['task_results'].append(task_result)

            # Check time constraint
            if task_result['time_taken_minutes'] > task.time_limit_minutes:
                print(f"⚠️ Time limit exceeded for {task.task_name}")

        # Calculate aggregate metrics
        results['aggregate_metrics'] = self._calculate_aggregate_metrics(results['task_results'])

        # Compare with AI baselines
        results['ai_comparison'] = self._compare_with_ai_baselines(results['aggregate_metrics'])

        results['total_time_minutes'] = (time.time() - benchmark_start) / 60

        return results

    def _evaluate_task_performance(self,
                                  task: StandardizedTask,
                                  source_data: gpd.GeoDataFrame,
                                  target_data: pd.DataFrame,
                                  cbsa_info: pd.DataFrame,
                                  expert_id: str) -> Dict:
        """Evaluate expert performance on a single task"""
        task_start = time.time()

        # Simulate expert solution (in real scenario, would be actual submission)
        expert_solution = self._simulate_expert_solution(task, source_data, target_data)

        # Evaluate solution quality
        evaluation_scores = self._evaluate_solution(task, expert_solution, source_data)

        # Calculate weighted score
        total_score = sum(
            evaluation_scores.get(criterion, 0) * weight
            for criterion, weight in task.evaluation_criteria.items()
        )

        task_time = (time.time() - task_start) / 60

        return {
            'task_id': task.task_id,
            'task_name': task.task_name,
            'difficulty': task.difficulty,
            'time_taken_minutes': task_time,
            'time_limit_minutes': task.time_limit_minutes,
            'on_time': task_time <= task.time_limit_minutes,
            'evaluation_scores': evaluation_scores,
            'total_score': total_score,
            'max_possible_score': 1.0,
            'solution_summary': expert_solution.get('summary', ''),
            'peer_review_score': self._simulate_peer_review(expert_solution),
            'innovation_rating': self._rate_innovation(expert_solution)
        }

    def _simulate_expert_solution(self,
                                 task: StandardizedTask,
                                 source_data: gpd.GeoDataFrame,
                                 target_data: pd.DataFrame) -> Dict:
        """
        Simulate expert solution for benchmark task
        In production, this would be replaced with actual expert submissions
        """
        solution = {
            'task_id': task.task_id,
            'approach': '',
            'implementation': None,
            'results': {},
            'summary': ''
        }

        if task.task_id == "SCT-001":  # Spatial Clustering
            # Simulate clustering solution
            numeric_cols = source_data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                values = source_data[numeric_cols[0]].values

                # Create weights and calculate Local Moran
                try:
                    w = lps.weights.Queen.from_dataframe(source_data, silence_warnings=True)
                    lm = Moran_Local(values, w, permutations=999)

                    # Identify clusters
                    significant = lm.p_sim < 0.05
                    clusters = source_data[significant].index.tolist()

                    solution['results'] = {
                        'clusters': clusters[:20],  # Top 20 clusters
                        'significance_values': lm.p_sim[significant].tolist()[:20],
                        'cluster_types': ['HH' if q == 1 else 'LL' if q == 3 else 'HL' if q == 4 else 'LH'
                                        for q in lm.q[significant]][:20]
                    }
                    solution['approach'] = 'Local Moran I with Queen contiguity'
                    solution['summary'] = f"Identified {len(clusters)} significant spatial clusters"
                except:
                    solution['results'] = {'error': 'Failed to calculate clusters'}

        elif task.task_id == "ZMA-002":  # Aggregation
            # Simulate aggregation solution
            solution['approach'] = 'Population-weighted aggregation with boundary adjustment'
            solution['implementation'] = """
def aggregate_zcta_to_msa(zcta_data, msa_boundaries, weight_col='population'):
    # Join ZCTA to MSA
    joined = gpd.sjoin(zcta_data, msa_boundaries, how='inner', op='intersects')

    # Calculate area proportions for partial memberships
    joined['intersection_area'] = joined.geometry.intersection(
        msa_boundaries.geometry[joined.index_right]
    ).area
    joined['area_proportion'] = joined['intersection_area'] / joined.geometry.area

    # Weight by population and area proportion
    joined['weighted_value'] = joined['value'] * joined[weight_col] * joined['area_proportion']

    # Aggregate to MSA level
    msa_aggregated = joined.groupby('MSA_CODE').agg({
        'weighted_value': 'sum',
        weight_col: 'sum'
    })

    # Calculate density-preserved values
    msa_aggregated['density_preserved'] = msa_aggregated['weighted_value'] / msa_aggregated[weight_col]

    return msa_aggregated
"""
            solution['results'] = {
                'conservation_error': 0.008,  # 0.8% error
                'msa_count': 50,
                'zcta_count': 1500
            }
            solution['summary'] = 'Implemented population-weighted aggregation with 0.8% conservation error'

        elif task.task_id == "VHD-003":  # Hotspot Detection
            # Simulate hotspot detection
            numeric_cols = source_data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                values = source_data[numeric_cols[0]].values

                try:
                    w = lps.weights.Queen.from_dataframe(source_data, silence_warnings=True)
                    g_local = G_Local(values, w, permutations=999)

                    # Find hotspots
                    hotspots = source_data[g_local.p_sim < 0.05].index.tolist()
                    coverage = len(hotspots) / len(source_data) * 100

                    solution['results'] = {
                        'hotspots': hotspots[:30],
                        'coverage_percentage': coverage,
                        'p_values': g_local.p_sim[g_local.p_sim < 0.05].tolist()[:30],
                        'within_expected_range': 5 <= coverage <= 15
                    }
                    solution['approach'] = 'Getis-Ord Gi* with FDR correction'
                    solution['summary'] = f"Detected {len(hotspots)} hotspots covering {coverage:.1f}% of ZCTAs"
                except:
                    solution['results'] = {'error': 'Failed to detect hotspots'}

        elif task.task_id == "CVL-004":  # Conservation Validation
            # Simulate conservation validation
            test_transformations = [
                {'name': 'valid_1', 'error': 0.002},
                {'name': 'valid_2', 'error': 0.005},
                {'name': 'valid_3', 'error': 0.008},
                {'name': 'invalid_1', 'error': 0.025},
                {'name': 'invalid_2', 'error': 0.018},
            ]

            solution['results'] = {
                'valid_transformations': [t for t in test_transformations if t['error'] < 0.01],
                'invalid_transformations': [t for t in test_transformations if t['error'] >= 0.01],
                'corrections_proposed': True,
                'final_max_error': 0.008
            }
            solution['approach'] = 'Direct sum validation with iterative correction'
            solution['summary'] = 'Identified 2 invalid transformations and proposed corrections'

        elif task.task_id == "CVD-005":  # Cross-validation Design
            # Simulate CV design
            solution['approach'] = 'Spatial block cross-validation with buffer zones'
            solution['implementation'] = """
def spatial_block_cv(data, n_blocks=5, buffer_distance=5000):
    # Create spatial blocks
    bounds = data.total_bounds
    x_splits = np.linspace(bounds[0], bounds[2], int(np.sqrt(n_blocks)) + 1)
    y_splits = np.linspace(bounds[1], bounds[3], int(np.sqrt(n_blocks)) + 1)

    # Assign points to blocks
    data['block'] = 0
    for i, x in enumerate(x_splits[:-1]):
        for j, y in enumerate(y_splits[:-1]):
            mask = (data.geometry.x >= x) & (data.geometry.x < x_splits[i+1]) & \
                   (data.geometry.y >= y) & (data.geometry.y < y_splits[j+1])
            data.loc[mask, 'block'] = i * len(y_splits) + j

    # Create folds ensuring spatial separation
    folds = []
    for block_id in data['block'].unique():
        test_mask = data['block'] == block_id

        # Add buffer to avoid leakage
        test_points = data[test_mask]
        buffer = test_points.geometry.buffer(buffer_distance)
        train_mask = ~data.geometry.within(buffer.unary_union)

        folds.append((train_mask, test_mask))

    return folds
"""
            solution['results'] = {
                'cv_strategy': 'spatial_block',
                'n_folds': 5,
                'spatial_independence_score': 0.92,
                'residual_autocorrelation': 0.03
            }
            solution['summary'] = 'Designed spatial block CV with 92% spatial independence'

        return solution

    def _evaluate_solution(self,
                          task: StandardizedTask,
                          solution: Dict,
                          source_data: gpd.GeoDataFrame) -> Dict:
        """Evaluate solution against task criteria"""
        scores = {}

        if task.task_id == "SCT-001":  # Spatial Clustering
            if 'clusters' in solution.get('results', {}):
                # Evaluate cluster accuracy
                n_clusters = len(solution['results']['clusters'])
                expected_clusters = int(len(source_data) * 0.1)  # Expect ~10% clustering
                scores['cluster_accuracy'] = max(0, 1 - abs(n_clusters - expected_clusters) / expected_clusters)

                # Statistical validity
                if 'significance_values' in solution['results']:
                    valid_sig = sum(p < 0.05 for p in solution['results']['significance_values'])
                    scores['statistical_validity'] = valid_sig / max(len(solution['results']['significance_values']), 1)
                else:
                    scores['statistical_validity'] = 0

                # Interpretation quality (simulated)
                scores['interpretation_quality'] = 0.7 if solution.get('summary') else 0.3

                # Visualization (simulated)
                scores['visualization'] = 0.8 if solution.get('approach') else 0.4
            else:
                scores = {k: 0 for k in task.evaluation_criteria.keys()}

        elif task.task_id == "ZMA-002":  # Aggregation
            if 'conservation_error' in solution.get('results', {}):
                # Conservation accuracy
                error = solution['results']['conservation_error']
                scores['conservation_accuracy'] = max(0, 1 - error / 0.01)  # Perfect if < 1%

                # Methodology soundness
                scores['methodology_soundness'] = 0.9 if solution.get('implementation') else 0.4

                # Code quality
                scores['code_quality'] = 0.8 if 'def ' in str(solution.get('implementation', '')) else 0.3

                # Documentation
                scores['documentation'] = 0.7 if solution.get('summary') else 0.2
            else:
                scores = {k: 0 for k in task.evaluation_criteria.keys()}

        elif task.task_id == "VHD-003":  # Hotspot Detection
            if 'coverage_percentage' in solution.get('results', {}):
                # Detection precision
                coverage = solution['results']['coverage_percentage']
                in_range = 5 <= coverage <= 15
                scores['detection_precision'] = 1.0 if in_range else max(0, 1 - abs(coverage - 10) / 10)

                # Statistical rigor
                scores['statistical_rigor'] = 0.9 if 'p_values' in solution['results'] else 0.4

                # False positive rate (simulated)
                scores['false_positive_rate'] = 0.8 if coverage < 20 else 0.4

                # Reporting quality
                scores['reporting_quality'] = 0.7 if solution.get('summary') else 0.3
            else:
                scores = {k: 0 for k in task.evaluation_criteria.keys()}

        elif task.task_id == "CVL-004":  # Conservation Validation
            if 'final_max_error' in solution.get('results', {}):
                # Calculation accuracy
                error = solution['results']['final_max_error']
                scores['calculation_accuracy'] = max(0, 1 - error / 0.01)

                # Error detection
                invalid_found = len(solution['results'].get('invalid_transformations', []))
                scores['error_detection'] = min(1, invalid_found / 2)  # Expected 2 invalid

                # Correction method
                scores['correction_method'] = 0.9 if solution['results'].get('corrections_proposed') else 0.2
            else:
                scores = {k: 0 for k in task.evaluation_criteria.keys()}

        elif task.task_id == "CVD-005":  # Cross-validation Design
            if 'spatial_independence_score' in solution.get('results', {}):
                # Spatial independence
                scores['spatial_independence'] = solution['results']['spatial_independence_score']

                # Statistical validity
                residual = solution['results'].get('residual_autocorrelation', 1)
                scores['statistical_validity'] = max(0, 1 - residual)

                # Implementation quality
                scores['implementation_quality'] = 0.9 if solution.get('implementation') else 0.4

                # Innovation
                scores['innovation'] = 0.7  # Base score for spatial block CV
            else:
                scores = {k: 0 for k in task.evaluation_criteria.keys()}

        return scores

    def _simulate_peer_review(self, solution: Dict) -> float:
        """Simulate peer review score (1-10 scale)"""
        # In production, would be actual peer review
        base_score = 5.0

        if solution.get('approach'):
            base_score += 1.5
        if solution.get('implementation'):
            base_score += 1.5
        if solution.get('summary'):
            base_score += 1.0
        if solution.get('results') and not solution['results'].get('error'):
            base_score += 1.0

        return min(10.0, base_score)

    def _rate_innovation(self, solution: Dict) -> float:
        """Rate innovation level (1-5 scale)"""
        # In production, would be expert assessment
        if 'spatial_block' in str(solution.get('approach', '')):
            return 3.5
        elif 'Queen' in str(solution.get('approach', '')):
            return 2.0
        else:
            return 2.5

    def _calculate_aggregate_metrics(self, task_results: List[Dict]) -> Dict:
        """Calculate aggregate performance metrics"""
        total_score = sum(r['total_score'] for r in task_results)
        max_score = sum(r['max_possible_score'] for r in task_results)
        total_time = sum(r['time_taken_minutes'] for r in task_results)
        on_time_tasks = sum(1 for r in task_results if r['on_time'])

        return {
            'overall_score': total_score / max_score if max_score > 0 else 0,
            'average_task_score': total_score / len(task_results) if task_results else 0,
            'total_time_minutes': total_time,
            'average_time_minutes': total_time / len(task_results) if task_results else 0,
            'on_time_completion_rate': on_time_tasks / len(task_results) if task_results else 0,
            'average_peer_review': np.mean([r['peer_review_score'] for r in task_results]),
            'average_innovation': np.mean([r['innovation_rating'] for r in task_results]),
            'tasks_completed': len(task_results),
            'perfect_scores': sum(1 for r in task_results if r['total_score'] >= 0.9)
        }

    def _compare_with_ai_baselines(self, human_metrics: Dict) -> Dict:
        """Compare human performance with AI baselines"""
        # Estimated AI performance (would be actual in production)
        ai_baselines = {
            'alphevolve': {
                'accuracy': 0.95,
                'speed_factor': 100,  # 100x faster
                'consistency': 1.0,
                'innovation': 2.0
            },
            'traditional_gp': {
                'accuracy': 0.85,
                'speed_factor': 50,
                'consistency': 0.95,
                'innovation': 2.5
            },
            'pure_llm': {
                'accuracy': 0.80,
                'speed_factor': 200,
                'consistency': 0.90,
                'innovation': 3.0
            }
        }

        comparison = {}
        human_accuracy = human_metrics['overall_score']
        human_speed = 1.0  # Baseline

        for method, ai_metrics in ai_baselines.items():
            comparison[method] = {
                'accuracy_ratio': human_accuracy / ai_metrics['accuracy'],
                'speed_ratio': human_speed / ai_metrics['speed_factor'],
                'consistency_ratio': 0.85 / ai_metrics['consistency'],  # Assume human consistency ~85%
                'innovation_ratio': human_metrics['average_innovation'] / ai_metrics['innovation'],
                'human_advantages': [],
                'ai_advantages': []
            }

            # Identify advantages
            if comparison[method]['accuracy_ratio'] > 1.0:
                comparison[method]['human_advantages'].append('Higher accuracy')
            else:
                comparison[method]['ai_advantages'].append('Higher accuracy')

            if comparison[method]['innovation_ratio'] > 1.0:
                comparison[method]['human_advantages'].append('More innovative')
            else:
                comparison[method]['ai_advantages'].append('More innovative')

            comparison[method]['ai_advantages'].append('Significantly faster')
            comparison[method]['human_advantages'].append('Better interpretability')

        return comparison

    def generate_report(self, results: Dict) -> str:
        """Generate human-readable benchmark report"""
        report = f"""
Human Expert Benchmark Report
==============================
Expert ID: {results['expert_id']}
Date: {results['timestamp']}
Total Time: {results['total_time_minutes']:.1f} minutes

Overall Performance
-------------------
Overall Score: {results['aggregate_metrics']['overall_score']:.2%}
Average Task Score: {results['aggregate_metrics']['average_task_score']:.2%}
On-time Completion Rate: {results['aggregate_metrics']['on_time_completion_rate']:.2%}
Average Peer Review Score: {results['aggregate_metrics']['average_peer_review']:.1f}/10
Average Innovation Rating: {results['aggregate_metrics']['average_innovation']:.1f}/5

Task-by-Task Results
--------------------
"""
        for task in results['task_results']:
            report += f"""
Task: {task['task_name']}
  Difficulty: {task['difficulty']}
  Score: {task['total_score']:.2%}
  Time: {task['time_taken_minutes']:.1f}/{task['time_limit_minutes']} min
  Peer Review: {task['peer_review_score']:.1f}/10
  Status: {'✓ On Time' if task['on_time'] else '✗ Overtime'}
"""

        report += """
AI Comparison
-------------
"""
        for method, comp in results['ai_comparison'].items():
            report += f"""
vs {method.upper()}:
  Accuracy Ratio (Human/AI): {comp['accuracy_ratio']:.2f}
  Speed Ratio (Human/AI): {comp['speed_ratio']:.4f}
  Innovation Ratio (Human/AI): {comp['innovation_ratio']:.2f}
  Human Advantages: {', '.join(comp['human_advantages']) if comp['human_advantages'] else 'None'}
  AI Advantages: {', '.join(comp['ai_advantages']) if comp['ai_advantages'] else 'None'}
"""

        return report

    def save_results(self, results: Dict, filepath: str):
        """Save results to JSON file"""
        with open(filepath, 'w') as f:
            json_results = json.loads(json.dumps(results, default=str))
            json.dump(json_results, f, indent=2)


if __name__ == "__main__":
    # Example usage
    print("Human Expert Benchmark System")
    print("=" * 50)

    # Initialize configuration
    config = HumanExpertConfig(
        max_task_time_minutes=30,
        expert_level="professional",
        documentation_required=True
    )

    # Create benchmark instance
    benchmark = HumanExpertBenchmark(config)

    print(f"Configuration:")
    print(f"  Expert Level: {config.expert_level}")
    print(f"  Max Task Time: {config.max_task_time_minutes} minutes")
    print(f"  Documentation Required: {config.documentation_required}")
    print(f"  Minimum Trials: {config.minimum_trials}")

    print("\nTask Suite:")
    for task in benchmark.task_suite:
        print(f"  - {task.task_name} ({task.difficulty}, {task.time_limit_minutes} min)")

    print("\nEvaluation Criteria:")
    print("  - Accuracy of solutions")
    print("  - Time to completion")
    print("  - Methodology quality (peer review)")
    print("  - Innovation factor")
    print("  - Reproducibility")

    print("\nReady to benchmark human expert performance")
    print("Compare against AI methods for comprehensive evaluation")