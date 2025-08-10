# CryptoMiner Enterprise V30 - Remote Mining Node

🚀 **Lightweight terminal-based mining node for distributed cryptocurrency mining**

The V30 Remote Node connects to a CryptoMiner Enterprise V30 central server to participate in distributed mining operations. This node handles all mining work assigned by the central control system and reports back results and statistics.

## 🎯 **Features**

### **Core Mining Capabilities**
- **Distributed Mining**: Connects to V30 central server for work distribution
- **Multi-Algorithm Support**: Scrypt-based cryptocurrency mining
- **CPU Mining**: Utilizes all available CPU cores efficiently
- **GPU Detection**: Automatic detection of NVIDIA and AMD GPUs
- **Real-time Statistics**: Live hashrate and performance monitoring

### **Enterprise Integration**
- **License Validation**: Secure V30 enterprise license key authentication
- **Auto-Discovery**: Automatic system capability detection and reporting
- **Load Balancing**: Receives work assignments based on node capabilities
- **Heartbeat Monitoring**: Regular health checks with central server

### **Management & Monitoring**
- **Terminal Interface**: Lightweight console-based operation
- **Systemd Service**: Professional system service integration
- **Automatic Updates**: Self-updating from central server
- **Comprehensive Logging**: Detailed operation and error logs

## 📋 **System Requirements**

### **Minimum Requirements**
- **OS**: Ubuntu 18.04+, Debian 10+, CentOS 7+, RHEL 7+
- **CPU**: 2+ cores (more cores = better performance)
- **RAM**: 2GB minimum (4GB+ recommended)
- **Network**: 100 Mbps internet connection
- **Python**: 3.8 or higher

### **Recommended for Optimal Performance**
- **CPU**: 8+ cores for efficient mining
- **RAM**: 8GB+ for smooth operation
- **Network**: 1 Gbps+ for enterprise operations
- **Storage**: SSD for faster operations

### **Enterprise Scale**
- **CPU**: 32+ cores (supports up to 250,000+ cores)
- **RAM**: 64GB+ (512GB recommended for large operations)
- **Network**: 1+ Gbps dedicated connection
- **GPUs**: NVIDIA and/or AMD GPUs supported

## 🚀 **Quick Installation**

### **1. Download the Remote Node**
```bash
# Download the installation files
wget https://your-v30-server.com/downloads/v30-remote-node.tar.gz
tar -xzf v30-remote-node.tar.gz
cd v30-remote-node
```

### **2. Run the Installation Script**
```bash
# Make sure you're in the v30-remote-node directory
sudo ./install.sh
```

The installer will:
- ✅ Install system dependencies (Python, pip, etc.)
- ✅ Create dedicated user account (`v30miner`)
- ✅ Set up Python virtual environment
- ✅ Install the mining node application
- ✅ Configure systemd service
- ✅ Create management scripts
- ✅ Set up logging and monitoring

### **3. Configure Your Node**
During installation, you'll be prompted for:
- **V30 Server Host**: IP address or hostname of your central server
- **V30 Server Port**: Usually 9001 (default)
- **Enterprise License Key**: Your V30 enterprise license key

## ⚙️ **Configuration**

### **Configuration File**: `/opt/cryptominer-v30-node/node_config.json`

```json
{
  "server_host": "your.v30.server.com",
  "server_port": 9001,
  "license_key": "YOUR-V30-ENTERPRISE-LICENSE-KEY",
  "max_cpu_threads": 16,
  "enable_gpu": true,
  "heartbeat_interval": 30.0,
  "work_request_interval": 10.0,
  "auto_update": true,
  "update_check_interval": 3600.0
}
```

### **Configuration Options**
- `server_host`: V30 central server hostname/IP
- `server_port`: V30 server port (default: 9001)
- `license_key`: Your V30 enterprise license key
- `max_cpu_threads`: Maximum CPU threads to use
- `enable_gpu`: Enable GPU mining (if available)
- `heartbeat_interval`: Seconds between heartbeats (default: 30)
- `work_request_interval`: Seconds between work requests (default: 10)
- `auto_update`: Enable automatic updates (default: true)
- `update_check_interval`: Seconds between update checks (default: 3600)

## 🔧 **Management Commands**

### **Service Management**
```bash
# Start the mining node
sudo systemctl start cryptominer-v30-node

# Stop the mining node
sudo systemctl stop cryptominer-v30-node

# Check service status
sudo systemctl status cryptominer-v30-node

# Enable auto-start on boot
sudo systemctl enable cryptominer-v30-node

# View live logs
sudo journalctl -u cryptominer-v30-node -f
```

### **Quick Management Scripts**
```bash
# Check node status and recent logs
/opt/cryptominer-v30-node/status.sh

# View live logs
/opt/cryptominer-v30-node/logs.sh

# Start the service
/opt/cryptominer-v30-node/start.sh

# Stop the service
/opt/cryptominer-v30-node/stop.sh
```

## 📊 **Monitoring & Logs**

### **Log Locations**
- **Service Logs**: `/opt/cryptominer-v30-node/logs/node.log`
- **Error Logs**: `/opt/cryptominer-v30-node/logs/error.log`
- **System Logs**: `journalctl -u cryptominer-v30-node`

### **Key Log Messages**
```
✅ Successfully registered with V30 server    # Node connected
🚀 Mining started - Work ID: work_123        # Received mining work
🎯 Share found! Hash: 0000abc123...          # Found mining share
📊 Work result received from server          # Completed work assignment
🔍 Checking for updates...                   # Auto-update check
```

## 🔄 **Updates & Maintenance**

### **Automatic Updates**
The node automatically checks for updates from the central server every hour (configurable). When updates are available, they're downloaded and applied automatically.

### **Manual Updates**
```bash
# Check for updates manually
sudo systemctl stop cryptominer-v30-node
cd /opt/cryptominer-v30-node
sudo wget https://your-v30-server.com/updates/v30_remote_node.py
sudo chown v30miner:v30miner v30_remote_node.py
sudo systemctl start cryptominer-v30-node
```

### **Version Management**
```bash
# Check current version
/opt/cryptominer-v30-node/venv/bin/python /opt/cryptominer-v30-node/v30_remote_node.py --version

# View update history
cat /opt/cryptominer-v30-node/logs/updates.log
```

## 🛡️ **Security**

### **Security Features**
- **Dedicated User**: Runs under `v30miner` user (not root)
- **Secure Configuration**: Config file permissions restricted
- **License Validation**: Enterprise license key verification
- **Encrypted Communication**: Secure protocol with central server

### **Network Security**
- **Outbound Only**: Only connects to central server
- **Firewall Ready**: Automatic firewall configuration
- **No Incoming Connections**: Client-only operation

## 🔍 **Troubleshooting**

### **Common Issues**

#### **Connection Failed**
```
❌ Failed to connect to server.example.com:9001
```
**Solutions:**
- Check network connectivity: `ping server.example.com`
- Verify server port is accessible: `telnet server.example.com 9001`
- Check firewall settings on both node and server
- Ensure V30 central server is running

#### **License Invalid**
```
❌ Registration rejected: Invalid license
```
**Solutions:**
- Verify your enterprise license key is correct
- Check with V30 server administrator
- Ensure license hasn't expired
- Check server logs for license validation errors

#### **Service Won't Start**
```bash
# Check service status
sudo systemctl status cryptominer-v30-node

# Check detailed logs
sudo journalctl -u cryptominer-v30-node -f

# Check configuration
cat /opt/cryptominer-v30-node/node_config.json
```

#### **No Work Received**
```
⏳ No work available from server
```
**Solutions:**
- Check if mining is active on central server
- Verify node registration was successful
- Check server logs for work distribution
- Ensure proper license and capabilities

### **Performance Issues**

#### **Low Hashrate**
- Check CPU usage: `htop`
- Verify all cores are being used
- Check system temperature
- Ensure no other intensive processes running

#### **High Memory Usage**
- Monitor memory: `free -h`
- Check for memory leaks in logs
- Consider reducing `max_cpu_threads`
- Restart service if memory usage grows

## 📞 **Support**

### **Getting Help**
1. **Check Logs**: Always check logs first for error details
2. **Server Administrator**: Contact your V30 server administrator
3. **Documentation**: Review V30 central server documentation
4. **System Status**: Use status scripts to gather information

### **Information to Provide**
When requesting support, please include:
- Node ID (found in logs or config)
- Operating system and version
- Error messages from logs
- V30 server details
- System specifications (CPU, RAM, network)

## 📂 **File Structure**

```
/opt/cryptominer-v30-node/
├── v30_remote_node.py      # Main application
├── node_config.json        # Configuration file
├── venv/                   # Python virtual environment
├── logs/                   # Log files
│   ├── node.log           # Application logs
│   └── error.log          # Error logs
├── data/                   # Application data
├── updates/                # Update cache
└── scripts/                # Management scripts
    ├── start.sh
    ├── stop.sh
    ├── status.sh
    └── logs.sh
```

## 📜 **License**

This software requires a valid CryptoMiner Enterprise V30 license key to operate. Contact your system administrator for license information.

---

**CryptoMiner Enterprise V30 Remote Node** - Distributed cryptocurrency mining for enterprise environments.