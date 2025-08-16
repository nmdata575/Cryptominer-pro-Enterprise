#!/bin/bash

# Quick fix for verification script
# This will update the verification to check actual service responsiveness

INSTALL_DIR="$HOME/CryptominerV30"

echo "🔍 Testing actual service status..."

echo "Testing backend API..."
if curl -s http://localhost:8001/api/health > /dev/null; then
    echo "✅ Backend API is responding on port 8001"
    backend_ok=true
else
    echo "❌ Backend API is not responding"
    backend_ok=false
fi

echo "Testing frontend..."
if curl -s http://localhost:3333 > /dev/null; then
    echo "✅ Frontend is responding on port 3333"
    frontend_ok=true
else
    echo "❌ Frontend is not responding"
    frontend_ok=false
fi

echo "Testing MongoDB..."
if mongosh --eval "db.adminCommand('ping')" &> /dev/null; then
    echo "✅ MongoDB is accessible"
    mongo_ok=true
else
    echo "❌ MongoDB is not accessible"
    mongo_ok=false
fi

echo "Checking installation directory..."
if [ -d "$INSTALL_DIR" ]; then
    echo "✅ Installation directory exists: $INSTALL_DIR"
    dir_ok=true
else
    echo "❌ Installation directory missing: $INSTALL_DIR"
    dir_ok=false
fi

echo "Checking credentials file..."
if [ -f "$INSTALL_DIR/.mongodb_credentials" ]; then
    echo "✅ MongoDB credentials file exists"
    creds_ok=true
else
    echo "❌ MongoDB credentials file missing"
    creds_ok=false
fi

echo ""
echo "=== VERIFICATION SUMMARY ==="
if $backend_ok && $frontend_ok && $mongo_ok && $dir_ok && $creds_ok; then
    echo "🎉 All services are working correctly!"
    echo "✅ Backend: Responding on localhost:8001"
    echo "✅ Frontend: Responding on localhost:3333"  
    echo "✅ MongoDB: Accessible"
    echo "✅ Installation: Complete at $INSTALL_DIR"
    echo "✅ Configuration: MongoDB credentials saved"
    echo ""
    echo "Your CryptoMiner Pro V30 installation is SUCCESSFUL and OPERATIONAL!"
    exit 0
else
    echo "❌ Some issues found - check the details above"
    exit 1
fi