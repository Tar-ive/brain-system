#!/bin/bash
# Global Brain System Setup
# This script configures your shell for continuous memory chain

BRAIN_POC_DIR="/Users/tarive/brain-poc"
BRAIN_DIR="/Users/tarive/brain"

# Ensure directories exist
mkdir -p "$BRAIN_DIR"/{contexts,knowledge,scripts,logs}
mkdir -p "$BRAIN_DIR/contexts"/{projects,modes,working-memory}
mkdir -p "$BRAIN_DIR/knowledge"/{principles,patterns,insights}

# Global brain search function
brain_find() {
    local query="$*"
    echo "🧠 Searching brain for: $query"
    echo ""
    
    # Search POC working memory
    if [ -x "$BRAIN_POC_DIR/bf" ]; then
        echo "=== Working Memory ==="
        "$BRAIN_POC_DIR/bf" "$query"
        echo ""
    fi
    
    # Search Basic Memory
    echo "=== Long-term Memory (Basic Memory) ==="
    basic-memory tool search-notes "$query" 2>/dev/null || echo "Basic Memory not available"
    echo ""
}

# Store memory function
brain_store() {
    local content="$*"
    if [ -z "$content" ]; then
        echo "Usage: brain_store <content>"
        return 1
    fi
    
    echo "💾 Storing: $content"
    python3 "$BRAIN_POC_DIR/scripts/unified_brain.py" store "$content"
}

# Get current context
brain_context() {
    echo "📋 Current Brain Context:"
    python3 "$BRAIN_POC_DIR/scripts/unified_brain.py" context
}

# Sync to Obsidian
brain_sync() {
    echo "🔄 Syncing to Obsidian..."
    python3 "$BRAIN_POC_DIR/scripts/unified_brain.py" sync
}

# Show brain status
brain_status() {
    echo "=== 🧠 Brain System Status ==="
    echo ""
    
    echo "📊 Working Memory:"
    python3 "$BRAIN_POC_DIR/scripts/poc_scoring.py" status 2>/dev/null || echo "POC not available"
    echo ""
    
    echo "💾 Basic Memory:"
    basic-memory status 2>/dev/null || echo "Basic Memory not configured"
    echo ""
    
    echo "📁 Brain Directories:"
    [ -d "$BRAIN_POC_DIR" ] && echo "✅ POC: $BRAIN_POC_DIR" || echo "❌ POC directory missing"
    [ -d "$BRAIN_DIR" ] && echo "✅ Main: $BRAIN_DIR" || echo "❌ Main directory missing"
}

# Quick capture for Claude sessions
claude_capture() {
    local insight="$*"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    
    # Store in unified brain
    brain_store "[$timestamp] Claude: $insight"
    
    # Also create a Basic Memory note
    echo "$insight" | basic-memory tool write-note \
        --title "Claude Session $(date +%Y-%m-%d)" \
        --folder "claude-sessions" \
        --tags "claude" \
        --tags "insight" 2>/dev/null
}

# Export functions for shell use
export -f brain_find brain_store brain_context brain_sync brain_status claude_capture

# Aliases for quick access
alias bf="brain_find"
alias bs="brain_store"
alias bc="brain_context"
alias bsync="brain_sync"
alias bst="brain_status"
alias cc="claude_capture"

# Add brain-poc to PATH for global bf command
export PATH="$BRAIN_POC_DIR:$PATH"

echo "🧠 Brain System Loaded!"
echo "Commands: bf (find), bs (store), bc (context), bsync (sync), bst (status), cc (claude capture)"