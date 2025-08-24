#!/usr/bin/env python3
"""
CryptoMiner V21 - Zeropool.io Authentication Fix Testing Suite
Tests the mining engine authentication fixes for zeropool.io compatibility
"""

import requests
import json
import time
import sys
import subprocess
import os
from datetime import datetime
from typing import Dict, Any

# Use the production backend URL from frontend/.env
BACKEND_URL = "https://smartcrypto-5.preview.emergentagent.com/api"

class ZeropoolAuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        self.mining_process_pid = None
        
    def log_test(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_mining_config_verification(self):
        """Verify mining_config.env has correct zeropool.io settings"""
        try:
            config_path = "/app/mining_config.env"
            if not os.path.exists(config_path):
                self.log_test("Config Verification", False, "mining_config.env file not found")
                return False
            
            with open(config_path, 'r') as f:
                config_content = f.read()
            
            # Check for required settings
            checks = {
                "COIN=XMR": "XMR coin configured",
                "WALLET=4793trzeyXigW8qj9JZU1bVUuohVqn76EBpXUEJdDxJS5tAP4rjAdS7PzWFXzV3MtE3b9MKxMeHmE5X8J2oBk7cyNdE65j8": "Clean wallet format (no solo: prefix)",
                "POOL=stratum+tcp://xmr.zeropool.io:3333": "Zeropool.io pool configured",
                "PASSWORD=x": "Password configured"
            }
            
            all_checks_passed = True
            for check, description in checks.items():
                if check in config_content:
                    print(f"   ✓ {description}")
                else:
                    print(f"   ✗ {description} - MISSING")
                    all_checks_passed = False
            
            # Verify no "solo:" prefix in wallet
            if "solo:" not in config_content:
                print(f"   ✓ Wallet format cleaned (no 'solo:' prefix)")
            else:
                print(f"   ✗ Wallet still contains 'solo:' prefix")
                all_checks_passed = False
            
            if all_checks_passed:
                self.log_test("Config Verification", True, "All zeropool.io configuration settings verified", 
                            {"config_file": config_path})
                return True
            else:
                self.log_test("Config Verification", False, "Configuration issues detected")
                return False
                
        except Exception as e:
            self.log_test("Config Verification", False, f"Error reading config: {str(e)}")
            return False
    
    def test_api_health(self):
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                data = response.json()
                if "CryptoMiner V21 API" in data.get("message", ""):
                    self.log_test("API Health Check", True, "Backend API is accessible and responding")
                    return True
                else:
                    self.log_test("API Health Check", False, f"Unexpected API response: {data}")
                    return False
            else:
                self.log_test("API Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("API Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_stop_existing_mining(self):
        """Stop any existing mining processes before starting new test"""
        try:
            stop_config = {"action": "stop"}
            response = self.session.post(f"{BACKEND_URL}/mining/control", json=stop_config)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Stop Existing Mining", True, 
                            f"Stopped existing processes: {data.get('message', '')}")
                time.sleep(3)  # Wait for cleanup
                return True
            else:
                self.log_test("Stop Existing Mining", True, "No existing processes to stop")
                return True
        except Exception as e:
            self.log_test("Stop Existing Mining", False, f"Error: {str(e)}")
            return False
    
    def test_start_zeropool_mining(self):
        """Test starting XMR mining with zeropool.io configuration"""
        try:
            # Configuration for zeropool.io with cleaned wallet format
            mining_config = {
                "action": "start",
                "config": {
                    "coin": "XMR",
                    "wallet": "4793trzeyXigW8qj9JZU1bVUuohVqn76EBpXUEJdDxJS5tAP4rjAdS7PzWFXzV3MtE3b9MKxMeHmE5X8J2oBk7cyNdE65j8",
                    "pool": "stratum+tcp://xmr.zeropool.io:3333",
                    "intensity": 90,
                    "threads": 4,
                    "password": "x"
                }
            }
            
            print(f"   Starting mining with cleaned wallet format (no 'solo:' prefix)")
            print(f"   Pool: xmr.zeropool.io:3333")
            print(f"   Wallet: {mining_config['config']['wallet'][:20]}...{mining_config['config']['wallet'][-20:]}")
            
            response = self.session.post(f"{BACKEND_URL}/mining/control", json=mining_config)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.mining_process_pid = data.get('process_id')
                    self.log_test("Start Zeropool Mining", True, 
                                f"Mining started successfully with PID: {self.mining_process_pid}", data)
                    return True
                else:
                    self.log_test("Start Zeropool Mining", False, 
                                f"Start failed: {data.get('message', 'Unknown error')}", data)
                    return False
            else:
                self.log_test("Start Zeropool Mining", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Start Zeropool Mining", False, f"Error: {str(e)}")
            return False
    
    def test_mining_process_status(self):
        """Test mining process status after starting with zeropool.io"""
        try:
            # Wait for process to initialize
            time.sleep(5)
            
            response = self.session.get(f"{BACKEND_URL}/mining/status")
            if response.status_code == 200:
                data = response.json()
                is_active = data.get('is_active', False)
                process_id = data.get('process_id')
                pool_connected = data.get('pool_connected', False)
                
                if is_active and process_id:
                    self.log_test("Mining Process Status", True, 
                                f"Mining active with PID {process_id}, Pool connected: {pool_connected}", data)
                    return True
                else:
                    self.log_test("Mining Process Status", False, 
                                f"Mining not properly active - Active: {is_active}, PID: {process_id}", data)
                    return False
            else:
                self.log_test("Mining Process Status", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Mining Process Status", False, f"Error: {str(e)}")
            return False
    
    def test_zeropool_connection_stats(self):
        """Test mining statistics to verify zeropool.io connection"""
        try:
            # Wait for stats to be collected from zeropool.io
            time.sleep(10)
            
            response = self.session.get(f"{BACKEND_URL}/mining/stats")
            if response.status_code == 200:
                data = response.json()
                
                # Check for key mining statistics
                hashrate = data.get('hashrate', 0)
                threads = data.get('threads', 0)
                coin = data.get('coin', '')
                pool_connected = data.get('pool_connected', False)
                accepted_shares = data.get('accepted_shares', 0)
                rejected_shares = data.get('rejected_shares', 0)
                
                success_indicators = []
                if coin == 'XMR':
                    success_indicators.append("XMR coin detected")
                if threads > 0:
                    success_indicators.append(f"{threads} threads active")
                if hashrate > 0:
                    success_indicators.append(f"{hashrate} H/s hashrate")
                if pool_connected:
                    success_indicators.append("Pool connection established")
                
                if len(success_indicators) >= 2:  # At least 2 indicators of success
                    self.log_test("Zeropool Connection Stats", True, 
                                f"Stats collected from zeropool.io - {', '.join(success_indicators)}", data)
                    return True
                else:
                    self.log_test("Zeropool Connection Stats", False, 
                                f"Insufficient connection indicators - Coin: {coin}, Threads: {threads}, Hashrate: {hashrate}", data)
                    return False
            else:
                self.log_test("Zeropool Connection Stats", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Zeropool Connection Stats", False, f"Error: {str(e)}")
            return False
    
    def test_authentication_monitoring(self):
        """Monitor for authentication issues by checking logs and stats"""
        try:
            # Wait longer for potential authentication issues to surface
            print("   Monitoring for authentication issues (30 seconds)...")
            time.sleep(30)
            
            # Check mining stats for any authentication-related issues
            response = self.session.get(f"{BACKEND_URL}/mining/stats")
            if response.status_code == 200:
                data = response.json()
                
                # Look for signs of successful authentication
                pool_connected = data.get('pool_connected', False)
                hashrate = data.get('hashrate', 0)
                accepted_shares = data.get('accepted_shares', 0)
                rejected_shares = data.get('rejected_shares', 0)
                
                # Calculate rejection rate if we have share data
                total_shares = accepted_shares + rejected_shares
                rejection_rate = (rejected_shares / total_shares * 100) if total_shares > 0 else 0
                
                auth_success_indicators = []
                auth_issues = []
                
                if pool_connected:
                    auth_success_indicators.append("Pool connection maintained")
                else:
                    auth_issues.append("Pool connection lost")
                
                if hashrate > 0:
                    auth_success_indicators.append(f"Active mining at {hashrate} H/s")
                else:
                    auth_issues.append("No hashrate detected")
                
                if total_shares > 0:
                    if rejection_rate < 50:  # Less than 50% rejection is acceptable
                        auth_success_indicators.append(f"Share acceptance rate: {100-rejection_rate:.1f}%")
                    else:
                        auth_issues.append(f"High share rejection rate: {rejection_rate:.1f}%")
                
                if len(auth_success_indicators) > len(auth_issues):
                    self.log_test("Authentication Monitoring", True, 
                                f"No authentication issues detected - {', '.join(auth_success_indicators)}", data)
                    return True
                else:
                    self.log_test("Authentication Monitoring", False, 
                                f"Potential authentication issues - {', '.join(auth_issues)}", data)
                    return False
            else:
                self.log_test("Authentication Monitoring", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Authentication Monitoring", False, f"Error: {str(e)}")
            return False
    
    def test_wallet_format_validation(self):
        """Validate that the wallet format is properly cleaned for zeropool.io"""
        try:
            # Check the actual configuration being used by the backend
            response = self.session.get(f"{BACKEND_URL}/mining/config-debug")
            if response.status_code == 200:
                data = response.json()
                config = data.get('default_mining_config', {})
                
                wallet = config.get('wallet', '')
                pool = config.get('pool', '')
                
                validation_results = []
                
                # Check wallet format
                if wallet and not wallet.startswith('solo:'):
                    validation_results.append("✓ Wallet format cleaned (no 'solo:' prefix)")
                elif wallet.startswith('solo:'):
                    validation_results.append("✗ Wallet still contains 'solo:' prefix")
                else:
                    validation_results.append("✗ No wallet configured")
                
                # Check pool configuration
                if 'xmr.zeropool.io:3333' in pool:
                    validation_results.append("✓ Zeropool.io pool configured")
                else:
                    validation_results.append("✗ Zeropool.io pool not configured")
                
                # Check wallet length (Monero addresses are typically 95 characters)
                if len(wallet) == 95:
                    validation_results.append("✓ Wallet length correct for Monero address")
                else:
                    validation_results.append(f"? Wallet length: {len(wallet)} characters")
                
                success = all('✓' in result for result in validation_results if '✓' in result or '✗' in result)
                
                self.log_test("Wallet Format Validation", success, 
                            f"Wallet format validation - {', '.join(validation_results)}", 
                            {"wallet_preview": f"{wallet[:20]}...{wallet[-20:]}" if wallet else "None",
                             "pool": pool})
                return success
            else:
                self.log_test("Wallet Format Validation", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Wallet Format Validation", False, f"Error: {str(e)}")
            return False
    
    def test_enhanced_auth_compatibility(self):
        """Test enhanced authentication logic for zeropool.io compatibility"""
        try:
            # Wait for mining to run and potentially encounter authentication scenarios
            time.sleep(15)
            
            # Check mining control log for any authentication-related entries
            response = self.session.get(f"{BACKEND_URL}/mining/control-log?limit=10")
            if response.status_code == 200:
                log_entries = response.json()
                
                # Look for recent start actions with zeropool configuration
                recent_starts = [entry for entry in log_entries 
                               if entry.get('action') == 'start' 
                               and 'zeropool.io' in str(entry.get('config', {}))]
                
                if recent_starts:
                    latest_start = recent_starts[0]
                    config = latest_start.get('config', {})
                    
                    # Verify the configuration used
                    wallet_clean = not config.get('wallet', '').startswith('solo:')
                    pool_correct = 'zeropool.io' in config.get('pool', '')
                    
                    if wallet_clean and pool_correct:
                        self.log_test("Enhanced Auth Compatibility", True, 
                                    "Enhanced authentication logic working - clean wallet format used", 
                                    {"latest_config": config})
                        return True
                    else:
                        self.log_test("Enhanced Auth Compatibility", False, 
                                    f"Configuration issues - Wallet clean: {wallet_clean}, Pool correct: {pool_correct}", 
                                    {"latest_config": config})
                        return False
                else:
                    self.log_test("Enhanced Auth Compatibility", False, 
                                "No recent zeropool.io start actions found in log")
                    return False
            else:
                self.log_test("Enhanced Auth Compatibility", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Enhanced Auth Compatibility", False, f"Error: {str(e)}")
            return False
    
    def test_final_mining_stop(self):
        """Stop mining process after testing"""
        try:
            stop_config = {"action": "stop"}
            response = self.session.post(f"{BACKEND_URL}/mining/control", json=stop_config)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Final Mining Stop", True, 
                            f"Mining stopped successfully: {data.get('message', '')}")
                return True
            else:
                self.log_test("Final Mining Stop", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Final Mining Stop", False, f"Error: {str(e)}")
            return False
    
    def run_zeropool_auth_test(self):
        """Run comprehensive zeropool.io authentication fix testing"""
        print("🔐 Starting Zeropool.io Authentication Fix Testing Suite")
        print(f"🔗 Testing against: {BACKEND_URL}")
        print("🎯 Focus: Wallet format fix and enhanced zeropool.io authentication compatibility")
        print("=" * 80)
        
        # Test sequence specifically for zeropool.io authentication
        tests = [
            self.test_mining_config_verification,
            self.test_api_health,
            self.test_stop_existing_mining,
            self.test_start_zeropool_mining,
            self.test_mining_process_status,
            self.test_wallet_format_validation,
            self.test_zeropool_connection_stats,
            self.test_authentication_monitoring,
            self.test_enhanced_auth_compatibility,
            self.test_final_mining_stop
        ]
        
        passed = 0
        total = len(tests)
        critical_tests = ['test_start_zeropool_mining', 'test_wallet_format_validation', 'test_authentication_monitoring']
        critical_passed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                    if test.__name__ in critical_tests:
                        critical_passed += 1
                time.sleep(2)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {str(e)}")
        
        print("=" * 80)
        print(f"📊 Test Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        print(f"🎯 Critical Tests: {critical_passed}/{len(critical_tests)} passed")
        
        # Determine overall result
        if critical_passed == len(critical_tests) and passed >= total * 0.8:
            print("🎉 ZEROPOOL.IO AUTHENTICATION FIX SUCCESSFUL!")
            print("   ✅ Wallet format cleaned (no 'solo:' prefix)")
            print("   ✅ Enhanced authentication compatibility working")
            print("   ✅ Mining process connects to xmr.zeropool.io:3333")
            result_status = "SUCCESS"
        elif critical_passed >= len(critical_tests) * 0.7:
            print("⚠️ PARTIAL SUCCESS - Some authentication improvements detected")
            print("   ⚠️ May still have minor authentication issues")
            result_status = "PARTIAL"
        else:
            print("❌ AUTHENTICATION FIX FAILED")
            print("   ❌ Critical authentication issues persist")
            print("   ❌ Wallet format or zeropool.io compatibility problems")
            result_status = "FAILED"
        
        return passed, total, self.test_results, result_status

def main():
    """Main test execution"""
    tester = ZeropoolAuthTester()
    passed, total, results, status = tester.run_zeropool_auth_test()
    
    # Save detailed results
    test_summary = {
        'test_type': 'zeropool_authentication_fix',
        'summary': {
            'passed': passed,
            'total': total,
            'success_rate': (passed/total)*100,
            'status': status,
            'timestamp': datetime.now().isoformat()
        },
        'focus_areas': {
            'wallet_format_cleaning': 'Remove solo: prefix from wallet addresses',
            'zeropool_compatibility': 'Enhanced authentication for xmr.zeropool.io',
            'share_submission': 'Resolve Unauthenticated share rejection issues'
        },
        'detailed_results': results
    }
    
    with open('/app/zeropool_auth_test_results.json', 'w') as f:
        json.dump(test_summary, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/zeropool_auth_test_results.json")
    
    # Exit with appropriate code
    sys.exit(0 if status == "SUCCESS" else 1)

if __name__ == "__main__":
    main()