"""
Traditional Genetic Programming Comparator
Classical GP approach without neural networks for spatial correlation discovery
Uses primitive spatial operations and fitness evaluation
"""

import numpy as np
import pandas as pd
import geopandas as gpd
from typing import Dict, List, Tuple, Optional, Any, Callable
import libpysal as lps
from esda.moran import Moran, Moran_Local
from esda.getisord import G, G_Local
import warnings
from dataclasses import dataclass
import time
import random
import copy
from scipy import stats
import json


@dataclass
class GPConfig:
    """Configuration for Traditional GP"""
    population_size: int = 100
    generations: int = 1000
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    tournament_size: int = 5
    max_tree_depth: int = 7
    min_tree_depth: int = 2
    elite_size: int = 10
    discovery_target: int = 50  # correlations per hour (lower than AlphaEvolve)
    conservation_error_threshold: float = 0.02
    permutations: int = 999  # Less than AlphaEvolve for speed


class GPNode:
    """Node in genetic programming tree"""

    def __init__(self, node_type: str, value: Any = None, children: List = None):
        self.node_type = node_type  # 'function' or 'terminal'
        self.value = value
        self.children = children or []

    def depth(self) -> int:
        """Calculate tree depth"""
        if not self.children:
            return 1
        return 1 + max(child.depth() for child in self.children)

    def size(self) -> int:
        """Calculate tree size (number of nodes)"""
        if not self.children:
            return 1
        return 1 + sum(child.size() for child in self.children)

    def copy(self):
        """Deep copy of tree"""
        return copy.deepcopy(self)

    def to_string(self) -> str:
        """String representation of tree"""
        if self.node_type == 'terminal':
            return str(self.value)
        else:
            child_strs = [child.to_string() for child in self.children]
            return f"{self.value}({','.join(child_strs)})"


class SpatialPrimitives:
    """Primitive operations for spatial analysis"""

    @staticmethod
    def get_functions() -> Dict[str, Tuple[Callable, int]]:
        """Get function primitives with their arities"""
        return {
            'spatial_mean': (SpatialPrimitives.spatial_mean, 2),
            'spatial_lag': (SpatialPrimitives.spatial_lag, 2),
            'local_moran': (SpatialPrimitives.local_moran, 2),
            'getis_ord': (SpatialPrimitives.getis_ord, 2),
            'add': (lambda x, y: x + y, 2),
            'subtract': (lambda x, y: x - y, 2),
            'multiply': (lambda x, y: x * y, 2),
            'safe_divide': (SpatialPrimitives.safe_divide, 2),
            'sqrt': (lambda x: np.sqrt(np.abs(x)), 1),
            'log': (lambda x: np.log1p(np.abs(x)), 1),
            'abs': (np.abs, 1),
            'normalize': (SpatialPrimitives.normalize, 1)
        }

    @staticmethod
    def get_terminals() -> List[str]:
        """Get terminal primitives"""
        return [
            'data_values',
            'queen_weights',
            'rook_weights',
            'distance_weights',
            'knn_weights',
            'constant_1',
            'constant_0.5',
            'constant_2'
        ]

    @staticmethod
    def spatial_mean(values: np.ndarray, weights: Any) -> np.ndarray:
        """Calculate spatial mean"""
        try:
            if isinstance(weights, lps.weights.W):
                return lps.weights.lag_spatial(weights, values)
            return values
        except:
            return values

    @staticmethod
    def spatial_lag(values: np.ndarray, weights: Any) -> np.ndarray:
        """Calculate spatial lag"""
        try:
            if isinstance(weights, lps.weights.W):
                return lps.weights.lag_spatial(weights, values)
            return values
        except:
            return values

    @staticmethod
    def local_moran(values: np.ndarray, weights: Any) -> np.ndarray:
        """Calculate local Moran's I"""
        try:
            if isinstance(weights, lps.weights.W):
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore")
                    lm = Moran_Local(values, weights, permutations=99)
                    return lm.Is
            return values
        except:
            return values

    @staticmethod
    def getis_ord(values: np.ndarray, weights: Any) -> np.ndarray:
        """Calculate Getis-Ord G*"""
        try:
            if isinstance(weights, lps.weights.W):
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore")
                    g_local = G_Local(values, weights, permutations=99)
                    return g_local.Gs
            return values
        except:
            return values

    @staticmethod
    def safe_divide(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Protected division"""
        with np.errstate(divide='ignore', invalid='ignore'):
            result = np.divide(x, y)
            result[~np.isfinite(result)] = 1.0
        return result

    @staticmethod
    def normalize(values: np.ndarray) -> np.ndarray:
        """Normalize values to [0, 1]"""
        min_val = np.min(values)
        max_val = np.max(values)
        if max_val > min_val:
            return (values - min_val) / (max_val - min_val)
        return values


class TraditionalGPComparator:
    """
    Traditional Genetic Programming for spatial correlation discovery
    No neural networks, pure evolutionary computation
    """

    def __init__(self, config: GPConfig = None):
        self.config = config or GPConfig()
        self.functions = SpatialPrimitives.get_functions()
        self.terminals = SpatialPrimitives.get_terminals()
        self.population = []
        self.best_individual = None
        self.generation_stats = []
        self.discovered_correlations = []
        self.start_time = None

    def discover_correlations(self,
                             source_data: gpd.GeoDataFrame,
                             target_data: pd.DataFrame,
                             cbsa_info: pd.DataFrame) -> Dict:
        """
        Main correlation discovery using traditional GP

        Parameters:
            source_data: GeoDataFrame with ZCTA geometries and metrics
            target_data: DataFrame with target variables
            cbsa_info: DataFrame with CBSA metadata

        Returns:
            Dictionary with discovered correlations and performance metrics
        """
        self.start_time = time.time()

        # Prepare evaluation context
        context = self._prepare_context(source_data)

        # Initialize population
        self.population = self._initialize_population()

        # Evolution loop
        for generation in range(self.config.generations):
            # Evaluate fitness
            fitness_scores = self._evaluate_population(self.population, context, target_data)

            # Record statistics
            self._record_generation_stats(generation, fitness_scores)

            # Check for valid correlations
            self._check_correlations(self.population, fitness_scores, context, target_data)

            # Selection and reproduction
            new_population = []

            # Elitism
            elite_indices = np.argsort(fitness_scores)[-self.config.elite_size:]
            for idx in elite_indices:
                new_population.append(self.population[idx].copy())

            # Generate rest of population
            while len(new_population) < self.config.population_size:
                if random.random() < self.config.crossover_rate:
                    parent1 = self._tournament_selection(self.population, fitness_scores)
                    parent2 = self._tournament_selection(self.population, fitness_scores)
                    child = self._crossover(parent1, parent2)
                else:
                    child = self._tournament_selection(self.population, fitness_scores).copy()

                # Mutation
                if random.random() < self.config.mutation_rate:
                    child = self._mutate(child)

                new_population.append(child)

            self.population = new_population

            # Early stopping if target met
            if self._check_discovery_rate():
                print(f"Target discovery rate achieved at generation {generation}")
                break

            # Progress report
            if generation % 100 == 0:
                best_fitness = np.max(fitness_scores)
                print(f"Generation {generation}: Best fitness = {best_fitness:.4f}, "
                      f"Correlations found = {len(self.discovered_correlations)}")

        # Final evaluation
        final_results = self._compile_final_results(source_data, target_data, cbsa_info)

        return final_results

    def _prepare_context(self, data: gpd.GeoDataFrame) -> Dict:
        """Prepare evaluation context with data and weights"""
        context = {}

        # Extract numeric data
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            context['data_values'] = data[numeric_cols[0]].values
        else:
            context['data_values'] = np.random.randn(len(data))

        # Create spatial weights
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")

            try:
                context['queen_weights'] = lps.weights.Queen.from_dataframe(data, silence_warnings=True)
            except:
                context['queen_weights'] = None

            try:
                context['rook_weights'] = lps.weights.Rook.from_dataframe(data, silence_warnings=True)
            except:
                context['rook_weights'] = None

            try:
                context['distance_weights'] = lps.weights.DistanceBand.from_dataframe(
                    data, threshold=10000, silence_warnings=True
                )
            except:
                context['distance_weights'] = None

            try:
                context['knn_weights'] = lps.weights.KNN.from_dataframe(
                    data, k=5, silence_warnings=True
                )
            except:
                context['knn_weights'] = None

        # Constants
        context['constant_1'] = np.ones(len(data))
        context['constant_0.5'] = np.full(len(data), 0.5)
        context['constant_2'] = np.full(len(data), 2.0)

        context['source_data'] = data

        return context

    def _initialize_population(self) -> List[GPNode]:
        """Initialize population with random trees"""
        population = []

        for _ in range(self.config.population_size):
            # Use ramped half-and-half initialization
            if random.random() < 0.5:
                # Full method
                depth = random.randint(self.config.min_tree_depth, self.config.max_tree_depth)
                tree = self._generate_full_tree(depth)
            else:
                # Grow method
                max_depth = random.randint(self.config.min_tree_depth, self.config.max_tree_depth)
                tree = self._generate_grow_tree(max_depth)

            population.append(tree)

        return population

    def _generate_full_tree(self, depth: int) -> GPNode:
        """Generate full tree of specified depth"""
        if depth == 1:
            # Terminal node
            terminal = random.choice(self.terminals)
            return GPNode('terminal', terminal)
        else:
            # Function node
            func_name = random.choice(list(self.functions.keys()))
            func, arity = self.functions[func_name]

            children = [self._generate_full_tree(depth - 1) for _ in range(arity)]

            return GPNode('function', func_name, children)

    def _generate_grow_tree(self, max_depth: int, current_depth: int = 0) -> GPNode:
        """Generate tree using grow method"""
        if current_depth >= max_depth or (current_depth > 0 and random.random() < 0.3):
            # Terminal node
            terminal = random.choice(self.terminals)
            return GPNode('terminal', terminal)
        else:
            # Function node
            func_name = random.choice(list(self.functions.keys()))
            func, arity = self.functions[func_name]

            children = [self._generate_grow_tree(max_depth, current_depth + 1) for _ in range(arity)]

            return GPNode('function', func_name, children)

    def _evaluate_population(self, population: List[GPNode], context: Dict,
                           target_data: pd.DataFrame) -> np.ndarray:
        """Evaluate fitness of population"""
        fitness_scores = np.zeros(len(population))

        target_values = target_data.iloc[:, 0].values

        for i, individual in enumerate(population):
            try:
                # Execute tree
                result = self._execute_tree(individual, context)

                if result is not None and len(result) == len(target_values):
                    # Calculate correlation
                    correlation = np.corrcoef(result, target_values)[0, 1]

                    # Check conservation
                    conservation_error = self._check_conservation(result, context['source_data'])

                    # Fitness combines correlation and conservation
                    if conservation_error < self.config.conservation_error_threshold:
                        fitness = abs(correlation)
                    else:
                        fitness = abs(correlation) * (1 - conservation_error)

                    # Parsimony pressure
                    size_penalty = individual.size() / 100.0
                    fitness = fitness / (1 + size_penalty * 0.01)

                    fitness_scores[i] = fitness
                else:
                    fitness_scores[i] = 0.0

            except Exception:
                fitness_scores[i] = 0.0

        return fitness_scores

    def _execute_tree(self, node: GPNode, context: Dict) -> Optional[np.ndarray]:
        """Execute GP tree and return result"""
        try:
            if node.node_type == 'terminal':
                # Return terminal value
                if node.value in context:
                    value = context[node.value]
                    if isinstance(value, lps.weights.W):
                        return value  # Return weights object
                    elif isinstance(value, np.ndarray):
                        return value.copy()
                    else:
                        return value
                else:
                    return None

            else:  # Function node
                # Execute children first
                child_results = []
                for child in node.children:
                    result = self._execute_tree(child, context)
                    child_results.append(result)

                # Apply function
                func, arity = self.functions[node.value]

                if all(r is not None for r in child_results):
                    try:
                        result = func(*child_results)
                        if isinstance(result, np.ndarray):
                            return result
                        else:
                            return None
                    except:
                        return None
                else:
                    return None

        except Exception:
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

    def _tournament_selection(self, population: List[GPNode], fitness_scores: np.ndarray) -> GPNode:
        """Tournament selection"""
        indices = np.random.choice(len(population), self.config.tournament_size, replace=False)
        winner_idx = indices[np.argmax(fitness_scores[indices])]
        return population[winner_idx].copy()

    def _crossover(self, parent1: GPNode, parent2: GPNode) -> GPNode:
        """Subtree crossover"""
        # Copy parents
        child1 = parent1.copy()
        child2 = parent2.copy()

        # Get all nodes
        nodes1 = self._get_all_nodes(child1)
        nodes2 = self._get_all_nodes(child2)

        if len(nodes1) > 1 and len(nodes2) > 1:
            # Select crossover points
            point1 = random.choice(nodes1[1:])  # Don't select root
            point2 = random.choice(nodes2)

            # Swap subtrees
            temp_children = point1.children
            temp_value = point1.value
            temp_type = point1.node_type

            point1.children = point2.children
            point1.value = point2.value
            point1.node_type = point2.node_type

            point2.children = temp_children
            point2.value = temp_value
            point2.node_type = temp_type

        # Check depth constraint
        if child1.depth() <= self.config.max_tree_depth:
            return child1
        else:
            return parent1.copy()

    def _mutate(self, individual: GPNode) -> GPNode:
        """Subtree mutation"""
        mutated = individual.copy()
        nodes = self._get_all_nodes(mutated)

        if nodes:
            # Select mutation point
            point = random.choice(nodes)

            # Generate new subtree
            if point.node_type == 'terminal':
                # Replace with new terminal
                point.value = random.choice(self.terminals)
            else:
                # Replace with new subtree
                new_depth = random.randint(1, 3)
                new_subtree = self._generate_full_tree(new_depth)
                point.children = new_subtree.children
                point.value = new_subtree.value
                point.node_type = new_subtree.node_type

        return mutated

    def _get_all_nodes(self, node: GPNode) -> List[GPNode]:
        """Get all nodes in tree"""
        nodes = [node]
        for child in node.children:
            nodes.extend(self._get_all_nodes(child))
        return nodes

    def _record_generation_stats(self, generation: int, fitness_scores: np.ndarray):
        """Record generation statistics"""
        self.generation_stats.append({
            'generation': generation,
            'best_fitness': np.max(fitness_scores),
            'mean_fitness': np.mean(fitness_scores),
            'std_fitness': np.std(fitness_scores),
            'correlations_found': len(self.discovered_correlations)
        })

    def _check_correlations(self, population: List[GPNode], fitness_scores: np.ndarray,
                          context: Dict, target_data: pd.DataFrame):
        """Check for valid correlations"""
        threshold_fitness = 0.5  # Minimum fitness for valid correlation

        for i, (individual, fitness) in enumerate(zip(population, fitness_scores)):
            if fitness > threshold_fitness:
                result = self._execute_tree(individual, context)

                if result is not None:
                    correlation_info = {
                        'tree': individual.to_string(),
                        'fitness': fitness,
                        'size': individual.size(),
                        'depth': individual.depth(),
                        'timestamp': time.time() - self.start_time
                    }

                    # Check if similar correlation already exists
                    is_novel = True
                    for existing in self.discovered_correlations:
                        if existing['tree'] == correlation_info['tree']:
                            is_novel = False
                            break

                    if is_novel:
                        self.discovered_correlations.append(correlation_info)

    def _check_discovery_rate(self) -> bool:
        """Check if discovery rate target is met"""
        if not self.discovered_correlations:
            return False

        elapsed_hours = (time.time() - self.start_time) / 3600
        discovery_rate = len(self.discovered_correlations) / max(elapsed_hours, 0.01)

        return discovery_rate >= self.config.discovery_target

    def _compile_final_results(self, source_data: gpd.GeoDataFrame,
                              target_data: pd.DataFrame, cbsa_info: pd.DataFrame) -> Dict:
        """Compile final results"""
        elapsed_time = time.time() - self.start_time

        # Get best individuals
        context = self._prepare_context(source_data)
        final_fitness = self._evaluate_population(self.population, context, target_data)
        best_indices = np.argsort(final_fitness)[-10:]

        best_solutions = []
        for idx in best_indices:
            best_solutions.append({
                'tree': self.population[idx].to_string(),
                'fitness': final_fitness[idx],
                'size': self.population[idx].size(),
                'depth': self.population[idx].depth()
            })

        return {
            'method': 'Traditional GP',
            'configuration': {
                'population_size': self.config.population_size,
                'generations': self.config.generations,
                'mutation_rate': self.config.mutation_rate,
                'crossover_rate': self.config.crossover_rate,
                'max_tree_depth': self.config.max_tree_depth
            },
            'performance': {
                'total_correlations_discovered': len(self.discovered_correlations),
                'discovery_rate': len(self.discovered_correlations) / (elapsed_time / 3600),
                'processing_time_seconds': elapsed_time,
                'generations_completed': len(self.generation_stats)
            },
            'best_solutions': best_solutions[:5],
            'evolution_history': {
                'best_fitness_progression': [s['best_fitness'] for s in self.generation_stats[-100:]],
                'discovery_progression': [s['correlations_found'] for s in self.generation_stats[-100:]]
            },
            'discovered_correlations': self.discovered_correlations[:10]
        }

    def save_results(self, results: Dict, filepath: str):
        """Save results to JSON file"""
        with open(filepath, 'w') as f:
            json_results = json.loads(json.dumps(results, default=str))
            json.dump(json_results, f, indent=2)


if __name__ == "__main__":
    # Example usage
    print("Traditional GP Comparator Implementation")
    print("=" * 50)

    # Initialize configuration
    config = GPConfig(
        population_size=100,
        generations=1000,
        mutation_rate=0.1,
        crossover_rate=0.8
    )

    # Create comparator instance
    comparator = TraditionalGPComparator(config)

    print(f"Configuration:")
    print(f"  Population Size: {config.population_size}")
    print(f"  Generations: {config.generations}")
    print(f"  Max Tree Depth: {config.max_tree_depth}")
    print(f"  Tournament Size: {config.tournament_size}")
    print(f"  Discovery Target: {config.discovery_target} correlations/hour")

    print("\nPrimitive Functions:")
    for func_name in comparator.functions.keys():
        print(f"  - {func_name}")

    print("\nPrimitive Terminals:")
    for terminal in comparator.terminals:
        print(f"  - {terminal}")

    print("\nReady for spatial correlation discovery using Traditional GP")
    print("No neural networks - pure evolutionary computation")