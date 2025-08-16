#!/bin/bash

# Simple MongoDB Authentication Enabler
# Enables authentication on existing MongoDB installation

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO] $1${NC}"; }
log_success() { echo -e "${GREEN}[SUCCESS] $1${NC}"; }
log_warning() { echo -e "${YELLOW}[WARNING] $1${NC}"; }
log_error() { echo -e "${RED}[ERROR] $1${NC}"; }

DB_PASSWORD="/IAzL/+DqhS/+5nyUZuiMOlo9JXVx8N4kxcN9ejtte0="
INSTALL_DIR="$HOME/CryptominerV30"

log_info "Enabling MongoDB authentication..."

# 1. Stop MongoDB
log_info "Stopping MongoDB..."
sudo pkill mongod 2>/dev/null || true
sleep 3

# 2. Create MongoDB config with auth enabled
log_info "Creating authenticated MongoDB configuration..."
sudo tee /etc/mongod.conf > /dev/null << EOF
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true

systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log

net:
  port: 27017
  bindIp: 127.0.0.1

processManagement:
  fork: true

security:
  authorization: enabled
EOF

# 3. Start MongoDB with authentication
log_info "Starting MongoDB with authentication enabled..."
sudo mongod --config /etc/mongod.conf

sleep 5

# 4. Test authentication
log_info "Testing MongoDB authentication..."
if mongosh crypto_miner_db --username cryptominer_user --password "$DB_PASSWORD" --eval "db.stats()" &> /dev/null; then
    log_success "✅ MongoDB authentication is working!"
else
    log_error "❌ MongoDB authentication failed"
    exit 1
fi

# 5. Save credentials
log_info "Saving credentials..."
mkdir -p "$INSTALL_DIR"
cat > "$INSTALL_DIR/.mongodb_credentials" << EOF
# MongoDB Credentials for CryptoMiner Pro V30
DB_NAME=crypto_miner_db
DB_USER=cryptominer_user
DB_PASSWORD=$DB_PASSWORD
MONGO_URL=mongodb://cryptominer_user:$DB_PASSWORD@localhost:27017/crypto_miner_db?authSource=crypto_miner_db
EOF

chmod 600 "$INSTALL_DIR/.mongodb_credentials"

log_success "✅ MongoDB authentication enabled successfully!"
log_info "Credentials saved to: $INSTALL_DIR/.mongodb_credentials"

echo -e "\n${YELLOW}📋 Next Steps:${NC}"
echo -e "1. Update your backend .env file with the new MONGO_URL"
echo -e "2. Restart your backend service"
echo -e "3. Test the application"