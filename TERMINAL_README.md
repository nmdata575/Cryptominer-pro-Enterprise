# CryptoMiner Pro V30 - Terminal Mining Application

## 🚀 Terminal-Based Mining with Web Monitoring

This version of CryptoMiner Pro V30 runs as a terminal application with an optional web interface for monitoring. No more complex service management - just simple, reliable terminal mining!

## ✅ Benefits

- **Simple & Reliable** - No supervisor, database dependencies, or service management
- **Terminal Control** - Direct feedback, easy debugging, Ctrl+C to stop
- **Web Monitoring** - Optional real-time dashboard at http://localhost:3333
- **Enterprise Features** - Full V30 functionality in a simpler package

## 🛠️ Quick Start

### 1. Setup Environment
```bash
# Activate virtual environment
cd backend
source venv/bin/activate

# Or use the quick start script
./start_mining.sh
```

### 2. Interactive Setup (Recommended)
```bash
python3 mine.py --setup
```

### 3. Command Line Mining
```bash
# Example: Mine Litecoin
python3 mine.py --coin LTC --wallet ltc1qqvz2zw9hqd804a03xg95m4594p7v7thk25sztl --pool stratum+tcp://litecoinpool.org:3333 --threads 8

# List available coins
python3 mine.py --list-coins
```

### 4. Use Saved Configuration  
```bash
# After running --setup, just run:
python3 mine.py
```

## 📋 Command Line Options

```bash
python3 mine.py [OPTIONS]

Options:
  --setup                    Interactive configuration setup
  --config CONFIG_FILE       Use specific configuration file
  --coin SYMBOL              Coin to mine (LTC, DOGE, FTC)
  --wallet ADDRESS           Your wallet address
  --pool POOL_URL            Pool address (stratum+tcp://pool:port)
  --threads COUNT            Number of mining threads
  --web-port PORT            Web monitor port (default: 3333)
  --no-web                   Disable web monitoring
  --list-coins               Show available cryptocurrencies
  --verbose, -v              Verbose logging
  --help                     Show help message
```

## 📊 Web Monitoring

When enabled (default), a web dashboard is available at:
- **URL:** http://localhost:3333
- **Features:** Real-time hashrate, system stats, mining status, efficiency metrics
- **WebSocket:** Live updates every 2 seconds

To disable web monitoring:
```bash
python3 mine.py --no-web --coin LTC --wallet ADDRESS --pool POOL
```

## 🔧 Configuration Files

The application supports JSON configuration files for easy reuse:

### Example Configuration (`mining_config.json`)
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
  "pool_host": "litecoinpool.org",
  "pool_port": 3333,
  "threads": 8,
  "web_port": 3333
}
```

### Using Configuration Files
```bash
# Use default config (mining_config.json)
python3 mine.py

# Use specific config file
python3 mine.py --config my_config.json
```

## 🏊 Supported Pools

### Litecoin (LTC)
- `stratum+tcp://litecoinpool.org:3333`
- `stratum+tcp://ltc.luckymonster.pro:4112`

### Dogecoin (DOGE) 
- `stratum+tcp://doge.luckymonster.pro:4114`
- `stratum+tcp://stratum.aikapool.com:7915`

### Feathercoin (FTC)
- `stratum+tcp://ftc.luckymonster.pro:4116`

## 🎛️ Mining Controls

### Terminal Interface
```bash
⏱️  Runtime: 00:05:32
⚡ Hashrate: 125.4 KH/s  
🖥️  CPU Usage: 45.2%
🌡️  Temperature: 62.5°C
✅ Accepted: 15
❌ Rejected: 0  
📊 Efficiency: 100.00%
🛑 Press Ctrl+C to stop mining
```

### Web Interface
- Real-time statistics dashboard
- System performance monitoring
- Mining efficiency tracking
- Share acceptance rates

## 🚨 Stopping Mining

**Terminal:** Press `Ctrl+C` for graceful shutdown
**Web:** Close terminal or use Ctrl+C

## 🔍 Troubleshooting

### Mining Won't Start
```bash
# Check coin support
python3 mine.py --list-coins

# Validate wallet address
python3 mine.py --setup  # Interactive validation

# Test with verbose logging
python3 mine.py --verbose --coin LTC --wallet ADDRESS --pool POOL
```

### Web Monitor Issues
```bash
# Check if port is available
netstat -tlnp | grep 3333

# Use different port
python3 mine.py --web-port 8080 --coin LTC --wallet ADDRESS --pool POOL

# Disable web monitoring
python3 mine.py --no-web --coin LTC --wallet ADDRESS --pool POOL
```

### Performance Issues
```bash
# Auto-detect optimal threads
python3 mine.py --setup  # Choose option 1 for thread config

# Manually set lower thread count
python3 mine.py --threads 4 --coin LTC --wallet ADDRESS --pool POOL
```

## 📝 Logging

- **Terminal Output:** Real-time mining statistics and status
- **Log File:** `mining.log` contains detailed operation logs
- **Web Logs:** Browser console shows WebSocket connection status

## 🔧 Advanced Usage

### Custom Thread Configuration
```bash
# Auto-detect optimal (recommended)
python3 mine.py --setup

# Manual thread count
python3 mine.py --threads 16 --coin LTC --wallet ADDRESS --pool POOL

# Maximum performance (use with caution)
python3 mine.py --threads 64 --coin LTC --wallet ADDRESS --pool POOL
```

### Solo Mining
```bash
# Solo mining (no pool required)
python3 mine.py --coin LTC --wallet ltc1address... --threads 8
```

### Development Mode
```bash
# Verbose output with web monitoring
python3 mine.py --verbose --web-port 8080 --coin LTC --wallet ADDRESS --pool POOL
```

## 💡 Tips

1. **Start with Interactive Setup** - Use `--setup` for guided configuration
2. **Monitor Web Dashboard** - Keep http://localhost:3333 open for real-time stats  
3. **Save Configurations** - Use JSON files for different mining setups
4. **Optimal Threads** - Let the system auto-detect for best performance
5. **Pool Selection** - Choose pools with low latency for better efficiency

## 🏗️ Integration

This terminal application uses all the existing CryptoMiner Pro V30 components:
- **Mining Engine:** Enterprise-grade Scrypt implementation
- **AI System:** Intelligent optimization and predictions  
- **System Detection:** Hardware capability analysis
- **Pool Management:** Stratum protocol support
- **Web Monitoring:** Real-time dashboard interface

The difference is the simplified execution model - no supervisor, no database dependencies, just pure mining power! 🚀