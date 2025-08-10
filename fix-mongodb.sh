#!/bin/bash

# CryptoMiner Pro - MongoDB Installation Fix Script
# Addresses common MongoDB installation issues on Ubuntu 24.04+

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

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Clean up existing MongoDB repositories and keys
cleanup_mongodb_repos() {
    log "Cleaning up existing MongoDB repositories..."
    
    # Remove existing MongoDB repository files
    sudo rm -f /etc/apt/sources.list.d/mongodb*.list
    
    # Remove existing GPG keys
    sudo rm -f /usr/share/keyrings/mongodb*.gpg
    
    # Clean apt cache
    sudo apt clean
    sudo apt update
    
    success "Cleaned up existing MongoDB repositories"
}

# Install MongoDB 7.0 (stable and compatible)
install_mongodb_70() {
    log "Installing MongoDB 7.0..."
    
    # Install required packages
    sudo apt install -y gnupg curl
    
    # Import MongoDB GPG key
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
        sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
    
    # Determine Ubuntu codename
    local ubuntu_version=$(lsb_release -cs)
    
    # For Ubuntu 24.04 (noble), use jammy repository
    if [ "$ubuntu_version" = "noble" ] || [ "$ubuntu_version" = "oracular" ]; then
        ubuntu_version="jammy"
        log "Using jammy repository for Ubuntu 24.04+ compatibility"
    fi
    
    # Add MongoDB repository
    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu $ubuntu_version/mongodb-org/7.0 multiverse" | \
        sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
    
    # Update package list
    sudo apt update
    
    # Install MongoDB
    sudo apt install -y mongodb-org
    
    return $?
}

# Fallback installation using snap
install_mongodb_snap() {
    log "Installing MongoDB via snap..."
    
    # Install snapd if not present
    if ! command -v snap &> /dev/null; then
        sudo apt install -y snapd
    fi
    
    # Install MongoDB community server
    sudo snap install mongodb-community-server
    
    return $?
}

# Alternative installation using Docker
install_mongodb_docker() {
    log "Installing MongoDB via Docker..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
    fi
    
    # Create MongoDB data directory
    sudo mkdir -p /opt/mongodb/data
    sudo chown -R $USER:$USER /opt/mongodb
    
    # Run MongoDB container
    docker run -d \
        --name mongodb \
        --restart unless-stopped \
        -p 27017:27017 \
        -v /opt/mongodb/data:/data/db \
        mongo:7.0
    
    # Create systemd service for MongoDB Docker container
    sudo tee /etc/systemd/system/mongodb-docker.service > /dev/null << EOF
[Unit]
Description=MongoDB Docker Container
Requires=docker.service
After=docker.service

[Service]
Type=simple
RemainAfterExit=yes
ExecStart=/usr/bin/docker start mongodb
ExecStop=/usr/bin/docker stop mongodb
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable mongodb-docker
    
    return $?
}

# Start MongoDB service
start_mongodb_service() {
    log "Starting MongoDB service..."
    
    # Try different service names
    if systemctl list-units --type=service | grep -q "mongod.service"; then
        sudo systemctl start mongod
        sudo systemctl enable mongod
        success "Started mongod service"
    elif systemctl list-units --type=service | grep -q "mongodb.service"; then
        sudo systemctl start mongodb
        sudo systemctl enable mongodb
        success "Started mongodb service"
    elif systemctl list-units --type=service | grep -q "mongodb-docker.service"; then
        sudo systemctl start mongodb-docker
        success "Started MongoDB Docker container"
    else
        warning "No MongoDB service found to start"
        return 1
    fi
    
    return 0
}

# Test MongoDB connection
test_mongodb_connection() {
    log "Testing MongoDB connection..."
    
    # Wait a moment for service to start
    sleep 3
    
    # Test connection using mongosh (new client) or mongo (legacy client)
    if command -v mongosh &> /dev/null; then
        if mongosh --eval "db.adminCommand('ping')" --quiet > /dev/null 2>&1; then
            success "MongoDB connection test passed (using mongosh)"
            return 0
        fi
    fi
    
    if command -v mongo &> /dev/null; then
        if mongo --eval "db.adminCommand('ping')" --quiet > /dev/null 2>&1; then
            success "MongoDB connection test passed (using mongo)"
            return 0
        fi
    fi
    
    # Test using Python pymongo as final check
    if python3 -c "
import pymongo
try:
    client = pymongo.MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print('MongoDB connection successful via pymongo')
    exit(0)
except Exception as e:
    print(f'MongoDB connection failed: {e}')
    exit(1)
" 2>/dev/null; then
        success "MongoDB connection test passed (using pymongo)"
        return 0
    fi
    
    error "MongoDB connection test failed"
    return 1
}

# Main function
main() {
    log "Starting MongoDB installation fix..."
    
    # Check if MongoDB is already working
    if test_mongodb_connection; then
        success "MongoDB is already working correctly!"
        exit 0
    fi
    
    # Clean up existing repositories
    cleanup_mongodb_repos
    
    # Try primary installation method
    if install_mongodb_70 && start_mongodb_service && test_mongodb_connection; then
        success "MongoDB 7.0 installed and working!"
        exit 0
    fi
    
    warning "Primary installation failed, trying snap installation..."
    
    # Try snap installation
    if install_mongodb_snap && start_mongodb_service && test_mongodb_connection; then
        success "MongoDB installed via snap and working!"
        exit 0
    fi
    
    warning "Snap installation failed, trying Docker installation..."
    
    # Try Docker installation
    if install_mongodb_docker && start_mongodb_service && test_mongodb_connection; then
        success "MongoDB installed via Docker and working!"
        exit 0
    fi
    
    error "All MongoDB installation methods failed!"
    error "Please check the following:"
    error "1. System compatibility (Ubuntu 20.04+ recommended)"
    error "2. Network connectivity for downloading packages"
    error "3. Available disk space (at least 2GB free)"
    error "4. System permissions (script should be run with sudo)"
    
    log "You can try running CryptoMiner Pro with an external MongoDB instance"
    log "Set MONGO_URL in /opt/cryptominer-pro/backend/.env to point to your MongoDB server"
    
    exit 1
}

# Check if running as root or with sudo
if [[ $EUID -eq 0 ]]; then
    warning "Running as root. This is generally not recommended but will proceed."
elif ! sudo -n true 2>/dev/null; then
    error "This script requires sudo privileges. Please run with sudo."
    exit 1
fi

# Run main function
main "$@"