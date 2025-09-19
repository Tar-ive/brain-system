#!/usr/bin/env python3
"""
Global Obsidian Sync System - Ensures EVERYTHING gets saved and indexed
This is the master sync that makes sure nothing is lost
"""

import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set
import hashlib
import subprocess

class GlobalObsidianSync:
    """
    Comprehensive sync system that ensures ALL brain data
    gets properly saved, indexed, and searchable in Obsidian
    """
    
    def __init__(self):
        self.brain_dir = Path("/Users/tarive/brain-poc")
        self.obsidian_dir = Path("/Users/tarive/Library/Mobile Documents/iCloud~md~obsidian/Documents/Saksham")
        
        # Master directories in Obsidian
        self.obs_brain = self.obsidian_dir / "brain-system"
        self.obs_daily = self.obsidian_dir / "daily"
        self.obs_people = self.obsidian_dir / "people"
        self.obs_projects = self.obsidian_dir / "projects"
        
        # Ensure all directories exist
        for dir_path in [self.obs_brain, self.obs_daily, self.obs_people, self.obs_projects]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Sub-directories for complete organization
        self.setup_obsidian_structure()
        
        # Track what needs syncing
        self.sync_manifest = self.brain_dir / ".sync_manifest.json"
        self.load_manifest()
    
    def setup_obsidian_structure(self):
        """Create comprehensive directory structure in Obsidian"""
        
        # Brain system structure
        subdirs = [
            "memories",
            "goals",
            "wins",
            "blockers",
            "patterns",
            "working-memory",
            "sessions",
            "insights",
            "photos",
            "indexes"
        ]
        
        for subdir in subdirs:
            (self.obs_brain / subdir).mkdir(exist_ok=True)
    
    def load_manifest(self):
        """Load sync manifest to track what's been synced"""
        if self.sync_manifest.exists():
            with open(self.sync_manifest) as f:
                self.manifest = json.load(f)
        else:
            self.manifest = {
                "last_sync": None,
                "synced_files": {},
                "sync_counts": {},
                "indexes": {}
            }
    
    def save_manifest(self):
        """Save sync manifest"""
        self.manifest["last_sync"] = datetime.now().isoformat()
        with open(self.sync_manifest, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    def get_file_hash(self, file_path: Path) -> str:
        """Get hash of file to detect changes"""
        if not file_path.exists():
            return ""
        
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()[:16]
    
    def sync_all(self, force: bool = False) -> Dict:
        """
        Complete sync of ALL brain data to Obsidian
        Set force=True to resync everything
        """
        
        print("🔄 Starting Global Obsidian Sync...")
        results = {
            "timestamp": datetime.now().isoformat(),
            "synced": [],
            "errors": [],
            "stats": {}
        }
        
        # 1. Sync core data files
        results["core_files"] = self.sync_core_files(force)
        
        # 2. Sync working memory
        results["working_memory"] = self.sync_working_memory(force)
        
        # 3. Sync goals and patterns
        results["goals"] = self.sync_goals_and_patterns(force)
        
        # 4. Sync daily photos and extracted goals
        results["photos"] = self.sync_daily_photos(force)
        
        # 5. Sync session contexts
        results["sessions"] = self.sync_sessions(force)
        
        # 6. Sync people and entities
        results["people"] = self.sync_people_entities(force)
        
        # 7. Create master indexes
        results["indexes"] = self.create_master_indexes()
        
        # 8. Create daily dashboard
        results["dashboard"] = self.create_daily_dashboard(results)
        
        # Save manifest
        self.save_manifest()
        
        return results
    
    def sync_core_files(self, force: bool = False) -> Dict:
        """Sync all core JSON and data files"""
        
        core_files = [
            "active_goals.json",
            "wins_log.json",
            "commitment.json",
            "current_session.json",
            ".auto_commit_state.json"
        ]
        
        synced = []
        for filename in core_files:
            file_path = self.brain_dir / filename
            if file_path.exists():
                # Check if needs syncing
                current_hash = self.get_file_hash(file_path)
                last_hash = self.manifest["synced_files"].get(str(file_path), "")
                
                if force or current_hash != last_hash:
                    # Convert to markdown and sync
                    self.json_to_markdown(file_path)
                    self.manifest["synced_files"][str(file_path)] = current_hash
                    synced.append(filename)
        
        return {"count": len(synced), "files": synced}
    
    def json_to_markdown(self, json_path: Path):
        """Convert JSON file to readable markdown in Obsidian"""
        
        with open(json_path) as f:
            data = json.load(f)
        
        # Determine output location
        filename = json_path.stem
        if "goal" in filename:
            output_dir = self.obs_brain / "goals"
        elif "win" in filename:
            output_dir = self.obs_brain / "wins"
        elif "session" in filename:
            output_dir = self.obs_brain / "sessions"
        else:
            output_dir = self.obs_brain / "memories"
        
        output_path = output_dir / f"{filename}.md"
        
        # Create markdown content
        content = [f"# {filename.replace('_', ' ').title()}\n\n"]
        content.append(f"*Last Updated: {datetime.now():%Y-%m-%d %H:%M}*\n\n")
        
        # Format based on content type
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    content.append(f"## {key.replace('_', ' ').title()}\n")
                    for subkey, subvalue in value.items():
                        content.append(f"- **{subkey}**: {subvalue}\n")
                    content.append("\n")
                elif isinstance(value, list):
                    content.append(f"## {key.replace('_', ' ').title()}\n")
                    for item in value[:20]:  # Limit to 20 items
                        if isinstance(item, dict):
                            content.append(f"- {json.dumps(item, indent=2)}\n")
                        else:
                            content.append(f"- {item}\n")
                    content.append("\n")
                else:
                    content.append(f"**{key}**: {value}\n\n")
        
        content.append("\n---\n")
        content.append(f"Source: `{json_path.name}`\n")
        content.append(f"Tags: #brain-system #synced #{filename.replace('_', '-')}\n")
        
        output_path.write_text("".join(content))
        
        return output_path
    
    def sync_working_memory(self, force: bool = False) -> Dict:
        """Sync all working memory items"""
        
        wm_dir = self.brain_dir / "working-memory"
        if not wm_dir.exists():
            return {"count": 0}
        
        synced = 0
        for wm_file in wm_dir.glob("wm_*.json"):
            current_hash = self.get_file_hash(wm_file)
            last_hash = self.manifest["synced_files"].get(str(wm_file), "")
            
            if force or current_hash != last_hash:
                # Read and convert to markdown
                with open(wm_file) as f:
                    data = json.load(f)
                
                # Create readable note
                output_path = self.obs_brain / "working-memory" / f"{wm_file.stem}.md"
                
                content = [f"# Working Memory: {data.get('id', wm_file.stem)}\n\n"]
                content.append(f"**Created**: {data.get('stored_at', 'unknown')}\n")
                content.append(f"**Importance**: {data.get('importance_score', 0)}\n")
                content.append(f"**Project**: {data.get('project_id', 'general')}\n\n")
                content.append("## Content\n")
                content.append(f"{data.get('content', 'No content')}\n\n")
                
                if data.get('context'):
                    content.append("## Context\n")
                    content.append(f"```json\n{json.dumps(data['context'], indent=2)}\n```\n\n")
                
                content.append("---\n")
                content.append("Tags: #working-memory #brain-system\n")
                
                output_path.write_text("".join(content))
                self.manifest["synced_files"][str(wm_file)] = current_hash
                synced += 1
        
        return {"count": synced}
    
    def sync_goals_and_patterns(self, force: bool = False) -> Dict:
        """Sync daily goals and detected patterns"""
        
        goals_dir = self.brain_dir / "daily-goals"
        patterns_dir = self.brain_dir / "patterns"
        
        synced_goals = 0
        synced_patterns = 0
        
        # Sync goals
        if goals_dir.exists():
            for goals_file in goals_dir.glob("*-goals.json"):
                current_hash = self.get_file_hash(goals_file)
                last_hash = self.manifest["synced_files"].get(str(goals_file), "")
                
                if force or current_hash != last_hash:
                    with open(goals_file) as f:
                        data = json.load(f)
                    
                    # Create detailed goal note
                    date = data.get("date", goals_file.stem.split("-goals")[0])
                    output_path = self.obs_brain / "goals" / f"{date}-goals.md"
                    
                    content = [f"# Daily Goals - {date}\n\n"]
                    
                    if data.get("goals"):
                        content.append("## Goals\n")
                        for goal in data["goals"]:
                            status = "✅" if goal.get("status") == "completed" else "⏳"
                            priority = "🔴" if goal.get("priority") == "high" else "🟡"
                            content.append(f"{status} {priority} **{goal['text']}**\n")
                            content.append(f"   - Category: {goal.get('category', 'general')}\n")
                            content.append(f"   - ID: `{goal.get('id', 'unknown')}`\n\n")
                    
                    if data.get("patterns"):
                        content.append("## Detected Patterns\n")
                        patterns = data["patterns"]
                        
                        if patterns.get("insights"):
                            content.append("### Insights\n")
                            for insight in patterns["insights"]:
                                content.append(f"- {insight}\n")
                            content.append("\n")
                        
                        if patterns.get("recurring_themes"):
                            content.append("### Recurring Themes\n")
                            for theme in patterns["recurring_themes"]:
                                content.append(f"- **{theme['theme']}** ({theme['frequency']}x)\n")
                            content.append("\n")
                    
                    content.append("---\n")
                    content.append(f"Tags: #daily-goals #{date} #brain-system\n")
                    
                    output_path.write_text("".join(content))
                    self.manifest["synced_files"][str(goals_file)] = current_hash
                    synced_goals += 1
        
        # Sync patterns
        if patterns_dir.exists():
            for pattern_file in patterns_dir.glob("*-patterns.json"):
                current_hash = self.get_file_hash(pattern_file)
                last_hash = self.manifest["synced_files"].get(str(pattern_file), "")
                
                if force or current_hash != last_hash:
                    self.json_to_markdown(pattern_file)
                    self.manifest["synced_files"][str(pattern_file)] = current_hash
                    synced_patterns += 1
        
        return {"goals": synced_goals, "patterns": synced_patterns}
    
    def sync_daily_photos(self, force: bool = False) -> Dict:
        """Copy daily photos to Obsidian attachments"""
        
        photos_dir = self.brain_dir / "daily-goals"
        obs_photos = self.obs_brain / "photos"
        
        synced = 0
        if photos_dir.exists():
            for photo in photos_dir.glob("*.jpg"):
                dest = obs_photos / photo.name
                if force or not dest.exists():
                    shutil.copy2(photo, dest)
                    synced += 1
            
            for photo in photos_dir.glob("*.png"):
                dest = obs_photos / photo.name
                if force or not dest.exists():
                    shutil.copy2(photo, dest)
                    synced += 1
        
        return {"count": synced}
    
    def sync_sessions(self, force: bool = False) -> Dict:
        """Sync all session contexts"""
        
        session_files = list(self.brain_dir.glob("*session*.json"))
        synced = 0
        
        for session_file in session_files:
            current_hash = self.get_file_hash(session_file)
            last_hash = self.manifest["synced_files"].get(str(session_file), "")
            
            if force or current_hash != last_hash:
                self.json_to_markdown(session_file)
                self.manifest["synced_files"][str(session_file)] = current_hash
                synced += 1
        
        # Also sync session notes from Obsidian claude-sessions
        claude_sessions = self.obsidian_dir / "claude-sessions"
        if claude_sessions.exists():
            # Create index of all sessions
            self.create_session_index(claude_sessions)
        
        return {"count": synced}
    
    def sync_people_entities(self, force: bool = False) -> Dict:
        """Ensure all people/entities are properly indexed"""
        
        # Read entities from current session
        session_file = self.brain_dir / "current_session.json"
        if not session_file.exists():
            return {"count": 0}
        
        with open(session_file) as f:
            data = json.load(f)
        
        entities = data.get("entities", {})
        synced = 0
        
        for entity, aliases in entities.items():
            entity_file = self.obs_people / f"{entity}.md"
            
            # Check if needs updating
            if force or not entity_file.exists():
                content = [f"# {entity.replace('_', ' ').title()}\n\n"]
                content.append("## Aliases\n")
                
                if isinstance(aliases, list):
                    for alias in aliases:
                        content.append(f"- {alias}\n")
                else:
                    content.append(f"- {aliases}\n")
                
                content.append("\n## Notes\n")
                content.append("_Add notes about this person/entity here_\n\n")
                
                content.append("## Related\n")
                content.append("- [[daily/|Daily Notes]]\n")
                content.append("- [[brain-system/|Brain System]]\n\n")
                
                content.append("---\n")
                content.append(f"Tags: #person #{entity.replace('_', '-')} #entity\n")
                
                entity_file.write_text("".join(content))
                synced += 1
        
        return {"count": synced}
    
    def create_master_indexes(self) -> Dict:
        """Create searchable indexes for everything"""
        
        indexes_created = []
        
        # 1. Master Brain Index
        master_index = self.obs_brain / "indexes" / "MASTER_INDEX.md"
        
        content = [f"# 🧠 Master Brain Index\n\n"]
        content.append(f"*Generated: {datetime.now():%Y-%m-%d %H:%M}*\n\n")
        
        # Stats
        stats = self.calculate_stats()
        content.append("## 📊 System Stats\n")
        for key, value in stats.items():
            content.append(f"- **{key}**: {value}\n")
        content.append("\n")
        
        # Quick Links
        content.append("## 🔗 Quick Access\n")
        content.append("- [[active-goals|Current Goals]]\n")
        content.append("- [[../daily/|Daily Notes]]\n")
        content.append("- [[../people/|People & Entities]]\n")
        content.append("- [[working-memory/|Working Memory]]\n")
        content.append("- [[patterns/|Detected Patterns]]\n\n")
        
        # Recent Activity
        content.append("## 📅 Recent Activity\n")
        recent_files = sorted(
            self.obs_brain.rglob("*.md"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:10]
        
        for file in recent_files:
            rel_path = file.relative_to(self.obs_brain)
            content.append(f"- [[{rel_path.stem}|{rel_path.stem.replace('-', ' ').title()}]]\n")
        
        content.append("\n---\n")
        content.append("Tags: #index #brain-system #master\n")
        
        master_index.write_text("".join(content))
        indexes_created.append("MASTER_INDEX")
        
        # 2. Goal Progress Index
        goal_index = self.obs_brain / "indexes" / "GOAL_PROGRESS.md"
        
        content = [f"# 📈 Goal Progress Tracker\n\n"]
        content.append(f"*Updated: {datetime.now():%Y-%m-%d %H:%M}*\n\n")
        
        # Load goal data
        goals_file = self.brain_dir / "active_goals.json"
        if goals_file.exists():
            with open(goals_file) as f:
                goals = json.load(f)
            
            for project, data in goals.items():
                excitement = "🔥" * data.get("excitement_level", 0)
                content.append(f"## {project}\n")
                content.append(f"- Days: {data.get('days_worked', 0)}\n")
                content.append(f"- Excitement: {excitement}\n")
                content.append(f"- Status: {data.get('status', 'unknown')}\n\n")
        
        goal_index.write_text("".join(content))
        indexes_created.append("GOAL_PROGRESS")
        
        # 3. Pattern Insights Index
        pattern_index = self.obs_brain / "indexes" / "PATTERN_INSIGHTS.md"
        
        content = [f"# 💡 Pattern Insights\n\n"]
        content.append(f"*Generated: {datetime.now():%Y-%m-%d %H:%M}*\n\n")
        
        # Aggregate all patterns
        patterns_dir = self.brain_dir / "patterns"
        if patterns_dir.exists():
            all_patterns = {}
            for pattern_file in patterns_dir.glob("*.json"):
                with open(pattern_file) as f:
                    data = json.load(f)
                    
                    # Aggregate insights
                    if "insights" in data:
                        date = pattern_file.stem.split("-patterns")[0]
                        all_patterns[date] = data["insights"]
            
            content.append("## Recent Insights\n")
            for date in sorted(all_patterns.keys(), reverse=True)[:7]:
                content.append(f"\n### {date}\n")
                for insight in all_patterns[date]:
                    content.append(f"- {insight}\n")
        
        pattern_index.write_text("".join(content))
        indexes_created.append("PATTERN_INSIGHTS")
        
        return {"indexes": indexes_created}
    
    def create_session_index(self, sessions_dir: Path):
        """Create index of all Claude sessions"""
        
        index_path = self.obs_brain / "indexes" / "SESSIONS.md"
        
        content = [f"# 📝 Claude Sessions Index\n\n"]
        content.append(f"*Updated: {datetime.now():%Y-%m-%d %H:%M}*\n\n")
        
        sessions = sorted(sessions_dir.glob("*.md"), reverse=True)
        
        for session in sessions[:20]:  # Last 20 sessions
            content.append(f"- [[{session.stem}]]\n")
        
        index_path.write_text("".join(content))
    
    def calculate_stats(self) -> Dict:
        """Calculate system statistics"""
        
        stats = {}
        
        # Working memory count
        wm_dir = self.brain_dir / "working-memory"
        if wm_dir.exists():
            stats["Working Memory Items"] = len(list(wm_dir.glob("wm_*.json")))
        
        # Goal stats
        goals_file = self.brain_dir / "active_goals.json"
        if goals_file.exists():
            with open(goals_file) as f:
                goals = json.load(f)
            stats["Active Projects"] = len(goals)
            
            total_days = sum(g.get("days_worked", 0) for g in goals.values())
            stats["Total Days Worked"] = total_days
        
        # Win count
        wins_file = self.brain_dir / "wins_log.json"
        if wins_file.exists():
            with open(wins_file) as f:
                wins = json.load(f)
            stats["Total Wins"] = len(wins)
        
        # Pattern count
        patterns_dir = self.brain_dir / "patterns"
        if patterns_dir.exists():
            stats["Pattern Files"] = len(list(patterns_dir.glob("*.json")))
        
        # Photo count
        photos_dir = self.brain_dir / "daily-goals"
        if photos_dir.exists():
            photo_count = len(list(photos_dir.glob("*.jpg"))) + len(list(photos_dir.glob("*.png")))
            stats["Daily Photos"] = photo_count
        
        return stats
    
    def create_daily_dashboard(self, sync_results: Dict) -> str:
        """Create a daily dashboard in Obsidian"""
        
        dashboard_path = self.obs_brain / f"{datetime.now():%Y-%m-%d}-dashboard.md"
        
        content = [f"# 📊 Brain Dashboard - {datetime.now():%Y-%m-%d}\n\n"]
        content.append(f"*Generated: {datetime.now():%H:%M:%S}*\n\n")
        
        # Sync Summary
        content.append("## 🔄 Sync Summary\n")
        content.append(f"- Core Files: {sync_results.get('core_files', {}).get('count', 0)}\n")
        content.append(f"- Working Memory: {sync_results.get('working_memory', {}).get('count', 0)}\n")
        content.append(f"- Goals: {sync_results.get('goals', {}).get('goals', 0)}\n")
        content.append(f"- Patterns: {sync_results.get('goals', {}).get('patterns', 0)}\n")
        content.append(f"- Photos: {sync_results.get('photos', {}).get('count', 0)}\n")
        content.append(f"- Sessions: {sync_results.get('sessions', {}).get('count', 0)}\n")
        content.append(f"- People: {sync_results.get('people', {}).get('count', 0)}\n\n")
        
        # Quick Links
        content.append("## 🚀 Quick Actions\n")
        content.append("- [[indexes/MASTER_INDEX|Master Index]]\n")
        content.append("- [[indexes/GOAL_PROGRESS|Goal Progress]]\n")
        content.append("- [[indexes/PATTERN_INSIGHTS|Pattern Insights]]\n")
        content.append("- [[active-goals|Current Goals]]\n\n")
        
        # Today's Focus
        content.append("## 🎯 Today's Focus\n")
        
        # Get today's goals if they exist
        today_goals = self.brain_dir / "daily-goals" / f"{datetime.now():%Y-%m-%d}-goals.json"
        if today_goals.exists():
            with open(today_goals) as f:
                data = json.load(f)
            
            for goal in data.get("goals", []):
                if goal.get("priority") == "high":
                    status = "✅" if goal.get("status") == "completed" else "⏳"
                    content.append(f"- {status} {goal['text']}\n")
        else:
            content.append("- No goals set for today\n")
        
        content.append("\n---\n")
        content.append("Tags: #dashboard #brain-system #daily\n")
        
        dashboard_path.write_text("".join(content))
        
        return str(dashboard_path)

def main():
    """Main entry point for global sync"""
    import sys
    
    syncer = GlobalObsidianSync()
    
    # Check for force flag
    force = "--force" in sys.argv or "-f" in sys.argv
    
    if force:
        print("🔄 FORCE SYNC: Resyncing everything...")
    
    # Run complete sync
    results = syncer.sync_all(force=force)
    
    # Print results
    print("\n✅ Global Obsidian Sync Complete!")
    print("=" * 50)
    
    print(f"\n📁 Synced to: {syncer.obs_brain}")
    
    print("\n📊 Sync Statistics:")
    print(f"  • Core Files: {results['core_files']['count']}")
    print(f"  • Working Memory: {results['working_memory']['count']}")
    print(f"  • Goals: {results['goals']['goals']}")
    print(f"  • Patterns: {results['goals']['patterns']}")
    print(f"  • Photos: {results['photos']['count']}")
    print(f"  • Sessions: {results['sessions']['count']}")
    print(f"  • People: {results['people']['count']}")
    print(f"  • Indexes: {len(results['indexes']['indexes'])}")
    
    print(f"\n📋 Dashboard: {Path(results['dashboard']).name}")
    
    print("\n🔍 Everything is now searchable in Obsidian!")
    print("💡 Use Obsidian's search to find anything")
    
    # Show any errors
    if results.get("errors"):
        print("\n⚠️ Errors encountered:")
        for error in results["errors"]:
            print(f"  • {error}")

if __name__ == "__main__":
    main()