#!/usr/bin/env python3
"""Debug the scoring system to see what scores we're getting"""

import sys
sys.path.append('/Users/tarive/brain-poc/scripts')

from poc_scoring import BrainPOCScoring

# Create brain instance with lower threshold for debugging
brain = BrainPOCScoring()
brain.config["confidence_threshold"] = 0.1  # Lower threshold to see all scores

# Load all items and manually score them
all_items = brain._load_all_items()

print(f"Found {len(all_items)} items in storage\n")

queries = ["boss THRC", "consumer spending", "weekend plans", "economic analysis"]

for query in queries:
    print(f"=== Query: '{query}' ===")
    
    for i, item in enumerate(all_items, 1):
        score = brain._calculate_relevance_score(item, query, "econ-data")
        breakdown = brain._get_score_breakdown(item, query, "econ-data")
        
        print(f"\nItem {i}: {item['content'][:50]}...")
        print(f"Overall Score: {score:.3f}")
        print("Breakdown:")
        for factor, data in breakdown.items():
            print(f"  {factor}: {data['factor']:.3f} × {data['weight']:.1f} = {data['contribution']:.3f}")
    print("\n" + "="*60 + "\n")