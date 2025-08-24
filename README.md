# 🚀 CryptoMiner V21

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Version](https://img.shields.io/badge/version-21.0.0-green.svg)](VERSION)

**Advanced Multi-Algorithm CPU Mining Platform with AI Optimization**

CryptoMiner V21 is an enterprise-grade, intelligent CPU mining solution that supports multiple algorithms including RandomX (Monero) and Scrypt (Litecoin, Dogecoin). Features real-time AI optimization, web-based monitoring, and professional mining pool integration.

## ✨ Key Features

### 🔀 Multi-Algorithm Support
- **RandomX**: Optimized for Monero (XMR) and Aeon mining
- **Scrypt**: Support for Litecoin (LTC), Dogecoin (DOGE)
- **Auto-Detection**: Automatically selects optimal algorithm based on coin
- **Pool Integration**: Real Stratum protocol implementation

### 🤖 AI-Powered Optimization
- **Machine Learning**: Advanced AI models for performance optimization
- **Predictive Analytics**: Share prediction and efficiency analysis
- **Real-time Adaptation**: Dynamic parameter adjustment
- **Performance Learning**: Continuous improvement from mining data

### 📊 Professional Monitoring
- **Web Dashboard**: Real-time browser-based monitoring
- **REST API**: Complete backend API for integration
- **Statistics Tracking**: Comprehensive mining metrics
- **Performance Analytics**: Detailed hashrate and efficiency reports

### ⚡ Enterprise Features
- **Multi-Threading**: Optimized CPU utilization
- **Connection Management**: Robust pool connection handling
- **Error Recovery**: Automatic reconnection and failover
- **Configuration Management**: Flexible configuration system

## 📋 Requirements

### System Requirements
- **OS**: Linux (Ubuntu 18.04+, CentOS 7+, or similar)
- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB (8GB+ recommended for RandomX)
- **CPU**: Modern multi-core processor (Intel/AMD)
- **Network**: Stable internet connection

### Dependencies
- Python 3.8+
- FastAPI
- AsyncIO support
- psutil
- aiohttp
- scikit-learn (for AI features)
- numpy, pandas (for analytics)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/cryptominer-v21.git
cd cryptominer-v21

# Install dependencies
pip install -r requirements.txt

# Make management script executable
chmod +x manage.sh
```

### 2. Configuration

Create your mining configuration:

```bash
# Copy template configuration
cp mining_config.template mining_config.env

# Edit configuration with your details
nano mining_config.env
```

Example configuration:
```env
# Mining Configuration
COIN=XMR
WALLET=your_monero_wallet_address_here
POOL=stratum+tcp://pool.supportxmr.com:3333
PASSWORD=x

# Performance Settings
INTENSITY=80
THREADS=auto

# Web Monitoring
WEB_PORT=3333
WEB_ENABLED=true

# AI Optimization
AI_ENABLED=true
```

### 3. Start Mining

```bash
# Start mining with management script
./manage.sh start

# Or start directly
python3 cryptominer.py
```

### 4. Monitor Performance

- **Web Dashboard**: Open http://localhost:8001 in your browser
- **API Endpoints**: Access REST API at http://localhost:8001/api
- **Logs**: Check `mining.log` for detailed logging

## 📖 Usage Guide

### Command Line Interface

```bash
# Basic usage
python3 cryptominer.py --coin XMR --wallet YOUR_WALLET --pool POOL_URL

# Advanced options
python3 cryptominer.py \
  --coin XMR \
  --wallet YOUR_WALLET \
  --pool stratum+tcp://pool.supportxmr.com:3333 \
  --intensity 90 \
  --threads 8 \
  --password worker1
```

### Management Script

```bash
# Start mining
./manage.sh start

# Stop mining
./manage.sh stop

# Restart mining
./manage.sh restart

# Check status
./manage.sh status

# View logs
./manage.sh logs

# Setup/install dependencies
./manage.sh setup
```

### Web API Usage

```bash
# Get mining statistics
curl http://localhost:8001/api/mining/stats

# Start mining via API
curl -X POST http://localhost:8001/api/mining/control \
  -H "Content-Type: application/json" \
  -d '{"action": "start", "config": {"coin": "XMR", "threads": 4}}'

# Stop mining
curl -X POST http://localhost:8001/api/mining/control \
  -H "Content-Type: application/json" \
  -d '{"action": "stop"}'
```

## ⚙️ Configuration Reference

### Mining Configuration (mining_config.env)

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `COIN` | Cryptocurrency to mine | - | `XMR`, `LTC`, `DOGE` |
| `WALLET` | Your wallet address | - | `48edfHu7V9Z84Yzz...` |
| `POOL` | Mining pool URL | - | `stratum+tcp://pool.supportxmr.com:3333` |
| `PASSWORD` | Pool password/worker | `x` | `worker1` |
| `INTENSITY` | Mining intensity (1-100) | `80` | `90` |
| `THREADS` | Number of threads | `auto` | `8` |
| `WEB_ENABLED` | Enable web monitoring | `true` | `false` |
| `AI_ENABLED` | Enable AI optimization | `true` | `false` |
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG` |

### Supported Coins

| Coin | Algorithm | Description | Recommended Pool |
|------|-----------|-------------|------------------|
| XMR | RandomX | Monero - CPU optimized | pool.supportxmr.com:3333 |
| AEON | RandomX | Aeon - CPU friendly | mine.aeon-pool.com:5555 |
| LTC | Scrypt | Litecoin | stratum.litecoinpool.org:3333 |
| DOGE | Scrypt | Dogecoin | doge.f2pool.com:4444 |

## 🏗️ Architecture

### File Structure
```
cryptominer-v21/
├── cryptominer.py          # Main application entry point
├── mining_engine.py        # Unified mining engine (all algorithms)
├── ai_mining_optimizer.py  # AI optimization system
├── config.py              # Configuration and constants
├── mining_config.env      # User configuration file
├── manage.sh              # Management script
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── backend/
│   ├── server.py         # FastAPI backend server
│   └── requirements.txt  # Backend dependencies
└── logs/
    └── mining.log        # Mining logs
```

### System Components

1. **Mining Engine**: Multi-algorithm mining with RandomX and Scrypt support
2. **AI Optimizer**: Machine learning for performance optimization
3. **Web Backend**: FastAPI-based REST API and monitoring
4. **Configuration**: Centralized configuration management
5. **Monitoring**: Real-time statistics and web dashboard

## 🔧 API Reference

### Mining Control Endpoints

#### Start Mining
```http
POST /api/mining/control
Content-Type: application/json

{
  "action": "start",
  "config": {
    "coin": "XMR",
    "wallet": "your_wallet_address",
    "pool": "stratum+tcp://pool.supportxmr.com:3333",
    "threads": 8,
    "intensity": 90
  }
}
```

#### Stop Mining
```http
POST /api/mining/control
Content-Type: application/json

{
  "action": "stop"
}
```

### Statistics Endpoints

#### Get Mining Statistics
```http
GET /api/mining/stats
```

Response:
```json
{
  "hashrate": 1250.5,
  "coin": "XMR",
  "algorithm": "RandomX",
  "threads": 8,
  "pool_connected": true,
  "shares_good": 15,
  "shares_rejected": 1,
  "uptime": 3600,
  "cpu_usage": 85.2,
  "ai_optimization": 12.5
}
```

#### Get Mining Configuration
```http
GET /api/mining/config
```

### AI Endpoints

#### Get AI Recommendations
```http
GET /api/mining/ai-recommendation
```

#### Update Mining Statistics
```http
POST /api/mining/update-stats
Content-Type: application/json

{
  "hashrate": 1250.5,
  "threads": 8,
  "shares_good": 15,
  "cpu_usage": 85.2
}
```

## 🤖 AI Optimization

### Features
- **Performance Learning**: Analyzes historical mining data
- **Parameter Optimization**: Automatically adjusts mining parameters
- **Predictive Analytics**: Predicts optimal mining conditions
- **Efficiency Analysis**: Tracks and improves mining efficiency

### AI Models
- **Random Forest**: For performance prediction
- **Gradient Boosting**: For optimization recommendations
- **Linear Regression**: For trend analysis
- **Neural Networks**: For complex pattern recognition

### Configuration
```env
# AI Configuration
AI_ENABLED=true
AI_LEARNING_RATE=1.0
AI_OPTIMIZATION_INTERVAL=30
```

## 📊 Monitoring & Analytics

### Web Dashboard Features
- Real-time hashrate monitoring
- Pool connection status
- Share acceptance rates
- CPU and memory usage
- AI optimization status
- Mining profitability estimates

### Key Metrics
- **Hashrate**: Mining speed (H/s, KH/s, MH/s)
- **Shares**: Accepted vs rejected shares
- **Efficiency**: Hashes per watt
- **Uptime**: Mining session duration
- **Temperature**: CPU temperature monitoring
- **Profitability**: Estimated earnings

## 🛠️ Troubleshooting

### Common Issues

#### Connection Problems
```bash
# Check pool connectivity
telnet pool.supportxmr.com 3333

# Test with different pool
# Edit mining_config.env and change POOL setting
```

#### Performance Issues
```bash
# Check system resources
htop
free -h

# Reduce thread count
# Edit mining_config.env: THREADS=4

# Lower intensity
# Edit mining_config.env: INTENSITY=60
```

#### Configuration Errors
```bash
# Validate configuration
python3 -c "from config import config; config.display_config()"

# Check for errors
tail -f mining.log
```

### Debug Mode
```bash
# Enable debug logging
echo "LOG_LEVEL=DEBUG" >> mining_config.env

# Start with verbose output
python3 cryptominer.py --debug
```

## 🚀 Performance Optimization

### CPU Optimization
- Use `THREADS=auto` for automatic optimization
- For RandomX: Use physical cores only (not hyperthreads)
- For Scrypt: Can use all logical cores

### Memory Optimization
- RandomX requires ~2GB per mining thread
- Ensure sufficient RAM for chosen thread count
- Enable huge pages for better performance

### Network Optimization
- Choose geographically close mining pools
- Use low-latency internet connection
- Configure proper pool backup/failover

## 📈 Mining Best Practices

### Pool Selection
- Choose pools with low latency
- Consider pool fees (typically 1-2%)
- Verify pool reputation and reliability
- Use backup pools for failover

### Security
- Never share your private keys
- Use dedicated mining wallets
- Keep software updated
- Monitor for unusual activity

### Profitability
- Calculate electricity costs
- Compare coin profitability
- Consider hardware depreciation
- Monitor market conditions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
```bash
# Clone repository
git clone https://github.com/yourusername/cryptominer-v21.git
cd cryptominer-v21

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Format code
black .
flake8 .
```

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/cryptominer-v21/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/cryptominer-v21/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/cryptominer-v21/discussions)

## 🔄 Changelog

### Version 21.0.0 (Current)
- ✅ Unified multi-algorithm mining engine
- ✅ Real RandomX and Scrypt implementation
- ✅ AI-powered optimization system
- ✅ Professional web dashboard
- ✅ Comprehensive REST API
- ✅ Advanced configuration management
- ✅ Pool connection stability improvements
- ✅ Enhanced error handling and recovery

### Previous Versions
- **v20.x**: Legacy multi-algorithm support
- **v19.x**: Initial AI integration
- **v18.x**: Web monitoring introduction

---

**⚡ Happy Mining! ⚡**

For more information, visit our [documentation](https://github.com/yourusername/cryptominer-v21/wiki) or join our [community discussions](https://github.com/yourusername/cryptominer-v21/discussions).