#!/bin/bash
# CryptoMiner Pro V30 - Stop Script

set -e

echo "🛑 Stopping CryptoMiner Pro V30..."

# Check if Docker Compose is running
if docker-compose ps -q >/dev/null 2>&1; then
    echo "🐳 Stopping Docker services..."
    docker-compose down
    echo "✅ Docker services stopped!"
    
else
    echo "📦 Stopping local services..."
    
    # Stop backend
    if [ -f ".backend.pid" ]; then
        BACKEND_PID=$(cat .backend.pid)
        if ps -p $BACKEND_PID > /dev/null; then
            echo "⚙️ Stopping backend..."
            kill $BACKEND_PID
        fi
        rm .backend.pid
    fi
    
    # Stop frontend
    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if ps -p $FRONTEND_PID > /dev/null; then
            echo "🌐 Stopping frontend..."
            kill $FRONTEND_PID
        fi
        rm .frontend.pid
    fi
    
    # Stop any running cryptominer processes
    pkill -f cryptominer.py || true
    
    echo "✅ Local services stopped!"
fi

echo "🏁 CryptoMiner Pro V30 stopped successfully!"