#!/usr/bin/env python3
"""
CryptoMiner Pro - Python Components Verification & Installation Script
Automatically checks and installs all required Python dependencies for the web application.
"""

import sys
import subprocess
import importlib
import json
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

# Icons for better visual feedback
class Icons:
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    INSTALL = "📦"
    CHECK = "🔍"
    PYTHON = "🐍"
    WEB = "🌐"
    DATABASE = "🗄️"
    SYSTEM = "🖥️"
    AI = "🤖"
    SECURITY = "🔒"

# Required components with their categories and purposes
REQUIRED_COMPONENTS = {
    # Core Web Framework Components
    "fastapi": {
        "version": "0.104.1",
        "category": "Core Web Framework",
        "icon": Icons.WEB,
        "purpose": "Main web framework - serves all API endpoints",
        "critical": True
    },
    "uvicorn": {
        "version": "0.24.0",
        "category": "Core Web Framework", 
        "icon": Icons.WEB,
        "purpose": "ASGI server - runs the web application",
        "critical": True,
        "extras": ["standard"]
    },
    "pydantic": {
        "version": "2.5.0",
        "category": "Core Web Framework",
        "icon": Icons.WEB,
        "purpose": "Data validation - handles API request/response models",
        "critical": True
    },
    "python-multipart": {
        "version": "0.0.6",
        "category": "Core Web Framework",
        "icon": Icons.WEB,
        "purpose": "Form handling - processes file uploads and form data",
        "critical": True
    },
    
    # Real-Time Communication
    "websockets": {
        "version": "12.0",
        "category": "Real-Time Communication",
        "icon": Icons.WEB,
        "purpose": "WebSocket support - real-time mining stats updates",
        "critical": True
    },
    
    # Database Components
    "pymongo": {
        "version": "4.6.0",
        "category": "Database",
        "icon": Icons.DATABASE,
        "purpose": "MongoDB driver - stores mining data and configurations",
        "critical": True
    },
    "motor": {
        "version": "3.3.2",
        "category": "Database",
        "icon": Icons.DATABASE,
        "purpose": "Async MongoDB driver - non-blocking database operations",
        "critical": True
    },
    
    # System Monitoring
    "psutil": {
        "version": "5.9.6",
        "category": "System Monitoring",
        "icon": Icons.SYSTEM,
        "purpose": "System stats - CPU, memory, disk usage monitoring",
        "critical": True
    },
    
    # Scientific Computing & AI
    "numpy": {
        "version": "1.26.4",
        "category": "Scientific Computing & AI",
        "icon": Icons.AI,
        "purpose": "Numerical computing - hash calculations and mining algorithms",
        "critical": False
    },
    "pandas": {
        "version": "2.2.1", 
        "category": "Scientific Computing & AI",
        "icon": Icons.AI,
        "purpose": "Data analysis - mining statistics and performance metrics",
        "critical": False
    },
    "scikit-learn": {
        "version": "1.4.2",
        "category": "Scientific Computing & AI",
        "icon": Icons.AI,
        "purpose": "Machine learning - AI optimization and predictions", 
        "critical": False
    },
    
    # Cryptographic
    "cryptography": {
        "version": "41.0.0",
        "category": "Cryptographic",
        "icon": Icons.SECURITY,
        "purpose": "Cryptographic operations - Scrypt hashing and security",
        "critical": True,
        "version_operator": ">="
    },
    
    # HTTP Clients
    "requests": {
        "version": "2.31.0",
        "category": "HTTP Client",
        "icon": Icons.WEB,
        "purpose": "HTTP client - external API calls (coin prices, pool data)",
        "critical": False
    },
    "aiohttp": {
        "version": "3.9.1",
        "category": "HTTP Client", 
        "icon": Icons.WEB,
        "purpose": "Async HTTP client - non-blocking external requests",
        "critical": False
    },
    
    # File & Configuration
    "aiofiles": {
        "version": "23.2.1",
        "category": "File & Configuration",
        "icon": Icons.SYSTEM,
        "purpose": "Async file I/O - log file handling and data storage",
        "critical": False
    },
    "python-dotenv": {
        "version": "1.0.0",
        "category": "File & Configuration",
        "icon": Icons.SYSTEM,
        "purpose": "Environment variables - configuration management",
        "critical": False
    }
}

class ComponentVerifier:
    def __init__(self):
        self.results = {
            "installed": [],
            "missing": [],
            "version_mismatch": [],
            "critical_missing": [],
            "installation_log": []
        }
        self.use_venv = self._detect_virtual_environment()
        
    def _detect_virtual_environment(self) -> bool:
        """Detect if running in a virtual environment"""
        in_venv = (
            hasattr(sys, 'real_prefix') or 
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
            os.environ.get('VIRTUAL_ENV') is not None
        )
        
        if in_venv:
            venv_path = os.environ.get('VIRTUAL_ENV', sys.prefix)
            print(f"{Icons.PYTHON} {Colors.CYAN}Detected virtual environment: {venv_path}{Colors.END}")
        else:
            print(f"{Icons.WARNING} {Colors.YELLOW}Using system Python: {sys.executable}{Colors.END}")
            
        return in_venv

    def print_header(self):
        """Print the script header"""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}{'=' * 80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.PURPLE}🐍 CryptoMiner Pro - Python Components Verification & Installation{Colors.END}")
        print(f"{Colors.BOLD}{Colors.PURPLE}{'=' * 80}{Colors.END}")
        print(f"{Colors.CYAN}Checking all required Python dependencies for the web application...{Colors.END}\n")
        
    def check_component(self, name: str, info: Dict) -> Tuple[bool, Optional[str], str]:
        """Check if a component is installed and get its version"""
        try:
            # Handle package name mapping
            import_name = name
            if name == "python-multipart":
                import_name = "multipart"
            elif name == "python-dotenv":
                import_name = "dotenv"
            elif name == "scikit-learn":
                import_name = "sklearn"
                
            module = importlib.import_module(import_name)
            
            # Get version
            version = None
            for attr in ['__version__', 'version', 'VERSION']:
                if hasattr(module, attr):
                    version = getattr(module, attr)
                    break
                    
            if version is None:
                # Try to get version from pip
                try:
                    result = subprocess.run([
                        sys.executable, '-m', 'pip', 'show', name
                    ], capture_output=True, text=True, check=True)
                    
                    for line in result.stdout.split('\n'):
                        if line.startswith('Version:'):
                            version = line.split(':')[1].strip()
                            break
                except subprocess.CalledProcessError:
                    pass
                    
            return True, version, "installed"
            
        except ImportError:
            return False, None, "missing"
        except Exception as e:
            return False, None, f"error: {str(e)}"

    def verify_all_components(self) -> Dict:
        """Verify all required components"""
        print(f"{Icons.CHECK} {Colors.BOLD}Verifying Python Components...{Colors.END}\n")
        
        categories = {}
        for name, info in REQUIRED_COMPONENTS.items():
            category = info["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append((name, info))
        
        # Check each category
        for category, components in categories.items():
            print(f"{Colors.BOLD}{Colors.WHITE}{components[0][1]['icon']} {category}:{Colors.END}")
            
            for name, info in components:
                is_installed, version, status = self.check_component(name, info)
                
                if is_installed:
                    if version:
                        version_check = self._check_version_compatibility(version, info.get("version", ""), info.get("version_operator", "=="))
                        if version_check:
                            print(f"  {Icons.SUCCESS} {Colors.GREEN}{name:<20} v{version:<12} ✓ Compatible{Colors.END}")
                            self.results["installed"].append(name)
                        else:
                            print(f"  {Icons.WARNING} {Colors.YELLOW}{name:<20} v{version:<12} ⚠ Version mismatch (expected {info.get('version', 'N/A')}){Colors.END}")
                            self.results["version_mismatch"].append(name)
                    else:
                        print(f"  {Icons.SUCCESS} {Colors.GREEN}{name:<20} {'installed':<12} ✓ Available{Colors.END}")
                        self.results["installed"].append(name)
                else:
                    criticality = "CRITICAL" if info.get("critical", False) else "optional"
                    color = Colors.RED if info.get("critical", False) else Colors.YELLOW
                    print(f"  {Icons.ERROR} {color}{name:<20} {'missing':<12} ❌ Missing ({criticality}){Colors.END}")
                    self.results["missing"].append(name)
                    if info.get("critical", False):
                        self.results["critical_missing"].append(name)
            
            print()  # Empty line between categories
            
        return self.results

    def _check_version_compatibility(self, installed_version: str, required_version: str, operator: str = "==") -> bool:
        """Check if installed version meets requirements"""
        if not required_version:
            return True
            
        try:
            # Simple version comparison (major.minor.patch)
            def version_tuple(v):
                return tuple(map(int, (v.split("."))))
            
            installed_tuple = version_tuple(installed_version)
            required_tuple = version_tuple(required_version)
            
            if operator == ">=":
                return installed_tuple >= required_tuple
            elif operator == "==":
                return installed_tuple == required_tuple
            elif operator == ">":
                return installed_tuple > required_tuple
            else:
                return True  # Default to compatible
                
        except Exception:
            return True  # If version parsing fails, assume compatible

    def install_missing_components(self, install_optional: bool = False) -> bool:
        """Install missing components"""
        if not self.results["missing"]:
            print(f"{Icons.SUCCESS} {Colors.GREEN}All required components are already installed!{Colors.END}")
            return True
            
        components_to_install = []
        
        # Always install critical components
        for name in self.results["missing"]:
            info = REQUIRED_COMPONENTS[name]
            if info.get("critical", False) or install_optional:
                components_to_install.append(name)
                
        if not components_to_install:
            print(f"{Icons.INFO} {Colors.CYAN}Only optional components are missing. Use --install-optional to install them.{Colors.END}")
            return True
            
        print(f"{Icons.INSTALL} {Colors.BOLD}Installing missing components...{Colors.END}\n")
        
        success_count = 0
        for name in components_to_install:
            if self._install_component(name):
                success_count += 1
                
        print(f"\n{Icons.SUCCESS} {Colors.GREEN}Installation complete: {success_count}/{len(components_to_install)} components installed successfully{Colors.END}")
        return success_count == len(components_to_install)

    def _install_component(self, name: str) -> bool:
        """Install a single component"""
        info = REQUIRED_COMPONENTS[name]
        
        # Construct pip install command
        package_spec = name
        if info.get("extras"):
            extras = ",".join(info["extras"])
            package_spec = f"{name}[{extras}]"
            
        if info.get("version") and info.get("version_operator", "==") == "==":
            package_spec += f"=={info['version']}"
        elif info.get("version") and info.get("version_operator") == ">=":
            package_spec += f">={info['version']}"
            
        print(f"  {Icons.INSTALL} Installing {Colors.CYAN}{package_spec}{Colors.END}...")
        
        try:
            cmd = [sys.executable, '-m', 'pip', 'install', package_spec]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            print(f"    {Icons.SUCCESS} {Colors.GREEN}Successfully installed {name}{Colors.END}")
            self.results["installation_log"].append(f"✅ {name}: Success")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"    {Icons.ERROR} {Colors.RED}Failed to install {name}: {e.stderr.strip()}{Colors.END}")
            self.results["installation_log"].append(f"❌ {name}: {e.stderr.strip()}")
            return False

    def generate_report(self) -> str:
        """Generate a detailed report"""
        report = []
        report.append(f"\n{Colors.BOLD}🔍 VERIFICATION REPORT{Colors.END}")
        report.append("=" * 50)
        
        total_components = len(REQUIRED_COMPONENTS)
        installed_count = len(self.results["installed"])
        missing_count = len(self.results["missing"])
        critical_missing = len(self.results["critical_missing"])
        
        # Summary
        report.append(f"\n📊 SUMMARY:")
        report.append(f"  Total Components: {total_components}")
        report.append(f"  ✅ Installed: {installed_count}")
        report.append(f"  ❌ Missing: {missing_count}")
        report.append(f"  🚨 Critical Missing: {critical_missing}")
        
        # Component status
        if self.results["missing"]:
            report.append(f"\n❌ MISSING COMPONENTS:")
            for name in self.results["missing"]:
                info = REQUIRED_COMPONENTS[name]
                criticality = "🚨 CRITICAL" if info.get("critical") else "⚠️ Optional"
                report.append(f"  • {name} - {criticality}")
                report.append(f"    Purpose: {info['purpose']}")
                
        if self.results["version_mismatch"]:
            report.append(f"\n⚠️ VERSION MISMATCHES:")
            for name in self.results["version_mismatch"]:
                report.append(f"  • {name}")
                
        # Web page impact
        report.append(f"\n🌐 WEB PAGE IMPACT:")
        if critical_missing > 0:
            report.append(f"  🚨 {Colors.RED}CRITICAL: Web page may not load properly!{Colors.END}")
            report.append(f"     Missing critical components will cause:")
            for name in self.results["critical_missing"]:
                info = REQUIRED_COMPONENTS[name]
                report.append(f"     • {info['purpose']}")
        else:
            report.append(f"  ✅ {Colors.GREEN}All critical components present - web page should load properly{Colors.END}")
            
        return "\n".join(report)

    def save_report(self, filename: str = None):
        """Save report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cryptominer_component_report_{timestamp}.txt"
            
        report_content = self.generate_report()
        # Remove color codes for file output
        import re
        clean_report = re.sub(r'\033\[[0-9;]*m', '', report_content)
        
        with open(filename, 'w') as f:
            f.write(clean_report)
            f.write(f"\n\nGenerated on: {datetime.now()}")
            f.write(f"\nPython: {sys.version}")
            f.write(f"\nVirtual Environment: {self.use_venv}")
            
        print(f"{Icons.SUCCESS} Report saved to: {filename}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CryptoMiner Pro Python Components Verification & Installation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python verify_components.py                    # Check all components
  python verify_components.py --install         # Install missing critical components
  python verify_components.py --install-all     # Install all missing components
  python verify_components.py --report          # Generate detailed report
  python verify_components.py --save-report     # Save report to file
        """
    )
    
    parser.add_argument('--install', action='store_true', 
                       help='Install missing critical components')
    parser.add_argument('--install-all', action='store_true',
                       help='Install all missing components (including optional)')
    parser.add_argument('--report', action='store_true',
                       help='Show detailed report')
    parser.add_argument('--save-report', action='store_true',
                       help='Save report to file')
    parser.add_argument('--quiet', action='store_true',
                       help='Minimize output')
    
    args = parser.parse_args()
    
    verifier = ComponentVerifier()
    
    if not args.quiet:
        verifier.print_header()
    
    # Verify components
    results = verifier.verify_all_components()
    
    # Install if requested
    if args.install or args.install_all:
        verifier.install_missing_components(install_optional=args.install_all)
        
        # Re-verify after installation
        print(f"\n{Icons.CHECK} Re-verifying components after installation...")
        results = verifier.verify_all_components()
    
    # Generate report
    if args.report or not args.quiet:
        print(verifier.generate_report())
        
    if args.save_report:
        verifier.save_report()
    
    # Exit with appropriate code
    if results["critical_missing"]:
        print(f"\n{Icons.ERROR} {Colors.RED}CRITICAL components are missing! Web application may not work properly.{Colors.END}")
        print(f"{Colors.YELLOW}Run with --install to install missing critical components.{Colors.END}")
        sys.exit(1)
    elif results["missing"]:
        print(f"\n{Icons.WARNING} {Colors.YELLOW}Some optional components are missing. Core functionality should work.{Colors.END}")
        print(f"{Colors.CYAN}Run with --install-all to install all missing components.{Colors.END}")
        sys.exit(0)
    else:
        print(f"\n{Icons.SUCCESS} {Colors.GREEN}All components verified successfully! CryptoMiner Pro web application should work perfectly.{Colors.END}")
        sys.exit(0)

if __name__ == "__main__":
    main()