#!/bin/bash

# Find and Fix CryptoMiner Pro Installation

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

# Find the actual installation directory
find_installation() {
    log "Finding CryptoMiner Pro installation directory..."
    
    # Method 1: Check supervisor configuration
    if [ -f /etc/supervisor/conf.d/mining_system.conf ]; then
        local backend_dir=$(grep "directory=" /etc/supervisor/conf.d/mining_system.conf | grep backend | cut -d'=' -f2 | head -1)
        if [ -n "$backend_dir" ] && [ -d "$backend_dir" ]; then
            INSTALL_DIR="$(dirname "$backend_dir")"
            log "Found installation via supervisor config: $INSTALL_DIR"
            return 0
        fi
    fi
    
    # Method 2: Check running processes
    local process_path=$(ps aux | grep "server.py" | grep -v grep | awk '{for(i=11;i<=NF;i++) if($i ~ /server\.py$/) print $i}' | head -1)
    if [ -n "$process_path" ] && [ -f "$process_path" ]; then
        INSTALL_DIR="$(dirname "$(dirname "$process_path")")"
        log "Found installation via running process: $INSTALL_DIR"
        return 0
    fi
    
    # Method 3: Search common locations
    local locations=(
        "/opt/cryptominer-pro"
        "/usr/local/cryptominer-pro"
        "/home/$USER/cryptominer-pro"
        "$HOME/Desktop/Cryptominer-pro-Enterprise-main"
        "$(pwd)"
    )
    
    for dir in "${locations[@]}"; do
        if [ -d "$dir/backend" ] && [ -f "$dir/backend/server.py" ]; then
            INSTALL_DIR="$dir"
            log "Found installation at: $INSTALL_DIR"
            return 0
        fi
    done
    
    error "Could not find CryptoMiner Pro installation directory"
    return 1
}

# Fix the motor package issue
fix_motor_package() {
    log "Fixing motor package installation..."
    
    if [ ! -d "$INSTALL_DIR/backend" ]; then
        error "Backend directory not found: $INSTALL_DIR/backend"
        return 1
    fi
    
    cd "$INSTALL_DIR/backend"
    
    if [ ! -d "venv" ]; then
        error "Virtual environment not found: $INSTALL_DIR/backend/venv"
        return 1
    fi
    
    log "Activating virtual environment..."
    source venv/bin/activate
    
    log "Installing missing motor package..."
    pip install motor
    
    log "Installing other potentially missing packages..."
    pip install motor pymongo asyncio-mqtt aiofiles
    
    success "Packages installed successfully"
}

# Test the fix
test_backend() {
    log "Testing backend functionality..."
    
    cd "$INSTALL_DIR/backend"
    source venv/bin/activate
    
    # Test critical imports
    python -c "
import sys
try:
    import motor
    print('✅ motor: OK')
except ImportError as e:
    print(f'❌ motor: {e}')
    
try:
    import pymongo
    print('✅ pymongo: OK')
except ImportError as e:
    print(f'❌ pymongo: {e}')
    
try:
    import fastapi
    print('✅ fastapi: OK')
except ImportError as e:
    print(f'❌ fastapi: {e}')
"
    
    # Test MongoDB connection
    python -c "
import pymongo
try:
    client = pymongo.MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=2000)
    client.admin.command('ping')
    print('✅ MongoDB connection: OK')
except Exception as e:
    print(f'❌ MongoDB connection: {e}')
"
}

# Restart services
restart_services() {
    log "Restarting backend service..."
    
    sudo supervisorctl restart mining_system:backend
    sleep 3
    
    local status=$(sudo supervisorctl status mining_system:backend | awk '{print $2}')
    if [ "$status" = "RUNNING" ]; then
        success "Backend service is running"
    else
        error "Backend service failed to start"
        return 1
    fi
    
    # Test API
    log "Testing API endpoint..."
    if curl -s http://localhost:8001/api/health > /dev/null; then
        success "Backend API is responding"
    else
        error "Backend API is not responding"
        return 1
    fi
}

# Main function
main() {
    log "Starting CryptoMiner Pro installation fix..."
    
    # Find installation directory
    if ! find_installation; then
        exit 1
    fi
    
    # Fix motor package
    if fix_motor_package; then
        success "Motor package fixed"
    else
        error "Failed to fix motor package"
        exit 1
    fi
    
    # Test backend
    if test_backend; then
        success "Backend test passed"
    else
        warning "Backend test had issues (but may still work)"
    fi
    
    # Restart services
    if restart_services; then
        success "🎉 Fix completed successfully!"
        log ""
        log "Installation directory: $INSTALL_DIR"
        log "Backend API: http://localhost:8001/api/health"
        log "Frontend: http://localhost:3334"
        log ""
        log "Your CryptoMiner Pro should now be fully functional!"
    else
        error "Service restart failed"
        exit 1
    fi
}

# Run main function
main "$@"