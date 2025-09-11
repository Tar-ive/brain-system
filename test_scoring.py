#!/usr/bin/env python3
"""Test the scoring system with different queries"""

import json
from pathlib import Path
import sys
sys.path.append('/Users/tarive/brain-poc/scripts')

from poc_scoring import BrainPOCScoring

# Create brain instance 
brain = BrainPOCScoring()

# Load the stored items
working_memory_dir = Path("/Users/tarive/brain-poc/working-memory")
items = []

for item_file in working_memory_dir.glob("wm_*.json"):
    with open(item_file) as f:
        items.append(json.load(f))

print(f"Loaded {len(items)} items\n")

# Test different queries
test_queries = [
    ("boss THRC", "Should match the boss communication about THRC"),
    ("economic analysis", "Should match THRC economic analysis"),
    ("consumer spending", "Should match items mentioning consumer spending"),  
    ("weekend plans", "Should match the weekend item"),
    ("data quality", "Should match boss mention of data quality")
]

for query, description in test_queries:
    print(f"=== Testing: '{query}' ===")
    print(f"Expected: {description}")
    
    best_score = 0
    best_item = None
    
    for item in items:
        score = brain._calculate_relevance_score(item, query, "econ-data")
        breakdown = brain._get_score_breakdown(item, query, "econ-data")
        
        if score > best_score:
            best_score = score
            best_item = item
        
        print(f"\nItem: {item['content'][:60]}...")
        print(f"Score: {score:.3f}")
        print(f"  Temporal: {breakdown['temporal']['contribution']:.3f}")
        print(f"  Project: {breakdown['project']['contribution']:.3f}")  
        print(f"  Connection: {breakdown['connection']['contribution']:.3f}")
        print(f"  Semantic: {breakdown['semantic']['contribution']:.3f}")
    
    print(f"\n🏆 Best match (score: {best_score:.3f}): {best_item['content'][:60]}...")
    print(f"Above threshold (0.95)? {'✅ YES' if best_score >= 0.95 else '❌ NO'}")
    print("\n" + "="*70 + "\n")