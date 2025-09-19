#!/usr/bin/env python3
"""
Project-wise working memory storage that integrates with existing Obsidian structure
"""

import json
import os
from pathlib import Path
from datetime import datetime
import re
from typing import Dict, Optional

class ProjectAwareStorage:
    def __init__(self):
        # Full path specifications
        self.OBSIDIAN_VAULT = Path("/Users/tarive/Library/Mobile Documents/iCloud~md~obsidian/Documents/Saksham")
        
        # Project paths mapping
        self.PROJECT_PATHS = {
            "econ-data": self.OBSIDIAN_VAULT / "uni-work/thrc/econ-data",
            "dci-analysis": self.OBSIDIAN_VAULT / "uni-work/thrc/dci_analysis",
            "thrc-main": self.OBSIDIAN_VAULT / "uni-work/thrc/THRC",
            "methodologies": self.OBSIDIAN_VAULT / "uni-work/thrc/methodologies",
            "personal": self.OBSIDIAN_VAULT / "saksham-personal",
            "general": self.OBSIDIAN_VAULT / "working-memory"
        }
        
        # People patterns for extraction
        self.PEOPLE_PATTERNS = [
            (r"Dr\.\s+([A-Z][a-z]+)", "doctor"),
            (r"Professor\s+([A-Z][a-z]+)", "professor"),
            (r"([A-Z][a-z]+)\s+said", "mentioned"),
            (r"meeting with\s+([A-Z][a-z]+)", "meeting"),
            (r"(boss|supervisor)", "role"),
        ]
    
    def detect_project(self, content: str, metadata: Dict) -> str:
        """Detect which project this memory belongs to"""
        
        # Check explicit project in metadata
        if metadata.get("project_id"):
            return metadata["project_id"]
        
        content_lower = content.lower()
        
        # Content-based detection
        if "thrc" in content_lower and ("economic" in content_lower or "econ" in content_lower):
            return "econ-data"
        
        if "dci" in content_lower or "spatial" in content_lower:
            return "dci-analysis"
        
        # Person-based detection
        if "ekren" in content_lower:
            return "dci-analysis"
        
        if "boss" in content_lower and "thrc" in content_lower:
            return "econ-data"
        
        # Context-based detection
        context = metadata.get("context", {})
        if isinstance(context, dict):
            if context.get("project_discussed"):
                return context["project_discussed"]
            if context.get("work_type") == "THRC":
                return "econ-data"
        
        return "general"
    
    def extract_people(self, content: str) -> list:
        """Extract people mentioned in content"""
        people = []
        
        for pattern, person_type in self.PEOPLE_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                people.append({
                    "name": match if isinstance(match, str) else match[0],
                    "type": person_type
                })
        
        # Deduplicate
        seen = set()
        unique_people = []
        for person in people:
            key = f"{person['name'].lower()}_{person['type']}"
            if key not in seen:
                seen.add(key)
                unique_people.append(person)
        
        return unique_people
    
    def store_working_memory(self, content: str, metadata: Dict) -> Dict:
        """Store working memory in appropriate project folder"""
        
        # Detect project
        project = self.detect_project(content, metadata)
        project_path = self.PROJECT_PATHS.get(project, self.PROJECT_PATHS["general"])
        
        # Extract people
        people = self.extract_people(content)
        
        # Create working memory directory in project
        wm_dir = project_path / "working-memory"
        wm_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d")
        time_str = timestamp.strftime("%H%M%S")
        
        # Determine source for filename
        source = "note"
        if metadata.get("context") and isinstance(metadata["context"], dict):
            source = metadata["context"].get("source", "note").lower().replace(" ", "-")
        
        filename = f"{date_str}-{time_str}-{source}.md"
        filepath = wm_dir / filename
        
        # Create markdown content
        md_content = f"""---
title: "{content[:50]}..."
date: {timestamp.isoformat()}
project: {project}
type: working-memory
people: {json.dumps(people)}
tags: ["working-memory", "{project}", "{source}"]
importance: {metadata.get('importance_score', 0.5)}
---

# {content[:50]}...

## Content
{content}

## Context
"""
        
        # Add context information
        context = metadata.get("context", {})
        if isinstance(context, dict):
            for key, value in context.items():
                md_content += f"- **{key}**: {value}\n"
        else:
            md_content += f"{context}\n"
        
        # Add people section if found
        if people:
            md_content += "\n## People Mentioned\n"
            for person in people:
                md_content += f"- {person['name']} ({person['type']})\n"
        
        # Add metadata
        md_content += f"\n## Metadata\n"
        md_content += f"- Detected Project: {project}\n"
        md_content += f"- Storage Path: `{filepath}`\n"
        md_content += f"- Timestamp: {timestamp.isoformat()}\n"
        
        # Save the file
        with open(filepath, 'w') as f:
            f.write(md_content)
        
        # Update daily index
        self.update_daily_index(filepath, content, project, people)
        
        # Update people notes if found
        if people:
            self.update_people_notes(people, content, project, timestamp)
        
        return {
            "status": "success",
            "project": project,
            "path": str(filepath),
            "people": people
        }
    
    def update_daily_index(self, filepath: Path, content: str, project: str, people: list):
        """Update the daily index with new entry"""
        
        daily_dir = self.OBSIDIAN_VAULT / "working-memory" / "daily"
        daily_dir.mkdir(parents=True, exist_ok=True)
        
        today = datetime.now().strftime("%Y-%m-%d")
        daily_file = daily_dir / f"{today}.md"
        
        # Create or append to daily file
        if not daily_file.exists():
            daily_content = f"""---
title: "Daily Working Memory - {today}"
date: {today}
type: daily-index
---

# Daily Working Memory - {today}

## Captures

"""
        else:
            with open(daily_file, 'r') as f:
                daily_content = f.read()
        
        # Add new entry
        timestamp = datetime.now().strftime("%H:%M:%S")
        people_str = ", ".join([p['name'] for p in people]) if people else "None"
        
        entry = f"""
### {timestamp} - {project}
- **Content**: {content[:100]}...
- **People**: {people_str}
- **Link**: [[{filepath.stem}]]

"""
        
        daily_content += entry
        
        with open(daily_file, 'w') as f:
            f.write(daily_content)
    
    def update_people_notes(self, people: list, content: str, project: str, timestamp: datetime):
        """Update individual people notes"""
        
        people_dir = self.OBSIDIAN_VAULT / "people"
        people_dir.mkdir(parents=True, exist_ok=True)
        
        for person in people:
            person_name = person['name'].lower().replace(" ", "-")
            person_file = people_dir / f"{person_name}.md"
            
            # Create or update person file
            if not person_file.exists():
                person_content = f"""---
title: "{person['name']}"
type: person
first_seen: {timestamp.isoformat()}
projects: ["{project}"]
---

# {person['name']}

## Profile
- Type: {person['type']}
- First Seen: {timestamp.strftime('%Y-%m-%d')}
- Associated Projects: {project}

## Communications Log

"""
            else:
                with open(person_file, 'r') as f:
                    person_content = f.read()
            
            # Add new communication entry
            comm_entry = f"""
### {timestamp.strftime('%Y-%m-%d %H:%M')} - {project}
{content[:200]}...

---
"""
            
            person_content += comm_entry
            
            with open(person_file, 'w') as f:
                f.write(person_content)

def test_project_storage():
    """Test the project-aware storage"""
    
    storage = ProjectAwareStorage()
    
    # Test cases
    test_cases = [
        {
            "content": "Dr. Ekren said the dci-analysis project is progressing well",
            "metadata": {
                "context": {"source": "Dr. Ekren", "meeting_type": "review"},
                "importance_score": 0.7
            }
        },
        {
            "content": "Boss wants the THRC economic data analysis by Friday",
            "metadata": {
                "context": {"source": "boss", "deadline": "Friday"},
                "importance_score": 0.9
            }
        },
        {
            "content": "Meeting with Professor Smith about methodologies",
            "metadata": {
                "context": {"source": "meeting", "topic": "methodologies"},
                "importance_score": 0.6
            }
        }
    ]
    
    for test in test_cases:
        result = storage.store_working_memory(test["content"], test["metadata"])
        print(f"✅ Stored to project: {result['project']}")
        print(f"   Path: {result['path']}")
        print(f"   People: {result['people']}")
        print()

if __name__ == "__main__":
    test_project_storage()