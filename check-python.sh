#!/bin/bash

# 🐍 Python Version Checker & Manager
# Comprehensive Python version detection and management tool

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

print_header() {
    clear
    echo -e "${CYAN}"
    echo "=================================================================="
    echo "          🐍 Python Version Checker & Manager"
    echo "=================================================================="
    echo -e "${NC}"
    echo "Comprehensive Python installation analysis and management"
    echo ""
}

print_section() {
    echo -e "\n${WHITE}$1${NC}"
    echo "$(printf '=%.0s' {1..50})"
}

print_info() {
    echo -e "${BLUE}  ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}  ✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}  ⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}  ❌ $1${NC}"
}

# Check system Python versions
check_system_python() {
    print_section "🔍 System Python Analysis"
    
    # Check default python3
    if command -v python3 &> /dev/null; then
        DEFAULT_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        DEFAULT_PATH=$(which python3)
        print_success "Default Python3: $DEFAULT_VERSION"
        print_info "Location: $DEFAULT_PATH"
        
        # Get detailed version info
        python3 -c "
import sys
import platform
print('  • Platform:', platform.platform())
print('  • Architecture:', platform.architecture()[0])
print('  • Compiler:', platform.python_compiler())
print('  • Implementation:', platform.python_implementation())
print('  • Version info:', sys.version_info)
print('  • Executable:', sys.executable)
"
    else
        print_error "No default python3 found"
    fi
    
    # Check for python (python2)
    if command -v python &> /dev/null; then
        PYTHON2_VERSION=$(python --version 2>&1)
        print_warning "Legacy Python: $PYTHON2_VERSION"
        print_info "Location: $(which python)"
    fi
    
    echo ""
}

# Check all available Python versions
check_available_versions() {
    print_section "📦 Available Python Versions"
    
    echo -e "${BLUE}Checking for installed Python versions...${NC}"
    
    local found_versions=()
    
    # Check common Python versions
    for version in 2.7 3.6 3.7 3.8 3.9 3.10 3.11 3.12 3.13 3.14 3.15; do
        if command -v python$version &> /dev/null; then
            FULL_VERSION=$(python$version --version 2>&1 | cut -d' ' -f2)
            VERSION_PATH=$(which python$version)
            print_success "Python $version: $FULL_VERSION"
            print_info "  └─ Path: $VERSION_PATH"
            found_versions+=("$version:$FULL_VERSION:$VERSION_PATH")
        fi
    done
    
    if [ ${#found_versions[@]} -eq 0 ]; then
        print_warning "No additional Python versions found"
    fi
    
    echo ""
    echo -e "${BLUE}Summary: Found ${#found_versions[@]} additional Python version(s)${NC}"
}

# Check Python packages and tools
check_python_tools() {
    print_section "🛠️  Python Package Managers & Tools"
    
    # Check pip versions
    echo -e "${BLUE}Package Managers:${NC}"
    
    if command -v pip &> /dev/null; then
        PIP_VERSION=$(pip --version 2>/dev/null | cut -d' ' -f2)
        print_success "pip: $PIP_VERSION"
        print_info "  └─ Path: $(which pip)"
    fi
    
    if command -v pip3 &> /dev/null; then
        PIP3_VERSION=$(pip3 --version 2>/dev/null | cut -d' ' -f2)
        print_success "pip3: $PIP3_VERSION"
        print_info "  └─ Path: $(which pip3)"
    fi
    
    # Check for other Python tools
    echo -e "\n${BLUE}Python Development Tools:${NC}"
    
    local tools=("pipenv" "poetry" "conda" "pyenv" "virtualenv" "pipx")
    
    for tool in "${tools[@]}"; do
        if command -v $tool &> /dev/null; then
            if [ "$tool" = "conda" ]; then
                TOOL_VERSION=$(conda --version 2>/dev/null | cut -d' ' -f2)
            elif [ "$tool" = "pyenv" ]; then
                TOOL_VERSION=$(pyenv --version 2>/dev/null | cut -d' ' -f2)
            else
                TOOL_VERSION=$($tool --version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)
            fi
            
            print_success "$tool: ${TOOL_VERSION:-unknown version}"
            print_info "  └─ Path: $(which $tool)"
        fi
    done
}

# Check Python development packages
check_dev_packages() {
    print_section "📚 Python Development Packages"
    
    echo -e "${BLUE}Checking installed development packages...${NC}"
    
    # Check for development packages
    local dev_packages=("python3-dev" "python3-venv" "python3-pip" "python3-setuptools" "python3-wheel")
    
    for package in "${dev_packages[@]}"; do
        if dpkg -l | grep -q "^ii.*$package "; then
            VERSION=$(dpkg -l | grep "^ii.*$package " | awk '{print $3}' | cut -d'-' -f1)
            print_success "$package: $VERSION"
        else
            print_warning "$package: not installed"
        fi
    done
    
    # Check for build essentials
    echo -e "\n${BLUE}Build Tools:${NC}"
    
    local build_tools=("build-essential" "gcc" "make" "cmake")
    
    for tool in "${build_tools[@]}"; do
        if command -v $tool &> /dev/null; then
            if [ "$tool" = "gcc" ]; then
                VERSION=$(gcc --version | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
            elif [ "$tool" = "make" ]; then
                VERSION=$(make --version | head -n1 | grep -oE '[0-9]+\.[0-9]+')
            elif [ "$tool" = "cmake" ]; then
                VERSION=$(cmake --version | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
            else
                VERSION="installed"
            fi
            print_success "$tool: $VERSION"
        elif dpkg -l | grep -q "^ii.*$tool "; then
            VERSION=$(dpkg -l | grep "^ii.*$tool " | awk '{print $3}' | cut -d'-' -f1)
            print_success "$tool: $VERSION (package)"
        else
            print_warning "$tool: not found"
        fi
    done
}

# Check virtual environments
check_virtual_environments() {
    print_section "🏠 Python Virtual Environments"
    
    echo -e "${BLUE}Checking for virtual environments...${NC}"
    
    # Check common venv locations
    local venv_locations=(
        "$HOME/.virtualenvs"
        "$HOME/venvs"
        "$HOME/.local/share/virtualenvs"
        "./venv"
        "./env"
        "./.venv"
    )
    
    local found_venvs=0
    
    for location in "${venv_locations[@]}"; do
        if [ -d "$location" ]; then
            if [ -f "$location/pyvenv.cfg" ]; then
                # Single venv
                PYTHON_VERSION=$(grep "version" "$location/pyvenv.cfg" 2>/dev/null | cut -d'=' -f2 | tr -d ' ')
                print_success "Virtual Environment: $location"
                print_info "  └─ Python Version: $PYTHON_VERSION"
                found_venvs=$((found_venvs + 1))
            else
                # Directory with multiple venvs
                local venv_count=$(find "$location" -name "pyvenv.cfg" 2>/dev/null | wc -l)
                if [ $venv_count -gt 0 ]; then
                    print_success "Virtual Environment Directory: $location"
                    print_info "  └─ Contains $venv_count virtual environment(s)"
                    found_venvs=$((found_venvs + venv_count))
                fi
            fi
        fi
    done
    
    if [ $found_venvs -eq 0 ]; then
        print_info "No virtual environments found in common locations"
    else
        print_info "Total virtual environments found: $found_venvs"
    fi
}

# Analyze Python for specific requirements
analyze_requirements() {
    print_section "⚙️  Requirement Analysis"
    
    echo -e "${BLUE}CryptoMiner Pro Requirements Analysis:${NC}"
    
    # Define requirements
    local MIN_MAJOR=3
    local MIN_MINOR=8
    local PREFERRED_MAJOR=3
    local PREFERRED_MINOR=12
    
    print_info "Minimum required: Python $MIN_MAJOR.$MIN_MINOR+"
    print_info "Preferred version: Python $PREFERRED_MAJOR.$PREFERRED_MINOR+"
    
    if command -v python3 &> /dev/null; then
        # Check minimum requirement
        if python3 -c "import sys; exit(0 if sys.version_info >= ($MIN_MAJOR, $MIN_MINOR) else 1)" 2>/dev/null; then
            print_success "✅ Meets minimum requirements"
            
            # Check preferred version
            if python3 -c "import sys; exit(0 if sys.version_info >= ($PREFERRED_MAJOR, $PREFERRED_MINOR) else 1)" 2>/dev/null; then
                print_success "✅ Meets preferred requirements"
                echo -e "${GREEN}  🎉 Ready for CryptoMiner Pro installation!${NC}"
            else
                print_warning "⚠️  Below preferred version"
                echo -e "${YELLOW}  💡 Consider upgrading to Python $PREFERRED_MAJOR.$PREFERRED_MINOR+ for best performance${NC}"
            fi
        else
            print_error "❌ Below minimum requirements"
            echo -e "${RED}  🚨 Must upgrade Python before installing CryptoMiner Pro${NC}"
        fi
    else
        print_error "❌ No Python 3 installation found"
        echo -e "${RED}  🚨 Must install Python 3 before proceeding${NC}"
    fi
    
    # Check required packages
    echo -e "\n${BLUE}Required Package Analysis:${NC}"
    
    local required_packages=("pip" "venv" "dev")
    local missing_packages=()
    
    for package in "${required_packages[@]}"; do
        case $package in
            "pip")
                if command -v pip3 &> /dev/null; then
                    print_success "pip3: available"
                else
                    print_warning "pip3: missing"
                    missing_packages+=("python3-pip")
                fi
                ;;
            "venv")
                if python3 -c "import venv" 2>/dev/null; then
                    print_success "venv module: available"
                else
                    print_warning "venv module: missing"
                    missing_packages+=("python3-venv")
                fi
                ;;
            "dev")
                if dpkg -l | grep -q "^ii.*python3-dev "; then
                    print_success "development headers: available"
                else
                    print_warning "development headers: missing"
                    missing_packages+=("python3-dev")
                fi
                ;;
        esac
    done
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        echo -e "\n${YELLOW}📝 Missing packages to install:${NC}"
        for package in "${missing_packages[@]}"; do
            echo -e "    ${YELLOW}•${NC} $package"
        done
        
        echo -e "\n${CYAN}💡 Install command:${NC}"
        echo "    sudo apt install ${missing_packages[*]}"
    else
        echo -e "\n${GREEN}✅ All required packages are available!${NC}"
    fi
}

# Generate recommendations
generate_recommendations() {
    print_section "💡 Recommendations"
    
    echo -e "${BLUE}Based on the analysis, here are the recommendations:${NC}"
    echo ""
    
    # Check if deadsnakes PPA would be beneficial
    if command -v python3 &> /dev/null; then
        if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)" 2>/dev/null; then
            echo -e "${YELLOW}🐍 Python Upgrade Recommended:${NC}"
            echo "    • Current version is below Python 3.12"
            echo "    • Consider installing Python 3.12+ via deadsnakes PPA"
            echo "    • Command: sudo add-apt-repository ppa:deadsnakes/ppa"
            echo ""
        fi
    fi
    
    # Check system
    UBUNTU_VERSION=$(lsb_release -rs 2>/dev/null || echo "unknown")
    echo -e "${BLUE}📋 System Information:${NC}"
    echo "    • Ubuntu Version: $UBUNTU_VERSION"
    echo "    • Architecture: $(uname -m)"
    echo "    • Kernel: $(uname -r)"
    echo ""
    
    # Performance recommendations
    echo -e "${GREEN}🚀 Performance Tips:${NC}"
    echo "    • Use Python 3.12+ for best performance"
    echo "    • Install development packages for compiled extensions"
    echo "    • Consider using virtual environments for project isolation"
    echo "    • Keep pip updated: python3 -m pip install --upgrade pip"
    echo ""
    
    # Security recommendations
    echo -e "${CYAN}🔒 Security Best Practices:${NC}"
    echo "    • Regularly update Python and packages"
    echo "    • Use virtual environments for project dependencies"
    echo "    • Verify package integrity when installing from PyPI"
    echo "    • Keep system packages updated"
}

# Main function
main() {
    print_header
    
    check_system_python
    check_available_versions
    check_python_tools
    check_dev_packages
    check_virtual_environments
    analyze_requirements
    generate_recommendations
    
    echo ""
    echo -e "${GREEN}🎯 Analysis Complete!${NC}"
    echo -e "${CYAN}Use this information to determine if your system is ready for Python development.${NC}"
    echo ""
}

# Handle command line arguments
case "${1:-}" in
    "--help"|"-h")
        echo "Python Version Checker & Manager"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h          Show this help message"
        echo "  --versions-only     Show only version information"
        echo "  --requirements      Check requirements only"
        echo "  --recommendations   Show recommendations only"
        echo ""
        echo "This script provides comprehensive Python environment analysis including:"
        echo "  • Installed Python versions and locations"
        echo "  • Package managers and development tools"
        echo "  • Development packages and build tools"
        echo "  • Virtual environment detection"
        echo "  • Requirements analysis for specific projects"
        echo "  • Installation and upgrade recommendations"
        ;;
    "--versions-only")
        print_header
        check_system_python
        check_available_versions
        ;;
    "--requirements")
        print_header
        analyze_requirements
        ;;
    "--recommendations")
        print_header
        generate_recommendations
        ;;
    *)
        main "$@"
        ;;
esac