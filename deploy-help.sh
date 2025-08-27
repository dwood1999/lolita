#!/bin/bash

# 📚 Quilty App - Deployment Help
# Shows all available deployment commands

echo "🚀 Quilty App - Deployment Commands"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Available Commands:${NC}"
echo ""

echo -e "${GREEN}1. Full Production Deployment${NC}"
echo "   ./deploy-to-production.sh"
echo "   • Complete deployment with dependencies and build"
echo "   • Creates backup, installs deps, builds frontend"
echo "   • Use for: New features, dependency changes"
echo ""

echo -e "${GREEN}2. Quick Deploy (Fast)${NC}"
echo "   ./quick-deploy.sh"
echo "   • Fast sync of source files only"
echo "   • No dependency install or full build"
echo "   • Use for: Small code changes, bug fixes"
echo ""

echo -e "${GREEN}3. Check Production Status${NC}"
echo "   ./check-production.sh"
echo "   • Check if services are running and healthy"
echo "   • View process status and recent errors"
echo "   • Monitor disk usage and logs"
echo ""

echo -e "${GREEN}4. Rollback to Previous Version${NC}"
echo "   ./rollback-production.sh"
echo "   • Emergency recovery from latest backup"
echo "   • Restores files and restarts services"
echo "   • Use for: Bad deployments, emergency fixes"
echo ""

echo -e "${BLUE}🎯 Recommended Workflow:${NC}"
echo ""
echo "For regular development:"
echo "  1. Make changes in /home/dwood/lolita"
echo "  2. Test locally"
echo "  3. Deploy: ./deploy-to-production.sh"
echo ""
echo "For quick fixes:"
echo "  1. Make small changes"
echo "  2. Quick deploy: ./quick-deploy.sh"
echo ""
echo "To check status:"
echo "  ./check-production.sh"
echo ""
echo "If something goes wrong:"
echo "  ./rollback-production.sh"
echo ""

echo -e "${BLUE}📁 Current Directory:${NC} $(pwd)"
echo -e "${BLUE}🌐 Production URL:${NC} https://quilty.app"
echo -e "${BLUE}📚 API Docs:${NC} https://quilty.app/api/docs"
echo ""

echo -e "${YELLOW}💡 Tip: All scripts include safety checks and automatic backups!${NC}"
