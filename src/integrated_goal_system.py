#!/usr/bin/env python3
"""
Integrated Goal System - Combines goal_keeper, photo extraction, and pattern search
Unified system for goal tracking with pattern detection and insights
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import subprocess
import hashlib
from collections import defaultdict

class IntegratedGoalSystem:
    """
    Unified goal tracking with:
    1. Goal Keeper for commitment tracking
    2. Photo extraction for daily priorities
    3. Pattern detection for insights
    4. Brain integration for context
    """
    
    def __init__(self):
        self.brain_dir = Path("/Users/tarive/brain-poc")
        self.goals_dir = self.brain_dir / "daily-goals"
        self.patterns_dir = self.brain_dir / "patterns"
        self.goals_dir.mkdir(exist_ok=True)
        self.patterns_dir.mkdir(exist_ok=True)
        
        # Load existing goal keeper
        self.goal_keeper = self._load_goal_keeper()
        
        # Pattern detection settings
        self.pattern_window = 7  # Days to look back for patterns
        self.min_pattern_occurrences = 3  # Minimum times to count as pattern
        
    def _load_goal_keeper(self):
        """Load the existing goal keeper"""
        import sys
        sys.path.append(str(self.brain_dir))
        try:
            from goal_keeper import GoalKeeper
            return GoalKeeper()
        except ImportError:
            print("Warning: goal_keeper.py not found, using basic tracking")
            return None
    
    def extract_goals_from_photo(self, photo_path: Optional[str] = None) -> Dict:
        """
        Extract goals from photo and integrate with goal keeper
        """
        if not photo_path:
            today = datetime.now().strftime("%Y-%m-%d")
            photo_path = self.goals_dir / f"{today}.jpg"
            if not photo_path.exists():
                photo_path = self.goals_dir / f"{today}.png"
        
        photo_path = Path(photo_path)
        
        if not photo_path.exists():
            return {
                "error": f"No photo found: {photo_path}",
                "suggestion": "Upload your daily photo to track goals"
            }
        
        # Extract goals (placeholder for OCR)
        goals = self._ocr_extract(photo_path)
        
        # Integrate with goal keeper
        if self.goal_keeper:
            for goal in goals.get("goals", []):
                if goal["priority"] == "high":
                    # Log as next action in goal keeper
                    self.goal_keeper.goals["brain_system"]["next_actions"].append(goal["text"])
            self.goal_keeper._save_goals()
        
        # Detect patterns in goals
        patterns = self.detect_goal_patterns(goals)
        goals["patterns"] = patterns
        
        # Save everything
        self._save_goals_with_patterns(goals)
        
        return goals
    
    def _ocr_extract(self, photo_path: Path) -> Dict:
        """
        Placeholder for OCR extraction
        In production: Use pytesseract or cloud vision API
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Check for manual entry
        manual_file = self.goals_dir / f"{today}-manual.txt"
        if manual_file.exists():
            with open(manual_file) as f:
                lines = f.readlines()
            
            goals = []
            for i, line in enumerate(lines):
                line = line.strip()
                if line:
                    priority = "high" if any(word in line.lower() for word in ["urgent", "important", "asap"]) else "medium"
                    goals.append({
                        "id": f"goal_{today}_{i+1}",
                        "text": line,
                        "priority": priority,
                        "status": "pending",
                        "category": self._categorize_goal(line)
                    })
            
            return {
                "date": today,
                "photo_path": str(photo_path),
                "extracted_at": datetime.now().isoformat(),
                "goals": goals,
                "metadata": {
                    "total_goals": len(goals),
                    "source": "manual_entry"
                }
            }
        
        # Default goals for demo
        return {
            "date": today,
            "photo_path": str(photo_path),
            "extracted_at": datetime.now().isoformat(),
            "goals": [
                {
                    "id": f"goal_{today}_1",
                    "text": "Complete brain POC integration",
                    "priority": "high",
                    "status": "pending",
                    "category": "development"
                }
            ],
            "metadata": {"total_goals": 1}
        }
    
    def _categorize_goal(self, text: str) -> str:
        """Categorize goal based on keywords"""
        text_lower = text.lower()
        
        categories = {
            "meeting": ["meeting", "call", "sync", "discussion"],
            "development": ["code", "implement", "build", "fix", "debug"],
            "communication": ["email", "message", "reply", "send", "contact"],
            "planning": ["plan", "design", "architecture", "strategy"],
            "research": ["research", "analyze", "study", "investigate"],
            "personal": ["personal", "home", "family", "health"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return "general"
    
    def detect_goal_patterns(self, current_goals: Dict) -> Dict:
        """
        Detect patterns in goals over time
        Returns insights about recurring themes, time patterns, etc.
        """
        patterns = {
            "recurring_themes": [],
            "time_patterns": [],
            "category_distribution": {},
            "completion_patterns": [],
            "insights": []
        }
        
        # Load historical goals
        historical = self._load_historical_goals()
        
        # 1. Detect recurring themes
        theme_counts = defaultdict(int)
        for hist_goals in historical:
            for goal in hist_goals.get("goals", []):
                # Extract key phrases
                key_phrases = self._extract_key_phrases(goal["text"])
                for phrase in key_phrases:
                    theme_counts[phrase] += 1
        
        # Find patterns that occur frequently
        for theme, count in theme_counts.items():
            if count >= self.min_pattern_occurrences:
                patterns["recurring_themes"].append({
                    "theme": theme,
                    "frequency": count,
                    "insight": f"'{theme}' appears {count} times in last {self.pattern_window} days"
                })
        
        # 2. Time patterns (what gets done when)
        completion_by_hour = defaultdict(list)
        for hist_goals in historical:
            for goal in hist_goals.get("goals", []):
                if goal.get("completed_at"):
                    hour = datetime.fromisoformat(goal["completed_at"]).hour
                    completion_by_hour[hour].append(goal["category"])
        
        if completion_by_hour:
            most_productive_hour = max(completion_by_hour.keys(), 
                                     key=lambda h: len(completion_by_hour[h]))
            patterns["time_patterns"].append({
                "pattern": "most_productive_hour",
                "value": most_productive_hour,
                "insight": f"You complete most tasks around {most_productive_hour}:00"
            })
        
        # 3. Category distribution
        category_counts = defaultdict(int)
        for goal in current_goals.get("goals", []):
            category_counts[goal["category"]] += 1
        
        total = sum(category_counts.values())
        for category, count in category_counts.items():
            patterns["category_distribution"][category] = {
                "count": count,
                "percentage": f"{(count/total)*100:.0f}%"
            }
        
        # 4. Completion patterns
        if historical:
            completion_rates = []
            for hist_goals in historical[-7:]:  # Last week
                goals = hist_goals.get("goals", [])
                if goals:
                    completed = sum(1 for g in goals if g.get("status") == "completed")
                    rate = completed / len(goals)
                    completion_rates.append(rate)
            
            if completion_rates:
                avg_completion = sum(completion_rates) / len(completion_rates)
                patterns["completion_patterns"].append({
                    "average_completion_rate": f"{avg_completion*100:.0f}%",
                    "trend": "improving" if completion_rates[-1] > avg_completion else "declining"
                })
        
        # 5. Generate insights
        patterns["insights"] = self._generate_insights(patterns, current_goals)
        
        return patterns
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from goal text"""
        # Remove common words
        stop_words = {"the", "a", "an", "to", "for", "and", "or", "but", "in", "on", "at", "with"}
        
        # Simple extraction: 2-3 word phrases
        words = text.lower().split()
        words = [w for w in words if w not in stop_words]
        
        phrases = []
        for i in range(len(words) - 1):
            # Two-word phrases
            phrase = f"{words[i]} {words[i+1]}"
            if len(phrase) > 5:  # Minimum length
                phrases.append(phrase)
        
        return phrases
    
    def _load_historical_goals(self) -> List[Dict]:
        """Load historical goals from the last N days"""
        historical = []
        
        for days_back in range(self.pattern_window):
            date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            goals_file = self.goals_dir / f"{date}-goals.json"
            
            if goals_file.exists():
                with open(goals_file) as f:
                    historical.append(json.load(f))
        
        return historical
    
    def _generate_insights(self, patterns: Dict, current_goals: Dict) -> List[str]:
        """Generate actionable insights from patterns"""
        insights = []
        
        # Insight 1: Recurring themes
        if patterns["recurring_themes"]:
            top_theme = patterns["recurring_themes"][0]
            insights.append(f"💡 '{top_theme['theme']}' is a recurring focus area - consider batching these tasks")
        
        # Insight 2: Category balance
        if patterns["category_distribution"]:
            categories = patterns["category_distribution"]
            if "meeting" in categories and categories["meeting"]["count"] > len(current_goals.get("goals", [])) * 0.5:
                insights.append("📅 Heavy meeting day - block time for deep work")
            
            if "development" in categories and "meeting" in categories:
                insights.append("⚖️ Balance of coding and meetings - schedule focused blocks")
        
        # Insight 3: Completion patterns
        if patterns["completion_patterns"]:
            comp = patterns["completion_patterns"][0]
            if comp["trend"] == "declining":
                insights.append("📉 Completion rate declining - consider reducing daily goals")
            else:
                insights.append(f"📈 Great momentum! {comp['average_completion_rate']} completion rate")
        
        # Insight 4: Time optimization
        if patterns["time_patterns"]:
            hour = patterns["time_patterns"][0]["value"]
            insights.append(f"⏰ Schedule important tasks around {hour}:00 (your peak productivity)")
        
        return insights
    
    def _save_goals_with_patterns(self, goals_data: Dict):
        """Save goals with pattern analysis"""
        date = goals_data["date"]
        
        # Save goals file
        goals_file = self.goals_dir / f"{date}-goals.json"
        with open(goals_file, 'w') as f:
            json.dump(goals_data, f, indent=2)
        
        # Save patterns separately for analysis
        if "patterns" in goals_data:
            patterns_file = self.patterns_dir / f"{date}-patterns.json"
            with open(patterns_file, 'w') as f:
                json.dump(goals_data["patterns"], f, indent=2)
        
        print(f"✅ Goals and patterns saved for {date}")
    
    def search_patterns(self, query: str) -> Dict:
        """
        Search for patterns in goals and brain content
        Uses the brain's semantic search plus pattern detection
        """
        results = {
            "query": query,
            "goal_patterns": [],
            "brain_patterns": [],
            "insights": []
        }
        
        # Search in historical goals
        historical = self._load_historical_goals()
        query_lower = query.lower()
        
        for hist in historical:
            for goal in hist.get("goals", []):
                if query_lower in goal["text"].lower():
                    results["goal_patterns"].append({
                        "date": hist["date"],
                        "goal": goal["text"],
                        "status": goal.get("status", "unknown"),
                        "category": goal.get("category", "general")
                    })
        
        # Search in brain using bf command
        try:
            result = subprocess.run(
                ["~/bin/bf", query],
                capture_output=True,
                text=True,
                shell=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout:
                # Parse brain search results
                brain_results = result.stdout.strip().split('\n')
                for line in brain_results[:5]:  # Top 5 results
                    if line.strip():
                        results["brain_patterns"].append(line.strip())
        except Exception as e:
            print(f"Brain search error: {e}")
        
        # Generate pattern insights
        if results["goal_patterns"]:
            # Analyze frequency
            freq = len(results["goal_patterns"])
            results["insights"].append(f"Found '{query}' in {freq} previous goals")
            
            # Analyze completion rate
            completed = sum(1 for p in results["goal_patterns"] if p["status"] == "completed")
            if freq > 0:
                completion_rate = (completed / freq) * 100
                results["insights"].append(f"Historical completion rate: {completion_rate:.0f}%")
            
            # Category analysis
            categories = defaultdict(int)
            for p in results["goal_patterns"]:
                categories[p["category"]] += 1
            
            if categories:
                top_category = max(categories.items(), key=lambda x: x[1])
                results["insights"].append(f"Usually categorized as: {top_category[0]}")
        
        return results
    
    def get_daily_summary(self) -> str:
        """Get comprehensive daily summary with patterns"""
        summary = ["=" * 60]
        summary.append("🧠 INTEGRATED GOAL SYSTEM - DAILY SUMMARY")
        summary.append("=" * 60)
        
        # Today's goals
        today = datetime.now().strftime("%Y-%m-%d")
        goals_file = self.goals_dir / f"{today}-goals.json"
        
        if goals_file.exists():
            with open(goals_file) as f:
                goals = json.load(f)
            
            summary.append(f"\n📅 TODAY'S GOALS ({today})")
            summary.append("-" * 40)
            
            for goal in goals.get("goals", []):
                status_icon = "✅" if goal["status"] == "completed" else "⏳"
                priority_icon = "🔴" if goal["priority"] == "high" else "🟡"
                summary.append(f"{status_icon} {priority_icon} {goal['text']}")
            
            # Show patterns if available
            if "patterns" in goals:
                summary.append("\n🔍 DETECTED PATTERNS")
                summary.append("-" * 40)
                
                patterns = goals["patterns"]
                
                # Recurring themes
                if patterns.get("recurring_themes"):
                    summary.append("Recurring Themes:")
                    for theme in patterns["recurring_themes"][:3]:
                        summary.append(f"  • {theme['theme']} ({theme['frequency']}x)")
                
                # Insights
                if patterns.get("insights"):
                    summary.append("\n💡 INSIGHTS")
                    for insight in patterns["insights"]:
                        summary.append(f"  {insight}")
        
        # Goal Keeper status
        if self.goal_keeper:
            summary.append("\n🎯 GOAL KEEPER STATUS")
            summary.append("-" * 40)
            
            for project, data in self.goal_keeper.goals.items():
                if data["status"] == "active":
                    summary.append(f"{project}: {'🔥' * data['excitement_level']} (Day {data['days_worked']})")
        
        # Brain working memory status
        try:
            result = subprocess.run(
                ["python3", f"{self.brain_dir}/scripts/poc_scoring.py", "status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split('\n')
                summary.append("\n📊 WORKING MEMORY")
                summary.append("-" * 40)
                for line in lines[:3]:  # First 3 lines
                    if "Items:" in line:
                        summary.append(line.strip())
        except:
            pass
        
        summary.append("\n" + "=" * 60)
        return "\n".join(summary)

def main():
    """Main entry point"""
    import sys
    
    system = IntegratedGoalSystem()
    
    if len(sys.argv) < 2:
        print("Integrated Goal System - Unified tracking with patterns")
        print("\nCommands:")
        print("  extract [photo]  - Extract goals from photo")
        print("  pattern <query>  - Search for patterns")
        print("  summary         - Daily summary with insights")
        print("  search <query>  - Search patterns in goals and brain")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "extract":
        photo = sys.argv[2] if len(sys.argv) > 2 else None
        result = system.extract_goals_from_photo(photo)
        
        if "error" in result:
            print(f"❌ {result['error']}")
        else:
            print(f"✅ Extracted {len(result['goals'])} goals")
            
            if "patterns" in result and result["patterns"]["insights"]:
                print("\n💡 Insights:")
                for insight in result["patterns"]["insights"]:
                    print(f"  {insight}")
    
    elif cmd == "pattern" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        patterns = system.detect_goal_patterns({"goals": []})
        
        print(f"\n🔍 Pattern Analysis for '{query}'")
        print("=" * 40)
        
        if patterns["recurring_themes"]:
            print("\nRecurring Themes:")
            for theme in patterns["recurring_themes"]:
                if query.lower() in theme["theme"]:
                    print(f"  • {theme['insight']}")
    
    elif cmd == "search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        results = system.search_patterns(query)
        
        print(f"\n🔍 Pattern Search: '{query}'")
        print("=" * 40)
        
        if results["goal_patterns"]:
            print(f"\nFound in {len(results['goal_patterns'])} previous goals:")
            for pattern in results["goal_patterns"][:5]:
                print(f"  • {pattern['date']}: {pattern['goal']} [{pattern['status']}]")
        
        if results["brain_patterns"]:
            print(f"\nBrain memory matches:")
            for pattern in results["brain_patterns"]:
                print(f"  • {pattern}")
        
        if results["insights"]:
            print("\nInsights:")
            for insight in results["insights"]:
                print(f"  💡 {insight}")
    
    elif cmd == "summary":
        print(system.get_daily_summary())
    
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()