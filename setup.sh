#!/bin/bash

# CryptoMiner Pro - Unified Setup Script
# Consolidates installation, frontend fixes, and deployment setup

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

# System requirements check
check_system_requirements() {
    log "Checking system requirements..."
    
    # Check Ubuntu version
    if ! grep -q "Ubuntu" /etc/os-release; then
        warning "This installer is optimized for Ubuntu. Other distributions may work but are not fully tested."
    fi
    
    # Check available memory
    local available_memory=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    if [ "$available_memory" -lt 2048 ]; then
        warning "Available memory is less than 2GB. Performance may be affected."
    fi
    
    # Check disk space
    local available_space=$(df / | awk 'NR==2{printf "%.0f", $4/1024}')
    if [ "$available_space" -lt 5120 ]; then
        warning "Available disk space is less than 5GB. Installation may fail."
    fi
    
    success "System requirements check completed"
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."
    
    sudo apt update
    
    # Essential packages (without MongoDB - we'll install it separately)
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
        "libssl-dev"
        "libffi-dev"
        "pkg-config"
        "redis-server"
        "gnupg"
        "lsb-release"
    )
    
    sudo apt install -y "${packages[@]}"
    
    # Install MongoDB with proper repository setup
    install_mongodb
    
    # Install Node.js
    if ! command -v node &> /dev/null; then
        log "Installing Node.js $NODE_VERSION..."
        curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | sudo -E bash -
        sudo apt install -y nodejs
    fi
    
    # Install Yarn
    if ! command -v yarn &> /dev/null; then
        log "Installing Yarn..."
        curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
        echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
        sudo apt update
        sudo apt install -y yarn
    fi
    
    success "System dependencies installed"
}

# Install MongoDB with proper repository setup
install_mongodb() {
    log "Installing MongoDB..."
    
    # Check if MongoDB is already installed
    if command -v mongod &> /dev/null; then
        success "MongoDB already installed"
        return 0
    fi
    
    # Get Ubuntu version
    local ubuntu_version=$(lsb_release -cs)
    
    # For Ubuntu 24.04 (noble), use jammy repository as it's the closest supported version
    if [ "$ubuntu_version" = "noble" ]; then
        ubuntu_version="jammy"
        log "Using jammy repository for Ubuntu 24.04 compatibility"
    fi
    
    # Import MongoDB GPG key
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
        sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
    
    # Add MongoDB repository
    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu $ubuntu_version/mongodb-org/7.0 multiverse" | \
        sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
    
    # Update package list and install MongoDB
    sudo apt update
    sudo apt install -y mongodb-org
    
    # Start and enable MongoDB
    sudo systemctl start mongod
    sudo systemctl enable mongod
    
    # Verify installation
    if systemctl is-active --quiet mongod; then
        success "MongoDB installed and started successfully"
    else
        warning "Primary MongoDB installation failed, trying fallback method..."
        install_mongodb_fallback
    fi
}

# Fallback MongoDB installation using Ubuntu's default repository
install_mongodb_fallback() {
    log "Attempting fallback MongoDB installation..."
    
    # Try installing mongodb from Ubuntu repositories
    sudo apt update
    sudo apt install -y mongodb-server mongodb-clients
    
    # If that fails, try installing a compatible alternative
    if ! command -v mongod &> /dev/null; then
        log "Installing alternative MongoDB setup..."
        
        # Install snapd if not present
        if ! command -v snap &> /dev/null; then
            sudo apt install -y snapd
        fi
        
        # Install MongoDB via snap as last resort
        sudo snap install mongodb-community-server
        
        if command -v mongod &> /dev/null; then
            success "MongoDB installed via snap"
        else
            error "All MongoDB installation methods failed"
            warning "You may need to install MongoDB manually"
            warning "The application will work with an external MongoDB instance"
            return 1
        fi
    else
        # Start and enable the service
        sudo systemctl start mongodb
        sudo systemctl enable mongodb
        success "MongoDB installed from Ubuntu repository"
    fi
}

# Setup application directories
setup_directories() {
    log "Setting up application directories..."
    
    # Create installation directory
    sudo mkdir -p "$INSTALL_DIR"
    sudo chown $USER:$USER "$INSTALL_DIR"
    
    # Verify current directory has the required files
    if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
        error "Required directories (backend, frontend) not found in current directory"
        error "Please run this script from the CryptoMiner Pro source directory"
        return 1
    fi
    
    # Copy application files
    log "Copying backend files..."
    cp -r backend/ "$INSTALL_DIR/"
    
    log "Copying frontend files..."
    cp -r frontend/ "$INSTALL_DIR/"
    
    # Copy v30-remote-node if it exists
    if [ -d "v30-remote-node" ]; then
        log "Copying v30-remote-node files..."
        cp -r v30-remote-node/ "$INSTALL_DIR/"
    fi
    
    # Copy documentation files
    if [ -f "README.md" ]; then
        cp README.md "$INSTALL_DIR/"
    fi
    
    if [ -f "DEPLOYMENT_GUIDE.md" ]; then
        cp DEPLOYMENT_GUIDE.md "$INSTALL_DIR/"
    fi
    
    if [ -f "SCRYPT_MINING_FIX.md" ]; then
        cp SCRYPT_MINING_FIX.md "$INSTALL_DIR/"
    fi
    
    if [ -f "MONGODB_FIX_GUIDE.md" ]; then
        cp MONGODB_FIX_GUIDE.md "$INSTALL_DIR/"
    fi
    
    # Verify critical files exist
    if [ ! -f "$INSTALL_DIR/backend/requirements.txt" ]; then
        error "Backend requirements.txt not found after copy"
        return 1
    fi
    
    if [ ! -f "$INSTALL_DIR/backend/server.py" ]; then
        error "Backend server.py not found after copy"
        return 1
    fi
    
    if [ ! -f "$INSTALL_DIR/frontend/package.json" ]; then
        error "Frontend package.json not found after copy"
        return 1
    fi
    
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
        sudo apt install -y python3-venv python3-pip
    fi
    
    # Remove existing venv if it exists but is broken
    if [ -d "venv" ] && [ ! -f "venv/bin/python3" ]; then
        log "Removing broken virtual environment..."
        rm -rf venv
    fi
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        log "Creating Python virtual environment..."
        python3 -m venv venv
        
        # Verify virtual environment was created successfully
        if [ ! -f "venv/bin/python3" ]; then
            error "Failed to create virtual environment"
            log "Trying alternative method..."
            
            # Try alternative venv creation
            virtualenv venv 2>/dev/null || {
                log "Installing virtualenv..."
                sudo apt install -y python3-virtualenv
                virtualenv venv
            }
            
            # Final check
            if [ ! -f "venv/bin/python3" ]; then
                error "All virtual environment creation methods failed"
                return 1
            fi
        fi
        
        success "Virtual environment created successfully"
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
    
    # Start MongoDB (try different service names)
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
    
    # Start Redis if not running  
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    
    # Start application services
    sudo supervisorctl start mining_system:backend
    sudo supervisorctl start mining_system:frontend
    
    success "All services started successfully"
}

# Verify installation
verify_installation() {
    log "Verifying installation..."
    
    # Check if backend is responding
    local backend_check=0
    for i in {1..30}; do
        if curl -s http://localhost:8001/api/health > /dev/null; then
            backend_check=1
            break
        fi
        sleep 2
    done
    
    if [ $backend_check -eq 1 ]; then
        success "Backend service is running"
    else
        error "Backend service is not responding"
        return 1
    fi
    
    # Check if frontend is responding
    local frontend_check=0
    for i in {1..30}; do
        if curl -s http://localhost:3334 > /dev/null; then
            frontend_check=1
            break
        fi
        sleep 2
    done
    
    if [ $frontend_check -eq 1 ]; then
        success "Frontend service is running"
    else
        error "Frontend service is not responding"
        return 1
    fi
    
    success "Installation verification completed"
}

# Display completion message
display_completion_message() {
    success "🎉 CryptoMiner Pro installation completed successfully!"
    log ""
    log "Access your mining dashboard at: http://localhost:3333"
    log "API endpoint available at: http://localhost:8001/api"
    log ""
    log "Service Management:"
    log "  Start:   sudo supervisorctl start mining_system:backend mining_system:frontend"
    log "  Stop:    sudo supervisorctl stop mining_system:backend mining_system:frontend"
    log "  Restart: sudo supervisorctl restart mining_system:backend mining_system:frontend"
    log "  Status:  sudo supervisorctl status mining_system:*"
    log ""
    log "Alternative group commands:"
    log "  All services: sudo supervisorctl restart backend frontend"
    log ""
    log "Troubleshooting:"
    log "  Backend logs:  tail -f /var/log/supervisor/backend.out.log"
    log "  Frontend logs: tail -f /var/log/supervisor/frontend.out.log"
    log ""
    log "Installation Directory: $INSTALL_DIR"
    log "Configuration Files:"
    log "  Backend:  $INSTALL_DIR/backend/.env"
    log "  Frontend: $INSTALL_DIR/frontend/.env"
    log ""
    log "For uninstallation, run: sudo ./uninstall.sh"
}

# Main function
main() {
    local mode="$1"
    
    case "$mode" in
        --install)
            log "Starting fresh installation..."
            check_permissions
            check_system_requirements
            install_dependencies
            setup_directories
            setup_python_environment
            setup_frontend_environment
            setup_services
            start_services
            verify_installation
            display_completion_message
            ;;
        --frontend-fix)
            log "Running frontend-only fixes..."
            check_permissions
            cd "$INSTALL_DIR/frontend" 2>/dev/null || { error "Installation directory not found. Run --install first."; exit 1; }
            yarn install
            sudo supervisorctl restart mining_system:frontend
            success "Frontend fixes applied"
            ;;
        --restart-services)
            log "Restarting all services..."
            check_permissions
            sudo supervisorctl restart mining_system:all
            success "All services restarted"
            ;;
        --status)
            log "Checking service status..."
            sudo supervisorctl status mining_system:all
            ;;
        --help|*)
            cat << EOF
CryptoMiner Pro Unified Setup Script

Usage: $0 [MODE]

Modes:
    --install           Full installation (default)
    --frontend-fix      Fix frontend issues only
    --restart-services  Restart all services
    --status           Check service status
    --help             Show this help message

Examples:
    $0 --install           # Fresh installation
    $0 --frontend-fix      # Fix frontend after changes
    $0 --restart-services  # Restart services after config changes

EOF
            ;;
    esac
}

# Default to install mode if no arguments
main "${1:---install}"