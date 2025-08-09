# CryptoMiner Pro - Service Troubleshooting Guide

## 🚨 Quick Fix for Supervisor Issues

If you're getting "no such group" or permission errors, follow these steps:

### Step 1: Run the Supervisor Setup Script
```bash
sudo ./setup-supervisor.sh
```

### Step 2: Manual Service Management
```bash
# Check what services are available
sudo supervisorctl avail

# Check service status
sudo supervisorctl status

# Start CryptoMiner Pro services
sudo supervisorctl start cryptominer_pro:*

# Stop services if needed
sudo supervisorctl stop cryptominer_pro:*

# Restart services
sudo supervisorctl restart cryptominer_pro:*
```

### Step 3: If Services Won't Start

**Check Backend:**
```bash
# Check backend logs
sudo tail -f /var/log/supervisor/cryptominer_backend.err.log

# Test backend directly
cd /app/backend
./venv/bin/python -m uvicorn server:app --host 0.0.0.0 --port 8001
```

**Check Frontend:**
```bash
# Check frontend logs
sudo tail -f /var/log/supervisor/cryptominer_frontend.err.log

# Test frontend directly  
cd /app/frontend
PORT=3333 yarn start
```

### Step 4: Access URLs
- **Frontend:** http://localhost:3333
- **Backend API:** http://localhost:8001/api/health
- **Backend Status:** http://localhost:8001/api/health

### Step 5: Common Issues

**Issue: "Permission denied"**
```bash
sudo chown -R www-data:www-data /app
sudo supervisorctl restart cryptominer_pro:*
```

**Issue: "Port already in use"**
```bash
# Kill processes on ports
sudo pkill -f "uvicorn"
sudo pkill -f "react-scripts"
sudo supervisorctl restart cryptominer_pro:*
```

**Issue: "Module not found"**
```bash
cd /app/backend
./venv/bin/pip install -r requirements.txt
sudo supervisorctl restart cryptominer_pro:backend
```

**Issue: "Yarn not found"**
```bash
# Install yarn
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt update
sudo apt install yarn
```

### Step 6: Alternative Manual Start

If supervisor continues to have issues, you can start services manually:

**Terminal 1 (Backend):**
```bash
cd /app/backend
source venv/bin/activate
python -m uvicorn server:app --host 0.0.0.0 --port 8001
```

**Terminal 2 (Frontend):**
```bash
cd /app/frontend  
PORT=3333 yarn start
```

### Step 7: Check Everything is Working

```bash
# Test backend
curl http://localhost:8001/api/health

# Test frontend (should return HTML)
curl http://localhost:3333

# Check processes
ps aux | grep -E "(uvicorn|react-scripts)"
```

---

## 📞 Still Having Issues?

1. Check the full logs: `sudo journalctl -u supervisor -f`
2. Verify all dependencies: `cd /app/backend && ./venv/bin/pip list`
3. Check ports: `sudo netstat -tlnp | grep -E "(8001|3333)"`
4. Restart supervisor service: `sudo systemctl restart supervisor`

The platform should work perfectly once supervisor is properly configured! 🚀