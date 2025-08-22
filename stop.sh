#!/bin/bash

# Lolita Screenplay Analysis Tool - Stop Script
# Usage: ./stop.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎬 Lolita Screenplay Analysis Tool - Stop Services${NC}"
echo -e "${BLUE}===================================================${NC}"
echo ""

# Function to stop service by PID file
stop_service_by_pid() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file" 2>/dev/null)
        if [ ! -z "$pid" ] && kill -0 $pid 2>/dev/null; then
            echo -e "${YELLOW}🛑 Stopping $service_name (PID: $pid)...${NC}"
            kill $pid
            
            # Wait for graceful shutdown
            local count=0
            while kill -0 $pid 2>/dev/null && [ $count -lt 10 ]; do
                sleep 1
                ((count++))
            done
            
            # Force kill if still running
            if kill -0 $pid 2>/dev/null; then
                echo -e "${YELLOW}   Force killing $service_name...${NC}"
                kill -9 $pid 2>/dev/null || true
            fi
            
            echo -e "${GREEN}✅ $service_name stopped${NC}"
        else
            echo -e "${YELLOW}⚠️  $service_name was not running${NC}"
        fi
        
        # Remove PID file
        rm -f "$pid_file"
    else
        echo -e "${YELLOW}⚠️  No PID file found for $service_name${NC}"
    fi
}

echo -e "${YELLOW}🛑 Stopping all Lolita services...${NC}"
echo ""

# Stop Python AI Service
stop_service_by_pid "Python AI Service" "python-ai-service/logs/python-service.pid"

# Stop Frontend Development Server
stop_service_by_pid "SvelteKit Dev Server" "logs/frontend-dev.pid"

# Stop Frontend Production Server
stop_service_by_pid "SvelteKit Production Server" "logs/frontend-prod.pid"

echo ""
echo -e "${YELLOW}🧹 Cleaning up any remaining processes...${NC}"

# Kill any remaining processes by name
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "uvicorn.*main:app" 2>/dev/null || true
pkill -f "python-ai-service" 2>/dev/null || true
pkill -f "vite.*--port 5174" 2>/dev/null || true
pkill -f "vite.*--port 5173" 2>/dev/null || true
pkill -f "svelte-kit.*preview" 2>/dev/null || true
pkill -f "node.*vite" 2>/dev/null || true

# Kill any processes using our ports
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
lsof -ti:5174 | xargs kill -9 2>/dev/null || true
lsof -ti:8001 | xargs kill -9 2>/dev/null || true

# Wait a moment for cleanup
sleep 2

echo ""
echo -e "${GREEN}🎉 All Lolita services have been stopped!${NC}"
echo ""

# Show final status
echo -e "${PURPLE}📊 Final Status Check:${NC}"
echo -e "${PURPLE}======================${NC}"

# Check if any processes are still running
if pgrep -f "python.*main.py" >/dev/null 2>&1; then
    echo -e "${RED}❌ Python AI Service: Still running${NC}"
else
    echo -e "${GREEN}✅ Python AI Service: Stopped${NC}"
fi

if pgrep -f "vite.*--port 517" >/dev/null 2>&1; then
    echo -e "${RED}❌ SvelteKit Server: Still running${NC}"
else
    echo -e "${GREEN}✅ SvelteKit Server: Stopped${NC}"
fi

# Check ports
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ Port 8001: Still in use${NC}"
else
    echo -e "${GREEN}✅ Port 8001: Free${NC}"
fi

if lsof -Pi :5174 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ Port 5174: Still in use${NC}"
else
    echo -e "${GREEN}✅ Port 5174: Free${NC}"
fi

echo ""
echo -e "${CYAN}💡 To restart services, run: ./start.sh [dev|prod]${NC}"
echo ""
