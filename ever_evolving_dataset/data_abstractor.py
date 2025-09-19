"""
Abstract Data Representation Layer for Ever-Expanding Dataset System.

This module converts any dataset into domain-agnostic representations
that capture statistical, semantic, structural, temporal, and spatial properties.
"""

import numpy as np
import pandas as pd
import geopandas as gpd
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass
from scipy import stats
from scipy.spatial import distance
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sentence_transformers import SentenceTransformer
import hashlib
import json


@dataclass
class StatisticalSignature:
    """Statistical properties of a dataset."""
    cardinality: Dict[str, int]
    distributions: Dict[str, Dict[str, float]]
    null_patterns: np.ndarray
    correlations: np.ndarray
    entropy: Dict[str, float]
    mutual_information: Dict[Tuple[str, str], float]


@dataclass
class SemanticSignature:
    """Semantic properties derived from column names and values."""
    column_embeddings: np.ndarray
    value_sample_embeddings: np.ndarray
    context_vector: np.ndarray
    semantic_types: Dict[str, str]
    domain_indicators: Dict[str, float]


@dataclass
class StructuralSignature:
    """Structural properties of the dataset."""
    shape: Tuple[int, int]
    dtypes: Dict[str, str]
    key_candidates: List[str]
    functional_dependencies: List[Tuple[str, str]]
    hierarchy_levels: Dict[str, int]
    graph_properties: Dict[str, Any]


@dataclass
class TemporalSignature:
    """Temporal properties if time-based data is present."""
    temporal_columns: List[str]
    frequency: Optional[str]
    seasonality: Dict[str, float]
    trend: Dict[str, float]
    stationarity: Dict[str, bool]


@dataclass
class SpatialSignature:
    """Spatial properties if geographic data is present."""
    geometry_type: Optional[str]
    crs: Optional[str]
    spatial_extent: Optional[Dict[str, float]]
    spatial_autocorrelation: Optional[float]
    topology: Optional[Dict[str, Any]]


class DataAbstractor:
    """Converts datasets into abstract representations for correlation discovery."""

    def __init__(self, semantic_model: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the data abstractor.

        Args:
            semantic_model: Name of the sentence transformer model for embeddings.
        """
        self.semantic_encoder = SentenceTransformer(semantic_model)
        self.scaler = StandardScaler()

    def extract_signatures(
        self,
        data: Union[pd.DataFrame, gpd.GeoDataFrame],
        dataset_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract comprehensive signatures from a dataset.

        Args:
            data: Input dataset
            dataset_id: Optional identifier for the dataset

        Returns:
            Dictionary containing all extracted signatures
        """
        if dataset_id is None:
            dataset_id = self._generate_dataset_id(data)

        signatures = {
            'dataset_id': dataset_id,
            'statistical': self._extract_statistical_signature(data),
            'semantic': self._extract_semantic_signature(data),
            'structural': self._extract_structural_signature(data)
        }

        # Extract temporal signature if temporal data detected
        if self._has_temporal_data(data):
            signatures['temporal'] = self._extract_temporal_signature(data)

        # Extract spatial signature if geographic data detected
        if isinstance(data, gpd.GeoDataFrame):
            signatures['spatial'] = self._extract_spatial_signature(data)

        return signatures

    def _generate_dataset_id(self, data: pd.DataFrame) -> str:
        """Generate unique identifier for dataset."""
        content = str(data.columns.tolist()) + str(data.shape)
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _extract_statistical_signature(self, data: pd.DataFrame) -> StatisticalSignature:
        """Extract statistical properties."""
        numeric_cols = data.select_dtypes(include=[np.number]).columns

        # Cardinality analysis
        cardinality = {col: data[col].nunique() for col in data.columns}

        # Distribution parameters for numeric columns
        distributions = {}
        for col in numeric_cols:
            if len(data[col].dropna()) > 0:
                distributions[col] = {
                    'mean': float(data[col].mean()),
                    'std': float(data[col].std()),
                    'skew': float(stats.skew(data[col].dropna())),
                    'kurtosis': float(stats.kurtosis(data[col].dropna())),
                    'min': float(data[col].min()),
                    'max': float(data[col].max()),
                    'q25': float(data[col].quantile(0.25)),
                    'q50': float(data[col].quantile(0.50)),
                    'q75': float(data[col].quantile(0.75))
                }

        # Null patterns
        null_patterns = data.isnull().values.astype(float)

        # Correlation matrix for numeric columns
        if len(numeric_cols) > 0:
            correlations = data[numeric_cols].corr().values
        else:
            correlations = np.array([[]])

        # Entropy for categorical columns
        entropy = {}
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            value_counts = data[col].value_counts(normalize=True)
            entropy[col] = float(stats.entropy(value_counts))

        # Mutual information between column pairs
        mutual_information = self._calculate_mutual_information(data)

        return StatisticalSignature(
            cardinality=cardinality,
            distributions=distributions,
            null_patterns=null_patterns,
            correlations=correlations,
            entropy=entropy,
            mutual_information=mutual_information
        )

    def _extract_semantic_signature(self, data: pd.DataFrame) -> SemanticSignature:
        """Extract semantic properties using transformer embeddings."""
        # Encode column names
        column_names = data.columns.tolist()
        column_embeddings = self.semantic_encoder.encode(column_names)

        # Sample and encode values
        value_samples = []
        for col in data.columns:
            # Sample up to 10 unique values
            unique_values = data[col].dropna().unique()[:10]
            value_samples.extend([f"{col}: {val}" for val in unique_values])

        if value_samples:
            value_sample_embeddings = self.semantic_encoder.encode(value_samples)
        else:
            value_sample_embeddings = np.array([[]])

        # Create context vector
        context_vector = np.mean(column_embeddings, axis=0)

        # Infer semantic types
        semantic_types = self._infer_semantic_types(data)

        # Domain indicators
        domain_indicators = self._detect_domain_indicators(column_names)

        return SemanticSignature(
            column_embeddings=column_embeddings,
            value_sample_embeddings=value_sample_embeddings,
            context_vector=context_vector,
            semantic_types=semantic_types,
            domain_indicators=domain_indicators
        )

    def _extract_structural_signature(self, data: pd.DataFrame) -> StructuralSignature:
        """Extract structural properties."""
        shape = data.shape
        dtypes = {col: str(dtype) for col, dtype in data.dtypes.items()}

        # Find key candidates
        key_candidates = self._find_key_candidates(data)

        # Detect functional dependencies
        functional_dependencies = self._detect_functional_dependencies(data)

        # Detect hierarchy levels
        hierarchy_levels = self._detect_hierarchy_levels(data)

        # Graph properties
        graph_properties = self._compute_graph_properties(data)

        return StructuralSignature(
            shape=shape,
            dtypes=dtypes,
            key_candidates=key_candidates,
            functional_dependencies=functional_dependencies,
            hierarchy_levels=hierarchy_levels,
            graph_properties=graph_properties
        )

    def _extract_temporal_signature(self, data: pd.DataFrame) -> TemporalSignature:
        """Extract temporal properties."""
        temporal_columns = []
        for col in data.columns:
            if pd.api.types.is_datetime64_any_dtype(data[col]):
                temporal_columns.append(col)

        if not temporal_columns:
            return TemporalSignature(
                temporal_columns=[],
                frequency=None,
                seasonality={},
                trend={},
                stationarity={}
            )

        # Detect frequency
        primary_time_col = temporal_columns[0]
        frequency = self._detect_frequency(data[primary_time_col])

        # Analyze time series properties
        seasonality = {}
        trend = {}
        stationarity = {}

        for col in data.select_dtypes(include=[np.number]).columns:
            if len(data[col].dropna()) > 10:
                seasonality[col] = self._detect_seasonality(data[col])
                trend[col] = self._detect_trend(data[col])
                stationarity[col] = self._test_stationarity(data[col])

        return TemporalSignature(
            temporal_columns=temporal_columns,
            frequency=frequency,
            seasonality=seasonality,
            trend=trend,
            stationarity=stationarity
        )

    def _extract_spatial_signature(self, gdf: gpd.GeoDataFrame) -> SpatialSignature:
        """Extract spatial properties from GeoDataFrame."""
        # Geometry type
        geometry_types = gdf.geometry.geom_type.unique()
        geometry_type = geometry_types[0] if len(geometry_types) == 1 else 'Mixed'

        # CRS
        crs = str(gdf.crs) if gdf.crs else None

        # Spatial extent
        if not gdf.empty:
            bounds = gdf.total_bounds
            spatial_extent = {
                'minx': float(bounds[0]),
                'miny': float(bounds[1]),
                'maxx': float(bounds[2]),
                'maxy': float(bounds[3])
            }
        else:
            spatial_extent = None

        # Spatial autocorrelation (simplified)
        spatial_autocorrelation = self._calculate_spatial_autocorrelation(gdf)

        # Topology
        topology = self._analyze_topology(gdf)

        return SpatialSignature(
            geometry_type=geometry_type,
            crs=crs,
            spatial_extent=spatial_extent,
            spatial_autocorrelation=spatial_autocorrelation,
            topology=topology
        )

    def _calculate_mutual_information(self, data: pd.DataFrame) -> Dict[Tuple[str, str], float]:
        """Calculate mutual information between column pairs."""
        mutual_info = {}
        columns = data.columns.tolist()

        for i, col1 in enumerate(columns):
            for col2 in columns[i + 1:]:
                # Simplified MI calculation
                mi_value = self._estimate_mutual_information(data[col1], data[col2])
                mutual_info[(col1, col2)] = mi_value

        return mutual_info

    def _estimate_mutual_information(self, x: pd.Series, y: pd.Series) -> float:
        """Estimate mutual information between two series."""
        # Handle missing values
        mask = (~x.isna()) & (~y.isna())
        x_clean = x[mask]
        y_clean = y[mask]

        if len(x_clean) < 2:
            return 0.0

        # Discretize continuous variables
        if pd.api.types.is_numeric_dtype(x_clean):
            x_clean = pd.qcut(x_clean, q=min(10, len(x_clean.unique())), duplicates='drop')
        if pd.api.types.is_numeric_dtype(y_clean):
            y_clean = pd.qcut(y_clean, q=min(10, len(y_clean.unique())), duplicates='drop')

        # Calculate MI using contingency table
        contingency = pd.crosstab(x_clean, y_clean)
        mi = 0.0

        for i in contingency.index:
            for j in contingency.columns:
                pxy = contingency.loc[i, j] / contingency.sum().sum()
                if pxy > 0:
                    px = contingency.loc[i].sum() / contingency.sum().sum()
                    py = contingency[j].sum() / contingency.sum().sum()
                    mi += pxy * np.log(pxy / (px * py))

        return float(mi)

    def _infer_semantic_types(self, data: pd.DataFrame) -> Dict[str, str]:
        """Infer semantic types of columns."""
        semantic_types = {}

        for col in data.columns:
            col_lower = col.lower()

            # Geographic indicators
            if any(geo in col_lower for geo in ['lat', 'lon', 'geo', 'location']):
                semantic_types[col] = 'geographic'
            # Temporal indicators
            elif any(time in col_lower for time in ['date', 'time', 'year', 'month']):
                semantic_types[col] = 'temporal'
            # Identifier indicators
            elif any(id_term in col_lower for id_term in ['id', 'key', 'code']):
                semantic_types[col] = 'identifier'
            # Numeric measures
            elif pd.api.types.is_numeric_dtype(data[col]):
                semantic_types[col] = 'measure'
            # Text/categorical
            else:
                semantic_types[col] = 'categorical'

        return semantic_types

    def _detect_domain_indicators(self, column_names: List[str]) -> Dict[str, float]:
        """Detect domain-specific indicators from column names."""
        domains = {
            'financial': ['price', 'cost', 'revenue', 'profit', 'margin'],
            'geographic': ['lat', 'lon', 'geo', 'location', 'address'],
            'temporal': ['date', 'time', 'year', 'month', 'day'],
            'demographic': ['age', 'gender', 'population', 'income'],
            'medical': ['diagnosis', 'treatment', 'symptom', 'patient']
        }

        indicators = {}
        for domain, keywords in domains.items():
            score = sum(
                1 for col in column_names
                if any(keyword in col.lower() for keyword in keywords)
            ) / len(column_names)
            indicators[domain] = float(score)

        return indicators

    def _find_key_candidates(self, data: pd.DataFrame) -> List[str]:
        """Find columns that could serve as keys."""
        candidates = []
        n_rows = len(data)

        for col in data.columns:
            if data[col].dtype == 'object' or pd.api.types.is_integer_dtype(data[col]):
                uniqueness_ratio = data[col].nunique() / n_rows
                if 0.5 < uniqueness_ratio <= 1.0:
                    candidates.append(col)

        return candidates

    def _detect_functional_dependencies(self, data: pd.DataFrame) -> List[Tuple[str, str]]:
        """Detect functional dependencies between columns."""
        dependencies = []
        columns = data.columns.tolist()

        for col1 in columns:
            for col2 in columns:
                if col1 != col2:
                    # Check if col1 determines col2
                    grouped = data.groupby(col1)[col2].nunique()
                    if (grouped == 1).all():
                        dependencies.append((col1, col2))

        return dependencies

    def _detect_hierarchy_levels(self, data: pd.DataFrame) -> Dict[str, int]:
        """Detect hierarchical levels in categorical columns."""
        hierarchy = {}

        categorical_cols = data.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            cardinality = data[col].nunique()
            # Assign level based on cardinality
            if cardinality <= 10:
                hierarchy[col] = 1  # Top level
            elif cardinality <= 100:
                hierarchy[col] = 2  # Middle level
            else:
                hierarchy[col] = 3  # Detail level

        return hierarchy

    def _compute_graph_properties(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Compute graph properties of the dataset structure."""
        n_nodes = len(data.columns)
        n_edges = 0  # Count of detected relationships

        # Count relationships based on correlations and dependencies
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = data[numeric_cols].corr().abs()
            n_edges = ((corr_matrix > 0.5) & (corr_matrix < 1.0)).sum().sum() // 2

        return {
            'n_nodes': n_nodes,
            'n_edges': n_edges,
            'density': n_edges / (n_nodes * (n_nodes - 1) / 2) if n_nodes > 1 else 0,
            'connected': n_edges > 0
        }

    def _has_temporal_data(self, data: pd.DataFrame) -> bool:
        """Check if dataset contains temporal data."""
        for col in data.columns:
            if pd.api.types.is_datetime64_any_dtype(data[col]):
                return True
            # Check for date-like strings
            if data[col].dtype == 'object':
                try:
                    pd.to_datetime(data[col].head(10), errors='coerce')
                    if data[col].head(10).notna().any():
                        return True
                except:
                    continue
        return False

    def _detect_frequency(self, time_series: pd.Series) -> Optional[str]:
        """Detect frequency of time series."""
        if len(time_series) < 2:
            return None

        # Calculate differences
        sorted_times = time_series.dropna().sort_values()
        if len(sorted_times) < 2:
            return None

        diffs = sorted_times.diff().dropna()
        if len(diffs) == 0:
            return None

        # Most common difference
        mode_diff = diffs.mode()
        if len(mode_diff) == 0:
            return None

        mode_diff = mode_diff.iloc[0]

        # Map to frequency string
        if mode_diff == pd.Timedelta(days=1):
            return 'daily'
        elif mode_diff == pd.Timedelta(days=7):
            return 'weekly'
        elif 28 <= mode_diff.days <= 31:
            return 'monthly'
        elif 365 <= mode_diff.days <= 366:
            return 'yearly'
        else:
            return 'irregular'

    def _detect_seasonality(self, series: pd.Series) -> float:
        """Detect seasonality in numeric series."""
        # Simplified seasonality detection
        clean_series = series.dropna()
        if len(clean_series) < 12:
            return 0.0

        # Use autocorrelation at different lags
        try:
            acf_12 = clean_series.autocorr(lag=12) if len(clean_series) > 12 else 0
            acf_4 = clean_series.autocorr(lag=4) if len(clean_series) > 4 else 0
            return float(max(abs(acf_12), abs(acf_4)))
        except:
            return 0.0

    def _detect_trend(self, series: pd.Series) -> float:
        """Detect trend in numeric series."""
        clean_series = series.dropna()
        if len(clean_series) < 2:
            return 0.0

        # Linear regression slope
        x = np.arange(len(clean_series))
        slope, _ = np.polyfit(x, clean_series.values, 1)
        return float(slope)

    def _test_stationarity(self, series: pd.Series) -> bool:
        """Test if series is stationary."""
        # Simplified stationarity test
        clean_series = series.dropna()
        if len(clean_series) < 10:
            return False

        # Check if mean and variance are relatively constant
        mid_point = len(clean_series) // 2
        first_half = clean_series[:mid_point]
        second_half = clean_series[mid_point:]

        mean_diff = abs(first_half.mean() - second_half.mean())
        var_diff = abs(first_half.var() - second_half.var())

        # Threshold-based decision
        is_stationary = mean_diff < 0.1 * abs(clean_series.mean()) and \
                       var_diff < 0.1 * clean_series.var()

        return bool(is_stationary)

    def _calculate_spatial_autocorrelation(self, gdf: gpd.GeoDataFrame) -> Optional[float]:
        """Calculate spatial autocorrelation (simplified Moran's I)."""
        if len(gdf) < 3:
            return None

        # Find a numeric column for analysis
        numeric_cols = gdf.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return None

        # Use first numeric column
        values = gdf[numeric_cols[0]].values

        # Simplified spatial weights based on distance
        centroids = gdf.geometry.centroid
        distances = np.zeros((len(gdf), len(gdf)))

        for i in range(len(gdf)):
            for j in range(len(gdf)):
                if i != j:
                    distances[i, j] = centroids.iloc[i].distance(centroids.iloc[j])

        # Create binary weights (neighbors within threshold)
        threshold = np.percentile(distances[distances > 0], 25)
        weights = (distances > 0) & (distances < threshold)

        # Calculate Moran's I
        n = len(values)
        mean_val = values.mean()
        numerator = 0
        denominator = 0

        for i in range(n):
            for j in range(n):
                if weights[i, j]:
                    numerator += weights[i, j] * (values[i] - mean_val) * (values[j] - mean_val)

            denominator += (values[i] - mean_val) ** 2

        W = weights.sum()
        if W == 0 or denominator == 0:
            return 0.0

        morans_i = (n / W) * (numerator / denominator)
        return float(morans_i)

    def _analyze_topology(self, gdf: gpd.GeoDataFrame) -> Optional[Dict[str, Any]]:
        """Analyze spatial topology."""
        if len(gdf) == 0:
            return None

        topology = {
            'n_features': len(gdf),
            'geometry_types': gdf.geometry.geom_type.value_counts().to_dict(),
            'has_overlaps': False,
            'has_gaps': False
        }

        # Check for overlaps (simplified)
        if len(gdf) > 1:
            for i in range(min(10, len(gdf))):  # Check first 10 for performance
                for j in range(i + 1, min(10, len(gdf))):
                    if gdf.geometry.iloc[i].intersects(gdf.geometry.iloc[j]):
                        topology['has_overlaps'] = True
                        break

        return topology


class SignatureComparator:
    """Compare signatures to identify potential correlations."""

    def __init__(self):
        self.similarity_threshold = 0.7

    def compare_signatures(
        self,
        sig1: Dict[str, Any],
        sig2: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Compare two data signatures and return similarity scores.

        Args:
            sig1: First signature
            sig2: Second signature

        Returns:
            Dictionary of similarity scores by component
        """
        scores = {}

        # Statistical similarity
        if 'statistical' in sig1 and 'statistical' in sig2:
            scores['statistical'] = self._compare_statistical(
                sig1['statistical'],
                sig2['statistical']
            )

        # Semantic similarity
        if 'semantic' in sig1 and 'semantic' in sig2:
            scores['semantic'] = self._compare_semantic(
                sig1['semantic'],
                sig2['semantic']
            )

        # Structural similarity
        if 'structural' in sig1 and 'structural' in sig2:
            scores['structural'] = self._compare_structural(
                sig1['structural'],
                sig2['structural']
            )

        # Overall score
        scores['overall'] = np.mean(list(scores.values()))

        return scores

    def _compare_statistical(
        self,
        stat1: StatisticalSignature,
        stat2: StatisticalSignature
    ) -> float:
        """Compare statistical signatures."""
        similarities = []

        # Compare cardinality distributions
        card1 = np.array(list(stat1.cardinality.values()))
        card2 = np.array(list(stat2.cardinality.values()))

        if len(card1) > 0 and len(card2) > 0:
            # Normalize and compare
            card1_norm = card1 / (card1.max() + 1e-10)
            card2_norm = card2 / (card2.max() + 1e-10)

            # Pad to same length
            max_len = max(len(card1_norm), len(card2_norm))
            card1_padded = np.pad(card1_norm, (0, max_len - len(card1_norm)))
            card2_padded = np.pad(card2_norm, (0, max_len - len(card2_norm)))

            similarity = 1 - distance.cosine(card1_padded, card2_padded)
            similarities.append(similarity)

        # Compare entropy distributions
        if stat1.entropy and stat2.entropy:
            ent1 = np.array(list(stat1.entropy.values()))
            ent2 = np.array(list(stat2.entropy.values()))

            if len(ent1) > 0 and len(ent2) > 0:
                similarity = 1 - abs(ent1.mean() - ent2.mean()) / (max(ent1.mean(), ent2.mean()) + 1e-10)
                similarities.append(similarity)

        return float(np.mean(similarities)) if similarities else 0.5

    def _compare_semantic(
        self,
        sem1: SemanticSignature,
        sem2: SemanticSignature
    ) -> float:
        """Compare semantic signatures."""
        # Compare context vectors
        if sem1.context_vector.shape[0] > 0 and sem2.context_vector.shape[0] > 0:
            similarity = 1 - distance.cosine(sem1.context_vector, sem2.context_vector)
        else:
            similarity = 0.5

        # Compare domain indicators
        if sem1.domain_indicators and sem2.domain_indicators:
            common_domains = set(sem1.domain_indicators.keys()) & set(sem2.domain_indicators.keys())
            if common_domains:
                domain_sim = []
                for domain in common_domains:
                    diff = abs(sem1.domain_indicators[domain] - sem2.domain_indicators[domain])
                    domain_sim.append(1 - diff)
                similarity = (similarity + np.mean(domain_sim)) / 2

        return float(similarity)

    def _compare_structural(
        self,
        struct1: StructuralSignature,
        struct2: StructuralSignature
    ) -> float:
        """Compare structural signatures."""
        similarities = []

        # Shape similarity
        shape_sim = 1 - abs(np.log10(struct1.shape[0] + 1) - np.log10(struct2.shape[0] + 1)) / 10
        similarities.append(max(0, shape_sim))

        # Key candidate overlap
        if struct1.key_candidates and struct2.key_candidates:
            # Check if similar types of keys exist
            key_sim = len(set(struct1.key_candidates) & set(struct2.key_candidates)) / \
                     max(len(struct1.key_candidates), len(struct2.key_candidates))
            similarities.append(key_sim)

        # Graph property similarity
        if struct1.graph_properties and struct2.graph_properties:
            density_diff = abs(struct1.graph_properties.get('density', 0) -
                             struct2.graph_properties.get('density', 0))
            density_sim = 1 - density_diff
            similarities.append(density_sim)

        return float(np.mean(similarities)) if similarities else 0.5