# 🚀 CryptoMiner Pro V30 - Real Mining Pool Setup Guide

## 📋 **STEP-BY-STEP MINING CONFIGURATION**

### **1. 💰 GET YOUR LITECOIN WALLET ADDRESS**

You need a real Litecoin address to receive mining rewards:

**Quick Setup Options:**
- **Exodus Wallet**: https://www.exodus.com/ (Beginner-friendly)
- **Electrum-LTC**: https://electrum-ltc.org/ (Advanced)
- **Coinbase**: Login → Wallet → Litecoin → Deposit

**Your address will look like:**
- `LXX1234567890abcdefghijk...` (Legacy - 34 chars)
- `ltc1qxx1234567890abcdef...` (Bech32 - 42+ chars)

### **2. 🏊 RECOMMENDED MINING POOLS**

**🥇 LitecoinPool.org (RECOMMENDED - NO FEES)**
- Pool: `stratum+tcp://litecoinpool.org:3333`
- Username: `YOUR_WALLET_ADDRESS.worker1`
- Password: `x`
- Fee: 0%
- Payment: PPS (Pay Per Share)

**🥈 ViaBTC (Alternative)**
- Pool: `stratum+tcp://ltc.viabtc.com:3333`  
- Username: `YOUR_WALLET_ADDRESS.worker1`
- Password: `x`
- Fee: 2-4%
- Payment: PPS+/PPLNS

**🥉 F2Pool (Global)**
- Pool: `stratum+tcp://ltc.f2pool.com:8888`
- Username: `YOUR_WALLET_ADDRESS.worker1`
- Password: `x`  
- Fee: 4%
- Payment: PPS

### **3. ⚙️ CONFIGURATION STEPS**

**Step A: Save Pool Configuration**
```bash
curl -X POST http://localhost:8001/api/pools/saved \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LitecoinPool.org",
    "coin_symbol": "LTC", 
    "wallet_address": "YOUR_WALLET_ADDRESS_HERE",
    "pool_address": "stratum+tcp://litecoinpool.org:3333",
    "pool_port": 3333,
    "username": "YOUR_WALLET_ADDRESS_HERE.cryptominer_v30",
    "password": "x",
    "description": "Official LitecoinPool.org - 0% fees, PPS system"
  }'
```

**Step B: Start Mining**
```bash
curl -X POST http://localhost:8001/api/mining/start \
  -H "Content-Type: application/json" \
  -d '{
    "coin": {
      "name": "Litecoin",
      "symbol": "LTC", 
      "algorithm": "Scrypt"
    },
    "wallet_address": "YOUR_WALLET_ADDRESS_HERE",
    "threads": 4,
    "mode": "pool",
    "pool_address": "stratum+tcp://litecoinpool.org:3333",
    "pool_username": "YOUR_WALLET_ADDRESS_HERE.cryptominer_v30",
    "pool_password": "x"
  }'
```

### **4. 📊 MONITORING YOUR MINING**

**Check Mining Status:**
```bash
curl http://localhost:8001/api/mining/status
```

**Expected Results:**
- **Hash Rate**: 50-500+ H/s (depending on your CPU)
- **Accepted Shares**: Should increase over time
- **Pool Connection**: Active stratum connection
- **Earnings**: Visible on pool website after first share

### **5. 🏆 EARNING EXPECTATIONS**

**Litecoin Mining Profitability (CPU):**
- **4-core CPU**: ~0.0001-0.001 LTC/day (~$0.01-0.10/day)
- **8-core CPU**: ~0.0002-0.002 LTC/day (~$0.02-0.20/day)  
- **16-core CPU**: ~0.0005-0.005 LTC/day (~$0.05-0.50/day)

**Note**: CPU mining is primarily for learning/testing. GPU mining is 100x more profitable.

### **6. 🔍 TROUBLESHOOTING**

**Common Issues:**

**Issue**: Hash rate shows 0 H/s
**Solution**: Check pool connection, verify wallet address format

**Issue**: "Invalid wallet address" 
**Solution**: Ensure address is valid Litecoin format (L/M/ltc1 prefix)

**Issue**: "Connection failed"
**Solution**: Check internet connection, try different pool server

**Issue**: No earnings showing
**Solution**: Wait 10-15 minutes for first share, check pool website

### **7. 🌐 POOL WEBSITES TO MONITOR EARNINGS**

**LitecoinPool.org**: https://www.litecoinpool.org/
- Register account with your wallet address
- View real-time statistics, earnings, payouts

**ViaBTC**: https://www.viabtc.com/
- Create account, add worker, monitor earnings

**F2Pool**: https://www.f2pool.com/
- Use wallet address to view earnings (no registration needed)

### **8. 🚀 SCALING UP (Optional)**

**For Serious Mining:**
- **ASIC Miners**: Antminer L7 (9.5 GH/s)
- **GPU Mining**: Multiple RTX 4090 setup
- **Pool Comparison**: Test different pools for best profits
- **Enterprise V30**: Scale to 250,000+ cores across multiple nodes

---

## ⚡ **QUICK START COMMAND**

Replace `YOUR_WALLET_ADDRESS_HERE` with your actual Litecoin address:

```bash
# Start mining with LitecoinPool.org (0% fees)
curl -X POST http://localhost:8001/api/mining/start \
  -H "Content-Type: application/json" \
  -d '{
    "coin": {"name": "Litecoin", "symbol": "LTC", "algorithm": "Scrypt"},
    "wallet_address": "YOUR_WALLET_ADDRESS_HERE",
    "threads": 4,
    "mode": "pool", 
    "pool_address": "stratum+tcp://litecoinpool.org:3333",
    "pool_username": "YOUR_WALLET_ADDRESS_HERE.cryptominer_v30",
    "pool_password": "x"
  }'
```

---

**🎉 CONGRATULATIONS! You're now ready for real cryptocurrency mining!**

*Remember: Start with a small number of threads (4-8) to test, then scale up based on your hardware capabilities.*