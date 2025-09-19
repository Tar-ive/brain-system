#!/usr/bin/env python3
"""
Create people entries in Obsidian for all mentioned entities
"""

from pathlib import Path
from datetime import datetime

# People mentioned so far
PEOPLE = {
    "dr-ekren": {
        "name": "Dr. Ekren",
        "type": "academic",
        "projects": ["dci-analysis"],
        "aliases": ["dr_ekren", "ekren", "professor ekren"],
        "context": "Professor supervising DCI spatial analysis project",
        "interactions": [
            "2025-09-11: Said dci-analysis project is taking shape nicely",
            "2025-09-11: Needs work update on project progress"
        ]
    },
    "cathy": {
        "name": "Cathy",
        "type": "professional/personal",
        "projects": ["personal"],
        "context": "Person requiring reply (context TBD)",
        "interactions": [
            "2025-09-11: Needed reply - COMPLETED"
        ]
    },
    "harshal": {
        "name": "Harshal",
        "type": "professional/personal",
        "projects": ["personal"],
        "context": "Person requiring reply",
        "interactions": [
            "2025-09-11: Needs reply"
        ]
    },
    "baby": {
        "name": "Baby (Girlfriend)",
        "type": "personal",
        "aliases": ["kusum", "shona", "puntu", "girlfriend"],
        "projects": ["personal"],
        "context": "Girlfriend - multiple nicknames",
        "interactions": [
            "2025-09-11: Make chutney for her"
        ]
    },
    "aditya": {
        "name": "Aditya",
        "type": "professional/personal",
        "projects": ["personal"],
        "context": "Person (context TBD)",
        "interactions": []
    },
    "boss": {
        "name": "Boss",
        "type": "professional",
        "projects": ["econ-data", "THRC"],
        "aliases": ["supervisor", "manager"],
        "context": "Supervisor for THRC economic analysis work",
        "interactions": [
            "2025-09-11: Emphasized THRC economic analysis priority",
            "2025-09-11: Wants preliminary report by Friday",
            "2025-09-11: Stressed Federal Reserve integration urgency"
        ]
    },
    "claude-web": {
        "name": "Claude Web",
        "type": "ai-agent",
        "aliases": ["claude_web"],
        "projects": ["job_dread_mvp"],
        "context": "AI agent that suggested job_dread_mvp idea",
        "interactions": [
            "2025-09-11: Suggested job_dread_mvp idea for validation"
        ]
    }
}

# Create people directory
people_dir = Path("/Users/tarive/Library/Mobile Documents/iCloud~md~obsidian/Documents/Saksham/people")
people_dir.mkdir(exist_ok=True)

print("👥 Creating people entries...\n")

for person_id, person_data in PEOPLE.items():
    # Create person file
    person_file = people_dir / f"{person_id}.md"
    
    # Generate content
    content = f"""---
title: {person_data['name']}
type: person
person_type: {person_data['type']}
projects: {person_data.get('projects', [])}
aliases: {person_data.get('aliases', [])}
created: {datetime.now().isoformat()}
last_interaction: {datetime.now().strftime('%Y-%m-%d')}
---

# {person_data['name']}

## Profile
- **Type**: {person_data['type']}
- **Context**: {person_data['context']}
- **Associated Projects**: {', '.join(person_data.get('projects', []))}
"""
    
    if person_data.get('aliases'):
        content += f"- **Also Known As**: {', '.join(person_data['aliases'])}\n"
    
    content += "\n## Interactions Log\n"
    
    if person_data['interactions']:
        for interaction in person_data['interactions']:
            content += f"- {interaction}\n"
    else:
        content += "- No interactions recorded yet\n"
    
    content += "\n## Notes\n"
    content += "- Add any additional notes about this person here\n"
    
    # Special sections for specific people
    if person_id == "dr-ekren":
        content += "\n## Academic Work\n"
        content += "- DCI Spatial Analysis Project\n"
        content += "- Supervisor for research work\n"
    
    if person_id == "baby":
        content += "\n## Personal Notes\n"
        content += "- Remember: All nicknames (kusum, shona, puntu, baby) refer to same person\n"
    
    # Save file
    with open(person_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Created: {person_file.name}")

# Create people index
index_content = f"""---
title: People Directory
type: index
created: {datetime.now().isoformat()}
---

# People Directory

## Academic
- [[dr-ekren|Dr. Ekren]] - DCI project supervisor

## Professional
- [[boss|Boss]] - THRC/econ-data supervisor
- [[cathy|Cathy]] - ✅ Reply completed
- [[harshal|Harshal]] - ⏳ Needs reply
- [[aditya|Aditya]] - Contact

## Personal
- [[baby|Girlfriend (Baby/Kusum/Shona/Puntu)]] - Multiple nicknames

## AI Agents
- [[claude-web|Claude Web]] - Suggested job_dread_mvp

## Quick Status
- ✅ Cathy - Reply completed
- ⏳ Harshal - Needs reply
- ⏳ Dr. Ekren - Send work update
- 📝 job_dread_mvp - Validate idea from Claude Web

Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

index_file = people_dir / "index.md"
with open(index_file, 'w') as f:
    f.write(index_content)

print(f"\n📋 Created people index: {index_file.name}")
print("\n✅ All people entities stored in Obsidian!")