#!/bin/bash

# CryptoMiner V21 - Stop Script
# Forcefully stops all CryptoMiner V21 processes

echo "🛑 Stopping CryptoMiner V21..."

# Stop supervisor services
if command -v supervisorctl &> /dev/null; then
    echo "Stopping supervisor services..."
    sudo supervisorctl stop frontend 2>/dev/null || true
    sudo supervisorctl stop backend 2>/dev/null || true  
    sudo supervisorctl stop cryptominer 2>/dev/null || true
fi

# Kill web dashboard (HTML server)
echo "Stopping web dashboard..."
pkill -f "python3 -m http.server" 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Kill backend API server
echo "Stopping backend API..."
pkill -f "uvicorn.*server:app" 2>/dev/null || true
lsof -ti:8001 | xargs kill -9 2>/dev/null || true

# Kill mining processes
echo "Stopping mining processes..."
pkill -TERM -f "python3.*cryptominer" 2>/dev/null || true
sleep 2
pkill -9 -f "python3.*cryptominer" 2>/dev/null || true

# Kill any remaining HTTP servers
pkill -f "http.server" 2>/dev/null || true

# Kill any timeout processes
pkill -f "timeout.*cryptominer" 2>/dev/null || true

echo "✅ All CryptoMiner V21 processes stopped"

# Optional: Show any remaining processes
echo ""
echo "Checking for any remaining processes..."
REMAINING=$(ps aux | grep -E "(cryptominer|uvicorn.*server|http\.server)" | grep -v grep | wc -l)

if [[ $REMAINING -gt 0 ]]; then
    echo "⚠️  Found $REMAINING remaining processes:"
    ps aux | grep -E "(cryptominer|uvicorn.*server|http\.server)" | grep -v grep
    echo ""
    echo "Force killing remaining processes..."
    ps aux | grep -E "(cryptominer|uvicorn.*server|http\.server)" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true
    echo "✅ Force cleanup completed"
else
    echo "✅ No remaining processes found"
fi

echo "🏁 CryptoMiner V21 stop script completed"