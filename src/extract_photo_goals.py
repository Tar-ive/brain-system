#!/usr/bin/env python3
"""
Daily Photo Goal Extraction System
Processes uploaded photos of daily priorities and tracks goals
Integrates with brain.md's working memory system
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import hashlib

class PhotoGoalExtractor:
    """
    Extracts and tracks goals from daily priority photos
    Following brain.md's cognitive load principles
    """
    
    def __init__(self):
        self.brain_dir = Path("/Users/tarive/brain-poc")
        self.goals_dir = self.brain_dir / "daily-goals"
        self.goals_dir.mkdir(exist_ok=True)
        self.working_memory_limit = 7  # From brain.md
        
        # Load goal keeper for integration
        self.goal_keeper = self._load_goal_keeper()
    
    def _load_goal_keeper(self):
        """Load the existing goal keeper for commitment tracking"""
        import sys
        sys.path.append(str(self.brain_dir))
        try:
            from goal_keeper import GoalKeeper
            return GoalKeeper()
        except ImportError:
            print("Note: goal_keeper.py not found, using standalone mode")
            return None
        
    def process_photo(self, photo_path: Optional[str] = None) -> Dict:
        """
        Process a photo of daily priorities
        If no path provided, looks for today's photo
        """
        
        if not photo_path:
            # Look for today's photo
            today = datetime.now().strftime("%Y-%m-%d")
            photo_path = self.goals_dir / f"{today}.jpg"
            
            if not photo_path.exists():
                # Try PNG format
                photo_path = self.goals_dir / f"{today}.png"
            
            if not photo_path.exists():
                return {
                    "error": f"No photo found for today ({today})",
                    "expected_path": str(self.goals_dir / f"{today}.jpg")
                }
        
        photo_path = Path(photo_path)
        
        if not photo_path.exists():
            return {"error": f"Photo not found: {photo_path}"}
        
        # Extract text from photo (simulated for now)
        # In production, this would use OCR (Tesseract, Vision API, etc.)
        goals_data = self.extract_goals_from_photo(photo_path)
        
        # Save extracted goals
        self.save_goals(goals_data)
        
        # Update working memory with today's goals
        self.update_working_memory(goals_data)
        
        # Integrate with goal keeper if available
        if self.goal_keeper:
            self._integrate_with_goal_keeper(goals_data)
        
        # Create progress tracking file
        self.create_progress_tracker(goals_data)
        
        return goals_data
    
    def _integrate_with_goal_keeper(self, goals_data: Dict):
        """Integrate extracted goals with goal keeper for commitment tracking"""
        try:
            # Add high priority goals as next actions
            for goal in goals_data.get("goals", []):
                if goal["priority"] == "high":
                    # Check if brain_system project exists
                    if "brain_system" in self.goal_keeper.goals:
                        # Add to next actions if not already there
                        next_actions = self.goal_keeper.goals["brain_system"].get("next_actions", [])
                        if goal["text"] not in next_actions:
                            self.goal_keeper.goals["brain_system"]["next_actions"].append(goal["text"])
                    
                    # Log as a potential win when completed
                    goal["goal_keeper_tracked"] = True
            
            # Save goal keeper state
            self.goal_keeper._save_goals()
            print("✅ Integrated with Goal Keeper for commitment tracking")
        except Exception as e:
            print(f"Note: Could not integrate with goal keeper: {e}")
    
    def extract_goals_from_photo(self, photo_path: Path) -> Dict:
        """
        Extract goals from photo (placeholder for OCR implementation)
        In production, this would use:
        - pytesseract for OCR
        - OpenCV for image preprocessing
        - Or cloud vision APIs
        """
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # For POC, create a template structure
        # Real implementation would extract text from image
        goals = {
            "date": today,
            "photo_path": str(photo_path),
            "photo_hash": self.get_file_hash(photo_path),
            "extracted_at": datetime.now().isoformat(),
            "goals": [
                {
                    "id": f"goal_{today}_1",
                    "text": "Complete brain POC documentation",
                    "priority": "high",
                    "status": "pending",
                    "category": "work"
                },
                {
                    "id": f"goal_{today}_2",
                    "text": "4pm meeting with Dr. Tahir",
                    "priority": "high",
                    "status": "pending",
                    "category": "meetings"
                },
                {
                    "id": f"goal_{today}_3",
                    "text": "Send work update to Dr. Ekren",
                    "priority": "medium",
                    "status": "pending",
                    "category": "communication"
                }
            ],
            "metadata": {
                "total_goals": 3,
                "high_priority": 2,
                "medium_priority": 1,
                "low_priority": 0
            }
        }
        
        # If we can read from a manual entry file
        manual_entry = self.goals_dir / f"{today}-manual.json"
        if manual_entry.exists():
            with open(manual_entry) as f:
                manual_goals = json.load(f)
                goals["goals"] = manual_goals.get("goals", goals["goals"])
                goals["metadata"]["manual_entry"] = True
        
        return goals
    
    def get_file_hash(self, file_path: Path) -> str:
        """Get SHA256 hash of file for tracking changes"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()[:16]  # Short hash
    
    def save_goals(self, goals_data: Dict):
        """Save extracted goals to JSON"""
        
        date = goals_data["date"]
        goals_file = self.goals_dir / f"{date}-goals.json"
        
        # Save goals
        with open(goals_file, 'w') as f:
            json.dump(goals_data, f, indent=2)
        
        print(f"✅ Goals saved to: {goals_file}")
    
    def update_working_memory(self, goals_data: Dict):
        """
        Update working memory with high-priority goals
        Respects the 7-item limit from brain.md
        """
        
        high_priority_goals = [
            g for g in goals_data["goals"] 
            if g["priority"] == "high"
        ][:3]  # Max 3 high priority goals to leave room for other items
        
        for goal in high_priority_goals:
            # Store in working memory with high importance
            memory_item = {
                "content": f"Daily Goal: {goal['text']}",
                "type": "daily_goal",
                "importance": 0.9,  # High importance for daily goals
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "goal_id": goal["id"],
                    "category": goal["category"],
                    "from_photo": True
                }
            }
            
            # Store using POC scoring system
            try:
                subprocess.run(
                    ["python3", "/Users/tarive/brain-poc/scripts/poc_scoring.py", 
                     "store", json.dumps(memory_item)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            except Exception as e:
                print(f"⚠️ Could not update working memory: {e}")
    
    def create_progress_tracker(self, goals_data: Dict):
        """Create a markdown file for tracking progress"""
        
        date = goals_data["date"]
        progress_file = self.goals_dir / f"{date}-progress.md"
        
        content = f"""# Daily Goals Progress - {date}

## Photo Analysis
- **Photo**: {goals_data['photo_path']}
- **Extracted**: {goals_data['extracted_at']}
- **Total Goals**: {goals_data['metadata']['total_goals']}

## Priority Breakdown
- 🔴 High Priority: {goals_data['metadata']['high_priority']}
- 🟡 Medium Priority: {goals_data['metadata']['medium_priority']}
- 🟢 Low Priority: {goals_data['metadata']['low_priority']}

## Goals Tracking

"""
        
        for goal in goals_data["goals"]:
            priority_emoji = {
                "high": "🔴",
                "medium": "🟡", 
                "low": "🟢"
            }.get(goal["priority"], "⚪")
            
            status_mark = "☐" if goal["status"] == "pending" else "☑"
            
            content += f"""### {status_mark} {goal['text']}
- **Priority**: {priority_emoji} {goal['priority'].capitalize()}
- **Category**: {goal['category']}
- **Status**: {goal['status']}
- **ID**: `{goal['id']}`

---

"""
        
        content += f"""
## Progress Updates

_Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_

### Morning Review
- [ ] Reviewed daily goals
- [ ] Prioritized tasks
- [ ] Blocked time for high-priority items

### Midday Check-in
- [ ] Progress on high-priority goals
- [ ] Adjustments needed?

### Evening Review
- [ ] Goals completed
- [ ] Lessons learned
- [ ] Tomorrow's priorities

## Notes
_Add any additional notes or context here_

---
*Generated by Brain POC Goal Tracking System*
"""
        
        with open(progress_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Progress tracker created: {progress_file}")
        
        # Also sync to Obsidian
        self.sync_to_obsidian(goals_data, content)
    
    def sync_to_obsidian(self, goals_data: Dict, progress_content: str):
        """Sync goals to Obsidian vault"""
        
        obsidian_daily = Path("/Users/tarive/Library/Mobile Documents/iCloud~md~obsidian/Documents/Saksham/daily")
        
        if obsidian_daily.exists():
            date = goals_data["date"]
            obsidian_goals = obsidian_daily / f"{date}-photo-goals.md"
            
            with open(obsidian_goals, 'w') as f:
                f.write(progress_content)
            
            print(f"✅ Synced to Obsidian: {obsidian_goals.name}")
    
    def update_goal_status(self, goal_id: str, new_status: str) -> bool:
        """Update the status of a specific goal"""
        
        # Find today's goals file
        today = datetime.now().strftime("%Y-%m-%d")
        goals_file = self.goals_dir / f"{today}-goals.json"
        
        if not goals_file.exists():
            print(f"❌ No goals file for today: {goals_file}")
            return False
        
        # Load goals
        with open(goals_file) as f:
            goals_data = json.load(f)
        
        # Update status
        updated = False
        for goal in goals_data["goals"]:
            if goal["id"] == goal_id:
                goal["status"] = new_status
                goal["updated_at"] = datetime.now().isoformat()
                updated = True
                break
        
        if updated:
            # Save updated goals
            with open(goals_file, 'w') as f:
                json.dump(goals_data, f, indent=2)
            
            # Recreate progress tracker
            self.create_progress_tracker(goals_data)
            
            print(f"✅ Updated goal {goal_id} to status: {new_status}")
            return True
        else:
            print(f"❌ Goal not found: {goal_id}")
            return False
    
    def get_today_status(self) -> Dict:
        """Get status of today's goals"""
        
        today = datetime.now().strftime("%Y-%m-%d")
        goals_file = self.goals_dir / f"{today}-goals.json"
        
        if not goals_file.exists():
            return {
                "date": today,
                "status": "no_goals",
                "message": "No goals set for today. Upload a photo to get started."
            }
        
        with open(goals_file) as f:
            goals_data = json.load(f)
        
        # Calculate completion
        total = len(goals_data["goals"])
        completed = sum(1 for g in goals_data["goals"] if g["status"] == "completed")
        in_progress = sum(1 for g in goals_data["goals"] if g["status"] == "in_progress")
        pending = sum(1 for g in goals_data["goals"] if g["status"] == "pending")
        
        return {
            "date": today,
            "status": "active",
            "total_goals": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "completion_rate": f"{(completed/total)*100:.0f}%" if total > 0 else "0%",
            "goals": goals_data["goals"]
        }

def main():
    """Main entry point for photo goal extraction"""
    
    extractor = PhotoGoalExtractor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            # Show today's goal status
            status = extractor.get_today_status()
            print(f"\n📅 Daily Goals Status - {status['date']}")
            print("=" * 50)
            
            if status["status"] == "no_goals":
                print(status["message"])
            else:
                print(f"Total Goals: {status['total_goals']}")
                print(f"✅ Completed: {status['completed']}")
                print(f"🔄 In Progress: {status['in_progress']}")
                print(f"⏳ Pending: {status['pending']}")
                print(f"📊 Completion: {status['completion_rate']}")
                
                print("\nGoals:")
                for goal in status["goals"]:
                    status_icon = {
                        "completed": "✅",
                        "in_progress": "🔄",
                        "pending": "⏳"
                    }.get(goal["status"], "❓")
                    
                    print(f"  {status_icon} {goal['text']}")
        
        elif command == "update" and len(sys.argv) >= 4:
            # Update goal status
            goal_id = sys.argv[2]
            new_status = sys.argv[3]
            extractor.update_goal_status(goal_id, new_status)
        
        elif command == "extract" and len(sys.argv) >= 3:
            # Extract from specific photo
            photo_path = sys.argv[2]
            result = extractor.process_photo(photo_path)
            
            if "error" in result:
                print(f"❌ {result['error']}")
            else:
                print(f"✅ Extracted {len(result['goals'])} goals from photo")
        
        else:
            # Process today's photo
            result = extractor.process_photo()
            
            if "error" in result:
                print(f"❌ {result['error']}")
                if "expected_path" in result:
                    print(f"📸 Please save your daily photo to: {result['expected_path']}")
            else:
                print(f"✅ Processed {len(result['goals'])} goals for today")
    
    else:
        # Default: process today's photo
        result = extractor.process_photo()
        
        if "error" in result:
            print(f"❌ {result['error']}")
            if "expected_path" in result:
                print(f"📸 Please save your daily photo to: {result['expected_path']}")
        else:
            print(f"✅ Processed {len(result['goals'])} goals for today")
            print("\n📊 Goal Summary:")
            for goal in result["goals"]:
                print(f"  - {goal['text']} ({goal['priority']})")
            
            print(f"\n📝 Progress tracker: daily-goals/{result['date']}-progress.md")
            print(f"💾 Goals data: daily-goals/{result['date']}-goals.json")

if __name__ == "__main__":
    main()