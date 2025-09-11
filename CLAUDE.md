# 🧠 Brain System v2.0 - Smart Context for Claude

**CRITICAL**: Limited context to prevent overload (7 items max)

---

## ⚡ Quick Start

```bash
# If brain system seems broken or unfamiliar:
cat SAKSHAM_INDEX.md  # User's personal guide
cat BRAIN_MASTER.md   # Complete documentation
```

---

## 🎯 Core Purpose

**Problem Solved**: User gets excited → builds → something breaks → abandons project → repeats

**Solution**: Goal tracking + anti-abandonment + auto-backup system

---

## 📍 Current System Status

- **Version**: 2.0 (Stable)
- **Location**: `/Users/tarive/brain-poc/`
- **GitHub**: `https://github.com/Tar-ive/brain-system` (private)
- **Auto-backups**: Every hour to GitHub
- **Obsidian Sync**: Active at `/Saksham/brain-system/`

---

## 🔧 Essential Commands Only

```bash
# Daily use (user knows these)
w "win"         # Log progress + dopamine
bl "blocker"    # Log problem (prevents quitting)
c "thought"     # Capture memory
f "search"      # Find in brain
b               # Status check

# Maintenance
bh              # Self-heal (fixes 90% of issues)
bgit            # Backup status
bbackup         # Force backup
```

---

## 🏗️ Architecture (Minimal)

```
brain-poc/
├── goal_keeper.py       # Anti-abandonment
├── simple_brain.py      # Memory storage
├── auto_commit.py       # Hourly backups
├── brain_core.sh        # Shell integration
└── SAKSHAM_INDEX.md     # User's guide
```

---

## 🪝 Feature Addition Hook

**When adding new features to brain system:**

1. **Naming**: Single letter/short commands (like `w`, `bl`)
2. **Integration**: Add to `brain_core.sh`
3. **Auto-backup**: Include in `auto_commit.py` 
4. **Documentation**: Update `SAKSHAM_INDEX.md` (user guide)

**Pattern for new features:**
```python
# In goal_keeper.py or new module
def new_feature(input):
    # 1. Process input
    # 2. Store in appropriate location
    # 3. Trigger auto_commit.check() if important
    # 4. Return user feedback
```

---

## 🔄 Context Preservation

**What to remember across sessions:**
1. User's commitment: "Don't abandon when things break"
2. Blocker pattern: Problems → Log them → Don't quit
3. 7-item working memory limit
4. Everything auto-backs up hourly

---

## 🚨 If User Says "It's Broken"

1. First: `bh` (self-heal)
2. Check: `bgit` (see uncommitted changes)
3. Verify: `./verify_setup.sh`
4. Nuclear: `./install.sh` (reinstall)

---

## 📊 Key Behavioral Insights

- User abandons when frustrated → `bl` prevents this
- User forgets to save → Auto-commits hourly
- User overcomplicates → System enforces simplicity
- User loses context → Everything in GitHub/Obsidian

---

## 🎮 Gamification Active

- **Excitement**: 🔥 levels (10 = max)
- **Streaks**: Days worked
- **Wins**: Logged for dopamine
- **Blockers**: Turned into challenges

---

## 📝 Smart Context Rules

1. **Never exceed 7 working memory items**
2. **Don't reload full history** (causes overload)
3. **Reference docs exist** (don't duplicate)
4. **User knows basics** (don't re-explain)

---

## 🔗 Related Files

- `SAKSHAM_INDEX.md` - User's personal guide
- `BRAIN_MASTER.md` - Complete documentation
- `QUICK_REFERENCE.md` - Command cheat sheet
- `.auto_commit_state.json` - Backup status

---

**Last Updated**: 2024-11-11
**Context Size**: ~50 lines (within cognitive limits)
**Remember**: This is a smart pointer, not full documentation