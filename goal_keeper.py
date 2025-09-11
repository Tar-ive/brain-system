#!/usr/bin/env python3
"""
Goal Keeper - The brain system that keeps you committed
Built specifically to prevent project abandonment
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import subprocess

class GoalKeeper:
    def __init__(self):
        self.brain_dir = Path("/Users/tarive/brain-poc")
        self.goals_file = self.brain_dir / "active_goals.json"
        self.wins_file = self.brain_dir / "wins_log.json"
        self.commitment_file = self.brain_dir / "commitment.json"
        
        # Load or initialize
        self.goals = self._load_goals()
        self.wins = self._load_wins()
        self.commitment = self._load_commitment()
    
    def _load_goals(self) -> Dict:
        """Load active goals"""
        if self.goals_file.exists():
            with open(self.goals_file) as f:
                return json.load(f)
        return {
            "brain_system": {
                "started": datetime.now().isoformat(),
                "status": "active",
                "excitement_level": 10,
                "days_worked": 0,
                "last_win": None,
                "commitment": "Build this to the core - no abandonment",
                "next_actions": [],
                "blockers": []
            }
        }
    
    def _load_wins(self) -> List:
        """Load wins history for dopamine tracking"""
        if self.wins_file.exists():
            with open(self.wins_file) as f:
                return json.load(f)
        return []
    
    def _load_commitment(self) -> Dict:
        """Load commitment contract"""
        if self.commitment_file.exists():
            with open(self.commitment_file) as f:
                return json.load(f)
        return {
            "brain_project": {
                "promise": "I will NOT abandon this project when things break",
                "signed": datetime.now().isoformat(),
                "minimum_days": 30,
                "fallback_plan": "If something breaks, fix it simply, don't rebuild"
            }
        }
    
    def add_goal(self, project: str, goal: str, why_excited: str):
        """Add a new goal/project to track"""
        self.goals[project] = {
            "goal": goal,
            "why_excited": why_excited,
            "started": datetime.now().isoformat(),
            "status": "active",
            "excitement_level": 10,
            "days_worked": 0,
            "last_win": None,
            "next_actions": [],
            "blockers": []
        }
        self._save_goals()
        return f"🎯 Goal added: {project}"
    
    def log_win(self, project: str, win: str, excitement_boost: int = 1):
        """Log a win to maintain momentum"""
        if project not in self.goals:
            return f"❌ Project {project} not found"
        
        win_entry = {
            "project": project,
            "win": win,
            "timestamp": datetime.now().isoformat(),
            "excitement_before": self.goals[project]["excitement_level"],
            "excitement_after": min(10, self.goals[project]["excitement_level"] + excitement_boost)
        }
        
        self.wins.append(win_entry)
        self.goals[project]["last_win"] = datetime.now().isoformat()
        self.goals[project]["excitement_level"] = win_entry["excitement_after"]
        self.goals[project]["days_worked"] += 1
        
        self._save_wins()
        self._save_goals()
        
        # DEEP SYNC TO OBSIDIAN
        try:
            from obsidian_deep_sync import deep_sync_everything
            deep_sync_everything()
        except:
            pass
        
        # Dopamine reward message
        streak = self.goals[project]["days_worked"]
        return f"""
🎉 WIN LOGGED for {project}!
✨ {win}
🔥 Excitement: {win_entry['excitement_before']} → {win_entry['excitement_after']}
📈 Streak: {streak} days
{'🏆 MILESTONE!' if streak % 7 == 0 else ''}
"""
    
    def log_blocker(self, project: str, blocker: str, severity: int = 5):
        """Log a blocker WITHOUT abandoning"""
        if project not in self.goals:
            return f"❌ Project {project} not found"
        
        self.goals[project]["blockers"].append({
            "issue": blocker,
            "severity": severity,
            "logged": datetime.now().isoformat(),
            "resolved": False
        })
        
        # Decrease excitement but not below 3 (commitment threshold)
        self.goals[project]["excitement_level"] = max(3, 
            self.goals[project]["excitement_level"] - (severity / 10))
        
        self._save_goals()
        
        # Anti-abandonment message
        commitment_days = self._get_commitment_days(project)
        return f"""
⚠️ BLOCKER LOGGED for {project}
🚧 {blocker} (severity: {severity}/10)
💪 Your commitment: {self.commitment.get(project, {}).get('promise', 'Keep going!')}
📅 You've invested {commitment_days} days - don't quit now!

Quick fixes to try:
1. Simplify the solution
2. Ask for help
3. Take a break and come back
4. Fix just this one thing, ignore perfection
"""
    
    def resolve_blocker(self, project: str, blocker_index: int = -1):
        """Resolve a blocker and get excitement back"""
        if project not in self.goals:
            return f"❌ Project {project} not found"
        
        if self.goals[project]["blockers"]:
            blocker = self.goals[project]["blockers"][blocker_index]
            blocker["resolved"] = True
            blocker["resolved_at"] = datetime.now().isoformat()
            
            # Excitement boost for overcoming challenges!
            self.goals[project]["excitement_level"] = min(10,
                self.goals[project]["excitement_level"] + 2)
            
            self._save_goals()
            
            return f"""
✅ BLOCKER RESOLVED!
🎯 {blocker['issue']}
💪 You pushed through instead of quitting!
🔥 Excitement restored to {self.goals[project]['excitement_level']}/10
"""
        return "No blockers to resolve"
    
    def daily_check(self):
        """Daily accountability check"""
        report = ["=" * 50]
        report.append("🧠 DAILY GOAL CHECK")
        report.append("=" * 50)
        
        for project, data in self.goals.items():
            if data["status"] != "active":
                continue
                
            days = self._get_commitment_days(project)
            last_win_days = self._days_since_last_win(project)
            
            # Excitement decay if no recent wins
            if last_win_days > 3:
                data["excitement_level"] = max(1, data["excitement_level"] - 1)
            
            status_emoji = "🟢" if data["excitement_level"] > 7 else "🟡" if data["excitement_level"] > 4 else "🔴"
            
            report.append(f"\n{status_emoji} {project.upper()}")
            report.append(f"   Days committed: {days}")
            report.append(f"   Excitement: {'🔥' * data['excitement_level']}")
            report.append(f"   Last win: {last_win_days} days ago")
            
            if data["blockers"]:
                unresolved = [b for b in data["blockers"] if not b.get("resolved")]
                if unresolved:
                    report.append(f"   ⚠️ {len(unresolved)} unresolved blockers")
            
            if last_win_days > 2:
                report.append(f"   💡 Need a win! Even a small one counts!")
        
        report.append("\n" + "=" * 50)
        report.append("Remember: Commitment > Excitement")
        report.append("=" * 50)
        
        self._save_goals()
        return "\n".join(report)
    
    def _get_commitment_days(self, project: str) -> int:
        """Get days committed to project"""
        if project in self.goals:
            start = datetime.fromisoformat(self.goals[project]["started"])
            return (datetime.now() - start).days
        return 0
    
    def _days_since_last_win(self, project: str) -> int:
        """Days since last win"""
        if project in self.goals and self.goals[project]["last_win"]:
            last_win = datetime.fromisoformat(self.goals[project]["last_win"])
            return (datetime.now() - last_win).days
        return 999
    
    def _save_goals(self):
        with open(self.goals_file, 'w') as f:
            json.dump(self.goals, f, indent=2)
    
    def _save_wins(self):
        with open(self.wins_file, 'w') as f:
            json.dump(self.wins, f, indent=2)
    
    def get_next_action(self, project: str = "brain_system"):
        """What should I do next?"""
        if project not in self.goals:
            return "Project not found"
        
        data = self.goals[project]
        
        # If blocked, focus on unblocking
        unresolved = [b for b in data.get("blockers", []) if not b.get("resolved")]
        if unresolved:
            return f"🚧 FIX BLOCKER: {unresolved[0]['issue']}\n(Don't abandon! Simplify the solution!)"
        
        # If no recent wins, get a quick win
        if self._days_since_last_win(project) > 1:
            return "🎯 GET A QUICK WIN: Do something small that works!\nExamples: Fix one bug, add one feature, write one test"
        
        # Normal flow
        if data.get("next_actions"):
            return f"➡️ NEXT: {data['next_actions'][0]}"
        
        return "✨ Add your next action with: keeper.add_next_action()"

def main():
    import sys
    keeper = GoalKeeper()
    
    if len(sys.argv) < 2:
        print("Goal Keeper - Stop abandoning projects!")
        print("Commands:")
        print("  win <description>     - Log a win")
        print("  blocker <description> - Log a blocker") 
        print("  resolve              - Resolve last blocker")
        print("  check                - Daily accountability")
        print("  next                 - What to do next")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "win":
        desc = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Made progress!"
        print(keeper.log_win("brain_system", desc))
    
    elif cmd == "blocker":
        desc = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Something broke"
        print(keeper.log_blocker("brain_system", desc))
    
    elif cmd == "resolve":
        print(keeper.resolve_blocker("brain_system"))
    
    elif cmd == "check":
        print(keeper.daily_check())
    
    elif cmd == "next":
        print(keeper.get_next_action())

if __name__ == "__main__":
    main()