#!/usr/bin/env python3
"""
Test search queries for Dr. Ekren's communication
"""

import sys
sys.path.append('/Users/tarive/brain-poc/scripts')

from improved_scoring import ImprovedBrainScoring

def run_search(query, project_context="dci-analysis"):
    """Run a search query and display results"""
    brain = ImprovedBrainScoring()
    
    print(f"\n🔍 Searching for: '{query}'")
    print(f"   Project context: {project_context}")
    print("-" * 50)
    
    results = brain.search_with_scoring(query, project_context)
    
    if results:
        print(f"✅ Found {len(results)} result(s)")
        for i, result in enumerate(results[:3], 1):
            score = result['relevance_score']
            content = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
            
            print(f"\n{i}. Score: {score:.3f}")
            print(f"   Content: {content}")
            
            # Show confidence level
            if score > 0.9:
                confidence = "🟢 Very High Confidence"
            elif score > 0.8:
                confidence = "🟡 High Confidence" 
            elif score > 0.75:
                confidence = "🟠 Medium Confidence"
            else:
                confidence = "🔴 Low Confidence"
            
            print(f"   {confidence}")
    else:
        print("❌ No results found above threshold (0.75)")
    
    return results

if __name__ == "__main__":
    # Test the queries you wanted to run
    
    print("=" * 60)
    print("🧠 BRAIN SEARCH TEST - Dr. Ekren Communication")
    print("=" * 60)
    
    # Query 1: "Ekren positive dci"
    run_search("Ekren positive dci")
    
    # Query 2: "keep up good work"  
    run_search("keep up good work")
    
    # Query 3: Direct name search
    run_search("Dr Ekren")
    
    # Query 4: Project search
    run_search("dci-analysis project")
    
    # Query 5: Exact phrase
    run_search("taking shape nicely")
    
    print("\n" + "=" * 60)
    print("✅ Search test complete!")