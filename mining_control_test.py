#!/usr/bin/env python3
"""
Focused Mining Control API Testing
Tests the specific mining control functionality requested
"""

import requests
import sys
import json
import time
from datetime import datetime

class MiningControlTester:
    def __init__(self, base_url="https://cryptominer-v21.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.session.timeout = 15

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                try:
                    json_response = response.json()
                    print(f"   Response: {json.dumps(json_response, indent=2, default=str)[:300]}...")
                    return True, json_response
                except:
                    print(f"   Response: {response.text[:200]}...")
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_mining_status(self):
        """Test GET /api/mining/status"""
        return self.run_test("Mining Status", "GET", "mining/status", 200)

    def test_mining_stats(self):
        """Test GET /api/mining/stats"""
        return self.run_test("Mining Stats", "GET", "mining/stats", 200)

    def test_control_stop(self):
        """Test POST /api/mining/control with action stop"""
        data = {"action": "stop"}
        return self.run_test("Control - Stop", "POST", "mining/control", 200, data)

    def test_control_start(self):
        """Test POST /api/mining/control with action start"""
        data = {
            "action": "start",
            "config": {
                "coin": "LTC",
                "wallet": "LTC_TEST_WALLET_ADDRESS_123456789",
                "pool": "ltc.luckymonster.pro:4112",
                "intensity": 75,
                "threads": 4,
                "password": "x"
            }
        }
        return self.run_test("Control - Start", "POST", "mining/control", 200, data)

    def test_control_restart(self):
        """Test POST /api/mining/control with action restart"""
        data = {
            "action": "restart",
            "config": {
                "coin": "DOGE",
                "wallet": "DOGE_TEST_WALLET_ADDRESS_987654321",
                "pool": "doge.luckymonster.pro:4112",
                "intensity": 85,
                "threads": 6
            }
        }
        return self.run_test("Control - Restart", "POST", "mining/control", 200, data)

    def test_control_invalid(self):
        """Test POST /api/mining/control with invalid action"""
        data = {"action": "invalid_action"}
        return self.run_test("Control - Invalid Action", "POST", "mining/control", 200, data)

    def test_control_log(self):
        """Test GET /api/mining/control-log"""
        return self.run_test("Control Log", "GET", "mining/control-log", 200)

    def run_focused_tests(self):
        """Run focused mining control tests"""
        print("⚡ CryptoMiner Pro V30 - Mining Control API Testing")
        print("=" * 60)
        print(f"API URL: {self.api_url}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # Test sequence
        tests = [
            ("Initial Status Check", self.test_mining_status),
            ("Mining Stats", self.test_mining_stats),
            ("Stop Mining (Cleanup)", self.test_control_stop),
            ("Start Mining", self.test_control_start),
            ("Status After Start", self.test_mining_status),
            ("Restart Mining", self.test_control_restart),
            ("Status After Restart", self.test_mining_status),
            ("Stop Mining", self.test_control_stop),
            ("Status After Stop", self.test_mining_status),
            ("Invalid Action Test", self.test_control_invalid),
            ("Control Log", self.test_control_log)
        ]

        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 40)
            try:
                success, response = test_func()
                if success and isinstance(response, dict):
                    # Analyze specific responses
                    if "mining/status" in test_func.__name__:
                        is_active = response.get("is_active", False)
                        process_id = response.get("process_id")
                        pool_connected = response.get("pool_connected", False)
                        print(f"   📊 Active: {is_active}, PID: {process_id}, Pool: {pool_connected}")
                    
                    elif "control" in test_func.__name__:
                        status = response.get("status", "unknown")
                        message = response.get("message", "")
                        print(f"   📊 Status: {status}, Message: {message[:100]}")
                
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test failed: {e}")

        # Final results
        print("\n" + "=" * 60)
        print("📊 MINING CONTROL TEST RESULTS")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL MINING CONTROL TESTS PASSED!")
            return 0
        else:
            print("⚠️  SOME TESTS FAILED!")
            return 1

def main():
    """Main entry point"""
    tester = MiningControlTester()
    return tester.run_focused_tests()

if __name__ == "__main__":
    sys.exit(main())