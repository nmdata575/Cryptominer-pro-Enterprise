#!/bin/bash

# Fix for Ubuntu Development Versions (like "plucky" 25.04)
# Handles PPA issues and Python version compatibility

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

# Clean up broken deadsnakes PPA configuration
cleanup_broken_ppa() {
    log "Cleaning up broken PPA configurations..."
    
    # Remove deadsnakes PPA files
    sudo rm -f /etc/apt/sources.list.d/deadsnakes-ubuntu-ppa-*.list
    
    # Remove any GPG keys
    sudo rm -f /usr/share/keyrings/deadsnakes*.gpg
    
    # Clean apt cache
    sudo apt clean
    sudo apt update
    
    success "Cleaned up broken PPA configurations"
}

# Install Python without PPAs
install_python_from_standard_repos() {
    log "Attempting to install Python from standard Ubuntu repositories..."
    
    sudo apt update
    
    # Try to install available Python versions
    local python_versions=("python3.12" "python3.11" "python3.10")
    
    for py_version in "${python_versions[@]}"; do
        log "Checking availability of $py_version..."
        
        if apt-cache show $py_version &>/dev/null; then
            log "Installing $py_version and related packages..."
            
            if sudo apt install -y \
                $py_version \
                ${py_version}-venv \
                ${py_version}-dev \
                ${py_version}-distutils; then
                
                success "$py_version installed successfully from standard repositories"
                echo "export PYTHON_CMD=\"$py_version\"" > /tmp/python_version
                return 0
            else
                warning "$py_version installation failed"
            fi
        else
            log "$py_version not available in standard repositories"
        fi
    done
    
    # If no specific version worked, try the default python3
    if command -v python3 &>/dev/null; then
        local py_version=$(python3 --version | cut -d' ' -f2)
        log "Using system default Python $py_version"
        
        # Install venv and dev packages for system python
        sudo apt install -y python3-venv python3-dev python3-pip python3-distutils-extra
        
        echo "export PYTHON_CMD=\"python3\"" > /tmp/python_version
        success "Using system Python $py_version"
        return 0
    fi
    
    error "No suitable Python version could be installed"
    return 1
}

# Install additional build dependencies for Python 3.13 compatibility
install_build_dependencies() {
    log "Installing build dependencies for Python compilation compatibility..."
    
    sudo apt install -y \
        build-essential \
        python3-dev \
        python3-pip \
        python3-venv \
        python3-wheel \
        libffi-dev \
        libssl-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        libncurses5-dev \
        libgdbm-dev \
        liblzma-dev \
        uuid-dev \
        zlib1g-dev \
        pkg-config \
        gcc \
        g++ \
        make
    
    success "Build dependencies installed"
}

# Create Python 3.13 compatible requirements
create_compatible_requirements() {
    log "Creating Python 3.13 compatible requirements..."
    
    local backend_dir="${1:-./backend}"
    
    if [ ! -d "$backend_dir" ]; then
        warning "Backend directory not found: $backend_dir"
        return 1
    fi
    
    # Create backup of original requirements
    if [ -f "$backend_dir/requirements.txt" ]; then
        cp "$backend_dir/requirements.txt" "$backend_dir/requirements.txt.backup"
    fi
    
    # Create minimal compatible requirements
    cat > "$backend_dir/requirements-dev.txt" << 'EOF'
# CryptoMiner Pro - Development Ubuntu Compatible Dependencies
# Minimal set for Ubuntu development versions

# FastAPI and Web Framework
fastapi==0.110.0
uvicorn[standard]==0.27.0
websockets==12.0
python-multipart==0.0.7
aiofiles==23.2.1

# Cryptography and Mining
cryptography==42.0.0
base58==2.1.1

# Database and Storage
pymongo==4.6.1

# System and Utilities
psutil==5.9.8
requests==2.31.0
python-dotenv==1.0.0
pydantic==2.6.0

# Development and Testing
pytest==8.0.0
EOF
    
    success "Created development-compatible requirements"
}

# Main function
main() {
    local ubuntu_version=$(lsb_release -cs 2>/dev/null || echo "unknown")
    
    log "Ubuntu Development Version Fix Script"
    log "Detected Ubuntu version: $ubuntu_version"
    
    case "$ubuntu_version" in
        "plucky"|"25.04"|"oracular"|"24.10")
            warning "Ubuntu development version detected: $ubuntu_version"
            log "This version may not be supported by third-party PPAs"
            ;;
        *)
            log "This script is designed for Ubuntu development versions"
            log "Your version ($ubuntu_version) may not need these fixes"
            ;;
    esac
    
    # Step 1: Clean up any broken PPA configurations
    cleanup_broken_ppa
    
    # Step 2: Install build dependencies
    install_build_dependencies
    
    # Step 3: Install Python from standard repositories
    if install_python_from_standard_repos; then
        success "Python installation completed"
    else
        error "Python installation failed"
        exit 1
    fi
    
    # Step 4: Create compatible requirements
    create_compatible_requirements "${1:-./backend}"
    
    success "Ubuntu development version fixes applied successfully!"
    log ""
    log "Next steps:"
    log "1. Run the main installation script: sudo ./local-setup.sh"
    log "2. If Python packages fail, the script will use fallback methods"
    log "3. Core mining functionality should work even if some AI features are limited"
    
    if [ -f /tmp/python_version ]; then
        source /tmp/python_version
        log "Python command to use: $PYTHON_CMD"
    fi
}

# Run main function
main "$@"