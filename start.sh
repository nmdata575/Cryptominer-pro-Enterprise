#!/bin/bash

# 🚀 CryptoMiner Pro - Quick Setup Script
# This script helps you get started quickly with the mining system

set -e  # Exit on any error

echo "🚀 CryptoMiner Pro - Quick Setup & Start"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running as root for service management
check_permissions() {
    if [ "$EUID" -ne 0 ]; then
        print_warning "Some operations require sudo privileges"
        print_info "Run with: sudo $0 for full functionality"
    fi
}

# Check system requirements
check_requirements() {
    print_info "Checking system requirements..."
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
        print_status "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.8+ required but not found"
        exit 1
    fi
    
    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_status "Node.js $NODE_VERSION found"
    else
        print_error "Node.js 16+ required but not found"
        exit 1
    fi
    
    # Check MongoDB
    if systemctl is-active --quiet mongod || pgrep mongod > /dev/null; then
        print_status "MongoDB is running"
    else
        print_warning "MongoDB not running - attempting to start..."
        if systemctl start mongod 2>/dev/null || mongod --fork --logpath /var/log/mongodb.log --dbpath /var/lib/mongodb 2>/dev/null; then
            print_status "MongoDB started successfully"
        else
            print_warning "Could not start MongoDB automatically"
            print_info "Please start MongoDB manually: sudo systemctl start mongod"
        fi
    fi
}

# Check if services are running
check_services() {
    print_info "Checking CryptoMiner Pro services..."
    
    if supervisorctl status mining_system:backend &> /dev/null; then
        if supervisorctl status mining_system:backend | grep -q RUNNING; then
            print_status "Backend service is running"
        else
            print_warning "Backend service exists but not running"
            return 1
        fi
    else
        print_warning "Backend service not configured"
        return 1
    fi
    
    if supervisorctl status mining_system:frontend &> /dev/null; then
        if supervisorctl status mining_system:frontend | grep -q RUNNING; then
            print_status "Frontend service is running"
        else
            print_warning "Frontend service exists but not running"
            return 1
        fi
    else
        print_warning "Frontend service not configured"
        return 1
    fi
    
    return 0
}

# Test API connectivity
test_api() {
    print_info "Testing backend API..."
    
    if curl -s http://localhost:8001/api/health > /dev/null; then
        print_status "Backend API is responding"
    else
        print_error "Backend API not responding"
        return 1
    fi
    
    return 0
}

# Test frontend connectivity
test_frontend() {
    print_info "Testing frontend..."
    
    if curl -s -I http://localhost:3000 | grep -q "200 OK"; then
        print_status "Frontend is accessible"
    else
        print_error "Frontend not accessible"
        return 1
    fi
    
    return 0
}

# Start services
start_services() {
    print_info "Starting CryptoMiner Pro services..."
    
    if supervisorctl start mining_system:* 2>/dev/null; then
        print_status "Services started successfully"
        sleep 5  # Give services time to start
    else
        print_error "Failed to start services"
        print_info "Try running: sudo supervisorctl start mining_system:*"
        return 1
    fi
}

# Display status and next steps
show_status() {
    echo ""
    echo "🎯 CryptoMiner Pro Status"
    echo "========================"
    
    # Service status
    if supervisorctl status mining_system:* 2>/dev/null; then
        supervisorctl status mining_system:*
    else
        print_warning "Services not managed by supervisor"
    fi
    
    echo ""
    print_info "System Information:"
    echo "  • CPU Cores: $(nproc)"
    echo "  • Memory: $(free -h | awk '/^Mem:/ {print $2}')"
    echo "  • Disk Space: $(df -h / | awk 'NR==2 {print $4}')"
    
    echo ""
    print_info "Access URLs:"
    echo "  • Dashboard: http://localhost:3000"
    echo "  • Backend API: http://localhost:8001/api/health"
    echo "  • API Documentation: http://localhost:8001/docs"
}

# Main execution flow
main() {
    echo ""
    check_permissions
    echo ""
    
    check_requirements
    echo ""
    
    # Try to check and start services
    if ! check_services; then
        print_info "Attempting to start services..."
        if ! start_services; then
            print_warning "Could not start services automatically"
            print_info "Please check the setup guide: cat SETUP_GUIDE.md"
            exit 1
        fi
    fi
    
    echo ""
    
    # Test connectivity
    if test_api && test_frontend; then
        print_status "All systems operational!"
    else
        print_warning "Some services may need attention"
    fi
    
    echo ""
    show_status
    
    echo ""
    echo "🎉 Quick Start Instructions:"
    echo "=============================="
    echo "1. Open browser: http://localhost:3000"
    echo "2. Select a cryptocurrency (Litecoin recommended for beginners)"
    echo "3. Enter your wallet address in the Wallet Configuration"
    echo "4. Adjust performance settings (start conservative)"
    echo "5. Click 'Start Mining' and monitor the dashboard"
    echo ""
    print_info "For detailed instructions, see: SETUP_GUIDE.md"
    print_info "For quick reference, see: QUICK_REFERENCE.md"
    echo ""
    print_status "Ready to start mining with AI optimization! 🚀"
}

# Handle command line arguments
case "${1:-}" in
    "check")
        check_requirements
        check_services
        ;;
    "start")
        start_services
        ;;
    "status")
        show_status
        ;;
    "test")
        test_api
        test_frontend
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [check|start|status|test|help]"
        echo ""
        echo "Commands:"
        echo "  check   - Check system requirements and service status"
        echo "  start   - Start CryptoMiner Pro services"
        echo "  status  - Show current system status"
        echo "  test    - Test API and frontend connectivity"
        echo "  help    - Show this help message"
        echo ""
        echo "Run without arguments for full setup and status check."
        ;;
    *)
        main
        ;;
esac