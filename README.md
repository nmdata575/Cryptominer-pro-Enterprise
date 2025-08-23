# 🚀 CryptoMiner V21

**Advanced Multi-Algorithm CPU Mining Platform with AI Optimization**

CryptoMiner V21 is an enterprise-grade distributed mining solution supporting 250,000+ CPU cores with intelligent algorithm switching and AI-driven performance optimization.

### Key Features

- ⚡ **Enterprise Mining Engine** - High-performance multi-threaded mining
- 🤖 **AI Optimization** - Machine learning-driven performance tuning
- 🔗 **Pool & Solo Support** - Connect to any Stratum-compatible pool
- 📊 **Web Monitoring** - Real-time dashboard and statistics
- 🛡️ **Graceful Shutdown** - Proper signal handling and resource cleanup
- 🎯 **Dynamic Configuration** - Adjust mining parameters on-the-fly

### Supported Algorithms

- **Scrypt** - Litecoin (LTC), Dogecoin (DOGE), Vertcoin (VTC)
- **RandomX** - Monero (XMR) *(CPU-friendly)*

## 🚀 Quick Start

### Automated Installation

```bash
# Run the installation script
chmod +x install.sh
./install.sh

# Edit your configuration
nano mining_config.env

# Start mining with integrated web dashboard
./start-integrated.sh
```

### Manual Installation

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv build-essential

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies  
pip install -r requirements.txt

# Configure mining settings
cp mining_config.template mining_config.env
# Edit mining_config.env with your wallet address

# Start mining
python3 cryptominer.py --proxy-mode
```

## 📊 Web Dashboard

The application automatically creates and starts a beautiful web dashboard:

- **URL**: http://localhost:3000
- **Features**: Real-time mining statistics, AI optimization progress, share tracking
- **Backend API**: http://localhost:8001/docs

## 🏗️ Architecture Options

### Proxy Mode (Recommended)
```bash
python3 cryptominer.py --proxy-mode --threads 8
```
- Single connection to pool
- Multiple internal mining threads
- Bypasses pool connection limits
- Maximum efficiency

### Direct Mode
```bash  
python3 cryptominer.py --threads 8
```
- Direct connections to pool
- Traditional mining approach
- May hit pool connection limits

## Command Line Options

```bash
Options:
  --setup                     Run interactive setup wizard
  --list-coins               Show available coins
  --coin COIN                Coin to mine (LTC, DOGE, VTC, XMR)
  --wallet ADDRESS           Your wallet address
  --pool URL                 Mining pool URL
  --password PASSWORD        Pool worker password (optional)
  --intensity PERCENT        Mining intensity 1-100% (default: 80)
  --threads COUNT            Number of threads (default: auto)
  --web-port PORT           Web monitoring port (default: 8001)
  --help                     Show help message
```

## Web Monitoring Dashboard

Access the real-time mining dashboard at: **http://localhost:8001**

### Dashboard Features

- 📊 **Real-time Statistics** - Hashrate, shares, uptime
- ⚙️ **Mining Configuration** - Current settings and status
- 🤖 **AI Metrics** - Learning and optimization progress
- 📈 **Performance Graphs** - Historical data and trends
- 🔗 **Pool Status** - Connection and difficulty information

## Configuration File

Create `mining_config.env` for persistent settings:

```env
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
```

## Popular Mining Pools

### Litecoin (LTC)
- **LitecoinPool**: `stratum+tcp://stratum.litecoinpool.org:3333`
- **F2Pool**: `stratum+tcp://ltc.f2pool.com:4444`
- **ViaBTC**: `stratum+tcp://ltc.viabtc.com:3333`

### Dogecoin (DOGE)
- **Prohashing**: `stratum+tcp://prohashing.com:3333`
- **MultiPool**: `stratum+tcp://stratum.multipool.us:3333`

## AI Optimization

The built-in AI optimizer continuously learns from mining performance and automatically adjusts parameters for optimal results:

- **Learning Progress** - Data collection and model training
- **Optimization Progress** - Performance improvement tracking
- **Automatic Tuning** - Thread count and intensity optimization
- **Performance Prediction** - Forecasting optimal configurations

## Architecture

### Core Components

```
cryptominer.py       # Main application with CLI interface
mining_engine.py     # Mining orchestration and thread management
scrypt_miner.py      # Low-level Scrypt mining and Stratum protocol
ai_optimizer.py      # AI-driven performance optimization
```

### Web Interface

```
backend/server.py    # FastAPI backend with mining APIs
frontend/src/App.js  # React dashboard for monitoring
```

## Troubleshooting

### Common Issues

#### 1. Connection Errors
```bash
# Check pool URL and firewall
telnet pool.example.com 4444
```

#### 2. Authorization Failed
- Verify wallet address format
- Check pool worker password
- Ensure pool supports the coin

#### 3. Low Hashrate
- Increase mining intensity: `--intensity 90`
- Add more threads: `--threads 16`
- Enable AI optimization (default)

#### 4. Shutdown Issues
The application now properly handles Ctrl+C with graceful shutdown:
- All mining threads are stopped
- Socket connections are closed
- Resources are cleaned up
- No hanging processes

### Performance Tuning

#### CPU-Intensive Workloads
```bash
# High performance setup
python3 cryptominer.py --coin LTC --wallet ADDRESS --pool POOL --intensity 95 --threads 16
```

#### Balanced Performance
```bash
# Moderate resource usage
python3 cryptominer.py --coin LTC --wallet ADDRESS --pool POOL --intensity 70 --threads 8
```

## Development

### Project Structure

```
/app/
├── cryptominer.py          # Main application
├── mining_engine.py        # Mining coordination
├── scrypt_miner.py         # Scrypt implementation
├── ai_optimizer.py         # AI optimization
├── install.py              # Installation script
├── requirements.txt        # Python dependencies
├── backend/
│   └── server.py           # FastAPI web API
└── frontend/
    └── src/
        └── App.js          # React dashboard
```

### API Endpoints

```
GET  /api/mining/stats      # Current mining statistics
POST /api/mining/update     # Update mining stats
GET  /api/mining/config     # Mining configuration
POST /api/mining/config     # Update configuration
GET  /api/mining/history    # Performance history
GET  /api/mining/coins      # Available coins
GET  /api/system/info       # System information
```

## Recent Improvements

### v30 Updates
- ✅ **Graceful Shutdown** - Fixed Ctrl+C handling with proper signal management
- ✅ **Password Authentication** - Corrected pool authorization issues
- ✅ **Difficulty Adjustment** - Implemented Bitcoin Wiki difficulty calculation
- ✅ **Connection Stability** - Increased timeouts and better error handling
- ✅ **Performance Optimization** - Replaced custom Scrypt with optimized library
- ✅ **AI Integration** - Enhanced machine learning capabilities
- ✅ **Web Dashboard** - Real-time monitoring interface

### Architecture Evolution
- **From**: Complex supervisor-managed full-stack system
- **To**: Streamlined terminal application with optional web monitoring
- **Benefits**: Easier deployment, better debugging, improved performance

## License

Enterprise Mining License - See LICENSE file for details.

## Support

For technical support and enterprise licensing:
- Documentation: See inline code comments
- Configuration: Use `--setup` for guided configuration
- Web Interface: Monitor at http://localhost:8001
- Logs: Check `mining.log` for detailed operation logs

---

**CryptoMiner Pro V30** - Building the future of distributed mining 🚀
