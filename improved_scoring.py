#!/usr/bin/env python3
"""
Improved scoring algorithm based on POC findings
"""

import json
from pathlib import Path
import sys
from typing import Dict, List
sys.path.append('/Users/tarive/brain-poc/scripts')

from poc_scoring import BrainPOCScoring

class ImprovedBrainScoring(BrainPOCScoring):
    def __init__(self, poc_dir: str = "/Users/tarive/brain-poc"):
        super().__init__(poc_dir)
        
        # Adjusted configuration based on POC findings
        self.config.update({
            "confidence_threshold": 0.75,  # More realistic threshold
            "scoring_weights": {
                "temporal": 0.25,      # Slightly reduced
                "project": 0.25,       # Slightly reduced  
                "connection": 0.15,    # Reduced since we have few connections
                "semantic": 0.35       # Increased importance for semantic matching
            },
            "semantic_boost_factors": {
                "exact_phrase": 0.3,
                "partial_phrase": 0.15,
                "context_match": 0.2
            }
        })
    
    def _calculate_semantic_similarity(self, item: Dict, query: str) -> float:
        """Enhanced semantic similarity with phrase matching and context awareness"""
        content = item.get("content", "").lower()
        context = str(item.get("context", {})).lower()
        tags = " ".join(item.get("tags", [])).lower()
        query_lower = query.lower()
        
        # Combine all searchable text
        full_text = f"{content} {context} {tags}"
        
        # Base word overlap
        query_words = set(query_lower.split())
        content_words = set(full_text.split())
        
        if not query_words:
            return 0.0
        
        overlap = len(query_words.intersection(content_words))
        base_similarity = overlap / len(query_words)
        
        # Boost factors
        similarity_boost = 0
        
        # Exact phrase match (highest boost)
        if query_lower in full_text:
            similarity_boost += self.config["semantic_boost_factors"]["exact_phrase"]
        
        # Partial phrase matches
        query_phrases = self._get_query_phrases(query_lower)
        for phrase in query_phrases:
            if phrase in full_text and phrase not in query_lower:  # Avoid double counting
                similarity_boost += self.config["semantic_boost_factors"]["partial_phrase"]
        
        # Context-specific matches (boss + work context, etc.)
        if self._has_context_alignment(item, query_lower):
            similarity_boost += self.config["semantic_boost_factors"]["context_match"]
        
        final_similarity = min(base_similarity + similarity_boost, 1.0)
        return final_similarity
    
    def _get_query_phrases(self, query: str) -> List[str]:
        """Extract meaningful phrases from query"""
        words = query.split()
        phrases = []
        
        # Two-word phrases
        for i in range(len(words) - 1):
            phrases.append(f"{words[i]} {words[i+1]}")
        
        return phrases
    
    def _has_context_alignment(self, item: Dict, query: str) -> bool:
        """Check for contextual alignment between query and item"""
        context = item.get("context", {})
        
        # Boss-related queries should match boss context
        if "boss" in query and isinstance(context, dict):
            if context.get("source") == "boss":
                return True
        
        # Work-type alignment
        if isinstance(context, dict) and "work_type" in context:
            work_type = context["work_type"].lower()
            if work_type in query:
                return True
        
        # Project alignment
        project_id = item.get("project_id", "").lower()
        if project_id in query or any(word in project_id for word in query.split()):
            return True
        
        return False
    
    def _calculate_connection_density(self, content: str) -> float:
        """Enhanced connection density that doesn't penalize lack of links"""
        base_density = super()._calculate_connection_density(content)
        
        # If no explicit connections, use content richness as proxy
        if base_density == 0:
            # Longer content with specific terminology gets higher connection score
            word_count = len(content.split())
            
            # Technical/domain terms boost
            domain_terms = ["analysis", "data", "report", "economic", "spending", "patterns"]
            domain_score = sum(1 for term in domain_terms if term.lower() in content.lower())
            
            # Calculate proxy connection density
            richness_score = min((word_count / 50.0) + (domain_score / 10.0), 1.0)
            return richness_score * 0.6  # Cap at 0.6 for proxy connections
        
        return base_density

def test_improved_scoring():
    """Test the improved scoring algorithm"""
    brain = ImprovedBrainScoring()
    
    # Load items
    working_memory_dir = Path("/Users/tarive/brain-poc/working-memory")
    items = []
    
    for item_file in working_memory_dir.glob("wm_*.json"):
        with open(item_file) as f:
            items.append(json.load(f))
    
    print("🔬 Testing Improved Scoring Algorithm")
    print(f"   Confidence Threshold: {brain.config['confidence_threshold']}")
    print(f"   Scoring Weights: {brain.config['scoring_weights']}")
    print()
    
    test_queries = [
        ("boss THRC", "Should match boss THRC communication"),
        ("economic analysis", "Should match THRC analysis"),  
        ("consumer spending", "Should match spending analysis"),
        ("data quality", "Should match boss data quality mention")
    ]
    
    for query, description in test_queries:
        print(f"=== Query: '{query}' ===")
        
        scores = []
        for item in items:
            score = brain._calculate_relevance_score(item, query, "econ-data")
            breakdown = brain._get_score_breakdown(item, query, "econ-data")
            scores.append((score, item, breakdown))
        
        # Sort by score
        scores.sort(key=lambda x: x[0], reverse=True)
        best_score, best_item, best_breakdown = scores[0]
        
        print(f"🏆 Best: {best_item['content'][:60]}...")
        print(f"   Score: {best_score:.3f} (threshold: {brain.config['confidence_threshold']:.3f})")
        print(f"   Above threshold? {'✅ YES' if best_score >= brain.config['confidence_threshold'] else '❌ NO'}")
        print(f"   Breakdown:")
        for factor, data in best_breakdown.items():
            print(f"     {factor}: {data['factor']:.3f} × {data['weight']:.2f} = {data['contribution']:.3f}")
        print()

if __name__ == "__main__":
    test_improved_scoring()