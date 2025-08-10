# CryptoMiner Pro V30 - Service Management Quick Reference

## 🚀 **Correct Service Commands**

### **Both Services (Recommended)**
```bash
# Start both services
sudo supervisorctl start mining_system:backend mining_system:frontend

# Stop both services
sudo supervisorctl stop mining_system:backend mining_system:frontend

# Restart both services (most common)
sudo supervisorctl restart mining_system:backend mining_system:frontend

# Check status of both services
sudo supervisorctl status mining_system:*
```

### **Individual Services**
```bash
# Backend only
sudo supervisorctl start mining_system:backend
sudo supervisorctl restart mining_system:backend
sudo supervisorctl stop mining_system:backend

# Frontend only
sudo supervisorctl start mining_system:frontend
sudo supervisorctl restart mining_system:frontend
sudo supervisorctl stop mining_system:frontend
```

## ❌ **Incorrect Commands (Don't Use These)**
```bash
# These DON'T work - documented incorrectly in some versions
sudo supervisorctl restart mining_system:all     # ❌ No such process
sudo supervisorctl restart backend frontend      # ❌ No such process
```

## 🌐 **Access URLs**
- **Frontend (Web Interface)**: http://localhost:3333
- **Backend API**: http://localhost:8001/api
- **API Documentation**: http://localhost:8001/docs

## 📊 **Service Information**
- **Service Group**: mining_system
- **Backend Service**: mining_system:backend
- **Frontend Service**: mining_system:frontend
- **Config File**: /etc/supervisor/conf.d/mining_app.conf

## 🔍 **Troubleshooting**
```bash
# Check service status
sudo supervisorctl status

# View logs
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/frontend.out.log

# Restart all supervisor services
sudo supervisorctl restart all

# Reload supervisor configuration
sudo supervisorctl reread
sudo supervisorctl update
```

## 🔧 **Installation Directory**
- **Default**: `/opt/cryptominer-pro/`
- **Alternative**: Detected automatically during setup
- **Configuration Files**:
  - Backend: `[install_dir]/backend/.env`
  - Frontend: `[install_dir]/frontend/.env`

---

**Note**: Always use the full service names with the `mining_system:` prefix for reliable operation.