#!/bin/bash

# 🔧 Python Environment Fix Script
# Fixes externally-managed-environment issues for CryptoMiner Pro

set -e

PROJECT_DIR="/opt/cryptominer-pro"
LOG_FILE="/tmp/python-env-fix.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root or with sudo"
        print_info "Usage: sudo $0"
        exit 1
    fi
    
    if [ -z "$SUDO_USER" ]; then
        print_error "SUDO_USER not set. Please run with 'sudo $0'"
        exit 1
    fi
}

# Fix Python environment for CryptoMiner Pro
fix_python_environment() {
    echo "🔧 Fixing Python Environment for CryptoMiner Pro"
    echo "================================================="
    echo ""
    
    if [ ! -d "$PROJECT_DIR" ]; then
        print_error "CryptoMiner Pro not found at $PROJECT_DIR"
        print_info "Please install CryptoMiner Pro first"
        exit 1
    fi
    
    print_info "Creating virtual environment for CryptoMiner Pro"
    
    # Create virtual environment
    if [ ! -d "$PROJECT_DIR/venv" ]; then
        sudo -u "$SUDO_USER" python3 -m venv "$PROJECT_DIR/venv" >> "$LOG_FILE" 2>&1
        print_success "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi
    
    # Upgrade pip in virtual environment
    print_info "Upgrading pip in virtual environment"
    sudo -u "$SUDO_USER" "$PROJECT_DIR/venv/bin/pip" install --upgrade pip >> "$LOG_FILE" 2>&1
    print_success "Pip upgraded successfully"
    
    # Install requirements if they exist
    if [ -f "$PROJECT_DIR/backend/requirements.txt" ]; then
        print_info "Installing Python packages in virtual environment"
        cd "$PROJECT_DIR/backend"
        sudo -u "$SUDO_USER" "$PROJECT_DIR/venv/bin/pip" install -r requirements.txt >> "$LOG_FILE" 2>&1
        print_success "Python packages installed"
    else
        print_warning "requirements.txt not found - skipping package installation"
    fi
    
    # Update supervisor configuration
    print_info "Updating supervisor configuration"
    
    if [ -f "/etc/supervisor/conf.d/cryptominer-pro.conf" ]; then
        # Backup original config
        cp "/etc/supervisor/conf.d/cryptominer-pro.conf" "/etc/supervisor/conf.d/cryptominer-pro.conf.backup"
        
        # Create new config with virtual environment
        cat > /etc/supervisor/conf.d/cryptominer-pro.conf << EOF
[program:cryptominer-backend]
command=$PROJECT_DIR/venv/bin/python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
directory=$PROJECT_DIR/backend
user=$SUDO_USER
autostart=true
autorestart=true
stderr_logfile=$PROJECT_DIR/logs/backend.err.log
stdout_logfile=$PROJECT_DIR/logs/backend.out.log
environment=PATH="$PROJECT_DIR/venv/bin:/usr/bin:/bin",PYTHONPATH="$PROJECT_DIR/backend"

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
        
        print_success "Supervisor configuration updated"
        
        # Reload supervisor
        print_info "Reloading supervisor configuration"
        supervisorctl reread >> "$LOG_FILE" 2>&1
        supervisorctl update >> "$LOG_FILE" 2>&1
        supervisorctl restart cryptominer-pro:cryptominer-backend >> "$LOG_FILE" 2>&1
        
        print_success "Services restarted with new configuration"
    else
        print_warning "Supervisor configuration not found"
    fi
    
    # Set proper permissions
    chown -R "$SUDO_USER:$SUDO_USER" "$PROJECT_DIR/venv"
    
    print_success "Python environment fix completed!"
    
    echo ""
    echo "📋 Summary:"
    echo "==========="
    echo "✅ Created virtual environment at: $PROJECT_DIR/venv"
    echo "✅ Upgraded pip in virtual environment"
    echo "✅ Installed Python packages in virtual environment"
    echo "✅ Updated supervisor configuration"
    echo "✅ Restarted backend service"
    echo ""
    echo "🔍 Check status with: cryptominer-status"
    echo "📄 View logs with: cryptominer-logs"
}

# Verify the fix
verify_fix() {
    echo ""
    echo "🔍 Verifying Fix"
    echo "================"
    
    # Check if virtual environment works
    if [ -f "$PROJECT_DIR/venv/bin/python" ]; then
        VENV_PYTHON_VERSION=$("$PROJECT_DIR/venv/bin/python" --version 2>&1)
        print_success "Virtual environment Python: $VENV_PYTHON_VERSION"
    else
        print_error "Virtual environment not working"
        return 1
    fi
    
    # Check if pip works in venv
    if "$PROJECT_DIR/venv/bin/pip" --version >> "$LOG_FILE" 2>&1; then
        VENV_PIP_VERSION=$("$PROJECT_DIR/venv/bin/pip" --version | cut -d' ' -f2)
        print_success "Virtual environment pip: $VENV_PIP_VERSION"
    else
        print_error "Virtual environment pip not working"
        return 1
    fi
    
    # Check service status
    if supervisorctl status cryptominer-pro:cryptominer-backend | grep -q RUNNING; then
        print_success "Backend service is running"
    else
        print_warning "Backend service may need attention"
        print_info "Try: sudo supervisorctl restart cryptominer-pro:cryptominer-backend"
    fi
    
    print_success "Fix verification completed!"
}

# Main execution
main() {
    echo "🔧 Python Environment Fix for CryptoMiner Pro"
    echo "=============================================="
    echo ""
    
    check_root
    
    echo "This script will fix Python environment issues by:"
    echo "• Creating a virtual environment for CryptoMiner Pro"
    echo "• Installing packages in the virtual environment"
    echo "• Updating supervisor configuration to use virtual environment"
    echo ""
    
    read -p "Continue with the fix? [y/N]: " -r
    if [ ! "$REPLY" = "y" ] && [ ! "$REPLY" = "Y" ]; then
        echo "Fix cancelled by user"
        exit 0
    fi
    
    fix_python_environment
    verify_fix
    
    echo ""
    print_success "🎉 Python environment successfully fixed!"
    echo ""
    echo "💡 Next steps:"
    echo "• Check service status: cryptominer-status"
    echo "• View logs if needed: cryptominer-logs"
    echo "• Access dashboard: http://localhost:3000"
}

# Handle arguments
case "${1:-}" in
    "--help"|"-h")
        echo "Python Environment Fix Script for CryptoMiner Pro"
        echo ""
        echo "Usage: sudo $0"
        echo ""
        echo "This script fixes the 'externally-managed-environment' error"
        echo "by creating a virtual environment for CryptoMiner Pro and"
        echo "updating the service configuration accordingly."
        echo ""
        echo "Requirements:"
        echo "• CryptoMiner Pro must be installed"
        echo "• Run as root/sudo user"
        ;;
    *)
        main "$@"
        ;;
esac