# 🎯 CryptoMiner Pro - Quick Reference Card

## ⚡ 5-Minute Quick Start

### 1. **Access Dashboard**
```
🌐 Open: http://localhost:3000
```

### 2. **Choose Cryptocurrency**
| Coin | Best For | Difficulty | Block Reward |
|------|----------|------------|--------------|
| **Litecoin (LTC)** | Established mining | Medium | 12.5 LTC |
| **Dogecoin (DOGE)** | Community, fun | Medium | 10,000 DOGE |
| **Feathercoin (FTC)** | Beginners, testing | Lower | 200 FTC |

### 3. **Configure Wallet**
```
Solo Mining: Enter wallet address → Click "Check" → ✅
Pool Mining: Enter username.worker → Enter password
```

### 4. **Set Performance**
```
Conservative: 2-4 threads, 50% intensity
Balanced:     4-6 threads, 75% intensity  
Maximum:      6-8 threads, 90% intensity
```

### 5. **Start Mining**
```
🚀 Click "Start Mining" → Monitor dashboard
```

---

## 📱 Dashboard Overview

```
┌─────────────────┬─────────────────────┬──────────────────┐
│   COIN & WALLET │    MINING STATS     │   AI & SYSTEM    │
├─────────────────┼─────────────────────┼──────────────────┤
│ • Coin Selector │ • Hash Rate (Live)  │ • AI Predictions │
│ • Wallet Config │ • Accepted Shares   │ • Optimization   │
│ • Mining Mode   │ • Rejected Shares   │ • System Monitor │
│ • Performance   │ • Blocks Found      │ • Performance    │
│   Controls      │ • Efficiency %      │   Insights       │
└─────────────────┴─────────────────────┴──────────────────┘
```

---

## 💰 Wallet Address Formats

### Litecoin (LTC)
```
✅ Legacy:    L1234567890abcdefghijk...     (34 chars)
✅ SegWit:    ltc1qw508d6qejxtdg4y5r...    (42+ chars)  
✅ Multisig:  M1234567890abcdefghijk...     (34 chars)
```

### Dogecoin (DOGE)
```
✅ Standard:  D1234567890abcdefghijk...     (34 chars)
✅ Multisig:  A1234567890abcdefghijk...     (34 chars)
```

### Feathercoin (FTC)
```
✅ Standard:  61234567890abcdefghijk...     (34 chars)
✅ Multisig:  31234567890abcdefghijk...     (34 chars)
```

---

## 🎛️ Performance Settings Guide

### Thread Count Recommendations
```
CPU Cores    │ Conservative │ Balanced │ Maximum
─────────────┼──────────────┼──────────┼─────────
4 cores      │     2        │    3     │    4    
8 cores      │     4        │    6     │    7    
16 cores     │     8        │   12     │   15    
```

### Mining Intensity Guide
```
Intensity │ Performance │ System Impact │ Use Case
──────────┼─────────────┼───────────────┼──────────────────
10-30%    │ Low         │ Minimal       │ Background mining
40-60%    │ Medium      │ Moderate      │ Casual mining    
70-90%    │ High        │ Significant   │ Dedicated mining
95-100%   │ Maximum     │ Heavy         │ Maximum profit
```

---

## 🧠 AI Features Explained

### AI Optimization Types
```
🎯 Hash Pattern Prediction
   └─ Learns optimal mining patterns for efficiency

📊 Difficulty Forecasting  
   └─ Predicts best times to mine based on network data

💱 Coin Switching Advice
   └─ Recommends most profitable coins to mine

⚙️ Auto-Optimization
   └─ Automatically adjusts settings for best performance
```

### AI Learning Timeline
```
⏱️ 0-10 mins:  Initial data collection
⏱️ 10-30 mins: Basic pattern recognition
⏱️ 30+ mins:   Advanced optimization active
⏱️ 2+ hours:   Full AI learning engaged
```

---

## 📊 Monitoring Dashboard

### Key Metrics to Watch
```
📈 Hash Rate:       Target >10 KH/s (depends on system)
✅ Efficiency:      Target >90% accepted shares  
🖥️ CPU Usage:       Keep <80% for stability
💾 Memory:          Keep <70% for performance
🌡️ Temperature:     Monitor if available
```

### Status Indicators
```
🟢 Connected:       WebSocket active, real-time updates
🟡 Mining:          Hash rate >0, shares being generated
🔴 Error:           Check error messages and logs
⚪ Stopped:         Mining not active
```

---

## 🔧 Common Commands

### System Control
```bash
# Check service status
sudo supervisorctl status

# Restart all services  
sudo supervisorctl restart mining_system:*

# View backend logs
tail -f /var/log/supervisor/backend.err.log

# View frontend logs  
tail -f /var/log/supervisor/frontend.err.log

# Test API health
curl http://localhost:8001/api/health
```

### Quick Fixes
```bash
# Frontend not loading?
sudo supervisorctl restart mining_system:frontend

# Backend API errors?
sudo supervisorctl restart mining_system:backend  

# Database issues?
sudo systemctl restart mongodb

# Clean restart everything
sudo supervisorctl stop mining_system:*
sudo supervisorctl start mining_system:*
```

---

## 🚨 Troubleshooting Quick Fixes

### Issue: Low Hash Rate
```
1. ✅ Increase thread count
2. ✅ Increase mining intensity  
3. ✅ Enable AI optimization
4. ✅ Close other applications
5. ✅ Check system cooling
```

### Issue: High Rejected Shares
```  
1. ✅ Check internet connection
2. ✅ Verify wallet address
3. ✅ Reduce mining intensity
4. ✅ Monitor system stability
```

### Issue: Dashboard Not Loading
```
1. ✅ Check URL: http://localhost:3000
2. ✅ Clear browser cache
3. ✅ Restart frontend service
4. ✅ Check service status
```

### Issue: Mining Won't Start
```
1. ✅ Verify wallet address is valid
2. ✅ Check error messages in red boxes
3. ✅ Ensure system has enough resources
4. ✅ Try lower performance settings
```

---

## 🏆 Optimization Tips

### Maximum Performance
```
1. 🎯 Use AI auto-optimization
2. ⚙️ Set intensity to 90-100%
3. 🧵 Use maximum safe thread count
4. 🔄 Enable all AI features
5. 📊 Monitor and adjust based on results
```

### System Stability
```
1. 🛡️ Keep CPU usage <80%
2. 💾 Monitor memory usage
3. 🌡️ Ensure adequate cooling
4. 🔄 Restart mining daily
5. 📱 Monitor dashboard regularly
```

### Energy Efficiency
```
1. ⚡ Use moderate intensity (70-80%)
2. 🤖 Let AI optimize automatically  
3. 📊 Mine most profitable coins
4. ⏰ Mine during off-peak electricity hours
```

---

## 🎯 Success Checklist

```
✅ Services running (check with: sudo supervisorctl status)
✅ Dashboard loads at http://localhost:3000
✅ Connection status shows "Connected" (green)
✅ Coin selected and details visible
✅ Wallet address entered and validated (green checkmark)
✅ Performance settings configured
✅ Mining started successfully
✅ Hash rate showing positive numbers
✅ AI insights panel showing data
✅ System metrics within healthy ranges
```

---

## 📞 Emergency Contacts

### Service URLs
- **Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8001/api/health  
- **API Docs**: http://localhost:8001/docs

### Log Locations
```
Backend:  /var/log/supervisor/backend.*.log
Frontend: /var/log/supervisor/frontend.*.log  
MongoDB:  /var/log/mongodb/mongod.log
System:   /var/log/syslog
```

---

<div align="center">

**🚀 Happy Mining with CryptoMiner Pro!**

*Keep this reference card handy while mining*

</div>