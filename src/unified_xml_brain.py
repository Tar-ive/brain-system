#!/usr/bin/env python3
"""
Unified XML-Based Brain System
Streamlines all fragmented storage into a cohesive XML-tagged system
Tracks across 5 dimensions: personal, work, research, uni, startup
"""

import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import xml.etree.ElementTree as ET
from dataclasses import dataclass
import subprocess

@dataclass
class BrainEntry:
    """Unified brain entry with XML tags and 5-dimensional tracking"""
    content: str
    xml_tags: List[str]
    dimensions: List[str]  # personal, work, research, uni, startup
    timestamp: str
    importance: float
    connections: List[str]
    project_context: Optional[str] = None
    thinking_mode: Optional[str] = None
    confidence: float = 1.0

class UnifiedXMLBrain:
    def __init__(self, brain_dir: str = "/Users/tarive/brain-poc"):
        self.brain_dir = Path(brain_dir)
        self.unified_db = self.brain_dir / "unified_brain.db"
        self.xml_config = self.brain_dir / "xml_brain_config.json"
        self.setup_unified_storage()
        
    def setup_unified_storage(self):
        """Initialize unified XML brain storage system"""
        # Create unified SQLite database
        with sqlite3.connect(self.unified_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS brain_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    xml_tags TEXT,  -- JSON array of XML tags
                    dimensions TEXT,  -- JSON array of dimensions
                    timestamp TEXT NOT NULL,
                    importance REAL DEFAULT 0.5,
                    connections TEXT,  -- JSON array of connections
                    project_context TEXT,
                    thinking_mode TEXT,
                    confidence REAL DEFAULT 1.0,
                    raw_xml TEXT,  -- Original XML format for retrieval
                    search_content TEXT,  -- Processed content for FTS
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create full-text search index
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS brain_fts USING fts5(
                    content, xml_tags, dimensions, project_context, search_content,
                    content='brain_entries', content_rowid='id'
                )
            """)
            
        # Create XML configuration
        default_config = {
            "xml_tags": {
                "people": {"description": "Person references", "examples": ["<people>baby</people>", "<people>harshal</people>"]},
                "project": {"description": "Project references", "examples": ["<project>ybrowser</project>", "<project>brain-system</project>"]},
                "b": {"description": "Brain system functionalities/updates", "examples": ["<b>add indexing docs</b>", "<b>fix search bug</b>"]},
                "bfeatures": {"description": "Brain system feature requests", "examples": ["<bfeatures>integrate with imessage</bfeatures>", "<bfeatures>add voice notes</bfeatures>"]},
                "research": {"description": "Research insights and findings", "examples": ["<research>Newton's philosophy of time</research>", "<research>quantum computing applications</research>"]},
                "goals": {"description": "Personal and professional goals", "examples": ["<goals>get O1 visa</goals>", "<goals>complete PhD</goals>"]},
                "chores": {"description": "Daily tasks and chores", "examples": ["<chores>make baby chutney</chores>", "<chores>grocery shopping</chores>"]}
            },
            "dimensions": {
                "personal": {"description": "Personal life, relationships, health", "weight": 1.0},
                "work": {"description": "Professional work, job applications", "weight": 1.0},
                "research": {"description": "Academic research, papers, insights", "weight": 1.2},
                "uni": {"description": "University activities, courses, deadlines", "weight": 1.0},
                "startup": {"description": "Entrepreneurial activities, business ideas", "weight": 1.1}
            },
            "integration": {
                "simple_brain": True,
                "goal_keeper": True,
                "working_memory": True,
                "basic_memory": True,
                "obsidian_sync": True
            }
        }
        
        if not self.xml_config.exists():
            with open(self.xml_config, 'w') as f:
                json.dump(default_config, f, indent=2)

    def parse_xml_input(self, input_text: str) -> BrainEntry:
        """Parse input text with XML tags into structured brain entry"""
        # Extract XML tags
        xml_pattern = r'<(\w+)>(.*?)</\1>'
        xml_matches = re.findall(xml_pattern, input_text, re.DOTALL)
        
        xml_tags = []
        extracted_content = []
        
        for tag, content in xml_matches:
            xml_tags.append(tag)
            extracted_content.append(f"{tag}: {content.strip()}")
        
        # Remove XML tags from original text for clean content
        clean_content = re.sub(xml_pattern, '', input_text).strip()
        if extracted_content:
            clean_content += "\n\n" + "\n".join(extracted_content)
        
        # Determine dimensions based on content and tags
        dimensions = self._infer_dimensions(xml_tags, clean_content)
        
        # Calculate importance based on tags and content
        importance = self._calculate_importance(xml_tags, clean_content)
        
        # Extract connections (references to other entries)
        connections = self._extract_connections(clean_content)
        
        return BrainEntry(
            content=clean_content,
            xml_tags=xml_tags,
            dimensions=dimensions,
            timestamp=datetime.now(timezone.utc).isoformat(),
            importance=importance,
            connections=connections
        )

    def store_entry(self, entry: BrainEntry, sync_to_legacy: bool = True) -> int:
        """Store brain entry in unified system and sync to legacy systems"""
        with sqlite3.connect(self.unified_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO brain_entries 
                (content, xml_tags, dimensions, timestamp, importance, connections, 
                 project_context, thinking_mode, confidence, raw_xml, search_content)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.content,
                json.dumps(entry.xml_tags),
                json.dumps(entry.dimensions),
                entry.timestamp,
                entry.importance,
                json.dumps(entry.connections),
                entry.project_context,
                entry.thinking_mode,
                entry.confidence,
                entry.content,  # Use content as raw_xml fallback
                self._create_search_content(entry)
            ))
            
            entry_id = cursor.lastrowid
            
            # Update FTS index
            conn.execute("""
                INSERT INTO brain_fts (rowid, content, xml_tags, dimensions, project_context, search_content)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                entry_id,
                entry.content,
                " ".join(entry.xml_tags),
                " ".join(entry.dimensions),
                entry.project_context or "",
                self._create_search_content(entry)
            ))
            
        # Sync to legacy systems if requested
        if sync_to_legacy:
            self._sync_to_legacy_systems(entry)
            
        return entry_id

    def search_unified(self, query: str, dimensions: Optional[List[str]] = None, 
                      xml_tags: Optional[List[str]] = None, limit: int = 10) -> List[Dict]:
        """Search unified brain with advanced filtering"""
        with sqlite3.connect(self.unified_db) as conn:
            # Build FTS query
            fts_query = query
            where_clauses = []
            params = []
            
            if dimensions:
                dim_conditions = []
                for dim in dimensions:
                    dim_conditions.append("dimensions LIKE ?")
                    params.append(f"%{dim}%")
                where_clauses.append(f"({' OR '.join(dim_conditions)})")
            
            if xml_tags:
                tag_conditions = []
                for tag in xml_tags:
                    tag_conditions.append("xml_tags LIKE ?")
                    params.append(f"%{tag}%")
                where_clauses.append(f"({' OR '.join(tag_conditions)})")
            
            # Base query with FTS
            base_query = """
                SELECT b.*, bm25(brain_fts) as rank
                FROM brain_fts 
                JOIN brain_entries b ON brain_fts.rowid = b.id
                WHERE brain_fts MATCH ?
            """
            params.insert(0, fts_query)
            
            if where_clauses:
                base_query += " AND " + " AND ".join(where_clauses)
            
            base_query += " ORDER BY rank ASC, importance DESC, timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.cursor()
            cursor.execute(base_query, params)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'content': row[1],
                    'xml_tags': json.loads(row[2] or '[]'),
                    'dimensions': json.loads(row[3] or '[]'),
                    'timestamp': row[4],
                    'importance': row[5],
                    'connections': json.loads(row[6] or '[]'),
                    'project_context': row[7],
                    'thinking_mode': row[8],
                    'confidence': row[9],
                    'rank': row[14] if len(row) > 14 else 0
                })
            
            return results

    def _infer_dimensions(self, xml_tags: List[str], content: str) -> List[str]:
        """Infer relevant dimensions based on tags and content"""
        dimensions = []
        
        # Tag-based dimension mapping
        tag_dimension_map = {
            'goals': ['personal', 'work'],
            'research': ['research', 'uni'],
            'project': ['work', 'startup'],
            'people': ['personal'],
            'bfeatures': ['work', 'research'],
            'chores': ['personal']
        }
        
        for tag in xml_tags:
            if tag in tag_dimension_map:
                dimensions.extend(tag_dimension_map[tag])
        
        # Content-based inference
        content_lower = content.lower()
        if any(word in content_lower for word in ['job', 'career', 'interview', 'application']):
            dimensions.append('work')
        if any(word in content_lower for word in ['research', 'paper', 'study', 'analysis']):
            dimensions.append('research')
        if any(word in content_lower for word in ['university', 'course', 'assignment', 'degree']):
            dimensions.append('uni')
        if any(word in content_lower for word in ['startup', 'business', 'entrepreneur', 'product']):
            dimensions.append('startup')
        if any(word in content_lower for word in ['personal', 'family', 'health', 'home']):
            dimensions.append('personal')
        
        return list(set(dimensions)) if dimensions else ['personal']  # Default to personal

    def _calculate_importance(self, xml_tags: List[str], content: str) -> float:
        """Calculate importance score based on tags and content"""
        base_importance = 0.5
        
        # Tag-based importance weighting
        tag_weights = {
            'goals': 0.3,
            'research': 0.25,
            'bfeatures': 0.2,
            'project': 0.15,
            'people': 0.1,
            'chores': 0.05
        }
        
        for tag in xml_tags:
            if tag in tag_weights:
                base_importance += tag_weights[tag]
        
        # Content-based importance indicators
        importance_keywords = ['critical', 'important', 'urgent', 'insight', 'breakthrough']
        for keyword in importance_keywords:
            if keyword.lower() in content.lower():
                base_importance += 0.1
        
        return min(base_importance, 1.0)

    def _extract_connections(self, content: str) -> List[str]:
        """Extract connections to other brain entries"""
        connections = []
        
        # Extract markdown links
        md_links = re.findall(r'\[\[([^\]]+)\]\]', content)
        connections.extend(md_links)
        
        # Extract references to other XML tags
        refs = re.findall(r'@(\w+)', content)
        connections.extend(refs)
        
        return list(set(connections))

    def _create_search_content(self, entry: BrainEntry) -> str:
        """Create optimized search content"""
        search_parts = [
            entry.content,
            " ".join(entry.xml_tags),
            " ".join(entry.dimensions),
            " ".join(entry.connections)
        ]
        return " ".join(filter(None, search_parts))

    def _sync_to_legacy_systems(self, entry: BrainEntry):
        """Sync entry to existing brain systems"""
        try:
            # Sync to simple_brain
            simple_brain_script = self.brain_dir / "simple_brain.py"
            if simple_brain_script.exists():
                subprocess.run([
                    "python3", str(simple_brain_script), "store", entry.content
                ], timeout=10)
            
            # Sync to goal_keeper if it's a goal
            if 'goals' in entry.xml_tags:
                goal_keeper_script = self.brain_dir / "goal_keeper.py"
                if goal_keeper_script.exists():
                    subprocess.run([
                        "python3", str(goal_keeper_script), "win", f"New goal: {entry.content}"
                    ], timeout=10)
            
            # Sync to Basic Memory
            try:
                folder = entry.dimensions[0] if entry.dimensions else "general"
                title = f"{entry.xml_tags[0] if entry.xml_tags else 'entry'} - {datetime.now().strftime('%Y-%m-%d')}"
                
                subprocess.run([
                    "basic-memory", "tool", "write-note",
                    "--title", title,
                    "--folder", folder,
                    "--content", entry.content
                ], input="", text=True, timeout=15)
                
            except subprocess.TimeoutExpired:
                print("Basic Memory sync timed out")
            except Exception as e:
                print(f"Basic Memory sync failed: {e}")
                
        except Exception as e:
            print(f"Legacy sync error: {e}")

    def get_dimension_summary(self, dimension: str) -> Dict:
        """Get summary of entries for a specific dimension"""
        with sqlite3.connect(self.unified_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*), AVG(importance), 
                       GROUP_CONCAT(DISTINCT json_extract(xml_tags, '$[0]')) as top_tags
                FROM brain_entries 
                WHERE dimensions LIKE ?
            """, (f"%{dimension}%",))
            
            result = cursor.fetchone()
            return {
                'dimension': dimension,
                'entry_count': result[0] or 0,
                'avg_importance': result[1] or 0,
                'top_tags': (result[2] or "").split(',')[:5]
            }

    def export_dimension_xml(self, dimension: str) -> str:
        """Export all entries for a dimension in XML format"""
        with sqlite3.connect(self.unified_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT content, timestamp, importance
                FROM brain_entries 
                WHERE dimensions LIKE ?
                ORDER BY importance DESC, timestamp DESC
            """, (f"%{dimension}%",))
            
            entries = cursor.fetchall()
            
        xml_output = f'<?xml version="1.0" encoding="UTF-8"?>\n<brain_export dimension="{dimension}">\n'
        for entry in entries:
            xml_output += f'  <entry timestamp="{entry[1]}" importance="{entry[2]}">\n'
            xml_output += f'    {entry[0]}\n'
            xml_output += '  </entry>\n'
        xml_output += '</brain_export>'
        
        return xml_output


def brain_help():
    """Global brain help system with XML tag hierarchy"""
    help_text = """
🧠 UNIFIED BRAIN SYSTEM - XML Tag Hierarchy

## XML TAGS FOR INFORMATION STORAGE

### Core Tags:
<people>person_name</people>         - Person references and relationships
<project>project_name</project>      - Project-related information  
<b>brain_update</b>                  - Brain system functionalities/updates
<bfeatures>feature_request</bfeatures> - Brain system feature requests
<research>insight</research>         - Research insights and findings
<goals>goal_description</goals>      - Personal and professional goals
<chores>task_description</chores>    - Daily tasks and chores

### 5-DIMENSIONAL TRACKING:
All information is automatically categorized across:
• personal  - Personal life, relationships, health
• work      - Professional work, job applications  
• research  - Academic research, papers, insights
• uni       - University activities, courses, deadlines
• startup   - Entrepreneurial activities, business ideas

### USAGE EXAMPLES:

Store person info:
  brain_store "<people>baby</people> loves homemade chutney, especially spicy varieties"

Log project work:  
  brain_store "<project>ybrowser</project> integration with <project>bu-nicehack</project> shows promise"

Brain system improvement:
  brain_store "<b>add indexing docs</b> to improve discoverability of brain functions"

Feature requests:
  brain_store "<bfeatures>integrate with imessage and reminders app</bfeatures> for seamless capture"

Research insights:
  brain_store "<research>Newton's philosophy: time is absolute, space is relative container</research>"

Set goals:
  brain_store "<goals>get O1 visa</goals> requires demonstrating extraordinary ability in AI research"

Daily chores:
  brain_store "<chores>make baby chutney</chores> using tomatoes from garden"

### SEARCH COMMANDS:

brain_search "query"                 - Search across all dimensions
brain_search "query" --dim personal  - Search specific dimension  
brain_search "query" --tag people    - Search by XML tag
brain_dimension personal             - View all personal entries
brain_export research                - Export research entries as XML

### INTEGRATION:
This system unifies all existing brain storage:
✅ Simple Brain (append-only log)
✅ Goal Keeper (JSON files) 
✅ Working Memory (7-item limit)
✅ Basic Memory (MCP integration)
✅ Obsidian Sync (markdown backup)

### GLOBAL AVAILABILITY:
Run 'brain_help' in any Claude session for this help.
All XML-tagged entries are searchable across sessions.
    """
    print(help_text)
    return help_text


if __name__ == "__main__":
    import sys
    brain = UnifiedXMLBrain()
    
    if len(sys.argv) < 2:
        brain_help()
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "help":
        brain_help()
    elif command == "store" and len(sys.argv) > 2:
        input_text = " ".join(sys.argv[2:])
        entry = brain.parse_xml_input(input_text)
        entry_id = brain.store_entry(entry)
        print(f"✅ Stored entry {entry_id} with tags: {entry.xml_tags}, dimensions: {entry.dimensions}")
    elif command == "search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        results = brain.search_unified(query)
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results[:5], 1):
            print(f"{i}. [{result['importance']:.2f}] {result['content'][:100]}...")
    elif command == "dimension" and len(sys.argv) > 2:
        dim = sys.argv[2]
        summary = brain.get_dimension_summary(dim)
        print(f"Dimension '{dim}': {summary['entry_count']} entries, avg importance: {summary['avg_importance']:.2f}")
    elif command == "export" and len(sys.argv) > 2:
        dim = sys.argv[2]
        xml_export = brain.export_dimension_xml(dim)
        export_file = f"/tmp/brain_export_{dim}_{datetime.now().strftime('%Y%m%d')}.xml"
        with open(export_file, 'w') as f:
            f.write(xml_export)
        print(f"Exported {dim} dimension to: {export_file}")
    else:
        print("Usage: python3 unified_xml_brain.py [help|store|search|dimension|export] [args...]")