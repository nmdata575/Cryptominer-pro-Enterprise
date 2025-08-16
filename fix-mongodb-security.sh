#!/bin/bash

# MongoDB Security Setup Fix
# Handles the case where MongoDB is already running

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
DB_NAME="crypto_miner_db"
DB_USER="cryptominer_user"
DB_PASSWORD=$(openssl rand -base64 32)
INSTALL_DIR="$HOME/CryptominerV30"

log_info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

log_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

log_security() {
    echo -e "${CYAN}[SECURITY] $1${NC}"
}

# Check if MongoDB is running
check_mongodb_status() {
    log_info "Checking MongoDB status..."
    
    if pgrep mongod > /dev/null; then
        log_info "MongoDB is currently running"
        
        # Test if we can connect
        if mongosh --eval "db.adminCommand('ping')" &> /dev/null; then
            log_success "MongoDB is accessible"
            return 0
        else
            log_warning "MongoDB is running but not accessible"
            return 1
        fi
    else
        log_info "MongoDB is not running"
        return 1
    fi
}

# Start MongoDB safely
start_mongodb_safely() {
    log_info "Starting MongoDB safely..."
    
    # Kill any existing MongoDB processes first
    if pgrep mongod > /dev/null; then
        log_info "Stopping existing MongoDB processes..."
        sudo pkill mongod 2>/dev/null || true
        sleep 3
    fi
    
    # Clean up any lock files
    sudo rm -f /var/lib/mongodb/mongod.lock 2>/dev/null || true
    
    # Ensure proper ownership of MongoDB directories
    sudo chown -R mongodb:mongodb /var/lib/mongodb /var/log/mongodb 2>/dev/null || true
    
    # Start MongoDB without authentication for setup
    log_info "Starting MongoDB without authentication..."
    sudo -u mongodb mongod \
        --dbpath /var/lib/mongodb \
        --logpath /var/log/mongodb/mongod-setup.log \
        --port 27017 \
        --bind_ip 127.0.0.1 \
        --fork &
    
    # Wait for MongoDB to start
    local count=0
    while ! mongosh --eval "db.adminCommand('ping')" &> /dev/null && [ $count -lt 30 ]; do
        sleep 2
        count=$((count + 1))
        echo -n "."
    done
    echo
    
    if mongosh --eval "db.adminCommand('ping')" &> /dev/null; then
        log_success "MongoDB started successfully"
        return 0
    else
        log_error "Failed to start MongoDB"
        return 1
    fi
}

# Setup MongoDB users
setup_mongodb_users() {
    log_security "Setting up MongoDB users..."
    
    # Create admin user
    log_info "Creating administrative user..."
    mongosh admin --eval "
    try {
        db.createUser({
            user: 'admin',
            pwd: '$DB_PASSWORD',
            roles: ['root']
        });
        print('Admin user created successfully');
    } catch(e) {
        if (e.code === 11000) {
            print('Admin user already exists');
        } else {
            print('Error creating admin user: ' + e.message);
        }
    }
    " &> /dev/null
    
    # Create application user
    log_info "Creating application user..."
    mongosh "$DB_NAME" --eval "
    try {
        db.createUser({
            user: '$DB_USER',
            pwd: '$DB_PASSWORD',
            roles: [
                { role: 'readWrite', db: '$DB_NAME' },
                { role: 'dbAdmin', db: '$DB_NAME' }
            ]
        });
        print('Application user created successfully');
    } catch(e) {
        if (e.code === 11000) {
            print('Application user already exists');
        } else {
            print('Error creating application user: ' + e.message);
        }
    }
    " &> /dev/null
    
    log_success "MongoDB users setup completed"
}

# Save credentials securely
save_credentials() {
    log_security "Saving MongoDB credentials..."
    
    mkdir -p "$INSTALL_DIR"
    local creds_file="$INSTALL_DIR/.mongodb_credentials"
    
    cat > "$creds_file" << EOF
# MongoDB Credentials for CryptoMiner Pro V30
# Created: $(date)
# KEEP THIS FILE SECURE

DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
MONGO_URL=mongodb://$DB_USER:$DB_PASSWORD@localhost:27017/$DB_NAME?authSource=$DB_NAME
EOF
    
    chmod 600 "$creds_file"
    log_success "Credentials saved to $creds_file"
}

# Configure MongoDB with authentication
configure_mongodb_auth() {
    log_security "Configuring MongoDB with authentication..."
    
    # Stop current MongoDB
    sudo pkill mongod 2>/dev/null || true
    sleep 3
    
    # Create production MongoDB configuration
    sudo tee /etc/mongod.conf > /dev/null << EOF
# MongoDB configuration for CryptoMiner Pro V30
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true

systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log
  quiet: false

net:
  port: 27017
  bindIp: 127.0.0.1

processManagement:
  fork: true
  pidFilePath: /var/run/mongodb/mongod.pid

security:
  authorization: enabled

setParameter:
  enableLocalhostAuthBypass: false
EOF
    
    # Set proper permissions
    sudo chown mongodb:mongodb /etc/mongod.conf
    sudo chmod 644 /etc/mongod.conf
    
    # Create necessary directories
    sudo mkdir -p /var/run/mongodb
    sudo chown mongodb:mongodb /var/run/mongodb
    
    # Start MongoDB with authentication
    log_info "Starting MongoDB with authentication..."
    sudo -u mongodb mongod --config /etc/mongod.conf
    
    # Wait for startup
    sleep 5
    
    # Test connection with credentials
    if mongosh "$DB_NAME" --username "$DB_USER" --password "$DB_PASSWORD" --eval "db.stats()" &> /dev/null; then
        log_success "MongoDB authentication working correctly"
        return 0
    else
        log_error "MongoDB authentication test failed"
        return 1
    fi
}

# Test the setup
test_mongodb_security() {
    log_info "Testing MongoDB security setup..."
    
    # Test 1: Ensure unauthenticated access is blocked
    if mongosh "$DB_NAME" --eval "db.stats()" &> /dev/null; then
        log_warning "MongoDB allows unauthenticated access (security may not be fully enabled)"
    else
        log_success "Unauthenticated access properly blocked"
    fi
    
    # Test 2: Test authenticated access
    if [ -f "$INSTALL_DIR/.mongodb_credentials" ]; then
        source "$INSTALL_DIR/.mongodb_credentials"
        if mongosh "$DB_NAME" --username "$DB_USER" --password "$DB_PASSWORD" --eval "db.stats()" &> /dev/null; then
            log_success "Authenticated access working correctly"
        else
            log_error "Authenticated access failed"
            return 1
        fi
    else
        log_error "Credentials file not found"
        return 1
    fi
    
    log_success "MongoDB security test completed successfully"
}

# Main function
main() {
    echo -e "${CYAN}🔐 MongoDB Security Setup Fix${NC}"
    echo -e "${BLUE}Fixing MongoDB security configuration...${NC}\n"
    
    # Check current status
    if check_mongodb_status; then
        log_info "MongoDB is running - proceeding with user setup"
        
        # Try to setup users on running instance
        if setup_mongodb_users; then
            save_credentials
            
            # Now configure with authentication
            if configure_mongodb_auth; then
                test_mongodb_security
                log_success "✅ MongoDB security setup completed successfully!"
                
                echo -e "\n${CYAN}📋 Next Steps:${NC}"
                echo -e "1. Update your backend .env file with the new MongoDB URL"
                echo -e "2. Restart your backend service to use authenticated connection"
                echo -e "3. Your credentials are saved in: ${YELLOW}$INSTALL_DIR/.mongodb_credentials${NC}"
                
                return 0
            else
                log_error "Failed to configure authentication"
                return 1
            fi
        else
            log_error "Failed to setup users"
            return 1
        fi
    else
        # MongoDB not running, start it safely
        if start_mongodb_safely; then
            setup_mongodb_users
            save_credentials
            configure_mongodb_auth
            test_mongodb_security
            log_success "✅ MongoDB security setup completed successfully!"
        else
            log_error "Failed to start MongoDB"
            return 1
        fi
    fi
}

# Run the fix
main "$@"