#!/bin/bash

# Log Rotation for Incentive Updater
# Rotate and compress old log files

LOG_DIR="/home/dwood/lolita/logs"
CRON_LOG="$LOG_DIR/incentive-updater-cron.log"
UPDATER_LOG="$LOG_DIR/incentive_updater.log"

# Rotate cron log
if [ -f "$CRON_LOG" ] && [ $(stat -c%s "$CRON_LOG") -gt 10485760 ]; then  # 10MB
    mv "$CRON_LOG" "$CRON_LOG.$(date +%Y%m%d)"
    gzip "$CRON_LOG.$(date +%Y%m%d)"
    touch "$CRON_LOG"
fi

# Rotate updater log
if [ -f "$UPDATER_LOG" ] && [ $(stat -c%s "$UPDATER_LOG") -gt 10485760 ]; then  # 10MB
    mv "$UPDATER_LOG" "$UPDATER_LOG.$(date +%Y%m%d)"
    gzip "$UPDATER_LOG.$(date +%Y%m%d)"
    touch "$UPDATER_LOG"
fi

# Clean up old compressed logs (keep 30 days)
find "$LOG_DIR" -name "*.gz" -mtime +30 -delete
