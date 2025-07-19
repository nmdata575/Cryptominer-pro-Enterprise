# 🚀 CryptoMiner Pro - Complete Setup & Usage Guide

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation Guide](#installation-guide)
3. [Configuration](#configuration)
4. [First Time Setup](#first-time-setup)
5. [Using the Mining System](#using-the-mining-system)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)
8. [Security Best Practices](#security-best-practices)

---

## 🖥️ System Requirements

### Minimum Requirements:
- **OS**: Linux (Ubuntu 18.04+), macOS (10.14+), or Windows 10/11
- **CPU**: Multi-core processor (4+ cores recommended)
- **RAM**: 4GB minimum (8GB+ recommended)
- **Storage**: 2GB free disk space
- **Network**: Stable internet connection

### Recommended Requirements:
- **OS**: Linux Ubuntu 20.04+ (best performance)
- **CPU**: 8+ core processor with good cooling
- **RAM**: 16GB+ for optimal AI performance
- **Storage**: SSD with 10GB+ free space
- **Network**: High-speed broadband connection

### Software Dependencies:
- Node.js 16+ and npm
- Python 3.8+
- MongoDB
- Git

---

## 🔧 Installation Guide

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd crypto-mining-system
```

### Step 2: Backend Setup

#### 2.1 Install Python Dependencies
```bash
cd /app/backend
pip install -r requirements.txt
```

#### 2.2 Set Up Environment Variables
Create `/app/backend/.env` file:
```env
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=crypto_miner_db
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=["http://localhost:3000"]
MAX_THREADS=8
DEFAULT_SCRYPT_N=1024
DEFAULT_SCRYPT_R=1
DEFAULT_SCRYPT_P=1
```

### Step 3: Frontend Setup

#### 3.1 Install Node.js Dependencies
```bash
cd /app/frontend
npm install
```

#### 3.2 Configure Frontend Environment
Create `/app/frontend/.env` file:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
GENERATE_SOURCEMAP=false
FAST_REFRESH=true
```

### Step 4: Database Setup

#### 4.1 Install MongoDB
**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb/brew/mongodb-community
```

**Windows:**
Download and install MongoDB Community Edition from the official website.

#### 4.2 Verify MongoDB Installation
```bash
mongo --version
```

### Step 5: Service Management Setup

#### 5.1 Create Supervisor Configuration
Create `/etc/supervisor/conf.d/mining_app.conf`:
```ini
[program:backend]
command=python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
directory=/app/backend
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/backend.err.log
stdout_logfile=/var/log/supervisor/backend.out.log

[program:frontend]
command=npm start
directory=/app/frontend
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/frontend.err.log
stdout_logfile=/var/log/supervisor/frontend.out.log
environment=PORT=3000

[group:mining_system]
programs=backend,frontend
priority=999
```

#### 5.2 Start Services
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start mining_system:*
```

---

## ⚙️ Configuration

### Step 1: Verify Installation
Check that all services are running:
```bash
sudo supervisorctl status
```

Expected output:
```
mining_system:backend     RUNNING   pid xxxx, uptime x:xx:xx
mining_system:frontend    RUNNING   pid xxxx, uptime x:xx:xx
```

### Step 2: Test Backend API
```bash
curl http://localhost:8001/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-XX-XXTXX:XX:XX.XXXXXX",
  "version": "1.0.0"
}
```

### Step 3: Test Frontend Access
Open browser and navigate to: `http://localhost:3000`

You should see the CryptoMiner Pro dashboard.

---

## 🎯 First Time Setup

### Step 1: Access the Dashboard
1. Open web browser
2. Navigate to `http://localhost:3000`
3. Wait for the dashboard to load completely

### Step 2: Familiarize with the Interface
The dashboard consists of four main sections:
- **Left Panel**: Coin selection and wallet configuration
- **Center Panel**: Mining dashboard and statistics
- **Right Panel**: AI insights and system monitoring
- **Header**: Connection status and controls

### Step 3: System Check
1. Verify **Connection Status** shows "Connected" (green indicator)
2. Check **System Monitor** shows current CPU, memory, and disk usage
3. Confirm **Coin Presets** loads Litecoin, Dogecoin, and Feathercoin options

---

## 🎮 Using the Mining System

### Phase 1: Choose Your Cryptocurrency

#### Step 1: Select Cryptocurrency
1. In the **"Select Cryptocurrency"** panel (top-left)
2. Click on your preferred coin:
   - **Litecoin (LTC)**: Established, moderate difficulty
   - **Dogecoin (DOGE)**: Popular, community-driven
   - **Feathercoin (FTC)**: Lower difficulty, good for testing
3. Review coin details (block reward, difficulty, parameters)

### Phase 2: Configure Your Wallet

#### Step 2A: For Solo Mining
1. In **"Wallet Configuration"** panel:
2. Select **"Solo Mining"** mode
3. Enter your wallet address:
   - **Litecoin**: Address starting with 'L', 'M', '3', or 'ltc1'
   - **Dogecoin**: Address starting with 'D', 'A', or '9'
   - **Feathercoin**: Address starting with '6' or '3'
4. Click **"Check"** to validate address
5. Wait for green checkmark ✅ confirmation

#### Step 2B: For Pool Mining
1. Select **"Pool Mining"** mode
2. Enter **Pool Username**: Usually your_wallet_address.worker_name
3. Enter **Pool Password**: Usually "x" (check your pool's requirements)
4. Verify pool configuration

### Phase 3: Optimize Performance Settings

#### Step 3: Configure Mining Performance
1. In **"Mining Performance"** panel:
2. **Thread Count**: 
   - Start with system recommendation (usually CPU cores - 1)
   - Higher = more power, lower = system stability
3. **Mining Intensity**: 
   - 100% = Maximum performance
   - Lower values = reduced system impact
4. **AI Features**:
   - ✅ Enable AI Optimization (recommended)
   - ✅ Auto-Optimization (let AI adjust settings)

### Phase 4: Start Mining

#### Step 4: Begin Mining Operations
1. Double-check all configurations
2. Click the **"🚀 Start Mining"** button
3. Wait for confirmation message
4. Monitor the **Mining Dashboard** for:
   - Hash rate progression
   - Share statistics
   - System resource usage
   - AI insights and recommendations

### Phase 5: Monitor & Optimize

#### Step 5: Real-time Monitoring
1. **Hash Rate**: Monitor current mining speed
2. **Shares**: Track accepted vs rejected shares
3. **Efficiency**: Aim for >90% efficiency
4. **System Health**: Keep CPU <80%, memory <70%
5. **AI Insights**: Review optimization suggestions

#### Step 6: AI-Powered Optimization
1. Check **AI Insights** panel for:
   - Hash pattern predictions
   - Optimization suggestions
   - Performance recommendations
2. Enable **Auto-Optimization** for automatic adjustments
3. Review **AI Predictions** for optimal settings

---

## 🧠 Advanced Features

### AI Optimization System

#### Understanding AI Features:
1. **Hash Pattern Prediction**: Learns optimal mining patterns
2. **Difficulty Forecasting**: Predicts best mining times
3. **Coin Switching Recommendations**: Suggests most profitable coins
4. **Auto-Optimization**: Automatically adjusts settings

#### Using AI Effectively:
1. Let the system run for at least 30 minutes to collect data
2. Enable all AI features for best results
3. Review AI suggestions in the insights panel
4. Allow auto-optimization for hands-free operation

### Performance Tuning

#### CPU Optimization:
- **Conservative**: 2-4 threads, 50-70% intensity
- **Balanced**: 4-6 threads, 70-90% intensity  
- **Maximum**: 6-8+ threads, 90-100% intensity

#### Memory Management:
- Monitor memory usage in system panel
- Keep memory usage below 80% for stability
- Restart mining if memory usage climbs too high

#### Thermal Management:
- Monitor CPU temperature if available
- Reduce intensity if system gets too hot
- Ensure adequate cooling for sustained operation

---

## 🔧 Troubleshooting

### Common Issues & Solutions

#### Issue: Services Won't Start
```bash
# Check service status
sudo supervisorctl status

# Restart services
sudo supervisorctl restart mining_system:*

# Check logs
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/frontend.err.log
```

#### Issue: Frontend Not Loading
1. Check if service is running: `sudo supervisorctl status mining_system:frontend`
2. Verify port 3000 is accessible: `curl http://localhost:3000`
3. Check for port conflicts: `sudo netstat -tulpn | grep :3000`
4. Clear browser cache and try again

#### Issue: Backend API Errors
1. Test API health: `curl http://localhost:8001/api/health`
2. Check backend logs: `tail -n 50 /var/log/supervisor/backend.err.log`
3. Verify MongoDB is running: `sudo systemctl status mongodb`
4. Restart backend: `sudo supervisorctl restart mining_system:backend`

#### Issue: Database Connection Failed
1. Start MongoDB: `sudo systemctl start mongodb`
2. Check MongoDB status: `sudo systemctl status mongodb`
3. Test connection: `mongo --eval "db.runCommand('ping')"`
4. Verify MONGO_URL in backend/.env

#### Issue: Mining Won't Start
1. **Check wallet address**: Ensure it's valid for selected coin
2. **Verify system resources**: Ensure sufficient CPU/memory
3. **Check error messages**: Review any red error notifications
4. **Try lower settings**: Reduce threads/intensity and retry

#### Issue: Low Hash Rate
1. **Increase threads**: Add more CPU threads if system allows
2. **Increase intensity**: Raise to 90-100% for maximum performance
3. **Check system load**: Ensure no other heavy processes running
4. **Review AI suggestions**: Let AI recommend optimal settings

#### Issue: High Rejected Shares
1. **Check network connection**: Ensure stable internet
2. **Reduce intensity**: Lower mining intensity slightly
3. **Verify wallet address**: Ensure address is correct
4. **Check system stability**: Monitor for system errors

### Getting Help

#### Debug Information Collection:
```bash
# System information
uname -a
python3 --version
node --version
mongo --version

# Service status
sudo supervisorctl status

# Recent logs
tail -n 100 /var/log/supervisor/backend.err.log
tail -n 100 /var/log/supervisor/frontend.err.log

# System resources
top -n 1
df -h
free -h
```

#### Log Locations:
- **Backend Logs**: `/var/log/supervisor/backend.*.log`
- **Frontend Logs**: `/var/log/supervisor/frontend.*.log`
- **MongoDB Logs**: `/var/log/mongodb/mongod.log`
- **System Logs**: `/var/log/syslog`

---

## 🔒 Security Best Practices

### Wallet Security
1. **Never share private keys**: Only use wallet addresses (public keys)
2. **Verify addresses**: Always double-check wallet addresses before mining
3. **Use separate mining wallets**: Don't use your main wallet for mining
4. **Keep backups**: Maintain secure backups of wallet files

### System Security
1. **Keep software updated**: Regularly update all dependencies
2. **Monitor system**: Watch for unusual activity or performance
3. **Secure access**: Use strong passwords and limit system access
4. **Network security**: Consider firewall rules for production use

### Mining Security
1. **Start with small amounts**: Test with low-value configurations first
2. **Monitor continuously**: Watch mining progress and system health
3. **Backup configurations**: Save working configurations
4. **Regular maintenance**: Restart services periodically for stability

---

## 📊 Performance Optimization Tips

### Maximizing Hash Rate:
1. **Use all available CPU cores** (minus 1 for system stability)
2. **Set intensity to 90-100%** if system can handle it
3. **Enable AI optimization** for automatic tuning
4. **Ensure adequate cooling** for sustained performance
5. **Close unnecessary applications** to free up resources

### Maintaining System Stability:
1. **Monitor CPU temperature** and reduce load if overheating
2. **Keep memory usage below 80%** for stability
3. **Restart mining daily** to prevent memory leaks
4. **Update software regularly** for bug fixes and improvements

### Energy Efficiency:
1. **Use AI auto-optimization** to balance power vs performance
2. **Adjust intensity based on electricity costs**
3. **Mine during off-peak hours** when electricity is cheaper
4. **Consider coin switching** based on profitability

---

## 🎉 Success Checklist

✅ **Installation Complete**: All services running without errors  
✅ **Dashboard Accessible**: Web interface loads at localhost:3000  
✅ **Wallet Configured**: Valid wallet address entered and verified  
✅ **Mining Started**: Hash rate showing and shares being accepted  
✅ **AI Active**: AI insights displaying and learning from data  
✅ **System Stable**: CPU/memory usage within acceptable ranges  
✅ **Monitoring Working**: Real-time updates functioning correctly  

---

## 📞 Support & Resources

### Quick Commands Reference:
```bash
# Start all services
sudo supervisorctl start mining_system:*

# Stop all services
sudo supervisorctl stop mining_system:*

# Restart all services
sudo supervisorctl restart mining_system:*

# Check service status
sudo supervisorctl status

# View live backend logs
tail -f /var/log/supervisor/backend.err.log

# View live frontend logs
tail -f /var/log/supervisor/frontend.err.log

# Test API health
curl http://localhost:8001/api/health

# Check system resources
htop
```

### Important URLs:
- **Main Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8001/api/health
- **API Documentation**: http://localhost:8001/docs

---

**🎯 You're now ready to start mining cryptocurrency with AI-powered optimization!**

Remember to start with conservative settings, monitor system performance, and let the AI system learn your optimal configuration over time.