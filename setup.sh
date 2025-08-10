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
        "libssl-dev"
        "libffi-dev"
        "pkg-config"
        "mongodb"
        "redis-server"
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
        curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
        echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
        sudo apt update
        sudo apt install -y yarn
    fi
    
    success "System dependencies installed"
}

# Setup application directories
setup_directories() {
    log "Setting up application directories..."
    
    sudo mkdir -p "$INSTALL_DIR"
    sudo chown $USER:$USER "$INSTALL_DIR"
    
    # Copy application files
    cp -r backend/ "$INSTALL_DIR/"
    cp -r frontend/ "$INSTALL_DIR/"
    cp -r v30-remote-node/ "$INSTALL_DIR/"
    
    # Copy documentation
    cp README.md "$INSTALL_DIR/"
    cp DEPLOYMENT_GUIDE.md "$INSTALL_DIR/"
    cp SCRYPT_MINING_FIX.md "$INSTALL_DIR/"
    
    success "Application directories setup completed"
}

# Setup Python environment
setup_python_environment() {
    log "Setting up Python environment..."
    
    cd "$INSTALL_DIR/backend"
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    pip install -r requirements.txt
    
    # Create environment file if it doesn't exist
    if [ ! -f .env ]; then
        cat > .env << EOF
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=crypto_miner_db
REMOTE_DB_ENABLED=false
REMOTE_MONGO_URL=mongodb://localhost:27017
LOG_LEVEL=INFO
EOF
        log "Created default backend .env file"
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
    
    # Start MongoDB if not running
    sudo systemctl start mongodb
    sudo systemctl enable mongodb
    
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
    log "Access your mining dashboard at: http://localhost:3334"
    log "API endpoint available at: http://localhost:8001/api"
    log ""
    log "Service Management:"
    log "  Start:   sudo supervisorctl start mining_system:all"
    log "  Stop:    sudo supervisorctl stop mining_system:all"
    log "  Restart: sudo supervisorctl restart mining_system:all"
    log "  Status:  sudo supervisorctl status mining_system:all"
    log ""
    log "Log Files:"
    log "  Backend:  /var/log/supervisor/backend.out.log"
    log "  Frontend: /var/log/supervisor/frontend.out.log"
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