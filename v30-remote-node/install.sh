#!/bin/bash

# CryptoMiner V30 Remote Node Installation Script
# Lightweight installation for mining nodes

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/cryptominer-v30-node"
SERVICE_NAME="cryptominer-v30-node"
USER_NAME="v30miner"
PYTHON_MIN_VERSION="3.8"
DEFAULT_SERVER_HOST="localhost"
DEFAULT_SERVER_PORT="9001"

# Print banner
print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║   🚀 CryptoMiner Enterprise V30 - Remote Node Installer     ║"
    echo "║                                                              ║"
    echo "║   Lightweight mining node for distributed operations        ║"
    echo "║   Version: 1.0.0                                             ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Detect operating system
detect_os() {
    log_step "Detecting operating system..."
    
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
        log_info "Detected OS: $PRETTY_NAME"
    else
        log_error "Cannot detect operating system"
        exit 1
    fi
    
    # Check if supported
    case $OS in
        ubuntu|debian)
            PACKAGE_MANAGER="apt-get"
            PYTHON_PKG="python3"
            PIP_PKG="python3-pip"
            ;;
        centos|rhel|rocky|almalinux)
            PACKAGE_MANAGER="yum"
            PYTHON_PKG="python3"
            PIP_PKG="python3-pip"
            ;;
        fedora)
            PACKAGE_MANAGER="dnf"
            PYTHON_PKG="python3"
            PIP_PKG="python3-pip"
            ;;
        *)
            log_warning "OS $OS may not be fully supported, attempting installation..."
            PACKAGE_MANAGER="apt-get"  # Default fallback
            PYTHON_PKG="python3"
            PIP_PKG="python3-pip"
            ;;
    esac
}

# Check Python version
check_python() {
    log_step "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_info "Found Python $PYTHON_VERSION"
        
        # Simple version check (should work for most cases)
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            log_success "Python version is compatible"
            return 0
        else
            log_warning "Python version may be too old, but attempting to continue..."
        fi
    else
        log_info "Python 3 not found, will install it"
        return 1
    fi
}

# Install system dependencies
install_system_deps() {
    log_step "Installing system dependencies..."
    
    # Update package manager
    case $PACKAGE_MANAGER in
        apt-get)
            apt-get update -qq
            apt-get install -y \
                python3 \
                python3-pip \
                python3-venv \
                curl \
                wget \
                git \
                build-essential \
                python3-dev \
                pkg-config \
                lsb-release \
                ca-certificates \
                gnupg \
                lsof \
                htop
            ;;
        yum|dnf)
            $PACKAGE_MANAGER install -y \
                python3 \
                python3-pip \
                python3-venv \
                curl \
                wget \
                git \
                gcc \
                gcc-c++ \
                python3-devel \
                pkgconfig \
                redhat-lsb-core \
                ca-certificates \
                gnupg2 \
                lsof \
                htop
            ;;
    esac
    
    log_success "System dependencies installed"
}

# Create user account
create_user() {
    log_step "Setting up user account..."
    
    if id "$USER_NAME" &>/dev/null; then
        log_info "User $USER_NAME already exists"
    else
        useradd -r -s /bin/bash -d "$INSTALL_DIR" "$USER_NAME"
        log_success "Created user: $USER_NAME"
    fi
}

# Create installation directory
setup_directories() {
    log_step "Setting up directories..."
    
    # Create main directory
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR/logs"
    mkdir -p "$INSTALL_DIR/data"
    mkdir -p "$INSTALL_DIR/updates"
    
    # Set ownership
    chown -R "$USER_NAME:$USER_NAME" "$INSTALL_DIR"
    chmod 755 "$INSTALL_DIR"
    
    log_success "Directories created: $INSTALL_DIR"
}

# Install Python dependencies
install_python_deps() {
    log_step "Installing Python dependencies..."
    
    # Create virtual environment
    sudo -u "$USER_NAME" python3 -m venv "$INSTALL_DIR/venv"
    
    # Install packages
    sudo -u "$USER_NAME" "$INSTALL_DIR/venv/bin/pip" install --upgrade pip
    sudo -u "$USER_NAME" "$INSTALL_DIR/venv/bin/pip" install \
        psutil==5.9.6 \
        asyncio \
        aiofiles \
        requests \
        cryptography
    
    log_success "Python dependencies installed"
}

# Install the remote node application
install_application() {
    log_step "Installing V30 Remote Node application..."
    
    # Copy the main application file
    if [[ -f "./v30_remote_node.py" ]]; then
        cp "./v30_remote_node.py" "$INSTALL_DIR/v30_remote_node.py"
        chown "$USER_NAME:$USER_NAME" "$INSTALL_DIR/v30_remote_node.py"
        chmod +x "$INSTALL_DIR/v30_remote_node.py"
        log_success "Application installed"
    else
        log_error "v30_remote_node.py not found in current directory"
        exit 1
    fi
}

# Create configuration
create_config() {
    log_step "Creating configuration..."
    
    # Get user input for configuration
    echo
    echo -e "${CYAN}📝 Configuration Setup${NC}"
    echo "Please provide the following information:"
    echo
    
    read -p "V30 Server Host [$DEFAULT_SERVER_HOST]: " SERVER_HOST
    SERVER_HOST=${SERVER_HOST:-$DEFAULT_SERVER_HOST}
    
    read -p "V30 Server Port [$DEFAULT_SERVER_PORT]: " SERVER_PORT
    SERVER_PORT=${SERVER_PORT:-$DEFAULT_SERVER_PORT}
    
    echo
    echo -e "${YELLOW}⚠️  Enterprise License Key Required${NC}"
    echo "You need a valid V30 Enterprise license key to connect to the server."
    echo "Contact your administrator or check the V30 server logs for available keys."
    echo
    read -p "Enterprise License Key: " LICENSE_KEY
    
    if [[ -z "$LICENSE_KEY" ]]; then
        log_warning "No license key provided. You can add it later in the config file."
        LICENSE_KEY=""
    fi
    
    # Create configuration file
    cat > "$INSTALL_DIR/node_config.json" << EOF
{
  "server_host": "$SERVER_HOST",
  "server_port": $SERVER_PORT,
  "license_key": "$LICENSE_KEY",
  "max_cpu_threads": $(nproc),
  "enable_gpu": true,
  "heartbeat_interval": 30.0,
  "work_request_interval": 10.0,
  "auto_update": true,
  "update_check_interval": 3600.0
}
EOF
    
    chown "$USER_NAME:$USER_NAME" "$INSTALL_DIR/node_config.json"
    chmod 600 "$INSTALL_DIR/node_config.json"  # Secure the config file
    
    log_success "Configuration created: $INSTALL_DIR/node_config.json"
}

# Create systemd service
create_service() {
    log_step "Creating systemd service..."
    
    cat > "/etc/systemd/system/$SERVICE_NAME.service" << EOF
[Unit]
Description=CryptoMiner V30 Remote Mining Node
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$USER_NAME
Group=$USER_NAME
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/v30_remote_node.py
Restart=always
RestartSec=10
StandardOutput=append:$INSTALL_DIR/logs/node.log
StandardError=append:$INSTALL_DIR/logs/error.log

# Security settings
PrivateTmp=true
ProtectHome=true
NoNewPrivileges=true

# Environment
Environment=PYTHONUNBUFFERED=1
Environment=PATH=$INSTALL_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    
    log_success "Service created: $SERVICE_NAME"
}

# Create management scripts
create_scripts() {
    log_step "Creating management scripts..."
    
    # Create start script
    cat > "$INSTALL_DIR/start.sh" << 'EOF'
#!/bin/bash
echo "🚀 Starting CryptoMiner V30 Remote Node..."
sudo systemctl start cryptominer-v30-node
sudo systemctl status cryptominer-v30-node --no-pager
EOF
    
    # Create stop script
    cat > "$INSTALL_DIR/stop.sh" << 'EOF'
#!/bin/bash
echo "🛑 Stopping CryptoMiner V30 Remote Node..."
sudo systemctl stop cryptominer-v30-node
echo "✅ Node stopped"
EOF
    
    # Create status script
    cat > "$INSTALL_DIR/status.sh" << 'EOF'
#!/bin/bash
echo "📊 CryptoMiner V30 Remote Node Status:"
echo "======================================"
sudo systemctl status cryptominer-v30-node --no-pager
echo ""
echo "📋 Recent Logs:"
echo "==============="
tail -n 20 /opt/cryptominer-v30-node/logs/node.log
EOF
    
    # Create update script
    cat > "$INSTALL_DIR/update.sh" << 'EOF'
#!/bin/bash
echo "📦 Checking for V30 Remote Node updates..."
echo "⚠️  Manual update process:"
echo "1. Download latest v30_remote_node.py from your V30 server"
echo "2. Stop the service: sudo systemctl stop cryptominer-v30-node"
echo "3. Replace the file: sudo cp v30_remote_node.py /opt/cryptominer-v30-node/"
echo "4. Fix permissions: sudo chown v30miner:v30miner /opt/cryptominer-v30-node/v30_remote_node.py"
echo "5. Start the service: sudo systemctl start cryptominer-v30-node"
EOF
    
    # Create logs script
    cat > "$INSTALL_DIR/logs.sh" << 'EOF'
#!/bin/bash
echo "📋 V30 Remote Node Logs:"
echo "========================"
echo "Press Ctrl+C to exit"
tail -f /opt/cryptominer-v30-node/logs/node.log
EOF
    
    # Make scripts executable
    chmod +x "$INSTALL_DIR"/*.sh
    chown "$USER_NAME:$USER_NAME" "$INSTALL_DIR"/*.sh
    
    log_success "Management scripts created"
}

# Set up firewall (optional)
setup_firewall() {
    log_step "Configuring firewall (optional)..."
    
    # Check if ufw is available
    if command -v ufw &> /dev/null; then
        log_info "Configuring UFW firewall..."
        ufw allow out 9001 comment "V30 Mining Server"
        log_success "Firewall configured for V30 server access"
    elif command -v firewall-cmd &> /dev/null; then
        log_info "Configuring firewalld..."
        firewall-cmd --permanent --add-port=9001/tcp
        firewall-cmd --reload
        log_success "Firewall configured for V30 server access"
    else
        log_info "No firewall management tool found, skipping firewall configuration"
    fi
}

# Test installation
test_installation() {
    log_step "Testing installation..."
    
    # Test Python environment
    if sudo -u "$USER_NAME" "$INSTALL_DIR/venv/bin/python" -c "import psutil, json, hashlib, asyncio; print('✅ Python modules OK')"; then
        log_success "Python environment test passed"
    else
        log_error "Python environment test failed"
        return 1
    fi
    
    # Test configuration loading
    if sudo -u "$USER_NAME" "$INSTALL_DIR/venv/bin/python" -c "
import json
with open('$INSTALL_DIR/node_config.json') as f:
    config = json.load(f)
print('✅ Configuration loading OK')
print(f'Server: {config[\"server_host\"]}:{config[\"server_port\"]}')
"; then
        log_success "Configuration test passed"
    else
        log_error "Configuration test failed"
        return 1
    fi
    
    log_success "Installation tests completed"
}

# Start the service
start_service() {
    log_step "Starting V30 Remote Node service..."
    
    systemctl start "$SERVICE_NAME"
    sleep 3
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_success "V30 Remote Node service started successfully"
        return 0
    else
        log_error "Service failed to start"
        log_info "Check logs: journalctl -u $SERVICE_NAME -f"
        return 1
    fi
}

# Print completion message
print_completion() {
    echo
    echo -e "${GREEN}🎉 CryptoMiner V30 Remote Node Installation Complete!${NC}"
    echo
    echo -e "${CYAN}📁 Installation Directory:${NC} $INSTALL_DIR"
    echo -e "${CYAN}👤 Service User:${NC} $USER_NAME"
    echo -e "${CYAN}⚙️  Service Name:${NC} $SERVICE_NAME"
    echo
    echo -e "${YELLOW}🔧 Management Commands:${NC}"
    echo "  Start:    sudo systemctl start $SERVICE_NAME"
    echo "  Stop:     sudo systemctl stop $SERVICE_NAME"
    echo "  Status:   sudo systemctl status $SERVICE_NAME"
    echo "  Logs:     sudo journalctl -u $SERVICE_NAME -f"
    echo
    echo -e "${YELLOW}📋 Quick Scripts:${NC}"
    echo "  Status:   $INSTALL_DIR/status.sh"
    echo "  Logs:     $INSTALL_DIR/logs.sh"
    echo "  Start:    $INSTALL_DIR/start.sh"
    echo "  Stop:     $INSTALL_DIR/stop.sh"
    echo
    echo -e "${YELLOW}📝 Configuration:${NC}"
    echo "  Config:   $INSTALL_DIR/node_config.json"
    echo "  Logs:     $INSTALL_DIR/logs/"
    echo
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✅ Service Status: RUNNING${NC}"
        echo -e "${GREEN}✅ Node should now be connecting to the V30 server${NC}"
    else
        echo -e "${RED}❌ Service Status: NOT RUNNING${NC}"
        echo -e "${YELLOW}⚠️  Check service logs for connection issues${NC}"
    fi
    echo
    echo -e "${CYAN}🔗 Next Steps:${NC}"
    echo "1. Verify the node connects to your V30 server"
    echo "2. Check the V30 server dashboard for this node"
    echo "3. Monitor logs for any connection or license issues"
    echo "4. Ensure your V30 enterprise license is valid"
    echo
}

# Main installation function
main() {
    print_banner
    
    log_info "Starting CryptoMiner V30 Remote Node installation..."
    echo
    
    # Pre-installation checks
    check_root
    detect_os
    
    # Installation steps
    check_python || install_system_deps
    install_system_deps
    create_user
    setup_directories
    install_python_deps
    install_application
    create_config
    create_service
    create_scripts
    setup_firewall
    
    # Test and start
    if test_installation; then
        if start_service; then
            print_completion
            exit 0
        else
            log_error "Service failed to start, but installation completed"
            log_info "You can manually start with: sudo systemctl start $SERVICE_NAME"
            exit 1
        fi
    else
        log_error "Installation tests failed"
        exit 1
    fi
}

# Handle script interruption
trap 'echo -e "\n${RED}Installation interrupted!${NC}"; exit 1' INT TERM

# Run main function
main "$@"