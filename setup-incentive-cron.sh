#!/bin/bash

# Film Incentive Data Update Cron Job Setup
# This script sets up automated daily updates for film incentive data

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/home/dwood/lolita"
PYTHON_SERVICE_DIR="$PROJECT_ROOT/python-ai-service"
VENV_PATH="$PYTHON_SERVICE_DIR/venv"
UPDATER_SCRIPT="$PYTHON_SERVICE_DIR/incentive_updater.py"
LOG_DIR="$PROJECT_ROOT/logs"
CRON_LOG="$LOG_DIR/incentive-updater-cron.log"

echo -e "${BLUE}🚀 Setting up Film Incentive Data Update Cron Job${NC}"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}❌ Virtual environment not found at $VENV_PATH${NC}"
    echo -e "${YELLOW}Please run the setup script first to create the virtual environment${NC}"
    exit 1
fi

# Check if updater script exists
if [ ! -f "$UPDATER_SCRIPT" ]; then
    echo -e "${RED}❌ Updater script not found at $UPDATER_SCRIPT${NC}"
    exit 1
fi

# Test the updater script
echo -e "${YELLOW}🧪 Testing incentive updater script...${NC}"
cd "$PYTHON_SERVICE_DIR"
source "$VENV_PATH/bin/activate"

if python "$UPDATER_SCRIPT" --health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Updater script test passed${NC}"
else
    echo -e "${RED}❌ Updater script test failed${NC}"
    echo -e "${YELLOW}Please check the script and dependencies${NC}"
    exit 1
fi

# Create the cron job script
CRON_SCRIPT="$PROJECT_ROOT/run-incentive-update.sh"

cat > "$CRON_SCRIPT" << 'EOF'
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
EOF

# Make the cron script executable
chmod +x "$CRON_SCRIPT"

echo -e "${GREEN}✅ Created cron runner script at $CRON_SCRIPT${NC}"

# Create the cron job entry
CRON_ENTRY="0 2 * * * $CRON_SCRIPT"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$CRON_SCRIPT"; then
    echo -e "${YELLOW}⚠️  Cron job already exists${NC}"
    echo -e "${BLUE}Current cron jobs:${NC}"
    crontab -l | grep "$CRON_SCRIPT"
else
    # Add the cron job
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
    echo -e "${GREEN}✅ Added cron job: $CRON_ENTRY${NC}"
fi

# Create additional utility scripts

# Health check script
HEALTH_CHECK_SCRIPT="$PROJECT_ROOT/check-incentive-sources.sh"
cat > "$HEALTH_CHECK_SCRIPT" << 'EOF'
#!/bin/bash

# Film Incentive Sources Health Check
# Quick script to check the health of incentive data sources

PROJECT_ROOT="/home/dwood/lolita"
PYTHON_SERVICE_DIR="$PROJECT_ROOT/python-ai-service"
VENV_PATH="$PYTHON_SERVICE_DIR/venv"
UPDATER_SCRIPT="$PYTHON_SERVICE_DIR/incentive_updater.py"

cd "$PYTHON_SERVICE_DIR"
source "$VENV_PATH/bin/activate"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
fi

python "$UPDATER_SCRIPT" --health
EOF

chmod +x "$HEALTH_CHECK_SCRIPT"
echo -e "${GREEN}✅ Created health check script at $HEALTH_CHECK_SCRIPT${NC}"

# Manual update script
MANUAL_UPDATE_SCRIPT="$PROJECT_ROOT/update-incentives-now.sh"
cat > "$MANUAL_UPDATE_SCRIPT" << 'EOF'
#!/bin/bash

# Manual Film Incentive Data Update
# Run this script to manually update incentive data

PROJECT_ROOT="/home/dwood/lolita"
PYTHON_SERVICE_DIR="$PROJECT_ROOT/python-ai-service"
VENV_PATH="$PYTHON_SERVICE_DIR/venv"
UPDATER_SCRIPT="$PYTHON_SERVICE_DIR/incentive_updater.py"

echo "🚀 Starting manual incentive data update..."

cd "$PYTHON_SERVICE_DIR"
source "$VENV_PATH/bin/activate"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
fi

python "$UPDATER_SCRIPT" --update --verbose

echo "✅ Manual update completed"
EOF

chmod +x "$MANUAL_UPDATE_SCRIPT"
echo -e "${GREEN}✅ Created manual update script at $MANUAL_UPDATE_SCRIPT${NC}"

# Create log rotation script
LOG_ROTATION_SCRIPT="$PROJECT_ROOT/rotate-incentive-logs.sh"
cat > "$LOG_ROTATION_SCRIPT" << 'EOF'
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
EOF

chmod +x "$LOG_ROTATION_SCRIPT"
echo -e "${GREEN}✅ Created log rotation script at $LOG_ROTATION_SCRIPT${NC}"

# Add weekly log rotation to cron
LOG_ROTATION_CRON="0 3 * * 0 $LOG_ROTATION_SCRIPT"
if ! crontab -l 2>/dev/null | grep -q "$LOG_ROTATION_SCRIPT"; then
    (crontab -l 2>/dev/null; echo "$LOG_ROTATION_CRON") | crontab -
    echo -e "${GREEN}✅ Added weekly log rotation cron job${NC}"
fi

echo ""
echo -e "${BLUE}📋 Setup Summary:${NC}"
echo -e "${GREEN}✅ Daily incentive update: 2:00 AM${NC}"
echo -e "${GREEN}✅ Weekly log rotation: 3:00 AM Sunday${NC}"
echo -e "${GREEN}✅ Manual update script: $MANUAL_UPDATE_SCRIPT${NC}"
echo -e "${GREEN}✅ Health check script: $HEALTH_CHECK_SCRIPT${NC}"
echo -e "${GREEN}✅ Log files: $LOG_DIR/${NC}"

echo ""
echo -e "${BLUE}🔧 Useful Commands:${NC}"
echo -e "${YELLOW}Check cron jobs:${NC} crontab -l"
echo -e "${YELLOW}View logs:${NC} tail -f $CRON_LOG"
echo -e "${YELLOW}Manual update:${NC} $MANUAL_UPDATE_SCRIPT"
echo -e "${YELLOW}Health check:${NC} $HEALTH_CHECK_SCRIPT"
echo -e "${YELLOW}Test update:${NC} cd $PYTHON_SERVICE_DIR && source venv/bin/activate && python incentive_updater.py --health"

echo ""
echo -e "${GREEN}🎉 Incentive data update automation setup complete!${NC}"
echo -e "${BLUE}The system will now automatically update incentive data daily at 2:00 AM${NC}"
