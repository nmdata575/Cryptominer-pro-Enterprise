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
# Auto-detect installation directory from supervisor config or use default
INSTALL_DIR_DEFAULT="/opt/cryptominer-pro"
SERVICE_NAME="cryptominer-pro"
PYTHON_VERSION="3.11"
NODE_VERSION="18"
PYTHON_CMD="python3"  # Will be updated by check_and_install_python function

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Auto-detect actual installation directory
detect_install_dir() {
    # Method 1: Check supervisor configuration
    if [ -f /etc/supervisor/conf.d/mining_system.conf ]; then
        local detected_dir=$(grep "directory=" /etc/supervisor/conf.d/mining_system.conf | grep backend | cut -d'=' -f2 | sed 's|/backend||' | head -1)
        if [ -n "$detected_dir" ] && [ -d "$detected_dir" ]; then
            INSTALL_DIR="$detected_dir"
            log "Detected installation directory from supervisor config: $INSTALL_DIR"
            return 0
        fi
    fi
    
    # Method 2: Look for running processes
    local process_dir=$(ps aux | grep "server.py" | grep -v grep | awk '{for(i=11;i<=NF;i++) print $i}' | grep server.py | head -1 | xargs dirname 2>/dev/null)
    if [ -n "$process_dir" ] && [ -d "$process_dir" ]; then
        INSTALL_DIR="$(dirname "$process_dir")"
        log "Detected installation directory from running process: $INSTALL_DIR"
        return 0
    fi
    
    # Method 3: Check common locations
    local common_locations=(
        "/opt/cryptominer-pro"
        "/usr/local/cryptominer-pro" 
        "/home/$USER/cryptominer-pro"
        "$HOME/Desktop/Cryptominer-pro-Enterprise-main"
        "$SCRIPT_DIR"
    )
    
    for dir in "${common_locations[@]}"; do
        if [ -d "$dir/backend" ] && [ -f "$dir/backend/server.py" ]; then
            INSTALL_DIR="$dir"
            log "Found installation directory: $INSTALL_DIR"
            return 0
        fi
    done
    
    # Method 4: Use default and create if needed
    INSTALL_DIR="$INSTALL_DIR_DEFAULT"
    warning "Could not auto-detect installation directory, using default: $INSTALL_DIR"
    return 1
}

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
    local ubuntu_version=$(lsb_release -cs 2>/dev/null || echo "unknown")
    
    log "Detected system Python: $python_version"
    log "Ubuntu version: $ubuntu_version"
    
    # Clean up any broken PPA configurations first
    if [ -f /etc/apt/sources.list.d/deadsnakes-ubuntu-ppa-*.list ]; then
        log "Checking existing deadsnakes PPA configuration..."
        if ! sudo apt update 2>/dev/null | grep -q "deadsnakes"; then
            warning "Existing deadsnakes PPA seems broken, cleaning up..."
            sudo rm -f /etc/apt/sources.list.d/deadsnakes-ubuntu-ppa-*.list
            sudo apt update
        fi
    fi
    
    # Determine optimal Python version based on Ubuntu version and compatibility
    case "$ubuntu_version" in
        "noble"|"24.04")
            # Ubuntu 24.04: Python 3.12 available, avoid Python 3.13 pandas issues
            if [ "$major_version" = "3" ] && [ "$minor_version" = "13" ]; then
                warning "Python 3.13 detected on Ubuntu 24.04 - pandas compilation issues known"
                log "Installing Python 3.12 for better package compatibility..."
                install_python312
                PYTHON_CMD="python3.12"
            elif [ "$major_version" = "3" ] && ([ "$minor_version" = "11" ] || [ "$minor_version" = "12" ]); then
                log "Python $python_version is optimal for Ubuntu 24.04"
                PYTHON_CMD="python3"
            else
                log "Installing Python 3.12 for optimal compatibility on Ubuntu 24.04..."
                install_python312
                PYTHON_CMD="python3.12"
            fi
            ;;
        "plucky"|"25.04"|"oracular"|"24.10")
            # Ubuntu development versions (25.04+)
            warning "Ubuntu development version detected: $ubuntu_version"
            if [ "$major_version" = "3" ] && [ "$minor_version" = "13" ]; then
                warning "Python 3.13 detected - may have pandas compatibility issues"
                log "Attempting to install Python 3.12 or 3.11 for better compatibility..."
                if install_python312; then
                    PYTHON_CMD="python3.12"
                else
                    warning "Could not install Python 3.12, will try to use Python 3.13 with workarounds"
                    PYTHON_CMD="python3"
                fi
            elif [ "$major_version" = "3" ] && [ "$minor_version" -ge "11" ]; then
                log "Python $python_version should work on development Ubuntu"
                PYTHON_CMD="python3"
            else
                log "Attempting to install newer Python version for better compatibility..."
                if install_python312; then
                    PYTHON_CMD="python3.12"
                else
                    PYTHON_CMD="python3"
                fi
            fi
            ;;
        "jammy"|"22.04")
            # Ubuntu 22.04: Python 3.11 default, 3.12 available via deadsnakes
            if [ "$major_version" = "3" ] && [ "$minor_version" = "13" ]; then
                warning "Python 3.13 detected - installing Python 3.12 for better compatibility"
                install_python312
                PYTHON_CMD="python3.12"
            elif [ "$major_version" = "3" ] && ([ "$minor_version" = "11" ] || [ "$minor_version" = "12" ]); then
                log "Python $python_version is compatible"
                PYTHON_CMD="python3"
            else
                log "Installing Python 3.12 for better package compatibility..."
                install_python312
                PYTHON_CMD="python3.12"
            fi
            ;;
        "focal"|"20.04")
            # Ubuntu 20.04: Python 3.8 default, newer versions via deadsnakes
            if [ "$major_version" = "3" ] && [ "$minor_version" -ge "11" ]; then
                if [ "$minor_version" = "13" ]; then
                    warning "Python 3.13 detected - installing Python 3.12 for better compatibility"
                    install_python312
                    PYTHON_CMD="python3.12"
                else
                    log "Python $python_version is compatible"
                    PYTHON_CMD="python3"
                fi
            else
                log "Installing Python 3.12 for better package compatibility..."
                install_python312
                PYTHON_CMD="python3.12"
            fi
            ;;
        *)
            # Unknown Ubuntu version - use conservative approach
            warning "Unknown Ubuntu version: $ubuntu_version"
            if [ "$major_version" = "3" ] && [ "$minor_version" = "13" ]; then
                warning "Python 3.13 detected - attempting to install Python 3.12 or 3.11 for better compatibility"
                if install_python312; then
                    PYTHON_CMD="python3.12"
                else
                    warning "Could not install alternative Python version, using Python 3.13 with workarounds"
                    PYTHON_CMD="python3"
                fi
            elif [ "$major_version" = "3" ] && [ "$minor_version" -ge "11" ] && [ "$minor_version" -le "12" ]; then
                log "Python $python_version should be compatible"
                PYTHON_CMD="python3"
            else
                log "Attempting to install Python 3.12 for optimal compatibility..."
                if install_python312; then
                    PYTHON_CMD="python3.12"
                else
                    warning "Could not install Python 3.12, using system Python"
                    PYTHON_CMD="python3"
                fi
            fi
            ;;
    esac
    
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
    
    # Detect Ubuntu version
    local ubuntu_version=$(lsb_release -cs 2>/dev/null || echo "unknown")
    log "Detected Ubuntu version: $ubuntu_version"
    
    case "$ubuntu_version" in
        "noble"|"24.04")
            # Ubuntu 24.04 - Python 3.12 available from standard repositories
            log "Installing Python 3.12 from Ubuntu 24.04 standard repositories..."
            sudo apt update
            sudo apt install -y \
                python3.12 \
                python3.12-venv \
                python3.12-dev \
                python3.12-distutils
            ;;
        "plucky"|"25.04"|"oracular"|"24.10")
            # Ubuntu 25.04+ or development versions - try standard repos first
            log "Ubuntu development/newer version detected: $ubuntu_version"
            log "Trying standard repositories first..."
            
            sudo apt update
            if sudo apt install -y python3.12 python3.12-venv python3.12-dev python3.12-distutils; then
                success "Python 3.12 installed from standard repositories"
            else
                warning "Standard repositories don't have Python 3.12"
                log "Trying to use existing Python 3.11 or compiling from source..."
                install_python312_alternative
            fi
            ;;
        "jammy"|"22.04")
            # Ubuntu 22.04 - Need deadsnakes PPA for Python 3.12
            log "Installing Python 3.12 from deadsnakes PPA for Ubuntu 22.04..."
            if ! install_python312_from_deadsnakes; then
                warning "Deadsnakes PPA installation failed, trying alternatives..."
                install_python312_alternative
            fi
            ;;
        "focal"|"20.04")
            # Ubuntu 20.04 - Need deadsnakes PPA for Python 3.12
            log "Installing Python 3.12 from deadsnakes PPA for Ubuntu 20.04..."
            if ! install_python312_from_deadsnakes; then
                warning "Deadsnakes PPA installation failed, trying alternatives..."
                install_python312_alternative
            fi
            ;;
        *)
            # Unknown Ubuntu version - try standard repos first, then alternatives
            warning "Unknown Ubuntu version: $ubuntu_version"
            log "Trying standard repositories first..."
            
            sudo apt update
            if sudo apt install -y python3.12 python3.12-venv python3.12-dev python3.12-distutils; then
                success "Python 3.12 installed from standard repositories"
            elif install_python312_from_deadsnakes; then
                success "Python 3.12 installed from deadsnakes PPA"
            else
                log "Both standard repos and deadsnakes PPA failed, trying alternatives..."
                install_python312_alternative
            fi
            ;;
    esac
    
    # Verify installation
    if python3.12 --version &> /dev/null; then
        success "Python 3.12 installed successfully"
    else
        error "Python 3.12 installation failed"
        return 1
    fi
}

# Alternative Python 3.12 installation methods
install_python312_alternative() {
    log "Trying alternative Python 3.12 installation methods..."
    
    # Method 1: Check if Python 3.11 is available and use it instead
    if command -v python3.11 &> /dev/null; then
        warning "Python 3.12 not available, using Python 3.11 instead"
        PYTHON_CMD="python3.11"
        return 0
    fi
    
    # Method 2: Try to install Python 3.11 if available
    if sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils; then
        success "Python 3.11 installed as alternative to Python 3.12"
        PYTHON_CMD="python3.11"
        return 0
    fi
    
    # Method 3: Use system Python 3 if it's reasonably recent
    local system_python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2 || echo "0.0.0")
    local major_version=$(echo $system_python_version | cut -d'.' -f1)
    local minor_version=$(echo $system_python_version | cut -d'.' -f2)
    
    if [ "$major_version" = "3" ] && [ "$minor_version" -ge "10" ]; then
        warning "Using system Python $system_python_version (may have some package compatibility issues)"
        PYTHON_CMD="python3"
        return 0
    fi
    
    # Method 4: Install from source (last resort)
    warning "All package installation methods failed"
    log "Would you like to compile Python 3.12 from source? This will take 10-20 minutes."
    log "Skipping source compilation for automated installation..."
    log "You can manually install Python 3.12 and re-run this script"
    
    return 1
}

# Install Python 3.12 from deadsnakes PPA (for older Ubuntu versions)
install_python312_from_deadsnakes() {
    log "Installing Python 3.12 from deadsnakes PPA..."
    
    # Install software-properties-common if not available
    if ! command -v add-apt-repository &> /dev/null; then
        log "Installing software-properties-common..."
        sudo apt install -y software-properties-common
    fi
    
    # Add deadsnakes PPA for newer Python versions
    log "Adding deadsnakes PPA..."
    if sudo add-apt-repository ppa:deadsnakes/ppa -y; then
        log "Successfully added deadsnakes PPA"
    else
        error "Failed to add deadsnakes PPA"
        return 1
    fi
    
    # Update package list and check if it works
    if sudo apt update 2>/dev/null; then
        log "Package list updated successfully"
    else
        warning "Package update failed - PPA may not support this Ubuntu version"
        return 1
    fi
    
    # Check if Python 3.12 is available from the PPA
    if apt-cache show python3.12 &>/dev/null; then
        log "Python 3.12 available from deadsnakes PPA"
    else
        warning "Python 3.12 not available from deadsnakes PPA for this Ubuntu version"
        return 1
    fi
    
    # Install Python 3.12 and related packages
    log "Installing Python 3.12 packages from deadsnakes..."
    sudo apt install -y \
        python3.12 \
        python3.12-venv \
        python3.12-dev \
        python3.12-distutils
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
        "software-properties-common"
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
    log "Setting up Python environment with $PYTHON_CMD..."
    
    cd "$INSTALL_DIR/backend"
    
    # Ensure we have the right Python version and venv module
    if ! $PYTHON_CMD -m venv --help &> /dev/null; then
        error "venv module not available for $PYTHON_CMD"
        return 1
    fi
    
    # Remove existing venv if it exists but is broken or uses wrong Python version
    if [ -d "venv" ]; then
        local existing_python=""
        if [ -f "venv/bin/python" ]; then
            existing_python=$(venv/bin/python --version 2>/dev/null | cut -d' ' -f2 || echo "unknown")
        fi
        
        local target_python=$($PYTHON_CMD --version | cut -d' ' -f2)
        
        if [ "$existing_python" != "$target_python" ] || [ ! -f "venv/bin/python3" ]; then
            log "Removing existing virtual environment (Python version mismatch or broken)"
            rm -rf venv
        fi
    fi
    
    # Create virtual environment with the selected Python version
    if [ ! -d "venv" ]; then
        log "Creating Python virtual environment with $PYTHON_CMD..."
        
        if $PYTHON_CMD -m venv venv; then
            success "Virtual environment created successfully"
        else
            error "Failed to create virtual environment with $PYTHON_CMD"
            return 1
        fi
        
        # Verify virtual environment was created successfully
        if [ ! -f "venv/bin/python3" ]; then
            error "Virtual environment creation appeared to succeed but python3 binary is missing"
            return 1
        fi
    else
        log "Virtual environment already exists and is compatible"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Verify activation worked
    if [ "$VIRTUAL_ENV" = "" ]; then
        error "Failed to activate virtual environment"
        return 1
    fi
    
    local venv_python_version=$(python --version | cut -d' ' -f2)
    log "Virtual environment activated with Python $venv_python_version"
    
    # Upgrade pip and build tools
    log "Upgrading pip and build tools..."
    python -m pip install --upgrade pip setuptools wheel
    
    # Install Python dependencies with optimized settings
    log "Installing Python dependencies..."
    if [ -f "requirements.txt" ]; then
        # Install with prefer-binary to avoid compilation issues and handle conflicts
        log "Installing core dependencies first..."
        
        # Install essential packages first to avoid conflicts
        pip install --prefer-binary --no-cache-dir \
            fastapi==0.110.0 \
            uvicorn[standard]==0.27.0 \
            websockets==12.0 \
            python-multipart==0.0.7 \
            aiofiles==23.2.1 \
            cryptography==42.0.0 \
            base58==2.1.1 \
            pymongo==4.6.1 \
            psutil==5.9.8 \
            requests==2.31.0 \
            python-dotenv==1.0.0 \
            pydantic==2.6.0
        
        # Try to install remaining packages, skipping problematic ones
        log "Installing additional dependencies..."
        
        # Skip problematic metadata package and install others individually
        local remaining_packages=(
            "pytest==8.0.0"
        )
        
        for package in "${remaining_packages[@]}"; do
            if pip install --prefer-binary --no-cache-dir "$package"; then
                log "✅ Installed $package"
            else
                warning "❌ Failed to install $package (skipping)"
            fi
        done
        
        # Try AI packages with fallbacks
        log "Installing AI/ML packages with fallbacks..."
        
        # Try NumPy first (required by most ML packages)
        if pip install --prefer-binary --no-cache-dir "numpy>=1.24.0,<2.0.0"; then
            success "NumPy installed successfully"
            
            # Try scikit-learn
            if pip install --prefer-binary --no-cache-dir "scikit-learn>=1.3.0,<2.0.0"; then
                success "Scikit-learn installed successfully"
            else
                warning "Scikit-learn installation failed"
            fi
            
            # Try pandas (most problematic with Python 3.13)
            if pip install --prefer-binary --no-cache-dir "pandas>=2.1.0,<3.0.0"; then
                success "Pandas installed successfully"
            else
                warning "Pandas installation failed - AI features will be limited"
                log "Attempting to install pandas with no-deps to avoid conflicts..."
                if pip install --prefer-binary --no-deps --no-cache-dir pandas; then
                    success "Pandas installed with --no-deps"
                else
                    warning "Pandas completely failed - core mining will still work"
                fi
            fi
        else
            warning "NumPy installation failed - installing alternative math libraries"
            # Continue without NumPy/pandas - core functionality will still work
        fi
        
        # Try scrypt package for mining
        log "Installing mining-specific packages..."
        if pip install --prefer-binary --no-cache-dir scrypt==0.8.20; then
            success "Scrypt library installed successfully"
        else
            warning "Scrypt library failed, installing alternative crypto library"
            pip install --prefer-binary --no-cache-dir pycryptodome
        fi
        
        # Verify critical packages are installed
        if ! python -c "import fastapi, pymongo, uvicorn" 2>/dev/null; then
            error "Critical packages failed to install"
            return 1
        fi
        
        success "Core packages installed successfully"
        
        # Check what AI packages are available
        local ai_status=""
        if python -c "import pandas, numpy, sklearn" 2>/dev/null; then
            ai_status="All AI libraries available"
        elif python -c "import numpy, sklearn" 2>/dev/null; then
            ai_status="NumPy and scikit-learn available (pandas missing)"
        elif python -c "import numpy" 2>/dev/null; then
            ai_status="Only NumPy available (limited AI features)"
        else
            ai_status="No AI libraries available (core mining only)"
        fi
        
        log "AI Package Status: $ai_status"
        
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
    check_and_install_python  # New function for Python version management
    install_dependencies
    install_mongodb
    setup_directories
    setup_python_environment
    setup_frontend_environment
    setup_services
    start_services
    
    success "🎉 CryptoMiner Pro installation completed successfully!"
    log ""
    log "Python version used: $($PYTHON_CMD --version)"
    log "Installation directory: $INSTALL_DIR"
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
    log "Troubleshooting:"
    log "  Backend logs:  tail -f /var/log/supervisor/backend.out.log"
    log "  Frontend logs: tail -f /var/log/supervisor/frontend.out.log"
}

# Run main function
main "$@"