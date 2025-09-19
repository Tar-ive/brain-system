#!/bin/bash

# Autosync script for Google Drive
# This script syncs local folders to Google Drive

# Configuration
LOCAL_DIR="/home/tarive"
GDRIVE_DIR="gdrive:eed_system_project"
LOG_FILE="/home/tarive/sync_gdrive.log"

# Folders to sync
SYNC_FOLDERS=(
    "eed_system"
    "ever_expanding_dataset_system_design.md"
    "eed_system_files.tar.gz"
)

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Main sync function
sync_to_gdrive() {
    log_message "Starting sync to Google Drive..."

    for item in "${SYNC_FOLDERS[@]}"; do
        if [ -e "$LOCAL_DIR/$item" ]; then
            log_message "Syncing $item..."
            if [ -d "$LOCAL_DIR/$item" ]; then
                # It's a directory
                rclone sync "$LOCAL_DIR/$item" "$GDRIVE_DIR/$item" \
                    --exclude "*.pyc" \
                    --exclude "__pycache__/" \
                    --exclude ".git/" \
                    -v 2>&1 | tee -a "$LOG_FILE"
            else
                # It's a file
                rclone copy "$LOCAL_DIR/$item" "$GDRIVE_DIR/" -v 2>&1 | tee -a "$LOG_FILE"
            fi
        else
            log_message "Warning: $item not found, skipping..."
        fi
    done

    log_message "Sync completed!"
}

# Run the sync
sync_to_gdrive

# Display summary
echo ""
echo "Sync Summary:"
echo "============="
rclone ls "$GDRIVE_DIR" --max-depth 2