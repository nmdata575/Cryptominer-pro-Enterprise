#!/bin/bash

# CryptoMiner V21 Management Script
# Comprehensive management for mining operations

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
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="CryptoMiner V21"
VERSION="21.0.0"
CONFIG_FILE="mining_config.env"
LOG_FILE="mining.log"
PID_FILE="cryptominer.pid"

# Print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Print banner
print_banner() {
    print_color $CYAN "╔══════════════════════════════════════════════════════════╗"
    print_color $CYAN "║                   🚀 CryptoMiner V21 🚀                 ║"
    print_color $CYAN "║              Management & Control Script                ║"
    print_color $CYAN "║                    Version $VERSION                     ║"
    print_color $CYAN "╚══════════════════════════════════════════════════════════╝"
    echo
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_color $YELLOW "⚠️  Warning: Running as root. Consider using a regular user for mining."
        echo
    fi
}

# Check system requirements
check_requirements() {
    print_color $BLUE "🔍 Checking system requirements..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version | cut -d' ' -f2)
        major_version=$(echo $python_version | cut -d'.' -f1)
        minor_version=$(echo $python_version | cut -d'.' -f2)
        
        if [[ $major_version -ge 3 && $minor_version -ge 8 ]]; then
            print_color $GREEN "✅ Python $python_version (OK)"
        else
            print_color $RED "❌ Python 3.8+ required (found $python_version)"
            exit 1
        fi
    else
        print_color $RED "❌ Python 3 not found"
        exit 1
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        print_color $GREEN "✅ pip3 available"
    else
        print_color $YELLOW "⚠️  pip3 not found - may need manual installation"
    fi
    
    # Check system resources
    total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    cpu_cores=$(nproc)
    
    print_color $GREEN "✅ System Resources:"
    echo "   💾 RAM: ${total_mem}MB"
    echo "   🔄 CPU Cores: $cpu_cores"
    
    if [[ $total_mem -lt 4096 ]]; then
        print_color $YELLOW "⚠️  Low RAM detected. RandomX mining may be limited."
    fi
    
    echo
}

# Install dependencies
install_dependencies() {
    print_color $BLUE "📦 Installing dependencies..."
    
    # Check if virtual environment should be used
    if [[ -n "$VIRTUAL_ENV" ]]; then
        print_color $GREEN "✅ Using virtual environment: $VIRTUAL_ENV"
    else
        print_color $YELLOW "⚠️  No virtual environment detected. Consider using venv."
    fi
    
    # Install Python dependencies
    if [[ -f "requirements.txt" ]]; then
        pip3 install -r requirements.txt
        print_color $GREEN "✅ Main dependencies installed"
    else
        print_color $RED "❌ requirements.txt not found"
        exit 1
    fi
    
    # Install backend dependencies
    if [[ -f "backend/requirements.txt" ]]; then
        pip3 install -r backend/requirements.txt
        print_color $GREEN "✅ Backend dependencies installed"
    fi
    
    print_color $GREEN "✅ All dependencies installed successfully"
    echo
}

# Setup configuration
setup_config() {
    print_color $BLUE "⚙️  Setting up configuration..."
    
    if [[ ! -f "$CONFIG_FILE" ]]; then
        if [[ -f "mining_config.template" ]]; then
            cp mining_config.template "$CONFIG_FILE"
            print_color $GREEN "✅ Created $CONFIG_FILE from template"
        else
            # Create basic configuration
            cat > "$CONFIG_FILE" << EOF
# CryptoMiner V21 Configuration
# Edit this file with your mining settings

# Mining Configuration - REQUIRED
COIN=XMR
WALLET=your_wallet_address_here
POOL=stratum+tcp://pool.supportxmr.com:3333
PASSWORD=x

# Performance Settings
INTENSITY=80
THREADS=auto

# Web Monitoring
WEB_PORT=3333
WEB_ENABLED=true

# AI Optimization
AI_ENABLED=true
AI_LEARNING_RATE=1.0

# Logging
LOG_LEVEL=INFO
LOG_FILE=mining.log
EOF
            print_color $GREEN "✅ Created basic $CONFIG_FILE"
        fi
        
        print_color $YELLOW "⚠️  Please edit $CONFIG_FILE with your mining details before starting"
        echo "   Required: COIN, WALLET, POOL"
        echo
    else
        print_color $GREEN "✅ Configuration file exists: $CONFIG_FILE"
    fi
}

# Validate configuration
validate_config() {
    if [[ ! -f "$CONFIG_FILE" ]]; then
        print_color $RED "❌ Configuration file not found: $CONFIG_FILE"
        print_color $YELLOW "   Run: $0 setup"
        exit 1
    fi
    
    # Source configuration
    source "$CONFIG_FILE" 2>/dev/null || {
        print_color $RED "❌ Invalid configuration file format"
        exit 1
    }
    
    # Check required fields
    local missing_fields=()
    
    [[ -z "$COIN" || "$COIN" == "your_coin_here" ]] && missing_fields+=("COIN")
    [[ -z "$WALLET" || "$WALLET" == "your_wallet_address_here" ]] && missing_fields+=("WALLET")
    [[ -z "$POOL" || "$POOL" == "your_pool_here" ]] && missing_fields+=("POOL")
    
    if [[ ${#missing_fields[@]} -gt 0 ]]; then
        print_color $RED "❌ Missing required configuration:"
        for field in "${missing_fields[@]}"; do
            echo "   - $field"
        done
        print_color $YELLOW "   Please edit $CONFIG_FILE with your details"
        exit 1
    fi
    
    print_color $GREEN "✅ Configuration validated"
}

# Get process status
get_status() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo "running:$pid"
        else
            echo "stopped"
        fi
    else
        echo "stopped"
    fi
}

# Start mining
start_mining() {
    print_color $BLUE "🚀 Starting $APP_NAME..."
    
    # Check if already running
    local status=$(get_status)
    if [[ $status == running:* ]]; then
        local pid=${status#running:}
        print_color $YELLOW "⚠️  Mining already running (PID: $pid)"
        return 0
    fi
    
    # Validate configuration
    validate_config
    
    # Start main mining process
    if [[ -f "cryptominer.py" ]]; then
        nohup python3 cryptominer.py > "$LOG_FILE" 2>&1 &
        local pid=$!
        echo $pid > "$PID_FILE"
        
        # Wait a moment and check if process started successfully
        sleep 2
        if kill -0 "$pid" 2>/dev/null; then
            print_color $GREEN "✅ Mining started successfully (PID: $pid)"
            print_color $CYAN "📊 Web dashboard: http://localhost:${WEB_PORT:-3333}"
            print_color $CYAN "📋 Logs: tail -f $LOG_FILE"
        else
            print_color $RED "❌ Failed to start mining process"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        print_color $RED "❌ cryptominer.py not found"
        return 1
    fi
    
    # Start backend API server if available
    if [[ -f "backend/server.py" ]]; then
        print_color $BLUE "🔧 Starting backend API server..."
        
        # Check if supervisor is available
        if command -v supervisorctl &> /dev/null; then
            supervisorctl start backend 2>/dev/null || {
                print_color $YELLOW "⚠️  Supervisor not configured, starting backend manually"
                cd backend && nohup python3 -m uvicorn server:app --host 0.0.0.0 --port ${WEB_PORT:-8001} >> "../$LOG_FILE" 2>&1 &
                cd ..
            }
        else
            cd backend && nohup python3 -m uvicorn server:app --host 0.0.0.0 --port ${WEB_PORT:-8001} >> "../$LOG_FILE" 2>&1 &
            cd ..
        fi
        
        print_color $GREEN "✅ Backend API server started"
    fi
    
    echo
    print_color $GREEN "🎉 $APP_NAME is now running!"
    print_color $CYAN "   Monitor: $0 status"
    print_color $CYAN "   Logs: $0 logs"
    print_color $CYAN "   Stop: $0 stop"
}

# Stop mining
stop_mining() {
    print_color $BLUE "🛑 Stopping $APP_NAME..."
    
    local stopped_any=false
    
    # Stop main process
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill -TERM "$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null
            print_color $GREEN "✅ Main process stopped (PID: $pid)"
            stopped_any=true
        fi
        rm -f "$PID_FILE"
    fi
    
    # Stop any remaining processes
    local remaining_pids=$(pgrep -f "cryptominer.py" 2>/dev/null || true)
    if [[ -n "$remaining_pids" ]]; then
        echo "$remaining_pids" | xargs kill -TERM 2>/dev/null || true
        sleep 2
        echo "$remaining_pids" | xargs kill -KILL 2>/dev/null || true
        print_color $GREEN "✅ Remaining processes stopped"
        stopped_any=true
    fi
    
    # Stop backend server
    if command -v supervisorctl &> /dev/null; then
        supervisorctl stop backend 2>/dev/null && {
            print_color $GREEN "✅ Backend API server stopped"
            stopped_any=true
        } || true
    else
        local backend_pids=$(pgrep -f "uvicorn.*server:app" 2>/dev/null || true)
        if [[ -n "$backend_pids" ]]; then
            echo "$backend_pids" | xargs kill -TERM 2>/dev/null || true
            print_color $GREEN "✅ Backend API server stopped"
            stopped_any=true
        fi
    fi
    
    if [[ "$stopped_any" == true ]]; then
        print_color $GREEN "✅ $APP_NAME stopped successfully"
    else
        print_color $YELLOW "⚠️  No running processes found"
    fi
}

# Restart mining
restart_mining() {
    print_color $BLUE "🔄 Restarting $APP_NAME..."
    stop_mining
    sleep 3
    start_mining
}

# Show status
show_status() {
    print_color $BLUE "📊 $APP_NAME Status"
    echo "================================"
    
    local status=$(get_status)
    if [[ $status == running:* ]]; then
        local pid=${status#running:}
        print_color $GREEN "Status: 🟢 RUNNING (PID: $pid)"
        
        # Show process details
        if command -v ps &> /dev/null; then
            local cpu_usage=$(ps -p "$pid" -o %cpu --no-headers 2>/dev/null || echo "N/A")
            local memory_usage=$(ps -p "$pid" -o %mem --no-headers 2>/dev/null || echo "N/A")
            local start_time=$(ps -p "$pid" -o lstart --no-headers 2>/dev/null || echo "N/A")
            
            echo "CPU Usage: ${cpu_usage}%"
            echo "Memory Usage: ${memory_usage}%"
            echo "Started: $start_time"
        fi
        
        # Check backend API
        if command -v curl &> /dev/null; then
            local api_port=${WEB_PORT:-8001}
            if curl -s "http://localhost:$api_port/api/" &> /dev/null; then
                print_color $GREEN "Backend API: 🟢 RUNNING (Port: $api_port)"
            else
                print_color $YELLOW "Backend API: 🟡 NOT RESPONDING"
            fi
        fi
        
        # Show recent log entries
        if [[ -f "$LOG_FILE" ]]; then
            echo
            print_color $CYAN "Recent Activity:"
            tail -n 5 "$LOG_FILE" | sed 's/^/  /'
        fi
        
    else
        print_color $RED "Status: 🔴 STOPPED"
    fi
    
    echo
    print_color $CYAN "Web Dashboard: http://localhost:${WEB_PORT:-8001}"
    print_color $CYAN "Configuration: $CONFIG_FILE"
    print_color $CYAN "Logs: $LOG_FILE"
}

# Show logs
show_logs() {
    if [[ -f "$LOG_FILE" ]]; then
        if [[ "$1" == "-f" || "$1" == "--follow" ]]; then
            print_color $BLUE "📋 Following logs (Ctrl+C to stop)..."
            tail -f "$LOG_FILE"
        else
            print_color $BLUE "📋 Recent logs (use -f to follow):"
            tail -n 50 "$LOG_FILE"
        fi
    else
        print_color $YELLOW "⚠️  Log file not found: $LOG_FILE"
    fi
}

# Show configuration
show_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        print_color $BLUE "⚙️  Current Configuration:"
        echo "================================"
        
        # Source and display config (hide sensitive info)
        source "$CONFIG_FILE" 2>/dev/null || {
            print_color $RED "❌ Invalid configuration file"
            return 1
        }
        
        echo "Coin: ${COIN:-Not set}"
        echo "Wallet: ${WALLET:-Not set}" | sed 's/\(.\{10\}\).*\(.\{10\}\)/\1...\2/'
        echo "Pool: ${POOL:-Not set}"
        echo "Password: ${PASSWORD:+***}"
        echo "Intensity: ${INTENSITY:-80}%"
        echo "Threads: ${THREADS:-auto}"
        echo "Web Port: ${WEB_PORT:-8001}"
        echo "Web Enabled: ${WEB_ENABLED:-true}"
        echo "AI Enabled: ${AI_ENABLED:-true}"
        echo "Log Level: ${LOG_LEVEL:-INFO}"
    else
        print_color $RED "❌ Configuration file not found: $CONFIG_FILE"
        print_color $YELLOW "   Run: $0 setup"
    fi
}

# Setup complete installation
setup_installation() {
    print_color $BLUE "🔧 Setting up $APP_NAME..."
    echo
    
    check_requirements
    install_dependencies
    setup_config
    
    print_color $GREEN "🎉 Setup completed successfully!"
    echo
    print_color $CYAN "Next steps:"
    echo "1. Edit configuration: nano $CONFIG_FILE"
    echo "2. Start mining: $0 start"
    echo "3. Monitor: $0 status"
}

# Show help
show_help() {
    print_color $CYAN "Usage: $0 [COMMAND] [OPTIONS]"
    echo
    print_color $YELLOW "COMMANDS:"
    echo "  start              Start mining operations"
    echo "  stop               Stop mining operations"
    echo "  restart            Restart mining operations"
    echo "  status             Show current status"
    echo "  logs [-f]          Show logs (-f to follow)"
    echo "  config             Show current configuration"
    echo "  setup              Run complete setup/installation"
    echo "  requirements       Check system requirements"
    echo "  help               Show this help message"
    echo
    print_color $YELLOW "EXAMPLES:"
    echo "  $0 start           # Start mining with current config"
    echo "  $0 logs -f         # Follow logs in real-time"
    echo "  $0 setup           # Run initial setup"
    echo
    print_color $YELLOW "FILES:"
    echo "  $CONFIG_FILE       # Main configuration file"
    echo "  $LOG_FILE          # Mining logs"
    echo "  requirements.txt   # Python dependencies"
    echo
    print_color $YELLOW "WEB INTERFACE:"
    echo "  Dashboard: http://localhost:8001"
    echo "  API: http://localhost:8001/api"
}

# Main script logic
main() {
    cd "$SCRIPT_DIR"
    
    case "${1:-help}" in
        "start")
            print_banner
            check_root
            start_mining
            ;;
        "stop")
            print_banner
            stop_mining
            ;;
        "restart")
            print_banner
            restart_mining
            ;;
        "status")
            print_banner
            show_status
            ;;
        "logs")
            show_logs "$2"
            ;;
        "config")
            print_banner
            show_config
            ;;
        "setup")
            print_banner
            check_root
            setup_installation
            ;;
        "requirements")
            print_banner
            check_requirements
            ;;
        "help"|"--help"|"-h")
            print_banner
            show_help
            ;;
        *)
            print_banner
            print_color $RED "❌ Unknown command: $1"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"