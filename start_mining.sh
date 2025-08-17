#!/bin/bash
# CryptoMiner Pro V30 - Quick Start Script

echo "🚀 CryptoMiner Pro V30 - Terminal Mining Application"
echo "=============================================="

# Check if Python virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "❌ Virtual environment not found. Please run:"
    echo "   cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source backend/venv/bin/activate

echo "✅ Virtual environment activated"
echo ""

# Check for existing configuration
if [ -f "mining_config.json" ]; then
    echo "📋 Found existing configuration:"
    cat mining_config.json | python3 -c "
import json, sys
config = json.load(sys.stdin)
print(f\"   Coin: {config['coin']['name']} ({config['coin']['symbol']})\")
print(f\"   Mode: {config['mode']}\")
print(f\"   Threads: {config['threads']}\")
print(f\"   Web Port: {config['web_port']}\")
"
    echo ""
    echo "Options:"
    echo "  1. Use existing configuration"  
    echo "  2. Setup new configuration"
    echo "  3. Command line mining"
    echo ""
    read -p "Choose option (1-3): " choice
    
    case $choice in
        1)
            python3 mine.py
            ;;
        2)
            python3 mine.py --setup
            ;;
        3)
            echo ""
            echo "Command line examples:"
            echo "  python3 mine.py --coin LTC --wallet ltc1xxx... --pool stratum+tcp://pool.com:4444"
            echo "  python3 mine.py --list-coins"
            echo ""
            ;;
        *)
            python3 mine.py
            ;;
    esac
else
    echo "⚠️  No configuration found."
    echo ""
    echo "Options:"
    echo "  1. Interactive setup (recommended)"
    echo "  2. Command line parameters"
    echo "  3. List available coins"
    echo ""
    read -p "Choose option (1-3): " choice
    
    case $choice in
        1)
            python3 mine.py --setup
            ;;
        2)
            echo ""
            echo "Example usage:"
            echo "  python3 mine.py --coin LTC --wallet YOUR_WALLET --pool stratum+tcp://pool.com:4444 --threads 8"
            echo ""
            echo "Required parameters:"
            echo "  --coin     Coin symbol (use --list-coins to see options)"
            echo "  --wallet   Your wallet address" 
            echo "  --pool     Pool address (optional for solo mining)"
            echo ""
            echo "Optional parameters:"
            echo "  --threads  Number of threads (auto-detected if not specified)"
            echo "  --web-port Web monitor port (default: 3333)"
            echo "  --no-web   Disable web monitoring"
            echo ""
            ;;
        3)
            python3 mine.py --list-coins
            ;;
        *)
            python3 mine.py --setup
            ;;
    esac
fi