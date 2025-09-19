#!/bin/bash

# Setup automatic sync using cron
# This will sync every hour

SCRIPT_PATH="/home/tarive/autosync_to_gdrive.sh"
CRON_SCHEDULE="0 * * * *"  # Every hour at minute 0

# Function to add cron job
add_cron_job() {
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "$SCRIPT_PATH"; then
        echo "Cron job already exists for autosync"
    else
        # Add new cron job
        (crontab -l 2>/dev/null; echo "$CRON_SCHEDULE $SCRIPT_PATH") | crontab -
        echo "Cron job added: Syncing every hour"
    fi
}

# Function to setup systemd timer (alternative to cron)
setup_systemd_timer() {
    # Create service file
    sudo tee /etc/systemd/system/gdrive-sync.service > /dev/null <<EOF
[Unit]
Description=Sync files to Google Drive
After=network.target

[Service]
Type=oneshot
User=$USER
ExecStart=$SCRIPT_PATH
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Create timer file
    sudo tee /etc/systemd/system/gdrive-sync.timer > /dev/null <<EOF
[Unit]
Description=Run Google Drive sync every hour
Requires=gdrive-sync.service

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
EOF

    # Enable and start timer
    sudo systemctl daemon-reload
    sudo systemctl enable gdrive-sync.timer
    sudo systemctl start gdrive-sync.timer

    echo "Systemd timer configured and started"
}

echo "Setting up automatic sync to Google Drive"
echo "=========================================="
echo ""
echo "Choose sync method:"
echo "1) Cron (traditional, simple)"
echo "2) Systemd timer (modern, more features)"
echo "3) Both (redundant but safe)"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        add_cron_job
        echo ""
        echo "View cron jobs with: crontab -l"
        ;;
    2)
        setup_systemd_timer
        echo ""
        echo "Check timer status with: systemctl status gdrive-sync.timer"
        echo "View logs with: journalctl -u gdrive-sync"
        ;;
    3)
        add_cron_job
        setup_systemd_timer
        echo ""
        echo "Both methods configured!"
        ;;
    *)
        echo "Invalid choice. Using cron by default."
        add_cron_job
        ;;
esac

echo ""
echo "Manual sync command: $SCRIPT_PATH"