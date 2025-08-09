#!/bin/bash

# CryptoMiner Pro - Complete Setup Script
# This script sets up the complete environment from scratch

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log "🚀 Setting up CryptoMiner Pro complete environment..."
log "Installation directory: $SCRIPT_DIR"

# Check for required system packages
log "📦 Checking system dependencies..."

# Install system dependencies
if ! command -v python3 &> /dev/null; then
    error "Python3 not found. Please install Python 3.8+ first"
    exit 1
fi

if ! command -v node &> /dev/null; then
    error "Node.js not found. Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

if ! command -v yarn &> /dev/null; then
    error "Yarn not found. Installing Yarn..."
    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
    sudo apt update
    sudo apt install -y yarn
fi

# Install build tools if needed
sudo apt update
sudo apt install -y python3-venv python3-pip build-essential python3-dev

# Setup Python backend
log "🐍 Setting up Python backend environment..."
cd "$SCRIPT_DIR/backend"

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
log "Detected Python version: $PYTHON_VERSION"

# Remove existing venv if it exists but is broken
if [ -d "venv" ] && [ ! -f "venv/bin/python" ]; then
    log "Removing broken virtual environment..."
    rm -rf venv
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    log "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate and install dependencies
log "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip setuptools wheel

# Try different installation strategies for Python 3.13 compatibility
if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    log "⚠️  Python 3.13 detected - using compatibility mode..."
    
    # Strategy 1: Try with only binary wheels
    log "Attempting binary-only installation..."
    if pip install -r requirements.txt --only-binary=all --no-cache-dir; then
        success "✅ Binary installation successful"
    else
        warning "Binary installation failed, trying simplified requirements..."
        
        # Strategy 2: Use simplified requirements
        if pip install -r requirements-simple.txt --prefer-binary --no-cache-dir; then
            success "✅ Simplified installation successful"
            warning "⚠️  Note: Some AI features may be limited without scikit-learn"
        else
            error "❌ Installation failed with Python 3.13"
            echo "💡 Recommendation: Install Python 3.11 or 3.12 for full compatibility:"
            echo "   sudo apt install python3.11 python3.11-venv python3.11-dev"
            echo "   Then rerun this script"
            exit 1
        fi
    fi
else
    # Standard installation for Python < 3.13
    log "Using standard installation for Python $PYTHON_VERSION..."
    if pip install -r requirements.txt --prefer-binary --no-cache-dir; then
        success "✅ Standard installation successful"
    else
        warning "Standard installation failed, trying simplified requirements..."
        if pip install -r requirements-simple.txt --prefer-binary --no-cache-dir; then
            success "✅ Fallback installation successful"
        else
            error "❌ All installation strategies failed"
            exit 1
        fi
    fi
fi

success "✅ Python backend environment ready"

# Setup Node.js frontend
log "⚛️  Setting up Node.js frontend environment..."
cd "$SCRIPT_DIR/frontend"

# Install frontend dependencies
log "Installing Node.js dependencies..."
yarn install

success "✅ Node.js frontend environment ready"

# Test the setup
log "🧪 Testing the setup..."

# Test backend
cd "$SCRIPT_DIR/backend"
if ! source venv/bin/activate && python -c "import fastapi, uvicorn, pymongo, psutil, numpy, sklearn"; then
    error "❌ Backend dependencies test failed"
    exit 1
fi
success "✅ Backend dependencies verified"

# Test frontend
cd "$SCRIPT_DIR/frontend"
if ! yarn --version > /dev/null; then
    error "❌ Frontend setup test failed"
    exit 1
fi
success "✅ Frontend dependencies verified"

# Set up environment files if they don't exist
log "⚙️  Setting up environment files..."

# Backend .env
if [ ! -f "$SCRIPT_DIR/backend/.env" ]; then
    log "Creating backend .env file..."
    cat > "$SCRIPT_DIR/backend/.env" << EOF
MONGO_URL=mongodb://localhost:27017/cryptominer_pro
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=false
LOG_LEVEL=info
EOF
fi

# Frontend .env
if [ ! -f "$SCRIPT_DIR/frontend/.env" ]; then
    log "Creating frontend .env file..."
    cat > "$SCRIPT_DIR/frontend/.env" << EOF
REACT_APP_BACKEND_URL=http://localhost:8001
REACT_APP_VERSION=2.0.0
GENERATE_SOURCEMAP=false
EOF
fi

# Install MongoDB if not present
if ! command -v mongod &> /dev/null; then
    log "📊 Installing MongoDB..."
    wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
    sudo apt update
    sudo apt install -y mongodb-org
    sudo systemctl start mongod
    sudo systemctl enable mongod
    success "✅ MongoDB installed and started"
else
    log "Starting MongoDB..."
    sudo systemctl start mongod || true
fi

success "🎉 Complete environment setup finished!"

echo
echo "📋 Setting up Supervisor..."

# Now set up supervisor automatically
if [[ $EUID -eq 0 ]]; then
    log "🔧 Setting up supervisor configuration as root..."
    USER_NAME=$SUDO_USER
else
    log "🔧 Need to set up supervisor (requires sudo)..."
    USER_NAME=$USER
fi

# Install supervisor if not already installed
if ! command -v supervisorctl &> /dev/null; then
    log "Installing supervisor..."
    sudo apt update
    sudo apt install -y supervisor
fi

# Create supervisor configuration directory if it doesn't exist
sudo mkdir -p /etc/supervisor/conf.d

# Create the mining app supervisor configuration
log "Creating supervisor configuration..."

sudo tee /etc/supervisor/conf.d/cryptominer-pro.conf > /dev/null << EOF
[program:cryptominer_backend]
command=$SCRIPT_DIR/backend/venv/bin/python -m uvicorn server:app --host 0.0.0.0 --port 8001
directory=$SCRIPT_DIR/backend
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/cryptominer_backend.err.log
stdout_logfile=/var/log/supervisor/cryptominer_backend.out.log
user=$USER_NAME
environment=PATH="$SCRIPT_DIR/backend/venv/bin"

[program:cryptominer_frontend]
command=yarn start
directory=$SCRIPT_DIR/frontend
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/cryptominer_frontend.err.log
stdout_logfile=/var/log/supervisor/cryptominer_frontend.out.log
user=$USER_NAME
environment=PORT=3333,PATH="/usr/bin:/bin:/usr/local/bin"

[group:cryptominer_pro]
programs=cryptominer_backend,cryptominer_frontend
priority=999
EOF

# Create log directory
sudo mkdir -p /var/log/supervisor

# Reload supervisor configuration
log "Reloading supervisor configuration..."
sudo supervisorctl reread
sudo supervisorctl update

# Start services
log "Starting CryptoMiner Pro services..."
sudo supervisorctl start cryptominer_pro:* || true

echo
echo "🚀 SETUP COMPLETE!"
echo
echo "📊 Service Status:"
sudo supervisorctl status cryptominer_pro:* || echo "Services not yet running"
echo
echo "🌐 Access URLs:"
echo "  Frontend: http://localhost:3333"
echo "  Backend:  http://localhost:8001"
echo "  Health:   http://localhost:8001/api/health"
echo
echo "🛠️ Useful Commands:"
echo "  sudo supervisorctl status                    # Check all services"
echo "  sudo supervisorctl start cryptominer_pro:*  # Start all services"
echo "  sudo supervisorctl stop cryptominer_pro:*   # Stop all services"
echo "  sudo supervisorctl restart cryptominer_pro:* # Restart all services"
echo
echo "🔧 Manual Start (if supervisor fails):"
echo "  Terminal 1: cd backend && source venv/bin/activate && python -m uvicorn server:app --host 0.0.0.0 --port 8001"
echo "  Terminal 2: cd frontend && PORT=3333 yarn start"