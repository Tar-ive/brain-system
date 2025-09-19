#!/usr/bin/env python3
"""Debug why some queries are missing the Dr. Ekren communication"""

import sys
sys.path.append('/Users/tarive/brain-poc/scripts')

from improved_scoring import ImprovedBrainScoring

brain = ImprovedBrainScoring()

# Test the missed queries with detailed breakdown
missed_queries = [
    "Dr Ekren positive feedback",
    "September 11 meeting", 
    "dci project feedback",
    "supervisor feedback dci"
]

print("🔍 Debugging Missed Queries")
print("=" * 50)

for query in missed_queries:
    print(f"\n🔍 Query: '{query}'")
    
    # Get all items and score them manually
    all_items = brain._load_all_items()
    
    for item in all_items:
        if "Dr. Ekren" in item.get('content', ''):
            score = brain._calculate_relevance_score(item, query, "dci-analysis")
            breakdown = brain._get_score_breakdown(item, query, "dci-analysis")
            
            print(f"   📊 Score: {score:.3f} (threshold: {brain.config['confidence_threshold']:.3f})")
            print(f"   Content: {item['content'][:60]}...")
            print(f"   Breakdown:")
            for factor, data in breakdown.items():
                print(f"     {factor}: factor={data['factor']:.3f}, contribution={data['contribution']:.3f}")
            
            # Check semantic similarity in detail
            print(f"   🔍 Semantic Analysis:")
            content_words = set(item['content'].lower().split())
            context_words = set(str(item.get('context', {})).lower().split())
            tags_words = set(' '.join(item.get('tags', [])).lower().split())
            query_words = set(query.lower().split())
            
            all_words = content_words | context_words | tags_words
            overlap = query_words & all_words
            
            print(f"     Query words: {query_words}")
            print(f"     Available words: {sorted(list(all_words))}")
            print(f"     Overlap: {overlap}")
            print(f"     Overlap ratio: {len(overlap)}/{len(query_words)} = {len(overlap)/len(query_words):.3f}")
            break