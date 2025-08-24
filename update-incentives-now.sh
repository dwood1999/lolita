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
