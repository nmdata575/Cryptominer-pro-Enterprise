# CryptoMiner Pro V30 - Terminal Edition Documentation

## Overview

CryptoMiner Pro V30 Terminal Edition is a streamlined, powerful cryptocurrency mining application that runs directly in your terminal with optional web monitoring. This documentation covers installation, configuration, and operation.

## Architecture

The terminal edition is a streamlined, single-file application that imports core modules:

- **cryptominer.py** - Main terminal application with integrated web monitoring
- **backend/mining_engine.py** - Core mining algorithms and engine
- **backend/ai_system.py** - AI optimization system  
- **backend/utils.py** - Utility functions and coin definitions
- **backend/enterprise_v30.py** - Enterprise mining implementations
- **backend/real_scrypt_miner.py** - Scrypt mining implementation
- **backend/randomx_miner.py** - RandomX mining implementation
- **config.example.json** - Example configuration file

## Installation

### Prerequisites
```bash
# Ensure Python 3.9+ is installed
python3 --version

# Install required system packages
sudo apt update
sudo apt install python3-venv python3-pip
```

### Setup
```bash
# Clone or extract the application
cd cryptominer-pro-v30

# Create and activate virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
cd ..
```

## Configuration

### Interactive Setup (Recommended)
```bash
python3 cryptominer.py --setup
```

This will guide you through:
1. Coin selection (LTC, DOGE, FTC)
2. Wallet address validation
3. Mining mode (pool or solo)
4. Thread configuration
5. Web monitoring setup

### Configuration Files

Configurations are stored as JSON files for easy management:

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
  "threads": 8,
  "web_port": 3333
}
```

### Command Line Usage

Direct mining without configuration files:
```bash
python3 cryptominer.py --coin LTC --wallet ADDRESS --pool POOL --threads 16
```

## Mining Operations

### Starting Mining
- **Interactive**: `python3 cryptominer.py --setup`
- **Saved Config**: `python3 cryptominer.py`
- **Command Line**: `python3 cryptominer.py --coin LTC --wallet ADDRESS --pool POOL`

### Stopping Mining
- Press `Ctrl+C` for graceful shutdown
- Mining statistics will be displayed upon exit

### Monitoring
- **Terminal**: Real-time statistics updated every 3 seconds
- **Web Dashboard**: Optional interface at http://localhost:3333
- **Logs**: Detailed logging to `mining.log`

## Supported Cryptocurrencies

### Litecoin (LTC)
- **Algorithm**: Scrypt
- **Popular Pools**: 
  - litecoinpool.org:3333
  - ltc.luckymonster.pro:4112

### Dogecoin (DOGE)
- **Algorithm**: Scrypt
- **Popular Pools**:
  - dogepool.com:3333
  - doge.luckymonster.pro:4114

### Feathercoin (FTC)
- **Algorithm**: Scrypt
- **Popular Pools**:
  - ftc.luckymonster.pro:4116

## Performance Optimization

### Thread Configuration
- **Auto-detection**: Recommended for optimal performance
- **Manual**: Typically CPU cores × 1-2 for best efficiency
- **Enterprise**: Up to 250,000 threads for data center deployments

### System Monitoring
The application monitors:
- CPU usage and temperature
- Mining hashrate and efficiency
- Pool connection status
- Share acceptance/rejection rates

## Troubleshooting

### Common Issues

**Application won't start:**
```bash
# Ensure virtual environment is activated
source backend/venv/bin/activate

# Check for missing dependencies
pip install -r backend/requirements.txt

# Run with verbose logging
python3 cryptominer.py --verbose
```

**Low hashrate:**
- Check CPU temperature for thermal throttling
- Reduce thread count if system is overloaded
- Verify stable network connection to mining pool

**Web monitor not accessible:**
```bash
# Check if port is in use
netstat -tlnp | grep 3333

# Use different port
python3 cryptominer.py --web-port 8080

# Disable web monitoring
python3 cryptominer.py --web-port 0
```

### Performance Issues

**High CPU temperature:**
- Reduce thread count
- Improve system cooling
- Monitor with: `python3 cryptominer.py --verbose`

**Pool connection problems:**
- Test connectivity: `telnet pool.address.com 3333`
- Try alternative pools
- Check firewall settings

## Advanced Features

### AI System Integration
The application includes AI-powered optimization:
- Automatic thread count adjustment
- Pool performance analysis
- Hardware optimization recommendations

### Enterprise Features
- Support for up to 250,000 mining threads
- Enterprise-grade system detection
- Professional logging and monitoring

### Solo Mining
```bash
python3 cryptominer.py --coin LTC --wallet ADDRESS --threads 16
# Note: Solo mining requires full blockchain node
```

## Security Considerations

- Always verify wallet addresses before mining
- Use reputable mining pools
- Monitor system resources to prevent overheating
- Keep software updated for security patches

## Migration from Service Version

If upgrading from the complex service-based version:

1. Stop old services: `sudo supervisorctl stop all`
2. Backup any custom configurations
3. Use the new terminal application: `python3 cryptominer.py --setup`
4. Import previous settings manually if needed

## API Reference

### Web Monitor Endpoints
- **GET /**: Web dashboard interface
- **WebSocket /ws**: Real-time mining statistics

The application provides WebSocket-based real-time updates for web monitoring.

## Logging

### Log Locations
- **Console**: Real-time mining statistics
- **File**: Detailed logs in `mining.log`
- **Web**: Browser console for WebSocket connections

### Log Levels
- **INFO**: Normal operation messages
- **DEBUG**: Detailed debugging (use `--verbose`)
- **ERROR**: Error conditions and failures

## Development

### Code Structure
- **cryptominer.py**: Main application entry point
- **backend/mining_engine.py**: Core mining algorithms
- **backend/ai_system.py**: AI optimization system
- **backend/utils.py**: Utility functions and coin definitions

### Extending Support
To add new cryptocurrencies, update `backend/utils.py` with coin definitions including algorithm parameters, default pools, and wallet validation rules.

## License

This project is licensed under the MIT License - see the LICENSE file for details.