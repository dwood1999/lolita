#!/bin/bash

# 🔍 Quilty App - Production Status Checker
# Check if production services are running and healthy

echo "🔍 Quilty App - Production Status"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check backend service
print_status "Checking backend service (port 8002)..."
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    print_success "✅ Backend is running and healthy"
    BACKEND_RESPONSE=$(curl -s http://localhost:8002/health | head -c 100)
    echo "   Response: $BACKEND_RESPONSE"
else
    print_error "❌ Backend is not responding"
fi

# Check frontend service
print_status "Checking frontend service..."
if curl -s https://quilty.app/api/auth/me > /dev/null 2>&1; then
    print_success "✅ Frontend is accessible"
else
    print_warning "⚠️ Frontend might not be responding"
fi

# Check processes
print_status "Checking running processes..."
BACKEND_PID=$(pgrep -f "uvicorn.*8002" || echo "")
FRONTEND_PID=$(pgrep -f "node.*5174" || echo "")

if [ -n "$BACKEND_PID" ]; then
    print_success "✅ Backend process running (PID: $BACKEND_PID)"
else
    print_error "❌ No backend process found"
fi

if [ -n "$FRONTEND_PID" ]; then
    print_success "✅ Frontend process running (PID: $FRONTEND_PID)"
else
    print_error "❌ No frontend process found"
fi

# Check disk space
print_status "Checking disk space..."
DISK_USAGE=$(df /var/www/vhosts/quilty.app/lolita | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    print_success "✅ Disk usage: ${DISK_USAGE}%"
else
    print_warning "⚠️ Disk usage high: ${DISK_USAGE}%"
fi

# Check recent logs
print_status "Checking recent logs..."
if [ -f "/var/log/quilty-backend.log" ]; then
    BACKEND_ERRORS=$(tail -50 /var/log/quilty-backend.log | grep -i error | wc -l)
    if [ "$BACKEND_ERRORS" -eq 0 ]; then
        print_success "✅ No recent backend errors"
    else
        print_warning "⚠️ Found $BACKEND_ERRORS recent backend errors"
    fi
else
    print_warning "⚠️ Backend log file not found"
fi

if [ -f "/var/log/quilty-frontend.log" ]; then
    FRONTEND_ERRORS=$(tail -50 /var/log/quilty-frontend.log | grep -i error | wc -l)
    if [ "$FRONTEND_ERRORS" -eq 0 ]; then
        print_success "✅ No recent frontend errors"
    else
        print_warning "⚠️ Found $FRONTEND_ERRORS recent frontend errors"
    fi
else
    print_warning "⚠️ Frontend log file not found"
fi

# Summary
echo ""
echo "🌐 Production URLs:"
echo "   Website: https://quilty.app"
echo "   API Docs: https://quilty.app/api/docs"
echo "   Health Check: https://quilty.app/api/auth/me"
echo ""

# Check if everything is healthy
if [ -n "$BACKEND_PID" ] && [ -n "$FRONTEND_PID" ] && curl -s http://localhost:8002/health > /dev/null 2>&1; then
    print_success "🎉 Production is healthy and running!"
else
    print_error "⚠️ Production has issues - consider restarting services"
    echo ""
    echo "To restart services:"
    echo "   cd /var/www/vhosts/quilty.app/lolita"
    echo "   ./start-production.sh"
fi
