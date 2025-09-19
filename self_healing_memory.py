#!/usr/bin/env python3
"""
Self-Healing Capabilities for Memory Tool
Automatically detects and fixes common issues
"""

import json
import os
from pathlib import Path
from datetime import datetime
import hashlib
import shutil

class SelfHealingMemory:
    """
    Self-healing capabilities for the memory system
    """
    
    def __init__(self):
        self.brain_poc = Path("/Users/tarive/brain-poc")
        self.obsidian_vault = Path("/Users/tarive/Library/Mobile Documents/iCloud~md~obsidian/Documents/Saksham")
        self.issues_found = []
        self.fixes_applied = []
    
    def diagnose_and_heal(self):
        """Run full diagnostic and healing process"""
        print("🔧 Running Self-Healing Diagnostics...\n")
        
        # Check directory structure
        self.check_directory_structure()
        
        # Fix duplicate IDs issue
        self.fix_duplicate_ids()
        
        # Repair broken links
        self.repair_broken_links()
        
        # Sync discrepancies
        self.sync_obsidian_working_memory()
        
        # Clean corrupted files
        self.clean_corrupted_files()
        
        # Rebuild indices
        self.rebuild_indices()
        
        # Report results
        self.report_healing_results()
    
    def check_directory_structure(self):
        """Ensure all required directories exist"""
        required_dirs = [
            self.brain_poc / "working-memory",
            self.brain_poc / "scripts",
            self.brain_poc / "data",
            self.obsidian_vault / "people",
            self.obsidian_vault / "working-memory",
            self.obsidian_vault / "daily"
        ]
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                self.fixes_applied.append(f"Created missing directory: {dir_path}")
                print(f"✅ Created: {dir_path}")
    
    def fix_duplicate_ids(self):
        """Fix the duplicate ID issue in working memory"""
        print("🔍 Checking for duplicate IDs...")
        
        wm_dir = self.brain_poc / "working-memory"
        seen_ids = {}
        duplicates = []
        
        for json_file in wm_dir.glob("wm_*.json"):
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    item_id = data.get('id')
                    
                    if item_id in seen_ids:
                        duplicates.append((json_file, seen_ids[item_id]))
                    else:
                        seen_ids[item_id] = json_file
            except Exception as e:
                self.issues_found.append(f"Corrupted file: {json_file}")
        
        # Fix duplicates by assigning new IDs
        for dup_file, original_file in duplicates:
            try:
                with open(dup_file) as f:
                    data = json.load(f)
                
                # Generate new unique ID
                timestamp = datetime.now()
                new_id = f"wm_{timestamp.strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"
                data['id'] = new_id
                
                # Save with new ID
                new_file = wm_dir / f"{new_id}.json"
                with open(new_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                # Remove duplicate
                dup_file.unlink()
                
                self.fixes_applied.append(f"Fixed duplicate ID: {dup_file.name} → {new_file.name}")
                print(f"✅ Fixed duplicate: {new_file.name}")
                
            except Exception as e:
                self.issues_found.append(f"Could not fix duplicate: {dup_file}")
    
    def repair_broken_links(self):
        """Find and repair broken links in Obsidian notes"""
        print("🔗 Checking for broken links...")
        
        broken_links = []
        
        for md_file in self.obsidian_vault.rglob("*.md"):
            try:
                with open(md_file) as f:
                    content = f.read()
                
                # Find wiki links
                import re
                wiki_links = re.findall(r'\[\[([^\]]+)\]\]', content)
                
                for link in wiki_links:
                    # Check if target exists
                    target_path = self.obsidian_vault / f"{link}.md"
                    if not target_path.exists():
                        # Try to find similar file
                        similar = self.find_similar_file(link)
                        if similar:
                            # Fix the link
                            new_content = content.replace(f"[[{link}]]", f"[[{similar}]]")
                            with open(md_file, 'w') as f:
                                f.write(new_content)
                            self.fixes_applied.append(f"Fixed link: {link} → {similar}")
                        else:
                            broken_links.append((md_file, link))
            except Exception as e:
                self.issues_found.append(f"Error checking {md_file}: {e}")
        
        if broken_links:
            self.issues_found.append(f"Found {len(broken_links)} broken links")
    
    def sync_obsidian_working_memory(self):
        """Ensure working memory is synced between brain-poc and Obsidian"""
        print("🔄 Syncing working memory...")
        
        # Get all working memory items
        wm_items = []
        wm_dir = self.brain_poc / "working-memory"
        
        for json_file in wm_dir.glob("wm_*.json"):
            try:
                with open(json_file) as f:
                    wm_items.append(json.load(f))
            except:
                pass
        
        # Check if each item exists in Obsidian
        missing_in_obsidian = []
        
        for item in wm_items:
            project = item.get('project_id', 'general')
            
            # Determine where it should be stored
            if project == "dci-analysis":
                project_dir = self.obsidian_vault / "uni-work/thrc/dci_analysis/working-memory"
            elif project == "econ-data":
                project_dir = self.obsidian_vault / "uni-work/thrc/econ-data/working-memory"
            elif project == "personal":
                project_dir = self.obsidian_vault / "saksham-personal/working-memory"
            else:
                project_dir = self.obsidian_vault / "working-memory"
            
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists
            item_id = item.get('id', 'unknown')
            expected_files = list(project_dir.glob(f"*{item_id}*.md"))
            
            if not expected_files:
                # Create the missing file
                self.create_obsidian_note(item, project_dir)
                self.fixes_applied.append(f"Created missing Obsidian note for {item_id}")
    
    def create_obsidian_note(self, item, project_dir):
        """Create an Obsidian note from working memory item"""
        timestamp = item.get('stored_at', datetime.now().isoformat())
        content = item.get('content', '')
        
        filename = f"{datetime.now().strftime('%Y-%m-%d-%H%M%S')}-memory.md"
        filepath = project_dir / filename
        
        md_content = f"""---
title: "{content[:50]}..."
date: {timestamp}
type: working-memory
---

# {content[:50]}...

## Content
{content}

## Metadata
{json.dumps(item.get('context', {}), indent=2)}
"""
        
        with open(filepath, 'w') as f:
            f.write(md_content)
    
    def clean_corrupted_files(self):
        """Remove or fix corrupted JSON files"""
        print("🧹 Cleaning corrupted files...")
        
        wm_dir = self.brain_poc / "working-memory"
        
        for json_file in wm_dir.glob("*.json"):
            try:
                with open(json_file) as f:
                    json.load(f)
            except json.JSONDecodeError:
                # Backup and remove corrupted file
                backup_dir = wm_dir / "corrupted_backup"
                backup_dir.mkdir(exist_ok=True)
                
                backup_path = backup_dir / f"{json_file.name}.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.move(str(json_file), str(backup_path))
                
                self.fixes_applied.append(f"Moved corrupted file to backup: {json_file.name}")
                print(f"🗑️ Moved corrupted: {json_file.name}")
    
    def rebuild_indices(self):
        """Rebuild the working memory index"""
        print("📇 Rebuilding indices...")
        
        wm_dir = self.brain_poc / "working-memory"
        index_file = wm_dir / "index.json"
        
        # Collect all valid items
        items = []
        for json_file in wm_dir.glob("wm_*.json"):
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    items.append({
                        "id": data.get('id'),
                        "stored_at": data.get('stored_at'),
                        "importance_score": data.get('importance_score', 0.5),
                        "project_id": data.get('project_id', 'unknown')
                    })
            except:
                pass
        
        # Sort by importance and recency
        items.sort(key=lambda x: (x['importance_score'], x['stored_at']), reverse=True)
        
        # Keep only top 7 (working memory limit)
        active_items = items[:7]
        
        # Save new index
        index_data = {
            "items": active_items,
            "last_updated": datetime.now().isoformat(),
            "capacity": 7,
            "current_count": len(active_items)
        }
        
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)
        
        self.fixes_applied.append("Rebuilt working memory index")
        print("✅ Index rebuilt")
    
    def find_similar_file(self, target):
        """Find similar file name in vault"""
        # Simple similarity check - could be enhanced
        target_lower = target.lower().replace("-", "_").replace(" ", "_")
        
        for md_file in self.obsidian_vault.rglob("*.md"):
            file_stem = md_file.stem.lower().replace("-", "_").replace(" ", "_")
            if target_lower in file_stem or file_stem in target_lower:
                return md_file.stem
        
        return None
    
    def report_healing_results(self):
        """Report all issues found and fixes applied"""
        print("\n" + "="*50)
        print("🏥 SELF-HEALING REPORT")
        print("="*50)
        
        if self.fixes_applied:
            print(f"\n✅ Fixes Applied ({len(self.fixes_applied)}):")
            for fix in self.fixes_applied:
                print(f"   • {fix}")
        else:
            print("\n✅ No issues found - system is healthy!")
        
        if self.issues_found:
            print(f"\n⚠️ Issues Found ({len(self.issues_found)}):")
            for issue in self.issues_found:
                print(f"   • {issue}")
        
        print("\n🎯 Healing Status: Complete")
        print(f"   Total Fixes: {len(self.fixes_applied)}")
        print(f"   Remaining Issues: {len(self.issues_found)}")

if __name__ == "__main__":
    healer = SelfHealingMemory()
    healer.diagnose_and_heal()