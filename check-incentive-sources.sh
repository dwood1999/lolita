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
