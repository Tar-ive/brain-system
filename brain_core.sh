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
    # Check for auto-commit
    python3 "$BRAIN_DIR/auto_commit.py" check >/dev/null 2>&1 &
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

# Git status check
git_status() {
    echo "📊 Git Status:"
    python3 "$BRAIN_DIR/auto_commit.py" status
}

# Force backup
backup() {
    echo "💾 Backing up to GitHub..."
    python3 "$BRAIN_DIR/auto_commit.py" force "${1:-Manual backup}"
    echo "✅ Backup complete"
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

# WhatsApp MCP Integration Commands
wa_status() {
    echo "📱 WhatsApp MCP Status: ❌ KNOWN ISSUE"
    echo "Error: Client outdated (405) - WhatsApp servers blocking connection"
    echo "Tracking: https://github.com/lharries/whatsapp-mcp/issues/94"
    echo ""
    echo "MCP Server Status:"
    claude mcp list | grep whatsapp
    echo ""
    echo "🔄 Workaround: Consider iOS Shortcuts or manual export integration"
}

wa_auth() {
    echo "🔐 Starting WhatsApp authentication..."
    echo "📱 Scan QR code with your phone: WhatsApp → Settings → Linked Devices"
    cd /Users/tarive/brain-poc/integrations/whatsapp-mcp/whatsapp-bridge
    ./whatsapp-bridge
}

wa_bridge_start() {
    echo "🌉 Starting WhatsApp bridge server..."
    cd /Users/tarive/brain-poc/integrations/whatsapp-mcp/whatsapp-bridge
    ./whatsapp-bridge &
    sleep 3
    wa_status
}

wa_bridge_stop() {
    echo "🛑 Stopping WhatsApp bridge..."
    pkill -f whatsapp-bridge
    echo "✅ Bridge stopped"
}

wa_memory_store() {
    echo "💾 Storing WhatsApp conversation to Basic Memory..."
    echo "$*" | basic-memory tool write-note --title "WhatsApp: $(date '+%Y-%m-%d %H:%M')" --folder "communications" --tags "whatsapp"
    echo "✅ Stored to Basic Memory"
}

wa_test_connection() {
    echo "🧪 Testing WhatsApp MCP integration..."
    echo "1. Bridge Status:"
    wa_status
    echo ""
    echo "2. Current Status: ❌ BLOCKED"
    echo "   - WhatsApp servers reject outdated client version"
    echo "   - Issue tracked at: https://github.com/lharries/whatsapp-mcp/issues/94"
    echo ""
    echo "3. Alternative Solutions:"
    echo "   ✅ iOS Shortcuts integration"
    echo "   ✅ Manual chat export + Claude processing"
    echo "   ✅ Basic Memory storage ready"
    echo ""
    echo "💡 Next: Try 'wa-alternative' for workaround options"
}

wa_alternative() {
    echo "🔄 WhatsApp Alternative Integration Options:"
    echo ""
    echo "1. 📱 iOS Shortcuts Integration (Recommended) ✅ READY"
    echo "   - Bridge server: wa-ios-start"
    echo "   - Setup guide: wa-ios-setup"
    echo "   - No API dependency, works directly with phone"
    echo ""
    echo "2. 📄 Manual Export Method"
    echo "   - Export chat from WhatsApp"
    echo "   - Process with Claude via Basic Memory"
    echo "   - Command: wa-manual-import <file>"
    echo ""
    echo "3. 🏢 WhatsApp Business API"
    echo "   - Requires business account verification"
    echo "   - More reliable but complex setup"
    echo "   - Command: wa-business-setup (advanced)"
    echo ""
    echo "🧠 All methods integrate with existing brain system!"
}

wa_ios_start() {
    echo "🌉 Starting WhatsApp iOS Bridge..."
    echo "📱 This will receive WhatsApp data from iOS Shortcuts"
    echo "💾 Auto-stores to Basic Memory with brain system integration"
    echo ""
    python3 /Users/tarive/brain-poc/integrations/whatsapp-mcp/whatsapp-ios-bridge.py
}

wa_ios_setup() {
    echo "📱 WhatsApp iOS Shortcuts Setup Guide"
    echo "===================================="
    echo ""
    echo "Step 1: Start the bridge server"
    echo "   Run: wa-ios-start (in another terminal)"
    echo ""
    echo "Step 2: Create iOS Shortcut"
    echo "   1. Open Shortcuts app on iPhone"
    echo "   2. Tap + to create new shortcut"
    echo "   3. Add these actions:"
    echo ""
    echo "   Action 1: 'Ask for Input'"
    echo "   - Prompt: 'Paste WhatsApp conversation'"
    echo "   - Input Type: Text"
    echo ""
    echo "   Action 2: 'Get Contents of URL'"
    echo "   - URL: http://[YOUR-MAC-IP]:3000/whatsapp-store"
    echo "   - Method: POST"
    echo "   - Request Body: [Output from Action 1]"
    echo ""
    echo "   Action 3: 'Show Result'"
    echo "   - Shows: [Contents of URL]"
    echo ""
    echo "Step 3: Usage"
    echo "   1. Export WhatsApp chat (Share → Export Chat → Without Media)"
    echo "   2. Copy the exported text"
    echo "   3. Run your iOS Shortcut"
    echo "   4. Paste the WhatsApp text"
    echo "   5. ✅ Auto-stored to Basic Memory!"
    echo ""
    echo "💡 Find your Mac IP: System Preferences → Network"
    echo "🔍 View stored chats: basic-memory tool search-notes whatsapp"
}

# Export all functions
export -f brain win blocker unblock capture find_memory save_session load_session heal startup git_status backup wa_status wa_auth wa_bridge_start wa_bridge_stop wa_memory_store wa_test_connection wa_alternative wa_ios_start wa_ios_setup

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
alias bgit="git_status"
alias bbackup="backup"

# WhatsApp aliases
alias wa="wa_status"
alias wa-auth="wa_auth"
alias wa-start="wa_bridge_start"  
alias wa-stop="wa_bridge_stop"
alias wa-store="wa_memory_store"
alias wa-test="wa_test_connection"
alias wa-alt="wa_alternative"
alias wa-ios="wa_ios_start"
alias wa-setup="wa_ios_setup"

echo "🧠 Brain Core Loaded!"
echo "Commands: b (status), w (win), bl (blocker), c (capture), f (find)"
echo "WhatsApp: wa-setup (iOS setup), wa-ios (start bridge), wa-alt (alternatives)"
echo "Start with: bstart"