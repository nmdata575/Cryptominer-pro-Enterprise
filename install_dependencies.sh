#!/bin/bash
# CryptoMiner Pro V30 - Quick Dependency Installation Script

echo "🚀 CryptoMiner Pro V30 - Installing Dependencies"
echo "================================================="

# Check Python version
echo "🔍 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1)
echo "   $PYTHON_VERSION"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "❌ Backend directory not found. Please run this script from the cryptominer-pro-v30 directory."
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
cd backend

# Try to install in virtual environment first
echo "🔧 Setting up virtual environment..."
python3 -m venv venv 2>/dev/null || echo "⚠️  Virtual environment already exists or couldn't be created"

if [ -f "venv/bin/activate" ]; then
    echo "🔄 Activating virtual environment..."
    source venv/bin/activate
    echo "   Virtual environment activated"
fi

echo "📥 Installing requirements..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
    cd ..
    echo ""
    echo "🎉 Installation complete!"
    echo ""
    echo "💡 To run the application:"
    echo "   python3 cryptominer.py --help"
    echo "   python3 cryptominer.py --setup"
    echo ""
    echo "🔧 If using virtual environment, activate it first:"
    echo "   cd backend && source venv/bin/activate && cd .."
else
    echo "❌ Failed to install dependencies"
    echo ""
    echo "🔧 Try manual installation:"
    echo "   pip3 install psutil fastapi uvicorn numpy scikit-learn pymongo"
    exit 1
fi