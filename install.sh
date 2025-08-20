#!/bin/bash

# CryptoMiner Pro V30 - Comprehensive Installation Script
# This script handles all dependencies and setup for the mining application

set -e  # Exit on any error

echo "🚀 CryptoMiner Pro V30 - Installation Script"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root. Some installations may be affected."
    fi
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get >/dev/null; then
            OS="ubuntu"
            log_info "Detected Ubuntu/Debian system"
        elif command -v yum >/dev/null; then
            OS="centos"
            log_info "Detected CentOS/RHEL system"
        elif command -v pacman >/dev/null; then
            OS="arch"
            log_info "Detected Arch Linux system"
        else
            OS="linux"
            log_info "Detected generic Linux system"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        log_info "Detected macOS system"
    else
        OS="unknown"
        log_warning "Unknown operating system: $OSTYPE"
    fi
}

# Install system dependencies
install_system_deps() {
    log_info "Installing system dependencies..."
    
    case $OS in
        "ubuntu")
            sudo apt-get update
            sudo apt-get install -y \
                python3 \
                python3-pip \
                python3-venv \
                python3-dev \
                build-essential \
                libssl-dev \
                libffi-dev \
                curl \
                wget \
                git \
                htop \
                net-tools
            ;;
        "centos")
            sudo yum update -y
            sudo yum install -y \
                python3 \
                python3-pip \
                python3-devel \
                gcc \
                gcc-c++ \
                make \
                openssl-devel \
                libffi-devel \
                curl \
                wget \
                git \
                htop \
                net-tools
            ;;
        "arch")
            sudo pacman -Syu --noconfirm
            sudo pacman -S --noconfirm \
                python3 \
                python-pip \
                base-devel \
                openssl \
                libffi \
                curl \
                wget \
                git \
                htop \
                net-tools
            ;;
        "macos")
            # Check if Homebrew is installed
            if ! command -v brew >/dev/null; then
                log_info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            
            brew update
            brew install python3 curl wget git htop
            ;;
        *)
            log_warning "Please install Python 3.8+, pip, and build tools manually"
            ;;
    esac
    
    log_success "System dependencies installed"
}

# Install Node.js
install_nodejs() {
    log_info "Installing Node.js..."
    
    if command -v node >/dev/null; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        log_info "Node.js version $NODE_VERSION already installed"
        
        # Check if version is 18+
        if [[ $(echo "$NODE_VERSION" | cut -d'.' -f1) -lt 18 ]]; then
            log_warning "Node.js version is below 18. Updating..."
            install_nodejs_fresh
        else
            log_success "Node.js version is sufficient"
        fi
    else
        install_nodejs_fresh
    fi
}

install_nodejs_fresh() {
    case $OS in
        "ubuntu")
            curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
            sudo apt-get install -y nodejs
            ;;
        "centos")
            curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
            sudo yum install -y nodejs
            ;;
        "arch")
            sudo pacman -S --noconfirm nodejs npm
            ;;
        "macos")
            brew install node
            ;;
        *)
            log_error "Please install Node.js 18+ manually from https://nodejs.org/"
            exit 1
            ;;
    esac
    
    log_success "Node.js installed successfully"
}

# Create virtual environment and install Python dependencies
setup_python_env() {
    log_info "Setting up Python environment..."
    
    # Create virtual environment
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
        log_success "Virtual environment created"
    else
        log_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt
    
    log_success "Python dependencies installed"
}

# Setup configuration files
setup_config() {
    log_info "Setting up configuration files..."
    
    # Create mining_config.env if it doesn't exist
    if [[ ! -f "mining_config.env" ]]; then
        if [[ -f "mining_config.template" ]]; then
            cp mining_config.template mining_config.env
            log_success "Created mining_config.env from template"
        else
            # Create basic config
            cat > mining_config.env << EOF
# CryptoMiner Pro V30 Configuration
# Edit this file with your mining settings

COIN=LTC
WALLET=your_wallet_address_here
POOL=ltc.luckymonster.pro:4112
PASSWORD=_d=128
INTENSITY=80
THREADS=8
WEB_PORT=8001
WEB_ENABLED=true
AI_ENABLED=true
EOF
            log_success "Created basic mining_config.env"
        fi
        
        log_warning "Please edit mining_config.env with your wallet address and preferences"
    else
        log_info "mining_config.env already exists"
    fi
    
    # Create backend .env if it doesn't exist
    if [[ ! -f "backend/.env" ]] && [[ -d "backend" ]]; then
        cat > backend/.env << EOF
MONGO_URL="mongodb://localhost:27017"
DB_NAME="cryptominer_db"
CORS_ORIGINS="*"
EOF
        log_success "Created backend/.env"
    fi
}

# Install MongoDB (optional)
install_mongodb() {
    read -p "Do you want to install MongoDB for advanced statistics? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Installing MongoDB..."
        
        case $OS in
            "ubuntu")
                wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
                echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
                sudo apt-get update
                sudo apt-get install -y mongodb-org
                sudo systemctl start mongod
                sudo systemctl enable mongod
                ;;
            "centos")
                cat > /etc/yum.repos.d/mongodb-org-6.0.repo << EOF
[mongodb-org-6.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/\$releasever/mongodb-org/6.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-6.0.asc
EOF
                sudo yum install -y mongodb-org
                sudo systemctl start mongod
                sudo systemctl enable mongod
                ;;
            "macos")
                brew tap mongodb/brew
                brew install mongodb-community
                brew services start mongodb/brew/mongodb-community
                ;;
            *)
                log_warning "Please install MongoDB manually"
                ;;
        esac
        
        log_success "MongoDB installation attempted"
    else
        log_info "Skipping MongoDB installation"
    fi
}

# Create startup scripts
create_scripts() {
    log_info "Creating startup scripts..."
    
    # Create start script
    cat > start.sh << EOF
#!/bin/bash
# Start CryptoMiner Pro V30

echo "🚀 Starting CryptoMiner Pro V30..."

# Activate virtual environment
source venv/bin/activate

# Start the mining application
python3 cryptominer.py --proxy-mode
EOF
    chmod +x start.sh
    
    # Create start with web dashboard script
    cat > start-with-dashboard.sh << EOF
#!/bin/bash
# Start CryptoMiner Pro V30 with Web Dashboard

echo "🚀 Starting CryptoMiner Pro V30 with Web Dashboard..."

# Activate virtual environment
source venv/bin/activate

# Start mining with integrated web dashboard
python3 cryptominer.py --proxy-mode

echo "📊 Web Dashboard: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8001"
EOF
    chmod +x start-with-dashboard.sh
    
    # Create stop script
    cat > stop.sh << EOF
#!/bin/bash
# Stop CryptoMiner Pro V30

echo "🛑 Stopping CryptoMiner Pro V30..."

# Kill mining processes
pkill -f "python3.*cryptominer"
pkill -f "uvicorn.*server"
pkill -f "http.server"

echo "✅ CryptoMiner Pro V30 stopped"
EOF
    chmod +x stop.sh
    
    log_success "Startup scripts created"
}

# Test installation
test_installation() {
    log_info "Testing installation..."
    
    # Test Python dependencies
    source venv/bin/activate
    
    python3 -c "
import sys
print(f'Python version: {sys.version}')

try:
    import fastapi
    import uvicorn
    import asyncio
    import aiohttp
    import scrypt
    import psutil
    print('✅ All required Python packages available')
except ImportError as e:
    print(f'❌ Missing Python package: {e}')
    sys.exit(1)
"
    
    if [[ $? -eq 0 ]]; then
        log_success "Python environment test passed"
    else
        log_error "Python environment test failed"
        exit 1
    fi
    
    # Test Node.js (if needed)
    if command -v node >/dev/null; then
        NODE_VERSION=$(node --version)
        log_success "Node.js available: $NODE_VERSION"
    fi
    
    log_success "Installation test completed"
}

# Create desktop launcher (Linux only)
create_desktop_launcher() {
    if [[ "$OS" == "ubuntu" ]] && [[ -n "$XDG_CURRENT_DESKTOP" ]]; then
        read -p "Create desktop launcher? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            INSTALL_DIR=$(pwd)
            cat > ~/.local/share/applications/cryptominer-pro.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=CryptoMiner Pro V30
Comment=Enterprise Mining Platform
Exec=gnome-terminal -- bash -c 'cd "$INSTALL_DIR" && ./start-with-dashboard.sh; exec bash'
Icon=utilities-terminal
Path=$INSTALL_DIR
Terminal=false
Categories=Utility;Network;
EOF
            log_success "Desktop launcher created"
        fi
    fi
}

# Main installation function
main() {
    log_info "Starting CryptoMiner Pro V30 installation..."
    
    # Check prerequisites
    check_root
    detect_os
    
    # Install dependencies
    install_system_deps
    install_nodejs
    setup_python_env
    
    # Setup configuration
    setup_config
    
    # Optional MongoDB
    install_mongodb
    
    # Create scripts
    create_scripts
    
    # Test installation
    test_installation
    
    # Optional desktop launcher
    create_desktop_launcher
    
    echo ""
    echo "🎉 Installation completed successfully!"
    echo "============================================="
    echo ""
    echo "📋 Next Steps:"
    echo "1. Edit mining_config.env with your wallet address"
    echo "2. Run: ./start-with-dashboard.sh"
    echo "3. Open: http://localhost:3000 (Web Dashboard)"
    echo "4. Monitor: http://localhost:8001/docs (API Documentation)"
    echo ""
    echo "🔧 Available Commands:"
    echo "  ./start.sh                 - Start mining only"
    echo "  ./start-with-dashboard.sh  - Start mining + web dashboard" 
    echo "  ./stop.sh                  - Stop all processes"
    echo ""
    echo "📚 Configuration:"
    echo "  mining_config.env          - Main mining configuration"
    echo "  backend/.env               - Backend API configuration"
    echo ""
    echo "🚀 Ready to mine! Edit your configuration and run the start script."
}

# Run main installation
main "$@"