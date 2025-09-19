# Obsidian Vault Structure Analysis

## Current Structure Discovery

Your Obsidian vault has a clear hierarchical organization:

```
/Users/tarive/Library/Mobile Documents/iCloud~md~obsidian/Documents/Saksham/
├── projects/                    # Personal projects
│   └── ybrowser/
├── uni-work/                    # University work (MAIN FOCUS)
│   ├── thrc/                   # THRC research work
│   │   ├── econ-data/          # Economic data analysis project
│   │   ├── dci_analysis/       # DCI spatial analysis project
│   │   ├── methodologies/      # Research methodologies
│   │   ├── requirements/       # Project requirements
│   │   └── data-sources/       # Data source documentation
│   └── cads/                   # Other university work
├── saksham-personal/           # Personal notes
│   └── success/
├── Science/                    # Science-related notes
│   └── Methodologies/
├── brain-poc/                  # Our POC integration (NEW)
└── communications/             # Communications tracking (NEW)
    └── econ-data/
```

## Key Insights

1. **Project Organization**: You already organize by project under `uni-work/thrc/`
2. **THRC Projects Identified**:
   - `econ-data` - Economic data analysis
   - `dci_analysis` - DCI spatial analysis  
   - Multiple related subdirectories

3. **Dr. Ekren's dci-analysis** maps to `/uni-work/thrc/dci_analysis/`
4. **Boss's THRC work** maps to `/uni-work/thrc/econ-data/`

## Proposed Working Memory Storage Strategy

### Option 1: Project-Centric Storage (RECOMMENDED)
```
uni-work/thrc/
├── econ-data/
│   ├── THRC Economic Data Analysis.md
│   └── working-memory/
│       ├── 2025-09-11-boss-communication.md
│       └── 2025-09-12-meeting-notes.md
├── dci_analysis/
│   ├── Corrected DCI Analysis....md
│   └── working-memory/
│       └── 2025-09-11-dr-ekren-feedback.md
```

**Pros**:
- Working memory stays with relevant project
- Easy to find project-specific communications
- Natural progression from working memory → permanent notes
- Maintains context locality

**Cons**:
- Working memory scattered across projects
- Harder to see all recent captures

### Option 2: Centralized Working Memory with Links
```
working-memory/
├── daily/
│   └── 2025-09-11.md
├── by-project/
│   ├── econ-data/
│   └── dci_analysis/
└── by-person/
    ├── dr-ekren/
    └── boss/
```

**Pros**:
- All working memory in one place
- Easy daily review
- Multiple organization schemes

**Cons**:
- Separated from project context
- Requires manual linking

### Option 3: Hybrid Approach (BEST OF BOTH)
```
uni-work/thrc/
├── econ-data/
│   ├── .working-memory → linked to central
│   └── permanent-notes.md
working-memory/
├── 2025-09-11/
│   ├── econ-data-boss.md
│   └── dci-analysis-ekren.md
└── index.md (auto-generated links to projects)
```

## People Finder Feature Design

### Concept
Automatically extract and track all people mentioned in notes:

```python
people_patterns = [
    r"Dr\.\s+(\w+)",           # Dr. Ekren
    r"Professor\s+(\w+)",       # Professor Smith
    r"(\w+)\s+said",           # Person said
    r"meeting with\s+(\w+)",   # meeting with Person
    r"boss",                   # Special case
    r"supervisor",             # Role-based
]
```

### Storage Structure
```
people/
├── dr-ekren.md
│   ├── Communications log
│   ├── Projects: [dci-analysis]
│   └── Last interaction: 2025-09-11
├── boss.md
│   ├── Communications log
│   ├── Projects: [econ-data, THRC]
│   └── Key decisions tracked
```

### Features
1. Auto-extract people from all notes
2. Track communication history
3. Link to relevant projects
4. Sentiment analysis of interactions
5. Meeting frequency tracking

## Full Path Specifications

All code should use absolute paths:

```python
OBSIDIAN_VAULT = "/Users/tarive/Library/Mobile Documents/iCloud~md~obsidian/Documents/Saksham"
BRAIN_POC = "/Users/tarive/brain-poc"
BASIC_MEMORY_DEFAULT = "/Users/tarive/basic-memory"

# Project paths
PATHS = {
    "econ-data": f"{OBSIDIAN_VAULT}/uni-work/thrc/econ-data",
    "dci-analysis": f"{OBSIDIAN_VAULT}/uni-work/thrc/dci_analysis",
    "working-memory": f"{OBSIDIAN_VAULT}/working-memory",
    "people": f"{OBSIDIAN_VAULT}/people",
    "communications": f"{OBSIDIAN_VAULT}/communications"
}
```

## Recommended Implementation

### Phase 1: Project-Wise Working Memory
1. Create `working-memory/` subdirectory in each project
2. Store communications in relevant project folder
3. Create daily index linking all captures

### Phase 2: Automated Transitions
1. Working memory (temporary) → Project notes (permanent)
2. After 7 days, prompt to consolidate or archive
3. Important items get promoted to permanent notes

### Phase 3: People Finder
1. Scan all notes for people mentions
2. Build relationship graph
3. Track communication patterns
4. Generate people dashboard

## Technical Implementation Notes

### Working Memory Lifecycle
```
Capture → Working Memory (7 days) → Review → Either:
  - Promote to permanent project note
  - Archive with reduced importance
  - Delete if no longer relevant
```

### Project Detection
```python
def detect_project_from_content(content, context):
    # Check explicit project mentions
    if "dci" in content.lower():
        return "dci-analysis"
    if "econ" in content.lower() or "THRC" in content:
        return "econ-data"
    
    # Check context clues
    if context.get("work_type") == "THRC":
        return "econ-data"
    
    # Default to general working memory
    return "general"
```

### Integration Points
1. **Obsidian**: Direct file writes to vault
2. **Basic Memory**: API calls for semantic search
3. **Brain POC**: Scoring and retrieval engine
4. **Claude Code**: Hooks for automatic capture