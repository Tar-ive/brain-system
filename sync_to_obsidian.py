#!/usr/bin/env python3
"""
Sync working memory items to Obsidian vault and Basic Memory
"""

import json
import os
from pathlib import Path
from datetime import datetime
import subprocess

def sync_to_obsidian():
    """Sync working memory items to Obsidian vault"""
    
    # Paths
    working_memory_dir = Path("/Users/tarive/brain-poc/working-memory")
    
    # Obsidian vault paths (adjust these to your actual vault locations)
    obsidian_vaults = [
        "/Users/tarive/Library/Mobile Documents/iCloud~md~obsidian/Documents/Saksham",
        "/Users/tarive/Google Drive/My Drive/Obsidian Vaults/Saksham's Vault"
    ]
    
    print("🔄 Syncing to Obsidian and Basic Memory...")
    
    # Load all working memory items
    items = []
    for item_file in working_memory_dir.glob("wm_*.json"):
        with open(item_file) as f:
            items.append(json.load(f))
    
    if not items:
        print("❌ No items to sync")
        return
    
    # Create consolidated markdown file
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Create markdown content
    md_content = f"""---
title: "Working Memory - {today}"
type: working-memory
created: {datetime.now().isoformat()}
tags: [brain-poc, working-memory, automated-capture]
---

# Working Memory Capture - {today}

## Summary
This file contains working memory items captured by the Digital Brain POC system.

---

"""
    
    for item in sorted(items, key=lambda x: x.get('importance_score', 0), reverse=True):
        item_id = item.get('id', 'unknown')
        content = item.get('content', '')
        project = item.get('project_id', 'unknown')
        importance = item.get('importance_score', 0)
        context = item.get('context', {})
        tags = item.get('tags', [])
        stored_at = item.get('stored_at', '')
        
        md_content += f"""## {item_id}

**Project**: {project}  
**Importance**: {importance:.2f}  
**Stored**: {stored_at}  
**Tags**: {', '.join(tags)}

### Content
{content}

### Context
"""
        
        if isinstance(context, dict):
            for key, value in context.items():
                md_content += f"- **{key}**: {value}\n"
        else:
            md_content += f"{context}\n"
        
        md_content += "\n---\n\n"
    
    # Save to Obsidian vaults
    for vault_path in obsidian_vaults:
        vault = Path(vault_path)
        if vault.exists():
            # Create brain-poc directory in vault
            brain_dir = vault / "brain-poc"
            brain_dir.mkdir(exist_ok=True)
            
            # Save markdown file
            output_file = brain_dir / f"working-memory-{today}.md"
            with open(output_file, 'w') as f:
                f.write(md_content)
            
            print(f"✅ Saved to Obsidian: {output_file}")
    
    # Also save to Basic Memory
    try:
        # Create a note in Basic Memory
        cmd = [
            "basic-memory", "tool", "write-note",
            "--title", f"Working Memory - {today}",
            "--folder", "brain-poc",
            "--tags", "working-memory",
            "--tags", "automated"
        ]
        
        # Use subprocess with input
        result = subprocess.run(
            cmd,
            input=md_content,
            text=True,
            capture_output=True
        )
        
        if result.returncode == 0:
            print("✅ Saved to Basic Memory")
        else:
            print(f"⚠️ Basic Memory save failed: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️ Could not save to Basic Memory: {e}")
    
    # Create individual notes for important items
    important_items = [i for i in items if i.get('importance_score', 0) >= 0.8]
    
    if important_items:
        print(f"\n📝 Creating individual notes for {len(important_items)} important items...")
        
        for item in important_items:
            content = item.get('content', '')
            project = item.get('project_id', 'unknown')
            context = item.get('context', {})
            
            # Determine title based on content
            if isinstance(context, dict) and 'source' in context:
                source = context['source']
                title = f"{source} - {project} - {today}"
            else:
                # Use first 50 chars of content as title
                title = content[:50].replace('\n', ' ') + "..."
            
            # Create individual note
            note_content = f"""---
title: "{title}"
project: {project}
date: {today}
type: communication
importance: {item.get('importance_score', 0)}
---

# {title}

## Content
{content}

## Context
Project: **{project}**
"""
            
            if isinstance(context, dict):
                for key, value in context.items():
                    note_content += f"\n- {key}: {value}"
            
            # Save to Obsidian
            for vault_path in obsidian_vaults:
                vault = Path(vault_path)
                if vault.exists():
                    # Save in daily notes or communications folder
                    comms_dir = vault / "communications" / project
                    comms_dir.mkdir(parents=True, exist_ok=True)
                    
                    filename = f"{today}-{source if isinstance(context, dict) and 'source' in context else 'note'}.md"
                    output_file = comms_dir / filename
                    
                    with open(output_file, 'w') as f:
                        f.write(note_content)
                    
                    print(f"   ✅ Created note: {output_file.name}")

if __name__ == "__main__":
    sync_to_obsidian()