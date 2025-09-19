#!/bin/bash
# Setup automatic Obsidian sync every 30 minutes

echo "🔧 Setting up automatic Obsidian sync..."

# Create the cron script
cat > /Users/tarive/brain-poc/auto_obsidian_sync.sh << 'EOF'
#!/bin/bash
# Auto sync to Obsidian

# Run global sync silently
python3 /Users/tarive/brain-poc/global_obsidian_sync.py > /Users/tarive/brain-poc/.last_sync.log 2>&1

# Check if successful
if [ $? -eq 0 ]; then
    echo "$(date): Sync successful" >> /Users/tarive/brain-poc/.sync_history.log
else
    echo "$(date): Sync failed" >> /Users/tarive/brain-poc/.sync_history.log
fi
EOF

chmod +x /Users/tarive/brain-poc/auto_obsidian_sync.sh

# Add to crontab (every 30 minutes)
(crontab -l 2>/dev/null | grep -v "auto_obsidian_sync.sh"; echo "*/30 * * * * /Users/tarive/brain-poc/auto_obsidian_sync.sh") | crontab -

echo "✅ Auto-sync configured to run every 30 minutes"
echo "📝 Logs will be saved to:"
echo "   - .last_sync.log (latest sync output)"
echo "   - .sync_history.log (sync history)"
echo ""
echo "To check cron status: crontab -l"
echo "To disable: crontab -e (and remove the line)"