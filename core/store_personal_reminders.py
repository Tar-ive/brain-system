#!/usr/bin/env python3
"""
Store personal reminders with entity resolution for nicknames
"""

import sys
sys.path.append('/Users/tarive/brain-poc/scripts')
sys.path.append('/Users/tarive/brain-poc')

from improved_scoring import ImprovedBrainScoring
from store_to_project import ProjectAwareStorage
from datetime import datetime

# Entity resolution mapping
ENTITY_RESOLUTION = {
    "girlfriend": ["kusum", "baby", "shona", "puntu"],  # All map to same person
    "boss": ["supervisor", "manager"],
    "dr_ekren": ["dr. ekren", "ekren", "professor ekren"]
}

def resolve_entity(name: str) -> str:
    """Resolve nicknames to canonical entity"""
    name_lower = name.lower()
    
    for canonical, aliases in ENTITY_RESOLUTION.items():
        if name_lower in aliases:
            return canonical
    
    return name_lower

# Store today's reminders
storage = ProjectAwareStorage()
brain = ImprovedBrainScoring()

# Reminder 1: Chutney for girlfriend
reminder1 = {
    "content": "Make chutney for baby today. Remember that kusum, baby, shona, and puntu are all the same person (girlfriend).",
    "context": {
        "type": "personal_reminder",
        "priority": "high",
        "deadline": "today",
        "person": "girlfriend",
        "entity_aliases": ["kusum", "baby", "shona", "puntu"]
    },
    "project_id": "personal",
    "thinking_mode": "capture",
    "tags": ["personal", "cooking", "girlfriend", "today"],
    "importance_score": 0.8
}

# Reminder 2: Flight tickets
reminder2 = {
    "content": "Get flight tickets today - this is urgent and needs to be done before end of day.",
    "context": {
        "type": "personal_reminder", 
        "priority": "urgent",
        "deadline": "today",
        "category": "travel"
    },
    "project_id": "personal",
    "thinking_mode": "capture",
    "tags": ["personal", "travel", "urgent", "today"],
    "importance_score": 0.9
}

# Store both reminders
print("📝 Storing personal reminders...\n")

# Store in brain POC working memory
item1_id = brain.store_working_memory_item(reminder1)
print(f"✅ Stored: Chutney reminder (ID: {item1_id})")

item2_id = brain.store_working_memory_item(reminder2)
print(f"✅ Stored: Flight tickets reminder (ID: {item2_id})")

# Also store in Obsidian with project awareness
result1 = storage.store_working_memory(reminder1["content"], reminder1)
print(f"   → Saved to Obsidian: {result1['project']} project")

result2 = storage.store_working_memory(reminder2["content"], reminder2)
print(f"   → Saved to Obsidian: {result2['project']} project")

print("\n✅ Personal reminders stored successfully!")
print("\n🔍 You can search for these using:")
print('   ~/bin/bf "chutney"')
print('   ~/bin/bf "flight tickets"')
print('   ~/bin/bf "girlfriend" (will find all aliases)')