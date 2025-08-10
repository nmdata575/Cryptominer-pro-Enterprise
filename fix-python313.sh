#!/bin/bash

# CryptoMiner Pro - Python 3.13 Compatibility Fix Script

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

# Check Python version
check_python_version() {
    log "Checking Python version..."
    
    local python_version=$(python3 --version | cut -d' ' -f2)
    local major_version=$(echo $python_version | cut -d'.' -f1)
    local minor_version=$(echo $python_version | cut -d'.' -f2)
    
    log "Detected Python $python_version"
    
    if [ "$major_version" = "3" ] && [ "$minor_version" = "13" ]; then
        warning "Python 3.13 detected - applying compatibility fixes"
        return 0
    elif [ "$major_version" = "3" ] && [ "$minor_version" -ge "11" ]; then
        log "Python $python_version should work fine"
        return 1
    else
        error "Python version $python_version may not be compatible"
        error "Recommended: Python 3.11 or 3.12"
        return 2
    fi
}

# Install system dependencies for Python 3.13 compilation
install_build_dependencies() {
    log "Installing build dependencies for Python 3.13..."
    
    sudo apt update
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
    
    local backend_dir="$1"
    if [ -z "$backend_dir" ]; then
        backend_dir="./backend"
    fi
    
    # Create a backup of original requirements
    if [ -f "$backend_dir/requirements.txt" ]; then
        cp "$backend_dir/requirements.txt" "$backend_dir/requirements.txt.backup"
    fi
    
    # Create new compatible requirements
    cat > "$backend_dir/requirements-py313.txt" << 'EOF'
# CryptoMiner Pro - Python 3.13 Compatible Dependencies
# Using pre-compiled wheels where possible

# FastAPI and Web Framework
fastapi==0.110.0
uvicorn[standard]==0.27.0
websockets==12.0
python-multipart==0.0.7
aiofiles==23.2.1

# Cryptography and Mining
cryptography==42.0.0
base58==2.1.1

# AI and Machine Learning (using pre-compiled wheels)
numpy>=1.26.0,<2.0.0
scikit-learn>=1.4.0,<2.0.0

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
    
    success "Created Python 3.13 compatible requirements"
}

# Install packages with pip options optimized for Python 3.13
install_packages_py313() {
    local backend_dir="$1"
    if [ -z "$backend_dir" ]; then
        backend_dir="./backend"
    fi
    
    log "Installing packages with Python 3.13 optimizations..."
    
    cd "$backend_dir"
    
    # Activate virtual environment if it exists
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        log "Activated virtual environment"
    else
        error "Virtual environment not found at $backend_dir/venv"
        return 1
    fi
    
    # Upgrade pip and build tools first
    pip install --upgrade pip setuptools wheel
    
    # Install packages with specific options for Python 3.13
    log "Installing core dependencies..."
    pip install --prefer-binary --no-cache-dir -r requirements-py313.txt
    
    # Try to install pandas separately with fallback options
    log "Installing pandas with fallback options..."
    if ! pip install --prefer-binary --no-cache-dir "pandas>=2.1.0,<3.0.0"; then
        warning "Failed to install pandas with binary wheel, trying without pandas..."
        log "CryptoMiner Pro will work without pandas (AI features may be limited)"
    fi
    
    # Try to install scrypt separately
    log "Installing scrypt mining library..."
    if ! pip install --prefer-binary --no-cache-dir scrypt==0.8.20; then
        warning "Failed to install scrypt library, trying alternative..."
        pip install --prefer-binary --no-cache-dir pycryptodome
    fi
    
    success "Package installation completed"
}

# Install alternative packages if main ones fail
install_alternatives() {
    log "Installing alternative packages for failed dependencies..."
    
    # Check if pandas is available
    if ! python -c "import pandas" 2>/dev/null; then
        warning "Pandas not available - installing minimal alternative"
        # For basic data handling, we can use built-in libraries
        log "AI features will use built-in Python libraries instead of pandas"
    fi
    
    # Check if scrypt is available
    if ! python -c "import scrypt" 2>/dev/null; then
        warning "Scrypt library not available - trying alternative crypto libraries"
        pip install --prefer-binary --no-cache-dir pycryptodome cryptography
    fi
    
    success "Alternative packages installed"
}

# Test the installation
test_installation() {
    log "Testing Python package installation..."
    
    local test_script=$(cat << 'EOF'
import sys
print(f"Python version: {sys.version}")

# Test core dependencies
try:
    import fastapi
    print("✅ FastAPI available")
except ImportError:
    print("❌ FastAPI missing")

try:
    import uvicorn
    print("✅ Uvicorn available")
except ImportError:
    print("❌ Uvicorn missing")

try:
    import pymongo
    print("✅ PyMongo available")
except ImportError:
    print("❌ PyMongo missing")

try:
    import numpy
    print("✅ NumPy available")
except ImportError:
    print("❌ NumPy missing")

try:
    import pandas
    print("✅ Pandas available")
except ImportError:
    print("⚠️  Pandas missing (AI features limited)")

try:
    import scrypt
    print("✅ Scrypt available")
except ImportError:
    print("⚠️  Scrypt missing (using alternative crypto)")

try:
    import cryptography
    print("✅ Cryptography available")
except ImportError:
    print("❌ Cryptography missing")

print("✅ Installation test completed")
EOF
)
    
    python -c "$test_script"
}

# Main function
main() {
    local backend_dir="$1"
    
    log "Starting Python 3.13 compatibility fix..."
    
    if check_python_version; then
        log "Applying Python 3.13 specific fixes..."
        install_build_dependencies
        create_compatible_requirements "$backend_dir"
        install_packages_py313 "$backend_dir"
        install_alternatives
        test_installation
        
        success "Python 3.13 compatibility fix completed!"
        warning "Note: Some AI features may be limited due to pandas compatibility issues"
        log "Core mining functionality will work normally"
    else
        log "No Python 3.13 specific fixes needed"
        return 0
    fi
}

# Check if backend directory is provided
backend_dir="${1:-./backend}"

if [ ! -d "$backend_dir" ]; then
    error "Backend directory not found: $backend_dir"
    error "Usage: $0 [backend_directory]"
    error "Example: $0 ./backend"
    exit 1
fi

main "$backend_dir"