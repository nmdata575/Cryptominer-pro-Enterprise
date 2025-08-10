#!/bin/bash

# Test Ubuntu Version Detection Script

echo "=== Ubuntu Version Detection Test ==="
echo

# Method 1: lsb_release
echo "1. Using lsb_release:"
if command -v lsb_release &> /dev/null; then
    echo "   Codename: $(lsb_release -cs)"
    echo "   Description: $(lsb_release -ds)"
    echo "   Release: $(lsb_release -rs)"
else
    echo "   lsb_release not available"
fi
echo

# Method 2: /etc/os-release
echo "2. Using /etc/os-release:"
if [ -f /etc/os-release ]; then
    source /etc/os-release
    echo "   NAME: $NAME"
    echo "   VERSION: $VERSION"
    echo "   VERSION_CODENAME: $VERSION_CODENAME"
    echo "   UBUNTU_CODENAME: $UBUNTU_CODENAME"
else
    echo "   /etc/os-release not found"
fi
echo

# Method 3: Python availability test
echo "3. Python Version Availability Test:"
for py_version in python3 python3.8 python3.9 python3.10 python3.11 python3.12 python3.13; do
    if command -v $py_version &> /dev/null; then
        version=$($py_version --version 2>&1)
        echo "   ✅ $py_version: $version"
    else
        echo "   ❌ $py_version: Not available"
    fi
done
echo

# Method 4: Package availability check
echo "4. Python Package Availability in Repositories:"
echo "   Checking what Python packages are available..."

if command -v apt-cache &> /dev/null; then
    for py_pkg in python3.11 python3.12 python3.13; do
        if apt-cache show $py_pkg &> /dev/null; then
            echo "   ✅ $py_pkg: Available in repositories"
        else
            echo "   ❌ $py_pkg: Not available in standard repositories"
        fi
    done
else
    echo "   apt-cache not available"
fi
echo

echo "=== Test Complete ==="
echo
echo "Recommended Python version for your system:"

# Detect Ubuntu version
ubuntu_version=$(lsb_release -cs 2>/dev/null || echo "unknown")
python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2 || echo "unknown")

echo "Current system: Ubuntu $ubuntu_version with Python $python_version"

case "$ubuntu_version" in
    "noble"|"24.04")
        echo "Recommendation: Use Python 3.12 (available from standard Ubuntu repositories)"
        ;;
    "jammy"|"22.04")
        echo "Recommendation: Use Python 3.11 or install Python 3.12 via deadsnakes PPA"
        ;;
    "focal"|"20.04")
        echo "Recommendation: Install Python 3.12 via deadsnakes PPA"
        ;;
    *)
        echo "Recommendation: Install Python 3.12 for best compatibility"
        ;;
esac