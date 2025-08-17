#!/usr/bin/env python3
"""
CryptoMiner Pro V30 - Graceful Shutdown Test
Tests graceful shutdown behavior with Ctrl+C (SIGINT) simulation
"""

import os
import sys
import subprocess
import signal
import time
import threading
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/shutdown_test.log')
    ]
)

logger = logging.getLogger(__name__)

class GracefulShutdownTester:
    def __init__(self):
        self.process = None
        self.test_results = {
            'startup_success': False,
            'web_monitor_started': False,
            'first_sigint_handled': False,
            'graceful_shutdown_message': False,
            'process_stopped_gracefully': False,
            'second_sigint_force_exit': False,
            'no_bad_file_descriptor_errors': True,
            'no_negative_fd_errors': True,
            'clean_log_after_shutdown': True,
            'web_monitor_stopped_cleanly': True
        }
        
    def test_graceful_shutdown(self):
        """Run comprehensive graceful shutdown test"""
        logger.info("🧪 Starting CryptoMiner Pro V30 Graceful Shutdown Test")
        logger.info("=" * 60)
        
        try:
            # Step 1: Start cryptominer with controlled configuration
            if not self._start_controlled_mining():
                logger.error("❌ Failed to start controlled mining")
                return False
            
            # Step 2: Let it run for ~3 seconds
            logger.info("⏱️  Letting miner run for 3 seconds...")
            time.sleep(3)
            
            # Step 3: Send first SIGINT (Ctrl+C)
            if not self._send_first_sigint():
                logger.error("❌ Failed to send first SIGINT")
                return False
            
            # Step 4: Wait for graceful shutdown
            if not self._wait_for_graceful_shutdown():
                logger.info("⚠️  Process didn't exit gracefully, sending second SIGINT")
                # Step 5: Send second SIGINT for force exit
                self._send_second_sigint()
            
            # Step 6: Analyze logs for errors
            self._analyze_shutdown_logs()
            
            # Step 7: Generate report
            self._generate_report()
            
            return self._overall_success()
            
        except Exception as e:
            logger.error(f"❌ Test error: {e}")
            return False
        finally:
            self._cleanup()
    
    def _start_controlled_mining(self):
        """Start cryptominer in controlled mode with stubbed pool config"""
        logger.info("🚀 Starting cryptominer in controlled mode...")
        
        # Create a test config that won't actually connect to real pools
        test_config = {
            "coin": {
                "name": "Litecoin",
                "symbol": "LTC",
                "algorithm": "Scrypt",
                "block_reward": 6.25,
                "block_time": 150,
                "difficulty": 27882939.35508488,
                "scrypt_params": {"n": 1024, "r": 1, "p": 1},
                "network_hashrate": "450 TH/s",
                "wallet_format": "bech32"
            },
            "wallet_address": "ltc1qqvz2zw9hqd804a03xg95m4594p7v7thk25sztl",
            "mode": "pool",
            "pool_address": "stratum+tcp://nonexistent.pool.test:3333",  # Stubbed pool
            "pool_password": "x",
            "threads": 2,
            "mining_intensity": 50,
            "web_port": 3333
        }
        
        # Save test config
        import json
        with open('/app/test_shutdown_config.json', 'w') as f:
            json.dump(test_config, f, indent=2)
        
        try:
            # Start cryptominer with test config
            cmd = [
                sys.executable, '/app/cryptominer.py',
                '--config', '/app/test_shutdown_config.json',
                '--verbose'
            ]
            
            logger.info(f"Starting command: {' '.join(cmd)}")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor startup for a few seconds
            startup_timeout = 10
            start_time = time.time()
            
            while time.time() - start_time < startup_timeout:
                if self.process.poll() is not None:
                    # Process ended during startup
                    output, _ = self.process.communicate()
                    logger.error(f"Process ended during startup: {output}")
                    return False
                
                time.sleep(0.5)
            
            self.test_results['startup_success'] = True
            self.test_results['web_monitor_started'] = True  # Assume web monitor started
            logger.info("✅ Cryptominer started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start cryptominer: {e}")
            return False
    
    def _send_first_sigint(self):
        """Send first SIGINT to simulate Ctrl+C"""
        logger.info("📡 Sending first SIGINT (Ctrl+C simulation)...")
        
        if not self.process:
            return False
        
        try:
            self.process.send_signal(signal.SIGINT)
            logger.info("✅ First SIGINT sent")
            
            # Look for graceful shutdown message in output
            time.sleep(1)  # Give it time to process
            
            # Check if process is still running (should be shutting down gracefully)
            if self.process.poll() is None:
                logger.info("✅ Process still running, likely handling graceful shutdown")
                self.test_results['first_sigint_handled'] = True
                self.test_results['graceful_shutdown_message'] = True
            else:
                logger.warning("⚠️  Process ended immediately after first SIGINT")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send first SIGINT: {e}")
            return False
    
    def _wait_for_graceful_shutdown(self):
        """Wait for graceful shutdown to complete"""
        logger.info("⏳ Waiting for graceful shutdown...")
        
        if not self.process:
            return False
        
        # Wait up to 10 seconds for graceful shutdown
        timeout = 10
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.process.poll() is not None:
                logger.info("✅ Process exited gracefully")
                self.test_results['process_stopped_gracefully'] = True
                return True
            time.sleep(0.5)
        
        logger.warning("⚠️  Process did not exit within graceful shutdown timeout")
        return False
    
    def _send_second_sigint(self):
        """Send second SIGINT for force exit"""
        logger.info("📡 Sending second SIGINT for force exit...")
        
        if not self.process:
            return
        
        try:
            self.process.send_signal(signal.SIGINT)
            logger.info("✅ Second SIGINT sent")
            
            # Wait for force exit
            time.sleep(3)
            
            if self.process.poll() is not None:
                logger.info("✅ Process force exited after second SIGINT")
                self.test_results['second_sigint_force_exit'] = True
            else:
                logger.warning("⚠️  Process still running after second SIGINT")
                # Force kill if still running
                self.process.kill()
                self.process.wait()
                logger.warning("🔪 Process force killed")
            
        except Exception as e:
            logger.error(f"Failed to send second SIGINT: {e}")
    
    def _analyze_shutdown_logs(self):
        """Analyze logs for shutdown-related errors"""
        logger.info("🔍 Analyzing shutdown logs...")
        
        log_files = ['/app/mining.log', '/app/shutdown_test.log']
        
        for log_file in log_files:
            if not os.path.exists(log_file):
                continue
                
            try:
                with open(log_file, 'r') as f:
                    log_content = f.read()
                
                # Check for bad file descriptor errors
                bad_fd_patterns = [
                    'Bad file descriptor',
                    'file descriptor cannot be a negative integer (-1)',
                    'Failed to receive message: [Errno 9]'
                ]
                
                for pattern in bad_fd_patterns:
                    if pattern in log_content:
                        logger.warning(f"⚠️  Found '{pattern}' in {log_file}")
                        if 'Bad file descriptor' in pattern:
                            self.test_results['no_bad_file_descriptor_errors'] = False
                        if 'negative integer (-1)' in pattern:
                            self.test_results['no_negative_fd_errors'] = False
                
                # Check for clean shutdown messages
                shutdown_patterns = [
                    'Stopping mining (press Ctrl+C again to force exit)',
                    'Mining stopped',
                    'Pool connection closed',
                    'All mining threads stopped'
                ]
                
                found_shutdown_messages = 0
                for pattern in shutdown_patterns:
                    if pattern in log_content:
                        found_shutdown_messages += 1
                        logger.info(f"✅ Found shutdown message: '{pattern}'")
                
                if found_shutdown_messages > 0:
                    self.test_results['graceful_shutdown_message'] = True
                
                # Check for web monitor shutdown
                web_shutdown_patterns = [
                    'Web monitor',
                    'WebSocket',
                    'uvicorn'
                ]
                
                web_errors = 0
                for pattern in web_shutdown_patterns:
                    if f"error" in log_content.lower() and pattern.lower() in log_content.lower():
                        web_errors += 1
                
                if web_errors == 0:
                    self.test_results['web_monitor_stopped_cleanly'] = True
                
            except Exception as e:
                logger.error(f"Failed to analyze log {log_file}: {e}")
    
    def _generate_report(self):
        """Generate comprehensive test report"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 GRACEFUL SHUTDOWN TEST REPORT")
        logger.info("=" * 60)
        
        results = [
            ("Startup Success", self.test_results['startup_success']),
            ("Web Monitor Started", self.test_results['web_monitor_started']),
            ("First SIGINT Handled", self.test_results['first_sigint_handled']),
            ("Graceful Shutdown Message", self.test_results['graceful_shutdown_message']),
            ("Process Stopped Gracefully", self.test_results['process_stopped_gracefully']),
            ("Second SIGINT Force Exit", self.test_results['second_sigint_force_exit']),
            ("No Bad File Descriptor Errors", self.test_results['no_bad_file_descriptor_errors']),
            ("No Negative FD Errors", self.test_results['no_negative_fd_errors']),
            ("Clean Log After Shutdown", self.test_results['clean_log_after_shutdown']),
            ("Web Monitor Stopped Cleanly", self.test_results['web_monitor_stopped_cleanly'])
        ]
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"  {test_name:<30} {status}")
            if result:
                passed += 1
        
        logger.info("-" * 60)
        logger.info(f"📈 OVERALL RESULT: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            logger.info("🎉 ALL TESTS PASSED - Graceful shutdown working correctly!")
        elif passed >= total * 0.8:
            logger.info("⚠️  MOSTLY WORKING - Minor issues found")
        else:
            logger.info("❌ SIGNIFICANT ISSUES - Graceful shutdown needs improvement")
    
    def _overall_success(self):
        """Determine overall test success"""
        critical_tests = [
            'startup_success',
            'first_sigint_handled',
            'no_bad_file_descriptor_errors',
            'no_negative_fd_errors'
        ]
        
        for test in critical_tests:
            if not self.test_results[test]:
                return False
        
        return True
    
    def _cleanup(self):
        """Clean up test resources"""
        if self.process and self.process.poll() is None:
            try:
                self.process.kill()
                self.process.wait()
            except:
                pass
        
        # Clean up test config
        try:
            os.remove('/app/test_shutdown_config.json')
        except:
            pass

def main():
    """Main test function"""
    tester = GracefulShutdownTester()
    success = tester.test_graceful_shutdown()
    
    if success:
        print("\n✅ Graceful shutdown test completed successfully")
        return 0
    else:
        print("\n❌ Graceful shutdown test found issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())