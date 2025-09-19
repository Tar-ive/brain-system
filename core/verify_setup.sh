#!/bin/bash
# Brain System Setup Verification
# Run this after installation to verify everything works

echo "🧠 Brain System Verification"
echo "============================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PASS=0
FAIL=0

# Function to check status
check() {
    local name=$1
    local command=$2
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name${NC}"
        ((PASS++))
    else
        echo -e "${RED}❌ $name${NC}"
        ((FAIL++))
    fi
}

echo "📋 Checking Core Components:"
check "Python 3" "python3 --version"
check "Git" "git --version"
check "GitHub CLI" "gh --version"
check "Basic Memory" "basic-memory --version"

echo ""
echo "📂 Checking Directories:"
check "Brain POC directory" "[ -d /Users/$(whoami)/brain-poc ]"
check "~/.brain directory" "[ -d ~/.brain ]"
check "~/.brain/sessions" "[ -d ~/.brain/sessions ]"
check "~/.claude/hooks" "[ -d ~/.claude/hooks ]"

echo ""
echo "📝 Checking Files:"
check "Goal keeper" "[ -f goal_keeper.py ]"
check "Simple brain" "[ -f simple_brain.py ]"
check "Brain core" "[ -f brain_core.sh ]"
check "Obsidian sync" "[ -f obsidian_sync.py ]"

echo ""
echo "🔐 Checking Permissions:"
check "Scripts executable" "[ -x goal_keeper.py ]"
check "Shell scripts executable" "[ -x brain_core.sh ]"

echo ""
echo "🧪 Testing Functionality:"
check "Goal system" "python3 goal_keeper.py check"
check "Memory system" "python3 simple_brain.py context"
check "Working memory" "python3 scripts/poc_scoring.py status"

echo ""
echo "🔗 Checking Integration:"
check "Shell integration" "grep -q 'brain_core.sh' ~/.zshrc || grep -q 'brain_core.sh' ~/.bashrc"
check "Claude hooks" "[ -f ~/.claude/hooks/session_start.py ]"

echo ""
echo "📚 Checking Obsidian:"
OBSIDIAN_DIR="/Users/$(whoami)/Library/Mobile Documents/iCloud~md~obsidian/Documents"
if [ -d "$OBSIDIAN_DIR" ]; then
    echo -e "${GREEN}✅ Obsidian vault found${NC}"
    ((PASS++))
    
    # Check for brain-system folder
    if [ -d "$OBSIDIAN_DIR/Saksham/brain-system" ] || [ -d "$OBSIDIAN_DIR/*/brain-system" ]; then
        echo -e "${GREEN}✅ Brain system folder in Obsidian${NC}"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠️ Brain system folder not yet created in Obsidian${NC}"
        echo "  Run: python3 obsidian_sync.py"
    fi
else
    echo -e "${YELLOW}⚠️ Obsidian vault not found${NC}"
    echo "  Install Obsidian and sync your vault"
fi

echo ""
echo "================================"
echo "📊 Results: $PASS passed, $FAIL failed"
echo "================================"

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed! Your brain system is ready.${NC}"
    echo ""
    echo "Test it with:"
    echo "  bstart - Start your day"
    echo "  w 'System verified' - Log a win"
else
    echo -e "${YELLOW}⚠️ Some checks failed. Run ./install.sh to fix.${NC}"
fi

echo ""
echo "📖 Documentation:"
echo "  BRAIN_MASTER.md - Complete guide"
echo "  QUICK_REFERENCE.md - Command reference"
echo "  README.md - Setup instructions"