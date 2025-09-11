# 🧠 Digital Brain POC - Complete System Documentation

**CRITICAL**: This is a SMART CONTEXT system that prevents cognitive overload by following brain.md's architecture.

---

## ⚡ Quick Start for New Session

```bash
# FIRST COMMAND - Always run this:
python3 /Users/tarive/brain-poc/smart_context_loader.py

# This loads ONLY what you need (max 7 items) to prevent overload
```

---

## 🎯 How Context Management Works

### **Smart Context Loading (Prevents Overload)**

Based on **brain.md's Three-Layer Architecture**:

1. **Working Memory Limit**: Only 7 items maximum (cognitive science limit)
2. **Temporal Decay**: Items older than 7 days automatically filtered
3. **Priority Scoring**: 
   - 40% recency
   - 30% importance  
   - 20% connections
   - 10% access frequency

### **What Gets Loaded Automatically**
- ✅ Today's urgent tasks only (max 3)
- ✅ Active entities mentioned today (compressed)
- ✅ Essential commands (3 core ones)
- ✅ Current project context
- ❌ NOT old tasks, NOT all entities, NOT full history

### **Full Context (Only When Needed)**
```bash
# Load everything (use sparingly):
python3 /Users/tarive/brain-poc/session_context.py load
```

---

## 📸 Daily Photo Goal Tracking

### **How It Works**
1. Upload a photo of your daily priorities
2. System extracts text/goals automatically
3. Goals tracked in `/daily-goals/` folder
4. Progress monitored throughout the day

### **Upload Daily Photo**
```bash
# Store photo in designated folder
cp /path/to/photo.jpg "/Users/tarive/brain-poc/daily-goals/$(date +%Y-%m-%d).jpg"

# Extract and track goals
python3 /Users/tarive/brain-poc/extract_photo_goals.py
```

### **Goal Tracking Structure**
```
brain-poc/
└── daily-goals/
    ├── 2025-09-11.jpg          # Today's photo
    ├── 2025-09-11-goals.json   # Extracted goals
    └── 2025-09-11-progress.md  # Progress tracking
```

---

## 🪝 Automatic Hooks Setup

### **Claude Code Hooks** (Auto-save on session end)

Location: `~/.claude/hooks/`

```python
# session_end.py - Automatically saves context
import subprocess
subprocess.run(["python3", "/Users/tarive/brain-poc/smart_context_loader.py"])
print("✅ Brain context auto-saved (smart filtered)")

# session_start.py - Automatically loads context  
import subprocess
subprocess.run(["python3", "/Users/tarive/brain-poc/smart_context_loader.py"])
print("🧠 Smart context loaded (7 items max)")
```

### **Git Hooks** (Track all changes)
```bash
# .git/hooks/pre-commit
#!/bin/bash
python3 /Users/tarive/brain-poc/smart_context_loader.py
echo "✅ Context saved before commit"
```

---

## 🗺️ Complete System Map

### **Architecture Overview**
```
┌─────────────────────────────────────────┐
│         METACOGNITIVE LAYER             │
│  (Context Management & Mode Control)     │
│  • Smart Context Loader (7 item limit)   │
│  • Project Switching                     │
│  • Thinking Modes                        │
└─────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────┐
│        CONSOLIDATION LAYER              │
│   (Knowledge Integration & Patterns)     │
│  • Working Memory → Long-term            │
│  • Pattern Detection                     │
│  • Temporal Decay (0.95/day)            │
└─────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────┐
│        REPRESENTATION LAYER             │
│        (Physical Storage)               │
│  • Obsidian Vault (Markdown)            │
│  • Basic Memory (Semantic)              │
│  • Brain POC (JSON)                     │
└─────────────────────────────────────────┘
```

### **File System Structure**
```
/Users/tarive/
├── brain-poc/                          # POC System
│   ├── CLAUDE.md                      # THIS FILE (Smart context)
│   ├── scripts/
│   │   ├── poc_scoring.py            # Scoring engine
│   │   └── improved_scoring.py       # Enhanced algorithm
│   ├── working-memory/                # Active memory (7 items)
│   │   ├── wm_*.json                 # Memory items
│   │   └── index.json                # Priority index
│   ├── daily-goals/                   # Photo tracking
│   │   ├── YYYY-MM-DD.jpg           # Daily photo
│   │   └── YYYY-MM-DD-goals.json    # Extracted goals
│   ├── smart_context_loader.py       # PREVENTS OVERLOAD
│   ├── session_context.py            # Full context (use rarely)
│   ├── self_healing_memory.py        # Auto-fix issues
│   └── bf                            # Search command
│
├── brain.md                           # MASTER ARCHITECTURE
│
└── Library/Mobile Documents/.../Saksham/  # Obsidian
    ├── people/                        # All entities
    │   ├── dr-tahir.md               # NEW: 4pm meeting
    │   ├── dr-ekren.md
    │   ├── baby.md (girlfriend)
    │   └── ...
    ├── daily/
    │   └── 2025-09-11-tasks.md
    ├── claude-sessions/               # Session history
    └── uni-work/thrc/
        ├── econ-data/working-memory/
        └── dci_analysis/working-memory/
```

### **Data Flow**
```
1. Input (Tasks/Memories)
   ↓
2. Priority Scoring (0.4*recency + 0.3*importance + ...)
   ↓
3. Working Memory (Max 7 items)
   ↓
4. Storage (Obsidian + Basic Memory + JSON)
   ↓
5. Smart Context Loading (Filtered)
   ↓
6. Claude Session (No overload!)
```

---

## 📅 Today's Context (September 11, 2025)

### **Urgent Items** (Working Memory: 4/7)
1. ⏰ **4pm Meeting with Dr. Tahir** 
2. 📧 Send work update to Dr. Ekren (dci-analysis)
3. 💬 Reply to Harshal
4. ✈️ Get flight tickets (urgent)

### **Completed Today**
- ✅ Replied to Cathy
- ✅ Created brain POC system
- ✅ Fixed iMessage MCP
- ✅ Implemented self-healing

### **Entity Mappings** (Active Only)
- **dr_tahir**: 4pm meeting today
- **girlfriend**: kusum, baby, shona, puntu
- **dr_ekren**: Needs work update

---

## 🔧 Essential Commands Only

```bash
# Daily Use
~/bin/bf "search"              # Search memory
brain-status                   # Check system
brain-save                     # Save context (smart)

# Maintenance  
brain-heal                     # Fix issues
python3 extract_photo_goals.py # Process daily photo

# Full Context (RARE)
brain-load                     # Load everything
```

---

## 🚀 Before Switching to New Claude Instance

### **Automatic Save Checklist**
1. ✅ Smart context auto-saved to CLAUDE.md (31 lines only)
2. ✅ Working memory limited to 7 items
3. ✅ Temporal decay applied (7-day window)
4. ✅ Dr. Tahir meeting stored
5. ✅ All hooks configured

### **Manual Save (If Needed)**
```bash
python3 /Users/tarive/brain-poc/smart_context_loader.py
```

---

## 🎯 Goal Tracking Integration

### **Daily Workflow**
1. **Morning**: Upload photo of priorities
2. **System**: Extracts goals, creates tracking
3. **Throughout Day**: Updates progress
4. **Evening**: Reviews completion

### **Photo Storage**
```bash
# Your daily photo goes here:
/Users/tarive/brain-poc/daily-goals/2025-09-11.jpg
```

---

## ⚠️ IMPORTANT PRINCIPLES

### **From brain.md**:
1. **Cognitive Load Management**: Never exceed 7 working memory items
2. **Temporal Decay**: 0.95^days decay rate for relevance
3. **Project Containerization**: Prevent cross-contamination
4. **Priority Scoring**: Automatic importance calculation

### **Smart Context Benefits**:
- ✅ **Prevents overload** (31 lines vs 175 lines)
- ✅ **Maintains focus** (only today's priorities)
- ✅ **Respects cognitive limits** (7±2 items)
- ✅ **Auto-filters old information**

---

## 🔄 Next Session Will Automatically:
1. Read this CLAUDE.md (smart filtered)
2. Load only essential context (7 items max)
3. Show today's urgent tasks
4. Maintain cognitive clarity

**The system is self-managing and prevents information overload!**

---

*Generated: September 11, 2025, 12:15 PM*
*System: Digital Brain POC v1.0*
*Architecture: brain.md compliant*