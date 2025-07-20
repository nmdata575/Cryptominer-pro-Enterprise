#!/bin/bash

# 🧪 Script Syntax Validator
# Validates shell scripts for compatibility issues

validate_script() {
    local script="$1"
    local errors=0
    
    echo "🧪 Validating script: $script"
    echo "================================================"
    
    if [ ! -f "$script" ]; then
        echo "❌ File not found: $script"
        return 1
    fi
    
    # Check if it's executable
    if [ ! -x "$script" ]; then
        echo "⚠️  Script is not executable"
        echo "   Fix: chmod +x $script"
    else
        echo "✅ Script is executable"
    fi
    
    # Check shebang
    local shebang=$(head -1 "$script")
    if [[ "$shebang" =~ ^#!/bin/bash ]]; then
        echo "✅ Uses bash shebang"
    elif [[ "$shebang" =~ ^#!/bin/sh ]]; then
        echo "⚠️  Uses sh shebang (may have compatibility issues)"
    else
        echo "❌ Invalid or missing shebang"
        errors=$((errors + 1))
    fi
    
    # Test bash syntax
    echo ""
    echo "🔍 Testing bash syntax..."
    if bash -n "$script" 2>/dev/null; then
        echo "✅ Bash syntax is valid"
    else
        echo "❌ Bash syntax errors found:"
        bash -n "$script"
        errors=$((errors + 1))
    fi
    
    # Test dash compatibility (if needed)
    echo ""
    echo "🔍 Testing dash compatibility..."
    if dash -n "$script" 2>/dev/null; then
        echo "✅ Compatible with dash (POSIX)"
    else
        echo "⚠️  Not compatible with dash (uses bash-specific features)"
        echo "   This is OK if script explicitly requires bash"
    fi
    
    # Check for common bash-specific constructs
    echo ""
    echo "🔍 Checking for bash-specific features..."
    
    local bash_features=0
    
    # Arrays
    if grep -q "\[\]" "$script" || grep -q "+=(" "$script"; then
        echo "📝 Uses arrays (bash-specific)"
        bash_features=$((bash_features + 1))
    fi
    
    # Extended test syntax
    if grep -q "\[\[.*\]\]" "$script"; then
        echo "📝 Uses [[ ]] test syntax (bash-specific)"
        bash_features=$((bash_features + 1))
    fi
    
    # Regex matching
    if grep -q "=~" "$script"; then
        echo "📝 Uses regex matching (bash-specific)"
        bash_features=$((bash_features + 1))
    fi
    
    # Function syntax
    if grep -q "function " "$script"; then
        echo "📝 Uses 'function' keyword (bash-specific)"
        bash_features=$((bash_features + 1))
    fi
    
    # Redirections
    if grep -q "&>" "$script"; then
        echo "📝 Uses &> redirection (bash-specific)"
        bash_features=$((bash_features + 1))
    fi
    
    if [ $bash_features -gt 0 ]; then
        echo "ℹ️  Script uses $bash_features bash-specific feature(s)"
        echo "   Ensure script has #!/bin/bash shebang"
    else
        echo "✅ No bash-specific features detected"
    fi
    
    # Final summary
    echo ""
    echo "📋 Validation Summary:"
    echo "======================"
    if [ $errors -eq 0 ]; then
        echo "✅ Script validation passed"
        if [ $bash_features -gt 0 ]; then
            echo "ℹ️  Script requires bash (has bash-specific features)"
        else
            echo "ℹ️  Script is POSIX compatible"
        fi
        return 0
    else
        echo "❌ Script validation failed with $errors error(s)"
        return 1
    fi
}

# Main execution
if [ $# -eq 0 ]; then
    echo "Usage: $0 <script-to-validate>"
    echo ""
    echo "Example: $0 install-ubuntu.sh"
    exit 1
fi

validate_script "$1"