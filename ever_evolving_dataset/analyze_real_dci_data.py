#!/usr/bin/env python3
"""
Analyze actual DCI datasets and compute real spatial statistics
Using actual data, not synthetic/random data
"""

import pandas as pd
import numpy as np
import geopandas as gpd
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("ANALYZING ACTUAL DCI DATASETS - REAL DATA, NOT SYNTHETIC")
print("="*70)

# Load the actual DCI datasets
print("\n1. Loading actual DCI datasets...")
try:
    dci_full = pd.read_excel('DCI-2019-2023-Full-Dataset.xlsx')
    print(f"✓ DCI Full Dataset loaded: {dci_full.shape}")
except Exception as e:
    print(f"Error loading full dataset: {e}")
    dci_full = None

try:
    dci_long = pd.read_excel('DCI_datasets_longitudinal_zip_scores.xlsx')
    print(f"✓ DCI Longitudinal Dataset loaded: {dci_long.shape}")
except Exception as e:
    print(f"Error loading longitudinal dataset: {e}")
    dci_long = None

# Examine the actual data structure
if dci_full is not None:
    print("\n2. DCI Full Dataset Structure:")
    print("-" * 50)
    print("Columns:", list(dci_full.columns)[:15])
    print("\nData types:")
    print(dci_full.dtypes.head(10))
    print("\nFirst 5 rows of actual data:")
    print(dci_full.head())

    # Check for ZCTA/ZIP codes
    zip_columns = [col for col in dci_full.columns if 'ZIP' in col.upper() or 'ZCTA' in col.upper()]
    print(f"\nZIP/ZCTA columns found: {zip_columns}")

    # Check for vulnerability/distress scores
    score_columns = [col for col in dci_full.columns if 'SCORE' in col.upper() or 'INDEX' in col.upper() or 'DCI' in col.upper()]
    print(f"Score/Index columns found: {score_columns}")

    # Get actual statistics
    print("\n3. Actual Data Statistics (NOT SYNTHETIC):")
    print("-" * 50)

    # Find numeric columns
    numeric_cols = dci_full.select_dtypes(include=[np.number]).columns
    print(f"Numeric columns: {list(numeric_cols)[:10]}")

    if len(numeric_cols) > 0:
        # Use the first numeric column as vulnerability score
        vuln_col = numeric_cols[0]
        actual_values = dci_full[vuln_col].dropna()

        print(f"\nAnalyzing column: '{vuln_col}'")
        print(f"Count: {len(actual_values)}")
        print(f"Mean: {actual_values.mean():.4f}")
        print(f"Std: {actual_values.std():.4f}")
        print(f"Min: {actual_values.min():.4f}")
        print(f"Max: {actual_values.max():.4f}")
        print(f"Median: {actual_values.median():.4f}")

        # Calculate Gini coefficient on ACTUAL data
        sorted_values = np.sort(actual_values)
        n = len(actual_values)
        cumsum = np.cumsum(sorted_values)
        gini = (2 * np.sum((np.arange(1, n+1)) * sorted_values)) / (n * cumsum[-1]) - (n + 1) / n
        print(f"\nGini Coefficient (ACTUAL DATA): {gini:.4f}")

if dci_long is not None:
    print("\n4. DCI Longitudinal Dataset Structure:")
    print("-" * 50)
    print("Columns:", list(dci_long.columns)[:15])
    print("\nFirst 5 rows of actual longitudinal data:")
    print(dci_long.head())

    # Check for years
    year_columns = [col for col in dci_long.columns if any(str(year) in str(col) for year in range(2019, 2024))]
    print(f"\nYear columns found: {year_columns[:10]}")

# Try to identify MSA/CBSA information
print("\n5. Geographic Identifiers:")
print("-" * 50)
if dci_full is not None:
    geo_columns = [col for col in dci_full.columns if any(term in col.upper() for term in ['MSA', 'CBSA', 'METRO', 'COUNTY', 'STATE'])]
    print(f"Geographic columns: {geo_columns}")

    if len(geo_columns) > 0:
        for col in geo_columns[:3]:
            unique_count = dci_full[col].nunique()
            print(f"  {col}: {unique_count} unique values")
            print(f"    Sample values: {dci_full[col].dropna().unique()[:5].tolist()}")

print("\n6. Data Quality Check:")
print("-" * 50)
if dci_full is not None:
    print(f"Total rows: {len(dci_full)}")
    print(f"Columns: {len(dci_full.columns)}")
    print(f"Missing values per column (first 10):")
    missing = dci_full.isnull().sum().head(10)
    for col, count in missing.items():
        pct = count / len(dci_full) * 100
        print(f"  {col}: {count} ({pct:.1f}%)")

print("\n" + "="*70)
print("IMPORTANT: These are ACTUAL DCI data statistics, NOT random/synthetic")
print("="*70)