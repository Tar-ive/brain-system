#!/usr/bin/env python3
"""
Auto-Commit System - Backs up brain changes hourly
Integrates with memory operations to track and commit changes
"""

import subprocess
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

class AutoCommit:
    def __init__(self):
        self.brain_dir = Path("/Users/tarive/brain-poc")
        self.state_file = self.brain_dir / ".auto_commit_state.json"
        self.commit_interval = 3600  # 1 hour in seconds
        
        # Load or initialize state
        self.state = self._load_state()
    
    def _load_state(self) -> dict:
        """Load auto-commit state"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {
            "last_commit": None,
            "last_hash": None,
            "commits_today": 0,
            "total_commits": 0
        }
    
    def _save_state(self):
        """Save auto-commit state"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _get_repo_hash(self) -> str:
        """Get hash of current repo state"""
        # Get list of tracked files and their modification times
        tracked_files = []
        for pattern in ["*.py", "*.sh", "*.md", "*.json"]:
            for file in self.brain_dir.glob(pattern):
                if file.name not in ['.auto_commit_state.json', 'active_goals.json', 'wins_log.json']:
                    stat = file.stat()
                    tracked_files.append(f"{file.name}:{stat.st_mtime}")
        
        # Create hash of current state
        content = "|".join(sorted(tracked_files))
        return hashlib.md5(content.encode()).hexdigest()
    
    def should_commit(self) -> bool:
        """Check if we should auto-commit"""
        # Check if enough time has passed
        if self.state["last_commit"]:
            last_commit = datetime.fromisoformat(self.state["last_commit"])
            time_since = datetime.now() - last_commit
            
            if time_since.total_seconds() < self.commit_interval:
                return False
        
        # Check if there are changes
        current_hash = self._get_repo_hash()
        if current_hash == self.state.get("last_hash"):
            return False  # No changes
        
        return True
    
    def auto_commit(self, message: str = None) -> bool:
        """Perform auto-commit if needed"""
        if not self.should_commit():
            return False
        
        try:
            # Check for changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.brain_dir
            )
            
            if not result.stdout.strip():
                return False  # No changes to commit
            
            # Stage all changes
            subprocess.run(["git", "add", "-A"], cwd=self.brain_dir)
            
            # Generate commit message
            if not message:
                time_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                message = f"Auto-save: Brain state at {time_str}\n\nAutomatic hourly backup of brain system state"
            
            # Commit
            commit_result = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True,
                text=True,
                cwd=self.brain_dir
            )
            
            if commit_result.returncode == 0:
                # Update state
                self.state["last_commit"] = datetime.now().isoformat()
                self.state["last_hash"] = self._get_repo_hash()
                self.state["commits_today"] += 1
                self.state["total_commits"] += 1
                self._save_state()
                
                # Push to remote
                push_result = subprocess.run(
                    ["git", "push"],
                    capture_output=True,
                    text=True,
                    cwd=self.brain_dir
                )
                
                # DEEP SYNC TO OBSIDIAN after every commit
                try:
                    from obsidian_deep_sync import deep_sync_everything
                    deep_sync_everything()
                    print("✅ Synced to Obsidian")
                except Exception as e:
                    print(f"⚠️ Obsidian sync failed: {e}")
                
                if push_result.returncode == 0:
                    return True
                else:
                    print(f"⚠️ Commit saved locally but push failed: {push_result.stderr}")
                    return True
            
        except Exception as e:
            print(f"❌ Auto-commit error: {e}")
        
        return False
    
    def force_commit(self, reason: str) -> bool:
        """Force a commit regardless of time"""
        # Temporarily set last commit to None to force
        original = self.state["last_commit"]
        self.state["last_commit"] = None
        
        message = f"Manual save: {reason}\n\nTriggered by user action"
        result = self.auto_commit(message)
        
        if not result:
            self.state["last_commit"] = original
        
        return result
    
    def status(self) -> str:
        """Get auto-commit status"""
        status_lines = ["📊 Auto-Commit Status"]
        status_lines.append("=" * 30)
        
        if self.state["last_commit"]:
            last = datetime.fromisoformat(self.state["last_commit"])
            time_since = datetime.now() - last
            mins = int(time_since.total_seconds() / 60)
            
            status_lines.append(f"Last commit: {mins} minutes ago")
            status_lines.append(f"Next commit: in {60 - mins} minutes")
        else:
            status_lines.append("No commits yet")
        
        status_lines.append(f"Commits today: {self.state['commits_today']}")
        status_lines.append(f"Total commits: {self.state['total_commits']}")
        
        # Check for uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=self.brain_dir
        )
        
        if result.stdout.strip():
            changes = len(result.stdout.strip().split('\n'))
            status_lines.append(f"⚠️ Uncommitted changes: {changes} files")
        else:
            status_lines.append("✅ All changes committed")
        
        return "\n".join(status_lines)

def main():
    """CLI interface"""
    import sys
    
    auto = AutoCommit()
    
    if len(sys.argv) < 2:
        print("Auto-Commit System")
        print("Commands: check | commit | force <reason> | status")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "check":
        if auto.should_commit():
            print("✅ Auto-commit needed")
            if auto.auto_commit():
                print("✅ Changes committed and pushed")
            else:
                print("❌ Commit failed")
        else:
            print("✅ No commit needed yet")
    
    elif cmd == "commit":
        if auto.auto_commit():
            print("✅ Changes committed and pushed")
        else:
            print("ℹ️ No changes to commit or not time yet")
    
    elif cmd == "force":
        reason = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Manual backup"
        if auto.force_commit(reason):
            print(f"✅ Force committed: {reason}")
        else:
            print("❌ Force commit failed")
    
    elif cmd == "status":
        print(auto.status())
    
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()