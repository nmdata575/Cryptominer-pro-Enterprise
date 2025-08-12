#!/bin/bash

# CryptoMiner Pro - MongoDB Connection Monitor
# Ensures MongoDB stays running for persistent database connections

LOG_FILE="/var/log/cryptominer-mongodb-monitor.log"
PID_FILE="/var/run/mongod.pid"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_mongodb() {
    # Check if MongoDB process is running
    if ! pgrep mongod > /dev/null; then
        log_message "❌ MongoDB process not found - restarting..."
        restart_mongodb
        return 1
    fi
    
    # Check if MongoDB is responding
    if ! timeout 5 mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
        log_message "❌ MongoDB not responding - restarting..."
        restart_mongodb
        return 1
    fi
    
    return 0
}

restart_mongodb() {
    log_message "🔄 Stopping existing MongoDB processes..."
    sudo pkill mongod
    sleep 3
    
    log_message "🚀 Starting MongoDB with configuration..."
    if sudo mongod --config /etc/mongod.conf --fork; then
        log_message "✅ MongoDB restarted successfully"
        
        # Restart backend to reconnect
        log_message "🔄 Restarting CryptoMiner backend..."
        sudo supervisorctl restart mining_system:backend
        sleep 5
        
        # Verify connection
        if curl -s http://localhost:8001/api/health | grep -q '"status":"connected"'; then
            log_message "✅ Backend reconnected to database"
        else
            log_message "⚠️ Backend may need more time to reconnect"
        fi
    else
        log_message "❌ Failed to restart MongoDB"
    fi
}

# Main monitoring loop
main() {
    log_message "🚀 Starting CryptoMiner MongoDB Monitor"
    
    while true; do
        if check_mongodb; then
            log_message "💓 MongoDB health check passed"
        fi
        
        # Check every 60 seconds
        sleep 60
    done
}

# Handle script termination
trap 'log_message "🛑 MongoDB monitor stopped"; exit 0' SIGTERM SIGINT

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi