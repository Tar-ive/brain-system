#!/bin/bash

# Quick upload script for Google Drive
# Usage: ./quick_gdrive_upload.sh

echo "Quick Google Drive Upload Script"
echo "================================="
echo ""

# Check if rclone is configured
if ! rclone listremotes | grep -q "gdrive:"; then
    echo "Error: Google Drive remote 'gdrive:' not found!"
    echo "Please run: ./setup_rclone_gdrive.sh first"
    exit 1
fi

# Create a folder with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FOLDER_NAME="eed_system_backup_${TIMESTAMP}"

echo "Creating folder on Google Drive: ${FOLDER_NAME}"

# Upload the tar file
echo "Uploading eed_system_files.tar.gz..."
rclone copy eed_system_files.tar.gz gdrive:${FOLDER_NAME}/ -v

# Upload individual files too
echo "Uploading individual files..."
rclone copy ever_expanding_dataset_system_design.md gdrive:${FOLDER_NAME}/ -v
rclone copy eed_system gdrive:${FOLDER_NAME}/eed_system/ -v

echo ""
echo "Upload complete! Files are in Google Drive folder: ${FOLDER_NAME}"
echo ""
echo "You can also view them with:"
echo "rclone ls gdrive:${FOLDER_NAME}/"