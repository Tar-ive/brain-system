#!/bin/bash

# Google Drive Manager Script
# Comprehensive tool for managing Google Drive sync

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
GDRIVE_DIR="gdrive:eed_system_project"
LOCAL_DIR="/home/tarive"
CONFIG_BACKUP="$LOCAL_DIR/rclone_backup.conf"

print_header() {
    echo ""
    echo "===================================="
    echo "    Google Drive Manager"
    echo "===================================="
    echo ""
}

show_menu() {
    echo "Options:"
    echo "  1) Sync now (upload local changes)"
    echo "  2) Download from Drive (overwrite local)"
    echo "  3) Show Drive contents"
    echo "  4) Show sync status"
    echo "  5) Backup rclone config"
    echo "  6) Restore rclone config"
    echo "  7) Show cron schedule"
    echo "  8) Test connection"
    echo "  9) Show recent sync logs"
    echo "  0) Exit"
    echo ""
    read -p "Choose option: " choice
}

sync_to_drive() {
    echo -e "${GREEN}Syncing to Google Drive...${NC}"
    ./autosync_to_gdrive.sh
    echo -e "${GREEN}Sync complete!${NC}"
}

download_from_drive() {
    echo -e "${YELLOW}Warning: This will overwrite local files!${NC}"
    read -p "Are you sure? (y/N): " confirm
    if [[ $confirm == "y" || $confirm == "Y" ]]; then
        echo -e "${GREEN}Downloading from Drive...${NC}"
        rclone sync "$GDRIVE_DIR" "$LOCAL_DIR/eed_system_downloaded" -v
        echo -e "${GREEN}Downloaded to eed_system_downloaded/!${NC}"
    fi
}

show_drive_contents() {
    echo -e "${GREEN}Google Drive contents:${NC}"
    echo "========================"
    rclone tree "$GDRIVE_DIR" --max-depth 3
    echo ""
    echo "Storage usage:"
    rclone size "$GDRIVE_DIR"
}

show_sync_status() {
    echo -e "${GREEN}Sync Status:${NC}"
    echo "============="

    # Check last sync time from log
    if [ -f "$LOCAL_DIR/sync_gdrive.log" ]; then
        last_sync=$(tail -n 100 "$LOCAL_DIR/sync_gdrive.log" | grep "Starting sync" | tail -1)
        echo "Last sync: $last_sync"
    fi

    # Check if cron is running
    if crontab -l 2>/dev/null | grep -q "autosync_to_gdrive.sh"; then
        echo -e "${GREEN}✓ Cron job is active${NC}"
    else
        echo -e "${RED}✗ Cron job is not configured${NC}"
    fi

    # Check Drive accessibility
    if rclone lsd "$GDRIVE_DIR" &>/dev/null; then
        echo -e "${GREEN}✓ Google Drive is accessible${NC}"
    else
        echo -e "${RED}✗ Cannot access Google Drive${NC}"
    fi
}

backup_config() {
    echo -e "${GREEN}Backing up rclone config...${NC}"
    cp /home/tarive/.config/rclone/rclone.conf "$CONFIG_BACKUP"
    rclone copy "$CONFIG_BACKUP" "$GDRIVE_DIR/configs/" -v
    echo -e "${GREEN}Config backed up to Drive!${NC}"
}

restore_config() {
    echo -e "${YELLOW}Restoring rclone config from Drive...${NC}"
    rclone copy "$GDRIVE_DIR/configs/rclone.conf" /tmp/ -v
    if [ -f "/tmp/rclone.conf" ]; then
        cp /tmp/rclone.conf /home/tarive/.config/rclone/rclone.conf
        echo -e "${GREEN}Config restored!${NC}"
    else
        echo -e "${RED}Config not found on Drive!${NC}"
    fi
}

show_cron_schedule() {
    echo -e "${GREEN}Current cron schedule:${NC}"
    crontab -l 2>/dev/null | grep "autosync" || echo "No sync jobs configured"
    echo ""
    echo "Next run times:"
    for i in {1..5}; do
        echo "  $(date -d "+$i hour" '+%Y-%m-%d %H:%M')"
    done
}

test_connection() {
    echo -e "${GREEN}Testing Google Drive connection...${NC}"
    if rclone about gdrive: &>/dev/null; then
        echo -e "${GREEN}✓ Connection successful!${NC}"
        rclone about gdrive: --full
    else
        echo -e "${RED}✗ Connection failed!${NC}"
        echo "Run 'rclone config' to reconfigure"
    fi
}

show_logs() {
    echo -e "${GREEN}Recent sync logs (last 20 lines):${NC}"
    echo "=================================="
    if [ -f "$LOCAL_DIR/sync_gdrive.log" ]; then
        tail -20 "$LOCAL_DIR/sync_gdrive.log"
    else
        echo "No logs found yet"
    fi
}

# Main loop
while true; do
    print_header
    show_menu

    case $choice in
        1) sync_to_drive ;;
        2) download_from_drive ;;
        3) show_drive_contents ;;
        4) show_sync_status ;;
        5) backup_config ;;
        6) restore_config ;;
        7) show_cron_schedule ;;
        8) test_connection ;;
        9) show_logs ;;
        0) echo "Goodbye!"; exit 0 ;;
        *) echo -e "${RED}Invalid option!${NC}" ;;
    esac

    echo ""
    read -p "Press Enter to continue..."
done