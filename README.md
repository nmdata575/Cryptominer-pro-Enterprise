# CryptoMiner Pro - Enterprise V30 Edition

**Advanced Cryptocurrency Mining System with AI Optimization and Distributed Mining Capabilities**

## 🚀 Quick Start

```bash
# Installation (Ubuntu 24+)
sudo ./setup.sh --install

# Start mining
sudo supervisorctl start mining_system:all

# Access dashboard
http://localhost:3334
```

## 🏗️ Streamlined Architecture

```
/opt/cryptominer-pro/
├── backend/
│   ├── server.py                    # Main FastAPI server
│   ├── mining_engine.py             # Core mining functionality
│   ├── ai_system.py                 # AI optimization system
│   ├── real_scrypt_miner.py         # cgminer-compatible Scrypt implementation
│   ├── enterprise_v30.py            # Consolidated V30 enterprise features
│   ├── v30_protocol.py              # Distributed mining protocol
│   ├── gpu_mining_engine.py         # GPU mining support
│   └── utils.py                     # Utility functions
├── frontend/
│   ├── src/
│   │   ├── App.js                   # Main application
│   │   ├── styles.css               # Consolidated styles
│   │   └── components/
│   │       ├── MiningDashboard.js   # Core mining interface
│   │       ├── SystemComponents.js  # System monitoring
│   │       ├── AIComponents.js      # AI assistant
│   │       ├── EnterpriseThreadManager.js # Thread management
│   │       ├── EnterpriseDBConfig.js # Database configuration
│   │       └── AdvancedComponents.js # Pool/coin management
├── v30-remote-node/                 # Remote mining node
├── setup.sh                         # Unified installation script
├── uninstall.sh                     # Complete removal script
└── Documentation/                   # Guides and documentation
```

## ✨ Key Features

### 🏪 **Pool Management System**
- Save frequently used pool configurations
- Quick-launch mining with one click
- EFL, LTC, DOGE, and custom coin support
- Wallet address validation

### 🪙 **Custom Coin Support**
- Add any cryptocurrency with custom parameters
- Support for multiple algorithms (Scrypt, SHA-256, X11, etc.)
- Configurable Scrypt parameters (N, R, P values)
- Database-backed persistence

### ⛏️ **Enterprise Mining (V30)**
- Scale to 250,000+ CPU threads
- Distributed mining across multiple nodes
- GPU acceleration (NVIDIA CUDA + AMD OpenCL)
- Real-time performance monitoring
- Load balancing and auto-failover

### 🤖 **AI-Powered Optimization**
- Automatic thread adjustment
- Pool performance analysis
- Hash pattern prediction
- Efficiency recommendations

### 🛠️ **Management Tools**
- Web-based dashboard at `http://localhost:3334`
- Real-time WebSocket updates
- Comprehensive system monitoring
- Enterprise licensing system

## 📋 Installation Requirements

**Minimum:**
- Ubuntu 24+ (other distros supported but not tested)
- 4GB RAM, 8GB recommended
- 4 CPU cores minimum
- 10GB free disk space

**Enterprise V30:**
- 64GB RAM (512GB recommended)
- 32+ CPU cores
- 1Gbps network connection
- GPU(s) for optimal performance

## 🔧 Management Commands

```bash
# Service Management
sudo supervisorctl status mining_system:all    # Check status
sudo supervisorctl start mining_system:all     # Start services  
sudo supervisorctl restart mining_system:all   # Restart services
sudo supervisorctl stop mining_system:all      # Stop services

# Installation Modes
./setup.sh --install                   # Fresh installation
./setup.sh --frontend-fix              # Fix frontend issues
./setup.sh --restart-services          # Restart services
./setup.sh --status                    # Check service status

# Complete Removal
./uninstall.sh                         # Basic uninstall with backup
./uninstall.sh --cleanup-database      # Remove database data
./uninstall.sh --remove-deps           # Remove dependencies
```

## 🔍 Troubleshooting

**Service Issues:**
```bash
# Check logs
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/frontend.out.log

# Restart specific service
sudo supervisorctl restart mining_system:backend
sudo supervisorctl restart mining_system:frontend
```

**Database Issues:**
```bash
# Restart MongoDB
sudo systemctl restart mongodb
sudo systemctl status mongodb
```

**Port Conflicts:**
```bash
# Check port usage
sudo lsof -i :8001  # Backend port
sudo lsof -i :3334  # Frontend port

# Kill conflicting processes
sudo kill -9 <PID>
```

## 📊 API Endpoints

- **Health Check:** `GET /api/health`
- **Mining Control:** `POST /api/mining/start|stop`
- **Pool Management:** `GET|POST|PUT|DELETE /api/pools/saved`
- **Custom Coins:** `GET|POST|PUT|DELETE /api/coins/custom`
- **Enterprise V30:** `POST /api/v30/system/initialize`

## 🔐 Enterprise Licensing

The V30 Enterprise edition includes 5000 pre-generated license keys. Each license enables:
- Distributed mining control
- Advanced hardware validation  
- GPU acceleration support
- Custom mining protocols
- Enterprise monitoring
- Load balancing & auto-failover

## 🌐 Remote Node Setup

Deploy remote mining nodes:
```bash
cd v30-remote-node/
sudo ./install.sh
# Configure with your license key and server details
```

## 📈 Performance Optimization

1. **Thread Configuration:** Use Enterprise Thread Manager for optimal CPU utilization
2. **GPU Mining:** Enable CUDA/ROCm for hybrid CPU+GPU mining
3. **Pool Selection:** Use saved pool configurations for lowest latency
4. **AI Optimization:** Enable automatic optimization for best efficiency
5. **Network:** Ensure stable 1Gbps+ connection for enterprise features

## 🛡️ Security Considerations

- Configure firewall rules for distributed mining ports
- Use secure wallet addresses and pool credentials
- Regular backup of pool configurations and custom coins
- Monitor system resources and network usage

## 📞 Support

- Configuration backup: `~/cryptominer-pro-backup-YYYYMMDD-HHMMSS/`
- Log files: `/var/log/supervisor/`
- Installation directory: `/opt/cryptominer-pro/`

---

**CryptoMiner Pro V30** - Professional cryptocurrency mining with enterprise scalability and AI optimization.