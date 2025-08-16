#!/bin/bash

# CryptoMiner Pro V30 - Comprehensive Dependency Checker
# Verifies all required dependencies before installation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Counters
AVAILABLE_DEPS=0
MISSING_DEPS=0
OUTDATED_DEPS=0

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

log_success() {
    echo -e "${GREEN}[AVAILABLE] ✅ $1${NC}"
    AVAILABLE_DEPS=$((AVAILABLE_DEPS + 1))
}

log_warning() {
    echo -e "${YELLOW}[OUTDATED] ⚠️  $1${NC}"
    OUTDATED_DEPS=$((OUTDATED_DEPS + 1))
}

log_error() {
    echo -e "${RED}[MISSING] ❌ $1${NC}"
    MISSING_DEPS=$((MISSING_DEPS + 1))
}

log_step() {
    echo -e "${PURPLE}[CHECK] 🔍 $1${NC}"
}

# Version comparison function
version_compare() {
    local version1="$1"
    local version2="$2"
    local operator="$3"
    
    # Remove 'v' prefix if present
    version1=${version1#v}
    version2=${version2#v}
    
    case "$operator" in
        ">=")
            [ "$(printf '%s\n' "$version1" "$version2" | sort -V | head -n1)" = "$version2" ]
            ;;
        ">")
            [ "$version1" != "$version2" ] && [ "$(printf '%s\n' "$version1" "$version2" | sort -V | tail -n1)" = "$version1" ]
            ;;
        "="|"==")
            [ "$version1" = "$version2" ]
            ;;
        *)
            return 1
            ;;
    esac
}

# Check system packages
check_system_packages() {
    log_step "Checking system packages..."
    
    local packages=(
        "curl:curl --version:7.68.0:>="
        "wget:wget --version:1.20:>="
        "git:git --version:2.25:>="
        "build-essential:gcc --version:9.0:>="
        "cmake:cmake --version:3.16:>="
        "pkg-config:pkg-config --version:0.29:>="
        "supervisor:supervisord --version:4.1:>="
        "nginx:nginx -v:1.18:>="
        "jq:jq --version:1.6:>="
        "openssl:openssl version:1.1:>="
    )
    
    for package_info in "${packages[@]}"; do
        IFS=':' read -r package command min_version operator <<< "$package_info"
        
        if command -v "${command%% *}" &> /dev/null; then
            local version_output=$($command 2>&1 | head -1)
            local version=$(echo "$version_output" | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1)
            
            if [ -n "$version" ]; then
                if version_compare "$version" "$min_version" "$operator"; then
                    log_success "$package: $version (meets requirement $operator $min_version)"
                else
                    log_warning "$package: $version (requires $operator $min_version)"
                fi
            else
                log_success "$package: installed (version detection failed)"
            fi
        else
            log_error "$package: not installed"
        fi
    done
}

# Check Python and dependencies
check_python_environment() {
    log_step "Checking Python environment..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        local python_version=$(python3 --version | cut -d' ' -f2)
        if version_compare "$python_version" "3.8.0" ">="; then
            log_success "Python: $python_version (compatible)"
        else
            log_error "Python: $python_version (requires >= 3.8.0)"
        fi
    else
        log_error "Python 3: not installed"
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        local pip_version=$(pip3 --version | cut -d' ' -f2)
        log_success "pip: $pip_version"
    else
        log_error "pip3: not installed"
    fi
    
    # Check venv module
    if python3 -c "import venv" 2>/dev/null; then
        log_success "Python venv module: available"
    else
        log_error "Python venv module: not available"
    fi
    
    # Check if we can create virtual environments
    local temp_venv="/tmp/test_venv_$$"
    if python3 -m venv "$temp_venv" 2>/dev/null; then
        log_success "Virtual environment creation: working"
        rm -rf "$temp_venv"
    else
        log_error "Virtual environment creation: failed"
    fi
}

# Check Node.js and npm ecosystem
check_nodejs_ecosystem() {
    log_step "Checking Node.js ecosystem..."
    
    # Check Node.js
    if command -v node &> /dev/null; then
        local node_version=$(node --version)
        if version_compare "${node_version#v}" "16.0.0" ">="; then
            log_success "Node.js: $node_version (compatible)"
        else
            log_warning "Node.js: $node_version (recommended >= 16.0.0)"
        fi
    else
        log_error "Node.js: not installed"
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        local npm_version=$(npm --version)
        log_success "npm: $npm_version"
    else
        log_error "npm: not installed"
    fi
    
    # Check Yarn
    if command -v yarn &> /dev/null; then
        local yarn_version=$(yarn --version)
        log_success "Yarn: $yarn_version"
    else
        log_error "Yarn: not installed (will be installed during setup)"
    fi
    
    # Check if we can install packages globally
    if npm list -g --depth=0 &> /dev/null; then
        log_success "Global npm package access: available"
    else
        log_warning "Global npm package access: may require sudo"
    fi
}

# Check MongoDB
check_mongodb() {
    log_step "Checking MongoDB..."
    
    # Check MongoDB installation
    if command -v mongod &> /dev/null; then
        local mongo_version=$(mongod --version | head -1 | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        if [ -n "$mongo_version" ]; then
            if version_compare "${mongo_version#v}" "4.4.0" ">="; then
                log_success "MongoDB: $mongo_version (compatible)"
            else
                log_warning "MongoDB: $mongo_version (recommended >= 4.4.0)"
            fi
        else
            log_success "MongoDB: installed (version detection failed)"
        fi
    else
        log_error "MongoDB: not installed"
    fi
    
    # Check MongoDB client tools
    if command -v mongosh &> /dev/null; then
        local mongosh_version=$(mongosh --version | head -1)
        log_success "MongoDB Shell (mongosh): available"
    elif command -v mongo &> /dev/null; then
        log_success "MongoDB Shell (legacy mongo): available"
    else
        log_warning "MongoDB Shell: not available (will be installed with MongoDB)"
    fi
    
    # Check if MongoDB service exists
    if systemctl list-unit-files | grep -q "mongod.service"; then
        log_success "MongoDB systemd service: configured"
    else
        log_warning "MongoDB systemd service: not configured (will be set up)"
    fi
}

# Check development libraries
check_development_libraries() {
    log_step "Checking development libraries..."
    
    local dev_packages=(
        "python3-dev:python3-config --ldflags"
        "libssl-dev:pkg-config --exists openssl"
        "libffi-dev:pkg-config --exists libffi"
        "libcrypto++-dev:pkg-config --exists libcrypto++"
        "build-essential:gcc --version"
    )
    
    for package_info in "${dev_packages[@]}"; do
        IFS=':' read -r package test_command <<< "$package_info"
        
        if eval "$test_command" &> /dev/null; then
            log_success "$package: available"
        else
            log_error "$package: not available"
        fi
    done
}

# Check system resources
check_system_resources() {
    log_step "Checking system resources..."
    
    # Check memory
    local total_memory=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    local available_memory=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    
    if [ "$total_memory" -ge 4096 ]; then
        log_success "Total memory: ${total_memory}MB (excellent)"
    elif [ "$total_memory" -ge 2048 ]; then
        log_warning "Total memory: ${total_memory}MB (minimum met)"
    else
        log_error "Total memory: ${total_memory}MB (insufficient, minimum 2GB required)"
    fi
    
    if [ "$available_memory" -ge 2048 ]; then
        log_success "Available memory: ${available_memory}MB (sufficient)"
    else
        log_warning "Available memory: ${available_memory}MB (may affect performance)"
    fi
    
    # Check disk space
    local available_space=$(df "$HOME" | awk 'NR==2{printf "%.0f", $4/1024}')
    
    if [ "$available_space" -ge 20480 ]; then
        log_success "Available disk space: ${available_space}MB (excellent)"
    elif [ "$available_space" -ge 10240 ]; then
        log_warning "Available disk space: ${available_space}MB (sufficient)"
    else
        log_error "Available disk space: ${available_space}MB (insufficient, minimum 10GB required)"
    fi
    
    # Check CPU cores
    local cpu_cores=$(nproc)
    
    if [ "$cpu_cores" -ge 4 ]; then
        log_success "CPU cores: $cpu_cores (excellent for mining)"
    elif [ "$cpu_cores" -ge 2 ]; then
        log_warning "CPU cores: $cpu_cores (sufficient)"
    else
        log_error "CPU cores: $cpu_cores (mining performance will be limited)"
    fi
}

# Check network connectivity
check_network_connectivity() {
    log_step "Checking network connectivity..."
    
    local test_hosts=(
        "google.com:Google (general connectivity)"
        "github.com:GitHub (source repositories)"
        "registry.npmjs.org:npm registry"
        "pypi.org:Python Package Index"
        "repo.mongodb.org:MongoDB repository"
    )
    
    for host_info in "${test_hosts[@]}"; do
        IFS=':' read -r host description <<< "$host_info"
        
        if ping -c 1 -W 5 "$host" &> /dev/null; then
            log_success "Network connectivity to $description: available"
        else
            log_error "Network connectivity to $description: failed"
        fi
    done
}

# Check specific Python packages that might need compilation
check_python_compilation_deps() {
    log_step "Checking Python compilation dependencies..."
    
    # Test if we can compile a simple C extension
    local test_setup_py="/tmp/test_setup_$$.py"
    cat > "$test_setup_py" << 'EOF'
from distutils.core import setup
from distutils.extension import Extension

setup(
    name="test",
    ext_modules=[Extension("test", sources=["test.c"])],
)
EOF
    
    local test_c_file="/tmp/test_$$.c"
    cat > "$test_c_file" << 'EOF'
#include <Python.h>

static PyMethodDef module_methods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "test",
    NULL,
    -1,
    module_methods
};

PyMODINIT_FUNC PyInit_test(void) {
    return PyModule_Create(&moduledef);
}
EOF
    
    cd /tmp
    if python3 "$test_setup_py" build &> /dev/null; then
        log_success "Python C extension compilation: working"
    else
        log_error "Python C extension compilation: failed (missing development packages)"
    fi
    
    # Cleanup
    rm -f "$test_setup_py" "$test_c_file"
    rm -rf build/
}

# Generate installation recommendations
generate_recommendations() {
    local total_deps=$((AVAILABLE_DEPS + MISSING_DEPS + OUTDATED_DEPS))
    local success_rate=$((AVAILABLE_DEPS * 100 / total_deps))
    
    echo -e "\n${CYAN}📋 Pre-Installation Assessment${NC}"
    echo -e "================================="
    echo -e "${GREEN}Available: $AVAILABLE_DEPS${NC}"
    echo -e "${YELLOW}Outdated: $OUTDATED_DEPS${NC}"
    echo -e "${RED}Missing: $MISSING_DEPS${NC}"
    echo -e "Total: $total_deps"
    echo -e "Readiness: $success_rate%"
    
    echo -e "\n${CYAN}📊 Installation Readiness:${NC}"
    if [ $MISSING_DEPS -eq 0 ] && [ $success_rate -ge 90 ]; then
        echo -e "${GREEN}🎉 SYSTEM READY FOR INSTALLATION${NC}"
        echo -e "All dependencies are available. You can proceed with installation."
    elif [ $MISSING_DEPS -le 3 ] && [ $success_rate -ge 70 ]; then
        echo -e "${YELLOW}⚠️  SYSTEM MOSTLY READY${NC}"
        echo -e "Few dependencies missing. Installation script will handle them."
    else
        echo -e "${RED}❌ SYSTEM NOT READY${NC}"
        echo -e "Several dependencies missing. Manual preparation recommended."
    fi
    
    if [ $MISSING_DEPS -gt 0 ]; then
        echo -e "\n${CYAN}🔧 Pre-Installation Commands:${NC}"
        echo -e "Run these commands before installation:"
        echo -e ""
        echo -e "${YELLOW}sudo apt update${NC}"
        
        if [ $MISSING_DEPS -gt 5 ]; then
            echo -e "${YELLOW}sudo apt install -y curl wget git build-essential python3 python3-pip python3-venv python3-dev${NC}"
            echo -e "${YELLOW}sudo apt install -y libssl-dev libffi-dev pkg-config cmake supervisor nginx${NC}"
        fi
        
        # MongoDB installation if missing
        if ! command -v mongod &> /dev/null; then
            echo -e ""
            echo -e "${CYAN}MongoDB Installation:${NC}"
            echo -e "${YELLOW}curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-8.0.gpg${NC}"
            echo -e "${YELLOW}echo \"deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu \$(lsb_release -cs)/mongodb-org/8.0 multiverse\" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list${NC}"
            echo -e "${YELLOW}sudo apt update && sudo apt install -y mongodb-org${NC}"
        fi
        
        # Node.js installation if missing
        if ! command -v node &> /dev/null; then
            echo -e ""
            echo -e "${CYAN}Node.js Installation:${NC}"
            echo -e "${YELLOW}curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -${NC}"
            echo -e "${YELLOW}sudo apt install -y nodejs${NC}"
        fi
    fi
    
    echo -e "\n${CYAN}🚀 Next Steps:${NC}"
    if [ $success_rate -ge 80 ]; then
        echo -e "1. Run: ${YELLOW}./setup-improved.sh${NC}"
        echo -e "2. The installation script will handle remaining dependencies"
        echo -e "3. Monitor the installation progress for any issues"
    else
        echo -e "1. Install missing dependencies using the commands above"
        echo -e "2. Run this dependency checker again: ${YELLOW}./dependency-checker.sh${NC}"
        echo -e "3. Once readiness is 80%+, run: ${YELLOW}./setup-improved.sh${NC}"
    fi
    
    echo -e "\n${CYAN}💡 Tips:${NC}"
    echo -e "- Run as regular user (not root) for security"
    echo -e "- Ensure stable internet connection during installation"
    echo -e "- Have at least 10GB free disk space"
    echo -e "- Close resource-intensive applications during installation"
}

# Main function
main() {
    echo -e "${PURPLE}🔍 CryptoMiner Pro V30 - Dependency Checker${NC}"
    echo -e "${CYAN}Checking system readiness for installation...${NC}\n"
    
    # Run all dependency checks
    check_system_packages
    check_python_environment
    check_nodejs_ecosystem
    check_mongodb
    check_development_libraries
    check_system_resources
    check_network_connectivity
    check_python_compilation_deps
    
    # Generate recommendations
    generate_recommendations
    
    # Exit with appropriate code
    if [ $MISSING_DEPS -eq 0 ]; then
        echo -e "\n${GREEN}✅ System is ready for installation!${NC}"
        exit 0
    else
        echo -e "\n${YELLOW}⚠️  Please address missing dependencies before installation.${NC}"
        exit 1
    fi
}

# Run dependency check
main "$@"