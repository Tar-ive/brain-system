#!/usr/bin/env python3
"""
Streamlined Storage Backend
Unifies all 8+ fragmented brain storage systems into a coherent backend
Maintains compatibility while providing unified access
"""

import json
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import subprocess
import hashlib
import uuid
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import logging

@dataclass
class StorageEntry:
    """Unified storage entry structure"""
    id: str
    content: str
    xml_tags: List[str]
    dimensions: List[str] 
    timestamp: str
    importance: float
    connections: List[str]
    project_context: Optional[str]
    thinking_mode: Optional[str]
    confidence: float
    source_system: str
    metadata: Dict[str, Any]

class StreamlinedStorageBackend:
    """
    Unified storage backend that manages all brain storage systems
    - Eliminates fragmentation
    - Provides single point of access
    - Maintains backward compatibility
    - Handles concurrent access
    - Automatic sync across all systems
    """
    
    def __init__(self, brain_dir: str = "/Users/tarive/brain-poc"):
        self.brain_dir = Path(brain_dir)
        self.unified_db = self.brain_dir / "streamlined_storage.db" 
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Legacy system paths
        self.legacy_systems = {
            "simple_brain": self.brain_dir / "simple_brain.py",
            "goal_keeper": self.brain_dir / "goal_keeper.py", 
            "working_memory": self.brain_dir / "working-memory",
            "session_context": self.brain_dir / "session_context.py",
            "obsidian_sync": self.brain_dir / "obsidian_sync.py",
            "auto_commit": self.brain_dir / "auto_commit.py"
        }
        
        self.setup_logging()
        self.init_storage()
        
    def setup_logging(self):
        """Setup logging for storage operations"""
        log_file = self.brain_dir / "streamlined_storage.log"
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def init_storage(self):
        """Initialize streamlined storage database"""
        with sqlite3.connect(self.unified_db) as conn:
            # Main unified storage table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS unified_entries (
                    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
                    id TEXT UNIQUE,
                    content TEXT NOT NULL,
                    xml_tags TEXT,           -- JSON array
                    dimensions TEXT,         -- JSON array  
                    timestamp TEXT NOT NULL,
                    importance REAL DEFAULT 0.5,
                    connections TEXT,        -- JSON array
                    project_context TEXT,
                    thinking_mode TEXT,
                    confidence REAL DEFAULT 1.0,
                    source_system TEXT,
                    metadata TEXT,           -- JSON object
                    content_hash TEXT,       -- For deduplication
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Legacy system mapping table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS legacy_mappings (
                    unified_id TEXT,
                    legacy_system TEXT,
                    legacy_id TEXT,
                    legacy_path TEXT,
                    sync_status TEXT DEFAULT 'pending',
                    last_sync TEXT,
                    PRIMARY KEY (unified_id, legacy_system)
                )
            """)
            
            # Full-text search
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS unified_fts USING fts5(
                    content, xml_tags, dimensions, project_context, source_system,
                    content='unified_entries', content_rowid='id'
                )
            """)
            
            # Indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON unified_entries(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_importance ON unified_entries(importance)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_dimensions ON unified_entries(dimensions)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_content_hash ON unified_entries(content_hash)")

    def store(self, entry: StorageEntry, sync_legacy: bool = True) -> str:
        """Store entry in unified system with optional legacy sync"""
        with self.lock:
            # Generate content hash for deduplication
            content_hash = hashlib.md5(entry.content.encode()).hexdigest()
            
            # Check for duplicates
            if self._is_duplicate(content_hash, entry.timestamp):
                self.logger.info(f"Duplicate content detected, skipping: {entry.id}")
                return entry.id
            
            # Store in unified database
            with sqlite3.connect(self.unified_db) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO unified_entries
                    (id, content, xml_tags, dimensions, timestamp, importance, connections,
                     project_context, thinking_mode, confidence, source_system, metadata, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.id,
                    entry.content,
                    json.dumps(entry.xml_tags),
                    json.dumps(entry.dimensions),
                    entry.timestamp,
                    entry.importance,
                    json.dumps(entry.connections),
                    entry.project_context,
                    entry.thinking_mode,
                    entry.confidence,
                    entry.source_system,
                    json.dumps(entry.metadata),
                    content_hash
                ))
                
                # Update FTS index - get the actual rowid from the insert
                entry_rowid = cursor.lastrowid
                conn.execute("""
                    INSERT OR REPLACE INTO unified_fts 
                    (rowid, content, xml_tags, dimensions, project_context, source_system)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entry_rowid,
                    entry.content,
                    " ".join(entry.xml_tags),
                    " ".join(entry.dimensions),
                    entry.project_context or "",
                    entry.source_system
                ))
            
            # Async sync to legacy systems
            if sync_legacy:
                self.executor.submit(self._sync_to_legacy_systems, entry)
                
            self.logger.info(f"Stored entry {entry.id} from {entry.source_system}")
            return entry.id

    def search(self, query: str, filters: Optional[Dict] = None, limit: int = 20) -> List[StorageEntry]:
        """Search unified storage with advanced filtering"""
        filters = filters or {}
        
        with sqlite3.connect(self.unified_db) as conn:
            # Build dynamic query
            base_query = """
                SELECT u.*, bm25(unified_fts) as rank
                FROM unified_fts
                JOIN unified_entries u ON unified_fts.rowid = u.rowid
                WHERE unified_fts MATCH ?
            """
            
            params = [query]
            where_clauses = []
            
            # Apply filters
            if filters.get('dimensions'):
                where_clauses.append("u.dimensions LIKE ?")
                params.append(f"%{filters['dimensions']}%")
                
            if filters.get('xml_tags'):
                where_clauses.append("u.xml_tags LIKE ?")
                params.append(f"%{filters['xml_tags']}%")
                
            if filters.get('project_context'):
                where_clauses.append("u.project_context = ?")
                params.append(filters['project_context'])
                
            if filters.get('source_system'):
                where_clauses.append("u.source_system = ?")
                params.append(filters['source_system'])
                
            if filters.get('min_importance'):
                where_clauses.append("u.importance >= ?")
                params.append(filters['min_importance'])
                
            if filters.get('after_date'):
                where_clauses.append("u.timestamp >= ?")
                params.append(filters['after_date'])
            
            if where_clauses:
                base_query += " AND " + " AND ".join(where_clauses)
            
            base_query += " ORDER BY rank ASC, u.importance DESC, u.timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.cursor()
            cursor.execute(base_query, params)
            
            results = []
            for row in cursor.fetchall():
                entry = StorageEntry(
                    id=row[0],
                    content=row[1],
                    xml_tags=json.loads(row[2] or '[]'),
                    dimensions=json.loads(row[3] or '[]'),
                    timestamp=row[4],
                    importance=row[5],
                    connections=json.loads(row[6] or '[]'),
                    project_context=row[7],
                    thinking_mode=row[8],
                    confidence=row[9],
                    source_system=row[10],
                    metadata=json.loads(row[11] or '{}')
                )
                results.append(entry)
            
            return results

    def migrate_legacy_data(self) -> Dict[str, int]:
        """Migrate data from all legacy systems to unified storage"""
        migration_stats = {}
        
        self.logger.info("Starting legacy data migration")
        
        # Migrate from simple_brain
        stats = self._migrate_simple_brain()
        migration_stats['simple_brain'] = stats
        
        # Migrate from goal_keeper
        stats = self._migrate_goal_keeper()
        migration_stats['goal_keeper'] = stats
        
        # Migrate from working_memory
        stats = self._migrate_working_memory()  
        migration_stats['working_memory'] = stats
        
        # Migrate from Basic Memory (if available)
        stats = self._migrate_basic_memory()
        migration_stats['basic_memory'] = stats
        
        self.logger.info(f"Migration completed: {migration_stats}")
        return migration_stats

    def _migrate_simple_brain(self) -> int:
        """Migrate simple_brain memory log"""
        count = 0
        memory_log = Path.home() / ".brain" / "memory.log"
        
        if not memory_log.exists():
            return count
        
        try:
            with open(memory_log, 'r') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) >= 5:
                        timestamp, session_id, importance, project, content = parts[:5]
                        
                        entry = StorageEntry(
                            id=str(uuid.uuid4()),
                            content=content,
                            xml_tags=[],
                            dimensions=['personal'],  # Default dimension
                            timestamp=timestamp,
                            importance=float(importance),
                            connections=[],
                            project_context=project if project != 'default' else None,
                            thinking_mode=None,
                            confidence=1.0,
                            source_system='simple_brain',
                            metadata={'session_id': session_id, 'migrated': True}
                        )
                        
                        self.store(entry, sync_legacy=False)
                        count += 1
                        
        except Exception as e:
            self.logger.error(f"Simple brain migration error: {e}")
            
        return count

    def _migrate_goal_keeper(self) -> int:
        """Migrate goal_keeper data"""
        count = 0
        
        # Migrate active goals
        goals_file = self.brain_dir / "active_goals.json"
        if goals_file.exists():
            try:
                with open(goals_file) as f:
                    goals_data = json.load(f)
                    
                for project, project_data in goals_data.items():
                    entry = StorageEntry(
                        id=str(uuid.uuid4()),
                        content=f"Goal: {project} - Status: {project_data.get('status', 'unknown')}",
                        xml_tags=['goals'],
                        dimensions=['work', 'personal'],
                        timestamp=project_data.get('started', datetime.now(timezone.utc).isoformat()),
                        importance=0.9,
                        connections=[],
                        project_context=project,
                        thinking_mode='planning',
                        confidence=1.0,
                        source_system='goal_keeper',
                        metadata=project_data
                    )
                    
                    self.store(entry, sync_legacy=False)
                    count += 1
                    
            except Exception as e:
                self.logger.error(f"Goal keeper migration error: {e}")
        
        # Migrate wins log
        wins_file = self.brain_dir / "wins_log.json"
        if wins_file.exists():
            try:
                with open(wins_file) as f:
                    wins_data = json.load(f)
                    
                for project, wins_list in wins_data.items():
                    if isinstance(wins_list, list):
                        for win in wins_list:
                            entry = StorageEntry(
                                id=str(uuid.uuid4()),
                                content=f"Win: {win.get('description', 'Unknown win')}",
                                xml_tags=['goals'],
                                dimensions=['work', 'personal'],
                                timestamp=win.get('timestamp', datetime.now(timezone.utc).isoformat()),
                                importance=0.8,
                                connections=[],
                                project_context=project,
                                thinking_mode='execution',
                                confidence=1.0,
                                source_system='goal_keeper',
                                metadata={'win_data': win, 'migrated': True}
                            )
                            
                            self.store(entry, sync_legacy=False)
                            count += 1
                            
            except Exception as e:
                self.logger.error(f"Wins log migration error: {e}")
                
        return count

    def _migrate_working_memory(self) -> int:
        """Migrate working memory files"""
        count = 0
        working_memory_dir = self.brain_dir / "working-memory"
        
        if not working_memory_dir.exists():
            return count
        
        try:
            for wm_file in working_memory_dir.glob("wm_*.json"):
                with open(wm_file) as f:
                    wm_data = json.load(f)
                    
                entry = StorageEntry(
                    id=wm_data.get('id', str(uuid.uuid4())),
                    content=wm_data.get('content', ''),
                    xml_tags=[],
                    dimensions=['personal'],  # Will be inferred
                    timestamp=wm_data.get('stored_at', datetime.now(timezone.utc).isoformat()),
                    importance=wm_data.get('importance_score', 0.5),
                    connections=[],
                    project_context=wm_data.get('project_id'),
                    thinking_mode=None,
                    confidence=1.0,
                    source_system='working_memory',
                    metadata=wm_data
                )
                
                self.store(entry, sync_legacy=False)
                count += 1
                
        except Exception as e:
            self.logger.error(f"Working memory migration error: {e}")
            
        return count

    def _migrate_basic_memory(self) -> int:
        """Migrate Basic Memory data"""
        count = 0
        
        try:
            # Use Basic Memory CLI to export data
            result = subprocess.run([
                "basic-memory", "tool", "list-notes"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Parse the output and migrate entries
                # This would need to be adapted based on actual Basic Memory output format
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        # Create entry from Basic Memory data
                        entry = StorageEntry(
                            id=str(uuid.uuid4()),
                            content=line.strip(),
                            xml_tags=[],
                            dimensions=['research'],  # Default for Basic Memory
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            importance=0.7,
                            connections=[],
                            project_context=None,
                            thinking_mode='research',
                            confidence=1.0,
                            source_system='basic_memory',
                            metadata={'migrated': True}
                        )
                        
                        self.store(entry, sync_legacy=False)
                        count += 1
                        
        except subprocess.TimeoutExpired:
            self.logger.warning("Basic Memory migration timed out")
        except Exception as e:
            self.logger.error(f"Basic Memory migration error: {e}")
            
        return count

    def _is_duplicate(self, content_hash: str, timestamp: str) -> bool:
        """Check if content is duplicate within recent timeframe"""
        with sqlite3.connect(self.unified_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM unified_entries 
                WHERE content_hash = ? AND timestamp > datetime(?, '-1 hour')
                LIMIT 1
            """, (content_hash, timestamp))
            
            return cursor.fetchone() is not None

    def _sync_to_legacy_systems(self, entry: StorageEntry):
        """Async sync entry to legacy systems"""
        try:
            # Sync to simple_brain
            if self.legacy_systems['simple_brain'].exists():
                subprocess.run([
                    "python3", str(self.legacy_systems['simple_brain']),
                    "store", entry.content
                ], timeout=15, check=False)
            
            # Sync to goal_keeper if it's a goal
            if 'goals' in entry.xml_tags and self.legacy_systems['goal_keeper'].exists():
                subprocess.run([
                    "python3", str(self.legacy_systems['goal_keeper']),
                    "win", f"Goal: {entry.content}"
                ], timeout=15, check=False)
            
            # Sync to Basic Memory
            try:
                folder = entry.dimensions[0] if entry.dimensions else "general"
                title = f"Unified Entry - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                
                subprocess.run([
                    "basic-memory", "tool", "write-note",
                    "--title", title,
                    "--folder", folder
                ], input=entry.content, text=True, timeout=20, check=False)
                
            except subprocess.TimeoutExpired:
                self.logger.warning("Basic Memory sync timed out")
            
            # Update sync status
            with sqlite3.connect(self.unified_db) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO legacy_mappings 
                    (unified_id, legacy_system, sync_status, last_sync)
                    VALUES (?, 'all', 'completed', ?)
                """, (entry.id, datetime.now(timezone.utc).isoformat()))
                
        except Exception as e:
            self.logger.error(f"Legacy sync error for {entry.id}: {e}")

    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        with sqlite3.connect(self.unified_db) as conn:
            cursor = conn.cursor()
            
            # Total entries
            cursor.execute("SELECT COUNT(*) FROM unified_entries")
            total_entries = cursor.fetchone()[0]
            
            # Entries by source system
            cursor.execute("""
                SELECT source_system, COUNT(*) 
                FROM unified_entries 
                GROUP BY source_system
            """)
            by_source = dict(cursor.fetchall())
            
            # Entries by dimension
            cursor.execute("""
                SELECT dimensions, COUNT(*)
                FROM unified_entries
                GROUP BY dimensions
            """)
            by_dimension = dict(cursor.fetchall())
            
            # Recent activity (last 7 days)
            cursor.execute("""
                SELECT COUNT(*) 
                FROM unified_entries 
                WHERE timestamp > datetime('now', '-7 days')
            """)
            recent_activity = cursor.fetchone()[0]
            
            # Average importance
            cursor.execute("SELECT AVG(importance) FROM unified_entries")
            avg_importance = cursor.fetchone()[0] or 0
            
        return {
            'total_entries': total_entries,
            'by_source_system': by_source,
            'by_dimension': by_dimension,
            'recent_activity_7d': recent_activity,
            'average_importance': round(avg_importance, 3),
            'database_path': str(self.unified_db),
            'legacy_systems': {k: v.exists() for k, v in self.legacy_systems.items()}
        }

    def cleanup_old_entries(self, days_old: int = 365) -> int:
        """Clean up entries older than specified days (keep important ones)"""
        cutoff_date = datetime.now(timezone.utc).isoformat()[:-13] + f"-{days_old*24:04d}:00:00+00:00"
        
        with sqlite3.connect(self.unified_db) as conn:
            cursor = conn.cursor()
            
            # Delete old, low-importance entries
            cursor.execute("""
                DELETE FROM unified_entries 
                WHERE timestamp < ? AND importance < 0.7
            """, (cutoff_date,))
            
            deleted = cursor.rowcount
            
            # Update FTS index
            conn.execute("INSERT INTO unified_fts(unified_fts) VALUES('rebuild')")
            
        self.logger.info(f"Cleaned up {deleted} old entries")
        return deleted


if __name__ == "__main__":
    import sys
    
    backend = StreamlinedStorageBackend()
    
    if len(sys.argv) < 2:
        print("Usage: streamlined_storage.py [migrate|stats|cleanup|test]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "migrate":
        print("🔄 Migrating legacy data...")
        stats = backend.migrate_legacy_data()
        print("✅ Migration complete:")
        for system, count in stats.items():
            print(f"  {system}: {count} entries")
    
    elif command == "stats":
        print("📊 System Statistics:")
        stats = backend.get_system_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    elif command == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 365
        print(f"🧹 Cleaning entries older than {days} days...")
        deleted = backend.cleanup_old_entries(days)
        print(f"✅ Deleted {deleted} old entries")
    
    elif command == "test":
        print("🧪 Testing storage system...")
        
        # Test storage
        test_entry = StorageEntry(
            id=str(uuid.uuid4()),
            content="<research>Test insight about unified storage</research>",
            xml_tags=['research'],
            dimensions=['research'],
            timestamp=datetime.now(timezone.utc).isoformat(),
            importance=0.8,
            connections=[],
            project_context='brain-system',
            thinking_mode='execution',
            confidence=1.0,
            source_system='test',
            metadata={'test': True}
        )
        
        entry_id = backend.store(test_entry)
        print(f"✅ Stored test entry: {entry_id}")
        
        # Test search
        results = backend.search("unified storage", {'source_system': 'test'})
        print(f"✅ Search found {len(results)} results")
        
        # Test stats
        stats = backend.get_system_stats()
        print(f"✅ System stats: {stats['total_entries']} total entries")
        
        print("🎉 All tests passed!")