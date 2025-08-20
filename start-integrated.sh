#!/bin/bash

# CryptoMiner Pro V30 - Integrated Startup Script
# Starts mining with automatic web dashboard integration and backend API

set -e

echo "🚀 CryptoMiner Pro V30 - Integrated Startup"
echo "==========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

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

# Cleanup function
cleanup() {
    log_info "Shutting down all services..."
    
    # Kill backend server
    if [[ -n "$BACKEND_PID" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        log_info "Stopping backend server (PID: $BACKEND_PID)..."
        kill "$BACKEND_PID" 2>/dev/null || true
        wait "$BACKEND_PID" 2>/dev/null || true
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn.*server:app" 2>/dev/null || true
    pkill -f "python3.*cryptominer" 2>/dev/null || true
    pkill -f "http.server" 2>/dev/null || true
    
    log_success "All services stopped"
    exit 0
}

# Setup signal handlers
trap cleanup SIGINT SIGTERM

# Check if mining_config.env exists
if [[ ! -f "mining_config.env" ]]; then
    log_warning "mining_config.env not found. Creating from template..."
    if [[ -f "mining_config.template" ]]; then
        cp mining_config.template mining_config.env
        log_success "Created mining_config.env from template"
    else
        cat > mining_config.env << EOF
# CryptoMiner Pro V30 Configuration
COIN=LTC
WALLET=ltc1qqvz2zw9hqd804a03xg95m4594p7v7thk25sztl
POOL=ltc.luckymonster.pro:4112
PASSWORD=_d=128
INTENSITY=80
THREADS=8
WEB_PORT=8001
WEB_ENABLED=true
AI_ENABLED=true
EOF
        log_success "Created basic mining_config.env"
    fi
    log_warning "Please edit mining_config.env with your wallet address"
fi

# Activate virtual environment if it exists
if [[ -d "venv" ]]; then
    log_info "Activating Python virtual environment..."
    source venv/bin/activate
else
    log_warning "No virtual environment found. Using system Python."
fi

# Check Python dependencies
log_info "Checking Python dependencies..."
python3 -c "
import sys
required_modules = ['fastapi', 'uvicorn', 'asyncio', 'aiohttp', 'scrypt', 'psutil']
missing = []

for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        missing.append(module)

if missing:
    print(f'❌ Missing modules: {missing}')
    print('Installing missing dependencies...')
    sys.exit(2)
else:
    print('✅ All required modules available')
" || {
    if [[ $? -eq 2 ]]; then
        log_info "Installing missing dependencies..."
        pip install -r requirements.txt
    else
        log_error "Dependency check failed"
        exit 1
    fi
}

# Stop any existing processes
log_info "Stopping any existing CryptoMiner processes..."
pkill -f "python3.*cryptominer" 2>/dev/null || true
pkill -f "uvicorn.*server" 2>/dev/null || true
pkill -f "http.server" 2>/dev/null || true
sleep 2

# Create backend .env if it doesn't exist
if [[ ! -f "backend/.env" ]] && [[ -d "backend" ]]; then
    log_info "Creating backend configuration..."
    cat > backend/.env << EOF
MONGO_URL="mongodb://localhost:27017"
DB_NAME="cryptominer_db"
CORS_ORIGINS="*"
EOF
    log_success "Created backend/.env"
fi

# Start the backend API server
log_info "Starting FastAPI backend server..."
if [[ -f "backend/server.py" ]]; then
    cd backend
    python3 -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload &
    BACKEND_PID=$!
    cd ..
    
    # Wait a moment for backend to start
    sleep 3
    
    # Check if backend started successfully
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        log_success "Backend API started (PID: $BACKEND_PID) - http://localhost:8001"
    else
        log_error "Failed to start backend API server"
        exit 1
    fi
else
    log_warning "backend/server.py not found. Backend API not started."
    BACKEND_PID=""
fi

# Start the integrated mining application
log_info "Starting CryptoMiner Pro V30 with integrated web dashboard..."
log_info ""
log_success "🌐 Web Dashboard: http://localhost:3000"
log_success "🔧 Backend API: http://localhost:8001"
log_success "📚 API Docs: http://localhost:8001/docs"
log_info ""
log_info "Press Ctrl+C to stop all services"
log_info ""

# Start with proxy mode for maximum efficiency
python3 cryptominer.py --proxy-mode

# If we reach here, cryptominer.py exited normally
cleanup