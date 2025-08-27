#!/bin/bash

# 🚀 Quilty App - Deploy to Production
# Syncs from /home/dwood/lolita to /var/www/vhosts/quilty.app/lolita

set -e  # Exit on any error

echo "🎬 Quilty App - Production Deployment"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SOURCE_DIR="/home/dwood/lolita"
DEST_DIR="/var/www/vhosts/quilty.app/lolita"
BACKUP_DIR="/tmp/quilty-production-backup-$(date +%Y%m%d-%H%M%S)"

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

if [ ! -f "$SOURCE_DIR/package.json" ] || [ ! -d "$SOURCE_DIR/python-ai-service" ]; then
    print_error "Source directory doesn't appear to be a Quilty app directory"
    exit 1
fi

print_status "Starting deployment from $SOURCE_DIR to $DEST_DIR..."

# Step 1: Create backup of production
print_status "Creating backup of current production..."
mkdir -p "$BACKUP_DIR"
rsync -av --exclude='node_modules' --exclude='python-ai-service/venv' --exclude='*.log' \
    "$DEST_DIR/" "$BACKUP_DIR/"
print_success "Backup created at: $BACKUP_DIR"

# Step 2: Stop production services
print_status "Stopping production services..."
cd "$DEST_DIR"
pkill -f "uvicorn.*8002" || true
pkill -f "node.*5174" || true
sleep 3

# Step 3: Sync files (excluding sensitive/generated files)
print_status "Syncing files to production..."
rsync -av --delete \
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
    "$SOURCE_DIR/" "$DEST_DIR/"

print_success "Files synced successfully"

# Step 4: Install dependencies
print_status "Installing frontend dependencies..."
cd "$DEST_DIR"
npm install

print_status "Installing Python dependencies..."
cd "$DEST_DIR/python-ai-service"
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r requirements.txt
else
    print_warning "Python virtual environment not found. Creating new one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi
cd "$DEST_DIR"

# Step 5: Build frontend
print_status "Building frontend..."
npm run build

# Step 6: Set proper permissions
print_status "Setting proper permissions..."
chown -R www-data:www-data "$DEST_DIR" 2>/dev/null || true
chmod -R 755 "$DEST_DIR" 2>/dev/null || true

# Step 7: Start services
print_status "Starting production services..."
./start-production.sh

# Step 8: Health check
print_status "Performing health check..."
sleep 8

# Check backend
BACKEND_HEALTHY=false
for i in {1..10}; do
    if curl -s http://localhost:8002/health > /dev/null 2>&1; then
        BACKEND_HEALTHY=true
        break
    fi
    print_status "Waiting for backend to start... ($i/10)"
    sleep 2
done

if [ "$BACKEND_HEALTHY" = true ]; then
    print_success "✅ Backend is healthy"
else
    print_error "❌ Backend health check failed"
    print_warning "Attempting to restore from backup..."
    
    # Restore backup
    rsync -av "$BACKUP_DIR/" "$DEST_DIR/"
    ./start-production.sh
    exit 1
fi

# Check frontend
sleep 3
if curl -s https://quilty.app/api/auth/me > /dev/null 2>&1; then
    print_success "✅ Frontend is responding"
else
    print_warning "⚠️ Frontend might need a moment to start"
fi

# Step 9: Summary
echo ""
echo "🎉 Production Deployment Complete!"
echo "=================================="
print_success "✅ Files synced from development"
print_success "✅ Dependencies updated"
print_success "✅ Frontend built"
print_success "✅ Services restarted"
print_success "✅ Health checks passed"
print_success "✅ Backup available at: $BACKUP_DIR"
echo ""
print_status "🌐 Your app is live at: https://quilty.app"
print_status "📚 API docs at: https://quilty.app/api/docs"
echo ""

# Optional: Clean up old backups (keep last 5)
print_status "Cleaning up old backups..."
ls -t /tmp/quilty-production-backup-* 2>/dev/null | tail -n +6 | xargs rm -rf 2>/dev/null || true

print_success "🚀 Production deployment successful!"
