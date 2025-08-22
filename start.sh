#!/bin/bash

# Lolita Screenplay Analysis Tool - Production Startup Script
# Usage: ./start.sh [dev|prod] [--frontend-only|--backend-only]
# This script kills existing services and starts them in background with persistence

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
MODE=${1:-dev}
SERVICE_MODE="both"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --frontend-only)
            SERVICE_MODE="frontend"
            shift
            ;;
        --backend-only)
            SERVICE_MODE="backend"
            shift
            ;;
        dev|development|prod|production)
            MODE=$1
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# Normalize mode
case $MODE in
    "development") MODE="dev" ;;
    "production") MODE="prod" ;;
esac

echo -e "${BLUE}🎬 Lolita Screenplay Analysis Tool - Production Startup${NC}"
echo -e "${BLUE}=========================================================${NC}"
echo -e "${CYAN}Mode: $MODE | Services: $SERVICE_MODE${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to kill existing services
kill_existing_services() {
    echo -e "${YELLOW}🛑 Killing existing services...${NC}"
    
    # Kill Python AI service processes
    echo -e "${YELLOW}   Stopping Python AI services...${NC}"
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "uvicorn.*main:app" 2>/dev/null || true
    pkill -f "python-ai-service" 2>/dev/null || true
    
    # Kill SvelteKit/Vite processes
    echo -e "${YELLOW}   Stopping SvelteKit services...${NC}"
    pkill -f "vite.*--port 5174" 2>/dev/null || true
    pkill -f "vite.*--port 5173" 2>/dev/null || true
    pkill -f "svelte-kit.*preview" 2>/dev/null || true
    pkill -f "node.*vite" 2>/dev/null || true
    
    # Kill any processes using our ports
    echo -e "${YELLOW}   Freeing up ports 5173, 5174, 8001...${NC}"
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true
    lsof -ti:5174 | xargs kill -9 2>/dev/null || true
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    
    # Wait a moment for processes to die
    sleep 2
    
    echo -e "${GREEN}✅ All existing services stopped${NC}"
}

# Function to wait for database connection
wait_for_db() {
    echo -e "${YELLOW}⏳ Checking database connection...${NC}"
    
    # Load environment variables
    if [ -f .env ]; then
        export $(grep -v '^#' .env | xargs)
    fi
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if mysql -h"${DB_HOST:-localhost}" -P"${DB_PORT:-3306}" -u"${DB_USER:-root}" -p"${DB_PASSWORD}" -e "SELECT 1;" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Database connection successful${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}   Attempt $attempt/$max_attempts - waiting for database...${NC}"
        sleep 2
        ((attempt++))
    done
    
    echo -e "${RED}❌ Could not connect to database after $max_attempts attempts${NC}"
    echo -e "${YELLOW}   Please check your database configuration in .env${NC}"
    return 1
}

# Function to initialize database
init_database() {
    echo -e "${YELLOW}🔧 Initializing database tables...${NC}"
    if npm run db:init >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Database initialized successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Database initialization skipped (may already exist)${NC}"
    fi
}

# Function to setup Python environment
setup_python_env() {
    echo -e "${YELLOW}🐍 Setting up Python AI service...${NC}"
    
    cd python-ai-service
    
    # Check Python version
    if ! command_exists python3; then
        echo -e "${RED}❌ Python 3 is not installed${NC}"
        echo -e "${YELLOW}   Please install Python 3.8+ from https://python.org/${NC}"
        return 1
    fi
    
    local python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo -e "${GREEN}✅ Python $python_version found${NC}"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    echo -e "${YELLOW}🔧 Activating virtual environment...${NC}"
    source venv/bin/activate
    
    # Install/upgrade requirements
    echo -e "${YELLOW}📚 Installing Python dependencies...${NC}"
    pip install --upgrade pip >/dev/null 2>&1
    pip install -r requirements.txt >/dev/null 2>&1
    
    # Create uploads directory
    mkdir -p uploads
    mkdir -p logs
    
    echo -e "${GREEN}✅ Python environment ready${NC}"
    cd ..
}

# Function to start Python backend in background
start_python_backend() {
    echo -e "${YELLOW}🚀 Starting Python AI service in background...${NC}"
    
    cd python-ai-service
    source venv/bin/activate
    
    # Check environment variables
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        echo -e "${YELLOW}⚠️  Warning: ANTHROPIC_API_KEY not set${NC}"
    fi
    
    # Create log file
    local log_file="logs/python-service.log"
    
    # Start the service in background with nohup for persistence
    echo -e "${GREEN}🔥 Python AI Service starting on port 8001...${NC}"
    nohup python main.py > "$log_file" 2>&1 &
    local python_pid=$!
    
    # Save PID for later management
    echo $python_pid > logs/python-service.pid
    
    # Wait a moment for startup
    sleep 5
    
    # Check if service started successfully
    if kill -0 $python_pid 2>/dev/null; then
        echo -e "${GREEN}✅ Python AI Service running in background (PID: $python_pid)${NC}"
        echo -e "${CYAN}   Log file: python-ai-service/$log_file${NC}"
        echo -e "${CYAN}   API available at: http://localhost:8001${NC}"
    else
        echo -e "${RED}❌ Python AI Service failed to start${NC}"
        echo -e "${YELLOW}   Check log file: python-ai-service/$log_file${NC}"
        return 1
    fi
    
    cd ..
}

# Function to install Node.js dependencies
install_node_dependencies() {
    echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"
    
    if [ ! -d "node_modules" ]; then
        npm install >/dev/null 2>&1
    else
        echo -e "${GREEN}✅ Node.js dependencies are up to date${NC}"
    fi
}

# Function to start frontend development server in background
start_frontend_dev() {
    echo -e "${YELLOW}🚀 Starting SvelteKit development server in background...${NC}"
    
    # Create logs directory
    mkdir -p logs
    
    local log_file="logs/frontend-dev.log"
    
    # Start development server in background with nohup
    nohup npm run dev -- --host 0.0.0.0 --port 5174 > "$log_file" 2>&1 &
    local frontend_pid=$!
    
    # Save PID for later management
    echo $frontend_pid > logs/frontend-dev.pid
    
    # Wait a moment for startup
    sleep 5
    
    # Check if service started successfully
    if kill -0 $frontend_pid 2>/dev/null; then
        echo -e "${GREEN}✅ SvelteKit Dev Server running in background (PID: $frontend_pid)${NC}"
        echo -e "${CYAN}   Log file: $log_file${NC}"
        echo -e "${CYAN}   Frontend available at: http://localhost:5174${NC}"
    else
        echo -e "${RED}❌ SvelteKit Dev Server failed to start${NC}"
        echo -e "${YELLOW}   Check log file: $log_file${NC}"
        return 1
    fi
}

# Function to start frontend production server in background
start_frontend_prod() {
    echo -e "${YELLOW}🏗️  Building application for production...${NC}"
    npm run build >/dev/null 2>&1
    
    echo -e "${YELLOW}🚀 Starting production server in background...${NC}"
    
    # Create logs directory
    mkdir -p logs
    
    local log_file="logs/frontend-prod.log"
    
    # Start production server in background with nohup
    nohup npm run preview -- --host 0.0.0.0 --port 5174 > "$log_file" 2>&1 &
    local frontend_pid=$!
    
    # Save PID for later management
    echo $frontend_pid > logs/frontend-prod.pid
    
    # Wait a moment for startup
    sleep 5
    
    # Check if service started successfully
    if kill -0 $frontend_pid 2>/dev/null; then
        echo -e "${GREEN}✅ SvelteKit Production Server running in background (PID: $frontend_pid)${NC}"
        echo -e "${CYAN}   Log file: $log_file${NC}"
        echo -e "${CYAN}   Frontend available at: http://localhost:5174${NC}"
    else
        echo -e "${RED}❌ SvelteKit Production Server failed to start${NC}"
        echo -e "${YELLOW}   Check log file: $log_file${NC}"
        return 1
    fi
}

# Function to show service status
show_service_status() {
    echo ""
    echo -e "${PURPLE}📊 Service Status:${NC}"
    echo -e "${PURPLE}==================${NC}"
    
    # Check Python service
    if [ -f "python-ai-service/logs/python-service.pid" ]; then
        local python_pid=$(cat python-ai-service/logs/python-service.pid 2>/dev/null)
        if [ ! -z "$python_pid" ] && kill -0 $python_pid 2>/dev/null; then
            echo -e "${GREEN}✅ Python AI Service: Running (PID: $python_pid)${NC}"
            echo -e "${CYAN}   API: http://localhost:8001${NC}"
            echo -e "${CYAN}   Log: python-ai-service/logs/python-service.log${NC}"
        else
            echo -e "${RED}❌ Python AI Service: Not running${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Python AI Service: Status unknown${NC}"
    fi
    
    # Check Frontend service
    local frontend_pid_file=""
    if [ "$MODE" = "dev" ]; then
        frontend_pid_file="logs/frontend-dev.pid"
    else
        frontend_pid_file="logs/frontend-prod.pid"
    fi
    
    if [ -f "$frontend_pid_file" ]; then
        local frontend_pid=$(cat "$frontend_pid_file" 2>/dev/null)
        if [ ! -z "$frontend_pid" ] && kill -0 $frontend_pid 2>/dev/null; then
            echo -e "${GREEN}✅ SvelteKit Server: Running (PID: $frontend_pid)${NC}"
            echo -e "${CYAN}   Frontend: http://localhost:5174${NC}"
            echo -e "${CYAN}   Log: logs/frontend-$MODE.log${NC}"
        else
            echo -e "${RED}❌ SvelteKit Server: Not running${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  SvelteKit Server: Status unknown${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}💡 Management Commands:${NC}"
    echo -e "${CYAN}   View Python logs: tail -f python-ai-service/logs/python-service.log${NC}"
    echo -e "${CYAN}   View Frontend logs: tail -f logs/frontend-$MODE.log${NC}"
    echo -e "${CYAN}   Stop all services: ./stop.sh${NC}"
    echo -e "${CYAN}   Restart services: ./start.sh $MODE${NC}"
    echo ""
}

# Main execution starts here
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

# Check Node.js and npm
if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    echo -e "${YELLOW}   Please install Node.js 18+ from https://nodejs.org/${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ npm is not installed${NC}"
    echo -e "${YELLOW}   Please install npm (usually comes with Node.js)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js $(node --version) found${NC}"
echo -e "${GREEN}✅ npm $(npm --version) found${NC}"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ package.json not found${NC}"
    echo -e "${YELLOW}   Please run this script from the project root directory${NC}"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo -e "${YELLOW}   Please create a .env file with your configuration${NC}"
    echo -e "${CYAN}   Required variables: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME${NC}"
    echo -e "${CYAN}   Optional: PYTHON_SERVICE_URL, ANTHROPIC_API_KEY, XAI_API_KEY${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Environment file found${NC}"

# Kill existing services first
kill_existing_services

echo ""

# Install Node.js dependencies
if [ "$SERVICE_MODE" = "both" ] || [ "$SERVICE_MODE" = "frontend" ]; then
    install_node_dependencies
fi

# Wait for database and initialize
if [ "$SERVICE_MODE" = "both" ] || [ "$SERVICE_MODE" = "frontend" ]; then
    wait_for_db || exit 1
    init_database || exit 1
fi

# Setup Python environment
if [ "$SERVICE_MODE" = "both" ] || [ "$SERVICE_MODE" = "backend" ]; then
    setup_python_env || exit 1
fi

echo ""
echo -e "${PURPLE}🎯 Starting services in background...${NC}"
echo ""

# Start services based on mode and service selection
if [ "$SERVICE_MODE" = "backend" ]; then
    # Backend only
    start_python_backend || exit 1
    
elif [ "$SERVICE_MODE" = "frontend" ]; then
    # Frontend only
    if [ "$MODE" = "dev" ]; then
        start_frontend_dev || exit 1
    else
        start_frontend_prod || exit 1
    fi
    
else
    # Both services
    start_python_backend || exit 1
    
    if [ "$MODE" = "dev" ]; then
        start_frontend_dev || exit 1
    else
        start_frontend_prod || exit 1
    fi
fi

# Show final status
echo ""
echo -e "${GREEN}🎉 All services started successfully in background!${NC}"
show_service_status

echo -e "${GREEN}✅ Services are now running persistently and will survive terminal disconnection${NC}"
echo -e "${YELLOW}   Use './stop.sh' to stop all services${NC}"
echo ""