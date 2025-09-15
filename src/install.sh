#!/bin/bash
# Brain System Installation Script
# Run this on a new machine to set everything up

set -e  # Exit on error

echo "🧠 Brain System Installer v1.0"
echo "=============================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 found${NC}"

# Check git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git not found. Please install git.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Git found${NC}"

# Check gh CLI
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}⚠️ GitHub CLI not found. Installing...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install gh
    else
        echo "Please install GitHub CLI: https://cli.github.com/"
        exit 1
    fi
fi
echo -e "${GREEN}✅ GitHub CLI found${NC}"

# Check Basic Memory
if ! command -v basic-memory &> /dev/null; then
    echo -e "${YELLOW}⚠️ Basic Memory not found. Installing...${NC}"
    pip3 install basic-memory
fi
echo -e "${GREEN}✅ Basic Memory found${NC}"

echo ""
echo "🔧 Setting up Brain System..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p ~/.brain/sessions
mkdir -p ~/.claude/hooks
mkdir -p ~/bin
mkdir -p working-memory
mkdir -p daily-goals
mkdir -p scripts

# Create placeholder files for git tracking
touch working-memory/.gitkeep
touch daily-goals/.gitkeep

# Make all scripts executable
echo "🔐 Setting permissions..."
chmod +x *.py *.sh 2>/dev/null || true
chmod +x scripts/*.py 2>/dev/null || true

# Set up shell integration
echo ""
echo "🐚 Setting up shell integration..."

SHELL_RC=""
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_RC="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_RC="$HOME/.bashrc"
else
    echo -e "${YELLOW}⚠️ Unknown shell. Please manually add to your shell RC:${NC}"
    echo "source $PWD/brain_core.sh"
fi

if [ -n "$SHELL_RC" ]; then
    # Check if already added
    if ! grep -q "brain_core.sh" "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "# Brain System Integration" >> "$SHELL_RC"
        echo "source $PWD/brain_core.sh" >> "$SHELL_RC"
        echo -e "${GREEN}✅ Added to $SHELL_RC${NC}"
    else
        echo -e "${GREEN}✅ Already in $SHELL_RC${NC}"
    fi
fi

# Set up Claude hooks
echo ""
echo "🪝 Setting up Claude Code hooks..."
cp -n session_start.py ~/.claude/hooks/ 2>/dev/null || echo "  session_start.py already exists"
cp -n session_end.py ~/.claude/hooks/ 2>/dev/null || echo "  session_end.py already exists"
cp -n post_tool_use.py ~/.claude/hooks/ 2>/dev/null || echo "  post_tool_use.py already exists"
chmod +x ~/.claude/hooks/*.py
echo -e "${GREEN}✅ Claude hooks installed${NC}"

# Configure Basic Memory
echo ""
echo "💾 Configuring Basic Memory..."
if [ -n "$OBSIDIAN_PATH" ]; then
    basic-memory project add brain-main "$PWD" 2>/dev/null || true
    basic-memory project set-default brain-main 2>/dev/null || true
    echo -e "${GREEN}✅ Basic Memory configured${NC}"
else
    echo -e "${YELLOW}⚠️ Set OBSIDIAN_PATH environment variable for full integration${NC}"
fi

# Initialize goal tracking
echo ""
echo "🎯 Initializing goal tracking..."
if [ ! -f "active_goals.json" ]; then
    cat > active_goals.json << 'EOF'
{
  "brain_system": {
    "status": "active",
    "excitement_level": 10,
    "commitment": "Build this to the core - no abandonment"
  }
}
EOF
    echo -e "${GREEN}✅ Goals initialized${NC}"
else
    echo -e "${GREEN}✅ Goals already exist${NC}"
fi

# Create symlink for bf command
echo ""
echo "🔗 Creating command shortcuts..."
if [ ! -L ~/bin/bf ]; then
    ln -s "$PWD/bf" ~/bin/bf 2>/dev/null || true
fi
echo -e "${GREEN}✅ Command shortcuts created${NC}"

# Run initial test
echo ""
echo "🧪 Running system test..."
if python3 goal_keeper.py check > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Goal keeper working${NC}"
else
    echo -e "${YELLOW}⚠️ Goal keeper needs attention${NC}"
fi

if python3 simple_brain.py context > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Simple brain working${NC}"
else
    echo -e "${YELLOW}⚠️ Simple brain needs attention${NC}"
fi

# Obsidian check
echo ""
echo "📚 Checking Obsidian integration..."
OBSIDIAN_DIR="/Users/$USER/Library/Mobile Documents/iCloud~md~obsidian/Documents"
if [ -d "$OBSIDIAN_DIR" ]; then
    echo -e "${GREEN}✅ Obsidian vault found${NC}"
    # Update obsidian_sync.py with correct path
    sed -i '' "s|/Users/tarive/|/Users/$USER/|g" obsidian_sync.py 2>/dev/null || true
else
    echo -e "${YELLOW}⚠️ Obsidian vault not found. Install Obsidian and sync your vault.${NC}"
fi

echo ""
echo "================================"
echo -e "${GREEN}🎉 Brain System Installation Complete!${NC}"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Restart your terminal or run: source $SHELL_RC"
echo "2. Test with: bstart"
echo "3. Log your first win: w 'Set up brain system on new machine'"
echo ""
echo "Commands available:"
echo "  bstart - Start your day"
echo "  b      - Check brain status"
echo "  w      - Log a win"
echo "  bl     - Log a blocker"
echo "  c      - Capture a thought"
echo "  f      - Find memories"
echo "  bh     - Heal the system"
echo ""
echo "Documentation:"
echo "  BRAIN_MASTER.md - Complete guide"
echo "  QUICK_REFERENCE.md - Command cheat sheet"
echo ""
echo "🧠 Your brain is ready!"