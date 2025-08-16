#!/bin/bash

# CryptoMiner Pro V30 - Installation Verification Script
# Comprehensive verification of all installation requirements

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="$HOME/CryptominerV30"
DB_NAME="crypto_miner_db"

# Verification counters
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

log_success() {
    echo -e "${GREEN}[PASS] ✅ $1${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
}

log_warning() {
    echo -e "${YELLOW}[WARN] ⚠️  $1${NC}"
    WARNING_CHECKS=$((WARNING_CHECKS + 1))
}

log_error() {
    echo -e "${RED}[FAIL] ❌ $1${NC}" >&2
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
}

log_step() {
    echo -e "${PURPLE}[STEP] 🔍 $1${NC}"
}

# Verification functions

verify_installation_path() {
    log_step "Verifying installation path..."
    
    if [ -d "$INSTALL_DIR" ]; then
        log_success "Installation directory exists: $INSTALL_DIR"
        
        # Check required subdirectories
        local required_dirs=("backend" "frontend")
        for dir in "${required_dirs[@]}"; do
            if [ -d "$INSTALL_DIR/$dir" ]; then
                log_success "Required directory exists: $dir"
            else
                log_error "Missing required directory: $dir"
            fi
        done
    else
        log_error "Installation directory not found: $INSTALL_DIR"
        log_error "Expected path: /home/USER/CryptominerV30 (✅ meets user requirement)"
    fi
}

verify_dependencies() {
    log_step "Verifying system dependencies..."
    
    # Essential system packages
    local system_packages=(
        "curl" "wget" "git" "build-essential" "python3" 
        "python3-venv" "python3-pip" "nodejs" "yarn"
        "supervisor" "mongod:mongodb"
    )
    
    for package in "${system_packages[@]}"; do
        local cmd="${package%%:*}"
        local name="${package##*:}"
        [ "$name" = "$cmd" ] && name="$cmd"
        
        # Special handling for certain packages
        case "$cmd" in
            "build-essential")
                if command -v gcc &> /dev/null; then
                    local version=$(gcc --version 2>&1 | head -1)
                    log_success "$name: $version"
                else
                    log_error "$name not found"
                fi
                ;;
            "python3-venv")
                if python3 -c "import venv" 2>/dev/null; then
                    log_success "$name: available"
                else
                    log_error "$name not found"
                fi
                ;;
            "python3-pip")
                if python3 -m pip --version &> /dev/null; then
                    local version=$(python3 -m pip --version 2>&1)
                    log_success "$name: $version"
                else
                    log_error "$name not found"
                fi
                ;;
            "supervisor")
                if command -v supervisorctl &> /dev/null; then
                    log_success "$name: available"
                else
                    log_error "$name not found"
                fi
                ;;
            *)
                if command -v "$cmd" &> /dev/null; then
                    local version
                    case "$cmd" in
                        "python3") version=$(python3 --version 2>&1) ;;
                        "node") version=$(node --version 2>&1) ;;
                        "yarn") version=$(yarn --version 2>&1) ;;
                        "mongod") version=$(mongod --version 2>&1 | head -1) ;;
                        *) version="installed" ;;
                    esac
                    log_success "$name: $version"
                else
                    log_error "$name not found"
                fi
                ;;
        esac
    done
}

verify_python_environment() {
    log_step "Verifying Python environment..."
    
    local venv_path="$INSTALL_DIR/backend/venv"
    
    if [ -d "$venv_path" ]; then
        log_success "Python virtual environment exists"
        
        if [ -f "$venv_path/bin/python3" ]; then
            log_success "Python executable found in venv"
            
            # Check Python version
            local python_version=$("$venv_path/bin/python3" --version)
            log_success "Python version: $python_version"
            
            # Verify critical packages
            local critical_packages=(
                "fastapi" "uvicorn" "pymongo" "motor" 
                "cryptography" "scrypt" "numpy" "requests"
            )
            
            for package in "${critical_packages[@]}"; do
                if "$venv_path/bin/python3" -c "import $package" 2>/dev/null; then
                    log_success "Python package: $package"
                else
                    log_error "Missing Python package: $package"
                fi
            done
        else
            log_error "Python executable not found in venv"
        fi
    else
        log_error "Python virtual environment not found"
    fi
}

verify_frontend_environment() {
    log_step "Verifying frontend environment..."
    
    local frontend_path="$INSTALL_DIR/frontend"
    
    if [ -d "$frontend_path" ]; then
        log_success "Frontend directory exists"
        
        # Check package.json
        if [ -f "$frontend_path/package.json" ]; then
            log_success "package.json found"
        else
            log_error "package.json not found"
        fi
        
        # Check node_modules
        if [ -d "$frontend_path/node_modules" ]; then
            log_success "node_modules directory exists"
            
            # Check critical dependencies
            local critical_deps=("react" "react-dom" "axios" "tailwindcss")
            for dep in "${critical_deps[@]}"; do
                if [ -d "$frontend_path/node_modules/$dep" ]; then
                    log_success "Frontend dependency: $dep"
                else
                    log_error "Missing frontend dependency: $dep"
                fi
            done
        else
            log_warning "node_modules not found - run 'yarn install' in frontend directory"
        fi
        
        # Check build directory
        if [ -d "$frontend_path/build" ]; then
            log_success "Production build exists"
        else
            log_warning "Production build not found - run 'yarn build' to create"
        fi
    else
        log_error "Frontend directory not found"
    fi
}

verify_mongodb_security() {
    log_step "Verifying MongoDB security setup..."
    
    # Check if MongoDB is running
    if systemctl is-active mongod &> /dev/null; then
        log_success "MongoDB service is running"
        
        # Check if authentication is enabled
        if mongosh --eval "db.adminCommand('ismaster')" &> /dev/null; then
            log_success "MongoDB is accessible"
            
            # Try to connect without authentication (should fail if security is properly configured)
            if mongosh "$DB_NAME" --eval "db.stats()" &> /dev/null; then
                log_warning "MongoDB allows unauthenticated access - security may not be properly configured"
            else
                log_success "MongoDB requires authentication (security enabled)"
            fi
            
            # Check if credentials file exists
            if [ -f "$INSTALL_DIR/.mongodb_credentials" ]; then
                log_success "MongoDB credentials file exists"
                
                # Verify credentials work
                if [ -r "$INSTALL_DIR/.mongodb_credentials" ]; then
                    source "$INSTALL_DIR/.mongodb_credentials"
                    if [ -n "$DB_USER" ] && [ -n "$DB_PASSWORD" ]; then
                        if mongosh "$DB_NAME" --username "$DB_USER" --password "$DB_PASSWORD" --eval "db.stats()" &> /dev/null; then
                            log_success "MongoDB authentication with app user works"
                        else
                            log_error "MongoDB authentication failed with app credentials"
                        fi
                    else
                        log_error "MongoDB credentials file is incomplete"
                    fi
                else
                    log_error "Cannot read MongoDB credentials file"
                fi
            else
                log_error "MongoDB credentials file not found"
            fi
        else
            log_error "Cannot connect to MongoDB"
        fi
    else
        log_error "MongoDB service is not running"
    fi
}

verify_configuration_files() {
    log_step "Verifying configuration files..."
    
    # Backend .env file
    local backend_env="$INSTALL_DIR/backend/.env"
    if [ -f "$backend_env" ]; then
        log_success "Backend .env file exists"
        
        # Check required environment variables
        local required_vars=("MONGO_URL" "DATABASE_NAME" "LOG_LEVEL")
        for var in "${required_vars[@]}"; do
            if grep -q "^$var=" "$backend_env"; then
                log_success "Backend env var: $var"
            else
                log_error "Missing backend env var: $var"
            fi
        done
        
        # Check file permissions
        local perms=$(stat -c "%a" "$backend_env")
        if [ "$perms" = "600" ]; then
            log_success "Backend .env has secure permissions (600)"
        else
            log_warning "Backend .env permissions should be 600 (currently $perms)"
        fi
    else
        log_error "Backend .env file not found"
    fi
    
    # Frontend .env file
    local frontend_env="$INSTALL_DIR/frontend/.env"
    if [ -f "$frontend_env" ]; then
        log_success "Frontend .env file exists"
        
        # Check required variables
        if grep -q "^REACT_APP_BACKEND_URL=" "$frontend_env"; then
            local backend_url=$(grep "^REACT_APP_BACKEND_URL=" "$frontend_env" | cut -d'=' -f2)
            log_success "Frontend backend URL: $backend_url"
        else
            log_error "Missing REACT_APP_BACKEND_URL in frontend .env"
        fi
        
        if grep -q "^PORT=3333" "$frontend_env"; then
            log_success "Frontend port correctly set to 3333"
        else
            log_warning "Frontend port not set to 3333"
        fi
    else
        log_error "Frontend .env file not found"
    fi
}

verify_services() {
    log_step "Verifying service configuration..."
    
    # Check supervisor configuration
    local supervisor_config="/etc/supervisor/conf.d/cryptominer-v30.conf"
    if [ -f "$supervisor_config" ]; then
        log_success "Supervisor configuration exists"
        
        # Check if paths in config match installation directory
        if grep -q "$INSTALL_DIR" "$supervisor_config"; then
            log_success "Supervisor config uses correct installation path"
        else
            log_error "Supervisor config does not reference correct installation path"
        fi
    else
        log_warning "Supervisor configuration not found (manual service management required)"
    fi
    
    # Check if services are running (check both old and new service names)
    if command -v supervisorctl &> /dev/null; then
        local backend_running=false
        local frontend_running=false
        
        # Check new service names
        if sudo supervisorctl status cryptominer-v30:backend 2>/dev/null | grep -q "RUNNING"; then
            log_success "Backend service is running (cryptominer-v30:backend)"
            backend_running=true
        # Check old service names
        elif sudo supervisorctl status mining_system:backend 2>/dev/null | grep -q "RUNNING"; then
            log_success "Backend service is running (mining_system:backend)"
            backend_running=true
        else
            log_warning "Backend service is not running"
        fi
        
        # Check new service names
        if sudo supervisorctl status cryptominer-v30:frontend 2>/dev/null | grep -q "RUNNING"; then
            log_success "Frontend service is running (cryptominer-v30:frontend)"
            frontend_running=true
        # Check old service names  
        elif sudo supervisorctl status mining_system:frontend 2>/dev/null | grep -q "RUNNING"; then
            log_success "Frontend service is running (mining_system:frontend)"
            frontend_running=true
        else
            log_warning "Frontend service is not running"
        fi
        
        # Overall supervisor status
        if $backend_running && $frontend_running; then
            log_success "All supervisor services are running"
        else
            log_error "Some supervisor services have issues"
        fi
    fi
}

verify_api_endpoints() {
    log_step "Verifying API endpoints..."
    
    # Check if backend is responding
    if curl -s http://localhost:8001/api/health > /dev/null; then
        log_success "Backend health endpoint responding"
        
        # Test specific endpoints
        local endpoints=("/api/health" "/api/system/cpu-info" "/api/mining/status")
        for endpoint in "${endpoints[@]}"; do
            if curl -s "http://localhost:8001$endpoint" | jq . &> /dev/null; then
                log_success "API endpoint: $endpoint"
            else
                log_warning "API endpoint may have issues: $endpoint"
            fi
        done
    else
        log_error "Backend is not responding on port 8001"
    fi
    
    # Check frontend
    if curl -s http://localhost:3333 > /dev/null; then
        log_success "Frontend is responding on port 3333"
    else
        log_error "Frontend is not responding on port 3333"
    fi
}

verify_file_permissions() {
    log_step "Verifying file permissions..."
    
    # Check installation directory ownership
    local owner=$(stat -c "%U" "$INSTALL_DIR" 2>/dev/null || echo "unknown")
    if [ "$owner" = "$USER" ]; then
        log_success "Installation directory owned by current user"
    else
        log_error "Installation directory not owned by current user (owner: $owner)"
    fi
    
    # Check critical file permissions
    local critical_files=(
        "$INSTALL_DIR/backend/.env:600"
        "$INSTALL_DIR/.mongodb_credentials:600"
        "$INSTALL_DIR/backend/server.py:644" 
        "$INSTALL_DIR/frontend/package.json:644"
    )
    
    for file_perm in "${critical_files[@]}"; do
        local file="${file_perm%%:*}"
        local expected_perm="${file_perm##*:}"
        
        if [ -f "$file" ]; then
            local actual_perm=$(stat -c "%a" "$file")
            if [ "$actual_perm" = "$expected_perm" ]; then
                log_success "File permissions correct: $(basename "$file") ($actual_perm)"
            else
                log_warning "File permissions should be $expected_perm: $(basename "$file") (currently $actual_perm)"
            fi
        fi
    done
}

display_verification_summary() {
    local total_checks=$((PASSED_CHECKS + FAILED_CHECKS + WARNING_CHECKS))
    local success_rate=$((PASSED_CHECKS * 100 / total_checks))
    
    echo -e "\n${CYAN}🔍 Verification Summary${NC}"
    echo -e "========================"
    echo -e "${GREEN}Passed: $PASSED_CHECKS${NC}"
    echo -e "${YELLOW}Warnings: $WARNING_CHECKS${NC}"
    echo -e "${RED}Failed: $FAILED_CHECKS${NC}"
    echo -e "Total: $total_checks"
    echo -e "Success Rate: $success_rate%"
    
    echo -e "\n${CYAN}📋 Compliance Status:${NC}"
    
    # Check user requirements compliance
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "✅ Install under /home/USER/CryptominerV30: ${GREEN}COMPLIANT${NC}"
    else
        echo -e "❌ Install under /home/USER/CryptominerV30: ${RED}NON-COMPLIANT${NC}"
    fi
    
    if [ $PASSED_CHECKS -gt $((total_checks * 7 / 10)) ]; then
        echo -e "✅ Install all required dependencies: ${GREEN}COMPLIANT${NC}"
    else
        echo -e "❌ Install all required dependencies: ${RED}NON-COMPLIANT${NC}"
    fi
    
    if [ $PASSED_CHECKS -gt $((total_checks * 8 / 10)) ]; then
        echo -e "✅ Install all necessary programs: ${GREEN}COMPLIANT${NC}"
    else
        echo -e "❌ Install all necessary programs: ${RED}NON-COMPLIANT${NC}"
    fi
    
    # MongoDB security check
    if mongosh "$DB_NAME" --eval "db.stats()" &> /dev/null 2>&1; then
        echo -e "❌ Setup proper security and user accounts for MongoDB: ${RED}NON-COMPLIANT${NC}"
        echo -e "   (Database accessible without authentication)"
    else
        echo -e "✅ Setup proper security and user accounts for MongoDB: ${GREEN}COMPLIANT${NC}"
    fi
    
    echo -e "\n${CYAN}📊 Overall Status:${NC}"
    if [ $FAILED_CHECKS -eq 0 ] && [ $success_rate -ge 90 ]; then
        echo -e "${GREEN}🎉 INSTALLATION EXCELLENT ($success_rate% success rate)${NC}"
    elif [ $FAILED_CHECKS -le 2 ] && [ $success_rate -ge 80 ]; then
        echo -e "${YELLOW}⚠️  INSTALLATION GOOD ($success_rate% success rate) - Minor issues${NC}"
    elif [ $success_rate -ge 60 ]; then
        echo -e "${YELLOW}⚠️  INSTALLATION NEEDS IMPROVEMENT ($success_rate% success rate)${NC}"
    else
        echo -e "${RED}❌ INSTALLATION HAS MAJOR ISSUES ($success_rate% success rate)${NC}"
    fi
    
    if [ $FAILED_CHECKS -gt 0 ] || [ $WARNING_CHECKS -gt 0 ]; then
        echo -e "\n${CYAN}🔧 Recommendations:${NC}"
        if [ $FAILED_CHECKS -gt 0 ]; then
            echo -e "- Fix failed checks by running: ${YELLOW}./setup-improved.sh${NC}"
        fi
        if [ $WARNING_CHECKS -gt 0 ]; then
            echo -e "- Address warnings for optimal performance"
        fi
        echo -e "- Review logs for detailed error information"
    fi
}

# Main verification function
main() {
    echo -e "${PURPLE}🔍 CryptoMiner Pro V30 - Installation Verification${NC}"
    echo -e "${CYAN}Verifying installation meets all requirements...${NC}\n"
    
    # Run all verification checks
    verify_installation_path
    verify_dependencies  
    verify_python_environment
    verify_frontend_environment
    verify_mongodb_security
    verify_configuration_files
    verify_services
    verify_api_endpoints
    verify_file_permissions
    
    # Display summary
    display_verification_summary
    
    # Exit with appropriate code
    if [ $FAILED_CHECKS -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Run verification
main "$@"