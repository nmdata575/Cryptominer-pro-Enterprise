#!/bin/bash
echo "🚀 CryptoMiner Pro V30 - Environment Setup Script"
echo "This script will help you set up the fixed environment"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run as root (sudo ./setup_environment.sh)"
  exit 1
fi

echo "📁 Current directory contents:"
ls -la

echo ""
echo "🔧 Setup Steps:"
echo "1. Install system dependencies (MongoDB, Node.js, Python, etc.)"
echo "2. Set up virtual environments" 
echo "3. Install backend dependencies (pip install -r backend/requirements.txt)"
echo "4. Install frontend dependencies (cd frontend && yarn install)"
echo "5. Configure supervisor with the provided config"
echo "6. Start MongoDB"
echo "7. Run the installation script (./install.sh --status)"
echo ""
echo "💡 For detailed setup instructions, see DOCUMENTATION.md"
echo "💡 For troubleshooting, see test_result.md"
echo ""
echo "🏃‍♂️ Quick start command: ./install.sh"
