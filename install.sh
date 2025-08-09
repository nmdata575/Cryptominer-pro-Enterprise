#!/bin/bash

# CryptoMiner Pro - Unified Installation Script
# Consolidates all installation functionality into a single robust installer

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

# Logging function
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

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root. Please run as a regular user with sudo privileges."
        exit 1
    fi
    
    if ! sudo -n true 2>/dev/null; then
        error "This script requires sudo privileges. Please run with sudo or configure passwordless sudo."
        exit 1
    fi
}

# Detect system information
detect_system() {
    log "Detecting system information..."
    
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS_NAME="$NAME"
        OS_VERSION="$VERSION_ID"
        log "Detected: $OS_NAME $OS_VERSION"
    else
        error "Cannot detect operating system"
        exit 1
    fi
    
    # Check Ubuntu version
    if [[ "$ID" != "ubuntu" ]]; then
        warning "This installer is optimized for Ubuntu. Other distributions may work but are not tested."
    fi
    
    if [[ "${VERSION_ID%%.*}" -lt 20 ]]; then
        error "Ubuntu 20.04 or later is required"
        exit 1
    fi
}

# Install system dependencies
install_system_dependencies() {
    log "Installing system dependencies..."
    
    sudo apt update
    
    # Essential packages
    local packages=(
        curl
        wget
        git
        build-essential
        software-properties-common
        apt-transport-https
        ca-certificates
        gnupg
        lsb-release
        supervisor
        nginx
    )
    
    sudo apt install -y "${packages[@]}"
    success "System dependencies installed"
}

# Install Python
install_python() {
    log "Installing Python ${PYTHON_VERSION}..."
    
    # Add deadsnakes PPA for latest Python versions
    if ! apt-cache policy | grep -q deadsnakes; then
        sudo add-apt-repository -y ppa:deadsnakes/ppa
        sudo apt update
    fi
    
    # Install Python and related packages
    local python_packages=(
        "python${PYTHON_VERSION}"
        "python${PYTHON_VERSION}-venv"
        "python${PYTHON_VERSION}-dev"
        "python${PYTHON_VERSION}-distutils"
        python3-pip
        python3-setuptools
        python3-wheel
    )
    
    sudo apt install -y "${python_packages[@]}"
    
    # Verify Python installation
    if ! command -v "python${PYTHON_VERSION}" &> /dev/null; then
        error "Python ${PYTHON_VERSION} installation failed"
        exit 1
    fi
    
    success "Python ${PYTHON_VERSION} installed successfully"
}

# Install Node.js and Yarn
install_nodejs() {
    log "Installing Node.js ${NODE_VERSION}..."
    
    # Install Node.js via NodeSource repository
    curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | sudo -E bash -
    sudo apt install -y nodejs
    
    # Install Yarn
    curl -fsSL https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
    sudo apt update
    sudo apt install -y yarn
    
    # Verify installations
    if ! command -v node &> /dev/null || ! command -v yarn &> /dev/null; then
        error "Node.js or Yarn installation failed"
        exit 1
    fi
    
    success "Node.js $(node --version) and Yarn $(yarn --version) installed"
}

# Install MongoDB
install_mongodb() {
    log "Installing MongoDB..."
    
    # Import MongoDB GPG key
    curl -fsSL https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
    
    # Add MongoDB repository
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
    
    sudo apt update
    sudo apt install -y mongodb-org
    
    # Start and enable MongoDB
    sudo systemctl start mongod
    sudo systemctl enable mongod
    
    success "MongoDB installed and started"
}

# Create application directories
create_directories() {
    log "Creating application directories..."
    
    sudo mkdir -p "$INSTALL_DIR"
    sudo mkdir -p /var/log/cryptominer-pro
    sudo mkdir -p /etc/cryptominer-pro
    
    # Set ownership
    sudo chown -R "$USER:$USER" "$INSTALL_DIR"
    sudo chown -R "$USER:$USER" /var/log/cryptominer-pro
    
    success "Directories created"
}

# Copy application files
copy_application_files() {
    log "Copying application files..."
    
    # Copy backend files
    cp -r backend/ "$INSTALL_DIR/"
    cp -r frontend/ "$INSTALL_DIR/"
    
    # Copy configuration files
    cp start.sh "$INSTALL_DIR/"
    cp README.md "$INSTALL_DIR/"
    
    # Make scripts executable
    chmod +x "$INSTALL_DIR/start.sh"
    
    success "Application files copied"
}

# Setup Python virtual environment
setup_python_environment() {
    log "Setting up Python virtual environment..."
    
    cd "$INSTALL_DIR/backend"
    
    # Create virtual environment with specific Python version
    "python${PYTHON_VERSION}" -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip and install build tools
    pip install --upgrade pip setuptools wheel
    
    # Install Python dependencies with multiple fallback strategies
    install_python_dependencies
    
    success "Python environment setup complete"
}

# Install Python dependencies with fallback
install_python_dependencies() {
    local attempt=1
    local max_attempts=3
    
    while [[ $attempt -le $max_attempts ]]; do
        log "Installing Python dependencies (attempt $attempt/$max_attempts)..."
        
        case $attempt in
            1)
                # First attempt: standard requirements
                if pip install -r requirements.txt --prefer-binary --no-cache-dir; then
                    success "Python dependencies installed successfully"
                    return 0
                fi
                ;;
            2)
                # Second attempt: fallback requirements if they exist
                if [[ -f requirements-fallback.txt ]]; then
                    warning "Using fallback requirements..."
                    if pip install -r requirements-fallback.txt --prefer-binary --no-cache-dir; then
                        success "Python dependencies installed with fallback versions"
                        return 0
                    fi
                fi
                ;;
            3)
                # Third attempt: minimal requirements
                warning "Installing minimal requirements..."
                local minimal_packages=(
                    "fastapi>=0.100.0"
                    "uvicorn[standard]>=0.20.0"
                    "websockets>=11.0.0"
                    "pymongo>=4.0.0"
                    "psutil>=5.9.0"
                    "requests>=2.28.0"
                    "python-dotenv>=1.0.0"
                    "pydantic>=2.0.0"
                    "numpy>=1.24.0"
                    "scikit-learn>=1.3.0"
                    "cryptography>=40.0.0"
                )
                
                for package in "${minimal_packages[@]}"; do
                    pip install "$package" --prefer-binary --no-cache-dir || true
                done
                
                success "Minimal Python environment installed"
                return 0
                ;;
        esac
        
        ((attempt++))
        warning "Attempt $((attempt-1)) failed, trying alternative approach..."
        sleep 2
    done
    
    error "Failed to install Python dependencies after $max_attempts attempts"
    exit 1
}

# Setup Node.js environment
setup_nodejs_environment() {
    log "Setting up Node.js environment..."
    
    cd "$INSTALL_DIR/frontend"
    
    # Install dependencies with retry logic
    local attempt=1
    local max_attempts=3
    
    while [[ $attempt -le $max_attempts ]]; do
        log "Installing Node.js dependencies (attempt $attempt/$max_attempts)..."
        
        if yarn install --frozen-lockfile --network-timeout 60000; then
            success "Node.js dependencies installed successfully"
            break
        elif [[ $attempt -eq $max_attempts ]]; then
            error "Failed to install Node.js dependencies after $max_attempts attempts"
            exit 1
        else
            warning "Attempt $attempt failed, retrying..."
            ((attempt++))
            # Clean cache and retry
            yarn cache clean
            sleep 2
        fi
    done
}

# Configure environment files
configure_environment() {
    log "Configuring environment files..."
    
    # Backend environment
    if [[ ! -f "$INSTALL_DIR/backend/.env" ]]; then
        cat > "$INSTALL_DIR/backend/.env" << EOF
MONGO_URL=mongodb://localhost:27017/cryptominer_pro
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=false
LOG_LEVEL=info
EOF
    fi
    
    # Frontend environment
    if [[ ! -f "$INSTALL_DIR/frontend/.env" ]]; then
        cat > "$INSTALL_DIR/frontend/.env" << EOF
REACT_APP_BACKEND_URL=http://localhost:8001
REACT_APP_VERSION=2.0.0
GENERATE_SOURCEMAP=false
EOF
    fi
    
    success "Environment files configured"
}

# Setup Supervisor configuration
setup_supervisor() {
    log "Setting up Supervisor configuration..."
    
    # Create supervisor configuration
    cat > /tmp/cryptominer-pro.conf << EOF
[program:cryptominer_backend]
command=$INSTALL_DIR/backend/venv/bin/python -m uvicorn server:app --host 0.0.0.0 --port 8001
directory=$INSTALL_DIR/backend
autostart=true
autorestart=true
stderr_logfile=/var/log/cryptominer-pro/backend.err.log
stdout_logfile=/var/log/cryptominer-pro/backend.out.log
user=$USER
environment=PATH="$INSTALL_DIR/backend/venv/bin"

[program:cryptominer_frontend]
command=/usr/bin/yarn start
directory=$INSTALL_DIR/frontend
autostart=true
autorestart=true
stderr_logfile=/var/log/cryptominer-pro/frontend.err.log
stdout_logfile=/var/log/cryptominer-pro/frontend.out.log
user=$USER
environment=PORT=3333,PATH="/usr/bin:/bin:/usr/local/bin"

[group:cryptominer_pro]
programs=cryptominer_backend,cryptominer_frontend
priority=999
EOF
    
    sudo mv /tmp/cryptominer-pro.conf /etc/supervisor/conf.d/
    sudo supervisorctl reread
    sudo supervisorctl update
    
    success "Supervisor configuration setup complete"
}

# Setup Nginx reverse proxy
setup_nginx() {
    log "Setting up Nginx reverse proxy..."
    
    cat > /tmp/cryptominer-pro << EOF
server {
    listen 80;
    server_name localhost;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8001/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
    
    # WebSocket
    location /ws {
        proxy_pass http://localhost:8001/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
    
    sudo mv /tmp/cryptominer-pro /etc/nginx/sites-available/
    sudo ln -sf /etc/nginx/sites-available/cryptominer-pro /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload Nginx
    sudo nginx -t && sudo systemctl reload nginx
    
    success "Nginx reverse proxy configured"
}

# Start services
start_services() {
    log "Starting CryptoMiner Pro services..."
    
    # Start MongoDB
    sudo systemctl start mongod
    
    # Start Supervisor services
    sudo supervisorctl start cryptominer-pro:*
    
    # Start Nginx
    sudo systemctl start nginx
    
    # Enable services to start on boot
    sudo systemctl enable mongod nginx supervisor
    
    success "All services started successfully"
}

# Verify installation
verify_installation() {
    log "Verifying installation..."
    
    local errors=0
    
    # Check services
    if ! sudo systemctl is-active --quiet mongod; then
        error "MongoDB service is not running"
        ((errors++))
    fi
    
    if ! sudo supervisorctl status cryptominer-pro:backend | grep -q RUNNING; then
        error "Backend service is not running"
        ((errors++))
    fi
    
    if ! sudo supervisorctl status cryptominer-pro:frontend | grep -q RUNNING; then
        error "Frontend service is not running"
        ((errors++))
    fi
    
    if ! sudo systemctl is-active --quiet nginx; then
        error "Nginx service is not running"
        ((errors++))
    fi
    
    # Test API endpoints
    sleep 5  # Give services time to start
    
    if ! curl -s http://localhost:8001/api/health > /dev/null; then
        error "Backend API is not responding"
        ((errors++))
    fi
    
    if [[ $errors -eq 0 ]]; then
        success "Installation verification completed successfully"
        return 0
    else
        error "Installation verification found $errors errors"
        return 1
    fi
}

# Cleanup function
cleanup() {
    log "Performing cleanup..."
    
    # Clean package caches
    sudo apt autoremove -y
    sudo apt autoclean
    
    # Clean pip cache
    if [[ -d "$HOME/.cache/pip" ]]; then
        rm -rf "$HOME/.cache/pip"
    fi
    
    # Clean yarn cache
    yarn cache clean 2>/dev/null || true
    
    success "Cleanup completed"
}

# Show installation summary
show_summary() {
    echo
    echo "======================================"
    echo "🚀 CryptoMiner Pro Installation Complete!"
    echo "======================================"
    echo
    echo "📋 Installation Summary:"
    echo "  • Install Directory: $INSTALL_DIR"
    echo "  • Python Version: $(python${PYTHON_VERSION} --version 2>/dev/null || echo 'Unknown')"
    echo "  • Node.js Version: $(node --version 2>/dev/null || echo 'Unknown')"
    echo "  • Yarn Version: $(yarn --version 2>/dev/null || echo 'Unknown')"
    echo
    echo "🌐 Access URLs:"
    echo "  • Web Interface: http://localhost"
    echo "  • Backend API: http://localhost:8001/api"
    echo "  • Health Check: http://localhost:8001/api/health"
    echo
    echo "🛠️ Service Management:"
    echo "  • Start All: sudo supervisorctl start cryptominer-pro:*"
    echo "  • Stop All: sudo supervisorctl stop cryptominer-pro:*"
    echo "  • Restart All: sudo supervisorctl restart cryptominer-pro:*"
    echo "  • Status: sudo supervisorctl status"
    echo
    echo "📂 Important Directories:"
    echo "  • Application: $INSTALL_DIR"
    echo "  • Logs: /var/log/cryptominer-pro/"
    echo "  • Configuration: /etc/supervisor/conf.d/cryptominer-pro.conf"
    echo
    echo "🔧 Troubleshooting:"
    echo "  • Backend Logs: sudo tail -f /var/log/cryptominer-pro/backend.log"
    echo "  • Frontend Logs: sudo tail -f /var/log/cryptominer-pro/frontend.log"
    echo "  • MongoDB Status: sudo systemctl status mongod"
    echo
    echo "✅ Installation completed successfully!"
    echo "   Navigate to http://localhost to start mining!"
    echo
}

# Main installation function
main() {
    echo "======================================"
    echo "🚀 CryptoMiner Pro - Unified Installer"
    echo "======================================"
    echo
    
    check_root
    detect_system
    
    log "Starting installation process..."
    
    # Installation steps
    install_system_dependencies
    install_python
    install_nodejs
    install_mongodb
    create_directories
    copy_application_files
    setup_python_environment
    setup_nodejs_environment
    configure_environment
    setup_supervisor
    setup_nginx
    start_services
    
    # Verification and cleanup
    if verify_installation; then
        cleanup
        show_summary
    else
        error "Installation completed with errors. Check the logs for details."
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "CryptoMiner Pro Unified Installer"
        echo
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --clean        Clean install (removes existing installation)"
        echo
        exit 0
        ;;
    --clean)
        warning "Performing clean installation..."
        sudo rm -rf "$INSTALL_DIR" 2>/dev/null || true
        sudo rm -f /etc/supervisor/conf.d/cryptominer-pro.conf 2>/dev/null || true
        sudo rm -f /etc/nginx/sites-available/cryptominer-pro 2>/dev/null || true
        sudo rm -f /etc/nginx/sites-enabled/cryptominer-pro 2>/dev/null || true
        sudo supervisorctl reread 2>/dev/null || true
        sudo supervisorctl update 2>/dev/null || true
        log "Clean installation mode enabled"
        ;;
esac

# Run main installation
main "$@"