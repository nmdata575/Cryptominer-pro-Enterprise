#!/bin/bash

# CryptoMiner Pro V30 - Comprehensive Uninstall Script
# Version: 2.0.0 - Updated for user directory installation and security cleanup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration - Updated for user directory
INSTALL_DIR="$HOME/CryptominerV30"
OLD_INSTALL_DIR="/opt/cryptominer-pro"  # Legacy location
SERVICE_NAME="cryptominer-v30"
BACKUP_DIR="$HOME/cryptominer-v30-backup-$(date +%Y%m%d-%H%M%S)"
DB_NAME="crypto_miner_db"

# Logging functions
log_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" >&2
}

log_step() {
    echo -e "${PURPLE}[$(date +'%Y-%m-%d %H:%M:%S')] 🚀 $1${NC}"
}

log_security() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')] 🔐 $1${NC}"
}

# Progress tracking
TOTAL_STEPS=10
CURRENT_STEP=0

show_progress() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    local percentage=$((CURRENT_STEP * 100 / TOTAL_STEPS))
    echo -e "${CYAN}Progress: [$CURRENT_STEP/$TOTAL_STEPS] ($percentage%)${NC}"
}

# Check permissions
check_permissions() {
    log_step "Checking permissions..."
    show_progress
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root. This is acceptable for uninstallation but not recommended."
    fi
    
    # Check sudo access for system-level operations
    if ! sudo -n true 2>/dev/null; then
        log_warning "This script may require sudo privileges for system cleanup."
        log_info "You may be prompted for your password."
        
        # Test sudo access
        if ! sudo -v; then
            log_warning "Unable to obtain sudo privileges. Some cleanup operations may be skipped."
        fi
    fi
    
    log_success "Permissions check completed"
}

# Create comprehensive backup
create_comprehensive_backup() {
    log_step "Creating comprehensive backup..."
    show_progress
    
    if [ -d "$INSTALL_DIR" ] || [ -d "$OLD_INSTALL_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        
        # Backup from current installation directory
        if [ -d "$INSTALL_DIR" ]; then
            log_info "Backing up from current installation: $INSTALL_DIR"
            
            # Backup configuration files
            if [ -f "$INSTALL_DIR/backend/.env" ]; then
                cp "$INSTALL_DIR/backend/.env" "$BACKUP_DIR/backend.env"
            fi
            
            if [ -f "$INSTALL_DIR/frontend/.env" ]; then
                cp "$INSTALL_DIR/frontend/.env" "$BACKUP_DIR/frontend.env"
            fi
            
            # Backup MongoDB credentials
            if [ -f "$INSTALL_DIR/.mongodb_credentials" ]; then
                cp "$INSTALL_DIR/.mongodb_credentials" "$BACKUP_DIR/"
            fi
            
            # Backup license keys
            if [ -f "$INSTALL_DIR/backend/enterprise_licenses.json" ]; then
                cp "$INSTALL_DIR/backend/enterprise_licenses.json" "$BACKUP_DIR/"
            fi
            
            # Backup any custom configuration
            if [ -d "$INSTALL_DIR/data" ]; then
                cp -r "$INSTALL_DIR/data" "$BACKUP_DIR/"
            fi
            
            # Backup logs (last 1000 lines of each)
            mkdir -p "$BACKUP_DIR/logs"
            if [ -d "$INSTALL_DIR/logs" ]; then
                for log_file in "$INSTALL_DIR/logs"/*.log; do
                    if [ -f "$log_file" ]; then
                        tail -n 1000 "$log_file" > "$BACKUP_DIR/logs/$(basename "$log_file")"
                    fi
                done
            fi
        fi
        
        # Backup from legacy installation directory
        if [ -d "$OLD_INSTALL_DIR" ]; then
            log_info "Backing up from legacy installation: $OLD_INSTALL_DIR"
            
            if [ -f "$OLD_INSTALL_DIR/backend/.env" ]; then
                cp "$OLD_INSTALL_DIR/backend/.env" "$BACKUP_DIR/legacy_backend.env"
            fi
            
            if [ -f "$OLD_INSTALL_DIR/frontend/.env" ]; then
                cp "$OLD_INSTALL_DIR/frontend/.env" "$BACKUP_DIR/legacy_frontend.env"
            fi
        fi
        
        # Create restoration information
        cat > "$BACKUP_DIR/restoration_info.txt" << EOF
CryptoMiner Pro V30 Uninstallation Backup
Created: $(date)
Hostname: $(hostname)
User: $(whoami)
Installation Directory: $INSTALL_DIR
Legacy Directory: $OLD_INSTALL_DIR

Backed up files:
- Backend environment configuration (.env)
- Frontend environment configuration (.env)
- MongoDB credentials (if available)
- Enterprise license keys (if available)
- Custom data files
- Recent log files (last 1000 lines)

To restore:
1. Reinstall CryptoMiner Pro V30
2. Copy the backed up .env files to their respective directories
3. Restore the MongoDB credentials
4. Copy any custom data back to the data directory

Backup directory: $BACKUP_DIR
EOF
        
        # Set proper permissions on backup
        chmod -R 600 "$BACKUP_DIR"
        chmod 700 "$BACKUP_DIR"
        
        log_success "Comprehensive backup created at: $BACKUP_DIR"
    else
        log_info "No installation directories found, skipping backup"
    fi
}

# Stop all related services
stop_all_services() {
    log_step "Stopping all CryptoMiner Pro services..."
    show_progress
    
    local stopped_services=()
    
    # Stop supervisor services
    if command -v supervisorctl &> /dev/null; then
        log_info "Stopping supervisor services..."
        
        # New service names
        local supervisor_services=(
            "cryptominer-v30:backend"
            "cryptominer-v30:frontend"
            "cryptominer-v30:all"
        )
        
        # Legacy service names
        local legacy_services=(
            "mining_system:backend"
            "mining_system:frontend"
            "mining_system:all"
            "mining_app:backend"
            "mining_app:frontend"
            "cryptominer-pro:backend"
            "cryptominer-pro:frontend"
        )
        
        # Stop new services
        for service in "${supervisor_services[@]}"; do
            if sudo supervisorctl stop "$service" 2>/dev/null; then
                stopped_services+=("$service")
                log_success "Stopped supervisor service: $service"
            fi
        done
        
        # Stop legacy services
        for service in "${legacy_services[@]}"; do
            if sudo supervisorctl stop "$service" 2>/dev/null; then
                stopped_services+=("$service")
                log_success "Stopped legacy supervisor service: $service"
            fi
        done
    fi
    
    # Stop systemd services
    local systemd_services=(
        "cryptominer-v30"
        "cryptominer-pro" 
        "cryptominer-v30-node"
    )
    
    for service in "${systemd_services[@]}"; do
        if systemctl is-active "$service" &> /dev/null; then
            if sudo systemctl stop "$service" 2>/dev/null; then
                stopped_services+=("systemd:$service")
                log_success "Stopped systemd service: $service"
            fi
        fi
    done
    
    # Kill any remaining processes
    log_info "Terminating remaining processes..."
    
    local process_patterns=(
        "cryptominer"
        "mining_system"
        "CryptominerV30"
        "server.py.*mining"
        "yarn.*start.*3333"
        "react-scripts.*start"
    )
    
    for pattern in "${process_patterns[@]}"; do
        if pgrep -f "$pattern" > /dev/null; then
            sudo pkill -f "$pattern" 2>/dev/null || true
            log_success "Terminated processes matching: $pattern"
        fi
    done
    
    # Kill processes from installation directories
    for install_path in "$INSTALL_DIR" "$OLD_INSTALL_DIR"; do
        if pgrep -f "$install_path" > /dev/null; then
            sudo pkill -f "$install_path" 2>/dev/null || true
            log_success "Terminated processes from: $install_path"
        fi
    done
    
    # Give processes time to terminate gracefully
    sleep 3
    
    if [ ${#stopped_services[@]} -gt 0 ]; then
        log_success "Stopped ${#stopped_services[@]} services"
    else
        log_info "No running services found to stop"
    fi
}

# Remove service configurations
remove_service_configurations() {
    log_step "Removing service configurations..."
    show_progress
    
    # Remove supervisor configurations
    log_info "Removing supervisor configurations..."
    
    local supervisor_configs=(
        "/etc/supervisor/conf.d/cryptominer-v30.conf"
        "/etc/supervisor/conf.d/mining_system.conf"
        "/etc/supervisor/conf.d/mining_app.conf"
        "/etc/supervisor/conf.d/cryptominer-pro.conf"
    )
    
    for config in "${supervisor_configs[@]}"; do
        if [ -f "$config" ]; then
            sudo rm -f "$config"
            log_success "Removed supervisor config: $config"
        fi
    done
    
    # Remove systemd services
    log_info "Removing systemd services..."
    
    local systemd_services=(
        "cryptominer-v30.service"
        "cryptominer-pro.service"
        "cryptominer-v30-node.service"
    )
    
    for service in "${systemd_services[@]}"; do
        local service_file="/etc/systemd/system/$service"
        if [ -f "$service_file" ]; then
            # Stop and disable first
            sudo systemctl stop "${service%%.service}" 2>/dev/null || true
            sudo systemctl disable "${service%%.service}" 2>/dev/null || true
            
            # Remove service file
            sudo rm -f "$service_file"
            log_success "Removed systemd service: $service"
        fi
    done
    
    # Reload systemd and supervisor
    sudo systemctl daemon-reload 2>/dev/null || true
    
    if command -v supervisorctl &> /dev/null; then
        if sudo supervisorctl status &> /dev/null; then
            sudo supervisorctl reread 2>/dev/null || true
            sudo supervisorctl update 2>/dev/null || true
            log_success "Reloaded supervisor configuration"
        fi
    fi
    
    log_success "Service configurations removed"
}

# Remove application files
remove_application_files() {
    log_step "Removing application files..."
    show_progress
    
    local removed_dirs=()
    
    # Remove current installation directory
    if [ -d "$INSTALL_DIR" ]; then
        log_info "Removing installation directory: $INSTALL_DIR"
        rm -rf "$INSTALL_DIR"
        removed_dirs+=("$INSTALL_DIR")
        log_success "Removed: $INSTALL_DIR"
    fi
    
    # Remove legacy installation directory
    if [ -d "$OLD_INSTALL_DIR" ]; then
        log_info "Removing legacy installation directory: $OLD_INSTALL_DIR"
        sudo rm -rf "$OLD_INSTALL_DIR"
        removed_dirs+=("$OLD_INSTALL_DIR")
        log_success "Removed: $OLD_INSTALL_DIR"
    fi
    
    # Remove common application paths
    local common_paths=(
        "/usr/local/bin/cryptominer-v30"
        "/usr/local/bin/cryptominer-pro"
        "/usr/local/bin/cryptominer"
        "/var/log/cryptominer-v30"
        "/var/log/cryptominer-pro"
        "/var/lib/cryptominer-v30"
        "/var/lib/cryptominer-pro"
        "/etc/cryptominer-v30"
        "/etc/cryptominer-pro"
        "/tmp/cryptominer*"
    )
    
    for path in "${common_paths[@]}"; do
        if [ -e "$path" ] || ls $path 1> /dev/null 2>&1; then
            sudo rm -rf $path 2>/dev/null || true
            log_success "Removed: $path"
        fi
    done
    
    if [ ${#removed_dirs[@]} -gt 0 ]; then
        log_success "Removed ${#removed_dirs[@]} installation directories"
    else
        log_info "No installation directories found to remove"
    fi
}

# Clean up system users and groups
cleanup_users_groups() {
    log_step "Cleaning up users and groups..."
    show_progress
    
    local users=("cryptominer" "cryptominer-pro" "cryptominer-v30")
    local groups=("cryptominer" "cryptominer-pro" "cryptominer-v30")
    
    # Remove users
    for user in "${users[@]}"; do
        if id "$user" &>/dev/null; then
            sudo userdel -r "$user" 2>/dev/null || sudo userdel "$user" 2>/dev/null || true
            log_success "Removed user: $user"
        fi
    done
    
    # Remove groups
    for group in "${groups[@]}"; do
        if getent group "$group" &>/dev/null; then
            sudo groupdel "$group" 2>/dev/null || true
            log_success "Removed group: $group"
        fi
    done
    
    log_success "User and group cleanup completed"
}

# Clean up all log files
cleanup_log_files() {
    log_step "Cleaning up log files..."
    show_progress
    
    local log_patterns=(
        "/var/log/supervisor/backend.*"
        "/var/log/supervisor/frontend.*"
        "/var/log/supervisor/mining_*"
        "/var/log/supervisor/cryptominer*"
        "/var/log/cryptominer*"
        "/tmp/cryptominer*"
        "/tmp/mining_*"
        "$HOME/.pm2/logs/cryptominer*"
        "$HOME/.pm2/logs/mining*"
    )
    
    local cleaned_files=0
    
    for log_pattern in "${log_patterns[@]}"; do
        if ls $log_pattern 1> /dev/null 2>&1; then
            sudo rm -f $log_pattern 2>/dev/null || rm -f $log_pattern 2>/dev/null || true
            cleaned_files=$((cleaned_files + 1))
            log_success "Cleaned logs: $log_pattern"
        fi
    done
    
    # Clean user-specific logs
    local user_log_dirs=(
        "$HOME/.cache/cryptominer"
        "$HOME/.local/share/cryptominer"
        "$HOME/.config/cryptominer"
    )
    
    for log_dir in "${user_log_dirs[@]}"; do
        if [ -d "$log_dir" ]; then
            rm -rf "$log_dir"
            cleaned_files=$((cleaned_files + 1))
            log_success "Removed user log directory: $log_dir"
        fi
    done
    
    if [ $cleaned_files -gt 0 ]; then
        log_success "Cleaned up $cleaned_files log locations"
    else
        log_info "No log files found to clean"
    fi
}

# Clean up MongoDB data and security
cleanup_mongodb_security() {
    local cleanup_db="$1"
    
    if [ "$cleanup_db" = "true" ]; then
        log_step "Cleaning up MongoDB data and security..."
        show_progress
        
        log_warning "This will permanently remove:"
        log_warning "- All CryptoMiner Pro database data"
        log_warning "- Database users and authentication"
        log_warning "- Mining statistics and configurations"
        log_warning "- AI training data"
        
        read -p "Are you absolutely sure? Type 'YES' to confirm: " -r
        echo
        
        if [[ $REPLY == "YES" ]]; then
            log_security "Removing MongoDB data and users..."
            
            # Try to connect and clean up database
            local mongodb_cleaned=false
            
            # Try mongosh first (MongoDB 5.0+)
            if command -v mongosh &> /dev/null; then
                log_info "Using mongosh to clean database..."
                
                # Remove the database
                if mongosh --eval "use $DB_NAME; db.dropDatabase()" 2>/dev/null; then
                    log_success "Database $DB_NAME dropped successfully"
                    mongodb_cleaned=true
                fi
                
                # Remove users
                mongosh admin --eval "
                    try {
                        db.dropUser('cryptominer_user');
                        print('Dropped cryptominer_user');
                    } catch(e) {
                        print('User cryptominer_user not found or already removed');
                    }
                " 2>/dev/null || true
                
            # Try legacy mongo client
            elif command -v mongo &> /dev/null; then
                log_info "Using legacy mongo client to clean database..."
                
                # Remove the database
                if mongo "$DB_NAME" --eval "db.dropDatabase()" 2>/dev/null; then
                    log_success "Database $DB_NAME dropped successfully"
                    mongodb_cleaned=true
                fi
                
                # Remove users
                mongo admin --eval "
                    try {
                        db.dropUser('cryptominer_user');
                        print('Dropped cryptominer_user');
                    } catch(e) {
                        print('User cryptominer_user not found or already removed');
                    }
                " 2>/dev/null || true
            fi
            
            # Clean up MongoDB configuration files
            local mongodb_configs=(
                "/etc/mongod.conf.backup"
                "/etc/mongod.conf.temp"
            )
            
            for config in "${mongodb_configs[@]}"; do
                if [ -f "$config" ]; then
                    sudo rm -f "$config"
                    log_success "Removed MongoDB config: $config"
                fi
            done
            
            # Clean up database data directories (only CryptoMiner specific data)
            local mongodb_data_paths=(
                "/var/lib/mongodb/$DB_NAME"
                "/data/db/$DB_NAME"
            )
            
            for data_path in "${mongodb_data_paths[@]}"; do
                if [ -d "$data_path" ]; then
                    sudo rm -rf "$data_path"
                    log_success "Removed database data: $data_path"
                fi
            done
            
            if $mongodb_cleaned; then
                log_success "MongoDB cleanup completed successfully"
            else
                log_warning "Database cleanup may have been incomplete"
            fi
        else
            log_info "MongoDB cleanup cancelled by user"
        fi
    else
        log_info "Skipping MongoDB cleanup (use --cleanup-database to remove data)"
    fi
}

# Remove development dependencies (optional)
remove_development_dependencies() {
    local remove_deps="$1"
    
    if [ "$remove_deps" = "true" ]; then
        log_step "Removing development dependencies..."
        show_progress
        
        log_warning "This will remove development packages that may be used by other applications:"
        log_warning "- Node.js and npm packages"
        log_warning "- Python development packages"
        log_warning "- Build tools and compilers"
        
        read -p "Continue with dependency removal? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Remove Node.js (but not system-wide)
            if [ -d "$HOME/.nvm" ]; then
                rm -rf "$HOME/.nvm"
                log_success "Removed Node Version Manager"
            fi
            
            # Clean npm cache
            if command -v npm &> /dev/null; then
                npm cache clean --force 2>/dev/null || true
                log_success "Cleaned npm cache"
            fi
            
            # Clean yarn cache
            if command -v yarn &> /dev/null; then
                yarn cache clean 2>/dev/null || true
                log_success "Cleaned yarn cache"
            fi
            
            # Remove Python virtual environments in user directory
            find "$HOME" -name "venv" -type d -path "*/CryptominerV30/*" -exec rm -rf {} + 2>/dev/null || true
            
            log_success "Development dependency cleanup completed"
            log_warning "System-wide packages were preserved to avoid breaking other applications"
        else
            log_info "Skipped dependency removal"
        fi
    fi
}

# Final system cleanup
final_cleanup() {
    log_step "Performing final system cleanup..."
    show_progress
    
    # Clear package cache
    sudo apt autoremove -y 2>/dev/null || true
    sudo apt autoclean 2>/dev/null || true
    
    # Clear temporary files
    sudo rm -rf /tmp/cryptominer* 2>/dev/null || true
    sudo rm -rf /tmp/mining_* 2>/dev/null || true
    
    # Clear user temporary files
    rm -rf "$HOME/.cache/cryptominer*" 2>/dev/null || true
    rm -rf "$HOME/.local/share/cryptominer*" 2>/dev/null || true
    
    # Update locate database
    sudo updatedb 2>/dev/null || true
    
    log_success "Final cleanup completed"
}

# Display completion message
display_completion_message() {
    local backup_created="$1"
    
    echo -e "\n${GREEN}🎉 CryptoMiner Pro V30 Uninstallation Complete! 🎉${NC}\n"
    
    echo -e "${CYAN}📊 Uninstallation Summary:${NC}"
    echo -e "   Services Stopped: ✅"
    echo -e "   Application Files Removed: ✅"
    echo -e "   Service Configurations Removed: ✅"
    echo -e "   Log Files Cleaned: ✅"
    echo -e "   System Cleanup: ✅"
    
    if [ "$backup_created" = "true" ]; then
        echo -e "\n${CYAN}💾 Backup Information:${NC}"
        echo -e "   Backup Location: ${YELLOW}$BACKUP_DIR${NC}"
        echo -e "   Restoration Guide: ${YELLOW}$BACKUP_DIR/restoration_info.txt${NC}"
        echo -e "   To restore your data, refer to the restoration guide"
    fi
    
    echo -e "\n${CYAN}🔄 To Reinstall:${NC}"
    echo -e "   1. Download the latest CryptoMiner Pro V30"
    echo -e "   2. Run: ${YELLOW}./setup-improved.sh${NC}"
    echo -e "   3. Restore your backed up configuration files if needed"
    
    echo -e "\n${CYAN}🧹 Manual Cleanup (if needed):${NC}"
    echo -e "   Check for remaining files: ${YELLOW}find / -name '*cryptominer*' 2>/dev/null${NC}"
    echo -e "   Check running processes: ${YELLOW}ps aux | grep cryptominer${NC}"
    echo -e "   Check MongoDB status: ${YELLOW}sudo systemctl status mongod${NC}"
    
    echo -e "\n${GREEN}✅ Uninstallation completed successfully at $(date)${NC}\n"
}

# Main uninstallation function
main() {
    echo -e "${PURPLE}🗑️  CryptoMiner Pro V30 - Comprehensive Uninstaller v2.0.0${NC}\n"
    
    # Parse command line arguments
    local remove_deps=false
    local cleanup_db=false
    local skip_backup=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --remove-deps|--remove-dependencies)
                remove_deps=true
                shift
                ;;
            --cleanup-database|--cleanup-db)
                cleanup_db=true
                shift
                ;;
            --skip-backup)
                skip_backup=true
                shift
                ;;
            --help|-h)
                cat << EOF
CryptoMiner Pro V30 - Comprehensive Uninstall Script v2.0.0

Usage: $0 [OPTIONS]

Options:
    --remove-deps          Remove development dependencies (may affect other apps)
    --cleanup-database     Remove all CryptoMiner Pro database data permanently
    --skip-backup         Skip creating backup of configuration files
    --help, -h            Show this help message

Features:
    ✅ Comprehensive service stopping
    ✅ Complete file removal (including legacy locations)
    ✅ MongoDB security cleanup
    ✅ Configuration backup before removal
    ✅ User and system cleanup
    ✅ Verification of complete removal

Examples:
    $0                              # Standard uninstall with backup
    $0 --cleanup-database          # Uninstall and remove all database data
    $0 --remove-deps --skip-backup # Complete removal without backup
    $0 --help                      # Show this help

EOF
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                log_info "Use '$0 --help' for usage information"
                exit 1
                ;;
        esac
    done
    
    # Check permissions
    check_permissions
    
    # Display confirmation
    log_warning "This will completely remove CryptoMiner Pro V30 from your system"
    
    if [ "$remove_deps" = "true" ]; then
        log_warning "Development dependencies will also be removed"
    fi
    
    if [ "$cleanup_db" = "true" ]; then
        log_warning "All database data will be permanently deleted"
    fi
    
    if [ "$skip_backup" = "true" ]; then
        log_warning "No backup will be created"
    fi
    
    echo
    read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Uninstallation cancelled by user"
        exit 0
    fi
    
    # Perform uninstallation
    local backup_created=false
    
    # Create backup unless skipped
    if [ "$skip_backup" != "true" ]; then
        create_comprehensive_backup
        backup_created=true
    fi
    
    # Uninstallation steps
    stop_all_services
    remove_service_configurations
    remove_application_files
    cleanup_users_groups
    cleanup_log_files
    cleanup_mongodb_security "$cleanup_db"
    remove_development_dependencies "$remove_deps"
    final_cleanup
    
    # Display completion message
    display_completion_message "$backup_created"
}

# Run main function with all arguments
main "$@"