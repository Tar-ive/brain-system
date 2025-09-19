#!/usr/bin/env python3
"""
Unified Brain Bridge - Connects POC working memory with Basic Memory
Provides continuous memory chain across Claude sessions
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class UnifiedBrain:
    def __init__(self):
        self.poc_dir = Path("/Users/tarive/brain-poc")
        self.brain_dir = Path("/Users/tarive/brain")
        self.working_memory_dir = self.poc_dir / "working-memory"
        
    def store_memory(self, content: str, project: Optional[str] = None, 
                    importance: float = 0.5, context: Optional[Dict] = None) -> bool:
        """
        Store memory in both working memory and Basic Memory for persistence
        """
        try:
            # Prepare metadata
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # Store in POC working memory with importance scoring
            poc_data = {
                "content": content,
                "importance": importance,
                "timestamp": timestamp,
                "context": context or {}
            }
            
            # Check if boss communication for auto-importance
            if any(word in content.lower() for word in ['boss', 'urgent', 'priority']):
                poc_data["importance"] = 0.9
            
            # Store via POC scoring system
            poc_result = subprocess.run([
                'python3', f'{self.poc_dir}/scripts/poc_scoring.py',
                'store', json.dumps(poc_data)
            ], capture_output=True, text=True)
            
            # Store in Basic Memory for long-term persistence
            bm_cmd = [
                'basic-memory', 'tool', 'write-note',
                '--title', f'WM: {content[:50]}{"..." if len(content) > 50 else ""}',
                '--folder', 'working-memory',
                '--tags', f'importance-{int(importance*10)}',
                '--tags', 'claude-session',
                '--tags', datetime.now().strftime('%Y-%m-%d')
            ]
            
            if project:
                bm_cmd.extend(['--project', project])
            
            # Add context as content body
            full_content = f"{content}\n\n---\nContext: {json.dumps(context, indent=2)}" if context else content
            
            bm_result = subprocess.run(
                bm_cmd, 
                input=full_content, 
                capture_output=True, 
                text=True
            )
            
            return poc_result.returncode == 0 and bm_result.returncode == 0
            
        except Exception as e:
            print(f"Error storing memory: {e}")
            return False
    
    def search_all(self, query: str, confidence_threshold: float = 0.75) -> List[Dict]:
        """
        Search across all memory systems with unified scoring
        """
        results = []
        
        try:
            # Search POC working memory
            poc_result = subprocess.run([
                f'{self.poc_dir}/bf', query
            ], capture_output=True, text=True)
            
            if poc_result.returncode == 0 and poc_result.stdout:
                for line in poc_result.stdout.strip().split('\n'):
                    if 'Score:' in line:
                        results.append({
                            'source': 'working_memory',
                            'content': line,
                            'score': self._extract_score(line)
                        })
            
            # Search Basic Memory
            bm_result = subprocess.run([
                'basic-memory', 'tool', 'search-notes', query
            ], capture_output=True, text=True)
            
            if bm_result.returncode == 0 and bm_result.stdout:
                # Parse Basic Memory results (adjust based on actual format)
                for line in bm_result.stdout.strip().split('\n'):
                    if line and not line.startswith('#'):
                        results.append({
                            'source': 'basic_memory',
                            'content': line,
                            'score': 0.8  # Default score for Basic Memory results
                        })
            
            # Filter by confidence threshold
            results = [r for r in results if r['score'] >= confidence_threshold]
            
            # Sort by score
            results.sort(key=lambda x: x['score'], reverse=True)
            
        except Exception as e:
            print(f"Search error: {e}")
        
        return results
    
    def get_session_context(self, hours_back: int = 24) -> Dict:
        """
        Get recent session context for restoration
        """
        context = {
            'working_memory': [],
            'recent_insights': [],
            'active_projects': []
        }
        
        try:
            # Get working memory status
            status_result = subprocess.run([
                'python3', f'{self.poc_dir}/scripts/poc_scoring.py', 'status'
            ], capture_output=True, text=True)
            
            if status_result.stdout:
                context['working_memory_status'] = status_result.stdout
            
            # Search recent Claude activity in Basic Memory
            recent_result = subprocess.run([
                'basic-memory', 'tool', 'search-notes', 
                f'claude-session after:{hours_back}h'
            ], capture_output=True, text=True)
            
            if recent_result.stdout:
                context['recent_activity'] = recent_result.stdout
            
            # Get current Basic Memory project
            project_result = subprocess.run([
                'basic-memory', 'project', 'current'
            ], capture_output=True, text=True)
            
            if project_result.stdout:
                context['current_project'] = project_result.stdout.strip()
            
        except Exception as e:
            print(f"Error getting session context: {e}")
        
        return context
    
    def sync_to_obsidian(self) -> bool:
        """
        Sync working memory to Obsidian vault
        """
        try:
            # Get current working memory items
            wm_files = list(self.working_memory_dir.glob("wm_*.json"))
            
            obsidian_path = Path("/Users/tarive/Library/Mobile Documents/iCloud~md~obsidian/Documents/Saksham/brain-poc")
            obsidian_path.mkdir(parents=True, exist_ok=True)
            
            # Create consolidated working memory note
            wm_note = obsidian_path / f"working_memory_{datetime.now():%Y%m%d}.md"
            
            content = f"# Working Memory - {datetime.now():%Y-%m-%d}\n\n"
            
            for wm_file in sorted(wm_files)[-7:]:  # Last 7 items (cognitive limit)
                with open(wm_file) as f:
                    data = json.load(f)
                    content += f"## {wm_file.stem}\n"
                    content += f"- **Content**: {data.get('content', 'N/A')}\n"
                    content += f"- **Importance**: {data.get('importance', 0)}\n"
                    content += f"- **Project**: {data.get('project_id', 'N/A')}\n\n"
            
            wm_note.write_text(content)
            return True
            
        except Exception as e:
            print(f"Obsidian sync error: {e}")
            return False
    
    def _extract_score(self, line: str) -> float:
        """Extract score from search result line"""
        try:
            if 'Score:' in line:
                score_str = line.split('Score:')[1].split()[0]
                return float(score_str)
        except:
            pass
        return 0.0

def main():
    """Command line interface for unified brain"""
    brain = UnifiedBrain()
    
    if len(sys.argv) < 2:
        print("Usage: unified_brain.py [store|search|context|sync] [args...]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "store":
        if len(sys.argv) < 3:
            print("Usage: unified_brain.py store <content> [importance]")
            sys.exit(1)
        
        content = sys.argv[2]
        importance = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
        
        if brain.store_memory(content, importance=importance):
            print(f"✅ Stored in unified brain: {content[:50]}...")
        else:
            print("❌ Failed to store memory")
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: unified_brain.py search <query>")
            sys.exit(1)
        
        query = " ".join(sys.argv[2:])
        results = brain.search_all(query)
        
        print(f"Found {len(results)} results for: {query}\n")
        for i, result in enumerate(results[:10], 1):
            print(f"{i}. [{result['source']}] Score: {result['score']:.3f}")
            print(f"   {result['content'][:100]}...\n")
    
    elif command == "context":
        context = brain.get_session_context()
        print(json.dumps(context, indent=2))
    
    elif command == "sync":
        if brain.sync_to_obsidian():
            print("✅ Synced to Obsidian")
        else:
            print("❌ Sync failed")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()