#!/usr/bin/env python3
"""
Simple test to reproduce the shutdown issue with socket errors
"""

import subprocess
import signal
import time
import sys
import os

def test_shutdown_issue():
    """Test the specific shutdown issue mentioned in review request"""
    print("🧪 Testing CryptoMiner shutdown issue reproduction...")
    
    # Start cryptominer with minimal config
    cmd = [
        sys.executable, '/app/cryptominer.py',
        '--coin', 'LTC',
        '--wallet', 'ltc1qqvz2zw9hqd804a03xg95m4594p7v7thk25sztl',
        '--pool', 'stratum+tcp://nonexistent.pool.test:3333',
        '--threads', '2',
        '--intensity', '50',
        '--web-port', '3333',
        '--verbose'
    ]
    
    print(f"Starting: {' '.join(cmd)}")
    
    # Clear previous log
    if os.path.exists('/app/mining.log'):
        with open('/app/mining.log', 'w') as f:
            f.write("")
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    # Let it run for 3 seconds
    print("⏱️  Letting it run for 3 seconds...")
    time.sleep(3)
    
    # Send SIGINT
    print("📡 Sending SIGINT (Ctrl+C)...")
    process.send_signal(signal.SIGINT)
    
    # Wait for process to finish
    try:
        stdout, _ = process.communicate(timeout=10)
        print("✅ Process finished")
    except subprocess.TimeoutExpired:
        print("⚠️  Process didn't finish, killing...")
        process.kill()
        stdout, _ = process.communicate()
    
    # Check for the specific errors in the log
    print("\n🔍 Checking for shutdown errors...")
    
    if os.path.exists('/app/mining.log'):
        with open('/app/mining.log', 'r') as f:
            log_content = f.read()
        
        bad_fd_count = log_content.count('Bad file descriptor')
        negative_fd_count = log_content.count('file descriptor cannot be a negative integer (-1)')
        errno9_count = log_content.count('Failed to receive message: [Errno 9]')
        
        print(f"❌ 'Bad file descriptor' errors: {bad_fd_count}")
        print(f"❌ 'negative integer (-1)' errors: {negative_fd_count}")
        print(f"❌ 'Errno 9' errors: {errno9_count}")
        
        if bad_fd_count > 0 or negative_fd_count > 0 or errno9_count > 0:
            print("\n⚠️  CONFIRMED: Shutdown produces noisy socket errors")
            print("   These errors occur when StratumClient socket is closed during shutdown")
            print("   The application should handle socket closure more gracefully")
            return False
        else:
            print("\n✅ No socket errors found during shutdown")
            return True
    else:
        print("⚠️  No mining.log found")
        return False

if __name__ == "__main__":
    success = test_shutdown_issue()
    sys.exit(0 if success else 1)