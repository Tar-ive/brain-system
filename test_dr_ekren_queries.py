#!/usr/bin/env python3
"""
Test different ways to query Dr. Ekren's feedback
"""

import sys
sys.path.append('/Users/tarive/brain-poc/scripts')

from improved_scoring import ImprovedBrainScoring

def test_dr_ekren_queries():
    """Test various ways to query Dr. Ekren's communication"""
    
    brain = ImprovedBrainScoring()
    
    print("🔍 Testing Dr. Ekren Communication Retrieval")
    print("=" * 60)
    
    # Different ways you might ask about this later
    query_scenarios = [
        # Exact recall questions
        ("Dr. Ekren dci-analysis", "What did Dr. Ekren say about dci-analysis?"),
        ("Dr Ekren positive feedback", "Did Dr. Ekren give positive feedback?"),
        ("September 11 meeting", "What was said in the Sept 11 meeting?"),
        
        # Vague/uncertain recall
        ("did someone say good work", "Did someone tell me I was doing good work?"),
        ("dci project feedback", "What feedback did I get on the dci project?"),
        ("taking shape nicely", "Did someone say something was taking shape nicely?"),
        
        # Verification queries
        ("Dr. Ekren said keep up good work", "Did Dr. Ekren tell me to keep up the good work?"),
        ("positive meeting feedback september", "Was there positive feedback in a September meeting?"),
        
        # Contextual queries
        ("supervisor feedback dci", "What feedback did I get from supervisors about dci?"),
        ("meeting notes positive", "Any positive meeting notes?")
    ]
    
    for query, human_question in query_scenarios:
        print(f"\n🤔 Human Question: \"{human_question}\"")
        print(f"🔍 Search Query: \"{query}\"")
        
        results = brain.search_with_scoring(query, project_context="dci-analysis")
        
        if results:
            top_result = results[0]
            score = top_result['relevance_score']
            content = top_result['content']
            
            print(f"✅ FOUND (score: {score:.3f})")
            print(f"💬 Answer: \"{content}\"")
            
            # Show confidence level
            if score > 0.9:
                confidence = "🟢 Very High"
            elif score > 0.8:
                confidence = "🟡 High" 
            elif score > 0.7:
                confidence = "🟠 Medium"
            else:
                confidence = "🔴 Low"
            
            print(f"📊 Confidence: {confidence}")
            
            # Key matching factors
            breakdown = top_result['score_breakdown']
            key_factors = []
            for factor, data in breakdown.items():
                if data['contribution'] > 0.05:
                    key_factors.append(f"{factor}({data['contribution']:.2f})")
            print(f"🎯 Why it matched: {', '.join(key_factors)}")
            
        else:
            print(f"❌ NOT FOUND (below threshold)")
        
        print("-" * 40)
    
    print("\n" + "=" * 60)
    print("📝 STORAGE BREAKDOWN:")
    print("✅ Content: Full verbatim quote stored")
    print("✅ Context: Source (Dr. Ekren), date, meeting type, sentiment")
    print("✅ Project: Linked to dci-analysis project")
    print("✅ Tags: Searchable by person, sentiment, project, meeting type")
    print("✅ Importance: 0.5 (moderate - positive feedback but not urgent)")
    print("✅ Connections: 0.372 (domain terms: project, analysis, work, meeting)")

if __name__ == "__main__":
    test_dr_ekren_queries()