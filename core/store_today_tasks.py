#!/usr/bin/env python3
"""
Store today's tasks with entity recognition
Picking up patterns from user's writing style
"""

import sys
import json
from datetime import datetime, timezone
sys.path.append('/Users/tarive/brain-poc/scripts')
sys.path.append('/Users/tarive/brain-poc')

from improved_scoring import ImprovedBrainScoring
from store_to_project import ProjectAwareStorage

# Initialize systems
storage = ProjectAwareStorage()
brain = ImprovedBrainScoring()

# Named entities detected (learning from patterns)
ENTITIES = {
    "cathy": {"type": "person", "context": "unknown"},
    "dr_ekren": {"type": "person", "context": "academic", "project": "dci-analysis"},
    "claude_web": {"type": "ai_agent", "context": "idea_generation"},
    "baby": {"type": "person", "context": "personal", "canonical": "girlfriend"},
    "harshal": {"type": "person", "context": "unknown"}
}

# Store today's tasks
tasks = [
    {
        "content": "Reply to Cathy today",
        "context": {
            "type": "task",
            "action": "reply",
            "person": "cathy",
            "deadline": "today",
            "status": "pending"
        },
        "project_id": "personal",  # Assuming personal unless corrected
        "tags": ["communication", "reply", "cathy", "today"],
        "importance_score": 0.7
    },
    {
        "content": "Send work update to Dr. Ekren about dci-analysis project progress",
        "context": {
            "type": "task",
            "action": "send_update",
            "person": "dr_ekren",
            "project": "dci-analysis",
            "deadline": "today",
            "status": "pending"
        },
        "project_id": "dci-analysis",
        "tags": ["work", "update", "dr-ekren", "dci-analysis", "today"],
        "importance_score": 0.8
    },
    {
        "content": "Check out and validate the job_dread_mvp idea that claude_web suggested",
        "context": {
            "type": "task",
            "action": "validate_idea",
            "source": "claude_web",
            "idea_name": "job_dread_mvp",
            "deadline": "today",
            "status": "pending"
        },
        "project_id": "personal",  # New ideas/projects go to personal
        "tags": ["idea-validation", "claude-web", "job-dread-mvp", "startup", "today"],
        "importance_score": 0.75
    },
    {
        "content": "Reply to Harshal",
        "context": {
            "type": "task",
            "action": "reply",
            "person": "harshal",
            "deadline": "today",
            "status": "pending"
        },
        "project_id": "personal",
        "tags": ["communication", "reply", "harshal", "today"],
        "importance_score": 0.7
    }
]

print("📝 Storing today's tasks...\n")

for i, task in enumerate(tasks, 1):
    # Store in brain POC
    item_id = brain.store_working_memory_item(task)
    print(f"{i}. ✅ {task['content'][:50]}...")
    print(f"   ID: {item_id}")
    
    # Store in Obsidian
    result = storage.store_working_memory(task["content"], task)
    print(f"   → Saved to: {result['project']} project")
    
    # Extract and note entities
    if result.get('people'):
        print(f"   → People: {', '.join([p['name'] for p in result['people']])}")
    print()

# Create a daily task list in Obsidian
daily_tasks_content = f"""---
title: Daily Tasks - {datetime.now().strftime('%Y-%m-%d')}
date: {datetime.now().isoformat()}
type: daily-tasks
tags: ["tasks", "today", "action-items"]
---

# Daily Tasks - {datetime.now().strftime('%B %d, %Y')}

## Communication Tasks
- [ ] Reply to Cathy
- [ ] Send work update to Dr. Ekren (dci-analysis)
- [ ] Reply to Harshal

## Project Tasks
- [ ] Validate job_dread_mvp idea from claude_web

## Named Entities Referenced
- **cathy**: Person (context TBD)
- **dr_ekren**: Academic supervisor (dci-analysis project)
- **claude_web**: AI agent that suggested ideas
- **harshal**: Person (context TBD)
- **job_dread_mvp**: New project/idea to validate

## Status
Created: {datetime.now().strftime('%I:%M %p')}
All tasks due: Today
"""

# Save daily tasks to Obsidian
from pathlib import Path
obsidian_vault = Path("/Users/tarive/Library/Mobile Documents/iCloud~md~obsidian/Documents/Saksham")
daily_dir = obsidian_vault / "daily"
daily_dir.mkdir(exist_ok=True)

daily_file = daily_dir / f"{datetime.now().strftime('%Y-%m-%d')}-tasks.md"
with open(daily_file, 'w') as f:
    f.write(daily_tasks_content)

print(f"📋 Daily task list created: {daily_file.name}")
print("\n🔍 You can search for these using:")
print('   ~/bin/bf "reply cathy"')
print('   ~/bin/bf "dr ekren update"')
print('   ~/bin/bf "job_dread_mvp"')
print('   ~/bin/bf "harshal"')