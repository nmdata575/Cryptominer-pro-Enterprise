# CryptoMiner Pro - Consolidated Documentation

## 🚀 Overview

CryptoMiner Pro is an AI-powered Scrypt cryptocurrency mining platform with advanced web controls and real-time monitoring. The platform has been consolidated from 59+ files down to exactly 20 files while maintaining all functionality.

### ⚡ Key Features

- **AI-Powered Mining**: Advanced machine learning for hash pattern prediction and optimization
- **Multi-Coin Support**: Litecoin (LTC), Dogecoin (DOGE), Feathercoin (FTC)
- **Smart Pool Management**: Custom pool connections with real-time testing
- **Dynamic Thread Optimization**: Auto-detection of optimal CPU core usage
- **Real-time Monitoring**: WebSocket-powered live updates
- **Role-based Dashboard**: Organized sections for different mining aspects

### 🏗️ Architecture

**Backend (Python FastAPI)**
- `server.py` - Main API server with WebSocket support
- `mining_engine.py` - Scrypt mining engine and pool management
- `ai_system.py` - AI optimization and prediction system
- `utils.py` - Utility functions and validation

**Frontend (React)**
- `App.js` - Main application component
- `MiningDashboard.js` - Consolidated mining interface
- `SystemComponents.js` - System controls and monitoring
- `AIComponents.js` - AI insights and optimization

**Configuration**
- Consolidated CSS styles, package configurations, and environment setup

## 🛠️ Installation

### Quick Installation (Ubuntu 24+)

```bash
# Clone or download CryptoMiner Pro
cd cryptominer-pro

# Run the unified installation script
chmod +x install.sh
sudo ./install.sh

# Start the application
./start.sh
```

### Manual Installation

**Backend Setup:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend Setup:**
```bash
cd frontend
yarn install
```

**Start Services:**
```bash
# Backend
cd backend && source venv/bin/activate && uvicorn server:app --host 0.0.0.0 --port 8001

# Frontend
cd frontend && yarn start
```

## 📊 AI System Features

### Hash Pattern Prediction
- Real-time analysis of mining patterns
- Predictive hashrate modeling using scikit-learn
- Confidence scoring for predictions

### Network Difficulty Forecasting
- Analysis of network difficulty trends
- 24-hour prediction horizon
- Market-based difficulty adjustments

### Pool Performance Analysis
- Real-time latency monitoring
- Share acceptance rate tracking
- Automatic pool optimization recommendations

### Mining Optimization
- Dynamic thread count adjustment
- CPU usage optimization
- Memory efficiency monitoring
- Performance grading system (A+ to D)

## 🎯 Mining Profiles

### Light Mining (50% cores)
- Minimal system impact
- Background mining capability
- Ideal for daily computer use

### Standard Mining (75% cores)
- Balanced performance
- Optimal efficiency
- Recommended for most users

### Maximum Mining (100% cores)
- Full system utilization
- Maximum hashrate
- Dedicated mining systems

## 🔧 Configuration

### Wallet Setup
**Litecoin (LTC):**
- Legacy: L/M prefix (26-35 chars)
- Bech32: ltc1 prefix (39-59 chars)
- Multisig: 3 prefix (26-35 chars)

**Dogecoin (DOGE):**
- Standard: D prefix (26-34 chars)
- Multisig: 9/A prefix (26-34 chars)

**Feathercoin (FTC):**
- Standard: 6/7 prefix (26-34 chars)

### Pool Configuration
```json
{
  "mode": "pool",
  "custom_pool_address": "stratum+tcp://ltc.luckymonster.pro",
  "custom_pool_port": 4112,
  "pool_username": "your_wallet_address",
  "pool_password": "d=24000"
}
```

### Solo Mining Configuration
```json
{
  "mode": "solo",
  "wallet_address": "your_wallet_address",
  "custom_rpc_host": "127.0.0.1",
  "custom_rpc_port": 9332,
  "custom_rpc_username": "rpcuser",
  "custom_rpc_password": "rpcpass"
}
```

## 📈 Monitoring & Analytics

### Real-time Metrics
- Hashrate (H/s, KH/s, MH/s, GH/s, TH/s)
- Accepted/Rejected shares
- CPU and memory usage
- Mining efficiency score
- System health status

### Performance Grading
- **A+**: >50 efficiency score (Excellent)
- **A**: 30-50 efficiency score (Very Good)
- **B**: 20-30 efficiency score (Good)
- **C**: 10-20 efficiency score (Average)
- **D**: <10 efficiency score (Poor)

### AI Learning Progress
- Data point collection
- Model training status
- Prediction accuracy
- Optimization recommendations

## 🔗 API Endpoints

### Mining Control
- `GET /api/health` - System health check
- `GET /api/coins/presets` - Available cryptocurrencies
- `POST /api/mining/start` - Start mining
- `POST /api/mining/stop` - Stop mining
- `GET /api/mining/status` - Mining status

### System Information
- `GET /api/system/stats` - System statistics
- `GET /api/system/cpu-info` - CPU information

### AI System
- `GET /api/mining/ai-insights` - AI predictions and insights
- `GET /api/ai/status` - AI system status
- `POST /api/ai/auto-optimize` - Trigger auto-optimization

### Pool/RPC Testing
- `POST /api/pool/test-connection` - Test pool connection
- `POST /api/validate_wallet` - Validate wallet address

### WebSocket
- `ws://localhost:8001/ws` - Real-time updates

## 🛡️ Security Features

- Wallet address validation for all supported coins
- Secure RPC connection handling
- Input sanitization and validation
- Environment variable protection
- Safe mining parameter limits

## 🚨 Troubleshooting

### Common Issues

**Installation Fails:**
```bash
# Clean installation
sudo ./install.sh --clean

# Use fallback packages
cp backend/requirements-fallback.txt backend/requirements.txt
pip install -r backend/requirements.txt
```

**Mining Won't Start:**
- Check wallet address format
- Verify pool connection with test button
- Ensure adequate system resources
- Check backend logs: `tail -f backend/backend.log`

**AI System Not Working:**
- AI requires mining data to learn
- Start mining to begin AI training
- Check AI status in dashboard
- Verify scikit-learn installation

**WebSocket Connection Issues:**
- Check firewall settings
- Verify port 8001 availability
- Restart backend service
- Clear browser cache

### Log Files
- Backend: `backend/backend.log`
- Frontend: Browser console
- System: `sudo journalctl -u cryptominer-pro`

## 📋 System Requirements

### Minimum Requirements
- CPU: 2+ cores
- RAM: 4GB
- Storage: 2GB free space
- OS: Ubuntu 20.04+ or compatible Linux

### Recommended Requirements
- CPU: 8+ cores (for optimal mining)
- RAM: 8GB+
- Storage: 5GB free space
- Network: Stable internet connection

### Supported Cryptocurrencies
- **Litecoin (LTC)**: Primary focus, full feature support
- **Dogecoin (DOGE)**: Complete implementation
- **Feathercoin (FTC)**: Full support with validation

## 🔄 Updates and Maintenance

### Regular Maintenance
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Restart mining services
sudo supervisorctl restart all

# Clean logs (optional)
sudo journalctl --vacuum-time=7d
```

### Performance Optimization
1. Monitor system resources during mining
2. Adjust thread count based on AI recommendations
3. Use appropriate mining profile for your use case
4. Keep system updated and clean

## 📞 Support

### Getting Help
1. Check troubleshooting section above
2. Review log files for error details
3. Verify system requirements
4. Test with different mining configurations

### Reporting Issues
Include the following information:
- System specifications
- Error messages from logs
- Mining configuration used
- Steps to reproduce the issue

## 📄 License

This project is open source. See LICENSE file for details.

---

**Built with ❤️ by the CryptoMiner Pro Team**

*AI-Powered Mining for the Modern Era*