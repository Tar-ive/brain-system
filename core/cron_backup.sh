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
