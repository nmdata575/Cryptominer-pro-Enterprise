#!/bin/bash

# 🐍 Simple Python Version Functions
# Include these functions in any script that needs Python version checking

# Simple function to check current Python version
check_python_version() {
    if command -v python3 &> /dev/null; then
        local version=$(python3 --version 2>&1 | cut -d' ' -f2)
        echo "Python $version"
        return 0
    else
        echo "No Python 3 found"
        return 1
    fi
}

# Function to check if Python meets minimum version requirement
python_meets_requirement() {
    local required_major=${1:-3}
    local required_minor=${2:-8}
    
    if ! command -v python3 &> /dev/null; then
        echo "Python 3 not found"
        return 1
    fi
    
    if python3 -c "import sys; exit(0 if sys.version_info >= ($required_major, $required_minor) else 1)" 2>/dev/null; then
        local current_version=$(python3 --version 2>&1 | cut -d' ' -f2)
        echo "✅ Python $current_version meets requirement $required_major.$required_minor+"
        return 0
    else
        local current_version=$(python3 --version 2>&1 | cut -d' ' -f2)
        echo "❌ Python $current_version below requirement $required_major.$required_minor+"
        return 1
    fi
}

# Function to get detailed Python info
get_python_info() {
    if ! command -v python3 &> /dev/null; then
        echo "No Python 3 installation found"
        return 1
    fi
    
    echo "=== Python Information ==="
    echo "Version: $(python3 --version)"
    echo "Path: $(which python3)"
    echo "Pip: $(python3 -m pip --version 2>/dev/null | cut -d' ' -f2 || echo 'Not available')"
    
    python3 -c "
import sys
print(f'Major.Minor: {sys.version_info.major}.{sys.version_info.minor}')
print(f'Full Version: {sys.version_info}')
print(f'Executable: {sys.executable}')
print(f'Platform: {sys.platform}')
" 2>/dev/null || echo "Could not get detailed info"
}

# Function to list all available Python versions
list_python_versions() {
    echo "=== Available Python Versions ==="
    
    local found=0
    
    # Check default python3
    if command -v python3 &> /dev/null; then
        echo "python3: $(python3 --version 2>&1 | cut -d' ' -f2)"
        found=1
    fi
    
    # Check specific versions
    for version in 3.8 3.9 3.10 3.11 3.12 3.13; do
        if command -v python$version &> /dev/null; then
            echo "python$version: $(python$version --version 2>&1 | cut -d' ' -f2)"
            found=1
        fi
    done
    
    if [ $found -eq 0 ]; then
        echo "No Python installations found"
        return 1
    fi
    
    return 0
}

# Function to verify Python development environment
verify_python_dev_env() {
    echo "=== Python Development Environment Check ==="
    
    local issues=0
    
    # Check Python
    if command -v python3 &> /dev/null; then
        echo "✅ Python 3: $(python3 --version 2>&1 | cut -d' ' -f2)"
    else
        echo "❌ Python 3: Not found"
        issues=$((issues + 1))
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null || python3 -m pip --version &> /dev/null; then
        local pip_version=$(python3 -m pip --version 2>/dev/null | cut -d' ' -f2 || pip3 --version | cut -d' ' -f2)
        echo "✅ pip: $pip_version"
    else
        echo "❌ pip: Not found"
        issues=$((issues + 1))
    fi
    
    # Check venv
    if python3 -c "import venv" 2>/dev/null; then
        echo "✅ venv: Available"
    else
        echo "❌ venv: Not available"
        issues=$((issues + 1))
    fi
    
    # Check development headers
    if dpkg -l | grep -q "^ii.*python3-dev "; then
        echo "✅ python3-dev: Installed"
    else
        echo "❌ python3-dev: Not installed"
        issues=$((issues + 1))
    fi
    
    if [ $issues -eq 0 ]; then
        echo "🎉 Python development environment is complete!"
        return 0
    else
        echo "⚠️  Found $issues issue(s) in Python development environment"
        return 1
    fi
}

# Quick one-liner version check
python_version_oneliner() {
    python3 -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null || echo "Python not available"
}

# Example usage function
example_usage() {
    echo "=== Python Version Functions Example Usage ==="
    echo ""
    
    echo "1. Quick version check:"
    echo "   $(check_python_version)"
    echo ""
    
    echo "2. Check if meets requirement (Python 3.8+):"
    echo "   $(python_meets_requirement 3 8)"
    echo ""
    
    echo "3. Check if meets requirement (Python 3.12+):"
    echo "   $(python_meets_requirement 3 12)"
    echo ""
    
    echo "4. One-liner version:"
    echo "   $(python_version_oneliner)"
    echo ""
    
    echo "5. Development environment check:"
    verify_python_dev_env
    echo ""
    
    echo "6. List all versions:"
    list_python_versions
    echo ""
    
    echo "7. Detailed info:"
    get_python_info
}

# If script is run directly, show example usage
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    example_usage
fi