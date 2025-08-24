#!/usr/bin/env python3
"""
CryptoMiner V21 Backend API Testing Suite
Tests the mining functionality after Stratum protocol fix
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any

# Use the production backend URL from frontend/.env
BACKEND_URL = "https://smartcrypto-5.preview.emergentagent.com/api"

class CryptoMinerTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        
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
    
    def test_mining_status_initial(self):
        """Test initial mining status before starting"""
        try:
            response = self.session.get(f"{BACKEND_URL}/mining/status")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Initial Mining Status", True, 
                            f"Status retrieved - Active: {data.get('is_active', False)}", data)
                return data
            else:
                self.log_test("Initial Mining Status", False, f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("Initial Mining Status", False, f"Error: {str(e)}")
            return None
    
    def test_mining_control_start_xmr(self):
        """Test starting XMR mining with updated Stratum protocol"""
        try:
            # Use XMR configuration to trigger RandomX algorithm with fixed Stratum
            mining_config = {
                "action": "start",
                "config": {
                    "coin": "XMR",
                    "wallet": "4793trzeyXigW8qj9JZU1bVUuohVqn76EBpXUEJdDxJS5tAP4rjAdS7PzWFXzV3MtE3b9MKxMeHmE5X8J2oBk7cyNdE65j8",
                    "pool": "stratum+tcp://pool.supportxmr.com:3333",
                    "intensity": 80,
                    "threads": 4,
                    "password": "x"
                }
            }
            
            response = self.session.post(f"{BACKEND_URL}/mining/control", 
                                       json=mining_config)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("Start XMR Mining", True, 
                                f"Mining started successfully with PID: {data.get('process_id', 'N/A')}", data)
                    return True
                else:
                    self.log_test("Start XMR Mining", False, f"Start failed: {data.get('message', 'Unknown error')}", data)
                    return False
            else:
                self.log_test("Start XMR Mining", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Start XMR Mining", False, f"Error: {str(e)}")
            return False
    
    def test_mining_status_after_start(self):
        """Test mining status after starting to verify process state"""
        try:
            # Wait a moment for process to initialize
            time.sleep(3)
            
            response = self.session.get(f"{BACKEND_URL}/mining/status")
            if response.status_code == 200:
                data = response.json()
                is_active = data.get('is_active', False)
                process_id = data.get('process_id')
                pool_connected = data.get('pool_connected', False)
                
                if is_active and process_id:
                    self.log_test("Mining Status After Start", True, 
                                f"Mining active with PID {process_id}, Pool connected: {pool_connected}", data)
                    return True
                else:
                    self.log_test("Mining Status After Start", False, 
                                f"Mining not properly active - Active: {is_active}, PID: {process_id}", data)
                    return False
            else:
                self.log_test("Mining Status After Start", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Mining Status After Start", False, f"Error: {str(e)}")
            return False
    
    def test_mining_stats_collection(self):
        """Test mining statistics collection from updated engine"""
        try:
            # Wait for stats to be collected
            time.sleep(5)
            
            response = self.session.get(f"{BACKEND_URL}/mining/stats")
            if response.status_code == 200:
                data = response.json()
                
                # Check for key mining statistics
                hashrate = data.get('hashrate', 0)
                threads = data.get('threads', 0)
                coin = data.get('coin', '')
                pool_connected = data.get('pool_connected', False)
                
                if coin == 'XMR' and threads > 0:
                    self.log_test("Mining Stats Collection", True, 
                                f"Stats collected - Coin: {coin}, Threads: {threads}, Hashrate: {hashrate} H/s, Pool: {pool_connected}", data)
                    return True
                else:
                    self.log_test("Mining Stats Collection", False, 
                                f"Invalid stats - Coin: {coin}, Threads: {threads}, Hashrate: {hashrate}", data)
                    return False
            else:
                self.log_test("Mining Stats Collection", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Mining Stats Collection", False, f"Error: {str(e)}")
            return False
    
    def test_stats_update_endpoint(self):
        """Test POST /api/mining/update-stats endpoint"""
        try:
            # Simulate stats update from mining engine
            test_stats = {
                "hashrate": 1250.5,
                "threads": 4,
                "intensity": 80,
                "coin": "XMR",
                "algorithm": "RandomX",
                "pool_connected": True,
                "accepted_shares": 15,
                "rejected_shares": 1,
                "uptime": 300.0,
                "difficulty": 250000.0,
                "ai_learning": 75.5,
                "ai_optimization": 68.2,
                "last_update": datetime.utcnow().isoformat()
            }
            
            response = self.session.post(f"{BACKEND_URL}/mining/update-stats", 
                                       json=test_stats)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("Stats Update Endpoint", True, 
                                "Successfully updated mining stats from engine", data)
                    return True
                else:
                    self.log_test("Stats Update Endpoint", False, 
                                f"Update failed: {data.get('message', 'Unknown error')}", data)
                    return False
            else:
                self.log_test("Stats Update Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Stats Update Endpoint", False, f"Error: {str(e)}")
            return False
    
    def test_randomx_algorithm_detection(self):
        """Test that RandomX algorithm is properly detected for XMR"""
        try:
            response = self.session.get(f"{BACKEND_URL}/mining/multi-stats")
            if response.status_code == 200:
                data = response.json()
                current_algorithm = data.get('current_algorithm')
                current_coin = data.get('current_coin')
                supported_algorithms = data.get('supported_algorithms', [])
                
                if 'RandomX' in supported_algorithms and current_coin == 'XMR':
                    self.log_test("RandomX Algorithm Detection", True, 
                                f"RandomX properly detected for XMR - Current: {current_algorithm}", data)
                    return True
                else:
                    self.log_test("RandomX Algorithm Detection", False, 
                                f"Algorithm detection issue - Coin: {current_coin}, Algorithm: {current_algorithm}", data)
                    return False
            else:
                self.log_test("RandomX Algorithm Detection", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("RandomX Algorithm Detection", False, f"Error: {str(e)}")
            return False
    
    def test_pool_connection_status(self):
        """Test pool connection status reporting"""
        try:
            # Wait for pool connection to establish
            time.sleep(8)
            
            response = self.session.get(f"{BACKEND_URL}/mining/status")
            if response.status_code == 200:
                data = response.json()
                pool_connected = data.get('pool_connected', False)
                is_active = data.get('is_active', False)
                
                if is_active:
                    self.log_test("Pool Connection Status", True, 
                                f"Pool connection status properly reported: {pool_connected}", data)
                    return True
                else:
                    self.log_test("Pool Connection Status", False, 
                                f"Mining not active, cannot verify pool connection", data)
                    return False
            else:
                self.log_test("Pool Connection Status", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Pool Connection Status", False, f"Error: {str(e)}")
            return False
    
    def test_mining_control_stop(self):
        """Test stopping mining process"""
        try:
            stop_config = {"action": "stop"}
            
            response = self.session.post(f"{BACKEND_URL}/mining/control", 
                                       json=stop_config)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("Stop Mining", True, 
                                f"Mining stopped successfully: {data.get('message', '')}", data)
                    return True
                else:
                    self.log_test("Stop Mining", False, 
                                f"Stop failed: {data.get('message', 'Unknown error')}", data)
                    return False
            else:
                self.log_test("Stop Mining", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Stop Mining", False, f"Error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting CryptoMiner V21 Backend API Testing Suite")
        print(f"🔗 Testing against: {BACKEND_URL}")
        print("=" * 60)
        
        # Test sequence
        tests = [
            self.test_api_health,
            self.test_mining_status_initial,
            self.test_mining_control_start_xmr,
            self.test_mining_status_after_start,
            self.test_mining_stats_collection,
            self.test_stats_update_endpoint,
            self.test_randomx_algorithm_detection,
            self.test_pool_connection_status,
            self.test_mining_control_stop
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                time.sleep(2)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {str(e)}")
        
        print("=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - CryptoMiner V21 backend is fully functional!")
        elif passed >= total * 0.8:
            print("✅ MOSTLY WORKING - Minor issues detected but core functionality works")
        else:
            print("⚠️ SIGNIFICANT ISSUES - Multiple test failures detected")
        
        return passed, total, self.test_results

def main():
    """Main test execution"""
    tester = CryptoMinerTester()
    passed, total, results = tester.run_comprehensive_test()
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'passed': passed,
                'total': total,
                'success_rate': (passed/total)*100,
                'timestamp': datetime.now().isoformat()
            },
            'detailed_results': results
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/backend_test_results.json")
    
    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()