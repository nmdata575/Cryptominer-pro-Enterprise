# CryptoMiner Pro V30 - Terminal Edition

## 🚀 Enterprise-Grade Terminal Mining Application

A powerful, reliable terminal-based cryptocurrency miner with enterprise features, AI optimization, and optional web monitoring - all in a single compact application.

### ✨ Features

- **🏢 Enterprise Mining Engine** - Supports up to 250,000 mining threads
- **🤖 AI-Powered Optimization** - Intelligent performance tuning
- **⚡ High-Performance Scrypt** - Optimized mining algorithms
- **🔗 Pool & Solo Mining** - Stratum protocol support
- **📊 Optional Web Monitor** - Real-time dashboard at http://localhost:3333
- **🛠️ Simple Terminal Interface** - No complex service management
- **💰 Multi-Coin Support** - Litecoin (LTC), Dogecoin (DOGE), Feathercoin (FTC)

## 🚀 Quick Start

### Prerequisites & Installation

**Important**: Install dependencies before running the application.

```bash
# Ensure Python 3.9+ is installed
python3 --version

# Install dependencies (recommended: use virtual environment)
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..

# Test installation
python3 cryptominer.py --help
```

**Quick Install (Alternative)**:
```bash
# Install system-wide (if virtual environment not preferred)
pip3 install -r backend/requirements.txt
```

### Interactive Setup (Recommended)
```bash
python3 cryptominer.py --setup
```
Follow the guided setup to configure your mining operation.

### Command Line Mining
```bash
# Mine Litecoin with pool
python3 cryptominer.py --coin LTC --wallet ltc1qqvz2zw9hqd804a03xg95m4594p7v7thk25sztl --pool stratum+tcp://litecoinpool.org:3333

# Mine Dogecoin with auto-threads
python3 cryptominer.py --coin DOGE --wallet DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L --pool stratum+tcp://dogepool.com:3333 --threads 16

# List available coins
python3 cryptominer.py --list-coins
```

### Using Configuration Files
```bash
# After running --setup, just run:
python3 cryptominer.py

# Use specific config file
python3 cryptominer.py --config my-setup.json
```

## 📊 Real-Time Interface

### Terminal Interface
```
╔══════════════════════════════════════════════════════════╗
║                  MINING STATISTICS                      ║
╠══════════════════════════════════════════════════════════╣
║  ⏱️  Runtime: 0:15:32                                   ║
║  ⚡ Hashrate: 1.25 MH/s                                 ║
║  🖥️  CPU: 85.2% | Temp: 65.1°C | Threads: 16           ║
║  ✅ Accepted: 42 | ❌ Rejected: 1 | 📊 Efficiency: 97.7% ║
╠══════════════════════════════════════════════════════════╣
║  📊 Web Monitor: http://localhost:3333                  ║
║  🛑 Press Ctrl+C to stop mining                         ║
╚══════════════════════════════════════════════════════════╝
```

### Web Dashboard (Optional)
- **URL:** http://localhost:3333
- **Features:** Real-time hashrate, system stats, efficiency metrics
- **Auto-updates:** Live WebSocket connection every 2 seconds

## ⚙️ Command Line Options

```bash
Usage: python3 cryptominer.py [OPTIONS]

Options:
  --setup              Interactive configuration setup
  --config FILE        Use specific configuration file  
  --coin SYMBOL        Coin to mine (LTC, DOGE, FTC)
  --wallet ADDRESS     Your wallet address
  --pool URL           Pool address (stratum+tcp://pool:port)  
  --threads COUNT      Number of mining threads
  --web-port PORT      Web monitor port (default: 3333, 0 to disable)
  --list-coins         Show available cryptocurrencies
  --verbose, -v        Enable verbose logging
  --help              Show help message

Examples:
  python3 cryptominer.py --setup
  python3 cryptominer.py --list-coins  
  python3 cryptominer.py --coin LTC --wallet ltc1xxx... --pool stratum+tcp://pool.com:3333
  python3 cryptominer.py --config my-ltc-config.json --web-port 8080
```

## 🏊 Supported Mining Pools

### Litecoin (LTC)
- **LitecoinPool:** `stratum+tcp://litecoinpool.org:3333`
- **LuckyMonster:** `stratum+tcp://ltc.luckymonster.pro:4112`
- **F2Pool:** `stratum+tcp://ltc.f2pool.com:4444`

### Dogecoin (DOGE)
- **DogePool:** `stratum+tcp://dogepool.com:3333`
- **LuckyMonster:** `stratum+tcp://doge.luckymonster.pro:4114`
- **Aikapool:** `stratum+tcp://stratum.aikapool.com:7915`

### Feathercoin (FTC)
- **LuckyMonster:** `stratum+tcp://ftc.luckymonster.pro:4116`

## 📁 Configuration Files

Configuration is stored in JSON format for easy management and sharing.

### Example Configuration
```json
{
  "coin": {
    "name": "Litecoin",
    "symbol": "LTC",
    "algorithm": "Scrypt"
  },
  "wallet_address": "ltc1qqvz2zw9hqd804a03xg95m4594p7v7thk25sztl",
  "mode": "pool",
  "pool_address": "stratum+tcp://litecoinpool.org:3333", 
  "threads": 16,
  "web_port": 3333
}
```

### Configuration Management
- **Default:** `mining_config.json` (created by --setup)
- **Custom:** Use `--config filename.json`
- **Example:** See `config.example.json`

## 🚀 Performance Optimization

### Thread Configuration
- **Auto-detect:** Recommended for optimal performance
- **Manual:** Set based on your CPU cores (typically cores × 2)
- **Enterprise:** Up to 250,000 threads for data center deployments

### System Requirements
- **CPU:** Any x86_64 processor
- **RAM:** 2GB minimum, 8GB+ recommended for high thread counts
- **Network:** Stable internet connection for pool mining

### Optimization Tips
1. **Use Interactive Setup** - Automatically detects optimal settings
2. **Monitor System Temperature** - Ensure adequate cooling
3. **Choose Low-Latency Pools** - Better for share submission efficiency
4. **Regular Monitoring** - Use web dashboard for real-time stats

## 🔧 Advanced Usage

### Solo Mining
```bash
python3 cryptominer.py --coin LTC --wallet ltc1address... --threads 32
# Note: Solo mining requires full blockchain node
```

### Development Mode
```bash
python3 cryptominer.py --verbose --web-port 8080 --coin LTC --wallet ADDRESS --pool POOL
```

### Multiple Configurations
```bash
# Create different setups
python3 cryptominer.py --setup  # Save as mining_config.json
cp mining_config.json ltc-home.json
cp mining_config.json doge-office.json

# Use different configs
python3 cryptominer.py --config ltc-home.json
python3 cryptominer.py --config doge-office.json
```

## 🚨 Troubleshooting

### Mining Won't Start
```bash
# Check available coins
python3 cryptominer.py --list-coins

# Validate configuration
python3 cryptominer.py --setup

# Enable verbose logging
python3 cryptominer.py --verbose --coin LTC --wallet ADDRESS --pool POOL
```

### Low Hashrate
- Check CPU temperature and thermal throttling
- Reduce thread count if system is overloaded
- Ensure pool connectivity is stable
- Use `--verbose` to check for errors

### Web Monitor Issues
```bash
# Check if port is in use
netstat -tlnp | grep 3333

# Use different port
python3 cryptominer.py --web-port 8080 --coin LTC --wallet ADDRESS --pool POOL

# Disable web monitoring  
python3 cryptominer.py --web-port 0 --coin LTC --wallet ADDRESS --pool POOL
```

## 📝 Logging

- **Console:** Real-time mining statistics and status updates
- **File:** Detailed logs saved to `mining.log` in current directory  
- **Web:** Browser console shows WebSocket connection status

## 🛡️ Security Notes

- **Wallet Addresses:** Always verify your wallet address before mining
- **Pool Selection:** Use reputable pools with good track records
- **Network Security:** Mining pools use unencrypted connections (normal)
- **System Monitoring:** Monitor CPU temperature to prevent overheating

## 📈 Mining Economics

### Profitability Factors
1. **Hashrate** - Higher is better, but consider electricity costs
2. **Pool Efficiency** - Choose pools with low rejection rates
3. **Network Difficulty** - Varies with overall network hashrate
4. **Electricity Costs** - Major factor in profitability calculations

### Monitoring Tools
- **Built-in Stats** - Real-time hashrate and efficiency
- **Web Dashboard** - Historical performance tracking
- **Pool Websites** - Check your mining progress online

## 🏗️ Architecture

The application is built on proven enterprise components in a simplified structure:

### Core Files
```
/app/
├── cryptominer.py          # Main terminal application
├── config.example.json     # Configuration example
├── README.md              # This documentation
├── DOCUMENTATION.md       # Technical documentation
├── LICENSE                # MIT License
└── backend/               # Core mining modules
    ├── mining_engine.py   # High-performance mining engine
    ├── ai_system.py       # Intelligent optimization
    ├── utils.py           # Coin definitions and utilities
    ├── enterprise_v30.py  # Enterprise mining features
    ├── real_scrypt_miner.py # Scrypt implementation
    ├── randomx_miner.py   # RandomX implementation
    ├── requirements.txt   # Python dependencies
    └── venv/             # Virtual environment
```

### Key Components
- **Mining Engine:** High-performance Scrypt and RandomX implementation
- **AI System:** Intelligent optimization and monitoring
- **System Detection:** Hardware capability analysis
- **Pool Communication:** Full Stratum protocol support
- **Web Interface:** Optional real-time monitoring dashboard

## 🔄 Migration from Service-Based Version

If you're upgrading from the previous complex service-based version:

1. **Backup Configurations** - Export any saved pool configurations
2. **Stop Old Services** (if still running) - `sudo supervisorctl stop all`
3. **Clean Setup** - The new version has already removed old service files
4. **Use New Application** - Run `python3 cryptominer.py --setup`
5. **Enjoy Simplicity** - No more service management needed!

### What Changed
- ✅ **Single executable** - No more separate backend/frontend services
- ✅ **Simplified setup** - No supervisor, MongoDB, or service management
- ✅ **Same features** - All original mining capabilities preserved
- ✅ **Better reliability** - Fewer components mean fewer failure points

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines before submitting PRs.

## 📞 Support

For issues and questions:
- **Documentation:** Check this README and inline help
- **Logs:** Enable `--verbose` mode for detailed troubleshooting
- **Configuration:** Use `--setup` for guided configuration

---

**Happy Mining!** ⛏️💰

*CryptoMiner Pro V30 - Terminal Edition: All the power, none of the complexity.*