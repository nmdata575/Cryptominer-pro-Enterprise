#!/usr/bin/env python3
"""
CryptoMiner Pro V30 - Installation Script
Installs dependencies and sets up the mining environment
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print installation banner"""
    banner = """
🚀 CryptoMiner Pro V30 - Installing Dependencies
=================================================
"""
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        sys.exit(1)

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Create virtual environment
    print("🔧 Setting up virtual environment...")
    venv_path = Path("venv")
    
    if not venv_path.exists():
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("   Virtual environment created")
    
    # Activate virtual environment
    print("🔄 Activating virtual environment...")
    if platform.system() == "Windows":
        activate_script = venv_path / "Scripts" / "activate.bat"
        pip_path = venv_path / "Scripts" / "pip"
        python_path = venv_path / "Scripts" / "python"
    else:
        activate_script = venv_path / "bin" / "activate"
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    print("   Virtual environment activated")
    
    # Upgrade pip
    subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    
    # Install requirements
    print("📥 Installing requirements...")
    subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
    
    print("✅ Dependencies installed successfully!")

def create_default_config():
    """Create default configuration file"""
    print("⚙️  Creating default configuration...")
    
    config_content = """# CryptoMiner Pro V30 Configuration Template
# Copy this file and customize for your setup

# Mining Configuration
COIN=LTC
WALLET=your_wallet_address_here
POOL=stratum+tcp://pool.example.com:4444
PASSWORD=worker1

# Performance Settings  
INTENSITY=80
THREADS=auto

# Web Monitoring
WEB_PORT=8001
WEB_ENABLED=true

# AI Optimization
AI_ENABLED=true
AI_LEARNING_RATE=0.1

# Logging
LOG_LEVEL=INFO
LOG_FILE=mining.log
"""
    
    with open("mining_config.template", "w") as f:
        f.write(config_content)
    
    print("   Configuration template created: mining_config.template")

def setup_directories():
    """Create necessary directories"""
    print("📁 Setting up directories...")
    
    directories = ["logs", "data", "models"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   Created directory: {directory}")

def display_completion_message():
    """Display installation completion message"""
    completion_msg = """

🎉 Installation complete!

💡 To run the application:
   python3 cryptominer.py --help
   python3 cryptominer.py --setup

🔧 If using virtual environment, activate it first:
   cd backend && source venv/bin/activate && cd ..

📖 Next steps:
   1. Run: python3 cryptominer.py --setup
   2. Follow the interactive setup wizard
   3. Start mining with your configured settings

🌐 Web monitoring will be available at:
   http://localhost:8001

📚 For more information, see README.md
"""
    print(completion_msg)

def main():
    """Main installation function"""
    try:
        print_banner()
        check_python_version()
        install_dependencies()
        create_default_config()
        setup_directories()
        display_completion_message()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()