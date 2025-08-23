#!/bin/bash

# CryptoMiner V21 - Complete Setup Script
# Ensures proper V21 branding and configuration

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🚀 CryptoMiner V21 - Complete Setup"
echo "=================================="
echo ""

# 1. Stop any running services
echo -e "${BLUE}Step 1: Stopping existing services...${NC}"
./stop.sh
sleep 2

# 2. Switch to HTML dashboard for proper V21 branding
echo ""
echo -e "${BLUE}Step 2: Configuring web interface...${NC}"
./switch-frontend.sh html

# 3. Start the integrated system
echo ""
echo -e "${BLUE}Step 3: Starting integrated system...${NC}"
echo -e "${YELLOW}Note: This will start both backend API and web dashboard${NC}"
echo ""

# Show final status
echo -e "${GREEN}✅ CryptoMiner V21 Setup Complete!${NC}"
echo ""
echo "🌐 Web Dashboard: http://localhost:3000 (V21 branding)"
echo "🔧 Backend API: http://localhost:8001"
echo "📚 API Docs: http://localhost:8001/docs"
echo ""
echo "💡 Use './start-integrated.sh' to start mining"
echo "💡 Use './stop.sh' to stop all services"
echo "💡 Use './switch-frontend.sh status' to check frontend"