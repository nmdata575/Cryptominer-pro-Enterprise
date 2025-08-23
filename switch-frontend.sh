#!/bin/bash

# CryptoMiner V21 - Frontend Switcher Script
# Switches between React frontend and HTML dashboard for proper V21 branding

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_usage() {
    echo "CryptoMiner V21 Frontend Switcher"
    echo ""
    echo "Usage: $0 [html|react|status]"
    echo ""
    echo "Commands:"
    echo "  html     - Switch to HTML dashboard (recommended for V21 branding)"
    echo "  react    - Switch to React frontend"
    echo "  status   - Show current frontend status"
    echo ""
    echo "Examples:"
    echo "  $0 html      # Switch to HTML dashboard"
    echo "  $0 react     # Switch to React frontend"
    echo "  $0 status    # Check what's running"
}

check_status() {
    log_info "Checking frontend status..."
    
    # Check what's running on port 3000
    PORT_3000_PID=$(lsof -ti:3000 2>/dev/null || echo "")
    
    if [[ -n "$PORT_3000_PID" ]]; then
        PORT_3000_CMD=$(ps -p "$PORT_3000_PID" -o comm= 2>/dev/null || echo "unknown")
        log_info "Port 3000: $PORT_3000_CMD (PID: $PORT_3000_PID)"
        
        # Determine which frontend is running
        if ps -p "$PORT_3000_PID" -o args= | grep -q "http.server"; then
            log_success "✅ HTML Dashboard is running on http://localhost:3000"
            log_info "   Branding: CryptoMiner V21 (correct)"
        elif ps -p "$PORT_3000_PID" -o args= | grep -q "node"; then
            log_warning "⚠️  React Frontend is running on http://localhost:3000"
            log_warning "   Branding: May show cached V30 content"
            log_info "   Recommendation: Switch to HTML for proper V21 branding"
        else
            log_info "Unknown service running on port 3000"
        fi
    else
        log_warning "❌ No service running on port 3000"
    fi
    
    # Check supervisor status
    if command -v supervisorctl &> /dev/null; then
        log_info ""
        log_info "Supervisor frontend status:"
        sudo supervisorctl status frontend 2>/dev/null || log_info "  Frontend service not configured"
    fi
}

switch_to_html() {
    log_info "Switching to HTML dashboard..."
    
    # Stop React frontend
    if command -v supervisorctl &> /dev/null; then
        log_info "Stopping React frontend service..."
        sudo supervisorctl stop frontend 2>/dev/null || true
    fi
    
    # Kill anything on port 3000
    log_info "Clearing port 3000..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    sleep 1
    
    # Start HTML dashboard
    if [[ -f "web-dashboard/index.html" ]]; then
        log_info "Starting HTML dashboard server..."
        cd web-dashboard
        python3 -m http.server 3000 > /dev/null 2>&1 &
        DASHBOARD_PID=$!
        cd ..
        
        # Wait and verify
        sleep 2
        if kill -0 "$DASHBOARD_PID" 2>/dev/null; then
            log_success "✅ HTML Dashboard started successfully!"
            log_success "🌐 Access: http://localhost:3000"
            log_success "🎯 Branding: CryptoMiner V21 (correct)"
            echo ""
            log_info "Dashboard PID: $DASHBOARD_PID"
        else
            log_error "❌ Failed to start HTML dashboard"
            exit 1
        fi
    else
        log_error "❌ web-dashboard/index.html not found"
        exit 1
    fi
}

switch_to_react() {
    log_info "Switching to React frontend..."
    
    # Stop HTML dashboard
    log_info "Stopping HTML dashboard..."
    pkill -f "python3 -m http.server" 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    sleep 1
    
    # Start React frontend
    if command -v supervisorctl &> /dev/null; then
        log_info "Starting React frontend service..."
        sudo supervisorctl start frontend
        sleep 3
        
        # Check if it started
        if sudo supervisorctl status frontend | grep -q "RUNNING"; then
            log_success "✅ React Frontend started successfully!"
            log_success "🌐 Access: http://localhost:3000"
            log_warning "⚠️  Note: May show cached V30 branding"
            log_info "💡 Tip: Use 'html' mode for proper V21 branding"
        else
            log_error "❌ Failed to start React frontend"
            log_info "Try: sudo supervisorctl restart frontend"
            exit 1
        fi
    else
        log_error "❌ supervisorctl not available"
        log_info "Manual React startup required"
        exit 1
    fi
}

# Main script logic
case "${1:-}" in
    "html")
        switch_to_html
        ;;
    "react")
        switch_to_react
        ;;
    "status")
        check_status
        ;;
    "")
        show_usage
        exit 0
        ;;
    *)
        log_error "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac

echo ""
log_info "Frontend switching completed!"
log_info "Current status:"
check_status