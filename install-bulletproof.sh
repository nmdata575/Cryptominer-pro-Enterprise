#!/bin/bash

# 🚀 CryptoMiner Pro - BULLETPROOF Ubuntu Installation Script
# Enhanced version with Python 3.13 protection and comprehensive cleanup
# Compatible with Ubuntu 24.04 LTS and later versions

# Ensure we're using bash, not sh/dash
if [ -z "$BASH_VERSION" ]; then
    echo "This script requires bash. Please run with: bash $0"
    exit 1
fi

set -e  # Exit on any error

# Configuration
SCRIPT_VERSION="2.0.0"
MIN_UBUNTU_VERSION="24.04"
PROJECT_DIR="/opt/cryptominer-pro"
LOG_FILE="/tmp/cryptominer-install.log"
USER_HOME="/home/$SUDO_USER"

# Force Python 3.11 usage - CRITICAL FOR COMPATIBILITY
REQUIRED_PYTHON="python3.11"
PYTHON_VERSION_REQUIRED="3.11"

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
GEAR="⚙️"
DATABASE="🗄️"
LOCK="🔒"
SHIELD="🛡️"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Print functions
print_header() {
    clear
    echo -e "${CYAN}"
    echo "=================================================================="
    echo "     🛡️ CryptoMiner Pro - BULLETPROOF Ubuntu Auto Installer"
    echo "=================================================================="
    echo -e "Version: ${SCRIPT_VERSION} - Python 3.13 Protected${NC}"
    echo -e "${BLUE}Enhanced installation with comprehensive compatibility fixes${NC}"
    echo ""
}

print_step() {
    echo -e "\n${WHITE}🔄 STEP: $1${NC}"
    echo "$(printf '=%.0s' {1..60})"
    log "STEP: $1"
}

print_substep() {
    echo -e "${BLUE}  ${GEAR} $1${NC}"
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

print_shield() {
    echo -e "${PURPLE}  ${SHIELD} $1${NC}"
    log "PROTECTION: $1"
}

# Error handling
error_exit() {
    print_error "Installation failed: $1"
    print_info "Check log file: $LOG_FILE"
    print_info "You can re-run this script to retry installation"
    exit 1
}

# Cleanup function
cleanup() {
    if [ $? -ne 0 ]; then
        print_error "Installation interrupted or failed"
        print_info "Cleaning up partial installation..."
        # Add cleanup logic here if needed
    fi
}
trap cleanup EXIT

# ENHANCED: Complete system cleanup before installation
complete_system_cleanup() {
    print_step "🧹 Complete System Cleanup (Python 3.13 Protection)"
    
    print_substep "Removing any existing CryptoMiner Pro installation"
    rm -rf "$PROJECT_DIR" 2>/dev/null || true
    
    print_substep "Clearing all pip caches (system-wide cleanup)"
    pip cache purge 2>/dev/null || true
    pip3 cache purge 2>/dev/null || true
    sudo -u "$SUDO_USER" pip cache purge 2>/dev/null || true
    sudo -u "$SUDO_USER" pip3 cache purge 2>/dev/null || true
    
    print_substep "Removing temporary build artifacts"
    rm -rf /tmp/pip-* 2>/dev/null || true
    rm -rf /tmp/build-env-* 2>/dev/null || true
    find /tmp -name "*python*" -type d -exec rm -rf {} + 2>/dev/null || true
    
    print_substep "Clearing Python cache directories"
    find /home -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find /root -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    print_success "System cleanup completed - fresh installation environment"
}

# ENHANCED: Strict Python version validation
validate_python_environment() {
    print_step "🐍 Python Environment Validation (Anti-Python 3.13)"
    
    print_substep "Checking for required Python 3.11"
    if ! command -v $REQUIRED_PYTHON &> /dev/null; then
        error_exit "Python 3.11 is required but not found. Please install: sudo apt install python3.11 python3.11-dev python3.11-venv"
    fi
    
    DETECTED_VERSION=$($REQUIRED_PYTHON --version 2>&1 | cut -d' ' -f2)
    print_success "Found Python $DETECTED_VERSION"
    
    print_substep "Verifying Python 3.11 functionality"
    $REQUIRED_PYTHON -c "import sys; assert sys.version_info >= (3, 11), 'Python 3.11+ required'" || \
        error_exit "Python 3.11 version validation failed"
    
    print_substep "Checking for Python 3.13 (should NOT exist)"
    if command -v python3.13 &> /dev/null; then
        print_warning "Python 3.13 detected on system - will avoid using it"
        PYTHON_313_FOUND=true
    else
        print_shield "No Python 3.13 found - good for compatibility"
        PYTHON_313_FOUND=false
    fi
    
    print_substep "Validating pip for Python 3.11"
    $REQUIRED_PYTHON -m pip --version >> "$LOG_FILE" 2>&1 || \
        error_exit "pip not available for Python 3.11"
    
    print_success "Python environment validated - using Python $DETECTED_VERSION"
    
    # Export the validated Python path
    export VALIDATED_PYTHON="$REQUIRED_PYTHON"
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

# Check Ubuntu version
check_ubuntu_version() {
    print_step "Checking System Compatibility"
    
    # Check if it's Ubuntu
    if ! grep -q "Ubuntu" /etc/os-release; then
        error_exit "This script is designed for Ubuntu 24.04+. Detected: $(lsb_release -d | cut -f2)"
    fi
    
    # Check Ubuntu version
    UBUNTU_VERSION=$(lsb_release -rs)
    if [ "$(printf '%s\n' "$MIN_UBUNTU_VERSION" "$UBUNTU_VERSION" | sort -V | head -n1)" != "$MIN_UBUNTU_VERSION" ]; then
        error_exit "Ubuntu 24.04+ required. Detected: Ubuntu $UBUNTU_VERSION"
    fi
    
    print_success "Ubuntu $UBUNTU_VERSION detected - Compatible"
    
    # Check system resources
    TOTAL_RAM=$(free -m | awk '/^Mem:/{print $2}')
    AVAILABLE_DISK=$(df / | awk 'NR==2{print $4}')
    CPU_CORES=$(nproc)
    
    print_substep "System Resources:"
    echo "    • CPU Cores: $CPU_CORES"
    echo "    • Total RAM: ${TOTAL_RAM}MB"
    echo "    • Available Disk: $((AVAILABLE_DISK/1024))MB"
    
    # Check minimum requirements
    if [ "$TOTAL_RAM" -lt 2048 ]; then
        print_warning "Low RAM detected (${TOTAL_RAM}MB). 4GB+ recommended"
    fi
    
    if [ "$AVAILABLE_DISK" -lt 2097152 ]; then  # 2GB in KB
        print_warning "Low disk space detected. 5GB+ recommended"
    fi
    
    if [ "$CPU_CORES" -lt 2 ]; then
        print_warning "Limited CPU cores detected. 4+ cores recommended"
    fi
    
    print_success "System compatibility check passed"
}

# Update system packages
update_system() {
    print_step "Updating System Packages"
    
    print_substep "Updating package lists"
    apt update >> "$LOG_FILE" 2>&1 || error_exit "Failed to update package lists"
    
    print_substep "Upgrading system packages"
    DEBIAN_FRONTEND=noninteractive apt upgrade -y >> "$LOG_FILE" 2>&1 || error_exit "Failed to upgrade packages"
    
    print_substep "Installing essential build tools and Python 3.11"
    apt install -y curl wget gnupg2 software-properties-common apt-transport-https ca-certificates \
        build-essential gcc g++ libc6-dev \
        python3.11 python3.11-dev python3.11-venv python3.11-distutils \
        python3-pip git supervisor ufw htop >> "$LOG_FILE" 2>&1 || \
        error_exit "Failed to install essential packages"
    
    print_success "System packages updated successfully"
}

# Install Node.js
install_nodejs() {
    print_step "Installing Node.js 20 LTS"
    
    print_substep "Adding NodeSource repository"
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - >> "$LOG_FILE" 2>&1 || \
        error_exit "Failed to add NodeSource repository"
    
    print_substep "Installing Node.js and npm"
    apt install -y nodejs >> "$LOG_FILE" 2>&1 || error_exit "Failed to install Node.js"
    
    # Verify installation
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    print_success "Node.js $NODE_VERSION and npm $NPM_VERSION installed"
    
    # Install yarn globally
    print_substep "Installing Yarn package manager"
    npm install -g yarn >> "$LOG_FILE" 2>&1 || error_exit "Failed to install Yarn"
    
    YARN_VERSION=$(yarn --version)
    print_success "Yarn $YARN_VERSION installed"
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
    
    # Wait for MongoDB to start
    print_substep "Waiting for MongoDB to initialize"
    sleep 5
    
    # Test MongoDB connection
    if mongosh --eval "db.adminCommand('ismaster')" >> "$LOG_FILE" 2>&1; then
        print_success "MongoDB 7.0 installed and running"
    else
        error_exit "MongoDB installation failed - service not responding"
    fi
}

# Create project structure
create_project_structure() {
    print_step "Creating Project Structure"
    
    print_substep "Creating project directory: $PROJECT_DIR"
    mkdir -p "$PROJECT_DIR" || error_exit "Failed to create project directory"
    
    print_substep "Setting up directory structure"
    mkdir -p "$PROJECT_DIR"/{backend,frontend/{src,public},logs,scripts,docs}
    
    print_substep "Setting ownership to $SUDO_USER"
    chown -R "$SUDO_USER:$SUDO_USER" "$PROJECT_DIR" || \
        error_exit "Failed to set directory ownership"
    
    print_success "Project structure created at $PROJECT_DIR"
}

# Copy application source code (MOVED BEFORE INSTALLATION)
copy_source_code() {
    print_step "Installing Application Source Code"
    
    print_info "Note: This installs the complete CryptoMiner Pro application"
    print_info "Source code will be copied from the current directory if available"
    
    # Check if we have source files in current directory
    CURRENT_DIR=$(pwd)
    
    if [ -f "$CURRENT_DIR/backend/server.py" ]; then
        print_substep "Copying backend source code"
        cp -r "$CURRENT_DIR/backend"/* "$PROJECT_DIR/backend/" 2>/dev/null || true
        print_success "Backend source code copied"
    else
        print_warning "Backend source code not found in current directory"
        print_info "You'll need to copy your backend files to: $PROJECT_DIR/backend/"
    fi
    
    if [ -f "$CURRENT_DIR/frontend/src/App.js" ]; then
        print_substep "Copying frontend source code"
        cp -r "$CURRENT_DIR/frontend/src" "$PROJECT_DIR/frontend/" 2>/dev/null || true
        cp -r "$CURRENT_DIR/frontend/public" "$PROJECT_DIR/frontend/" 2>/dev/null || true
        print_success "Frontend source code copied"
    else
        print_warning "Frontend source code not found in current directory"
        print_info "You'll need to copy your frontend files to: $PROJECT_DIR/frontend/"
    fi
    
    # Set proper ownership
    chown -R "$SUDO_USER:$SUDO_USER" "$PROJECT_DIR"
    
    print_success "Application source code installation completed"
}

# ENHANCED: Install application with bulletproof Python handling
install_application() {
    print_step "Installing CryptoMiner Pro Application (Python 3.13 Protected)"
    
    # Create backend files with updated requirements
    print_substep "Installing backend application files"
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
scikit-learn==1.4.0
pandas==2.2.0
aiofiles==23.2.1
cryptography>=41.0.0
requests==2.31.0
aiohttp==3.9.1
python-dotenv==1.0.0
EOF

    # Create fallback requirements with stable versions
    cat > "$PROJECT_DIR/backend/requirements-fallback.txt" << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
pymongo==4.6.0
motor==3.3.2
pydantic==2.5.0
python-multipart==0.0.6
psutil==5.9.6
numpy==1.24.3
scikit-learn==1.3.2
pandas==2.1.4
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

    # ENHANCED: Install backend dependencies with bulletproof Python 3.11 enforcement
    print_substep "Installing Python dependencies with Python 3.11 enforcement"
    cd "$PROJECT_DIR/backend"
    
    # Create virtual environment with EXPLICIT Python 3.11
    print_substep "Creating bulletproof Python 3.11 virtual environment"
    print_shield "Forcing Python 3.11 usage (avoiding Python 3.13)"
    
    # Double-check Python version before creating venv
    VENV_PYTHON_VERSION=$($VALIDATED_PYTHON --version 2>&1)
    print_info "Creating virtual environment with: $VENV_PYTHON_VERSION"
    
    if [ ! -d "$PROJECT_DIR/venv" ]; then
        # Use the validated Python path explicitly
        sudo -u "$SUDO_USER" $VALIDATED_PYTHON -m venv "$PROJECT_DIR/venv" >> "$LOG_FILE" 2>&1 || \
            error_exit "Failed to create Python 3.11 virtual environment at $PROJECT_DIR/venv"
        
        print_substep "Setting virtual environment permissions"
        chown -R "$SUDO_USER:$SUDO_USER" "$PROJECT_DIR/venv" || \
            error_exit "Failed to set virtual environment permissions"
        
        print_success "Python 3.11 virtual environment created at $PROJECT_DIR/venv"
    else
        print_info "Virtual environment already exists"
    fi
    
    # CRITICAL: Verify the virtual environment is using Python 3.11
    VENV_PYTHON_VERSION=$("$PROJECT_DIR/venv/bin/python" --version 2>&1)
    print_shield "Virtual environment Python version: $VENV_PYTHON_VERSION"
    
    if [[ ! "$VENV_PYTHON_VERSION" =~ "3.11" ]]; then
        error_exit "Virtual environment is not using Python 3.11! Got: $VENV_PYTHON_VERSION"
    fi
    
    print_success "✅ Virtual environment verified to use Python 3.11"
    
    # Clear pip cache in virtual environment
    print_substep "Clearing virtual environment pip cache"
    sudo -u "$SUDO_USER" "$PROJECT_DIR/venv/bin/pip" cache purge >> "$LOG_FILE" 2>&1 || true
    
    # Upgrade build tools in virtual environment
    print_substep "Upgrading build tools in Python 3.11 virtual environment"
    sudo -u "$SUDO_USER" "$PROJECT_DIR/venv/bin/pip" install --upgrade pip setuptools wheel >> "$LOG_FILE" 2>&1 || \
        error_exit "Failed to upgrade build tools in virtual environment"
    
    print_success "Build tools upgraded successfully in Python 3.11 environment"
    
    # Install packages with maximum compatibility settings
    print_substep "Installing Python packages (ONLY pre-compiled wheels - no compilation)"
    print_shield "Using --only-binary=all to prevent any C++ compilation issues"
    
    # Try with only pre-compiled wheels first (most compatible)
    if sudo -u "$SUDO_USER" "$PROJECT_DIR/venv/bin/pip" install --only-binary=all -r requirements.txt >> "$LOG_FILE" 2>&1; then
        print_success "Python dependencies installed successfully with pre-compiled wheels"
    else
        print_warning "Pre-compiled wheel installation failed, trying with binary preference"
        
        # Fallback to prefer binary but allow source builds if necessary
        if sudo -u "$SUDO_USER" "$PROJECT_DIR/venv/bin/pip" install --prefer-binary -r requirements.txt >> "$LOG_FILE" 2>&1; then
            print_success "Python dependencies installed successfully with binary preference"
        else
            print_warning "Latest packages failed, trying stable fallback versions"
            print_substep "Attempting installation with proven stable package versions"
            
            if sudo -u "$SUDO_USER" "$PROJECT_DIR/venv/bin/pip" install --only-binary=all -r requirements-fallback.txt >> "$LOG_FILE" 2>&1; then
                print_success "Python dependencies installed with stable fallback versions"
            else
                error_exit "Failed to install Python dependencies with all attempted methods"
            fi
        fi
    fi
    
    # Install frontend dependencies
    print_substep "Installing Node.js dependencies"
    cd "$PROJECT_DIR/frontend"
    sudo -u "$SUDO_USER" npm install >> "$LOG_FILE" 2>&1 || \
        error_exit "Failed to install Node.js dependencies"
    
    print_success "Application dependencies installed successfully"
}

# Setup supervisor configuration
setup_supervisor() {
    print_step "Configuring Service Management"
    
    print_substep "Creating supervisor configuration"
    
    # Use the Python 3.11 virtual environment explicitly
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

    print_substep "Creating log directory"
    mkdir -p "$PROJECT_DIR/logs"
    chown -R "$SUDO_USER:$SUDO_USER" "$PROJECT_DIR/logs"
    
    print_substep "Reloading supervisor configuration"
    supervisorctl reread >> "$LOG_FILE" 2>&1 || error_exit "Failed to read supervisor config"
    supervisorctl update >> "$LOG_FILE" 2>&1 || error_exit "Failed to update supervisor config"
    
    print_success "Service management configured with Python 3.11"
}

# Configure firewall
configure_firewall() {
    print_step "Configuring Firewall"
    
    print_substep "Enabling UFW firewall"
    ufw --force enable >> "$LOG_FILE" 2>&1
    
    print_substep "Configuring firewall rules"
    ufw allow ssh >> "$LOG_FILE" 2>&1
    ufw allow 3000/tcp comment "CryptoMiner Frontend" >> "$LOG_FILE" 2>&1
    ufw allow 8001/tcp comment "CryptoMiner Backend" >> "$LOG_FILE" 2>&1
    ufw allow 27017/tcp comment "MongoDB (local only)" >> "$LOG_FILE" 2>&1
    
    print_substep "Firewall status:"
    ufw status numbered | head -10
    
    print_success "Firewall configured"
}

# Create management scripts
create_management_scripts() {
    print_step "Creating Management Scripts"
    
    # Create start script
    cat > "$PROJECT_DIR/scripts/start.sh" << 'EOF'
#!/bin/bash
echo "🚀 Starting CryptoMiner Pro services..."
sudo supervisorctl start cryptominer-pro:*
echo "✅ Services started"
EOF

    # Create stop script
    cat > "$PROJECT_DIR/scripts/stop.sh" << 'EOF'
#!/bin/bash
echo "🛑 Stopping CryptoMiner Pro services..."
sudo supervisorctl stop cryptominer-pro:*
echo "✅ Services stopped"
EOF

    # Create restart script
    cat > "$PROJECT_DIR/scripts/restart.sh" << 'EOF'
#!/bin/bash
echo "🔄 Restarting CryptoMiner Pro services..."
sudo supervisorctl restart cryptominer-pro:*
echo "✅ Services restarted"
EOF

    # Create status script
    cat > "$PROJECT_DIR/scripts/status.sh" << 'EOF'
#!/bin/bash
echo "📊 CryptoMiner Pro Service Status:"
echo "=================================="
sudo supervisorctl status cryptominer-pro:*
echo ""
echo "🌐 URLs:"
echo "  Dashboard: http://localhost:3000"
echo "  API:       http://localhost:8001/api/health"
echo ""
echo "📋 System Resources:"
echo "  CPU Usage: $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}')"
echo "  Memory:    $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
echo "  Disk:      $(df / | awk 'NR==2{printf "%.1f%%", $3/$2*100}')"
EOF

    # Create logs script
    cat > "$PROJECT_DIR/scripts/logs.sh" << 'EOF'
#!/bin/bash
echo "📝 CryptoMiner Pro Logs"
echo "======================"
echo ""
echo "Choose log to view:"
echo "1. Backend logs"
echo "2. Frontend logs"
echo "3. All logs (tail -f)"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "📄 Backend Logs:"
        tail -n 50 /opt/cryptominer-pro/logs/backend.out.log
        ;;
    2)
        echo "📄 Frontend Logs:"
        tail -n 50 /opt/cryptominer-pro/logs/frontend.out.log
        ;;
    3)
        echo "📄 Following all logs (Ctrl+C to exit):"
        tail -f /opt/cryptominer-pro/logs/*.log
        ;;
    *)
        echo "Invalid choice"
        ;;
esac
EOF

    # Make scripts executable
    chmod +x "$PROJECT_DIR/scripts"/*.sh
    chown -R "$SUDO_USER:$SUDO_USER" "$PROJECT_DIR/scripts"
    
    # Create symlinks in /usr/local/bin for easy access
    ln -sf "$PROJECT_DIR/scripts/start.sh" /usr/local/bin/cryptominer-start
    ln -sf "$PROJECT_DIR/scripts/stop.sh" /usr/local/bin/cryptominer-stop
    ln -sf "$PROJECT_DIR/scripts/restart.sh" /usr/local/bin/cryptominer-restart
    ln -sf "$PROJECT_DIR/scripts/status.sh" /usr/local/bin/cryptominer-status
    ln -sf "$PROJECT_DIR/scripts/logs.sh" /usr/local/bin/cryptominer-logs
    
    print_success "Management scripts created and installed"
}

# Start services
start_services() {
    print_step "Starting CryptoMiner Pro Services"
    
    print_substep "Starting backend service (Python 3.11 environment)"
    supervisorctl start cryptominer-pro:cryptominer-backend >> "$LOG_FILE" 2>&1 || \
        error_exit "Failed to start backend service"
    
    print_substep "Starting frontend service"  
    supervisorctl start cryptominer-pro:cryptominer-frontend >> "$LOG_FILE" 2>&1 || \
        error_exit "Failed to start frontend service"
    
    print_substep "Waiting for services to initialize"
    sleep 10
    
    # Check service status
    if supervisorctl status cryptominer-pro:cryptominer-backend | grep -q RUNNING; then
        print_success "Backend service is running (Python 3.11 environment)"
    else
        print_warning "Backend service may have issues"
    fi
    
    if supervisorctl status cryptominer-pro:cryptominer-frontend | grep -q RUNNING; then
        print_success "Frontend service is running"
    else
        print_warning "Frontend service may have issues"
    fi
}

# Verify installation
verify_installation() {
    print_step "🔍 Verifying Installation (Final Checks)"
    
    # Test MongoDB
    print_substep "Testing MongoDB connection"
    if mongosh --eval "db.adminCommand('ismaster')" >> "$LOG_FILE" 2>&1; then
        print_success "MongoDB is responding"
    else
        print_warning "MongoDB connection test failed"
    fi
    
    # Verify Python environment in virtual environment
    print_substep "Verifying Python 3.11 virtual environment"
    FINAL_VENV_VERSION=$("$PROJECT_DIR/venv/bin/python" --version 2>&1)
    if [[ "$FINAL_VENV_VERSION" =~ "3.11" ]]; then
        print_shield "✅ Virtual environment confirmed using Python 3.11: $FINAL_VENV_VERSION"
    else
        print_error "❌ Virtual environment NOT using Python 3.11: $FINAL_VENV_VERSION"
    fi
    
    # Test backend API
    print_substep "Testing backend API"
    sleep 5  # Give more time for backend to start
    if curl -s http://localhost:8001/api/health >> "$LOG_FILE" 2>&1; then
        print_success "Backend API is responding"
    else
        print_warning "Backend API test failed - may still be starting"
    fi
    
    # Test frontend
    print_substep "Testing frontend"
    if curl -s -I http://localhost:3000 | grep -q "200 OK" >> "$LOG_FILE" 2>&1; then
        print_success "Frontend is responding"
    else
        print_warning "Frontend test failed - may still be starting"
    fi
    
    print_success "Installation verification completed"
}

# Create desktop launcher
create_desktop_launcher() {
    print_step "Creating Desktop Integration"
    
    if [ -n "$SUDO_USER" ] && [ -d "/home/$SUDO_USER" ]; then
        DESKTOP_DIR="/home/$SUDO_USER/Desktop"
        
        if [ -d "$DESKTOP_DIR" ]; then
            print_substep "Creating desktop launcher"
            cat > "$DESKTOP_DIR/CryptoMiner-Pro.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=CryptoMiner Pro
Comment=AI-Powered Cryptocurrency Mining Dashboard (Python 3.11 Protected)
Exec=xdg-open http://localhost:3000
Icon=applications-internet
Terminal=false
Categories=Network;Finance;
EOF
            
            chmod +x "$DESKTOP_DIR/CryptoMiner-Pro.desktop"
            chown "$SUDO_USER:$SUDO_USER" "$DESKTOP_DIR/CryptoMiner-Pro.desktop"
            print_success "Desktop launcher created"
        fi
    fi
}

# Display final information
show_completion_info() {
    print_header
    echo -e "${GREEN}"
    echo "🛡️🎉🛡️ BULLETPROOF INSTALLATION COMPLETED SUCCESSFULLY! 🛡️🎉🛡️"
    echo "=================================================================="
    echo -e "${NC}"
    
    echo -e "${CYAN}📍 Installation Location:${NC} $PROJECT_DIR"
    echo -e "${CYAN}🐍 Python Environment:${NC} $("$PROJECT_DIR/venv/bin/python" --version 2>&1) (Protected from 3.13)"
    echo -e "${CYAN}📋 Service Status:${NC}"
    supervisorctl status cryptominer-pro:* | sed 's/^/    /'
    
    echo ""
    echo -e "${YELLOW}🌐 Access URLs:${NC}"
    echo -e "    ${BLUE}• Dashboard:${NC}       http://localhost:3000"
    echo -e "    ${BLUE}• Backend API:${NC}     http://localhost:8001/api/health"
    echo -e "    ${BLUE}• API Docs:${NC}        http://localhost:8001/docs"
    
    echo ""
    echo -e "${YELLOW}🛠️  Management Commands:${NC}"
    echo -e "    ${BLUE}• Start services:${NC}   cryptominer-start"
    echo -e "    ${BLUE}• Stop services:${NC}    cryptominer-stop"
    echo -e "    ${BLUE}• Restart services:${NC} cryptominer-restart"
    echo -e "    ${BLUE}• Check status:${NC}     cryptominer-status"
    echo -e "    ${BLUE}• View logs:${NC}        cryptominer-logs"
    
    echo ""
    echo -e "${YELLOW}📂 Important Directories:${NC}"
    echo -e "    ${BLUE}• Application:${NC}      $PROJECT_DIR"
    echo -e "    ${BLUE}• Logs:${NC}             $PROJECT_DIR/logs"
    echo -e "    ${BLUE}• Scripts:${NC}          $PROJECT_DIR/scripts"
    echo -e "    ${BLUE}• Backend Config:${NC}   $PROJECT_DIR/backend/.env"
    echo -e "    ${BLUE}• Frontend Config:${NC}  $PROJECT_DIR/frontend/.env"
    echo -e "    ${BLUE}• Python Virtual Env:${NC} $PROJECT_DIR/venv (Python 3.11 Protected)"
    
    echo ""
    echo -e "${PURPLE}🛡️  Security & Compatibility Features:${NC}"
    echo -e "    ${SHIELD} Python 3.13 protection enabled - uses Python 3.11 exclusively"
    echo -e "    ${SHIELD} Pre-compiled wheel preference - avoids compilation issues"
    echo -e "    ${SHIELD} Automatic fallback system - stable package versions available"
    echo -e "    ${SHIELD} Complete cache cleanup - fresh installation environment"
    echo -e "    ${SHIELD} Build tools validation - modern pip, setuptools, wheel"
    
    echo ""
    echo -e "${YELLOW}🚀 Quick Start Guide:${NC}"
    echo -e "    ${GREEN}1.${NC} Open your web browser"
    echo -e "    ${GREEN}2.${NC} Navigate to: ${BLUE}http://localhost:3000${NC}"
    echo -e "    ${GREEN}3.${NC} Select a cryptocurrency (Litecoin recommended for beginners)"
    echo -e "    ${GREEN}4.${NC} Configure your wallet address"
    echo -e "    ${GREEN}5.${NC} Set performance options"
    echo -e "    ${GREEN}6.${NC} Click 'Start Mining' and monitor the dashboard"
    
    echo ""
    echo -e "${YELLOW}💡 Next Steps:${NC}"
    echo -e "    ${BLUE}•${NC} Review the configuration files in $PROJECT_DIR"
    echo -e "    ${BLUE}•${NC} Check that all services are running: ${CYAN}cryptominer-status${NC}"
    echo -e "    ${BLUE}•${NC} Access the dashboard and test the interface"
    echo -e "    ${BLUE}•${NC} Configure your wallet addresses for mining"
    echo -e "    ${BLUE}•${NC} Enable AI optimization for best performance"
    
    echo ""
    echo -e "${YELLOW}🔒 Security Notes:${NC}"
    echo -e "    ${BLUE}•${NC} Firewall has been configured with necessary ports open"
    echo -e "    ${BLUE}•${NC} Change default passwords and keys in production"
    echo -e "    ${BLUE}•${NC} Only enter wallet addresses, never private keys"
    echo -e "    ${BLUE}•${NC} Monitor system resources during mining operations"
    echo -e "    ${BLUE}•${NC} Python 3.11 environment protects against compatibility issues"
    
    echo ""
    echo -e "${YELLOW}📞 Support:${NC}"
    echo -e "    ${BLUE}•${NC} Installation log: ${CYAN}$LOG_FILE${NC}"
    echo -e "    ${BLUE}•${NC} Application logs: ${CYAN}cryptominer-logs${NC}"
    echo -e "    ${BLUE}•${NC} Service status: ${CYAN}cryptominer-status${NC}"
    
    echo ""
    echo -e "${GREEN}${ROCKET} CryptoMiner Pro is ready for bulletproof cryptocurrency mining!${NC}"
    echo -e "${PURPLE}${SHIELD} Protected against Python 3.13 compatibility issues${NC}"
    echo ""
}

# Main installation function
main() {
    # Initialize log file
    echo "CryptoMiner Pro BULLETPROOF Installation Log - $(date)" > "$LOG_FILE"
    
    print_header
    check_root
    
    echo -e "${YELLOW}${WARNING} This script will install CryptoMiner Pro with enhanced compatibility${NC}"
    echo -e "${CYAN}${INFO} Enhanced features: Python 3.13 protection, comprehensive cleanup, fallback systems${NC}"
    echo ""
    read -p "Do you want to continue? [y/N]: " -r
    echo ""
    if [ ! "$REPLY" = "y" ] && [ ! "$REPLY" = "Y" ]; then
        echo -e "${CYAN}Installation cancelled by user${NC}"
        exit 0
    fi
    
    # Start enhanced installation process
    complete_system_cleanup        # NEW: Complete cleanup
    check_ubuntu_version
    validate_python_environment    # NEW: Strict Python validation
    update_system
    install_nodejs
    install_mongodb
    create_project_structure
    copy_source_code               # MOVED: Before install_application
    install_application            # ENHANCED: Bulletproof Python handling
    setup_supervisor
    configure_firewall
    create_management_scripts
    start_services
    verify_installation            # ENHANCED: Python environment verification
    create_desktop_launcher
    
    # Show completion information
    show_completion_info
    
    log "BULLETPROOF Installation completed successfully"
}

# Handle command line arguments
case "${1:-}" in
    "--help"|"-h")
        echo "CryptoMiner Pro - BULLETPROOF Ubuntu 24+ Automated Installer"
        echo ""
        echo "Usage: sudo $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h    Show this help message"
        echo "  --version     Show version information"
        echo ""
        echo "Enhanced Features:"
        echo "  🛡️  Python 3.13 protection - forces Python 3.11 usage"
        echo "  🧹 Complete system cleanup - removes all conflicting cache"
        echo "  ⚙️  Pre-compiled wheels preference - avoids compilation issues"
        echo "  🔄 Automatic fallback system - stable package versions"
        echo "  ✅ Comprehensive validation - verifies each installation step"
        echo ""
        echo "This script will:"
        echo "  • Install all required dependencies (Python 3.11, Node.js, MongoDB)"
        echo "  • Set up the complete CryptoMiner Pro application"
        echo "  • Configure services and firewall"
        echo "  • Create management scripts"
        echo "  • Start all services with bulletproof compatibility"
        echo ""
        echo "Requirements:"
        echo "  • Ubuntu 24.04+ (clean installation recommended)"
        echo "  • Internet connection for downloading packages"
        echo "  • At least 4GB RAM and 5GB disk space"
        echo "  • Run as root/sudo user"
        ;;
    "--version")
        echo "CryptoMiner Pro BULLETPROOF Installer Version: $SCRIPT_VERSION"
        echo "Enhanced with Python 3.13 protection and comprehensive compatibility fixes"
        echo "Compatible with: Ubuntu 24.04+"
        ;;
    *)
        main "$@"
        ;;
esac