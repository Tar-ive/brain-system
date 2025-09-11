#!/usr/bin/env python3
"""
Session Context Manager - Saves and restores Claude session context
"""

import json
from datetime import datetime
from pathlib import Path

class SessionContext:
    def __init__(self):
        self.context_file = Path("/Users/tarive/brain-poc/current_session.json")
        self.obsidian_vault = Path("/Users/tarive/Library/Mobile Documents/iCloud~md~obsidian/Documents/Saksham")
    
    def save_session(self, context_data=None):
        """Save current session context"""
        
        if not context_data:
            # Default context from our current session
            context_data = {
                "last_session": datetime.now().isoformat(),
                "project": "brain-poc",
                "status": "POC implementation and testing",
                "completed_tasks": [
                    "Created brain POC with scoring algorithm",
                    "Integrated with Obsidian vault structure",
                    "Created people tracking system",
                    "Fixed iMessage MCP integration",
                    "Implemented self-healing capabilities",
                    "Replied to Cathy"
                ],
                "pending_tasks": [
                    "Send work update to Dr. Ekren (dci-analysis)",
                    "Reply to Harshal",
                    "Validate job_dread_mvp idea from claude_web"
                ],
                "key_files": {
                    "brain_plan": "/Users/tarive/brain.md",
                    "poc_dir": "/Users/tarive/brain-poc/",
                    "search_command": "~/bin/bf",
                    "people_dir": "/Users/tarive/Library/Mobile Documents/iCloud~md~obsidian/Documents/Saksham/people/",
                    "daily_tasks": "/Users/tarive/Library/Mobile Documents/iCloud~md~obsidian/Documents/Saksham/daily/2025-09-11-tasks.md"
                },
                "entities": {
                    "girlfriend": ["kusum", "baby", "shona", "puntu"],
                    "dr_ekren": ["professor", "dci-analysis supervisor"],
                    "claude_web": ["AI agent", "suggested job_dread_mvp"],
                    "cathy": ["replied ✅"],
                    "harshal": ["needs reply"],
                    "aditya": ["contact"]
                },
                "notes": [
                    "Working memory has 7-item limit",
                    "Scoring threshold is 0.75",
                    "iMessage MCP needs macOS permissions",
                    "Self-healing can fix duplicate IDs and broken links"
                ]
            }
        
        # Save to JSON
        with open(self.context_file, 'w') as f:
            json.dump(context_data, f, indent=2)
        
        # Also create a markdown summary for Obsidian
        self.create_session_summary(context_data)
        
        # DEEP SYNC TO OBSIDIAN
        try:
            from obsidian_deep_sync import deep_sync_everything
            deep_sync_everything()
            print("✅ Synced to Obsidian")
        except Exception as e:
            print(f"⚠️ Obsidian sync failed: {e}")
        
        print(f"✅ Session context saved to: {self.context_file}")
        return context_data
    
    def create_session_summary(self, context_data):
        """Create a markdown summary in Obsidian"""
        
        session_dir = self.obsidian_vault / "claude-sessions"
        session_dir.mkdir(exist_ok=True)
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        session_file = session_dir / f"{date_str}-session.md"
        
        content = f"""---
title: Claude Session - {date_str}
date: {datetime.now().isoformat()}
type: session-context
---

# Claude Session Context - {date_str}

## Project Status
- **Current Project**: {context_data.get('project', 'brain-poc')}
- **Status**: {context_data.get('status', 'In progress')}

## Completed Tasks
{chr(10).join([f"- ✅ {task}" for task in context_data.get('completed_tasks', [])])}

## Pending Tasks
{chr(10).join([f"- ⏳ {task}" for task in context_data.get('pending_tasks', [])])}

## Key Files & Commands
```bash
# Search command
~/bin/bf "search query"

# Brain plan
cat {context_data['key_files'].get('brain_plan', '/Users/tarive/brain.md')}

# POC directory
cd {context_data['key_files'].get('poc_dir', '/Users/tarive/brain-poc/')}

# Self-healing
python3 /Users/tarive/brain-poc/self_healing_memory.py
```

## Entity Mappings
{chr(10).join([f"- **{entity}**: {', '.join(aliases)}" for entity, aliases in context_data.get('entities', {}).items()])}

## Important Notes
{chr(10).join([f"- {note}" for note in context_data.get('notes', [])])}

## Next Session Instructions
When starting next Claude session, run:
```bash
python3 /Users/tarive/brain-poc/restore_context.py
```

This will load all context and show pending tasks.
"""
        
        with open(session_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Session summary saved to Obsidian: {session_file.name}")
    
    def load_session(self):
        """Load previous session context"""
        
        if not self.context_file.exists():
            print("❌ No previous session found")
            return None
        
        with open(self.context_file) as f:
            context = json.load(f)
        
        print("="*60)
        print("🧠 PREVIOUS SESSION CONTEXT LOADED")
        print("="*60)
        
        print(f"\n📅 Last Session: {context.get('last_session', 'Unknown')}")
        print(f"📁 Project: {context.get('project', 'Unknown')}")
        print(f"📊 Status: {context.get('status', 'Unknown')}")
        
        print("\n✅ Completed Tasks:")
        for task in context.get('completed_tasks', []):
            print(f"   • {task}")
        
        print("\n⏳ Pending Tasks:")
        for task in context.get('pending_tasks', []):
            print(f"   • {task}")
        
        print("\n🔧 Key Commands:")
        print('   • Search: ~/bin/bf "query"')
        print('   • Self-heal: python3 /Users/tarive/brain-poc/self_healing_memory.py')
        print('   • Status: python3 /Users/tarive/brain-poc/scripts/poc_scoring.py status')
        
        print("\n👥 Entity Mappings:")
        for entity, aliases in context.get('entities', {}).items():
            print(f"   • {entity}: {aliases}")
        
        print("\n" + "="*60)
        
        return context

if __name__ == "__main__":
    manager = SessionContext()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "load":
        manager.load_session()
    else:
        manager.save_session()
        print("\n🔄 To restore in next session, run:")
        print("   python3 /Users/tarive/brain-poc/session_context.py load")