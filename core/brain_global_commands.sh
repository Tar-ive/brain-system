#!/bin/bash
# Global Brain Commands - Available across all shells and Claude sessions
# Integrates unified XML brain system with existing brain infrastructure

# Configuration
BRAIN_POC_DIR="/Users/tarive/brain-poc"
UNIFIED_BRAIN="$BRAIN_POC_DIR/unified_xml_brain.py"
GLOBAL_HELP="$BRAIN_POC_DIR/brain_help_global.py"

# Ensure scripts are executable
chmod +x "$UNIFIED_BRAIN" "$GLOBAL_HELP" 2>/dev/null

# Global brain help command (works everywhere)
brain_help() {
    python3 "$GLOBAL_HELP" help "$@"
}

# Store information with XML tags
brain_store() {
    if [ $# -eq 0 ]; then
        echo "Usage: brain_store \"<tag>content</tag> additional context\""
        echo "Example: brain_store \"<people>baby</people> loves spicy chutney\""
        return 1
    fi
    
    local content="$*"
    echo "🧠 Storing: $content"
    python3 "$UNIFIED_BRAIN" store "$content"
    
    # Also store in existing simple brain for backwards compatibility
    if [ -f "$BRAIN_POC_DIR/simple_brain.py" ]; then
        python3 "$BRAIN_POC_DIR/simple_brain.py" store "$content" 2>/dev/null
    fi
}

# Search across all brain systems
brain_search() {
    if [ $# -eq 0 ]; then
        echo "Usage: brain_search \"query\" [--dim dimension] [--tag xmltag]"
        echo "Examples:"
        echo "  brain_search \"job applications\""
        echo "  brain_search \"research\" --dim research"
        echo "  brain_search \"baby\" --tag people"
        return 1
    fi
    
    echo "🔍 Searching brain for: $*"
    python3 "$UNIFIED_BRAIN" search "$@"
}

# View entries for specific dimension
brain_dimension() {
    if [ $# -eq 0 ]; then
        echo "Usage: brain_dimension [personal|work|research|uni|startup]"
        return 1
    fi
    
    local dimension="$1"
    echo "📊 Dimension: $dimension"
    python3 "$UNIFIED_BRAIN" dimension "$dimension"
}

# Export dimension as XML
brain_export() {
    if [ $# -eq 0 ]; then
        echo "Usage: brain_export [personal|work|research|uni|startup]"
        return 1
    fi
    
    local dimension="$1"
    echo "📦 Exporting dimension: $dimension"
    python3 "$UNIFIED_BRAIN" export "$dimension"
}

# Show comprehensive brain system status
brain_status() {
    echo "🧠 UNIFIED BRAIN SYSTEM STATUS"
    echo "================================"
    echo ""
    
    # Unified system status
    if [ -f "$UNIFIED_BRAIN" ]; then
        echo "✅ Unified XML Brain: Available"
    else
        echo "❌ Unified XML Brain: Missing"
    fi
    
    # Legacy systems status
    if [ -f "$BRAIN_POC_DIR/simple_brain.py" ]; then
        echo "✅ Simple Brain: Available"
    else
        echo "❌ Simple Brain: Missing"
    fi
    
    if [ -f "$BRAIN_POC_DIR/goal_keeper.py" ]; then
        echo "✅ Goal Keeper: Available"
    else
        echo "❌ Goal Keeper: Missing"
    fi
    
    if [ -d "$BRAIN_POC_DIR/working-memory" ]; then
        echo "✅ Working Memory: Available"
        local wm_count=$(find "$BRAIN_POC_DIR/working-memory" -name "wm_*.json" 2>/dev/null | wc -l)
        echo "   📁 Working Memory Items: $wm_count"
    else
        echo "❌ Working Memory: Missing"
    fi
    
    # Basic Memory status
    if command -v basic-memory >/dev/null 2>&1; then
        echo "✅ Basic Memory: Available"
        basic-memory status 2>/dev/null | head -3
    else
        echo "❌ Basic Memory: Not installed"
    fi
    
    # Obsidian sync check
    local obsidian_path="/Users/tarive/Library/Mobile Documents/iCloud~md~obsidian/Documents/Saksham/brain-system"
    if [ -d "$obsidian_path" ]; then
        echo "✅ Obsidian Sync: Available"
        local obs_files=$(find "$obsidian_path" -name "*.md" 2>/dev/null | wc -l)
        echo "   📄 Obsidian Files: $obs_files"
    else
        echo "❌ Obsidian Sync: Path not found"
    fi
    
    echo ""
    echo "📊 DIMENSIONAL SUMMARY:"
    python3 "$GLOBAL_HELP" status 2>/dev/null | grep "📊" -A 10 2>/dev/null || echo "   Run setup to initialize dimensions"
}

# Quick dimension shortcuts
brain_personal() {
    brain_dimension "personal"
}

brain_work() {
    brain_dimension "work"  
}

brain_research() {
    brain_dimension "research"
}

brain_uni() {
    brain_dimension "uni"
}

brain_startup() {
    brain_dimension "startup"
}

# Quick XML tag shortcuts for common patterns
store_people() {
    if [ $# -eq 0 ]; then
        echo "Usage: store_people \"person_name additional_context\""
        return 1
    fi
    brain_store "<people>$*</people>"
}

store_project() {
    if [ $# -eq 0 ]; then
        echo "Usage: store_project \"project_name additional_context\""
        return 1
    fi
    brain_store "<project>$*</project>"
}

store_research() {
    if [ $# -eq 0 ]; then
        echo "Usage: store_research \"research_insight\""
        return 1
    fi
    brain_store "<research>$*</research>"
}

store_goal() {
    if [ $# -eq 0 ]; then
        echo "Usage: store_goal \"goal_description\""
        return 1
    fi
    brain_store "<goals>$*</goals>"
}

store_chore() {
    if [ $# -eq 0 ]; then
        echo "Usage: store_chore \"task_description\""
        return 1
    fi
    brain_store "<chores>$*</chores>"
}

store_brain_feature() {
    if [ $# -eq 0 ]; then
        echo "Usage: store_brain_feature \"feature_description\""
        return 1
    fi
    brain_store "<bfeatures>$*</bfeatures>"
}

# Integration with existing brain system
alias bh_xml="brain_help"
alias bs_xml="brain_store"
alias bf_xml="brain_search"
alias bst_xml="brain_status"

# Backward compatibility aliases
alias brain="brain_status"
alias bhelp="brain_help"

# Integration with existing brain-poc system
if [ -f "$BRAIN_POC_DIR/brain_core.sh" ]; then
    source "$BRAIN_POC_DIR/brain_core.sh" 2>/dev/null
fi

# Export all functions for sub-shells
export -f brain_help brain_store brain_search brain_dimension brain_export brain_status
export -f brain_personal brain_work brain_research brain_uni brain_startup  
export -f store_people store_project store_research store_goal store_chore store_brain_feature

# Setup function for first-time initialization
brain_setup() {
    echo "🚀 Setting up Unified Brain System..."
    
    # Create necessary directories
    mkdir -p "$BRAIN_POC_DIR"
    
    # Initialize unified brain system
    if [ -f "$UNIFIED_BRAIN" ]; then
        echo "✅ Unified brain system initialized"
        python3 "$UNIFIED_BRAIN" help
    else
        echo "❌ Unified brain system files missing"
        return 1
    fi
    
    # Setup shell integration
    local shell_config=""
    if [ -n "$ZSH_VERSION" ]; then
        shell_config="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        shell_config="$HOME/.bashrc"
    fi
    
    if [ -n "$shell_config" ]; then
        local source_line="source \"$BRAIN_POC_DIR/brain_global_commands.sh\""
        if ! grep -q "$source_line" "$shell_config" 2>/dev/null; then
            echo "" >> "$shell_config"
            echo "# Unified Brain System" >> "$shell_config"
            echo "$source_line" >> "$shell_config"
            echo "✅ Added brain system to $shell_config"
            echo "Run 'source $shell_config' or restart terminal to activate"
        else
            echo "✅ Brain system already integrated in $shell_config"
        fi
    fi
    
    echo ""
    echo "🎉 Setup complete! Available commands:"
    echo "  brain_help    - Show comprehensive help"
    echo "  brain_store   - Store with XML tags"
    echo "  brain_search  - Search across dimensions"
    echo "  brain_status  - System health check"
    echo ""
    echo "Quick shortcuts:"
    echo "  store_people \"name context\"   - <people>name context</people>"
    echo "  store_project \"project info\"  - <project>project info</project>"  
    echo "  store_research \"insight\"      - <research>insight</research>"
    echo "  store_goal \"goal\"             - <goals>goal</goals>"
    echo ""
    echo "Try: brain_help --detailed"
}

# Auto-setup check
if [ ! -f "$HOME/.brain_setup_complete" ] && [ -t 1 ]; then
    echo "🧠 Unified Brain System available! Run 'brain_setup' for first-time setup."
fi

# Mark functions as loaded
export BRAIN_GLOBAL_LOADED=1

echo "🧠 Unified Brain System loaded. Type 'brain_help' for usage guide."