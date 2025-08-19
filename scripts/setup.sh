#!/bin/bash
# CryptoMiner Pro V30 - Setup Script

set -e

echo "🔧 Setting up CryptoMiner Pro V30..."

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    echo "✅ Python $PYTHON_VERSION is compatible"
else
    echo "❌ Python $REQUIRED_VERSION or higher required. Found: $PYTHON_VERSION"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/db logs models

# Setup Python virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup frontend if Node.js is available
if command -v node >/dev/null 2>&1; then
    echo "📱 Setting up frontend..."
    cd frontend
    
    # Install yarn if not available
    if ! command -v yarn >/dev/null 2>&1; then
        echo "📦 Installing Yarn..."
        npm install -g yarn
    fi
    
    # Install dependencies
    yarn install
    cd ..
    
    echo "✅ Frontend setup complete"
else
    echo "⚠️ Node.js not found. Frontend setup skipped."
    echo "   Install Node.js to use the web dashboard."
fi

# Create default configuration
echo "⚙️ Creating default configuration..."
if [ ! -f "mining_config.env" ]; then
    cp mining_config.template mining_config.env
    echo "📝 Created mining_config.env - please edit with your settings"
fi

# Make scripts executable
chmod +x scripts/*.sh

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit mining_config.env with your wallet and pool settings"
echo "2. Start services: ./scripts/start.sh"
echo "3. Run miner: python3 cryptominer.py"
echo "4. View dashboard: http://localhost:3000"
echo ""
echo "For help: python3 cryptominer.py --help"