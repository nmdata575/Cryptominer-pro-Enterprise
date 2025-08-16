#!/bin/bash

# Quick fix for Python environment issue
# Run this if install.sh fails at Python environment setup

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

INSTALL_DIR="$HOME/CryptominerV30"

echo -e "${BLUE}🔧 Fixing Python Environment...${NC}"

if [ ! -d "$INSTALL_DIR/backend" ]; then
    echo -e "${RED}❌ Backend directory not found at $INSTALL_DIR/backend${NC}"
    echo "Please ensure the installation directory exists and contains backend files"
    exit 1
fi

cd "$INSTALL_DIR/backend"

# Remove any broken virtual environment
if [ -d "venv" ]; then
    echo -e "${BLUE}Removing existing virtual environment...${NC}"
    rm -rf venv
fi

# Create new virtual environment
echo -e "${BLUE}Creating Python virtual environment...${NC}"
if python3 -m venv venv; then
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${RED}❌ Failed to create virtual environment${NC}"
    exit 1
fi

# Verify python3 exists in venv
if [ ! -f "venv/bin/python3" ]; then
    echo -e "${RED}❌ Python3 not found in virtual environment${NC}"
    exit 1
fi

# Install Python dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
./venv/bin/python3 -m pip install --upgrade pip setuptools wheel

if [ -f "requirements.txt" ]; then
    if ./venv/bin/python3 -m pip install -r requirements.txt; then
        echo -e "${GREEN}✅ Python dependencies installed${NC}"
    else
        echo -e "${RED}❌ Failed to install Python dependencies${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating backend .env file...${NC}"
    cat > .env << 'EOF'
MONGO_URL=mongodb://localhost:27017/crypto_miner_db
DATABASE_NAME=crypto_miner_db
LOG_LEVEL=INFO
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8001
CORS_ORIGINS=http://localhost:3333,http://127.0.0.1:3333
EOF
    chmod 600 .env
    echo -e "${GREEN}✅ Backend .env file created${NC}"
fi

echo -e "${GREEN}🎉 Python environment fixed successfully!${NC}"
echo -e "${BLUE}Now you can continue with: ./install.sh${NC}"