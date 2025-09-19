#!/usr/bin/env python3
"""
Obsidian Deep Sync - EVERYTHING goes to Obsidian
This is the core principle: Every operation syncs to Obsidian
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

class ObsidianDeepSync:
    def __init__(self):
        self.brain_dir = Path("/Users/tarive/brain-poc")
        self.obsidian_dir = Path("/Users/tarive/Library/Mobile Documents/iCloud~md~obsidian/Documents/Saksham/brain-system")
        
        # Ensure Obsidian directory exists
        self.obsidian_dir.mkdir(parents=True, exist_ok=True)
        
        # Create all necessary subdirectories
        self.ensure_structure()
    
    def ensure_structure(self):
        """Create complete Obsidian structure"""
        dirs = [
            "wins",
            "blockers",
            "memories",
            "documentation",
            "daily",
            "working-memory",
            "commits",
            "insights"
        ]
        for dir_name in dirs:
            (self.obsidian_dir / dir_name).mkdir(exist_ok=True)
    
    def sync_file(self, source_file: Path, category: str = "documentation") -> bool:
        """Sync any file to Obsidian immediately"""
        if not source_file.exists():
            return False
        
        dest_dir = self.obsidian_dir / category
        dest_dir.mkdir(exist_ok=True)
        
        dest_file = dest_dir / source_file.name
        
        # Copy file to Obsidian
        shutil.copy2(source_file, dest_file)
        
        # Also create a markdown note about the sync
        sync_note = self.obsidian_dir / "daily" / f"{datetime.now():%Y-%m-%d}-syncs.md"
        
        with open(sync_note, 'a') as f:
            f.write(f"\n- {datetime.now():%H:%M} - Synced {source_file.name} to {category}\n")
        
        return True
    
    def sync_json_as_markdown(self, json_file: Path, category: str) -> bool:
        """Convert JSON to readable Markdown in Obsidian"""
        if not json_file.exists():
            return False
        
        with open(json_file) as f:
            data = json.load(f)
        
        # Create markdown version
        md_file = self.obsidian_dir / category / f"{json_file.stem}.md"
        
        content = [f"# {json_file.stem.replace('_', ' ').title()}\n\n"]
        content.append(f"*Updated: {datetime.now():%Y-%m-%d %H:%M}*\n\n")
        
        # Convert JSON to readable format
        if isinstance(data, dict):
            for key, value in data.items():
                content.append(f"## {key.replace('_', ' ').title()}\n")
                if isinstance(value, dict):
                    for k, v in value.items():
                        content.append(f"- **{k}**: {v}\n")
                else:
                    content.append(f"{value}\n")
                content.append("\n")
        else:
            content.append(f"```json\n{json.dumps(data, indent=2)}\n```\n")
        
        md_file.write_text("".join(content))
        return True
    
    def sync_all_documentation(self):
        """Sync ALL documentation to Obsidian"""
        docs_synced = 0
        
        # Sync all markdown files
        for md_file in self.brain_dir.glob("*.md"):
            if self.sync_file(md_file, "documentation"):
                docs_synced += 1
        
        # Sync all Python files as documentation
        for py_file in self.brain_dir.glob("*.py"):
            # Create markdown version with code
            md_content = f"# {py_file.stem}\n\n```python\n{py_file.read_text()}\n```"
            md_file = self.obsidian_dir / "documentation" / f"{py_file.stem}.md"
            md_file.write_text(md_content)
            docs_synced += 1
        
        # Sync shell scripts
        for sh_file in self.brain_dir.glob("*.sh"):
            md_content = f"# {sh_file.stem}\n\n```bash\n{sh_file.read_text()}\n```"
            md_file = self.obsidian_dir / "documentation" / f"{sh_file.stem}.md"
            md_file.write_text(md_content)
            docs_synced += 1
        
        return docs_synced
    
    def create_index(self):
        """Create master index in Obsidian"""
        index_file = self.obsidian_dir / "README.md"
        
        content = [
            "# 🧠 Brain System - Obsidian View\n\n",
            f"*Auto-updated: {datetime.now():%Y-%m-%d %H:%M}*\n\n",
            "## 📁 Structure\n\n",
            "- [[documentation/]] - All system docs\n",
            "- [[wins/]] - Every victory\n",
            "- [[blockers/]] - Problems solved\n",
            "- [[memories/]] - Captured thoughts\n",
            "- [[daily/]] - Daily summaries\n",
            "- [[working-memory/]] - Active items\n",
            "- [[commits/]] - Git history\n\n",
            "## 📚 Key Documents\n\n",
            "- [[documentation/SAKSHAM_INDEX]] - Personal guide\n",
            "- [[documentation/BRAIN_MASTER]] - Complete docs\n",
            "- [[documentation/QUICK_REFERENCE]] - Commands\n",
            "- [[active-goals]] - Current commitments\n\n",
            "## 🔄 Auto-Sync Status\n\n",
            "✅ Everything syncs to Obsidian automatically\n",
            "✅ Hourly backups to GitHub\n",
            "✅ Real-time updates\n"
        ]
        
        index_file.write_text("".join(content))

def deep_sync_everything():
    """Master sync function - call this from EVERYWHERE"""
    syncer = ObsidianDeepSync()
    
    # Sync all documentation
    syncer.sync_all_documentation()
    
    # Sync JSON files as markdown
    for json_file in Path("/Users/tarive/brain-poc").glob("*.json"):
        if not json_file.name.startswith('.'):
            syncer.sync_json_as_markdown(json_file, "working-memory")
    
    # Create index
    syncer.create_index()
    
    return True

if __name__ == "__main__":
    if deep_sync_everything():
        print("✅ Everything synced to Obsidian")
    else:
        print("❌ Sync failed")