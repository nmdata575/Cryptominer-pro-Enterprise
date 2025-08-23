#!/bin/bash

# CryptoMiner V21 - Stop Script
# Forcefully stops all CryptoMiner V21 processes

echo "🛑 Stopping CryptoMiner V21..."

# First try graceful shutdown
echo "Attempting graceful shutdown..."
pkill -TERM -f "python3.*cryptominer" 2>/dev/null || true
pkill -TERM -f "uvicorn.*server" 2>/dev/null || true
pkill -TERM -f "http.server" 2>/dev/null || true

# Wait a moment for graceful shutdown
sleep 3

# Force kill any remaining processes
echo "Force killing any remaining processes..."
pkill -9 -f "python3.*cryptominer" 2>/dev/null || true
pkill -9 -f "uvicorn.*server" 2>/dev/null || true
pkill -9 -f "http.server" 2>/dev/null || true

# Also kill any timeout processes that might be hanging
pkill -9 -f "timeout.*cryptominer" 2>/dev/null || true

# Wait a moment for cleanup
sleep 2

# Check if any processes are still running
REMAINING=$(ps aux | grep -E "(python3.*cryptominer|uvicorn.*server|http.server)" | grep -v grep | wc -l)

if [[ $REMAINING -eq 0 ]]; then
    echo "✅ All CryptoMiner Pro V30 processes stopped successfully"
else
    echo "⚠️  Some processes may still be running:"
    ps aux | grep -E "(python3.*cryptominer|uvicorn.*server|http.server)" | grep -v grep
    echo ""
    echo "Trying one more force kill..."
    ps aux | grep -E "(python3.*cryptominer|uvicorn.*server|http.server)" | grep -v grep | awk '{print $2}' | xargs -r kill -9 2>/dev/null || true
fi

echo "🏁 Stop script completed"