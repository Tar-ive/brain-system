#!/usr/bin/env python3
"""
Obsidian Sync - Saves brain memory to Obsidian vault
Ensures everything important is backed up to your knowledge base
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class ObsidianSync:
    def __init__(self):
        self.brain_dir = Path("/Users/tarive/brain-poc")
        self.obsidian_dir = Path("/Users/tarive/Library/Mobile Documents/iCloud~md~obsidian/Documents/Saksham")
        
        # Ensure directories exist
        self.obsidian_brain = self.obsidian_dir / "brain-system"
        self.obsidian_brain.mkdir(exist_ok=True)
        
        self.obsidian_wins = self.obsidian_brain / "wins"
        self.obsidian_wins.mkdir(exist_ok=True)
        
        self.obsidian_blockers = self.obsidian_brain / "blockers"
        self.obsidian_blockers.mkdir(exist_ok=True)
        
        self.obsidian_memory = self.obsidian_brain / "memories"
        self.obsidian_memory.mkdir(exist_ok=True)
    
    def sync_all(self) -> Dict:
        """Sync everything to Obsidian"""
        results = {
            'goals': self.sync_goals(),
            'wins': self.sync_wins(),
            'memories': self.sync_recent_memories(),
            'daily': self.create_daily_note()
        }
        return results
    
    def sync_goals(self) -> bool:
        """Sync active goals to Obsidian"""
        goals_file = self.brain_dir / "active_goals.json"
        if not goals_file.exists():
            return False
        
        with open(goals_file) as f:
            goals = json.load(f)
        
        # Create goals overview in Obsidian
        obsidian_goals = self.obsidian_brain / "active-goals.md"
        
        content = ["# 🎯 Active Goals\n"]
        content.append(f"*Updated: {datetime.now():%Y-%m-%d %H:%M}*\n\n")
        
        for project, data in goals.items():
            excitement = "🔥" * data.get('excitement_level', 0)
            content.append(f"## {project}\n")
            content.append(f"- **Status**: {data.get('status', 'unknown')}\n")
            content.append(f"- **Excitement**: {excitement} ({data.get('excitement_level', 0)}/10)\n")
            content.append(f"- **Days Committed**: {data.get('days_worked', 0)}\n")
            content.append(f"- **Last Win**: {data.get('last_win', 'Never')}\n")
            content.append(f"- **Commitment**: {data.get('commitment', 'Keep going!')}\n")
            
            if data.get('blockers'):
                content.append("\n### ⚠️ Active Blockers\n")
                for blocker in data['blockers']:
                    if not blocker.get('resolved'):
                        content.append(f"- {blocker['issue']}\n")
            
            content.append("\n---\n\n")
        
        obsidian_goals.write_text("".join(content))
        return True
    
    def sync_wins(self) -> int:
        """Sync wins log to Obsidian"""
        wins_file = self.brain_dir / "wins_log.json"
        if not wins_file.exists():
            return 0
        
        with open(wins_file) as f:
            wins = json.load(f)
        
        # Create individual win notes
        count = 0
        for win in wins[-10:]:  # Last 10 wins
            timestamp = win.get('timestamp', datetime.now().isoformat())
            date_str = timestamp.split('T')[0]
            
            win_file = self.obsidian_wins / f"{date_str}-win-{count}.md"
            
            content = [f"# 🎉 Win: {win.get('win', 'Achievement')}\n\n"]
            content.append(f"**Project**: {win.get('project', 'unknown')}\n")
            content.append(f"**Time**: {timestamp}\n")
            content.append(f"**Excitement**: {win.get('excitement_before', 0)} → {win.get('excitement_after', 0)}\n\n")
            content.append("---\n")
            content.append("Tags: #win #progress #brain-system\n")
            
            win_file.write_text("".join(content))
            count += 1
        
        return count
    
    def sync_recent_memories(self) -> int:
        """Sync recent memories from simple_brain to Obsidian"""
        memory_log = Path.home() / ".brain" / "memory.log"
        if not memory_log.exists():
            return 0
        
        # Read last 20 memories
        with open(memory_log) as f:
            lines = f.readlines()
        
        recent = lines[-20:] if len(lines) > 20 else lines
        
        # Create consolidated memory note
        memory_note = self.obsidian_memory / f"{datetime.now():%Y-%m-%d}-memories.md"
        
        content = [f"# 📝 Memories - {datetime.now():%Y-%m-%d}\n\n"]
        
        for line in recent:
            try:
                parts = line.strip().split('|')
                if len(parts) >= 5:
                    timestamp, session, importance, project, memory = parts[:5]
                    content.append(f"### {timestamp.split('T')[1][:8]}\n")
                    content.append(f"- **Memory**: {memory}\n")
                    content.append(f"- **Importance**: {importance}\n")
                    content.append(f"- **Project**: {project}\n\n")
            except:
                continue
        
        memory_note.write_text("".join(content))
        return len(recent)
    
    def create_daily_note(self) -> str:
        """Create daily brain summary in Obsidian"""
        daily_note = self.obsidian_brain / f"{datetime.now():%Y-%m-%d}-brain-summary.md"
        
        # Gather all data
        goals_file = self.brain_dir / "active_goals.json"
        wins_file = self.brain_dir / "wins_log.json"
        
        content = [f"# 🧠 Brain Summary - {datetime.now():%Y-%m-%d}\n\n"]
        
        # Goals section
        if goals_file.exists():
            with open(goals_file) as f:
                goals = json.load(f)
            
            content.append("## 🎯 Goals Status\n")
            for project, data in goals.items():
                status_emoji = "🟢" if data['excitement_level'] > 7 else "🟡" if data['excitement_level'] > 4 else "🔴"
                content.append(f"- {status_emoji} **{project}**: Day {data.get('days_worked', 0)}, Excitement {data.get('excitement_level', 0)}/10\n")
        
        # Today's wins
        if wins_file.exists():
            with open(wins_file) as f:
                wins = json.load(f)
            
            today = datetime.now().date().isoformat()
            todays_wins = [w for w in wins if w.get('timestamp', '').startswith(today)]
            
            if todays_wins:
                content.append(f"\n## 🎉 Today's Wins ({len(todays_wins)})\n")
                for win in todays_wins:
                    content.append(f"- {win['win']}\n")
        
        # Working memory status
        wm_index = self.brain_dir / "working-memory" / "index.json"
        if wm_index.exists():
            with open(wm_index) as f:
                wm = json.load(f)
            
            content.append(f"\n## 💭 Working Memory\n")
            content.append(f"- **Capacity**: {wm.get('current_count', 0)}/{wm.get('capacity', 7)}\n")
            content.append(f"- **Last Updated**: {wm.get('last_updated', 'unknown')}\n")
        
        # Links to related notes
        content.append("\n## 🔗 Related\n")
        content.append("- [[active-goals|Current Goals]]\n")
        content.append("- [[wins/|Recent Wins]]\n")
        content.append("- [[memories/|Recent Memories]]\n")
        
        content.append("\n---\n")
        content.append("Tags: #brain-system #daily-summary\n")
        
        daily_note.write_text("".join(content))
        return str(daily_note)

def main():
    import sys
    
    syncer = ObsidianSync()
    
    print("🔄 Syncing to Obsidian...")
    results = syncer.sync_all()
    
    print(f"✅ Goals synced: {results['goals']}")
    print(f"✅ Wins synced: {results['wins']} notes created")
    print(f"✅ Memories synced: {results['memories']} entries")
    print(f"✅ Daily note: {Path(results['daily']).name}")
    
    print(f"\n📁 View in Obsidian: {syncer.obsidian_brain}")

if __name__ == "__main__":
    main()