#!/bin/bash

# Fix pip dependency conflicts for CryptoMiner Pro
# Specifically handles the metadata/hachoir-core conflict

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

# Clean up pip cache and problematic packages
cleanup_pip_environment() {
    log "Cleaning up pip environment..."
    
    if [ -d "venv" ]; then
        source venv/bin/activate
        
        # Clear pip cache
        pip cache purge 2>/dev/null || true
        
        # Uninstall problematic packages if they exist
        local problematic_packages=("metadata" "hachoir-core" "hachoir" "hachoir-parser")
        
        for package in "${problematic_packages[@]}"; do
            if pip list | grep -q "^$package "; then
                log "Uninstalling problematic package: $package"
                pip uninstall -y "$package" 2>/dev/null || true
            fi
        done
        
        success "Pip environment cleaned"
    else
        warning "Virtual environment not found"
    fi
}

# Install packages in optimal order to avoid conflicts
install_packages_step_by_step() {
    log "Installing packages step by step to avoid conflicts..."
    
    if [ ! -d "venv" ]; then
        error "Virtual environment not found. Please run the main setup script first."
        return 1
    fi
    
    source venv/bin/activate
    
    # Upgrade pip and tools
    log "Upgrading pip and build tools..."
    python -m pip install --upgrade pip setuptools wheel
    
    # Step 1: Install build dependencies
    log "Step 1: Installing build dependencies..."
    pip install --prefer-binary --no-cache-dir \
        packaging \
        distlib \
        filelock
    
    # Step 2: Install core web framework
    log "Step 2: Installing web framework..."
    pip install --prefer-binary --no-cache-dir \
        fastapi==0.110.0 \
        uvicorn[standard]==0.27.0 \
        websockets==12.0 \
        python-multipart==0.0.7
    
    # Step 3: Install utility libraries
    log "Step 3: Installing utility libraries..."
    pip install --prefer-binary --no-cache-dir \
        aiofiles==23.2.1 \
        requests==2.31.0 \
        python-dotenv==1.0.0 \
        psutil==5.9.8
    
    # Step 4: Install crypto libraries
    log "Step 4: Installing cryptography libraries..."
    pip install --prefer-binary --no-cache-dir \
        cryptography==42.0.0 \
        base58==2.1.1
    
    # Step 5: Install database libraries
    log "Step 5: Installing database libraries..."
    pip install --prefer-binary --no-cache-dir \
        pymongo==4.6.1 \
        pydantic==2.6.0
    
    # Step 6: Try to install scrypt for mining
    log "Step 6: Installing mining libraries..."
    if ! pip install --prefer-binary --no-cache-dir scrypt==0.8.20; then
        warning "Scrypt installation failed, installing alternative..."
        pip install --prefer-binary --no-cache-dir pycryptodome
    fi
    
    # Step 7: Install AI libraries with careful handling
    log "Step 7: Installing AI/ML libraries..."
    
    # Install numpy first (required by other ML packages)
    if pip install --prefer-binary --no-cache-dir "numpy>=1.24.0,<2.0.0"; then
        success "NumPy installed successfully"
        
        # Try scikit-learn
        if pip install --prefer-binary --no-cache-dir "scikit-learn>=1.3.0,<2.0.0"; then
            success "Scikit-learn installed successfully"
        else
            warning "Scikit-learn installation failed"
        fi
        
        # Try pandas (most problematic)
        log "Attempting pandas installation..."
        if pip install --prefer-binary --no-cache-dir "pandas>=2.1.0,<3.0.0"; then
            success "Pandas installed successfully"
        else
            warning "Pandas installation failed, trying alternative approach..."
            # Try installing pandas dependencies individually first
            pip install --prefer-binary --no-cache-dir pytz python-dateutil six
            
            if pip install --prefer-binary --no-cache-dir --no-deps pandas; then
                success "Pandas installed with --no-deps"
            else
                warning "Pandas completely failed - AI features will be limited"
            fi
        fi
    else
        warning "NumPy installation failed - AI features will not be available"
    fi
    
    # Step 8: Install testing framework
    log "Step 8: Installing testing framework..."
    pip install --prefer-binary --no-cache-dir pytest==8.0.0 || warning "Pytest installation failed"
    
    success "Package installation completed"
}

# Test the installation
test_installation() {
    log "Testing package installation..."
    
    if [ -d "venv" ]; then
        source venv/bin/activate
        
        # Test core packages
        local core_packages=("fastapi" "uvicorn" "pymongo" "cryptography" "psutil")
        local failed_packages=()
        
        for package in "${core_packages[@]}"; do
            if python -c "import $package" 2>/dev/null; then
                success "✅ $package working"
            else
                error "❌ $package failed"
                failed_packages+=("$package")
            fi
        done
        
        # Test AI packages
        local ai_packages=("numpy" "pandas" "sklearn")
        local working_ai=0
        
        for package in "${ai_packages[@]}"; do
            if python -c "import $package" 2>/dev/null; then
                success "✅ $package working"
                ((working_ai++))
            else
                warning "⚠️  $package not available"
            fi
        done
        
        # Test mining-specific packages
        if python -c "import scrypt" 2>/dev/null; then
            success "✅ Scrypt library working"
        elif python -c "import Crypto" 2>/dev/null; then
            success "✅ PyCryptodome working (alternative crypto library)"
        else
            warning "⚠️  No crypto mining library available"
        fi
        
        # Summary
        if [ ${#failed_packages[@]} -eq 0 ]; then
            success "🎉 All core packages are working!"
            log "AI packages working: $working_ai/3"
            log "CryptoMiner Pro is ready to run"
        else
            error "❌ Some core packages failed: ${failed_packages[*]}"
            return 1
        fi
        
    else
        error "Virtual environment not found"
        return 1
    fi
}

# Main function
main() {
    local backend_dir="${1:-./backend}"
    
    log "Starting pip conflict resolution..."
    log "Backend directory: $backend_dir"
    
    if [ ! -d "$backend_dir" ]; then
        error "Backend directory not found: $backend_dir"
        error "Usage: $0 [backend_directory]"
        exit 1
    fi
    
    cd "$backend_dir"
    
    # Step 1: Clean up environment
    cleanup_pip_environment
    
    # Step 2: Install packages carefully
    if install_packages_step_by_step; then
        success "Package installation completed"
    else
        error "Package installation failed"
        exit 1
    fi
    
    # Step 3: Test installation
    if test_installation; then
        success "🎉 Pip conflict resolution completed successfully!"
        log "You can now continue with the main installation script"
    else
        error "Installation test failed"
        exit 1
    fi
}

# Run main function
main "$@"