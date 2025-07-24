#!/bin/bash

# 🐍 CryptoMiner Pro - Quick Component Verification Script
# Simple wrapper for the Python verification script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/verify_components.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${PURPLE}🐍 CryptoMiner Pro - Component Verification${NC}"
    echo -e "${PURPLE}===========================================${NC}"
    echo ""
}

print_usage() {
    echo -e "${CYAN}Usage:${NC}"
    echo "  $0 [check|install|install-all|report]"
    echo ""
    echo -e "${CYAN}Commands:${NC}"
    echo "  check         - Verify all components (default)"
    echo "  install       - Install missing critical components"
    echo "  install-all   - Install all missing components"
    echo "  report        - Generate detailed report and save to file"
    echo ""
    echo -e "${CYAN}Examples:${NC}"
    echo "  $0                    # Quick verification"
    echo "  $0 check              # Detailed verification"
    echo "  $0 install            # Install critical components"
    echo "  $0 install-all        # Install everything"
    echo "  $0 report             # Generate report file"
    echo ""
}

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}❌ Error: verify_components.py not found in $SCRIPT_DIR${NC}"
    exit 1
fi

# Check Python availability
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: python3 not found. Please install Python 3.x${NC}"
    exit 1
fi

# Main logic
case "${1:-check}" in
    "check"|"verify"|"")
        print_header
        echo -e "${BLUE}🔍 Checking all Python components...${NC}"
        echo ""
        python3 "$PYTHON_SCRIPT" --report
        ;;
    
    "install"|"install-critical")
        print_header
        echo -e "${YELLOW}📦 Installing missing critical components...${NC}"
        echo ""
        python3 "$PYTHON_SCRIPT" --install --report
        ;;
    
    "install-all"|"install-optional")
        print_header
        echo -e "${YELLOW}📦 Installing all missing components...${NC}"
        echo ""
        python3 "$PYTHON_SCRIPT" --install-all --report
        ;;
    
    "report"|"save-report")
        print_header
        echo -e "${CYAN}📋 Generating detailed report...${NC}"
        echo ""
        python3 "$PYTHON_SCRIPT" --report --save-report
        ;;
    
    "quick"|"fast")
        # Quick check without detailed output
        python3 "$PYTHON_SCRIPT" --quiet
        exit_code=$?
        if [ $exit_code -eq 0 ]; then
            echo -e "${GREEN}✅ All components verified successfully!${NC}"
        elif [ $exit_code -eq 1 ]; then
            echo -e "${RED}❌ Critical components missing!${NC}"
        else
            echo -e "${YELLOW}⚠️ Some optional components missing.${NC}"
        fi
        exit $exit_code
        ;;
    
    "help"|"-h"|"--help")
        print_header
        print_usage
        ;;
    
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac