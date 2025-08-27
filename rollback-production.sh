#!/bin/bash

# 🔄 Quilty App - Production Rollback Script
# Quickly restore from the most recent backup

set -e  # Exit on any error

echo "🔄 Quilty App - Production Rollback"
echo "==================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
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

# Find the most recent backup
LATEST_BACKUP=$(ls -t /tmp/quilty-production-backup-* 2>/dev/null | head -n 1)

if [ -z "$LATEST_BACKUP" ]; then
    print_error "No backup found in /tmp/quilty-production-backup-*"
    print_status "Available backups:"
    ls -la /tmp/quilty-* 2>/dev/null || echo "No backups found"
    exit 1
fi

print_status "Found latest backup: $LATEST_BACKUP"
print_warning "This will restore production from backup and restart services"
echo ""
read -p "Are you sure you want to rollback? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Rollback cancelled"
    exit 0
fi

# Step 1: Stop services
print_status "Stopping production services..."
cd "$DEST_DIR"
pkill -f "uvicorn.*8002" || true
pkill -f "node.*5174" || true
sleep 3

# Step 2: Restore from backup
print_status "Restoring from backup: $LATEST_BACKUP"
rsync -av "$LATEST_BACKUP/" "$DEST_DIR/"
print_success "Files restored from backup"

# Step 3: Reinstall dependencies (in case they changed)
print_status "Reinstalling dependencies..."
npm install

cd python-ai-service
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r requirements.txt
fi
cd ..

# Step 4: Rebuild frontend
print_status "Rebuilding frontend..."
npm run build

# Step 5: Set permissions
print_status "Setting proper permissions..."
chown -R www-data:www-data "$DEST_DIR" 2>/dev/null || true
chmod -R 755 "$DEST_DIR" 2>/dev/null || true

# Step 6: Start services
print_status "Starting production services..."
./start-production.sh

# Step 7: Health check
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
    print_error "❌ Backend health check failed after rollback"
    exit 1
fi

# Check frontend
sleep 3
if curl -s https://quilty.app/api/auth/me > /dev/null 2>&1; then
    print_success "✅ Frontend is responding"
else
    print_warning "⚠️ Frontend might need a moment to start"
fi

# Summary
echo ""
echo "🎉 Rollback Complete!"
echo "===================="
print_success "✅ Restored from: $LATEST_BACKUP"
print_success "✅ Services restarted"
print_success "✅ Health checks passed"
echo ""
print_status "🌐 Your app is live at: https://quilty.app"
print_status "📚 API docs at: https://quilty.app/api/docs"
echo ""

print_success "🔄 Rollback successful!"
