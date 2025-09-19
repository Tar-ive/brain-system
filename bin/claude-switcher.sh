#!/bin/bash

# Claude Code Environment Switcher
# This script allows you to switch between Claude Code with GLM-4.5 and original Claude

# Path to settings file
SETTINGS_FILE="$HOME/.claude/settings.json"

# Handle different options
if [ $# -eq 0 ]; then
    # No parameters provided, launch original Claude Code
    echo "Launching original Claude Code..."

    # Create settings directory if it doesn't exist
    mkdir -p "$HOME/.claude"

    # Create empty settings file or remove it to use defaults
    if [ -f "$SETTINGS_FILE" ]; then
        # Backup existing settings
        cp "$SETTINGS_FILE" "$SETTINGS_FILE.bak"
        # Create empty settings
        cat > "$SETTINGS_FILE" << EOF_INNER
{
  "env": {}
}
EOF_INNER
    else
        # Create empty settings file
        cat > "$SETTINGS_FILE" << EOF_INNER
{
  "env": {}
}
EOF_INNER
    fi

    # Launch Claude Code
    claude
else
    # Parameters provided, handle them
    case "$1" in
        --zai)
            echo "Setting up Claude Code with GLM-4.5 (Z.AI)..."

            # Check if API key is set
            if [ -z "$ZAI_API_KEY" ]; then
                echo "Error: ZAI_API_KEY environment variable is not set."
                echo "Please set it with: export ZAI_API_KEY=your_api_key_here"
                exit 1
            fi

            # Create settings directory if it doesn't exist
            mkdir -p "$HOME/.claude"

            # Create settings file for Z.AI
            cat > "$SETTINGS_FILE" << EOF_INNER
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "$ZAI_API_KEY",
    "ANTHROPIC_MODEL": "glm-4.5"
  }
}
EOF_INNER

            echo "Configuration updated. Starting Claude Code with GLM-4.5..."
            # Launch Claude Code
            claude
            ;;
            
        --original)
            echo "Setting up original Claude Code..."

            # Create settings directory if it doesn't exist
            mkdir -p "$HOME/.claude"

            # Create empty settings file or remove it to use defaults
            if [ -f "$SETTINGS_FILE" ]; then
                # Backup existing settings
                cp "$SETTINGS_FILE" "$SETTINGS_FILE.bak"
                # Create empty settings
                cat > "$SETTINGS_FILE" << EOF_INNER
{
  "env": {}
}
EOF_INNER
            else
                # Create empty settings file
                cat > "$SETTINGS_FILE" << EOF_INNER
{
                  "env": {}
                }
EOF_INNER
            fi

            echo "Configuration updated. Starting original Claude Code..."
            # Launch Claude Code
            claude
            ;;
            
        --status)
            echo "Current Claude Code environment settings:"
            if [ -f "$SETTINGS_FILE" ]; then
                echo "Settings file exists at: $SETTINGS_FILE"
                echo "Contents:"
                cat "$SETTINGS_FILE"
            else
                echo "No settings file found. Using default Claude Code configuration."
            fi
            ;;
            
        *)
            echo "Unknown option: $1"
            echo "Usage: claude-switcher.sh [option]"
            echo "Options:"
            echo "  (no args) or --original Launch original Claude Code"
            echo "  --zai      Launch Claude Code with GLM-4.5 (Z.AI)"
            echo "  --status   Show current environment settings"
            exit 1
            ;;
    esac
fi
