# 📋 CryptoMiner Pro V30 - Complete Dependencies List

## 🖥️ **SYSTEM REQUIREMENTS**

### **Operating System**
- **Required**: Ubuntu 20.04+ (24.04 recommended)
- **Architecture**: x86_64 (amd64) or ARM64 (aarch64)
- **Kernel**: Linux 5.4+
- **Memory**: Minimum 8GB RAM (64GB+ recommended for enterprise)
- **Storage**: 50GB+ free disk space
- **CPU**: 4+ cores (16+ cores recommended for profitable mining)

### **Network Requirements**
- **Internet Connection**: Broadband (10+ Mbps for pool mining)
- **Firewall**: Allow outbound connections on ports 3333, 5555, 8001
- **DNS**: Working DNS resolution

---

## 🐍 **PYTHON DEPENDENCIES**

### **Python Runtime**
- **Python**: 3.11+ (3.12+ recommended)
- **pip**: Latest version (23.0+)
- **venv**: Python virtual environment support
- **setuptools**: Latest version

### **Core Framework Dependencies**
```txt
fastapi==0.110.0              # Main web framework
uvicorn[standard]==0.27.0     # ASGI server with performance features
websockets==12.0              # WebSocket support for real-time updates
python-multipart==0.0.7       # File upload and form processing
aiofiles==23.2.1               # Async file operations
```

### **Cryptography & Mining Dependencies**
```txt
cryptography==42.0.0          # Core cryptographic operations
scrypt==0.8.20                 # Scrypt algorithm for mining
base58==2.1.1                  # Base58 encoding for wallet addresses
hashlib (built-in)             # Hash functions (SHA256, SHA3, Blake2b)
struct (built-in)              # Binary data handling
```

### **Database Dependencies**
```txt
pymongo==4.6.1                # MongoDB driver (sync)
motor==3.3.2                   # MongoDB async driver
```

### **AI & Machine Learning Dependencies**
```txt
numpy==1.26.4                  # Numerical computing
scikit-learn==1.4.0           # Machine learning algorithms
pandas==2.2.1                 # Data manipulation and analysis
```

### **System & Utility Dependencies**
```txt
psutil==5.9.8                 # System monitoring (CPU, memory, etc.)
requests==2.31.0              # HTTP client library
python-dotenv==1.0.0          # Environment variable loading
pydantic==2.6.0               # Data validation and settings
```

### **Development & Testing Dependencies**
```txt
pytest==8.0.0                 # Testing framework
pytest-asyncio==0.23.0        # Async testing support
```

### **Python Built-in Modules Used**
- `asyncio` - Asynchronous programming
- `json` - JSON data handling
- `logging` - Application logging
- `time` - Time operations
- `socket` - Network socket operations
- `threading` - Multi-threading support
- `multiprocessing` - Multi-processing support
- `os` - Operating system interface
- `sys` - System-specific parameters
- `pathlib` - Object-oriented filesystem paths
- `subprocess` - Process management
- `signal` - Signal handling
- `traceback` - Exception tracebacks

---

## 📱 **NODE.JS & FRONTEND DEPENDENCIES**

### **Node.js Runtime**
- **Node.js**: 18.0+ (20.19+ recommended)
- **npm**: 10.0+ (latest recommended)
- **Yarn**: 1.22+ (recommended package manager)

### **React Framework Dependencies**
```json
"react": "^18.2.0"             # Core React library
"react-dom": "^18.2.0"         # React DOM renderer
"react-scripts": "5.0.1"       # Build tools and dev server
```

### **UI & Styling Dependencies**
```json
"@heroicons/react": "^2.0.18"  # Icon library
"tailwindcss": "^3.3.6"        # Utility-first CSS framework
"autoprefixer": "^10.4.16"     # CSS vendor prefixing
"postcss": "^8.4.32"           # CSS processing tool
"classnames": "^2.3.2"         # Conditional CSS classes
```

### **Data Visualization Dependencies**
```json
"chart.js": "^4.4.0"           # Charting library
"react-chartjs-2": "^5.2.0"    # React wrapper for Chart.js
```

### **Network & Communication Dependencies**
```json
"axios": "^1.6.0"              # HTTP client library
"socket.io-client": "^4.7.4"   # WebSocket client for real-time updates
```

### **Testing Dependencies**
```json
"@testing-library/jest-dom": "^5.17.0"      # Jest DOM matchers
"@testing-library/react": "^13.4.0"         # React testing utilities
"@testing-library/user-event": "^14.5.0"    # User event simulation
"web-vitals": "^2.1.4"                      # Performance metrics
```

---

## 🗄️ **DATABASE DEPENDENCIES**

### **MongoDB**
- **Version**: 7.0.22+ (8.0+ recommended)
- **Configuration**: WiredTiger storage engine
- **Memory**: 2GB+ allocated to MongoDB
- **Storage**: 10GB+ for database files

### **MongoDB Configuration Requirements**
```yaml
storage:
  dbPath: /data/db
  journal:
    enabled: true
    
net:
  port: 27017
  bindIp: 127.0.0.1
  maxIncomingConnections: 2000

operationProfiling:
  slowOpThresholdMs: 1000
```

---

## 🔧 **SYSTEM TOOLS & UTILITIES**

### **Essential System Packages**
```bash
curl                    # HTTP client for API testing
wget                    # File downloading
git                     # Version control (for updates)
build-essential         # Compilation tools (gcc, make, etc.)
pkg-config              # Package configuration tool
libssl-dev              # SSL development libraries
libffi-dev              # Foreign Function Interface library
python3-dev             # Python development headers
python3-venv            # Python virtual environment
```

### **Process Management**
```bash
supervisor              # Process control system
supervisorctl           # Supervisor command-line tool
```

### **Network Tools**
```bash
netstat                 # Network connection monitoring
ss                      # Socket statistics
lsof                    # List open files and network connections
```

### **System Monitoring**
```bash
htop                    # Enhanced process viewer
iotop                   # I/O monitoring
nethogs                 # Network usage per process
```

---

## 🚀 **SERVICE DEPENDENCIES**

### **Supervisor Configuration**
- **Service**: supervisor
- **Config File**: `/etc/supervisor/conf.d/mining_app.conf`
- **Commands**: supervisorctl start/stop/restart

### **SystemD Services (Alternative)**
- **MongoDB**: systemd service management
- **Custom Services**: Optional systemd integration

---

## 🌐 **NETWORK & MINING DEPENDENCIES**

### **Mining Pool Connections**
- **Stratum Protocol**: TCP socket connections
- **SSL/TLS**: For secure pool connections
- **DNS Resolution**: For pool hostname resolution

### **Supported Mining Pools**
- **Litecoin**: LitecoinPool.org (port 3333)
- **Monero**: SupportXMR (port 5555)
- **EFL**: LuckyDogPool (port 7026)
- **Custom Pools**: User-configurable

### **Cryptocurrency Libraries**
- **Address Validation**: Base58, Bech32 support
- **Hash Functions**: SHA256, Scrypt, RandomX
- **Network Protocols**: Stratum, JSON-RPC

---

## 🔐 **SECURITY DEPENDENCIES**

### **Cryptographic Libraries**
- **OpenSSL**: 3.0+ for encryption
- **libssl**: SSL/TLS support
- **Random Number Generation**: /dev/urandom access

### **File Permissions**
- **Application Files**: 644 (readable)
- **Scripts**: 755 (executable)
- **Configuration**: 600 (secure)
- **Logs**: 644 (readable)

---

## 💻 **HARDWARE DEPENDENCIES**

### **CPU Requirements**
- **Architecture**: x86_64 or ARM64
- **Cores**: 4+ (16+ recommended)
- **Instructions**: SSE2, AES-NI (for performance)
- **Cache**: L3 cache recommended for mining

### **Memory Requirements**
- **System RAM**: 8GB minimum (64GB+ enterprise)
- **Virtual Memory**: 16GB+ swap recommended
- **MongoDB**: 2-4GB dedicated memory

### **Storage Requirements**
- **System**: 20GB for OS and applications
- **Database**: 10GB for mining data
- **Logs**: 5GB for application logs
- **Temp**: 5GB for temporary files

### **Network Hardware**
- **Ethernet**: Gigabit recommended for enterprise
- **WiFi**: 802.11n minimum (enterprise should use wired)

---

## 🔧 **DEVELOPMENT DEPENDENCIES (Optional)**

### **Code Development**
```bash
git                     # Version control
vim/nano               # Text editors
code                   # Visual Studio Code (optional)
```

### **Build Tools**
```bash
gcc                    # GNU Compiler Collection
make                   # Build automation
cmake                  # Cross-platform build system
```

### **Python Development**
```bash
python3-pip           # Python package installer
python3-setuptools    # Python packaging tools
python3-wheel         # Python wheel format support
```

---

## 📦 **PACKAGE INSTALLATION COMMANDS**

### **Ubuntu/Debian System Packages**
```bash
# Update package lists
sudo apt update

# Essential system packages
sudo apt install -y curl wget git build-essential pkg-config
sudo apt install -y libssl-dev libffi-dev python3-dev python3-venv
sudo apt install -y supervisor netstat-persistent htop

# MongoDB (if not using Docker)
sudo apt install -y mongodb-org

# Node.js (via NodeSource)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Yarn package manager
npm install -g yarn
```

### **Python Packages (via pip)**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install all Python dependencies
pip install -r requirements.txt
```

### **Frontend Packages (via Yarn)**
```bash
# Install Node.js dependencies
cd frontend
yarn install
```

---

## 🎯 **VERIFICATION COMMANDS**

### **Check All Dependencies**
```bash
# Python and packages
python3 --version
pip list

# Node.js and packages
node --version
npm --version
yarn --version

# Database
mongod --version
mongo --eval "db.runCommand('ismaster')"

# System tools
curl --version
git --version
supervisorctl version

# System resources
free -h
df -h
lscpu
```

### **Service Status**
```bash
# Check running services
sudo supervisorctl status
sudo systemctl status mongodb
ps aux | grep -E "python|node|mongod"

# Check network ports
netstat -tulpn | grep -E "8001|3333|27017"
```

---

## 🚨 **CRITICAL DEPENDENCIES**

### **Absolutely Required (Will Not Work Without)**
1. **Python 3.11+** - Core runtime
2. **Node.js 18+** - Frontend runtime
3. **MongoDB 7.0+** - Database storage
4. **Supervisor** - Process management
5. **Internet Connection** - Mining pool access

### **Highly Recommended (Major Impact if Missing)**
1. **8GB+ RAM** - Performance and stability
2. **Multi-core CPU** - Mining efficiency
3. **SSD Storage** - Database performance
4. **Yarn** - Better package management
5. **Build Tools** - Compilation support

### **Optional but Beneficial**
1. **htop/iotop** - System monitoring
2. **Git** - Updates and version control
3. **SSL Libraries** - Secure connections
4. **Swap Space** - Memory overflow protection

---

## ✅ **INSTALLATION VERIFICATION CHECKLIST**

- [ ] **Python 3.11+ installed and working**
- [ ] **All Python packages from requirements.txt installed**
- [ ] **Node.js 18+ and Yarn installed**
- [ ] **All frontend packages installed via yarn**
- [ ] **MongoDB 7.0+ running and accessible**
- [ ] **Supervisor configured and running**
- [ ] **Backend API responding on port 8001**
- [ ] **Frontend serving on port 3333**
- [ ] **Database connection established**
- [ ] **Mining engine functional**
- [ ] **All system resources adequate**

---

## 🎉 **COMPLETE DEPENDENCY SUMMARY**

**Total Dependencies**: 50+ packages and tools
**Core Languages**: Python, JavaScript, JSON, YAML, Bash
**Frameworks**: FastAPI, React, MongoDB
**Protocols**: HTTP/HTTPS, WebSocket, Stratum, JSON-RPC
**Platforms**: Linux (Ubuntu/Debian preferred)

This complete dependency list ensures CryptoMiner Pro V30 runs optimally with all features functional!