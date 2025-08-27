#!/bin/bash

# CryptoMiner V21 - Integrated Startup Script
# Starts mining with automatic web dashboard integration and backend API

set -e

echo "🚀 CryptoMiner V21 - Integrated Startup"
echo "======================================="

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

    # Stop backend server gracefully
    if [[ -n "$BACKEND_PID" ]]; then
        log_info "Stopping backend server (PID: $BACKEND_PID)..."
        kill -TERM "$BACKEND_PID" 2>/dev/null || true
        sleep 2
        kill -9 "$BACKEND_PID" 2>/dev/null || true
    fi

    # Stop dashboard server gracefully
    if [[ -n "$DASHBOARD_PID" ]]; then
        log_info "Stopping web dashboard (PID: $DASHBOARD_PID)..."
        kill -TERM "$DASHBOARD_PID" 2>/dev/null || true
        sleep 2
        kill -9 "$DASHBOARD_PID" 2>/dev/null || true
    fi

    # Stop cryptominer process
    if [[ -n "$CRYPTO_PID" ]]; then
        log_info "Stopping cryptominer (PID: $CRYPTO_PID)..."
        kill -TERM "$CRYPTO_PID" 2>/dev/null || true
        sleep 2
        kill -9 "$CRYPTO_PID" 2>/dev/null || true
    fi

    # Force kill any remaining processes
    log_info "Force stopping all CryptoMiner V21 processes..."
    pkill -9 -f "uvicorn.*server:app" 2>/dev/null || true
    pkill -9 -f "python3.*cryptominer" 2>/dev/null || true
    pkill -9 -f "http.server" 2>/dev/null || true
    pkill -9 -f "timeout.*cryptominer" 2>/dev/null || true

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
# CryptoMiner V21 Configuration
COIN=XMR
WALLET=your_monero_wallet_address_here
POOL=pool.supportxmr.com:3333
PASSWORD=cryptominer-v21
INTENSITY=80
THREADS=8
WEB_PORT=3000
WEB_ENABLED=true
AI_ENABLED=true
EOF
        log_success "Created basic mining_config.env"
    fi
    log_warning "Please edit mining_config.env with your wallet address"
fi

# Export WEB_PORT from mining_config.env, default to 3000 if not set
WEB_PORT=$(grep -E '^WEB_PORT=' mining_config.env | cut -d'=' -f2 | tr -d '"')
if [[ -z "$WEB_PORT" ]]; then
    WEB_PORT=3000
fi
export WEB_PORT

# Create virtual environment if it doesn't exist
if [[ ! -d "venv" ]]; then
    log_info "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
log_info "Activating Python virtual environment..."
source venv/bin/activate

# Ensure setuptools & wheel installed for building packages
log_info "Ensuring setuptools and wheel are installed/upgraded in the virtual environment..."
pip install --upgrade setuptools wheel

# Always upgrade pip and install requirements
log_info "Upgrading pip..."
if ! pip install --upgrade pip; then
    log_error "Failed to upgrade pip"
    exit 1
fi

log_info "Installing Python dependencies from requirements.txt (prefer binary wheels)..."
if ! pip install --prefer-binary --only-binary=:all: -r requirements.txt; then
    log_error "Failed to install Python dependencies (binary wheels not available for some packages)"
    exit 1
fi

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

# Stop any existing frontend or HTTP server on the dashboard port
log_info "Setting up web dashboard..."
if command -v supervisorctl &> /dev/null; then
    sudo supervisorctl stop frontend 2>/dev/null || true
    log_info "Stopped React frontend (if running)"
fi

lsof -ti:"$WEB_PORT" | xargs kill -9 2>/dev/null || true
sleep 1

# Build and serve frontend dashboard
if [[ -d "frontend" ]]; then
    log_info "Building React frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
    if [[ -d "frontend/build" ]]; then
        log_info "Starting CryptoMiner V21 web dashboard on port $WEB_PORT..."
        cd frontend/build
        python3 -m http.server "$WEB_PORT" > /dev/null 2>&1 &
        DASHBOARD_PID=$!
        cd ../..
        sleep 2
        if kill -0 "$DASHBOARD_PID" 2>/dev/null; then
            log_success "Web Dashboard started (PID: $DASHBOARD_PID) - http://localhost:$WEB_PORT"
        else
            log_error "Failed to start web dashboard"
            exit 1
        fi
    else
        log_error "frontend/build not found. Web dashboard not started."
        DASHBOARD_PID=""
    fi
else
    log_warning "frontend directory not found. Web dashboard not started."
    DASHBOARD_PID=""
fi

# Start the integrated mining application
log_info "Starting CryptoMiner V21 with integrated web dashboard..."
log_info ""
log_success "🌐 Web Dashboard: http://localhost:$WEB_PORT"
log_success "🔧 Backend API: http://localhost:8001"
log_success "📚 API Docs: http://localhost:8001/docs"
log_info ""
log_info "Press Ctrl+C to stop all services"
log_info ""

# Start with proxy mode for maximum efficiency and capture PID
python3 cryptominer.py --proxy-mode &
CRYPTO_PID=$!

# Wait for cryptominer to exit (foreground wait)
wait $CRYPTO_PID

# If we reach here, cryptominer.py exited normally
cleanup
