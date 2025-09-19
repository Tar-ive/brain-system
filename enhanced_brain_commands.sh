#!/bin/bash
# Enhanced Brain Commands with Natural Language XML Processing
# Supports <remind> and <gmail> tags with automatic parsing

BRAIN_POC_DIR="/Users/tarive/brain-poc"
ENHANCED_BRAIN="$BRAIN_POC_DIR/enhanced_xml_brain.py"
GMAIL_MCP_DIR="$BRAIN_POC_DIR/mcp-gmail"
REMINDERS_MCP_DIR="$BRAIN_POC_DIR/mcp-server-apple-reminders"

# Enhanced brain store command with natural language processing
brain_store_enhanced() {
    if [ $# -eq 0 ]; then
        echo "Usage: brain_store_enhanced \"<tag>content</tag>\""
        echo ""
        echo "Enhanced XML Tags:"
        echo "  <remind>wake baby up at 14:45 CST</remind>"
        echo "  <gmail>check how many job application replies I got</gmail>"
        echo "  <people>baby</people> needs care"
        echo "  <project>ybrowser</project> integration progress"
        echo "  <goals>complete O1 visa</goals> by December"
        return 1
    fi
    
    local content="$*"
    echo "🧠 Processing enhanced XML: $content"
    
    python3 "$ENHANCED_BRAIN" store "$content"
}

# Natural language reminder function
remind_me() {
    if [ $# -eq 0 ]; then
        echo "Usage: remind_me \"wake baby up at 14:45 CST\""
        echo "       remind_me \"call mom tomorrow at 2pm\""
        echo "       remind_me \"dentist appointment Friday 10:30am\""
        return 1
    fi
    
    local reminder_text="$*"
    echo "⏰ Setting reminder: $reminder_text"
    
    # Use enhanced brain system
    brain_store_enhanced "<remind>$reminder_text</remind>"
}

# Gmail analysis function
gmail_analyze() {
    if [ $# -eq 0 ]; then
        echo "Usage: gmail_analyze \"check how many job application replies I got\""
        echo "       gmail_analyze \"find emails from founders this week\""
        echo "       gmail_analyze \"show me recruiting emails\""
        return 1
    fi
    
    local analysis_request="$*"
    echo "📧 Gmail analysis: $analysis_request"
    
    # Use enhanced brain system
    brain_store_enhanced "<gmail>$analysis_request</gmail>"
}

# Quick reminder shortcuts
remind_baby() {
    local time_or_task="$1"
    local task="${2:-wake up}"
    
    if [[ "$time_or_task" =~ ^[0-9]{1,2}:[0-9]{2} ]]; then
        # Time provided first
        remind_me "$task baby at $time_or_task CST"
    else
        # Task provided, default time
        remind_me "$time_or_task at $(date -v +1H '+%H:%M') CST"
    fi
}

# Job application tracking
check_job_replies() {
    echo "📊 Analyzing job application responses..."
    gmail_analyze "check how many job application replies I got this week"
}

# Founder outreach tracking  
check_founder_emails() {
    echo "🤝 Analyzing founder communications..."
    gmail_analyze "find emails from founders and startup contacts"
}

# Test enhanced system
test_enhanced_brain() {
    echo "🧪 Testing Enhanced Brain System"
    echo "================================"
    
    echo ""
    echo "1. Testing reminder parsing..."
    remind_me "test reminder at 15:30 CST"
    
    echo ""
    echo "2. Testing Gmail analysis..."
    gmail_analyze "test Gmail integration for job applications"
    
    echo ""
    echo "3. Testing search functionality..."
    python3 "$ENHANCED_BRAIN" search "test"
    
    echo ""
    echo "✅ Enhanced brain system test complete!"
}

# Configure Claude MCP for both Gmail and Apple Reminders
setup_claude_mcp() {
    echo "🔧 Setting up Claude MCP integration..."
    
    # Check if credentials exist
    if [ ! -f "$GMAIL_MCP_DIR/credentials.json" ]; then
        echo "⚠️  Gmail credentials not found!"
        echo "    Please complete Google Cloud setup first:"
        echo "    1. Go to https://console.cloud.google.com/"
        echo "    2. Create project and enable Gmail API"
        echo "    3. Download credentials.json to $GMAIL_MCP_DIR/"
        return 1
    fi
    
    # Backup existing claude config
    if [ -f "$HOME/.claude.json" ]; then
        cp "$HOME/.claude.json" "$HOME/.claude.json.backup.$(date +%Y%m%d_%H%M%S)"
        echo "✅ Backed up existing Claude config"
    fi
    
    # Add Gmail and Apple Reminders MCP servers
    cat > "$HOME/.claude_mcp_addition.json" << 'EOF'
{
  "gmail": {
    "type": "stdio", 
    "command": "uv",
    "args": ["run", "python", "-m", "mcp_gmail"],
    "cwd": "/Users/tarive/brain-poc/mcp-gmail",
    "env": {
      "GMAIL_CREDENTIALS_PATH": "/Users/tarive/brain-poc/mcp-gmail/credentials.json",
      "GMAIL_TOKEN_PATH": "/Users/tarive/brain-poc/mcp-gmail/token.json"
    }
  },
  "apple-reminders": {
    "type": "stdio",
    "command": "node", 
    "args": ["/Users/tarive/brain-poc/mcp-server-apple-reminders/dist/index.js"],
    "env": {}
  }
}
EOF
    
    echo "✅ MCP configuration ready"
    echo "   Gmail MCP: $GMAIL_MCP_DIR"
    echo "   Apple Reminders MCP: $REMINDERS_MCP_DIR"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Restart Claude Desktop"
    echo "   2. Test: remind_me \"test at 15:30 CST\""
    echo "   3. Test: gmail_analyze \"check job replies\""
}

# Status check for all integrations
brain_integrations_status() {
    echo "🧠 BRAIN INTEGRATIONS STATUS"
    echo "=============================="
    
    # Check enhanced brain system
    if [ -f "$ENHANCED_BRAIN" ]; then
        echo "✅ Enhanced XML Brain: Available"
    else
        echo "❌ Enhanced XML Brain: Missing"
    fi
    
    # Check Gmail MCP
    if [ -d "$GMAIL_MCP_DIR" ]; then
        if [ -f "$GMAIL_MCP_DIR/credentials.json" ]; then
            echo "✅ Gmail MCP: Ready (credentials found)"
        else
            echo "⚠️  Gmail MCP: Installed but needs credentials"
        fi
    else
        echo "❌ Gmail MCP: Not installed"
    fi
    
    # Check Apple Reminders MCP
    if [ -d "$REMINDERS_MCP_DIR" ]; then
        if [ -f "$REMINDERS_MCP_DIR/dist/index.js" ]; then
            echo "✅ Apple Reminders MCP: Ready"
        else
            echo "⚠️  Apple Reminders MCP: Needs building (run npm run build)"
        fi
    else
        echo "❌ Apple Reminders MCP: Not installed"
    fi
    
    # Check existing iMessage MCP
    if claude mcp list | grep -q "imessage.*Connected"; then
        echo "✅ iMessage MCP: Connected"
    else
        echo "⚠️  iMessage MCP: Check connection"
    fi
    
    echo ""
    echo "🎯 Available Enhanced Commands:"
    echo "   remind_me \"wake baby up at 14:45 CST\""
    echo "   gmail_analyze \"check job application replies\""
    echo "   check_job_replies"
    echo "   check_founder_emails"
    echo "   brain_store_enhanced \"<tag>content</tag>\""
}

# Export all functions
export -f brain_store_enhanced remind_me gmail_analyze remind_baby 
export -f check_job_replies check_founder_emails test_enhanced_brain
export -f setup_claude_mcp brain_integrations_status

# Quick aliases
alias remind="remind_me"
alias gmail="gmail_analyze"
alias job_replies="check_job_replies" 
alias founder_emails="check_founder_emails"
alias brain_status="brain_integrations_status"

echo "🚀 Enhanced Brain Commands Loaded!"
echo "   Type 'brain_status' to check integration status"
echo "   Type 'test_enhanced_brain' to test functionality"