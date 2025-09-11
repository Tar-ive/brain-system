#!/usr/bin/env python3
"""
Brain System Proof of Concept - Scoring Algorithm
Tests the multi-factor relevance scoring system
"""

import json
import math
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class BrainPOCScoring:
    def __init__(self, poc_dir: str = "/Users/tarive/brain-poc"):
        self.poc_dir = Path(poc_dir)
        self.data_dir = self.poc_dir / "data"
        self.working_memory_dir = self.poc_dir / "working-memory"
        
        # Scoring configuration
        self.config = {
            "confidence_threshold": 0.95,
            "temporal_decay_rate": 0.95,
            "max_working_memory_items": 7,
            "scoring_weights": {
                "temporal": 0.3,     # Recent content preferred
                "project": 0.3,      # Project-relevant content preferred  
                "connection": 0.2,   # Well-connected content preferred
                "semantic": 0.2      # Semantically relevant content preferred
            }
        }
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.working_memory_dir.mkdir(parents=True, exist_ok=True)
    
    def store_working_memory_item(self, item_data: Dict) -> str:
        """
        Store an item in working memory with automatic metadata
        Returns: item_id for future reference
        """
        timestamp = datetime.now(timezone.utc)
        item_id = f"wm_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        # Enrich item with metadata
        enriched_item = {
            "id": item_id,
            "stored_at": timestamp.isoformat(),
            "content": item_data.get("content", ""),
            "context": item_data.get("context", {}),
            "project_id": item_data.get("project_id", "unknown"),
            "thinking_mode": item_data.get("thinking_mode", "capture"),
            "importance_score": self._calculate_importance_score(item_data),
            "connection_density": self._calculate_connection_density(item_data.get("content", "")),
            "tags": item_data.get("tags", [])
        }
        
        # Store to file
        item_file = self.working_memory_dir / f"{item_id}.json"
        with open(item_file, 'w') as f:
            json.dump(enriched_item, f, indent=2)
        
        # Update working memory index
        self._update_working_memory_index(enriched_item)
        
        print(f"✅ Stored working memory item: {item_id}")
        print(f"   Importance: {enriched_item['importance_score']:.3f}")
        print(f"   Connections: {enriched_item['connection_density']:.3f}")
        
        return item_id
    
    def search_with_scoring(self, query: str, project_context: Optional[str] = None) -> List[Dict]:
        """
        Search working memory and data with relevance scoring
        """
        print(f"\n🔍 Searching for: '{query}' (context: {project_context})")
        
        # Get all stored items
        all_items = self._load_all_items()
        
        if not all_items:
            print("❌ No items found in storage")
            return []
        
        # Score each item
        scored_results = []
        for item in all_items:
            score = self._calculate_relevance_score(item, query, project_context)
            
            if score >= self.config["confidence_threshold"]:
                item["relevance_score"] = score
                item["score_breakdown"] = self._get_score_breakdown(item, query, project_context)
                scored_results.append(item)
        
        # Sort by relevance (highest first)
        scored_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        print(f"✅ Found {len(scored_results)} high-confidence results")
        return scored_results
    
    def _calculate_relevance_score(self, item: Dict, query: str, project_context: Optional[str]) -> float:
        """
        Multi-factor relevance scoring algorithm
        """
        weights = self.config["scoring_weights"]
        
        # 1. Temporal relevance (exponential decay)
        temporal_factor = self._calculate_temporal_factor(item)
        
        # 2. Project alignment
        project_factor = self._calculate_project_alignment(item, project_context)
        
        # 3. Connection density (from stored metadata)
        connection_factor = item.get("connection_density", 0.0)
        
        # 4. Semantic similarity
        semantic_factor = self._calculate_semantic_similarity(item, query)
        
        # Weighted combination
        relevance_score = (
            weights["temporal"] * temporal_factor +
            weights["project"] * project_factor +
            weights["connection"] * connection_factor +
            weights["semantic"] * semantic_factor
        )
        
        return min(relevance_score, 1.0)
    
    def _get_score_breakdown(self, item: Dict, query: str, project_context: Optional[str]) -> Dict:
        """
        Get detailed scoring breakdown for analysis
        """
        weights = self.config["scoring_weights"]
        
        temporal_factor = self._calculate_temporal_factor(item)
        project_factor = self._calculate_project_alignment(item, project_context)
        connection_factor = item.get("connection_density", 0.0)
        semantic_factor = self._calculate_semantic_similarity(item, query)
        
        return {
            "temporal": {
                "factor": temporal_factor,
                "weight": weights["temporal"],
                "contribution": weights["temporal"] * temporal_factor
            },
            "project": {
                "factor": project_factor,
                "weight": weights["project"],
                "contribution": weights["project"] * project_factor
            },
            "connection": {
                "factor": connection_factor,
                "weight": weights["connection"],
                "contribution": weights["connection"] * connection_factor
            },
            "semantic": {
                "factor": semantic_factor,
                "weight": weights["semantic"],
                "contribution": weights["semantic"] * semantic_factor
            }
        }
    
    def _calculate_temporal_factor(self, item: Dict) -> float:
        """Calculate temporal relevance with exponential decay"""
        if "stored_at" not in item:
            return 0.5  # Default for items without timestamp
        
        try:
            stored_time = datetime.fromisoformat(item["stored_at"].replace('Z', '+00:00'))
            age = datetime.now(timezone.utc) - stored_time
            age_days = age.total_seconds() / (24 * 3600)
            
            # Exponential decay
            return self.config["temporal_decay_rate"] ** age_days
        except:
            return 0.5
    
    def _calculate_project_alignment(self, item: Dict, project_context: Optional[str]) -> float:
        """Calculate project context alignment"""
        if not project_context:
            return 0.5  # Neutral if no context
        
        item_project = item.get("project_id", "")
        
        # Exact project match
        if project_context.lower() in item_project.lower():
            return 1.0
        
        # Check for project relationships (THRC work under econ-data project)
        context_data = item.get("context", {})
        if isinstance(context_data, dict):
            # Check if context mentions the project
            context_text = str(context_data).lower()
            if project_context.lower() in context_text:
                return 0.8
            
            # Check for related projects
            related_projects = context_data.get("related_projects", [])
            if project_context in related_projects:
                return 0.9
        
        return 0.3  # Low alignment if no clear connection
    
    def _calculate_connection_density(self, content: str) -> float:
        """Calculate how well-connected the content is"""
        if not content:
            return 0.0
        
        # Count various connection indicators
        link_count = len(re.findall(r'\[\[.*?\]\]', content))  # Wiki-style links
        ref_count = len(re.findall(r'\[.*?\]\(.*?\)', content))  # Markdown links
        tag_count = len(re.findall(r'#\w+', content))  # Tags
        mention_count = len(re.findall(r'@\w+', content))  # Mentions
        
        total_connections = link_count + ref_count + tag_count + mention_count
        
        # Normalize (assume 10+ connections = maximum density)
        return min(total_connections / 10.0, 1.0)
    
    def _calculate_semantic_similarity(self, item: Dict, query: str) -> float:
        """Calculate semantic similarity using word overlap"""
        content = item.get("content", "").lower()
        query_lower = query.lower()
        
        # Simple word overlap (could be enhanced with embeddings later)
        query_words = set(query_lower.split())
        content_words = set(content.split())
        
        if not query_words:
            return 0.0
        
        overlap = len(query_words.intersection(content_words))
        similarity = overlap / len(query_words)
        
        # Boost for exact phrase matches
        if query_lower in content:
            similarity = min(similarity + 0.3, 1.0)
        
        return similarity
    
    def _calculate_importance_score(self, item_data: Dict) -> float:
        """Calculate importance based on various factors"""
        importance = 0.5  # Base importance
        
        # Context factors
        context = item_data.get("context", {})
        if isinstance(context, dict):
            # Boss communication = higher importance
            if "boss" in str(context).lower():
                importance += 0.3
            
            # Urgent/deadline context
            if any(word in str(context).lower() for word in ["urgent", "deadline", "asap", "critical"]):
                importance += 0.2
        
        # Content length (longer content might be more important)
        content_length = len(item_data.get("content", ""))
        if content_length > 200:
            importance += 0.1
        
        # Tags indicating importance
        tags = item_data.get("tags", [])
        if "important" in tags or "critical" in tags:
            importance += 0.2
        
        return min(importance, 1.0)
    
    def _load_all_items(self) -> List[Dict]:
        """Load all stored items from working memory and data"""
        items = []
        
        # Load working memory items
        for item_file in self.working_memory_dir.glob("*.json"):
            try:
                with open(item_file) as f:
                    items.append(json.load(f))
            except Exception as e:
                print(f"Warning: Could not load {item_file}: {e}")
        
        return items
    
    def _update_working_memory_index(self, item: Dict):
        """Update the working memory index with capacity management"""
        index_file = self.working_memory_dir / "index.json"
        
        # Load existing index
        if index_file.exists():
            with open(index_file) as f:
                index = json.load(f)
        else:
            index = {"items": [], "last_updated": None, "capacity": self.config["max_working_memory_items"]}
        
        # Add new item
        index["items"].append({
            "id": item["id"],
            "stored_at": item["stored_at"],
            "importance_score": item["importance_score"],
            "project_id": item["project_id"]
        })
        
        # Sort by importance and recency
        index["items"].sort(key=lambda x: (x["importance_score"], x["stored_at"]), reverse=True)
        
        # Keep only top items within capacity
        if len(index["items"]) > index["capacity"]:
            # Archive excess items
            excess_items = index["items"][index["capacity"]:]
            index["items"] = index["items"][:index["capacity"]]
            
            print(f"📦 Archived {len(excess_items)} items due to capacity limit")
        
        # Update metadata
        index["last_updated"] = datetime.now(timezone.utc).isoformat()
        index["current_count"] = len(index["items"])
        
        # Save updated index
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def show_working_memory_status(self):
        """Display current working memory status"""
        index_file = self.working_memory_dir / "index.json"
        
        if not index_file.exists():
            print("📭 Working memory is empty")
            return
        
        with open(index_file) as f:
            index = json.load(f)
        
        print(f"\n🧠 Working Memory Status")
        print(f"   Items: {index['current_count']}/{index['capacity']}")
        print(f"   Last Updated: {index.get('last_updated', 'Unknown')}")
        
        if index["items"]:
            print(f"\n   📋 Current Items:")
            for i, item in enumerate(index["items"][:5], 1):
                print(f"   {i}. {item['id']} (importance: {item['importance_score']:.3f})")

if __name__ == "__main__":
    # Command-line interface for testing
    import sys
    brain = BrainPOCScoring()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "store":
            # Example: python poc_scoring.py store "My boss said we need to prioritize the THRC economic data analysis"
            content = sys.argv[2] if len(sys.argv) > 2 else "Test content"
            item_data = {
                "content": content,
                "project_id": "econ-data",
                "context": {"source": "boss", "work_type": "THRC"},
                "thinking_mode": "capture",
                "tags": ["boss-communication"]
            }
            brain.store_working_memory_item(item_data)
        
        elif command == "search":
            query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "test"
            results = brain.search_with_scoring(query, project_context="econ-data")
            
            if results:
                print(f"\n📊 Search Results:")
                for i, result in enumerate(results[:3], 1):
                    print(f"\n{i}. Score: {result['relevance_score']:.3f}")
                    print(f"   Content: {result['content'][:100]}...")
                    
                    # Show score breakdown
                    breakdown = result.get('score_breakdown', {})
                    print(f"   Score Breakdown:")
                    for factor, data in breakdown.items():
                        print(f"     {factor}: {data['factor']:.3f} × {data['weight']:.1f} = {data['contribution']:.3f}")
        
        elif command == "status":
            brain.show_working_memory_status()
        
        else:
            print("Usage: python poc_scoring.py [store|search|status] [content|query]")
    
    else:
        print("🧠 Brain POC Scoring System")
        print("Commands:")
        print("  store 'content'   - Store item in working memory")
        print("  search 'query'    - Search with relevance scoring")
        print("  status            - Show working memory status")