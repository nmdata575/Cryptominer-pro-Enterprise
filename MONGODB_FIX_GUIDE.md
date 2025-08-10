# MongoDB Installation Fix Guide

## Issue Description
You're encountering MongoDB installation issues on Ubuntu 24.04+ due to:
- Missing GPG keys for MongoDB repository
- Package availability issues
- Architecture compatibility problems

## Quick Fix Options

### Option 1: Automated Fix Script (Recommended)
```bash
# Run the automated MongoDB fix script
sudo ./fix-mongodb.sh
```

This script will:
- Clean up existing MongoDB repositories
- Try multiple installation methods (official repository, snap, Docker)
- Test the connection to ensure it's working
- Provide detailed error messages if all methods fail

### Option 2: Manual MongoDB 7.0 Installation
```bash
# Clean up existing repositories
sudo rm -f /etc/apt/sources.list.d/mongodb*.list
sudo rm -f /usr/share/keyrings/mongodb*.gpg

# Install dependencies
sudo apt install -y gnupg curl

# Add MongoDB GPG key
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
    sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

# Add repository (using jammy for Ubuntu 24.04 compatibility)
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
    sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update and install
sudo apt update
sudo apt install -y mongodb-org

# Start services
sudo systemctl start mongod
sudo systemctl enable mongod
```

### Option 3: Use Ubuntu's MongoDB Package
```bash
# Install MongoDB from Ubuntu repository
sudo apt update
sudo apt install -y mongodb-server mongodb-clients

# Start services
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### Option 4: Docker Installation
```bash
# Install Docker if not present
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Create data directory
sudo mkdir -p /opt/mongodb/data
sudo chown -R $USER:$USER /opt/mongodb

# Run MongoDB container
docker run -d \
    --name mongodb \
    --restart unless-stopped \
    -p 27017:27017 \
    -v /opt/mongodb/data:/data/db \
    mongo:7.0
```

### Option 5: Use External MongoDB Service
If all local installations fail, you can use an external MongoDB service:

```bash
# Edit the backend configuration
nano /opt/cryptominer-pro/backend/.env

# Change MONGO_URL to point to your external MongoDB
MONGO_URL=mongodb://your-external-mongodb-server:27017
```

## Verify Installation

After installation, test MongoDB connection:

```bash
# Test with mongosh (new client)
mongosh --eval "db.adminCommand('ping')"

# Or test with mongo (legacy client)
mongo --eval "db.adminCommand('ping')"

# Or test with Python
python3 -c "
import pymongo
client = pymongo.MongoClient('mongodb://localhost:27017')
print('MongoDB connection successful:', client.admin.command('ping'))
"
```

## Continue with CryptoMiner Pro Installation

Once MongoDB is working, continue with the main installation:

```bash
# Run the setup script
sudo ./setup.sh --install

# Or if you had issues, run with frontend fix
sudo ./setup.sh --frontend-fix
```

## Troubleshooting

### Common Issues:

1. **"Package mongodb has no installation candidate"**
   - Use the automated fix script or manual MongoDB 7.0 installation

2. **GPG key verification failed**
   - The fix script handles this by properly importing the GPG keys

3. **Service won't start**
   ```bash
   # Check service status
   sudo systemctl status mongod
   # or
   sudo systemctl status mongodb
   
   # Check logs
   sudo journalctl -u mongod -f
   ```

4. **Permission issues**
   ```bash
   # Fix MongoDB data directory permissions
   sudo chown -R mongodb:mongodb /var/lib/mongodb
   sudo chown mongodb:mongodb /tmp/mongodb-27017.sock
   ```

5. **Port conflicts**
   ```bash
   # Check if port 27017 is in use
   sudo lsof -i :27017
   
   # Kill conflicting processes if needed
   sudo kill -9 <PID>
   ```

## Alternative: Skip MongoDB for Testing

If you want to test CryptoMiner Pro without MongoDB temporarily:

```bash
# Comment out MongoDB-dependent features in server.py
# This will disable saved pools and custom coins features
# but allow basic mining functionality to work
```

## Support

If you continue having issues:
1. Run the diagnostic fix script: `sudo ./fix-mongodb.sh`
2. Check the detailed error messages
3. Ensure you have at least 2GB free disk space
4. Try the Docker installation method as a last resort

The CryptoMiner Pro application will work with any of these MongoDB installation methods.