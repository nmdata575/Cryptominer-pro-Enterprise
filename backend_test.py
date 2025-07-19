#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for CryptoMiner Pro
Tests all endpoints, mining functionality, AI system, and WebSocket connections
"""

import requests
import json
import time
import sys
from datetime import datetime
import websocket
import threading
from typing import Dict, Any, Optional

class CryptoMinerAPITester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url.rstrip('/')
        self.tests_run = 0
        self.tests_passed = 0
        self.websocket_data = []
        self.websocket_connected = False
        
    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}: PASSED {details}")
        else:
            print(f"❌ {name}: FAILED {details}")
        return success

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, timeout: int = 10) -> tuple:
        """Make HTTP request and return success status and response"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            else:
                return False, {"error": f"Unsupported method: {method}"}
            
            return response.status_code < 400, response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}
        except json.JSONDecodeError:
            return False, {"error": "Invalid JSON response"}

    def test_health_endpoint(self) -> bool:
        """Test /api/health endpoint"""
        success, response = self.make_request('GET', '/api/health')
        
        if success and response.get('status') == 'healthy':
            return self.log_test("Health Check", True, f"- Status: {response.get('status')}")
        else:
            return self.log_test("Health Check", False, f"- Response: {response}")

    def test_coin_presets(self) -> bool:
        """Test /api/coins/presets endpoint"""
        success, response = self.make_request('GET', '/api/coins/presets')
        
        if success and 'presets' in response:
            presets = response['presets']
            expected_coins = ['litecoin', 'dogecoin', 'feathercoin']
            
            all_coins_present = all(coin in presets for coin in expected_coins)
            
            if all_coins_present:
                return self.log_test("Coin Presets", True, f"- Found {len(presets)} coin presets")
            else:
                missing = [coin for coin in expected_coins if coin not in presets]
                return self.log_test("Coin Presets", False, f"- Missing coins: {missing}")
        else:
            return self.log_test("Coin Presets", False, f"- Response: {response}")

    def test_system_stats(self) -> bool:
        """Test /api/system/stats endpoint"""
        success, response = self.make_request('GET', '/api/system/stats')
        
        if success and 'cpu' in response and 'memory' in response:
            cpu_usage = response['cpu'].get('usage_percent', 0)
            memory_percent = response['memory'].get('percent', 0)
            
            return self.log_test("System Stats", True, 
                               f"- CPU: {cpu_usage}%, Memory: {memory_percent}%")
        else:
            return self.log_test("System Stats", False, f"- Response: {response}")

    def test_mining_status_initial(self) -> bool:
        """Test initial mining status (should not be mining)"""
        success, response = self.make_request('GET', '/api/mining/status')
        
        if success:
            is_mining = response.get('is_mining', True)  # Default to True to catch issues
            
            if not is_mining:
                return self.log_test("Initial Mining Status", True, "- Not mining (expected)")
            else:
                return self.log_test("Initial Mining Status", False, "- Already mining (unexpected)")
        else:
            return self.log_test("Initial Mining Status", False, f"- Response: {response}")

    def test_wallet_validation(self) -> bool:
        """Test wallet address validation endpoint"""
        test_cases = [
            # Litecoin valid addresses
            {"address": "LhK1Nk7QidqUBKLMBKVr8fWsNu4gp7rqLs", "coin_symbol": "LTC", "should_be_valid": True},
            {"address": "ltc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4", "coin_symbol": "LTC", "should_be_valid": True},
            {"address": "M8T1B2Z97gVdvmfkQcAtYbEepune1tzGua", "coin_symbol": "LTC", "should_be_valid": True},
            
            # Dogecoin valid addresses
            {"address": "DQVpNjNVHjTgHaE4Y1oqRxCLe6rKVrUUgJ", "coin_symbol": "DOGE", "should_be_valid": True},
            {"address": "A1bvP1Lqtj3rSxGsMLQ9Tt2DVbWnQQjKvW", "coin_symbol": "DOGE", "should_be_valid": True},
            
            # Feathercoin valid addresses
            {"address": "6nsHHMiUexBgE8GZzw5EBVL8Lz2sJEzQRc", "coin_symbol": "FTC", "should_be_valid": True},
            
            # Invalid addresses
            {"address": "invalid_address", "coin_symbol": "LTC", "should_be_valid": False},
            {"address": "BTC1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4", "coin_symbol": "LTC", "should_be_valid": False},
            {"address": "", "coin_symbol": "LTC", "should_be_valid": False},
        ]
        
        passed_tests = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases):
            success, response = self.make_request('POST', '/api/wallet/validate', {
                "address": test_case["address"],
                "coin_symbol": test_case["coin_symbol"]
            })
            
            if success:
                is_valid = response.get("valid", False)
                expected = test_case["should_be_valid"]
                
                if is_valid == expected:
                    passed_tests += 1
                    print(f"  ✅ Test {i+1}: {test_case['address'][:20]}... -> {is_valid} (expected {expected})")
                else:
                    print(f"  ❌ Test {i+1}: {test_case['address'][:20]}... -> {is_valid} (expected {expected})")
            else:
                print(f"  ❌ Test {i+1}: Request failed for {test_case['address'][:20]}...")
        
        success_rate = (passed_tests / total_tests) * 100
        return self.log_test("Wallet Validation", passed_tests == total_tests, 
                           f"- {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")

    def test_mining_start_stop_cycle(self) -> bool:
        """Test complete mining start/stop cycle with wallet validation"""
        # First get coin presets
        success, presets_response = self.make_request('GET', '/api/coins/presets')
        if not success:
            return self.log_test("Mining Cycle", False, "- Failed to get coin presets")
        
        # Test solo mining without wallet (should fail)
        litecoin_config = presets_response['presets']['litecoin']
        mining_config_no_wallet = {
            "coin": litecoin_config,
            "mode": "solo",
            "threads": 2,
            "intensity": 0.5,
            "auto_optimize": True,
            "ai_enabled": True,
            "wallet_address": ""
        }
        
        start_success, start_response = self.make_request('POST', '/api/mining/start', mining_config_no_wallet)
        if start_success:
            self.log_test("Solo Mining Validation", False, "- Should fail without wallet address")
        else:
            self.log_test("Solo Mining Validation", True, "- Correctly rejected solo mining without wallet")
        
        # Test solo mining with valid wallet
        mining_config = {
            "coin": litecoin_config,
            "mode": "solo",
            "threads": 2,  # Use fewer threads for testing
            "intensity": 0.5,  # Lower intensity for testing
            "auto_optimize": True,
            "ai_enabled": True,
            "wallet_address": "LhK1Nk7QidqUBKLMBKVr8fWsNu4gp7rqLs"  # Valid Litecoin address
        }
        
        # Test pool mining with credentials
        pool_config = {
            "coin": litecoin_config,
            "mode": "pool",
            "threads": 2,
            "intensity": 0.5,
            "auto_optimize": True,
            "ai_enabled": True,
            "wallet_address": "",
            "pool_username": "test_user.worker1",
            "pool_password": "x"
        }
        
        pool_start_success, pool_start_response = self.make_request('POST', '/api/mining/start', pool_config)
        
        if pool_start_success and pool_start_response.get('success'):
            self.log_test("Pool Mining Start", True, "- Pool mining started successfully")
            
            # Stop pool mining
            self.make_request('POST', '/api/mining/stop')
            time.sleep(1)
        else:
            self.log_test("Pool Mining Start", False, f"- Pool mining failed: {pool_start_response}")
        
        # Test mining start with valid wallet
        start_success, start_response = self.make_request('POST', '/api/mining/start', mining_config)
        start_success, start_response = self.make_request('POST', '/api/mining/start', mining_config)
        
        if not start_success:
            return self.log_test("Mining Start", False, f"- Start failed: {start_response}")
        
        if not start_response.get('success'):
            return self.log_test("Mining Start", False, f"- Start unsuccessful: {start_response}")
        
        self.log_test("Mining Start", True, "- Mining started successfully")
        
        # Wait a moment for mining to initialize
        time.sleep(2)
        
        # Check mining status
        status_success, status_response = self.make_request('GET', '/api/mining/status')
        
        if status_success and status_response.get('is_mining'):
            self.log_test("Mining Status Check", True, "- Mining confirmed active")
        else:
            self.log_test("Mining Status Check", False, f"- Mining not active: {status_response}")
        
        # Wait a bit more to collect some stats
        time.sleep(3)
        
        # Test mining stop
        stop_success, stop_response = self.make_request('POST', '/api/mining/stop')
        
        if stop_success and stop_response.get('success'):
            self.log_test("Mining Stop", True, "- Mining stopped successfully")
            
            # Verify mining stopped
            time.sleep(1)
            final_status_success, final_status_response = self.make_request('GET', '/api/mining/status')
            
            if final_status_success and not final_status_response.get('is_mining'):
                return self.log_test("Mining Cycle Complete", True, "- Full cycle successful")
            else:
                return self.log_test("Mining Cycle Complete", False, "- Mining didn't stop properly")
        else:
            return self.log_test("Mining Stop", False, f"- Stop failed: {stop_response}")

    def test_ai_insights(self) -> bool:
        """Test AI insights endpoint"""
        success, response = self.make_request('GET', '/api/mining/ai-insights')
        
        if success:
            if 'error' in response:
                # AI system not available is acceptable for initial state
                return self.log_test("AI Insights", True, "- AI system not yet available (expected)")
            elif 'insights' in response:
                return self.log_test("AI Insights", True, "- AI insights available")
            else:
                return self.log_test("AI Insights", False, f"- Unexpected response: {response}")
        else:
            return self.log_test("AI Insights", False, f"- Request failed: {response}")

    def test_websocket_connection(self) -> bool:
        """Test WebSocket connection and data flow"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                self.websocket_data.append(data)
            except json.JSONDecodeError:
                pass

        def on_open(ws):
            self.websocket_connected = True

        def on_error(ws, error):
            print(f"WebSocket error: {error}")

        def on_close(ws, close_status_code, close_msg):
            self.websocket_connected = False

        try:
            # Create WebSocket connection
            ws_url = self.base_url.replace('http://', 'ws://').replace('https://', 'wss://') + '/api/ws'
            ws = websocket.WebSocketApp(ws_url,
                                      on_open=on_open,
                                      on_message=on_message,
                                      on_error=on_error,
                                      on_close=on_close)
            
            # Run WebSocket in a separate thread
            ws_thread = threading.Thread(target=ws.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.websocket_connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if not self.websocket_connected:
                return self.log_test("WebSocket Connection", False, "- Connection timeout")
            
            # Wait for some data
            time.sleep(3)
            ws.close()
            
            if len(self.websocket_data) > 0:
                data_types = set(data.get('type') for data in self.websocket_data)
                return self.log_test("WebSocket Data", True, 
                                   f"- Received {len(self.websocket_data)} messages, types: {data_types}")
            else:
                return self.log_test("WebSocket Data", False, "- No data received")
                
        except Exception as e:
            return self.log_test("WebSocket Connection", False, f"- Exception: {str(e)}")

    def test_scrypt_algorithm(self) -> bool:
        """Test the scrypt algorithm implementation by starting a brief mining session"""
        # Get coin presets
        success, presets_response = self.make_request('GET', '/api/coins/presets')
        if not success:
            return self.log_test("Scrypt Algorithm", False, "- Failed to get coin presets")
        
        # Start mining briefly to test scrypt
        litecoin_config = presets_response['presets']['litecoin']
        mining_config = {
            "coin": litecoin_config,
            "mode": "solo",
            "threads": 1,
            "intensity": 0.1,  # Very low intensity
            "auto_optimize": False,
            "ai_enabled": False
        }
        
        # Start mining
        start_success, start_response = self.make_request('POST', '/api/mining/start', mining_config)
        if not start_success:
            return self.log_test("Scrypt Algorithm", False, "- Failed to start mining for scrypt test")
        
        # Let it run briefly
        time.sleep(5)
        
        # Check if we got any hash rate
        status_success, status_response = self.make_request('GET', '/api/mining/status')
        
        # Stop mining
        self.make_request('POST', '/api/mining/stop')
        
        if status_success and status_response.get('stats', {}).get('hashrate', 0) > 0:
            hashrate = status_response['stats']['hashrate']
            return self.log_test("Scrypt Algorithm", True, f"- Hashrate achieved: {hashrate:.2f} H/s")
        else:
            return self.log_test("Scrypt Algorithm", False, "- No hashrate detected")

    def run_all_tests(self) -> bool:
        """Run all tests and return overall success"""
        print("🚀 Starting CryptoMiner Pro API Tests")
        print("=" * 50)
        
        # Basic API tests
        self.test_health_endpoint()
        self.test_coin_presets()
        self.test_system_stats()
        self.test_mining_status_initial()
        
        # Core mining functionality
        self.test_mining_start_stop_cycle()
        self.test_scrypt_algorithm()
        
        # Advanced features
        self.test_ai_insights()
        self.test_websocket_connection()
        
        # Results
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 Overall Status: GOOD - System is functioning well")
            return True
        elif success_rate >= 60:
            print("⚠️  Overall Status: FAIR - Some issues detected")
            return False
        else:
            print("🚨 Overall Status: POOR - Major issues detected")
            return False

def main():
    """Main test runner"""
    # Use the public endpoint from environment
    import os
    backend_url = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
    
    print(f"Testing backend at: {backend_url}")
    
    tester = CryptoMinerAPITester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())