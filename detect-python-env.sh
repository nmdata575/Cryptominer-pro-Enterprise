#!/bin/bash

# 🐍 Python Environment Detector
# Detects Python environment management type and provides appropriate setup

detect_python_env() {
    echo "🔍 Python Environment Analysis"
    echo "==============================="
    echo ""
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        echo "✅ Python Version: $PYTHON_VERSION"
        
        # Check if externally managed
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
            echo "📋 Environment Type: Externally Managed (PEP 668)"
            echo "   This is common in Ubuntu 24.04+ with Python 3.11+"
            
            # Test if pip install works
            if python3 -m pip install --help >/dev/null 2>&1; then
                echo "🔧 Pip Status: Available but restricted"
                
                # Try a test install to see the error
                TEST_OUTPUT=$(python3 -m pip install --upgrade pip 2>&1 || true)
                if echo "$TEST_OUTPUT" | grep -q "externally-managed-environment"; then
                    echo "⚠️  System Protection: Active (externally-managed-environment)"
                    echo ""
                    echo "💡 Recommended Solutions:"
                    echo "   1. Use virtual environments: python3 -m venv myproject"
                    echo "   2. Use system packages: apt install python3-package-name"
                    echo "   3. Use --break-system-packages (not recommended)"
                    echo ""
                else
                    echo "✅ Pip Install: Working normally"
                fi
            else
                echo "❌ Pip Status: Not available"
            fi
        else
            echo "📋 Environment Type: Traditional (pip install allowed)"
            echo "✅ System Protection: Not active"
        fi
    else
        echo "❌ Python 3: Not found"
        return 1
    fi
    
    echo ""
    echo "📦 Package Management Recommendations:"
    echo "======================================"
    
    # Check virtual environment support
    if python3 -c "import venv" 2>/dev/null; then
        echo "✅ Virtual Environment: Supported"
        echo "   Command: python3 -m venv project_name"
    else
        echo "❌ Virtual Environment: Not available"
        echo "   Install: sudo apt install python3-venv"
    fi
    
    # Check available system packages
    echo ""
    echo "📋 Common System Packages Available:"
    
    local packages=("python3-pip" "python3-venv" "python3-dev" "python3-setuptools" "python3-wheel")
    for package in "${packages[@]}"; do
        if dpkg -l | grep -q "^ii.*$package "; then
            echo "   ✅ $package (installed)"
        elif apt-cache show "$package" &>/dev/null; then
            echo "   📦 $package (available)"
        else
            echo "   ❌ $package (not found)"
        fi
    done
}

# Show virtual environment setup example
show_venv_setup() {
    echo ""
    echo "🏗️  Virtual Environment Setup Example:"
    echo "======================================"
    echo ""
    echo "# Create a virtual environment"
    echo "python3 -m venv cryptominer-env"
    echo ""
    echo "# Activate it"
    echo "source cryptominer-env/bin/activate"
    echo ""
    echo "# Upgrade pip (now safe to do)"
    echo "pip install --upgrade pip"
    echo ""
    echo "# Install packages"
    echo "pip install fastapi uvicorn pymongo"
    echo ""
    echo "# Deactivate when done"
    echo "deactivate"
}

# Show system package approach
show_system_approach() {
    echo ""
    echo "📦 System Package Approach:"
    echo "=========================="
    echo ""
    echo "# Install packages via apt (recommended for system services)"
    echo "sudo apt install python3-pip python3-venv python3-dev"
    echo "sudo apt install python3-fastapi python3-uvicorn"  # if available
    echo ""
    echo "# For packages not in apt, use virtual environments"
}

# Main execution
main() {
    detect_python_env
    
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
        show_venv_setup
        show_system_approach
        
        echo ""
        echo "💡 For CryptoMiner Pro Installation:"
        echo "   The installer will automatically handle this by creating"
        echo "   a virtual environment in /opt/cryptominer-pro/venv/"
    fi
}

# Handle arguments
case "${1:-}" in
    "--help"|"-h")
        echo "Python Environment Detector"
        echo ""
        echo "Usage: $0"
        echo ""
        echo "This script analyzes your Python environment and provides"
        echo "recommendations for package installation methods."
        ;;
    *)
        main "$@"
        ;;
esac