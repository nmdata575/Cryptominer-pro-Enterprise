#!/bin/bash

# CryptoMiner Pro - Supervisor Setup Script
# This script configures supervisor to manage the mining services

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

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    error "This script must be run as root (use sudo)"
    exit 1
fi

log "Setting up CryptoMiner Pro Supervisor configuration..."

# Install supervisor if not already installed
if ! command -v supervisorctl &> /dev/null; then
    log "Installing supervisor..."
    apt update
    apt install -y supervisor
fi

# Create supervisor configuration directory if it doesn't exist
mkdir -p /etc/supervisor/conf.d

# Create the mining app supervisor configuration
log "Creating supervisor configuration..."

cat > /etc/supervisor/conf.d/cryptominer-pro.conf << 'EOF'
[program:cryptominer_backend]
command=/app/backend/venv/bin/python -m uvicorn server:app --host 0.0.0.0 --port 8001
directory=/app/backend
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/cryptominer_backend.err.log
stdout_logfile=/var/log/supervisor/cryptominer_backend.out.log
user=www-data
environment=PATH="/app/backend/venv/bin"

[program:cryptominer_frontend]
command=yarn start
directory=/app/frontend
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/cryptominer_frontend.err.log
stdout_logfile=/var/log/supervisor/cryptominer_frontend.out.log
user=www-data
environment=PORT=3333,PATH="/usr/bin:/bin:/usr/local/bin"

[group:cryptominer_pro]
programs=cryptominer_backend,cryptominer_frontend
priority=999
EOF

# Create log directory
mkdir -p /var/log/supervisor

# Set proper ownership for the application directory
chown -R www-data:www-data /app

# Reload supervisor configuration
log "Reloading supervisor configuration..."
supervisorctl reread
supervisorctl update

# Check if services are configured
log "Checking supervisor configuration..."
if supervisorctl avail | grep -q cryptominer_pro; then
    success "CryptoMiner Pro services configured successfully!"
    
    # Start services
    log "Starting CryptoMiner Pro services..."
    supervisorctl start cryptominer_pro:*
    
    # Show status
    echo
    log "Service Status:"
    supervisorctl status cryptominer_pro:*
    
    echo
    success "Setup complete! Services should be running on:"
    echo "  🌐 Frontend: http://localhost:3333"
    echo "  🔧 Backend:  http://localhost:8001"
    echo
    echo "💡 Useful commands:"
    echo "  sudo supervisorctl status                    # Check all services"
    echo "  sudo supervisorctl start cryptominer_pro:*  # Start all services"
    echo "  sudo supervisorctl stop cryptominer_pro:*   # Stop all services"
    echo "  sudo supervisorctl restart cryptominer_pro:* # Restart all services"
    
else
    error "Failed to configure supervisor services"
    exit 1
fi
EOF