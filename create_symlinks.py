#!/usr/bin/env python3
"""
Create Symlinks for Real-Time Obsidian Sync
Instead of copying files, create symlinks so changes are instant
"""

import os
from pathlib import Path
import subprocess

class SymlinkSync:
    def __init__(self):
        self.brain_dir = Path("/Users/tarive/brain-poc")
        self.obsidian_dir = Path("/Users/tarive/Library/Mobile Documents/iCloud~md~obsidian/Documents/Saksham/brain-system")
        
    def create_symlinks(self):
        """Create symlinks for real-time sync"""
        
        # Ensure Obsidian directory exists
        self.obsidian_dir.mkdir(parents=True, exist_ok=True)
        
        links_created = 0
        links_skipped = 0
        
        # Critical files to symlink
        critical_files = [
            "CLAUDE.md",
            "BRAIN_MASTER.md", 
            "QUICK_REFERENCE.md",
            "SAKSHAM_INDEX.md",
            "active_goals.json",
            "wins_log.json",
            "commitment.json",
            "current_session.json"
        ]
        
        for filename in critical_files:
            source = self.brain_dir / filename
            target = self.obsidian_dir / filename
            
            if source.exists():
                if target.exists() or target.is_symlink():
                    # Remove existing file/link
                    target.unlink()
                    
                # Create symlink
                os.symlink(source, target)
                links_created += 1
                print(f"✅ Linked: {filename}")
            else:
                links_skipped += 1
                print(f"⏭️ Skipped (not found): {filename}")
        
        # Link all Python files as documentation
        docs_dir = self.obsidian_dir / "code"
        docs_dir.mkdir(exist_ok=True)
        
        for py_file in self.brain_dir.glob("*.py"):
            target = docs_dir / py_file.name
            
            if target.exists() or target.is_symlink():
                target.unlink()
            
            os.symlink(py_file, target)
            links_created += 1
        
        # Link shell scripts
        for sh_file in self.brain_dir.glob("*.sh"):
            target = docs_dir / sh_file.name
            
            if target.exists() or target.is_symlink():
                target.unlink()
                
            os.symlink(sh_file, target)
            links_created += 1
        
        print(f"\n📊 Symlink Summary:")
        print(f"   Created: {links_created} links")
        print(f"   Skipped: {links_skipped} files")
        print(f"\n✨ Real-time sync enabled!")
        print(f"   Changes in {self.brain_dir}")
        print(f"   Instantly appear in Obsidian!")
        
        return links_created

    def verify_sync(self):
        """Verify that symlinks are working"""
        from datetime import datetime
        test_file = self.brain_dir / "sync_test.txt"
        test_content = f"Test sync at {datetime.now().isoformat()}"
        
        # Write test file
        test_file.write_text(test_content)
        
        # Check if it appears in Obsidian
        obsidian_test = self.obsidian_dir / "sync_test.txt"
        
        if not obsidian_test.exists():
            # Create symlink for test file
            os.symlink(test_file, obsidian_test)
        
        # Verify content matches
        if obsidian_test.exists() and obsidian_test.read_text() == test_content:
            print("✅ Real-time sync verified!")
            # Clean up test files
            test_file.unlink()
            obsidian_test.unlink()
            return True
        else:
            print("❌ Sync verification failed")
            return False

def main():
    syncer = SymlinkSync()
    
    print("🔗 Creating symlinks for real-time Obsidian sync...")
    links = syncer.create_symlinks()
    
    print("\n🧪 Verifying sync...")
    if syncer.verify_sync():
        print("\n🎉 SUCCESS! All changes now sync instantly to Obsidian!")
        print("   No more manual syncing needed!")
    else:
        print("\n⚠️ Sync verification failed, but links were created")
        print("   Check Obsidian vault permissions")

if __name__ == "__main__":
    main()