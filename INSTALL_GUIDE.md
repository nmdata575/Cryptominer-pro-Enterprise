# 🤖 CryptoMiner Pro - Automated Ubuntu Installation Guide

## 📋 Overview

The automated installation script provides a **one-click solution** to install CryptoMiner Pro with all dependencies on Ubuntu 24.04+ systems. This script handles everything from system updates to service configuration.

## 🎯 What the Automated Installer Does

### 📦 **Complete Dependency Installation**
- ✅ **System Updates**: Updates all packages to latest versions
- ✅ **Python 3.12+**: Latest Python with development tools
- ✅ **Node.js 20 LTS**: Latest stable Node.js with npm and Yarn
- ✅ **MongoDB 7.0**: Latest MongoDB Community Edition
- ✅ **Build Tools**: GCC, make, and development libraries
- ✅ **System Tools**: Supervisor, UFW firewall, monitoring tools

### 🏗️ **Application Setup**
- ✅ **Project Structure**: Creates organized directory layout
- ✅ **Source Code**: Installs complete CryptoMiner Pro application
- ✅ **Dependencies**: Installs all Python and Node.js packages
- ✅ **Configuration**: Sets up environment files and database
- ✅ **Services**: Configures systemd and supervisor services

### 🔧 **System Configuration**
- ✅ **Service Management**: Supervisor configuration for auto-restart
- ✅ **Firewall Setup**: UFW rules for necessary ports
- ✅ **User Permissions**: Proper ownership and security settings
- ✅ **Management Scripts**: Command-line tools for easy management
- ✅ **Desktop Integration**: Launcher shortcuts

---

## ⚡ Quick Installation (Recommended)

### **For Fresh Ubuntu 24.04+ Systems:**

```bash
# 1. Download and run the installer
sudo curl -fsSL https://your-domain.com/install-ubuntu.sh | bash

# OR if you have the script locally:
chmod +x install-ubuntu.sh
sudo ./install-ubuntu.sh
```

### **That's it!** 🎉
- The script will handle everything automatically
- Access your dashboard at: **http://localhost:3000**
- Total installation time: ~10-15 minutes

---

## 📋 Detailed Installation Process

### **Step 1: System Preparation**

#### **System Requirements Check:**
```bash
# Minimum Requirements (Checked Automatically):
• Ubuntu 24.04+ (required)
• 2GB+ RAM (4GB+ recommended)
• 2GB+ free disk space (5GB+ recommended)  
• 2+ CPU cores (4+ recommended)
• Internet connection
```

#### **Pre-installation Verification:**
```bash
# Check Ubuntu version
lsb_release -a

# Check available resources
free -h                    # Memory
df -h                     # Disk space
nproc                     # CPU cores

# Ensure system is up to date (optional, script will do this)
sudo apt update && sudo apt upgrade -y
```

### **Step 2: Download Installation Script**

#### **Method 1: Direct Download**
```bash
# Download the installer script
wget https://your-domain.com/install-ubuntu.sh

# Make it executable
chmod +x install-ubuntu.sh

# Review the script (recommended)
less install-ubuntu.sh
```

#### **Method 2: Git Clone (if available)**
```bash
# Clone the repository
git clone https://github.com/your-repo/cryptominer-pro.git
cd cryptominer-pro

# The script is ready to use
ls -la install-ubuntu.sh
```

### **Step 3: Run Installation**

#### **Interactive Installation (Recommended):**
```bash
# Run with confirmation prompts
sudo ./install-ubuntu.sh
```

#### **Silent Installation:**
```bash
# Skip confirmations (use with caution)
echo "y" | sudo ./install-ubuntu.sh
```

#### **Help and Options:**
```bash
# View help information
sudo ./install-ubuntu.sh --help

# Check script version
sudo ./install-ubuntu.sh --version
```

### **Step 4: Installation Progress**

The installer will show detailed progress through these phases:

```
🔄 STEP: Checking System Compatibility
🔄 STEP: Updating System Packages  
🔄 STEP: Installing Node.js 20 LTS
🔄 STEP: Setting up Python Environment
🔄 STEP: Installing MongoDB 7.0
🔄 STEP: Creating Project Structure
🔄 STEP: Installing CryptoMiner Pro Application
🔄 STEP: Installing Application Source Code
🔄 STEP: Configuring Service Management
🔄 STEP: Configuring Firewall
🔄 STEP: Creating Management Scripts
🔄 STEP: Starting CryptoMiner Pro Services
🔄 STEP: Verifying Installation
🔄 STEP: Creating Desktop Integration
```

### **Step 5: Post-Installation Verification**

After installation completes, verify everything is working:

```bash
# Check service status
cryptominer-status

# Test web interfaces
curl http://localhost:8001/api/health    # Backend API
curl -I http://localhost:3000            # Frontend

# View logs if needed
cryptominer-logs
```

---

## 🗂️ Installation Locations

### **Default Installation Paths:**
```bash
📁 Main Application:           /opt/cryptominer-pro/
📁 Backend Code:               /opt/cryptominer-pro/backend/
📁 Frontend Code:              /opt/cryptominer-pro/frontend/
📁 Logs:                      /opt/cryptominer-pro/logs/
📁 Scripts:                   /opt/cryptominer-pro/scripts/

📄 Backend Config:            /opt/cryptominer-pro/backend/.env
📄 Frontend Config:           /opt/cryptominer-pro/frontend/.env
📄 Supervisor Config:         /etc/supervisor/conf.d/cryptominer-pro.conf
📄 Installation Log:          /tmp/cryptominer-install.log
```

### **System Integration:**
```bash
🔧 Management Commands:       /usr/local/bin/cryptominer-*
🖥️ Desktop Launcher:          ~/Desktop/CryptoMiner-Pro.desktop
🔥 Firewall Rules:            UFW ports 3000, 8001, 27017
📋 System Services:           systemctl/supervisorctl
```

---

## 🛠️ Management Commands

The installer creates convenient command-line tools:

### **Service Management:**
```bash
cryptominer-start      # Start all services
cryptominer-stop       # Stop all services  
cryptominer-restart    # Restart all services
cryptominer-status     # Show service status and system info
cryptominer-logs       # View application logs
```

### **Manual Service Control:**
```bash
# Using supervisor directly
sudo supervisorctl status cryptominer-pro:*
sudo supervisorctl start cryptominer-pro:*
sudo supervisorctl stop cryptominer-pro:*
sudo supervisorctl restart cryptominer-pro:*

# Individual services
sudo supervisorctl restart cryptominer-pro:cryptominer-backend
sudo supervisorctl restart cryptominer-pro:cryptominer-frontend
```

---

## 🔍 Troubleshooting Installation

### **Common Installation Issues:**

#### **Issue: Permission Denied**
```bash
# Solution: Ensure running with sudo
sudo ./install-ubuntu.sh
```

#### **Issue: Package Installation Fails**
```bash
# Check internet connection
ping google.com

# Update package lists manually
sudo apt update

# Re-run installer
sudo ./install-ubuntu.sh
```

#### **Issue: MongoDB Connection Failed**
```bash
# Check MongoDB status
sudo systemctl status mongod

# Start MongoDB manually
sudo systemctl start mongod

# Test connection
mongosh --eval "db.adminCommand('ismaster')"
```

#### **Issue: Services Won't Start**
```bash
# Check logs
cryptominer-logs

# Check supervisor status
sudo supervisorctl status

# Restart supervisor
sudo systemctl restart supervisor

# Manual service start
sudo supervisorctl start cryptominer-pro:*
```

#### **Issue: Frontend/Backend Not Accessible**
```bash
# Check if ports are open
sudo netstat -tulpn | grep -E "(3000|8001)"

# Check firewall
sudo ufw status

# Test services directly
curl http://localhost:8001/api/health
curl -I http://localhost:3000
```

### **Installation Logs:**
```bash
# View installation log
cat /tmp/cryptominer-install.log

# View service logs
cryptominer-logs

# View system logs
sudo journalctl -u supervisor
```

---

## 🔧 Advanced Installation Options

### **Custom Installation Directory:**
```bash
# Modify the script to use custom directory
sudo sed -i 's|PROJECT_DIR="/opt/cryptominer-pro"|PROJECT_DIR="/your/custom/path"|' install-ubuntu.sh
sudo ./install-ubuntu.sh
```

### **Selective Component Installation:**
```bash
# Edit the script to comment out unwanted components
# For example, to skip MongoDB installation:
sudo nano install-ubuntu.sh
# Comment out the install_mongodb function call
```

### **Development Installation:**
```bash
# For development setups, you might want to:
# 1. Install in user directory instead of /opt
# 2. Use development dependencies
# 3. Enable debug modes
# 4. Skip production optimizations
```

---

## 🗑️ Uninstallation

### **Complete Removal:**
```bash
# Download and run uninstaller
sudo curl -fsSL https://your-domain.com/uninstall-ubuntu.sh | bash

# Or if you have it locally
chmod +x uninstall-ubuntu.sh
sudo ./uninstall-ubuntu.sh
```

### **Uninstaller Options:**
```bash
# Remove everything including dependencies
sudo ./uninstall-ubuntu.sh --remove-mongodb --remove-nodejs --reset-firewall

# View uninstaller help
sudo ./uninstall-ubuntu.sh --help
```

---

## 🚀 Quick Start After Installation

### **Immediate Next Steps:**

1. **🌐 Access Dashboard:**
   ```bash
   # Open in browser:
   http://localhost:3000
   ```

2. **⚙️ Check System Status:**
   ```bash
   cryptominer-status
   ```

3. **🎯 Configure Mining:**
   - Select cryptocurrency (Litecoin recommended for beginners)
   - Enter wallet address (will be validated)
   - Set performance options
   - Enable AI optimization

4. **🚀 Start Mining:**
   - Click "Start Mining" button
   - Monitor dashboard for real-time statistics
   - Watch AI insights for optimization

### **First-Time Configuration:**
```bash
# Backend configuration (if needed)
sudo nano /opt/cryptominer-pro/backend/.env

# Frontend configuration (if needed) 
sudo nano /opt/cryptominer-pro/frontend/.env

# Restart after configuration changes
cryptominer-restart
```

---

## 📊 System Requirements & Performance

### **Minimum System Requirements:**
| Component | Minimum | Recommended | Optimal |
|-----------|---------|-------------|---------|
| **OS** | Ubuntu 24.04 | Ubuntu 24.04 LTS | Ubuntu 24.04 LTS |
| **RAM** | 2GB | 4GB | 8GB+ |
| **CPU** | 2 cores | 4 cores | 8+ cores |
| **Storage** | 2GB | 5GB | 10GB+ |
| **Network** | 1 Mbps | 10 Mbps | 100 Mbps+ |

### **Expected Installation Time:**
- **Fast System (SSD, 8+ cores)**: 5-8 minutes
- **Average System**: 10-15 minutes  
- **Slower System (HDD, 2-4 cores)**: 15-25 minutes

### **Network Usage:**
- **Package Downloads**: ~200-500MB
- **Ongoing Usage**: ~10-50MB per hour (depending on mining activity)

---

## 🔒 Security Considerations

### **Firewall Configuration:**
```bash
# Ports opened by installer:
• 22/tcp    (SSH - if enabled)
• 3000/tcp  (Frontend Dashboard)
• 8001/tcp  (Backend API) 
• 27017/tcp (MongoDB - local only)
```

### **Security Best Practices:**
- ✅ Change default passwords after installation
- ✅ Review firewall rules for your network setup
- ✅ Only enter wallet addresses, never private keys
- ✅ Monitor system resources during operation
- ✅ Keep system updated: `sudo apt update && sudo apt upgrade`

### **Production Deployment:**
```bash
# For production use, consider:
• Using reverse proxy (nginx/apache)
• Enabling HTTPS with SSL certificates
• Restricting network access
• Setting up monitoring and alerting
• Regular backups of configuration and data
```

---

## 📞 Support & Resources

### **Getting Help:**
- 📋 **Installation Log**: `/tmp/cryptominer-install.log`
- 📄 **Service Logs**: `cryptominer-logs`
- 🔍 **System Status**: `cryptominer-status`
- 🌐 **Dashboard**: `http://localhost:3000`
- 🔧 **API Health**: `http://localhost:8001/api/health`

### **Community & Documentation:**
- 📖 **Setup Guide**: `SETUP_GUIDE.md`
- 🎯 **Quick Reference**: `QUICK_REFERENCE.md`
- 📚 **Full Documentation**: `README.md`

---

<div align="center">

**🎉 Ready to mine cryptocurrency with AI optimization!**

**The automated installer makes setup effortless on Ubuntu 24+**

</div>