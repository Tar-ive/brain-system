#!/bin/bash
# Setup automatic hourly backups for brain system

echo "🔄 Setting up automatic hourly backups..."

BRAIN_DIR="/Users/$(whoami)/brain-poc"

# Create the cron script
cat > "$BRAIN_DIR/cron_backup.sh" << 'EOF'
#!/bin/bash
# Brain system hourly backup
# This runs every hour to commit and push changes

BRAIN_DIR="/Users/$(whoami)/brain-poc"
cd "$BRAIN_DIR"

# Run auto-commit
/usr/bin/python3 "$BRAIN_DIR/auto_commit.py" check >> "$BRAIN_DIR/backup.log" 2>&1

# Log the action
echo "[$(date)] Auto-backup check completed" >> "$BRAIN_DIR/backup.log"

# Keep log file size manageable (last 100 lines)
tail -100 "$BRAIN_DIR/backup.log" > "$BRAIN_DIR/backup.log.tmp"
mv "$BRAIN_DIR/backup.log.tmp" "$BRAIN_DIR/backup.log"
EOF

chmod +x "$BRAIN_DIR/cron_backup.sh"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "cron_backup.sh"; then
    echo "✅ Cron job already exists"
else
    # Add to crontab (every hour at minute 0)
    (crontab -l 2>/dev/null; echo "0 * * * * $BRAIN_DIR/cron_backup.sh") | crontab -
    echo "✅ Cron job added for hourly backups"
fi

# Create launchd alternative for macOS (more reliable)
PLIST_FILE="$HOME/Library/LaunchAgents/com.brain.autobackup.plist"

cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.brain.autobackup</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$BRAIN_DIR/auto_commit.py</string>
        <string>check</string>
    </array>
    
    <key>StartInterval</key>
    <integer>3600</integer> <!-- Run every hour (3600 seconds) -->
    
    <key>WorkingDirectory</key>
    <string>$BRAIN_DIR</string>
    
    <key>StandardOutPath</key>
    <string>$BRAIN_DIR/backup.log</string>
    
    <key>StandardErrorPath</key>
    <string>$BRAIN_DIR/backup_error.log</string>
    
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF

# Load the launch agent
launchctl unload "$PLIST_FILE" 2>/dev/null
launchctl load "$PLIST_FILE"

echo "✅ LaunchAgent created for macOS"
echo ""
echo "🎯 Automatic backups configured:"
echo "  - Every hour at :00"
echo "  - Commits and pushes changes to GitHub"
echo "  - Logs saved to: $BRAIN_DIR/backup.log"
echo ""
echo "📊 Check backup status with: bgit"
echo "💾 Force backup with: bbackup"
echo ""
echo "To disable:"
echo "  Cron: crontab -e (remove the line)"
echo "  LaunchAgent: launchctl unload $PLIST_FILE"