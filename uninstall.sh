#!/bin/bash

# CryptoMiner Pro - Comprehensive Uninstall Script
# Removes all components, services, and configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/cryptominer-pro"
SERVICE_NAME="cryptominer-pro"
BACKUP_DIR="$HOME/cryptominer-pro-backup-$(date +%Y%m%d-%H%M%S)"

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Check if running as root
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        warning "Running as root. This is generally not recommended but will proceed."
    fi
    
    if ! sudo -n true 2>/dev/null; then
        error "This script requires sudo privileges. Please run with sudo or configure passwordless sudo."
        exit 1
    fi
}

# Create backup of important data
create_backup() {
    log "Creating backup of important data..."
    
    if [ -d "$INSTALL_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        
        # Backup configuration files
        if [ -f "$INSTALL_DIR/backend/.env" ]; then
            cp "$INSTALL_DIR/backend/.env" "$BACKUP_DIR/"
        fi
        
        if [ -f "$INSTALL_DIR/frontend/.env" ]; then
            cp "$INSTALL_DIR/frontend/.env" "$BACKUP_DIR/"
        fi
        
        # Backup license keys if they exist
        if [ -f "$INSTALL_DIR/backend/enterprise_licenses.json" ]; then
            cp "$INSTALL_DIR/backend/enterprise_licenses.json" "$BACKUP_DIR/"
        fi
        
        # Create a list of installed components
        cat > "$BACKUP_DIR/installation_info.txt" << EOF
CryptoMiner Pro Uninstallation Backup
Created: $(date)
Installation Directory: $INSTALL_DIR
User: $(whoami)

Files backed up:
- Backend environment configuration (.env)
- Frontend environment configuration (.env)
- Enterprise license keys (if available)

To reinstall, use the backed up .env files and license information.
EOF
        
        success "Backup created at: $BACKUP_DIR"
    else
        log "No installation directory found, skipping backup"
    fi
}

# Stop all services
stop_services() {
    log "Stopping CryptoMiner Pro services..."
    
    # Stop supervisor services
    if command -v supervisorctl &> /dev/null; then
        # Stop all mining_system services
        sudo supervisorctl stop mining_system:backend 2>/dev/null || true
        sudo supervisorctl stop mining_system:frontend 2>/dev/null || true
        sudo supervisorctl stop mining_system:all 2>/dev/null || true
        success "Stopped mining_system services"
        
        # Also check for older service names
        sudo supervisorctl stop mining_app:backend 2>/dev/null || true
        sudo supervisorctl stop mining_app:frontend 2>/dev/null || true
        sudo supervisorctl stop cryptominer-pro:backend 2>/dev/null || true
        sudo supervisorctl stop cryptominer-pro:frontend 2>/dev/null || true
    fi
    
    # Stop any systemd services
    if systemctl is-active --quiet cryptominer-pro 2>/dev/null; then
        sudo systemctl stop cryptominer-pro
        sudo systemctl disable cryptominer-pro
        success "Stopped and disabled systemd service"
    fi
    
    # Stop any V30 remote node services
    if systemctl is-active --quiet cryptominer-v30-node 2>/dev/null; then
        sudo systemctl stop cryptominer-v30-node
        sudo systemctl disable cryptominer-v30-node
        success "Stopped and disabled V30 remote node service"
    fi
    
    # Kill any remaining processes
    if pgrep -f "cryptominer\|mining_system\|server.py.*mining\|yarn.*start" > /dev/null; then
        sudo pkill -f "cryptominer\|mining_system\|server.py.*mining\|yarn.*start" 2>/dev/null || true
        success "Killed remaining CryptoMiner processes"
    fi
    
    # Kill any Python processes running from the installation directory
    if pgrep -f "$INSTALL_DIR" > /dev/null; then
        sudo pkill -f "$INSTALL_DIR" 2>/dev/null || true
        success "Killed processes from installation directory"
    fi
}

# Remove supervisor configurations
remove_supervisor_config() {
    log "Removing supervisor configurations..."
    
    local supervisor_configs=(
        "/etc/supervisor/conf.d/mining_system.conf"
        "/etc/supervisor/conf.d/mining_app.conf"
        "/etc/supervisor/conf.d/cryptominer-pro.conf"
    )
    
    for config in "${supervisor_configs[@]}"; do
        if [ -f "$config" ]; then
            sudo rm -f "$config"
            success "Removed supervisor config: $config"
        fi
    done
    
    # Reload supervisor if it's running
    if command -v supervisorctl &> /dev/null; then
        if sudo supervisorctl status &> /dev/null; then
            sudo supervisorctl reread
            sudo supervisorctl update
            success "Reloaded supervisor configuration"
        fi
    fi
}

# Remove systemd services
remove_systemd_services() {
    log "Removing systemd services..."
    
    local systemd_services=(
        "cryptominer-pro.service"
        "cryptominer-v30-node.service"
    )
    
    for service in "${systemd_services[@]}"; do
        local service_file="/etc/systemd/system/$service"
        if [ -f "$service_file" ]; then
            sudo systemctl stop "$service" 2>/dev/null || true
            sudo systemctl disable "$service" 2>/dev/null || true
            sudo rm -f "$service_file"
            success "Removed systemd service: $service"
        fi
    done
    
    sudo systemctl daemon-reload
}

# Remove application files
remove_application_files() {
    log "Removing application files..."
    
    if [ -d "$INSTALL_DIR" ]; then
        sudo rm -rf "$INSTALL_DIR"
        success "Removed installation directory: $INSTALL_DIR"
    fi
    
    # Remove any files in common locations
    local common_paths=(
        "/usr/local/bin/cryptominer-pro"
        "/usr/local/bin/cryptominer"
        "/var/log/cryptominer-pro"
        "/var/lib/cryptominer-pro"
        "/etc/cryptominer-pro"
        "/data/db/crypto_miner_db"
    )
    
    for path in "${common_paths[@]}"; do
        if [ -e "$path" ]; then
            sudo rm -rf "$path"
            success "Removed: $path"
        fi
    done
}

# Remove users and groups
remove_users_groups() {
    log "Removing users and groups..."
    
    # Remove cryptominer user if it exists
    if id "cryptominer" &>/dev/null; then
        sudo userdel -r cryptominer 2>/dev/null || true
        success "Removed cryptominer user"
    fi
    
    # Remove cryptominer group if it exists
    if getent group cryptominer &>/dev/null; then
        sudo groupdel cryptominer 2>/dev/null || true
        success "Removed cryptominer group"
    fi
}

# Clean up logs
cleanup_logs() {
    log "Cleaning up log files..."
    
    local log_paths=(
        "/var/log/supervisor/backend.*"
        "/var/log/supervisor/frontend.*"
        "/var/log/supervisor/mining_*"
        "/var/log/supervisor/cryptominer*"
        "/var/log/cryptominer*"
        "/tmp/cryptominer*"
        "/tmp/mining_*"
    )
    
    for log_pattern in "${log_paths[@]}"; do
        if ls $log_pattern 1> /dev/null 2>&1; then
            sudo rm -f $log_pattern
            success "Cleaned up logs: $log_pattern"
        fi
    done
}

# Optional: Remove dependencies
remove_dependencies() {
    local remove_deps="$1"
    
    if [ "$remove_deps" = "true" ]; then
        log "Removing dependencies (this may affect other applications)..."
        
        warning "This will remove Python packages and Node.js packages that may be used by other applications."
        read -p "Are you sure you want to continue? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Remove Python virtual environment if it exists
            if [ -d "$INSTALL_DIR/backend/venv" ]; then
                rm -rf "$INSTALL_DIR/backend/venv"
                success "Removed Python virtual environment"
            fi
            
            # Note: We don't remove system-wide Python or Node.js packages
            # as they may be used by other applications
            warning "System-wide packages were not removed to avoid breaking other applications"
            warning "If you want to remove Python/Node.js completely, do it manually"
        else
            log "Skipped dependency removal"
        fi
    fi
}

# Clean up MongoDB data (optional)
cleanup_mongodb_data() {
    local cleanup_db="$1"
    
    if [ "$cleanup_db" = "true" ]; then
        warning "This will remove all CryptoMiner Pro database data including:"
        warning "- Mining statistics"
        warning "- Saved pool configurations"  
        warning "- Custom coins"
        warning "- AI training data"
        
        read -p "Are you sure you want to remove database data? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log "Cleaning up database data..."
            
            # Connect to MongoDB and drop the database
            if command -v mongosh &> /dev/null; then
                mongosh --eval "db.dropDatabase()" crypto_miner_db 2>/dev/null || true
                success "Removed CryptoMiner Pro database (using mongosh)"
            elif command -v mongo &> /dev/null; then
                mongo --eval "db.dropDatabase()" crypto_miner_db 2>/dev/null || true
                success "Removed CryptoMiner Pro database (using mongo)"
            else
                # Try using Python pymongo
                python3 -c "
import pymongo
try:
    client = pymongo.MongoClient('mongodb://localhost:27017')
    client.drop_database('crypto_miner_db')
    print('Database dropped successfully')
except Exception as e:
    print(f'Failed to drop database: {e}')
" 2>/dev/null || warning "Could not connect to MongoDB to drop database"
            fi
            
            # Remove Docker MongoDB container if it exists
            if command -v docker &> /dev/null && docker ps -a | grep -q mongodb; then
                docker stop mongodb 2>/dev/null || true
                docker rm mongodb 2>/dev/null || true
                success "Removed MongoDB Docker container"
            fi
            
            # Remove MongoDB data directory if using Docker
            if [ -d "/opt/mongodb" ]; then
                sudo rm -rf /opt/mongodb
                success "Removed MongoDB data directory"
            fi
        else
            log "Skipped database cleanup"
        fi
    fi
}

# Main uninstall function
main() {
    log "Starting CryptoMiner Pro uninstallation..."
    
    # Parse command line arguments
    local remove_deps=false
    local cleanup_db=false
    local skip_backup=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --remove-deps)
                remove_deps=true
                shift
                ;;
            --cleanup-database)
                cleanup_db=true
                shift
                ;;
            --skip-backup)
                skip_backup=true
                shift
                ;;
            --help)
                cat << EOF
CryptoMiner Pro Uninstall Script

Usage: $0 [OPTIONS]

Options:
    --remove-deps       Remove Python and Node.js dependencies (may affect other apps)
    --cleanup-database  Remove all CryptoMiner Pro database data
    --skip-backup       Skip creating backup of configuration files
    --help             Show this help message

Examples:
    $0                           # Basic uninstall with backup
    $0 --cleanup-database        # Uninstall and remove database data
    $0 --remove-deps --skip-backup  # Full removal without backup

EOF
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    check_permissions
    
    # Confirmation
    warning "This will completely remove CryptoMiner Pro from your system."
    if [ "$remove_deps" = "true" ]; then
        warning "Dependencies will also be removed (may affect other applications)."
    fi
    if [ "$cleanup_db" = "true" ]; then
        warning "Database data will be permanently deleted."
    fi
    
    echo
    read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Uninstallation cancelled by user"
        exit 0
    fi
    
    # Create backup unless skipped
    if [ "$skip_backup" != "true" ]; then
        create_backup
    fi
    
    # Perform uninstallation steps
    stop_services
    remove_supervisor_config
    remove_systemd_services
    remove_application_files
    remove_users_groups
    cleanup_logs
    remove_dependencies "$remove_deps"
    cleanup_mongodb_data "$cleanup_db"
    
    success "CryptoMiner Pro has been completely uninstalled!"
    
    if [ "$skip_backup" != "true" ]; then
        log "Your configuration backup is saved at: $BACKUP_DIR"
        log "You can use this backup to reinstall with your previous settings"
    fi
    
    log "To reinstall CryptoMiner Pro, download the installer and run: sudo ./install.sh"
}

# Run main function with all arguments
main "$@"