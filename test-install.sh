#!/bin/bash

# 🧪 CryptoMiner Pro - Installation Test Script
# Tests the automated installer in a controlled environment

set -e

# Configuration
TEST_LOG="/tmp/cryptominer-test.log"
PROJECT_DIR="/opt/cryptominer-pro"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_test_header() {
    echo -e "${BLUE}"
    echo "=================================================================="
    echo "          🧪 CryptoMiner Pro - Installation Tester"
    echo "=================================================================="
    echo -e "${NC}"
    echo "Testing automated installation script functionality"
    echo ""
}

print_test_step() {
    echo -e "\n${YELLOW}🔬 TEST: $1${NC}"
    echo "$(printf '=%.0s' {1..50})"
}

print_success() {
    echo -e "${GREEN}  ✅ $1${NC}"
}

print_error() {
    echo -e "${RED}  ❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}  ℹ️  $1${NC}"
}

# Test system compatibility
test_system_compatibility() {
    print_test_step "System Compatibility"
    
    # Check Ubuntu version
    if grep -q "Ubuntu" /etc/os-release; then
        UBUNTU_VERSION=$(lsb_release -rs)
        print_success "Ubuntu $UBUNTU_VERSION detected"
    else
        print_error "Not running on Ubuntu"
        return 1
    fi
    
    # Check minimum requirements
    TOTAL_RAM=$(free -m | awk '/^Mem:/{print $2}')
    AVAILABLE_DISK=$(df / | awk 'NR==2{print $4}')
    CPU_CORES=$(nproc)
    
    print_info "System Resources:"
    echo "    • CPU Cores: $CPU_CORES"
    echo "    • Total RAM: ${TOTAL_RAM}MB"
    echo "    • Available Disk: $((AVAILABLE_DISK/1024))MB"
    
    if [ "$TOTAL_RAM" -ge 2048 ] && [ "$AVAILABLE_DISK" -ge 2097152 ] && [ "$CPU_CORES" -ge 2 ]; then
        print_success "System meets minimum requirements"
        return 0
    else
        print_error "System does not meet minimum requirements"
        return 1
    fi
}

# Test prerequisites
test_prerequisites() {
    print_test_step "Prerequisites Check"
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        print_error "Test must be run as root/sudo"
        return 1
    fi
    print_success "Running with proper privileges"
    
    # Check internet connection
    if ping -c 1 google.com > /dev/null 2>&1; then
        print_success "Internet connection available"
    else
        print_error "No internet connection"
        return 1
    fi
    
    # Check if installer script exists
    if [ -f "./install-ubuntu.sh" ]; then
        print_success "Installer script found"
    else
        print_error "install-ubuntu.sh not found in current directory"
        return 1
    fi
    
    return 0
}

# Test script syntax
test_script_syntax() {
    print_test_step "Script Syntax Validation"
    
    # Check bash syntax
    if bash -n ./install-ubuntu.sh; then
        print_success "Installer script syntax is valid"
    else
        print_error "Installer script has syntax errors"
        return 1
    fi
    
    # Check if script is executable
    if [ -x "./install-ubuntu.sh" ]; then
        print_success "Script is executable"
    else
        print_error "Script is not executable"
        return 1
    fi
    
    return 0
}

# Test dry run capabilities
test_dry_run() {
    print_test_step "Dry Run Test"
    
    print_info "Testing installer help and version options"
    
    # Test help option
    if ./install-ubuntu.sh --help > /dev/null 2>&1; then
        print_success "Help option works correctly"
    else
        print_error "Help option failed"
        return 1
    fi
    
    # Test version option
    if ./install-ubuntu.sh --version > /dev/null 2>&1; then
        print_success "Version option works correctly"
    else
        print_error "Version option failed"
        return 1
    fi
    
    return 0
}

# Test dependency availability
test_dependency_availability() {
    print_test_step "Dependency Availability"
    
    print_info "Testing if required packages are available in repositories"
    
    # Update package lists
    apt update > "$TEST_LOG" 2>&1
    
    # Check Node.js repository availability
    if curl -fsSL https://deb.nodesource.com/setup_20.x > /dev/null 2>&1; then
        print_success "NodeSource repository accessible"
    else
        print_error "NodeSource repository not accessible"
        return 1
    fi
    
    # Check MongoDB repository availability
    if curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc > /dev/null 2>&1; then
        print_success "MongoDB repository accessible"
    else
        print_error "MongoDB repository not accessible"
        return 1
    fi
    
    # Check essential packages
    ESSENTIAL_PACKAGES="curl wget gnupg2 software-properties-common build-essential python3-dev python3-pip supervisor"
    
    for package in $ESSENTIAL_PACKAGES; do
        if apt-cache show "$package" > /dev/null 2>&1; then
            print_success "Package '$package' available"
        else
            print_error "Package '$package' not available"
            return 1
        fi
    done
    
    return 0
}

# Test directory permissions
test_directory_permissions() {
    print_test_step "Directory Permissions"
    
    # Test if we can create the project directory
    if mkdir -p "$PROJECT_DIR/test" 2>/dev/null; then
        print_success "Can create project directory"
        rm -rf "$PROJECT_DIR/test"
    else
        print_error "Cannot create project directory"
        return 1
    fi
    
    # Test if we can write supervisor config
    TEST_SUPERVISOR_CONFIG="/etc/supervisor/conf.d/test-cryptominer.conf"
    if echo "# Test config" > "$TEST_SUPERVISOR_CONFIG" 2>/dev/null; then
        print_success "Can write supervisor configuration"
        rm -f "$TEST_SUPERVISOR_CONFIG"
    else
        print_error "Cannot write supervisor configuration"
        return 1
    fi
    
    return 0
}

# Test uninstaller
test_uninstaller() {
    print_test_step "Uninstaller Script"
    
    if [ -f "./uninstall-ubuntu.sh" ]; then
        print_success "Uninstaller script found"
        
        # Check syntax
        if bash -n ./uninstall-ubuntu.sh; then
            print_success "Uninstaller script syntax is valid"
        else
            print_error "Uninstaller script has syntax errors"
            return 1
        fi
        
        # Test help option
        if ./uninstall-ubuntu.sh --help > /dev/null 2>&1; then
            print_success "Uninstaller help option works"
        else
            print_error "Uninstaller help option failed"
            return 1
        fi
        
    else
        print_error "Uninstaller script not found"
        return 1
    fi
    
    return 0
}

# Generate test report
generate_test_report() {
    print_test_step "Test Report Generation"
    
    REPORT_FILE="/tmp/cryptominer-test-report.txt"
    
    cat > "$REPORT_FILE" << EOF
CryptoMiner Pro Installation Test Report
Generated: $(date)
System: $(lsb_release -d | cut -f2)
Hardware: $(nproc) cores, $(free -m | awk '/^Mem:/{print $2}')MB RAM

Test Results:
=============
EOF
    
    # Add test results to report
    echo "System Compatibility: PASSED" >> "$REPORT_FILE"
    echo "Prerequisites: PASSED" >> "$REPORT_FILE"  
    echo "Script Syntax: PASSED" >> "$REPORT_FILE"
    echo "Dry Run: PASSED" >> "$REPORT_FILE"
    echo "Dependencies: PASSED" >> "$REPORT_FILE"
    echo "Permissions: PASSED" >> "$REPORT_FILE"
    echo "Uninstaller: PASSED" >> "$REPORT_FILE"
    
    print_success "Test report generated: $REPORT_FILE"
    
    # Display summary
    echo ""
    echo -e "${GREEN}📊 TEST SUMMARY${NC}"
    echo "=================="
    echo "✅ All installation pre-checks passed"
    echo "✅ System is ready for automated installation"
    echo "✅ Installer and uninstaller scripts are functional"
    echo ""
    echo -e "${BLUE}💡 Next Steps:${NC}"
    echo "• Run the actual installation: sudo ./install-ubuntu.sh"
    echo "• Monitor installation progress and logs"
    echo "• Test the application after installation"
    echo ""
}

# Main test function
main() {
    print_test_header
    
    # Run all tests
    local test_failed=0
    
    test_system_compatibility || test_failed=1
    test_prerequisites || test_failed=1
    test_script_syntax || test_failed=1
    test_dry_run || test_failed=1
    test_dependency_availability || test_failed=1
    test_directory_permissions || test_failed=1
    test_uninstaller || test_failed=1
    
    if [ $test_failed -eq 0 ]; then
        generate_test_report
        echo -e "${GREEN}🎉 ALL TESTS PASSED! System is ready for installation.${NC}"
        exit 0
    else
        echo -e "${RED}❌ Some tests failed. Please resolve issues before installation.${NC}"
        exit 1
    fi
}

# Handle command line arguments
case "${1:-}" in
    "--help"|"-h")
        echo "CryptoMiner Pro Installation Tester"
        echo ""
        echo "Usage: sudo $0"
        echo ""
        echo "This script tests if your system is ready for CryptoMiner Pro installation."
        echo ""
        echo "Tests performed:"
        echo "  • System compatibility (Ubuntu version, resources)"
        echo "  • Prerequisites (permissions, internet connectivity)"
        echo "  • Script syntax validation"
        echo "  • Repository availability"
        echo "  • Directory permissions"
        echo "  • Uninstaller functionality"
        ;;
    *)
        main "$@"
        ;;
esac