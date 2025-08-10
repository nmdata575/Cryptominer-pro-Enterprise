#!/bin/bash

# CryptoMiner Pro - Local Directory Setup Script
# Run this from your source directory (e.g., ~/Desktop/Cryptominer-pro-Enterprise-main/)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/cryptominer-pro"
SERVICE_NAME="cryptominer-pro"
PYTHON_VERSION="3.11"
NODE_VERSION="18"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Check if we're in the right directory
check_source_directory() {
    log "Checking source directory..."
    
    if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
        error "Required directories (backend, frontend) not found in current directory: $(pwd)"
        error "Please run this script from the CryptoMiner Pro source directory"
        error "Expected structure:"
        error "  ./backend/"
        error "  ./frontend/"
        error "  ./setup.sh (this script)"
        exit 1
    fi
    
    if [ ! -f "backend/server.py" ]; then
        error "backend/server.py not found"
        exit 1
    fi
    
    if [ ! -f "frontend/package.json" ]; then
        error "frontend/package.json not found"
        exit 1
    fi
    
    success "Source directory structure verified"
}

# Check and install optimal Python version
check_and_install_python() {
    log "Checking Python version compatibility..."
    
    local python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2 || echo "unknown")
    local major_version=$(echo $python_version | cut -d'.' -f1)
    local minor_version=$(echo $python_version | cut -d'.' -f2)
    
    log "Detected system Python: $python_version"
    
    # Check if Python 3.13 is being used (known compatibility issues)
    if [ "$major_version" = "3" ] && [ "$minor_version" = "13" ]; then
        warning "Python 3.13 detected - this version has known compatibility issues with pandas"
        log "Installing Python 3.12 for better package compatibility..."
        install_python312
        PYTHON_CMD="python3.12"
    elif [ "$major_version" = "3" ] && [ "$minor_version" -ge "11" ] && [ "$minor_version" -le "12" ]; then
        log "Python $python_version is compatible"
        PYTHON_CMD="python3"
    else
        warning "Python version $python_version may have compatibility issues"
        log "Installing Python 3.12 for optimal compatibility..."
        install_python312
        PYTHON_CMD="python3.12"
    fi
    
    # Verify the chosen Python version works
    if ! $PYTHON_CMD --version &> /dev/null; then
        error "Selected Python version ($PYTHON_CMD) is not available"
        exit 1
    fi
    
    local final_version=$($PYTHON_CMD --version | cut -d' ' -f2)
    success "Using Python $final_version for installation"
}

# Install Python 3.12 for optimal compatibility
install_python312() {
    log "Installing Python 3.12 for optimal package compatibility..."
    
    # Check if Python 3.12 is already installed
    if command -v python3.12 &> /dev/null; then
        success "Python 3.12 already installed"
        return 0
    fi
    
    # Install software-properties-common if not available
    if ! command -v add-apt-repository &> /dev/null; then
        log "Installing software-properties-common..."
        sudo apt install -y software-properties-common
    fi
    
    # Add deadsnakes PPA for newer Python versions
    log "Adding deadsnakes PPA..."
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    
    # Install Python 3.12 and related packages
    log "Installing Python 3.12 packages..."
    sudo apt install -y \
        python3.12 \
        python3.12-venv \
        python3.12-dev \
        python3.12-distutils
    
    # Verify installation
    if python3.12 --version &> /dev/null; then
        success "Python 3.12 installed successfully"
    else
        error "Python 3.12 installation failed"
        exit 1
    fi
}

# Check permissions
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root. Please run as a regular user with sudo privileges."
        exit 1
    fi
    
    if ! sudo -n true 2>/dev/null; then
        error "This script requires sudo privileges. Please run with sudo or configure passwordless sudo."
        exit 1
    fi
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."
    
    sudo apt update
    
    # Essential packages
    local packages=(
        "curl"
        "wget"
        "git"
        "build-essential"
        "supervisor"
        "nginx"
        "python3-pip"
        "python3-venv" 
        "python3-dev"
        "python3-virtualenv"
        "libssl-dev"
        "libffi-dev"
        "pkg-config"
        "redis-server"
        "gnupg"
        "lsb-release"
    )
    
    sudo apt install -y "${packages[@]}"
    
    # Install Node.js
    if ! command -v node &> /dev/null; then
        log "Installing Node.js $NODE_VERSION..."
        curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | sudo -E bash -
        sudo apt install -y nodejs
    fi
    
    # Install Yarn
    if ! command -v yarn &> /dev/null; then
        log "Installing Yarn..."
        npm install -g yarn
    fi
    
    success "System dependencies installed"
}

# Install MongoDB
install_mongodb() {
    log "Installing MongoDB..."
    
    # Check if MongoDB is already installed
    if command -v mongod &> /dev/null; then
        success "MongoDB already installed"
        return 0
    fi
    
    # Run the MongoDB fix script if it exists
    if [ -f "/app/fix-mongodb.sh" ]; then
        log "Running MongoDB installation fix..."
        sudo /app/fix-mongodb.sh
        return $?
    fi
    
    # Fallback MongoDB installation
    log "Installing MongoDB via apt..."
    sudo apt update
    sudo apt install -y mongodb-server mongodb-clients
    
    # Start and enable MongoDB
    sudo systemctl start mongodb
    sudo systemctl enable mongodb
    
    success "MongoDB installed"
}

# Setup application directories
setup_directories() {
    log "Setting up application directories..."
    
    # Create installation directory
    sudo mkdir -p "$INSTALL_DIR"
    sudo chown $USER:$USER "$INSTALL_DIR"
    
    # Copy application files from current directory
    log "Copying backend files..."
    cp -r backend/ "$INSTALL_DIR/"
    
    log "Copying frontend files..."
    cp -r frontend/ "$INSTALL_DIR/"
    
    # Copy additional directories if they exist
    if [ -d "v30-remote-node" ]; then
        log "Copying v30-remote-node files..."
        cp -r v30-remote-node/ "$INSTALL_DIR/"
    fi
    
    # Copy documentation files if they exist
    for doc in README.md DEPLOYMENT_GUIDE.md SCRYPT_MINING_FIX.md MONGODB_FIX_GUIDE.md; do
        if [ -f "$doc" ]; then
            cp "$doc" "$INSTALL_DIR/"
        fi
    done
    
    # Set proper permissions
    sudo chown -R $USER:$USER "$INSTALL_DIR"
    
    success "Application directories setup completed"
}

# Setup Python environment
setup_python_environment() {
    log "Setting up Python environment..."
    
    cd "$INSTALL_DIR/backend"
    
    # Ensure we have the right Python version and venv module
    if ! python3 -m venv --help &> /dev/null; then
        error "python3-venv module not available. Installing..."
        sudo apt install -y python3-venv python3-pip python3-virtualenv
    fi
    
    # Remove existing venv if it exists but is broken
    if [ -d "venv" ] && [ ! -f "venv/bin/python3" ]; then
        log "Removing broken virtual environment..."
        rm -rf venv
    fi
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        log "Creating Python virtual environment..."
        
        if python3 -m venv venv; then
            success "Virtual environment created with python3 -m venv"
        elif virtualenv venv; then
            success "Virtual environment created with virtualenv"
        else
            error "Failed to create virtual environment"
            return 1
        fi
        
        # Verify virtual environment was created successfully
        if [ ! -f "venv/bin/python3" ]; then
            error "Virtual environment creation appeared to succeed but python3 binary is missing"
            return 1
        fi
    else
        log "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Verify activation worked
    if [ "$VIRTUAL_ENV" = "" ]; then
        error "Failed to activate virtual environment"
        return 1
    fi
    
    log "Virtual environment activated: $VIRTUAL_ENV"
    
    # Upgrade pip
    log "Upgrading pip..."
    python -m pip install --upgrade pip
    
    # Install Python dependencies
    log "Installing Python dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        error "requirements.txt not found"
        return 1
    fi
    
    # Create environment file if it doesn't exist
    if [ ! -f .env ]; then
        log "Creating default backend .env file..."
        cat > .env << EOF
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=crypto_miner_db
REMOTE_DB_ENABLED=false
REMOTE_MONGO_URL=mongodb://localhost:27017
LOG_LEVEL=INFO
EOF
        success "Created default backend .env file"
    else
        log "Backend .env file already exists"
    fi
    
    success "Python environment setup completed"
}

# Setup frontend environment
setup_frontend_environment() {
    log "Setting up frontend environment..."
    
    cd "$INSTALL_DIR/frontend"
    
    # Install dependencies
    yarn install
    
    # Create environment file if it doesn't exist
    if [ ! -f .env ]; then
        cat > .env << EOF
REACT_APP_BACKEND_URL=http://localhost:8001
GENERATE_SOURCEMAP=false
EOF
        log "Created default frontend .env file"
    fi
    
    success "Frontend environment setup completed"
}

# Setup services
setup_services() {
    log "Setting up system services..."
    
    # Create supervisor configuration
    sudo tee /etc/supervisor/conf.d/mining_system.conf > /dev/null << EOF
[group:mining_system]
programs=backend,frontend

[program:backend]
command=$INSTALL_DIR/backend/venv/bin/python server.py
directory=$INSTALL_DIR/backend
user=$USER
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/backend.err.log
stdout_logfile=/var/log/supervisor/backend.out.log
environment=PATH="$INSTALL_DIR/backend/venv/bin"

[program:frontend]
command=yarn start
directory=$INSTALL_DIR/frontend
user=$USER
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/frontend.err.log
stdout_logfile=/var/log/supervisor/frontend.out.log
environment=PORT=3334
EOF
    
    # Reload supervisor
    sudo supervisorctl reread
    sudo supervisorctl update
    
    success "System services configured"
}

# Start services
start_services() {
    log "Starting CryptoMiner Pro services..."
    
    # Start MongoDB
    if systemctl list-units --type=service | grep -q "mongod.service"; then
        sudo systemctl start mongod
        sudo systemctl enable mongod
        log "Started mongod service"
    elif systemctl list-units --type=service | grep -q "mongodb.service"; then
        sudo systemctl start mongodb
        sudo systemctl enable mongodb
        log "Started mongodb service"
    else
        warning "MongoDB service not found - you may need to start it manually"
    fi
    
    # Start Redis
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    
    # Start application services
    sudo supervisorctl start mining_system:backend
    sudo supervisorctl start mining_system:frontend
    
    success "All services started successfully"
}

# Main function
main() {
    log "Starting CryptoMiner Pro installation from current directory..."
    log "Current directory: $(pwd)"
    
    check_source_directory
    check_permissions
    install_dependencies
    install_mongodb
    setup_directories
    setup_python_environment
    setup_frontend_environment
    setup_services
    start_services
    
    success "🎉 CryptoMiner Pro installation completed successfully!"
    log ""
    log "Access your mining dashboard at: http://localhost:3334"
    log "API endpoint available at: http://localhost:8001/api"
    log ""
    log "Service Management:"
    log "  Start:   sudo supervisorctl start mining_system:all"
    log "  Stop:    sudo supervisorctl stop mining_system:all"
    log "  Restart: sudo supervisorctl restart mining_system:all"
    log "  Status:  sudo supervisorctl status mining_system:all"
}

# Run main function
main "$@"