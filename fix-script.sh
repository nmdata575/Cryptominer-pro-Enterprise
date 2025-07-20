#!/bin/bash

# 🔧 Quick Script Syntax Fixes
# Common fixes for shell script compatibility issues

fix_common_issues() {
    local script="$1"
    
    if [ ! -f "$script" ]; then
        echo "❌ File not found: $script"
        return 1
    fi
    
    echo "🔧 Applying common syntax fixes to: $script"
    echo "================================================"
    
    # Create backup
    cp "$script" "${script}.backup"
    echo "📁 Backup created: ${script}.backup"
    
    local fixed=0
    
    # Fix: Ensure bash shebang
    if head -1 "$script" | grep -q "#!/bin/sh"; then
        sed -i '1s|#!/bin/sh|#!/bin/bash|' "$script"
        echo "✅ Fixed: Changed #!/bin/sh to #!/bin/bash"
        fixed=$((fixed + 1))
    fi
    
    # Fix: Add bash version check if using bash features
    if ! grep -q "BASH_VERSION" "$script" && (grep -q "\[\[" "$script" || grep -q "&>" "$script" || grep -q "+=(" "$script"); then
        # Insert bash check after shebang
        sed -i '1a\\n# Ensure we'\''re using bash, not sh/dash\nif [ -z "$BASH_VERSION" ]; then\n    echo "This script requires bash. Please run with: bash $0"\n    exit 1\nfi\n' "$script"
        echo "✅ Fixed: Added bash version check"
        fixed=$((fixed + 1))
    fi
    
    # Make executable if not already
    if [ ! -x "$script" ]; then
        chmod +x "$script"
        echo "✅ Fixed: Made script executable"
        fixed=$((fixed + 1))
    fi
    
    echo ""
    echo "📋 Summary: Applied $fixed fix(es)"
    
    if [ $fixed -gt 0 ]; then
        echo "🧪 Validating fixed script..."
        if bash -n "$script"; then
            echo "✅ Fixed script has valid syntax"
            return 0
        else
            echo "❌ Fixed script still has syntax errors"
            echo "🔄 Restoring backup..."
            mv "${script}.backup" "$script"
            return 1
        fi
    else
        echo "ℹ️  No fixes needed"
        rm -f "${script}.backup"
        return 0
    fi
}

# Usage information
show_usage() {
    echo "Script Syntax Fixer"
    echo "==================="
    echo ""
    echo "Usage: $0 <script-to-fix>"
    echo ""
    echo "This script applies common fixes for shell script compatibility:"
    echo "  • Changes #!/bin/sh to #!/bin/bash if bash features detected"
    echo "  • Adds bash version check for bash-specific scripts"
    echo "  • Makes script executable"
    echo "  • Creates backup before making changes"
    echo ""
    echo "Example: $0 install-ubuntu.sh"
}

# Main execution
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_usage
    exit 0
fi

fix_common_issues "$1"