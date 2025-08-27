#!/bin/bash

# 🚀 Quilty App - Quick Deploy (No Build)
# Fast sync for small changes without full rebuild

set -e  # Exit on any error

echo "⚡ Quilty App - Quick Deploy"
echo "============================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SOURCE_DIR="/home/dwood/lolita"
DEST_DIR="/var/www/vhosts/quilty.app/lolita"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Safety checks
if [ ! -d "$SOURCE_DIR" ]; then
    print_error "Source directory $SOURCE_DIR does not exist!"
    exit 1
fi

if [ ! -d "$DEST_DIR" ]; then
    print_error "Destination directory $DEST_DIR does not exist!"
    exit 1
fi

print_status "Quick deploying changes from $SOURCE_DIR to $DEST_DIR..."

# Step 1: Sync only source files (no dependencies or build)
print_status "Syncing source files..."
rsync -av \
    --exclude='node_modules/' \
    --exclude='python-ai-service/venv/' \
    --exclude='python-ai-service/__pycache__/' \
    --exclude='*.log' \
    --exclude='*.pid' \
    --exclude='.git/' \
    --exclude='logs/' \
    --exclude='uploads/' \
    --exclude='static/posters/' \
    --exclude='screenplay_analysis.db' \
    --exclude='service.pid' \
    --exclude='frontend-dev.log' \
    --exclude='package-lock.json' \
    "$SOURCE_DIR/src/" "$DEST_DIR/src/" \
    "$SOURCE_DIR/python-ai-service/*.py" "$DEST_DIR/python-ai-service/" \
    "$SOURCE_DIR/static/" "$DEST_DIR/static/" \
    "$SOURCE_DIR/package.json" "$DEST_DIR/" \
    "$SOURCE_DIR/svelte.config.js" "$DEST_DIR/" \
    "$SOURCE_DIR/vite.config.ts" "$DEST_DIR/" \
    "$SOURCE_DIR/tailwind.config.js" "$DEST_DIR/" \
    "$SOURCE_DIR/tsconfig.json" "$DEST_DIR/" 2>/dev/null || true

print_success "Source files synced"

# Step 2: Restart services (they will pick up changes automatically)
print_status "Restarting services..."
cd "$DEST_DIR"
pkill -f "uvicorn.*8002" || true
pkill -f "node.*5174" || true
sleep 2

./start-production.sh

# Step 3: Quick health check
print_status "Quick health check..."
sleep 5

if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    print_success "✅ Backend is responding"
else
    print_warning "⚠️ Backend might need a moment to start"
fi

echo ""
print_success "⚡ Quick deploy complete!"
print_status "🌐 Check your changes at: https://quilty.app"
echo ""
print_warning "Note: This was a quick deploy. If you added new dependencies or made major changes,"
print_warning "consider running the full deployment: ./deploy-to-production.sh"
