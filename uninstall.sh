#!/bin/bash

# CryptoMiner Pro V30 - Unified Uninstall Script
# Combines uninstall-improved.sh functionality
# Version: 3.0.0 - Consolidated Edition

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
INSTALL_DIR="/app"
BACKUP_DIR="/tmp/cryptominer-backup-$(date +%Y%m%d-%H%M%S)"
DB_NAME="crypto_miner_db"

log_info() { echo -e "${BLUE}[INFO] $1${NC}"; }
log_success() { echo -e "${GREEN}[SUCCESS] $1${NC}"; }
log_warning() { echo -e "${YELLOW}[WARNING] $1${NC}"; }
log_error() { echo -e "${RED}[ERROR] $1${NC}"; }

# Create backup
create_backup() {
    log_info "Creating backup..."
    
    if [ -d "$INSTALL_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        
        # Backup configuration files
        [ -f "$INSTALL_DIR/backend/.env" ] && cp "$INSTALL_DIR/backend/.env" "$BACKUP_DIR/"
        [ -f "$INSTALL_DIR/frontend/.env" ] && cp "$INSTALL_DIR/frontend/.env" "$BACKUP_DIR/"
        [ -f "$INSTALL_DIR/.mongodb_credentials" ] && cp "$INSTALL_DIR/.mongodb_credentials" "$BACKUP_DIR/"
        
        # Backup logs (last 1000 lines)
        mkdir -p "$BACKUP_DIR/logs"
        for log_file in "$INSTALL_DIR/logs"/*.log; do
            [ -f "$log_file" ] && tail -n 1000 "$log_file" > "$BACKUP_DIR/logs/$(basename "$log_file")"
        done
        
        log_success "Backup created at: $BACKUP_DIR"
    else
        log_info "No installation found to backup"
    fi
}

# Stop services
stop_services() {
    log_info "Stopping services..."
    
    # Stop supervisor services
    sudo supervisorctl stop cryptominer-v30:* 2>/dev/null || true
    sudo supervisorctl stop mining_system:* 2>/dev/null || true
    
    # Kill any remaining processes
    pkill -f "cryptominer" 2>/dev/null || true
    pkill -f "server.py" 2>/dev/null || true
    pkill -f "yarn.*start.*3333" 2>/dev/null || true
    
    log_success "Services stopped"
}

# Remove files
remove_files() {
    log_info "Removing application files..."
    
    # Remove installation directory
    [ -d "$INSTALL_DIR" ] && rm -rf "$INSTALL_DIR"
    
    # Remove supervisor configs
    sudo rm -f /etc/supervisor/conf.d/cryptominer-v30.conf
    sudo rm -f /etc/supervisor/conf.d/mining_system.conf
    
    # Remove logs
    sudo rm -f /var/log/supervisor/backend.*
    sudo rm -f /var/log/supervisor/frontend.*
    
    log_success "Files removed"
}

# Clean MongoDB
clean_mongodb() {
    local cleanup_db="${1:-false}"
    
    if [ "$cleanup_db" = "true" ]; then
        log_warning "This will permanently remove all database data!"
        read -p "Are you sure? Type 'YES' to confirm: " -r
        
        if [[ $REPLY == "YES" ]]; then
            log_info "Cleaning MongoDB data..."
            
            # Drop database
            mongosh --eval "use $DB_NAME; db.dropDatabase()" 2>/dev/null || true
            
            # Remove users
            mongosh admin --eval "
                try { db.dropUser('admin'); } catch(e) {}
                try { db.dropUser('cryptominer_user'); } catch(e) {}
            " 2>/dev/null || true
            
            log_success "MongoDB cleaned"
        else
            log_info "MongoDB cleanup cancelled"
        fi
    else
        log_info "Skipping MongoDB cleanup (use --clean-db to remove data)"
    fi
}

# Final cleanup
final_cleanup() {
    log_info "Final cleanup..."
    
    # Reload supervisor
    sudo supervisorctl reread 2>/dev/null || true
    sudo supervisorctl update 2>/dev/null || true
    
    # Clean package cache
    sudo apt autoremove -y 2>/dev/null || true
    
    log_success "Cleanup complete"
}

# Show completion message
show_completion() {
    echo -e "\n${GREEN}🎉 Uninstallation Complete! 🎉${NC}\n"
    
    echo -e "${CYAN}📊 Summary:${NC}"
    echo -e "   ✅ Services stopped"
    echo -e "   ✅ Files removed"
    echo -e "   ✅ Configuration cleaned"
    
    if [ -d "$BACKUP_DIR" ]; then
        echo -e "\n${CYAN}💾 Backup:${NC}"
        echo -e "   Location: ${YELLOW}$BACKUP_DIR${NC}"
        echo -e "   Contains: Configuration files and logs"
    fi
    
    echo -e "\n${CYAN}🔄 To Reinstall:${NC}"
    echo -e "   Run: ${YELLOW}./install.sh${NC}"
    
    echo -e "\n${GREEN}✅ Uninstallation successful!${NC}\n"
}

# Main function
main() {
    local clean_db=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --clean-db|--cleanup-database)
                clean_db=true
                shift
                ;;
            --help|-h)
                cat << EOF
CryptoMiner Pro V30 - Unified Uninstall Script v3.0.0

Usage: $0 [OPTIONS]

Options:
    --clean-db           Remove all database data permanently
    --help, -h           Show this help

Features:
    ✅ Automatic backup creation
    ✅ Complete service cleanup
    ✅ Configuration preservation
    ✅ Safe database handling

Examples:
    $0                   # Standard uninstall with backup
    $0 --clean-db       # Uninstall and remove all data

EOF
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    echo -e "${CYAN}🗑️  CryptoMiner Pro V30 - Uninstaller v3.0.0${NC}\n"
    
    log_warning "This will remove CryptoMiner Pro V30 from your system"
    [ "$clean_db" = "true" ] && log_warning "Database data will also be permanently deleted"
    
    echo
    read -p "Continue? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Uninstallation cancelled"
        exit 0
    fi
    
    # Execute uninstallation
    create_backup
    stop_services
    remove_files
    clean_mongodb "$clean_db"
    final_cleanup
    show_completion
}

# Run main function
main "$@"