#!/usr/bin/env python3
"""
Test graceful shutdown with real pool connection to reproduce socket errors
"""

import subprocess
import signal
import time
import sys
import os

def test_real_pool_shutdown():
    """Test shutdown with real pool connection"""
    print("🧪 Testing CryptoMiner shutdown with real pool connection...")
    
    # Use a real pool that's likely to be available
    cmd = [
        sys.executable, '/app/cryptominer.py',
        '--coin', 'LTC',
        '--wallet', 'ltc1qqvz2zw9hqd804a03xg95m4594p7v7thk25sztl',
        '--pool', 'stratum+tcp://ltc.luckymonster.pro:4112',  # Real pool
        '--threads', '2',
        '--intensity', '50',
        '--web-port', '3333',
        '--verbose'
    ]
    
    print(f"Starting with real pool: {' '.join(cmd)}")
    
    # Clear previous log
    if os.path.exists('/app/mining.log'):
        with open('/app/mining.log', 'w') as f:
            f.write("")
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    # Let it run for 3 seconds to establish connection
    print("⏱️  Letting it run for 3 seconds to establish pool connection...")
    time.sleep(3)
    
    # Send SIGINT
    print("📡 Sending SIGINT (Ctrl+C)...")
    process.send_signal(signal.SIGINT)
    
    # Wait for process to finish
    try:
        stdout, _ = process.communicate(timeout=15)
        print("✅ Process finished")
    except subprocess.TimeoutExpired:
        print("⚠️  Process didn't finish, sending second SIGINT...")
        process.send_signal(signal.SIGINT)
        try:
            stdout, _ = process.communicate(timeout=5)
            print("✅ Process finished after second SIGINT")
        except subprocess.TimeoutExpired:
            print("🔪 Force killing process...")
            process.kill()
            stdout, _ = process.communicate()
    
    # Check for the specific errors in the log
    print("\n🔍 Checking for shutdown errors...")
    
    if os.path.exists('/app/mining.log'):
        with open('/app/mining.log', 'r') as f:
            log_content = f.read()
        
        # Look for the specific patterns mentioned in the review request
        bad_fd_errors = []
        negative_fd_errors = []
        errno9_errors = []
        
        lines = log_content.split('\n')
        for i, line in enumerate(lines):
            if 'Bad file descriptor' in line:
                bad_fd_errors.append(f"Line {i+1}: {line.strip()}")
            if 'file descriptor cannot be a negative integer (-1)' in line:
                negative_fd_errors.append(f"Line {i+1}: {line.strip()}")
            if 'Failed to receive message: [Errno 9]' in line:
                errno9_errors.append(f"Line {i+1}: {line.strip()}")
        
        print(f"❌ 'Bad file descriptor' errors: {len(bad_fd_errors)}")
        for error in bad_fd_errors[:3]:  # Show first 3
            print(f"   {error}")
        
        print(f"❌ 'negative integer (-1)' errors: {len(negative_fd_errors)}")
        for error in negative_fd_errors[:3]:  # Show first 3
            print(f"   {error}")
        
        print(f"❌ 'Errno 9' errors: {len(errno9_errors)}")
        for error in errno9_errors[:3]:  # Show first 3
            print(f"   {error}")
        
        # Look for graceful shutdown messages
        graceful_messages = []
        for line in lines:
            if any(msg in line for msg in [
                'Stopping mining (press Ctrl+C again to force exit)',
                'Mining stopped',
                'Pool connection closed',
                'All mining threads stopped'
            ]):
                graceful_messages.append(line.strip())
        
        print(f"\n✅ Graceful shutdown messages: {len(graceful_messages)}")
        for msg in graceful_messages:
            print(f"   {msg}")
        
        total_errors = len(bad_fd_errors) + len(negative_fd_errors) + len(errno9_errors)
        
        if total_errors > 0:
            print(f"\n⚠️  CONFIRMED: Shutdown produces {total_errors} noisy socket errors")
            print("   These errors occur when StratumClient socket operations fail during shutdown")
            print("   The application should handle socket closure more gracefully")
            return False, total_errors
        else:
            print("\n✅ No socket errors found during shutdown")
            return True, 0
    else:
        print("⚠️  No mining.log found")
        return False, 0

if __name__ == "__main__":
    success, error_count = test_real_pool_shutdown()
    print(f"\n📊 RESULT: {'PASS' if success else 'FAIL'} - {error_count} socket errors found")
    sys.exit(0 if success else 1)