#!/bin/bash

# CryptoMiner Pro - Python Environment Diagnostic Script

echo "=== Python Environment Diagnostics ==="
echo

echo "1. Python Version:"
python3 --version
echo

echo "2. Python3 Location:"
which python3
echo

echo "3. Python3 Venv Module:"
python3 -m venv --help > /dev/null 2>&1 && echo "✅ venv module available" || echo "❌ venv module missing"
echo

echo "4. Pip3 Status:"
which pip3 && pip3 --version || echo "❌ pip3 not found"
echo

echo "5. Virtual Environment Test:"
echo "Creating test virtual environment..."
mkdir -p /tmp/test-venv
cd /tmp/test-venv

if python3 -m venv test-env; then
    echo "✅ Virtual environment creation successful"
    if [ -f "test-env/bin/python3" ]; then
        echo "✅ Python3 binary exists in venv"
    else
        echo "❌ Python3 binary missing from venv"
    fi
    rm -rf test-env
else
    echo "❌ Virtual environment creation failed"
fi
cd - > /dev/null
echo

echo "6. Required Packages:"
packages=("python3-venv" "python3-pip" "python3-dev" "build-essential")
for pkg in "${packages[@]}"; do
    if dpkg -l | grep -q "^ii  $pkg "; then
        echo "✅ $pkg installed"
    else
        echo "❌ $pkg missing"
    fi
done
echo

echo "7. Disk Space:"
df -h /tmp
echo

echo "8. Installation Directory Check:"
if [ -d "/opt/cryptominer-pro" ]; then
    echo "✅ Installation directory exists"
    ls -la /opt/cryptominer-pro/
else
    echo "❌ Installation directory missing"
fi
echo

echo "9. Current Working Directory:"
pwd
ls -la
echo

echo "=== Diagnostic Complete ==="
echo
echo "If you see any ❌ marks above, those need to be fixed."
echo "Common fixes:"
echo "  - Install missing packages: sudo apt update && sudo apt install python3-venv python3-pip python3-dev"
echo "  - Free up disk space if /tmp is full"
echo "  - Run the setup script from the correct directory (where backend/ and frontend/ folders exist)"