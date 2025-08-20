#!/bin/bash

# CryptoMiner Pro V30 - Integrated Startup Script
# Starts mining with automatic web dashboard integration

set -e

echo "🚀 CryptoMiner Pro V30 - Integrated Startup"
echo "==========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
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
    print('Run: pip install -r requirements.txt')
    sys.exit(1)
else:
    print('✅ All required modules available')
" || {
    echo "Installing missing dependencies..."
    pip install -r requirements.txt
}

# Stop any existing processes
log_info "Stopping any existing CryptoMiner processes..."
pkill -f "python3.*cryptominer" 2>/dev/null || true
pkill -f "uvicorn.*server" 2>/dev/null || true
pkill -f "http.server" 2>/dev/null || true
sleep 2

# Start the integrated mining application
log_info "Starting CryptoMiner Pro V30 with integrated web dashboard..."
log_info "Web Dashboard will be available at: http://localhost:3000"
log_info "Backend API will be available at: http://localhost:8001"
log_info ""
log_info "Press Ctrl+C to stop mining"
log_info ""

# Start with proxy mode for maximum efficiency
python3 cryptominer.py --proxy-mode

echo ""
log_success "CryptoMiner Pro V30 stopped"