#!/bin/bash

# CryptoMiner Pro V30 - Stop Script
# Stops all CryptoMiner Pro V30 processes

echo "🛑 Stopping CryptoMiner Pro V30..."

# Stop all related processes
echo "Stopping mining processes..."
pkill -f "python3.*cryptominer" 2>/dev/null || true

echo "Stopping backend API server..."
pkill -f "uvicorn.*server" 2>/dev/null || true

echo "Stopping web dashboard server..."
pkill -f "http.server" 2>/dev/null || true

# Wait a moment for processes to stop
sleep 2

# Check if any processes are still running
REMAINING=$(ps aux | grep -E "(python3.*cryptominer|uvicorn.*server|http.server)" | grep -v grep | wc -l)

if [[ $REMAINING -eq 0 ]]; then
    echo "✅ All CryptoMiner Pro V30 processes stopped successfully"
else
    echo "⚠️  Some processes may still be running. You may need to stop them manually."
    echo "Running processes:"
    ps aux | grep -E "(python3.*cryptominer|uvicorn.*server|http.server)" | grep -v grep
fi

echo "🏁 Stop script completed"