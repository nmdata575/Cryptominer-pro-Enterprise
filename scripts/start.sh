#!/bin/bash
# CryptoMiner Pro V30 - Start Script

set -e

echo "🚀 Starting CryptoMiner Pro V30..."

# Check if Docker is available
if command -v docker >/dev/null 2>&1; then
    echo "🐳 Docker detected, starting with Docker Compose..."
    docker-compose up -d
    
    echo "✅ Services started successfully!"
    echo ""
    echo "📊 Dashboard: http://localhost:3000"
    echo "🔗 API: http://localhost:8001/api"
    echo "📋 Status: docker-compose ps"
    
else
    echo "📦 Docker not found, starting local services..."
    
    # Install dependencies if needed
    if [ ! -d "venv" ]; then
        echo "🔧 Setting up virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    # Start MongoDB if not running
    if ! pgrep mongod >/dev/null; then
        echo "🍃 Starting MongoDB..."
        mongod --fork --logpath /tmp/mongodb.log --dbpath ./data/db --port 27017
    fi
    
    # Start backend
    echo "⚙️ Starting backend API..."
    cd backend
    python3 server.py &
    BACKEND_PID=$!
    cd ..
    
    # Start frontend
    echo "🌐 Starting frontend dashboard..."
    cd frontend
    yarn start &
    FRONTEND_PID=$!
    cd ..
    
    echo "✅ Services started successfully!"
    echo ""
    echo "📊 Dashboard: http://localhost:3000"
    echo "🔗 API: http://localhost:8001/api"
    echo ""
    echo "To stop services: ./scripts/stop.sh"
    
    # Save PIDs for stop script
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid
fi