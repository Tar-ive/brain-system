# 🧠 Brain System - Goal Tracking & Memory System

A personal brain extension system designed to prevent project abandonment and maintain continuous memory across work sessions.

## 🎯 What This Solves

**The Problem**: Getting excited about projects → Something breaks → Lose hope → Abandon → Repeat

**The Solution**: A commitment-tracking system with memory persistence that:
- Tracks goals and maintains excitement
- Logs wins for dopamine rewards
- Handles blockers WITHOUT letting you quit
- Self-heals when things break
- Syncs everything to Obsidian

## 🚀 Quick Start

### New Machine Setup

```bash
# 1. Clone this repo
git clone https://github.com/YOUR_USERNAME/brain-system.git
cd brain-system

# 2. Run installer
./install.sh

# 3. Restart terminal
source ~/.zshrc  # or ~/.bashrc

# 4. Start using
bstart  # Start your day
w "Set up brain on new machine"  # Log first win
```

## 📁 What's Included

### Core Systems

| Component | Purpose | File |
|-----------|---------|------|
| **Goal Keeper** | Prevents project abandonment | `goal_keeper.py` |
| **Simple Brain** | Concurrent-safe memory storage | `simple_brain.py` |
| **Brain Core** | Shell integration & commands | `brain_core.sh` |
| **Obsidian Sync** | Backs up everything to Obsidian | `obsidian_sync.py` |

### Documentation

- `BRAIN_MASTER.md` - Complete system documentation
- `QUICK_REFERENCE.md` - One-page command reference
- `CLAUDE.md` - Context for AI sessions

## 🎮 Daily Commands

```bash
# Morning routine
bstart              # Load context, show goals

# Throughout the day
w "made progress"   # Log any win
bl "hit a problem"  # Log blocker (don't quit!)
c "important idea"  # Capture thought
f "search term"     # Find memories
b                   # Check status

# If something breaks
bh                  # Heal system (fixes 90% of issues)
```

## 🔄 Obsidian Integration

Everything automatically syncs to your Obsidian vault:

```
/YourVault/brain-system/
├── active-goals.md         # Your commitments
├── YYYY-MM-DD-brain-summary.md  # Daily summaries
├── wins/                   # Every victory logged
├── memories/               # Captured thoughts
└── blockers/              # Problems you're solving
```

## 🛠️ Installation Requirements

- macOS (tested) or Linux
- Python 3.8+
- Git
- Obsidian (optional but recommended)
- Basic Memory (`pip install basic-memory`)
- GitHub CLI (`brew install gh`)

## 📦 What Gets Backed Up

This repo contains the **system** not your personal data:
- ✅ All scripts and tools
- ✅ Documentation
- ✅ Installation scripts
- ❌ Your personal memories (stays local)
- ❌ Your goals and wins (stays local)

## 🔐 Privacy

Personal data is `.gitignore`d:
- Working memory files
- Active goals
- Win logs
- Daily photos
- Session data

Only the system itself is in the repo.

## 🧪 Testing After Installation

```bash
# Test goal system
python3 goal_keeper.py check

# Test memory
python3 simple_brain.py context

# Test search
f "test"

# Test Obsidian sync
python3 obsidian_sync.py
```

## 🆘 Troubleshooting

### "Command not found"
```bash
source ~/.zshrc  # Reload shell config
```

### "Permission denied"
```bash
chmod +x *.py *.sh
```

### System broken
```bash
bh  # Heals most issues automatically
```

### Complete reset
```bash
./install.sh  # Re-run installer
```

## 💡 Philosophy

**Commitment > Excitement**

This system is built on the principle that maintaining commitment through low-excitement periods is more important than starting new projects when excitement is high.

## 📝 The Commitment

> "I will NOT abandon the brain project when things break. I will simplify, not rebuild."

---

Built to solve my specific problem of project abandonment.  
Designed to be simple enough that it won't break.  
If it does break, it self-heals.

**Remember**: Small wins count. Every `w` command is a victory.