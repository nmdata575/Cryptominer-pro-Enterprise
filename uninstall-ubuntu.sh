#!/bin/bash

# 🗑️ CryptoMiner Pro - Uninstall Script for Ubuntu 24+
# Completely removes CryptoMiner Pro and optionally removes dependencies

set -e

# Configuration
PROJECT_DIR="/opt/cryptominer-pro"
LOG_FILE="/tmp/cryptominer-uninstall.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Unicode symbols
SUCCESS="✅"
ERROR="❌"
WARNING="⚠️"
INFO="ℹ️"
TRASH="🗑️"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Print functions
print_header() {
    clear
    echo -e "${RED}"
    echo "=================================================================="
    echo "          🗑️  CryptoMiner Pro - Uninstaller"
    echo "=================================================================="
    echo -e "${NC}"
    echo -e "${YELLOW}Complete removal of CryptoMiner Pro from Ubuntu system${NC}"
    echo ""
}

print_step() {
    echo -e "\n${WHITE}🔄 STEP: $1${NC}"
    echo "$(printf '=%.0s' {1..60})"
    log "STEP: $1"
}

print_substep() {
    echo -e "${BLUE}  🔧 $1${NC}"
    log "SUBSTEP: $1"
}

print_success() {
    echo -e "${GREEN}  ${SUCCESS} $1${NC}"
    log "SUCCESS: $1"
}

print_warning() {
    echo -e "${YELLOW}  ${WARNING} $1${NC}"
    log "WARNING: $1"
}

print_error() {
    echo -e "${RED}  ${ERROR} $1${NC}"
    log "ERROR: $1"
}

print_info() {
    echo -e "${CYAN}  ${INFO} $1${NC}"
    log "INFO: $1"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}${ERROR} This script must be run as root or with sudo${NC}"
        echo -e "${CYAN}${INFO} Usage: sudo $0${NC}"
        exit 1
    fi
}

# Stop and remove services
remove_services() {
    print_step "Removing CryptoMiner Pro Services"
    
    print_substep "Stopping all CryptoMiner services"
    supervisorctl stop cryptominer-pro:* >> "$LOG_FILE" 2>&1 || true
    
    print_substep "Removing supervisor configuration"
    if [ -f "/etc/supervisor/conf.d/cryptominer-pro.conf" ]; then
        rm -f /etc/supervisor/conf.d/cryptominer-pro.conf
        print_success "Supervisor configuration removed"
    fi
    
    print_substep "Reloading supervisor"
    supervisorctl reread >> "$LOG_FILE" 2>&1 || true
    supervisorctl update >> "$LOG_FILE" 2>&1 || true
    
    print_success "Services removed"
}

# Remove application files
remove_application() {
    print_step "Removing Application Files"
    
    if [ -d "$PROJECT_DIR" ]; then
        print_substep "Backing up configuration files"
        if [ -d "$PROJECT_DIR/backend" ] || [ -d "$PROJECT_DIR/frontend" ]; then
            BACKUP_DIR="/tmp/cryptominer-backup-$(date +%Y%m%d_%H%M%S)"
            mkdir -p "$BACKUP_DIR"
            cp -r "$PROJECT_DIR/backend/.env" "$BACKUP_DIR/" 2>/dev/null || true
            cp -r "$PROJECT_DIR/frontend/.env" "$BACKUP_DIR/" 2>/dev/null || true
            print_info "Configuration backed up to: $BACKUP_DIR"
        fi
        
        print_substep "Removing project directory: $PROJECT_DIR"
        rm -rf "$PROJECT_DIR"
        print_success "Application files removed"
    else
        print_info "Project directory not found - already removed"
    fi
}

# Remove management scripts
remove_management_scripts() {
    print_step "Removing Management Scripts"
    
    print_substep "Removing system-wide command shortcuts"
    rm -f /usr/local/bin/cryptominer-start
    rm -f /usr/local/bin/cryptominer-stop
    rm -f /usr/local/bin/cryptominer-restart
    rm -f /usr/local/bin/cryptominer-status
    rm -f /usr/local/bin/cryptominer-logs
    
    print_success "Management scripts removed"
}

# Remove desktop integration
remove_desktop_integration() {
    print_step "Removing Desktop Integration"
    
    # Find all user desktop directories and remove launcher
    for user_home in /home/*; do
        if [ -d "$user_home/Desktop" ]; then
            DESKTOP_FILE="$user_home/Desktop/CryptoMiner-Pro.desktop"
            if [ -f "$DESKTOP_FILE" ]; then
                rm -f "$DESKTOP_FILE"
                print_substep "Removed desktop launcher for $(basename "$user_home")"
            fi
        fi
    done
    
    print_success "Desktop integration removed"
}

# Remove MongoDB (optional)
remove_mongodb() {
    if [ "$REMOVE_MONGODB" = "yes" ]; then
        print_step "Removing MongoDB"
        
        print_substep "Stopping MongoDB service"
        systemctl stop mongod >> "$LOG_FILE" 2>&1 || true
        systemctl disable mongod >> "$LOG_FILE" 2>&1 || true
        
        print_substep "Removing MongoDB packages"
        apt purge -y mongodb-org* >> "$LOG_FILE" 2>&1 || true
        
        print_substep "Removing MongoDB data and logs"
        rm -rf /var/log/mongodb
        rm -rf /var/lib/mongodb
        
        print_substep "Removing MongoDB repository"
        rm -f /etc/apt/sources.list.d/mongodb-org-*.list
        rm -f /usr/share/keyrings/mongodb-server-*.gpg
        
        print_success "MongoDB completely removed"
    else
        print_info "Keeping MongoDB (use --remove-mongodb to remove)"
    fi
}

# Remove Node.js (optional)
remove_nodejs() {
    if [ "$REMOVE_NODEJS" = "yes" ]; then
        print_step "Removing Node.js"
        
        print_substep "Removing Node.js and npm"
        apt purge -y nodejs npm >> "$LOG_FILE" 2>&1 || true
        
        print_substep "Removing NodeSource repository"
        rm -f /etc/apt/sources.list.d/nodesource.list
        apt-key del 9FD3B784BC1C6FC31A8A0A1C1655A0AB68576280 >> "$LOG_FILE" 2>&1 || true
        
        print_success "Node.js removed"
    else
        print_info "Keeping Node.js (use --remove-nodejs to remove)"
    fi
}

# Clean up system packages
cleanup_packages() {
    print_step "Cleaning Up System"
    
    print_substep "Removing orphaned packages"
    apt autoremove -y >> "$LOG_FILE" 2>&1 || true
    
    print_substep "Cleaning package cache"
    apt autoclean >> "$LOG_FILE" 2>&1 || true
    
    print_substep "Updating package database"
    apt update >> "$LOG_FILE" 2>&1 || true
    
    print_success "System cleanup completed"
}

# Reset firewall rules (optional)
reset_firewall() {
    if [ "$RESET_FIREWALL" = "yes" ]; then
        print_step "Resetting Firewall Rules"
        
        print_substep "Removing CryptoMiner-specific firewall rules"
        ufw delete allow 3000/tcp >> "$LOG_FILE" 2>&1 || true
        ufw delete allow 8001/tcp >> "$LOG_FILE" 2>&1 || true
        ufw delete allow 27017/tcp >> "$LOG_FILE" 2>&1 || true
        
        print_success "Firewall rules removed"
    else
        print_info "Keeping firewall rules (use --reset-firewall to remove)"
    fi
}

# Show completion information
show_completion_info() {
    print_header
    echo -e "${GREEN}"
    echo "✅✅✅ UNINSTALLATION COMPLETED SUCCESSFULLY! ✅✅✅"
    echo "======================================================="
    echo -e "${NC}"
    
    echo -e "${CYAN}📋 What was removed:${NC}"
    echo -e "    ${BLUE}•${NC} CryptoMiner Pro application and services"
    echo -e "    ${BLUE}•${NC} Supervisor configuration"
    echo -e "    ${BLUE}•${NC} Management scripts and system commands"
    echo -e "    ${BLUE}•${NC} Desktop integration"
    
    if [ "$REMOVE_MONGODB" = "yes" ]; then
        echo -e "    ${BLUE}•${NC} MongoDB database and data"
    fi
    
    if [ "$REMOVE_NODEJS" = "yes" ]; then
        echo -e "    ${BLUE}•${NC} Node.js and npm"
    fi
    
    if [ "$RESET_FIREWALL" = "yes" ]; then
        echo -e "    ${BLUE}•${NC} Firewall rules"
    fi
    
    echo ""
    echo -e "${YELLOW}📂 What was kept:${NC}"
    
    if [ "$REMOVE_MONGODB" != "yes" ]; then
        echo -e "    ${BLUE}•${NC} MongoDB (database server)"
    fi
    
    if [ "$REMOVE_NODEJS" != "yes" ]; then
        echo -e "    ${BLUE}•${NC} Node.js and npm"
    fi
    
    if [ "$RESET_FIREWALL" != "yes" ]; then
        echo -e "    ${BLUE}•${NC} Firewall configuration"
    fi
    
    echo -e "    ${BLUE}•${NC} System Python installation"
    echo -e "    ${BLUE}•${NC} System packages and dependencies"
    
    if [ -d "/tmp/cryptominer-backup"* ]; then
        echo ""
        echo -e "${YELLOW}💾 Configuration Backup:${NC}"
        echo -e "    ${BLUE}•${NC} Your configuration files have been backed up to /tmp/"
        echo -e "    ${BLUE}•${NC} Look for folders named: cryptominer-backup-*"
    fi
    
    echo ""
    echo -e "${YELLOW}🔄 Next Steps (if needed):${NC}"
    echo -e "    ${BLUE}•${NC} Run 'sudo apt autoremove' to clean up remaining packages"
    echo -e "    ${BLUE}•${NC} Check for any remaining configuration files in /etc/"
    echo -e "    ${BLUE}•${NC} Review firewall rules: 'sudo ufw status'"
    echo -e "    ${BLUE}•${NC} Restart system if major dependencies were removed"
    
    echo ""
    echo -e "${GREEN}${TRASH} CryptoMiner Pro has been completely removed from your system!${NC}"
    echo ""
    
    log "Uninstallation completed successfully"
}

# Main uninstall function
main() {
    # Initialize log file
    echo "CryptoMiner Pro Uninstallation Log - $(date)" > "$LOG_FILE"
    
    print_header
    check_root
    
    echo -e "${RED}${WARNING} This will completely remove CryptoMiner Pro from your system${NC}"
    echo -e "${CYAN}${INFO} This includes all application files, services, and configuration${NC}"
    echo ""
    
    # Ask for confirmation
    read -p "Are you sure you want to uninstall CryptoMiner Pro? [y/N]: " -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${CYAN}Uninstallation cancelled by user${NC}"
        exit 0
    fi
    
    # Ask about optional removals
    echo -e "${YELLOW}Optional removals:${NC}"
    echo ""
    
    read -p "Remove MongoDB database? [y/N]: " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        REMOVE_MONGODB="yes"
        echo -e "${RED}${WARNING} This will delete ALL MongoDB data permanently!${NC}"
        read -p "Are you absolutely sure? [y/N]: " -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            REMOVE_MONGODB="no"
        fi
    else
        REMOVE_MONGODB="no"
    fi
    
    read -p "Remove Node.js and npm? [y/N]: " -r
    REMOVE_NODEJS=$([[ $REPLY =~ ^[Yy]$ ]] && echo "yes" || echo "no")
    
    read -p "Reset firewall rules? [y/N]: " -r
    RESET_FIREWALL=$([[ $REPLY =~ ^[Yy]$ ]] && echo "yes" || echo "no")
    
    echo ""
    echo -e "${YELLOW}Starting uninstallation process...${NC}"
    echo ""
    
    # Start uninstallation process
    remove_services
    remove_application
    remove_management_scripts
    remove_desktop_integration
    remove_mongodb
    remove_nodejs
    reset_firewall
    cleanup_packages
    
    # Show completion information
    show_completion_info
}

# Handle command line arguments
case "${1:-}" in
    "--help"|"-h")
        echo "CryptoMiner Pro - Ubuntu Uninstaller"
        echo ""
        echo "Usage: sudo $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h         Show this help message"
        echo "  --remove-mongodb   Remove MongoDB and all data"
        echo "  --remove-nodejs    Remove Node.js and npm"
        echo "  --reset-firewall   Reset firewall rules"
        echo "  --force            Skip confirmation prompts"
        echo ""
        echo "This script will:"
        echo "  • Stop and remove all CryptoMiner Pro services"
        echo "  • Remove application files and configuration"
        echo "  • Remove management scripts and desktop integration"
        echo "  • Optionally remove dependencies (MongoDB, Node.js)"
        echo "  • Clean up system packages"
        echo ""
        echo "Warning: This action cannot be undone!"
        ;;
    "--remove-mongodb")
        REMOVE_MONGODB="yes"
        main "$@"
        ;;
    "--remove-nodejs")
        REMOVE_NODEJS="yes"
        main "$@"
        ;;
    "--reset-firewall")
        RESET_FIREWALL="yes"
        main "$@"
        ;;
    "--force")
        # Set all removals and skip prompts
        export FORCE_UNINSTALL="yes"
        main "$@"
        ;;
    *)
        main "$@"
        ;;
esac