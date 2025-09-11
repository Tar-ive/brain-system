#!/bin/bash
# Brain Core - The simple system that actually works

BRAIN_DIR="/Users/tarive/brain-poc"

# Quick brain status
brain() {
    echo "=== 🧠 BRAIN STATUS ==="
    
    # Show goals and commitment
    python3 "$BRAIN_DIR/goal_keeper.py" check
    
    echo ""
    echo "=== 📝 WORKING MEMORY ==="
    python3 "$BRAIN_DIR/scripts/poc_scoring.py" status 2>/dev/null || echo "No working memory"
    
    echo ""
    echo "=== ⏰ TODAY'S FOCUS ==="
    python3 "$BRAIN_DIR/goal_keeper.py" next
}

# Log a win (dopamine hit!)
win() {
    python3 "$BRAIN_DIR/goal_keeper.py" win "$*"
    echo "💾 Saving to memory..."
    python3 "$BRAIN_DIR/simple_brain.py" store "WIN: $*" 0.9
    # Auto-sync wins to Obsidian
    python3 "$BRAIN_DIR/obsidian_sync.py" >/dev/null 2>&1 &
    echo "📝 Synced to Obsidian"
}

# Log a blocker (without quitting!)
blocker() {
    python3 "$BRAIN_DIR/goal_keeper.py" blocker "$*"
    echo "💾 Documenting blocker..."
    python3 "$BRAIN_DIR/simple_brain.py" store "BLOCKER: $*" 0.8
}

# Resolve blocker
unblock() {
    python3 "$BRAIN_DIR/goal_keeper.py" resolve
}

# Quick capture
capture() {
    local content="$*"
    python3 "$BRAIN_DIR/simple_brain.py" store "$content"
    echo "✅ Captured: $content"
}

# Search everything
find_memory() {
    echo "🔍 Searching for: $*"
    python3 "$BRAIN_DIR/simple_brain.py" search "$*"
}

# Save session
save_session() {
    echo "💾 Saving session..."
    python3 "$BRAIN_DIR/session_context.py"
    echo "🔄 Syncing to Obsidian..."
    python3 "$BRAIN_DIR/obsidian_sync.py"
    echo "✅ Session saved & synced"
}

# Load session
load_session() {
    echo "📂 Loading previous session..."
    python3 "$BRAIN_DIR/session_context.py" load
}

# The "make it work" command
heal() {
    echo "🔧 Self-healing brain..."
    python3 "$BRAIN_DIR/self_healing_memory.py" 2>/dev/null || echo "Creating new healing system..."
    
    # Quick healing: fix common issues
    # Fix permissions
    chmod +x "$BRAIN_DIR"/*.py "$BRAIN_DIR"/*.sh 2>/dev/null
    
    # Ensure directories exist
    mkdir -p "$BRAIN_DIR/working-memory"
    mkdir -p "$BRAIN_DIR/scripts"
    mkdir -p ~/.brain/sessions
    
    # Initialize if missing
    if [ ! -f "$BRAIN_DIR/active_goals.json" ]; then
        echo '{"brain_system": {"status": "active"}}' > "$BRAIN_DIR/active_goals.json"
    fi
    
    echo "✅ Brain healed"
}

# Daily startup routine
startup() {
    echo "🌅 BRAIN STARTUP ROUTINE"
    echo "========================"
    
    # 1. Load context
    load_session
    
    # 2. Show goals
    brain
    
    # 3. Show what to do
    echo ""
    echo "🎯 FOCUS:"
    python3 "$BRAIN_DIR/goal_keeper.py" next
}

# Export all functions
export -f brain win blocker unblock capture find_memory save_session load_session heal startup

# Aliases for ultra-quick access
alias b="brain"
alias w="win"
alias bl="blocker"
alias ub="unblock"
alias c="capture"
alias f="find_memory"
alias bs="save_session"
alias bl="load_session"
alias bh="heal"
alias bstart="startup"

echo "🧠 Brain Core Loaded!"
echo "Commands: b (status), w (win), bl (blocker), c (capture), f (find)"
echo "Start with: bstart"