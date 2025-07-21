#!/bin/bash

# 🐍 CryptoMiner Pro - Python 3.13 Compatible Installation Script
# Designed to work specifically with Python 3.13

set -e  # Exit on any error

# Configuration
SCRIPT_VERSION="3.13.0"
PROJECT_DIR="/opt/cryptominer-pro"
LOG_FILE="/tmp/cryptominer-python313-install.log"
USER_HOME="/home/$SUDO_USER"

# Force Python 3.13 usage
REQUIRED_PYTHON="python3.13"
PYTHON_VERSION_REQUIRED="3.13"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Unicode symbols
SUCCESS="✅"
ERROR="❌"
WARNING="⚠️"
INFO="ℹ️"
ROCKET="🚀"
PYTHON="🐍"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Print functions
print_header() {
    clear
    echo -e "${PURPLE}"
    echo "=================================================================="
    echo "      🐍 CryptoMiner Pro - Python 3.13 Compatible Installer"
    echo "=================================================================="
    echo -e "Version: ${SCRIPT_VERSION} - Built for Python 3.13${NC}"
    echo -e "${BLUE}Latest Python support with modern package compatibility${NC}"
    echo ""
}

print_step() {
    echo -e "\n${WHITE}🔄 STEP: $1${NC}"
    echo "$(printf '=%.0s' {1..60})"
    log "STEP: $1"
}

print_substep() {
    echo -e "${BLUE}  🔧 $1${NC}"
    log "SUBSTEP: $1"
}

print_success() {
    echo -e "${GREEN}  ${SUCCESS} $1${NC}"
    log "SUCCESS: $1"
}

print_warning() {
    echo -e "${YELLOW}  ${WARNING} $1${NC}"
    log "WARNING: $1"
}

print_error() {
    echo -e "${RED}  ${ERROR} $1${NC}"
    log "ERROR: $1"
}

print_info() {
    echo -e "${CYAN}  ${INFO} $1${NC}"
    log "INFO: $1"
}

print_python() {
    echo -e "${PURPLE}  ${PYTHON} $1${NC}"
    log "PYTHON: $1"
}

# Error handling
error_exit() {
    print_error "Installation failed: $1"
    print_info "Check log file: $LOG_FILE"
    exit 1
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}${ERROR} This script must be run as root or with sudo${NC}"
        echo -e "${CYAN}${INFO} Usage: sudo $0${NC}"
        exit 1
    fi
    
    if [ -z "$SUDO_USER" ]; then
        error_exit "SUDO_USER not set. Please run with 'sudo $0' not as root user directly"
    fi
}

# Complete system cleanup for Python 3.13
complete_system_cleanup() {
    print_step "🧹 Python 3.13 Environment Preparation"
    
    print_substep "Removing any existing CryptoMiner Pro installation"
    rm -rf "$PROJECT_DIR" 2>/dev/null || true
    
    print_substep "Clearing all pip caches (Python 3.13 compatible cleanup)"
    pip cache purge 2>/dev/null || true
    pip3 cache purge 2>/dev/null || true
    python3.13 -m pip cache purge 2>/dev/null || true
    sudo -u "$SUDO_USER" pip cache purge 2>/dev/null || true
    
    print_substep "Removing temporary build artifacts"
    rm -rf /tmp/pip-* 2>/dev/null || true
    rm -rf /tmp/build-env-* 2>/dev/null || true
    find /tmp -name "*python*" -type d -exec rm -rf {} + 2>/dev/null || true
    
    print_success "Clean environment prepared for Python 3.13"
}

# Python 3.13 validation and setup
setup_python313_environment() {
    print_step "🐍 Python 3.13 Environment Setup"
    
    print_substep "Checking for Python 3.13"
    if ! command -v $REQUIRED_PYTHON &> /dev/null; then
        print_warning "Python 3.13 not found. Installing..."
        
        # Install Python 3.13 from deadsnakes PPA
        print_substep "Adding deadsnakes PPA for Python 3.13"
        apt update >> "$LOG_FILE" 2>&1
        apt install -y software-properties-common >> "$LOG_FILE" 2>&1
        add-apt-repository -y ppa:deadsnakes/ppa >> "$LOG_FILE" 2>&1
        apt update >> "$LOG_FILE" 2>&1
        
        print_substep "Installing Python 3.13 and development tools"
        apt install -y python3.13 python3.13-dev python3.13-venv python3.13-distutils >> "$LOG_FILE" 2>&1 || \
            error_exit "Failed to install Python 3.13"
    fi
    
    DETECTED_VERSION=$($REQUIRED_PYTHON --version 2>&1 | cut -d' ' -f2)
    print_python "Found Python $DETECTED_VERSION"
    
    print_substep "Verifying Python 3.13 functionality"
    $REQUIRED_PYTHON -c "import sys; assert sys.version_info >= (3, 13), 'Python 3.13+ required'" || \
        error_exit "Python 3.13 version validation failed"
    
    print_substep "Installing modern pip for Python 3.13"
    $REQUIRED_PYTHON -m ensurepip --upgrade >> "$LOG_FILE" 2>&1 || true
    $REQUIRED_PYTHON -m pip install --upgrade pip >> "$LOG_FILE" 2>&1 || \
        error_exit "Failed to upgrade pip for Python 3.13"
    
    print_success "Python 3.13 environment ready"
    
    # Export the validated Python path
    export VALIDATED_PYTHON="$REQUIRED_PYTHON"
}

# Install system dependencies
install_system_dependencies() {
    print_step "Installing System Dependencies"
    
    print_substep "Updating package lists"
    apt update >> "$LOG_FILE" 2>&1 || error_exit "Failed to update package lists"
    
    print_substep "Installing essential build tools"
    apt install -y curl wget gnupg2 software-properties-common apt-transport-https ca-certificates \
        build-essential gcc g++ libc6-dev git supervisor ufw htop >> "$LOG_FILE" 2>&1 || \
        error_exit "Failed to install essential packages"
    
    print_success "System dependencies installed"
}

# Install Node.js
install_nodejs() {
    print_step "Installing Node.js 20 LTS"
    
    print_substep "Adding NodeSource repository"
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - >> "$LOG_FILE" 2>&1 || \
        error_exit "Failed to add NodeSource repository"
    
    print_substep "Installing Node.js and npm"
    apt install -y nodejs >> "$LOG_FILE" 2>&1 || error_exit "Failed to install Node.js"
    
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    print_success "Node.js $NODE_VERSION and npm $NPM_VERSION installed"
}

# Install MongoDB
install_mongodb() {
    print_step "Installing MongoDB 7.0"
    
    print_substep "Adding MongoDB repository key"
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
        gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg >> "$LOG_FILE" 2>&1 || \
        error_exit "Failed to add MongoDB key"
    
    print_substep "Adding MongoDB repository"
    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
        tee /etc/apt/sources.list.d/mongodb-org-7.0.list >> "$LOG_FILE" 2>&1
    
    print_substep "Updating package lists"
    apt update >> "$LOG_FILE" 2>&1 || error_exit "Failed to update package lists"
    
    print_substep "Installing MongoDB"
    apt install -y mongodb-org >> "$LOG_FILE" 2>&1 || error_exit "Failed to install MongoDB"
    
    print_substep "Starting and enabling MongoDB service"
    systemctl start mongod >> "$LOG_FILE" 2>&1 || error_exit "Failed to start MongoDB"
    systemctl enable mongod >> "$LOG_FILE" 2>&1 || error_exit "Failed to enable MongoDB"
    
    sleep 5
    if mongosh --eval "db.adminCommand('ismaster')" >> "$LOG_FILE" 2>&1; then
        print_success "MongoDB 7.0 installed and running"
    else
        error_exit "MongoDB installation failed - service not responding"
    fi
}

# Create project structure
create_project_structure() {
    print_step "Creating Project Structure"
    
    mkdir -p "$PROJECT_DIR"/{backend,frontend/{src,public},logs,scripts,docs} || \
        error_exit "Failed to create project directory"
    
    chown -R "$SUDO_USER:$SUDO_USER" "$PROJECT_DIR" || \
        error_exit "Failed to set directory ownership"
    
    print_success "Project structure created at $PROJECT_DIR"
}

# Copy application source code
copy_source_code() {
    print_step "Installing Application Source Code"
    
    CURRENT_DIR=$(pwd)
    
    if [ -f "$CURRENT_DIR/backend/server.py" ]; then
        print_substep "Copying backend source code"
        cp -r "$CURRENT_DIR/backend"/* "$PROJECT_DIR/backend/" 2>/dev/null || true
        print_success "Backend source code copied"
    fi
    
    if [ -f "$CURRENT_DIR/frontend/src/App.js" ]; then
        print_substep "Copying frontend source code"
        cp -r "$CURRENT_DIR/frontend/src" "$PROJECT_DIR/frontend/" 2>/dev/null || true
        cp -r "$CURRENT_DIR/frontend/public" "$PROJECT_DIR/frontend/" 2>/dev/null || true
        print_success "Frontend source code copied"
    fi
    
    chown -R "$SUDO_USER:$SUDO_USER" "$PROJECT_DIR"
    print_success "Application source code installation completed"
}

# Install application with Python 3.13 compatibility
install_application() {
    print_step "🐍 Installing CryptoMiner Pro (Python 3.13 Compatible)"
    
    # Create Python 3.13 compatible requirements
    print_substep "Creating Python 3.13 compatible requirements"
    cat > "$PROJECT_DIR/backend/requirements.txt" << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
pymongo==4.6.0
motor==3.3.2
pydantic==2.5.0
python-multipart==0.0.6
psutil==5.9.6
numpy==1.26.4
scikit-learn==1.4.2
pandas==2.2.1
aiofiles==23.2.1
cryptography>=41.0.0
requests==2.31.0
aiohttp==3.9.1
python-dotenv==1.0.0
EOF

    # Create backend environment file
    cat > "$PROJECT_DIR/backend/.env" << EOF
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=crypto_miner_db
SECRET_KEY=$(openssl rand -hex 32)
CORS_ORIGINS=["http://localhost:3000"]
MAX_THREADS=$(nproc)
DEFAULT_SCRYPT_N=1024
DEFAULT_SCRYPT_R=1
DEFAULT_SCRYPT_P=1
EOF

    # Create frontend package.json
    cat > "$PROJECT_DIR/frontend/package.json" << 'EOF'
{
  "name": "crypto-mining-dashboard",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^5.17.0",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^14.5.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "web-vitals": "^2.1.4",
    "axios": "^1.6.0",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0",
    "socket.io-client": "^4.7.4",
    "tailwindcss": "^3.3.6",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "@heroicons/react": "^2.0.18",
    "classnames": "^2.3.2"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "proxy": "http://localhost:8001"
}
EOF

    # Create frontend environment file
    cat > "$PROJECT_DIR/frontend/.env" << 'EOF'
REACT_APP_BACKEND_URL=http://localhost:8001
GENERATE_SOURCEMAP=false
FAST_REFRESH=true
EOF

    # Install Python dependencies in Python 3.13 virtual environment
    print_substep "Creating Python 3.13 virtual environment"
    cd "$PROJECT_DIR/backend"
    
    if [ ! -d "$PROJECT_DIR/venv" ]; then
        sudo -u "$SUDO_USER" $VALIDATED_PYTHON -m venv "$PROJECT_DIR/venv" >> "$LOG_FILE" 2>&1 || \
            error_exit "Failed to create Python 3.13 virtual environment"
        
        chown -R "$SUDO_USER:$SUDO_USER" "$PROJECT_DIR/venv" || \
            error_exit "Failed to set virtual environment permissions"
    fi
    
    # Verify Python 3.13 in virtual environment
    VENV_PYTHON_VERSION=$("$PROJECT_DIR/venv/bin/python" --version 2>&1)
    print_python "Virtual environment using: $VENV_PYTHON_VERSION"
    
    if [[ ! "$VENV_PYTHON_VERSION" =~ "3.13" ]]; then
        error_exit "Virtual environment is not using Python 3.13! Got: $VENV_PYTHON_VERSION"
    fi
    
    # Upgrade pip and build tools in Python 3.13 environment
    print_substep "Upgrading build tools in Python 3.13 environment"
    sudo -u "$SUDO_USER" "$PROJECT_DIR/venv/bin/pip" install --upgrade pip setuptools wheel >> "$LOG_FILE" 2>&1 || \
        error_exit "Failed to upgrade build tools"
    
    # Install packages with Python 3.13 compatible versions
    print_substep "Installing Python 3.13 compatible packages (pre-compiled wheels only)"
    print_python "Using --only-binary=all to avoid compilation issues"
    
    if sudo -u "$SUDO_USER" "$PROJECT_DIR/venv/bin/pip" install --only-binary=all -r requirements.txt >> "$LOG_FILE" 2>&1; then
        print_success "Python 3.13 compatible packages installed successfully"
    else
        print_warning "Some packages may need to be built from source"
        print_substep "Trying with --prefer-binary flag"
        
        if sudo -u "$SUDO_USER" "$PROJECT_DIR/venv/bin/pip" install --prefer-binary -r requirements.txt >> "$LOG_FILE" 2>&1; then
            print_success "Python 3.13 packages installed with binary preference"
        else
            error_exit "Failed to install Python 3.13 compatible packages"
        fi
    fi
    
    # Install frontend dependencies
    print_substep "Installing Node.js dependencies"
    cd "$PROJECT_DIR/frontend"
    sudo -u "$SUDO_USER" npm install >> "$LOG_FILE" 2>&1 || \
        error_exit "Failed to install Node.js dependencies"
    
    print_success "All dependencies installed for Python 3.13"
}

# Setup supervisor with Python 3.13 path
setup_supervisor() {
    print_step "Configuring Service Management (Python 3.13)"
    
    PYTHON_CMD="$PROJECT_DIR/venv/bin/python"
    PYTHON_PATH="$PROJECT_DIR/venv/bin:/home/$SUDO_USER/.local/bin:/usr/bin:/bin"
    
    cat > /etc/supervisor/conf.d/cryptominer-pro.conf << EOF
[program:cryptominer-backend]
command=$PYTHON_CMD -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
directory=$PROJECT_DIR/backend
user=$SUDO_USER
autostart=true
autorestart=true
stderr_logfile=$PROJECT_DIR/logs/backend.err.log
stdout_logfile=$PROJECT_DIR/logs/backend.out.log
environment=PATH="$PYTHON_PATH",PYTHONPATH="$PROJECT_DIR/backend"

[program:cryptominer-frontend]
command=npm start
directory=$PROJECT_DIR/frontend
user=$SUDO_USER
autostart=true
autorestart=true
stderr_logfile=$PROJECT_DIR/logs/frontend.err.log
stdout_logfile=$PROJECT_DIR/logs/frontend.out.log
environment=PORT=3000,PATH="/usr/bin:/bin:/usr/local/bin"

[group:cryptominer-pro]
programs=cryptominer-backend,cryptominer-frontend
priority=999
EOF

    mkdir -p "$PROJECT_DIR/logs"
    chown -R "$SUDO_USER:$SUDO_USER" "$PROJECT_DIR/logs"
    
    supervisorctl reread >> "$LOG_FILE" 2>&1 || error_exit "Failed to read supervisor config"
    supervisorctl update >> "$LOG_FILE" 2>&1 || error_exit "Failed to update supervisor config"
    
    print_success "Service management configured for Python 3.13"
}

# Start services and verify
start_and_verify() {
    print_step "🚀 Starting Services and Verification"
    
    print_substep "Starting CryptoMiner Pro services"
    supervisorctl start cryptominer-pro:* >> "$LOG_FILE" 2>&1 || \
        error_exit "Failed to start services"
    
    print_substep "Waiting for services to initialize"
    sleep 10
    
    # Verify Python 3.13 is running
    print_substep "Verifying Python 3.13 backend service"
    if supervisorctl status cryptominer-pro:cryptominer-backend | grep -q RUNNING; then
        print_python "Backend service running with Python 3.13"
    else
        print_warning "Backend service may have issues"
    fi
    
    # Test API
    print_substep "Testing backend API"
    if curl -s http://localhost:8001/api/health >> "$LOG_FILE" 2>&1; then
        print_success "Backend API responding correctly"
    else
        print_warning "Backend API test failed - may still be starting"
    fi
    
    print_success "Python 3.13 installation completed successfully!"
}

# Main installation function
main() {
    echo "CryptoMiner Pro Python 3.13 Installation Log - $(date)" > "$LOG_FILE"
    
    print_header
    check_root
    
    echo -e "${YELLOW}${WARNING} This will install CryptoMiner Pro with Python 3.13 support${NC}"
    echo -e "${PURPLE}${PYTHON} Using the latest Python 3.13 with modern package compatibility${NC}"
    echo ""
    read -p "Do you want to continue with Python 3.13 installation? [y/N]: " -r
    echo ""
    if [ ! "$REPLY" = "y" ] && [ ! "$REPLY" = "Y" ]; then
        echo -e "${CYAN}Installation cancelled by user${NC}"
        exit 0
    fi
    
    # Start Python 3.13 installation process
    complete_system_cleanup
    setup_python313_environment
    install_system_dependencies
    install_nodejs
    install_mongodb
    create_project_structure
    copy_source_code
    install_application
    setup_supervisor
    start_and_verify
    
    print_header
    echo -e "${GREEN}🐍🎉🐍 PYTHON 3.13 INSTALLATION COMPLETED! 🐍🎉🐍${NC}"
    echo ""
    echo -e "${PURPLE}🐍 Python Version: $("$PROJECT_DIR/venv/bin/python" --version 2>&1)${NC}"
    echo -e "${CYAN}🌐 Dashboard: http://localhost:3000${NC}"
    echo -e "${CYAN}🔧 API: http://localhost:8001/docs${NC}"
    echo ""
    echo -e "${GREEN}✅ CryptoMiner Pro is now running on Python 3.13!${NC}"
    
    log "Python 3.13 installation completed successfully"
}

# Handle command line arguments
case "${1:-}" in
    "--help"|"-h")
        echo "CryptoMiner Pro - Python 3.13 Compatible Installer"
        echo ""
        echo "This installer specifically targets Python 3.13 compatibility"
        echo "with modern package versions and pre-compiled wheel preferences."
        echo ""
        echo "Usage: sudo $0"
        ;;
    *)
        main "$@"
        ;;
esac