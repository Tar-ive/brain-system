#!/usr/bin/env python3
"""
Smart Context Loader - Implements brain.md's context management strategy
Prevents cognitive overload by limiting context to working memory capacity
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

class SmartContextLoader:
    """
    Implements brain.md's Three-Layer Cognitive Architecture
    with proper working memory limits and temporal decay
    """
    
    def __init__(self):
        self.WORKING_MEMORY_LIMIT = 7  # From brain.md line 1032
        self.TEMPORAL_DECAY_RATE = 0.95  # From brain.md
        self.context_file = Path("/Users/tarive/brain-poc/current_session.json")
        self.claude_md = Path("/Users/tarive/brain-poc/CLAUDE.md")
        
    def calculate_priority(self, item: Dict) -> float:
        """
        From brain.md lines 1037-1048: Priority scoring for working memory
        """
        # Temporal recency (40% weight)
        if 'timestamp' in item:
            age_days = (datetime.now() - datetime.fromisoformat(item['timestamp'])).days
            temporal_score = self.TEMPORAL_DECAY_RATE ** age_days
        else:
            temporal_score = 0.5
            
        # Importance (30% weight)
        importance = item.get('importance', 0.5)
        
        # Connection density (20% weight)
        connections = len(item.get('related_items', []))
        connection_score = min(connections / 10, 1.0)
        
        # Access frequency (10% weight)
        access_count = item.get('access_count', 1)
        access_score = min(access_count / 10, 1.0)
        
        return (
            0.4 * temporal_score +
            0.3 * importance +
            0.2 * connection_score +
            0.1 * access_score
        )
    
    def load_smart_context(self) -> Dict:
        """
        Load only the most relevant context items
        Following brain.md's memory access patterns (lines 85-89)
        """
        
        if not self.context_file.exists():
            return self.get_minimal_context()
        
        with open(self.context_file) as f:
            full_context = json.load(f)
        
        # Apply Three-Layer Architecture filtering
        filtered_context = {
            # Layer 3: Metacognitive (current mode and project)
            "current_project": full_context.get("project", "brain-poc"),
            "thinking_mode": full_context.get("thinking_mode", "execution"),
            
            # Layer 2: Consolidation (only recent patterns)
            "recent_patterns": self.filter_by_temporal_relevance(
                full_context.get("patterns", [])
            ),
            
            # Layer 1: Representation (only active working memory)
            "working_memory": self.get_working_memory_items(full_context),
            
            # Essential commands only
            "essential_commands": {
                "search": "~/bin/bf 'query'",
                "status": "brain-status",
                "save": "brain-save"
            },
            
            # Only today's pending tasks
            "todays_tasks": self.get_todays_tasks(full_context),
            
            # Active entity mappings (compressed)
            "active_entities": self.get_active_entities(full_context)
        }
        
        return filtered_context
    
    def get_working_memory_items(self, context: Dict) -> List[Dict]:
        """
        Get only the top 7 working memory items
        Based on brain.md's working memory management (lines 1029-1054)
        """
        all_items = []
        
        # Collect all potential items
        for task in context.get('pending_tasks', []):
            all_items.append({
                'content': task,
                'type': 'task',
                'importance': 0.8 if 'urgent' in task.lower() else 0.5,
                'timestamp': context.get('last_session', datetime.now().isoformat())
            })
        
        # Score and sort
        scored_items = [(self.calculate_priority(item), item) for item in all_items]
        scored_items.sort(key=lambda x: x[0], reverse=True)
        
        # Return only top 7
        return [item for score, item in scored_items[:self.WORKING_MEMORY_LIMIT]]
    
    def filter_by_temporal_relevance(self, items: List) -> List:
        """
        Apply temporal decay to filter out old items
        """
        recent_items = []
        cutoff_date = datetime.now() - timedelta(days=7)  # 7-day window from brain.md
        
        for item in items:
            if isinstance(item, dict) and 'timestamp' in item:
                item_date = datetime.fromisoformat(item['timestamp'])
                if item_date > cutoff_date:
                    recent_items.append(item)
            elif isinstance(item, str):
                # Keep string items if they're short
                if len(item) < 100:
                    recent_items.append(item)
        
        return recent_items[:5]  # Limit to 5 patterns
    
    def get_todays_tasks(self, context: Dict) -> List[str]:
        """Get only today's urgent tasks"""
        tasks = []
        for task in context.get('pending_tasks', []):
            if any(word in task.lower() for word in ['today', 'urgent', 'asap']):
                tasks.append(task)
        return tasks[:3]  # Max 3 urgent tasks
    
    def get_active_entities(self, context: Dict) -> Dict:
        """Get only currently relevant entities"""
        entities = context.get('entities', {})
        
        # Only include entities mentioned in today's tasks
        active = {}
        todays_content = str(context.get('pending_tasks', []))
        
        for entity, aliases in entities.items():
            if entity.lower() in todays_content.lower():
                # Compress aliases
                if isinstance(aliases, list) and len(aliases) > 3:
                    active[entity] = aliases[:3] + ["..."]
                else:
                    active[entity] = aliases
        
        return active
    
    def get_minimal_context(self) -> Dict:
        """Minimal context when no session exists"""
        return {
            "message": "No previous session. Start with brain-load to check for context.",
            "essential_commands": {
                "load": "python3 /Users/tarive/brain-poc/session_context.py load",
                "search": "~/bin/bf 'query'",
                "status": "python3 /Users/tarive/brain-poc/scripts/poc_scoring.py status"
            }
        }
    
    def generate_smart_claude_md(self):
        """
        Generate a context-aware CLAUDE.md that doesn't overload
        """
        context = self.load_smart_context()
        
        content = f"""# Brain POC - Smart Context (Limited)

## Active Context Only

### Current Focus
- **Project**: {context.get('current_project', 'brain-poc')}
- **Mode**: {context.get('thinking_mode', 'execution')}

### Working Memory ({len(context.get('working_memory', []))}/{self.WORKING_MEMORY_LIMIT} items)
{chr(10).join([f"- {item['content'][:50]}..." for item in context.get('working_memory', [])])}

### Today's Tasks
{chr(10).join([f"- {task}" for task in context.get('todays_tasks', [])])}

### Essential Commands
```bash
{chr(10).join([f"{cmd}: {command}" for cmd, command in context.get('essential_commands', {}).items()])}
```

### Active Entities
{chr(10).join([f"- {entity}: {aliases if isinstance(aliases, str) else ', '.join(aliases[:2])}" 
              for entity, aliases in context.get('active_entities', {}).items()])}

---
**Note**: This is a smart-filtered context. For full context, run: `brain-load`
**Working Memory Limit**: 7 items (cognitive science limit)
**Temporal Window**: Last 7 days only
"""
        
        # Save smart context
        with open(self.claude_md, 'w') as f:
            f.write(content)
        
        print(f"✅ Smart context saved (limited to {self.WORKING_MEMORY_LIMIT} items)")
        print(f"📊 Cognitive load: {len(context.get('working_memory', []))}/7")
        return context

if __name__ == "__main__":
    loader = SmartContextLoader()
    context = loader.generate_smart_claude_md()
    
    print("\n🧠 Smart Context Loaded:")
    print(f"   Working Memory: {len(context.get('working_memory', []))} items")
    print(f"   Today's Tasks: {len(context.get('todays_tasks', []))} urgent")
    print(f"   Active Entities: {len(context.get('active_entities', {}))} relevant")
    print("\nThis follows brain.md's cognitive load management principles!")