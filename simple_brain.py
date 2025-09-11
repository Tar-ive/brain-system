#!/usr/bin/env python3
"""
Simple Brain - First Principles Implementation
No race conditions, no complexity, just works.
"""

import os
import json
import time
import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import fcntl  # For file locking

class SimpleBrain:
    def __init__(self, brain_dir: str = "~/.brain"):
        self.brain_dir = Path(brain_dir).expanduser()
        self.brain_dir.mkdir(exist_ok=True)
        
        # Paths
        self.memory_log = self.brain_dir / "memory.log"
        self.sessions_dir = self.brain_dir / "sessions"
        self.sessions_dir.mkdir(exist_ok=True)
        
        # Get or create session ID
        self.session_id = os.environ.get('CLAUDE_SESSION_ID', self._generate_session_id())
        self.session_dir = self.sessions_dir / self.session_id
        self.session_dir.mkdir(exist_ok=True)
        
        # Initialize search index
        self._init_search_index()
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID from PID and timestamp"""
        unique = f"{os.getpid()}_{time.time()}"
        return hashlib.md5(unique.encode()).hexdigest()[:8]
    
    def _init_search_index(self):
        """Initialize SQLite for fast searching (read-heavy, write-light)"""
        self.index_db = self.brain_dir / "search.db"
        self.conn = sqlite3.connect(str(self.index_db), check_same_thread=False)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                timestamp TEXT,
                session_id TEXT,
                content TEXT,
                importance REAL,
                project TEXT
            )
        ''')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_content ON memories(content)')
        self.conn.commit()
    
    def store(self, content: str, importance: float = 0.5, project: str = None) -> bool:
        """
        Store memory - append-only, no conflicts possible
        """
        timestamp = datetime.now().isoformat()
        
        # 1. Append to shared log (atomic operation)
        log_entry = f"{timestamp}|{self.session_id}|{importance}|{project or 'default'}|{content}\n"
        
        with open(self.memory_log, 'a') as f:
            # Use file locking for the append operation
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(log_entry)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # 2. Update session-specific working memory (7 items max)
        session_memory = self.session_dir / "working_memory.json"
        
        working_memory = []
        if session_memory.exists():
            with open(session_memory) as f:
                working_memory = json.load(f)
        
        # Add new item
        working_memory.append({
            'timestamp': timestamp,
            'content': content,
            'importance': importance,
            'project': project
        })
        
        # Keep only 7 most important/recent items
        working_memory.sort(key=lambda x: (x['importance'], x['timestamp']), reverse=True)
        working_memory = working_memory[:7]
        
        with open(session_memory, 'w') as f:
            json.dump(working_memory, f, indent=2)
        
        # 3. Update search index (async would be better, but keeping it simple)
        self.conn.execute(
            'INSERT INTO memories VALUES (?, ?, ?, ?, ?)',
            (timestamp, self.session_id, content, importance, project)
        )
        self.conn.commit()
        
        return True
    
    def search(self, query: str, threshold: float = 0.75) -> List[Dict]:
        """
        Search memories - read-only, no conflicts
        """
        # Simple SQL search (could enhance with FTS5)
        results = self.conn.execute('''
            SELECT timestamp, session_id, content, importance, project
            FROM memories
            WHERE content LIKE ?
            ORDER BY importance DESC, timestamp DESC
            LIMIT 20
        ''', (f'%{query}%',)).fetchall()
        
        # Convert to dicts and calculate simple relevance score
        scored_results = []
        for row in results:
            # Simple scoring: word overlap + importance
            content = row[2].lower()
            query_words = set(query.lower().split())
            content_words = set(content.split())
            
            overlap = len(query_words & content_words) / len(query_words) if query_words else 0
            score = (overlap * 0.7) + (row[3] * 0.3)  # 70% content match, 30% importance
            
            if score >= threshold:
                scored_results.append({
                    'timestamp': row[0],
                    'session': row[1],
                    'content': row[2],
                    'importance': row[3],
                    'project': row[4],
                    'score': score
                })
        
        return scored_results
    
    def get_working_memory(self) -> List[Dict]:
        """Get current session's working memory"""
        session_memory = self.session_dir / "working_memory.json"
        if session_memory.exists():
            with open(session_memory) as f:
                return json.load(f)
        return []
    
    def get_context(self, include_other_sessions: bool = True) -> Dict:
        """Get current context with option to see other active sessions"""
        context = {
            'session_id': self.session_id,
            'working_memory': self.get_working_memory(),
            'memory_log_size': self.memory_log.stat().st_size if self.memory_log.exists() else 0
        }
        
        if include_other_sessions:
            # List other active sessions (modified in last hour)
            active_sessions = []
            cutoff = time.time() - 3600  # 1 hour
            
            for session_dir in self.sessions_dir.iterdir():
                if session_dir.is_dir():
                    wm_file = session_dir / "working_memory.json"
                    if wm_file.exists() and wm_file.stat().st_mtime > cutoff:
                        active_sessions.append(session_dir.name)
            
            context['active_sessions'] = active_sessions
            context['total_active'] = len(active_sessions)
        
        return context

def main():
    """CLI for testing"""
    import sys
    
    brain = SimpleBrain()
    
    if len(sys.argv) < 2:
        print(f"Simple Brain - Session: {brain.session_id}")
        print("Commands: store <content> | search <query> | context | working")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "store":
        content = " ".join(sys.argv[2:])
        if brain.store(content):
            print(f"✅ Stored: {content[:50]}...")
    
    elif command == "search":
        query = " ".join(sys.argv[2:])
        results = brain.search(query)
        print(f"Found {len(results)} results:")
        for r in results[:5]:
            print(f"  [{r['score']:.2f}] {r['content'][:70]}...")
    
    elif command == "context":
        context = brain.get_context()
        print(json.dumps(context, indent=2))
    
    elif command == "working":
        wm = brain.get_working_memory()
        print(f"Working Memory ({len(wm)}/7 items):")
        for item in wm:
            print(f"  [{item['importance']}] {item['content'][:60]}...")

if __name__ == "__main__":
    main()