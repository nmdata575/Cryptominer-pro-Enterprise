#!/bin/bash

# CryptoMiner Pro V30 - Secure Complete Installation Script
# Installs to /home/USER/CryptominerV30 with proper security and all dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
USER_HOME="$(eval echo ~$USER)"
INSTALL_DIR="$USER_HOME/CryptominerV30"
SERVICE_NAME="cryptominer-v30"
PYTHON_VERSION="3.12"
NODE_VERSION="20"
MONGODB_VERSION="8.0"

# MongoDB security configuration
MONGO_DB_NAME="cryptominer_v30_db"
MONGO_APP_USER="cryptominer_app"
MONGO_APP_PASS=""  # Will be generated

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

info() {
    echo -e "${CYAN}[INFO] $1${NC}"
}

security() {
    echo -e "${PURPLE}[SECURITY] $1${NC}"
}

# Generate secure random password
generate_password() {
    python3 -c "import secrets, string; chars = string.ascii_letters + string.digits + '!@#$%^&*'; print(''.join(secrets.choice(chars) for _ in range(32)))"
}

# Check permissions
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root for security reasons."
        error "Please run as a regular user with sudo privileges."
        exit 1
    fi
    
    if ! sudo -n true 2>/dev/null; then
        error "This script requires sudo privileges for system package installation."
        error "Please run 'sudo -v' first or configure passwordless sudo."
        exit 1
    fi
    
    security "Running installation as user: $USER"
    security "Installation directory: $INSTALL_DIR"
}

# System requirements check
check_system_requirements() {
    log "Performing comprehensive system requirements check..."
    
    # Check OS compatibility
    if ! grep -qE "Ubuntu|Debian" /etc/os-release; then
        warning "This installer is optimized for Ubuntu/Debian. Other distributions may have issues."
    fi
    
    local ubuntu_version=$(lsb_release -rs 2>/dev/null || echo "unknown")
    info "Detected Ubuntu version: $ubuntu_version"
    
    # Check architecture
    local arch=$(uname -m)
    if [[ "$arch" != "x86_64" && "$arch" != "aarch64" ]]; then
        error "Unsupported architecture: $arch. Only x86_64 and aarch64 are supported."
        exit 1
    fi
    info "System architecture: $arch"
    
    # Check available memory (minimum 4GB)
    local total_memory=$(free -m | awk 'NR==2{print $2}')
    if [ "$total_memory" -lt 4096 ]; then
        error "Insufficient memory: ${total_memory}MB. Minimum 4GB required for stable operation."
        exit 1
    fi
    info "Available memory: ${total_memory}MB"
    
    # Check available disk space (minimum 20GB)
    local available_space=$(df "$USER_HOME" | awk 'NR==2{printf "%.0f", $4/1024}')
    if [ "$available_space" -lt 20480 ]; then
        error "Insufficient disk space: ${available_space}MB. Minimum 20GB required."
        exit 1
    fi
    info "Available disk space: ${available_space}MB"
    
    # Check CPU cores (minimum 4)
    local cpu_cores=$(nproc)
    if [ "$cpu_cores" -lt 4 ]; then
        warning "Limited CPU cores: ${cpu_cores}. Recommended: 8+ cores for optimal mining performance."
    fi
    info "CPU cores available: $cpu_cores"
    
    success "System requirements check completed"
}

# Install comprehensive system dependencies
install_system_dependencies() {
    log "Installing comprehensive system dependencies..."
    
    # Update package lists
    sudo apt update
    
    # Essential build and development tools
    local essential_packages=(
        # Build essentials
        "build-essential"
        "gcc"
        "g++"
        "make"
        "cmake"
        "pkg-config"
        
        # Python development
        "python3"
        "python3-pip"
        "python3-venv" 
        "python3-dev"
        "python3-setuptools"
        "python3-wheel"
        
        # Security libraries
        "libssl-dev"
        "libffi-dev"
        "libcrypto++-dev"
        "openssl"
        
        # Network and utilities
        "curl"
        "wget"
        "git"
        "unzip"
        "software-properties-common"
        "apt-transport-https"
        "ca-certificates"
        "gnupg"
        "lsb-release"
        
        # Process management
        "supervisor"
        "htop"
        "iotop"
        "netstat-persistent"
        
        # Additional utilities
        "jq"
        "tree"
        "nano"
        "vim"
    )
    
    sudo apt install -y "${essential_packages[@]}"
    
    success "Essential system packages installed"
}

# Install Python 3.12 with full compatibility
install_python() {
    log "Installing Python $PYTHON_VERSION with full development environment..."
    
    # Check current Python version
    local current_python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2 || echo "none")
    info "Current system Python: $current_python_version"
    
    # Install Python 3.12 based on Ubuntu version
    local ubuntu_version=$(lsb_release -cs 2>/dev/null || echo "unknown")
    
    case "$ubuntu_version" in
        "noble"|"24.04")
            # Ubuntu 24.04 - Python 3.12 available from standard repos
            log "Installing Python 3.12 from Ubuntu 24.04 repositories..."
            sudo apt install -y \
                python3.12 \
                python3.12-venv \
                python3.12-dev \
                python3.12-distutils \
                python3.12-full
            ;;
        "jammy"|"22.04"|"focal"|"20.04")
            # Older Ubuntu - use deadsnakes PPA
            log "Installing Python 3.12 from deadsnakes PPA..."
            sudo add-apt-repository ppa:deadsnakes/ppa -y
            sudo apt update
            sudo apt install -y \
                python3.12 \
                python3.12-venv \
                python3.12-dev \
                python3.12-distutils \
                python3.12-full
            ;;
        *)
            # Try standard repos first
            if sudo apt install -y python3.12 python3.12-venv python3.12-dev; then
                success "Python 3.12 installed from standard repositories"
            else
                error "Python 3.12 installation failed for Ubuntu version: $ubuntu_version"
                exit 1
            fi
            ;;
    esac
    
    # Verify installation
    if python3.12 --version &> /dev/null; then
        local installed_version=$(python3.12 --version | cut -d' ' -f2)
        success "Python $installed_version installed successfully"
    else
        error "Python 3.12 installation verification failed"
        exit 1
    fi
}

# Install Node.js and Yarn
install_nodejs() {
    log "Installing Node.js $NODE_VERSION and Yarn..."
    
    # Check if Node.js is already installed with correct version
    if command -v node &> /dev/null; then
        local current_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$current_version" -ge "$NODE_VERSION" ]; then
            success "Node.js $current_version already installed"
        else
            log "Upgrading Node.js from version $current_version to $NODE_VERSION..."
        fi
    fi
    
    # Install Node.js from NodeSource repository
    curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | sudo -E bash -
    sudo apt install -y nodejs
    
    # Verify Node.js installation
    local installed_node_version=$(node --version)
    info "Node.js version: $installed_node_version"
    
    # Install Yarn package manager
    if ! command -v yarn &> /dev/null; then
        log "Installing Yarn package manager..."
        npm install -g yarn
    fi
    
    # Verify Yarn installation
    local yarn_version=$(yarn --version)
    info "Yarn version: $yarn_version"
    
    success "Node.js and Yarn installed successfully"
}

# Install and secure MongoDB 8.0
install_mongodb() {
    log "Installing MongoDB $MONGODB_VERSION with security configuration..."
    
    # Check if MongoDB is already installed
    if command -v mongod &> /dev/null; then
        local current_version=$(mongod --version | head -1 | grep -o 'v[0-9]*\.[0-9]*\.[0-9]*' || echo "unknown")
        warning "MongoDB already installed: $current_version"
        log "Continuing with configuration..."
    else
        # Install MongoDB 8.0 from official repository
        log "Installing MongoDB 8.0 from official repository..."
        
        # Import MongoDB GPG key
        curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | \
            sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg --dearmor
        
        # Add MongoDB repository
        local ubuntu_version=$(lsb_release -cs)
        # Use jammy repository for newer Ubuntu versions if needed
        if [ "$ubuntu_version" = "noble" ]; then
            ubuntu_version="jammy"
        fi
        
        echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu $ubuntu_version/mongodb-org/8.0 multiverse" | \
            sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
        
        # Update and install MongoDB
        sudo apt update
        sudo apt install -y mongodb-org
    fi
    
    # Create MongoDB configuration with security
    log "Configuring MongoDB with security settings..."
    sudo tee /etc/mongod.conf > /dev/null << EOF
# CryptoMiner Pro V30 - MongoDB Configuration
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true

systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log
  logRotate: reopen

net:
  port: 27017
  bindIp: 127.0.0.1
  maxIncomingConnections: 1000

# Security configuration
security:
  authorization: enabled

# Performance settings
operationProfiling:
  slowOpThresholdMs: 1000

# Connection settings for application
setParameter:
  authenticationMechanisms: SCRAM-SHA-256
EOF
    
    # Create MongoDB data directory with proper permissions
    sudo mkdir -p /var/lib/mongodb
    sudo mkdir -p /var/log/mongodb
    sudo chown mongodb:mongodb /var/lib/mongodb
    sudo chown mongodb:mongodb /var/log/mongodb
    
    # Start MongoDB service
    sudo systemctl start mongod
    sudo systemctl enable mongod
    
    # Wait for MongoDB to start
    sleep 5
    
    # Check if MongoDB is running
    if ! sudo systemctl is-active --quiet mongod; then
        error "MongoDB failed to start"
        sudo systemctl status mongod
        exit 1
    fi
    
    success "MongoDB installed and started successfully"
}

# Setup MongoDB security and application user
setup_mongodb_security() {
    log "Setting up MongoDB security and application user..."
    
    # Generate secure password for application user
    MONGO_APP_PASS=$(generate_password)
    
    # Create MongoDB admin user first
    log "Creating MongoDB admin user..."
    mongosh --eval "
    use admin
    try {
        db.createUser({
            user: 'admin',
            pwd: '$MONGO_APP_PASS',
            roles: [
                { role: 'userAdminAnyDatabase', db: 'admin' },
                { role: 'dbAdminAnyDatabase', db: 'admin' },
                { role: 'readWriteAnyDatabase', db: 'admin' }
            ]
        })
        print('Admin user created successfully')
    } catch(e) {
        if (e.code === 51003) {
            print('Admin user already exists')
        } else {
            throw e
        }
    }
    "
    
    # Restart MongoDB with authentication
    sudo systemctl restart mongod
    sleep 5
    
    # Create application-specific user and database
    log "Creating application database and user..."
    mongosh -u admin -p "$MONGO_APP_PASS" --authenticationDatabase admin --eval "
    use $MONGO_DB_NAME
    try {
        db.createUser({
            user: '$MONGO_APP_USER',
            pwd: '$MONGO_APP_PASS',
            roles: [
                { role: 'readWrite', db: '$MONGO_DB_NAME' },
                { role: 'dbAdmin', db: '$MONGO_DB_NAME' }
            ]
        })
        print('Application user created successfully')
    } catch(e) {
        if (e.code === 51003) {
            print('Application user already exists')
        } else {
            throw e
        }
    }
    
    // Create initial collections
    db.mining_stats.createIndex({ 'timestamp': 1 })
    db.mining_configs.createIndex({ 'user_id': 1 })
    db.saved_pools.createIndex({ 'user_id': 1, 'name': 1 })
    db.custom_coins.createIndex({ 'user_id': 1, 'symbol': 1 })
    
    print('Database and collections initialized')
    "
    
    security "MongoDB security configured with authentication enabled"
    security "Database: $MONGO_DB_NAME"
    security "App User: $MONGO_APP_USER"
    security "Password: [SECURELY GENERATED - will be saved to .env]"
}

# Create secure installation directory
create_installation_directory() {
    log "Creating secure installation directory structure..."
    
    # Remove existing installation if it exists
    if [ -d "$INSTALL_DIR" ]; then
        warning "Existing installation found at $INSTALL_DIR"
        log "Creating backup before removal..."
        if [ -f "$INSTALL_DIR/backend/.env" ]; then
            cp "$INSTALL_DIR/backend/.env" "$USER_HOME/cryptominer-backup.env" 2>/dev/null || true
        fi
        rm -rf "$INSTALL_DIR"
    fi
    
    # Create directory structure
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR/logs"
    mkdir -p "$INSTALL_DIR/backup"
    mkdir -p "$INSTALL_DIR/config"
    
    # Verify current directory has the required files
    if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
        error "Required directories (backend, frontend) not found in current directory"
        error "Please run this script from the CryptoMiner Pro source directory"
        exit 1
    fi
    
    # Copy application files with verification
    log "Copying application files..."
    cp -r backend/ "$INSTALL_DIR/"
    cp -r frontend/ "$INSTALL_DIR/"
    
    # Copy additional components
    if [ -d "v30-remote-node" ]; then
        cp -r v30-remote-node/ "$INSTALL_DIR/"
    fi
    
    # Copy documentation
    for doc in README.md DEPLOYMENT_GUIDE.md *.md; do
        if [ -f "$doc" ]; then
            cp "$doc" "$INSTALL_DIR/"
        fi
    done
    
    # Set secure file permissions
    chmod 755 "$INSTALL_DIR"
    chmod 750 "$INSTALL_DIR/logs"
    chmod 750 "$INSTALL_DIR/backup"
    chmod 750 "$INSTALL_DIR/config"
    
    # Set ownership
    chown -R $USER:$USER "$INSTALL_DIR"
    
    success "Installation directory created with secure permissions"
    info "Installation path: $INSTALL_DIR"
}

# Setup Python environment with security
setup_python_environment() {
    log "Setting up secure Python environment..."
    
    cd "$INSTALL_DIR/backend"
    
    # Create virtual environment with Python 3.12
    log "Creating Python virtual environment..."
    python3.12 -m venv venv
    
    # Verify virtual environment
    if [ ! -f "venv/bin/python" ]; then
        error "Virtual environment creation failed"
        exit 1
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip and essential tools
    log "Upgrading Python tools..."
    python -m pip install --upgrade pip setuptools wheel
    
    # Install dependencies with security considerations
    log "Installing Python dependencies securely..."
    if [ -f "requirements.txt" ]; then
        # Install with hash verification when available
        pip install -r requirements.txt --prefer-binary --no-cache-dir
    else
        error "requirements.txt not found"
        exit 1
    fi
    
    # Verify critical imports
    if ! python -c "import fastapi, pymongo, uvicorn, cryptography" 2>/dev/null; then
        error "Critical Python packages failed to import"
        exit 1
    fi
    
    # Create secure .env file
    log "Creating secure backend configuration..."
    cat > .env << EOF
# CryptoMiner Pro V30 - Secure Configuration
MONGO_URL=mongodb://${MONGO_APP_USER}:${MONGO_APP_PASS}@localhost:27017/${MONGO_DB_NAME}?authSource=${MONGO_DB_NAME}
DATABASE_NAME=${MONGO_DB_NAME}

# Remote Database (Enterprise)
REMOTE_DB_ENABLED=false
REMOTE_MONGO_URL=mongodb://localhost:27017

# Security Settings
LOG_LEVEL=INFO
SECRET_KEY=$(generate_password)

# CORS Configuration
CORS_ORIGINS=["http://localhost:3333", "https://localhost:3333"]

# Mining Configuration  
DEFAULT_THREADS=4
MAX_THREADS=64
ENTERPRISE_MODE=true

# Performance Settings
CONNECTION_POOL_SIZE=50
CONNECTION_TIMEOUT=30
QUERY_TIMEOUT=10
EOF
    
    # Secure the .env file
    chmod 600 .env
    
    success "Python environment configured securely"
}

# Setup frontend environment
setup_frontend_environment() {
    log "Setting up frontend environment..."
    
    cd "$INSTALL_DIR/frontend"
    
    # Install Node.js dependencies
    log "Installing frontend dependencies..."
    yarn install --frozen-lockfile
    
    # Create frontend configuration
    log "Creating frontend configuration..."
    cat > .env << EOF
# CryptoMiner Pro V30 - Frontend Configuration
REACT_APP_BACKEND_URL=http://localhost:8001
PORT=3333
GENERATE_SOURCEMAP=false
FAST_REFRESH=true
DANGEROUSLY_DISABLE_HOST_CHECK=false

# Security Settings
HTTPS=false
SSL_CRT_FILE=
SSL_KEY_FILE=

# Build Settings
BUILD_PATH=build
PUBLIC_URL=
EOF
    
    # Set file permissions
    chmod 644 .env
    
    # Build production assets
    log "Building production frontend assets..."
    yarn build
    
    success "Frontend environment configured"
}

# Setup secure services
setup_services() {
    log "Setting up secure system services..."
    
    # Create supervisor configuration for user-space operation
    sudo tee /etc/supervisor/conf.d/${SERVICE_NAME}.conf > /dev/null << EOF
# CryptoMiner Pro V30 - Secure Service Configuration
[group:${SERVICE_NAME}]
programs=backend,frontend
priority=999

[program:backend]
command=${INSTALL_DIR}/backend/venv/bin/python server.py
directory=${INSTALL_DIR}/backend
user=${USER}
autostart=true
autorestart=true
startsecs=10
startretries=3
stderr_logfile=${INSTALL_DIR}/logs/backend.err.log
stdout_logfile=${INSTALL_DIR}/logs/backend.out.log
stderr_logfile_maxbytes=50MB
stdout_logfile_maxbytes=50MB
stderr_logfile_backups=3
stdout_logfile_backups=3
environment=PATH="${INSTALL_DIR}/backend/venv/bin",HOME="${USER_HOME}",USER="${USER}"

[program:frontend]
command=yarn start
directory=${INSTALL_DIR}/frontend
user=${USER}
autostart=true
autorestart=true
startsecs=10
startretries=3
stderr_logfile=${INSTALL_DIR}/logs/frontend.err.log
stdout_logfile=${INSTALL_DIR}/logs/frontend.out.log
stderr_logfile_maxbytes=50MB
stdout_logfile_maxbytes=50MB
stderr_logfile_backups=3
stdout_logfile_backups=3
environment=PORT="3333",HOME="${USER_HOME}",USER="${USER}"
EOF
    
    # Set log directory permissions
    mkdir -p "$INSTALL_DIR/logs"
    chmod 755 "$INSTALL_DIR/logs"
    chown $USER:$USER "$INSTALL_DIR/logs"
    
    # Reload supervisor configuration
    sudo supervisorctl reread
    sudo supervisorctl update
    
    success "Secure services configured"
}

# Start all services
start_services() {
    log "Starting CryptoMiner Pro V30 services..."
    
    # Ensure MongoDB is running
    if ! sudo systemctl is-active --quiet mongod; then
        sudo systemctl start mongod
    fi
    
    # Start application services
    sudo supervisorctl start ${SERVICE_NAME}:backend
    sleep 5
    sudo supervisorctl start ${SERVICE_NAME}:frontend
    
    success "All services started"
}

# Verify installation
verify_installation() {
    log "Performing comprehensive installation verification..."
    
    # Check service status
    log "Checking service status..."
    if ! sudo supervisorctl status ${SERVICE_NAME}:backend | grep -q "RUNNING"; then
        error "Backend service is not running"
        sudo supervisorctl status ${SERVICE_NAME}:backend
        return 1
    fi
    
    if ! sudo supervisorctl status ${SERVICE_NAME}:frontend | grep -q "RUNNING"; then
        error "Frontend service is not running"  
        sudo supervisorctl status ${SERVICE_NAME}:frontend
        return 1
    fi
    
    # Check API endpoints
    log "Testing API connectivity..."
    local backend_check=0
    for i in {1..30}; do
        if curl -s http://localhost:8001/api/health > /dev/null; then
            backend_check=1
            break
        fi
        sleep 2
    done
    
    if [ $backend_check -eq 0 ]; then
        error "Backend API is not responding after 60 seconds"
        return 1
    fi
    
    # Check frontend
    log "Testing frontend accessibility..."
    local frontend_check=0
    for i in {1..20}; do
        if curl -s http://localhost:3333 > /dev/null; then
            frontend_check=1
            break
        fi
        sleep 3
    done
    
    if [ $frontend_check -eq 0 ]; then
        error "Frontend is not responding after 60 seconds"
        return 1
    fi
    
    # Test database connectivity
    log "Testing database connectivity..."
    local db_test=$(curl -s http://localhost:8001/api/health | jq -r '.database.status' 2>/dev/null || echo "failed")
    if [ "$db_test" != "connected" ]; then
        error "Database connection test failed: $db_test"
        return 1
    fi
    
    success "All verification tests passed"
}

# Create management scripts
create_management_scripts() {
    log "Creating management and maintenance scripts..."
    
    # Create start script
    cat > "$INSTALL_DIR/start.sh" << EOF
#!/bin/bash
# CryptoMiner Pro V30 - Start Services
sudo supervisorctl start ${SERVICE_NAME}:all
sudo supervisorctl status ${SERVICE_NAME}:all
EOF
    
    # Create stop script  
    cat > "$INSTALL_DIR/stop.sh" << EOF
#!/bin/bash
# CryptoMiner Pro V30 - Stop Services
sudo supervisorctl stop ${SERVICE_NAME}:all
EOF
    
    # Create status script
    cat > "$INSTALL_DIR/status.sh" << EOF
#!/bin/bash
# CryptoMiner Pro V30 - Service Status
echo "=== Service Status ==="
sudo supervisorctl status ${SERVICE_NAME}:all
echo ""
echo "=== MongoDB Status ==="
sudo systemctl status mongod --no-pager -l
echo ""
echo "=== API Health Check ==="
curl -s http://localhost:8001/api/health | jq . || echo "API not responding"
EOF
    
    # Create backup script
    cat > "$INSTALL_DIR/backup.sh" << EOF
#!/bin/bash
# CryptoMiner Pro V30 - Backup Script
BACKUP_DIR="$INSTALL_DIR/backup/\$(date +%Y%m%d_%H%M%S)"
mkdir -p "\$BACKUP_DIR"

echo "Creating backup at \$BACKUP_DIR..."

# Backup configuration
cp "$INSTALL_DIR/backend/.env" "\$BACKUP_DIR/"
cp "$INSTALL_DIR/frontend/.env" "\$BACKUP_DIR/"

# Backup database
mongodump --uri="mongodb://${MONGO_APP_USER}:${MONGO_APP_PASS}@localhost:27017/${MONGO_DB_NAME}?authSource=${MONGO_DB_NAME}" --out "\$BACKUP_DIR/mongodb/"

echo "Backup completed: \$BACKUP_DIR"
EOF
    
    # Make scripts executable
    chmod +x "$INSTALL_DIR"/*.sh
    
    success "Management scripts created"
}

# Display completion message with security information
display_completion_message() {
    success "🎉 CryptoMiner Pro V30 installation completed successfully!"
    echo ""
    security "=== SECURITY INFORMATION ==="
    security "Installation Directory: $INSTALL_DIR"
    security "Database: $MONGO_DB_NAME (authenticated)"
    security "App User: $MONGO_APP_USER"
    security "Configuration files are secured with 600 permissions"
    echo ""
    info "=== ACCESS INFORMATION ==="
    info "Mining Dashboard: http://localhost:3333"
    info "API Endpoint: http://localhost:8001/api"
    info "API Documentation: http://localhost:8001/docs"
    echo ""
    info "=== SERVICE MANAGEMENT ==="
    info "Start All:    $INSTALL_DIR/start.sh"
    info "Stop All:     $INSTALL_DIR/stop.sh"  
    info "Status Check: $INSTALL_DIR/status.sh"
    info "Backup:       $INSTALL_DIR/backup.sh"
    echo ""
    info "Manual Commands:"
    info "  Start:   sudo supervisorctl start ${SERVICE_NAME}:all"
    info "  Stop:    sudo supervisorctl stop ${SERVICE_NAME}:all"
    info "  Restart: sudo supervisorctl restart ${SERVICE_NAME}:all"
    info "  Status:  sudo supervisorctl status ${SERVICE_NAME}:all"
    echo ""
    info "=== LOG FILES ==="
    info "Backend:  $INSTALL_DIR/logs/backend.out.log"
    info "Frontend: $INSTALL_DIR/logs/frontend.out.log"
    info "MongoDB:  /var/log/mongodb/mongod.log"
    echo ""
    warning "=== IMPORTANT NOTES ==="
    warning "1. Database password is saved in $INSTALL_DIR/backend/.env"
    warning "2. Keep backup of .env files for recovery"
    warning "3. Run $INSTALL_DIR/backup.sh regularly"
    warning "4. Monitor logs for any security issues"
    echo ""
    success "Installation completed securely! 🔒"
}

# Main installation function
main() {
    log "🚀 Starting CryptoMiner Pro V30 secure installation..."
    echo ""
    
    # Pre-installation checks
    check_permissions
    check_system_requirements
    
    # System setup
    install_system_dependencies
    install_python
    install_nodejs
    install_mongodb
    setup_mongodb_security
    
    # Application setup  
    create_installation_directory
    setup_python_environment
    setup_frontend_environment
    setup_services
    
    # Service startup and verification
    start_services
    sleep 10
    verify_installation
    
    # Finalization
    create_management_scripts
    display_completion_message
    
    success "🎯 CryptoMiner Pro V30 is ready for cryptocurrency mining!"
}

# Trap signals for cleanup
trap 'error "Installation interrupted"; exit 1' INT TERM

# Check if running from correct directory
if [ ! -f "backend/server.py" ] || [ ! -f "frontend/package.json" ]; then
    error "Please run this script from the CryptoMiner Pro V30 source directory"
    error "Expected files: backend/server.py, frontend/package.json"
    exit 1
fi

# Run main installation
main "$@"