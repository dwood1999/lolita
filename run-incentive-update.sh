#!/bin/bash

# Film Incentive Data Update Cron Job Runner
# This script is executed by cron to update incentive data

# Set environment variables
export PATH="/usr/local/bin:/usr/bin:/bin"
export HOME="/home/dwood"

# Project paths
PROJECT_ROOT="/home/dwood/lolita"
PYTHON_SERVICE_DIR="$PROJECT_ROOT/python-ai-service"
VENV_PATH="$PYTHON_SERVICE_DIR/venv"
UPDATER_SCRIPT="$PYTHON_SERVICE_DIR/incentive_updater.py"
LOG_DIR="$PROJECT_ROOT/logs"
CRON_LOG="$LOG_DIR/incentive-updater-cron.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Log start time
echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting incentive data update" >> "$CRON_LOG"

# Change to project directory
cd "$PYTHON_SERVICE_DIR"

# Activate virtual environment and run updater
if source "$VENV_PATH/bin/activate"; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Virtual environment activated" >> "$CRON_LOG"
    
    # Load environment variables
    if [ -f "$PROJECT_ROOT/.env" ]; then
        export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Environment variables loaded" >> "$CRON_LOG"
    fi
    
    # Run the updater with timeout (30 minutes max)
    if timeout 1800 python "$UPDATER_SCRIPT" --update >> "$CRON_LOG" 2>&1; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Incentive update completed successfully" >> "$CRON_LOG"
        
        # Optional: Send success notification
        # curl -X POST "your-webhook-url" -d "Incentive data updated successfully"
        
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Incentive update failed or timed out" >> "$CRON_LOG"
        
        # Optional: Send failure notification
        # curl -X POST "your-webhook-url" -d "Incentive data update failed"
    fi
    
    deactivate
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Failed to activate virtual environment" >> "$CRON_LOG"
fi

# Log completion
echo "$(date '+%Y-%m-%d %H:%M:%S') - Incentive update job completed" >> "$CRON_LOG"
echo "----------------------------------------" >> "$CRON_LOG"

# Rotate log file if it gets too large (keep last 1000 lines)
if [ -f "$CRON_LOG" ] && [ $(wc -l < "$CRON_LOG") -gt 1000 ]; then
    tail -n 1000 "$CRON_LOG" > "$CRON_LOG.tmp" && mv "$CRON_LOG.tmp" "$CRON_LOG"
fi
