#!/usr/bin/env python3
"""
CryptoMiner Pro V30 Backend API Testing
Comprehensive test suite for all API endpoints
"""

import requests
import sys
import json
import time
from datetime import datetime

class CryptoMinerAPITester:
    def __init__(self, base_url="https://cryptomine-central.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.session.timeout = 30

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                # Try to parse JSON response
                try:
                    json_response = response.json()
                    print(f"   Response: {json.dumps(json_response, indent=2)[:200]}...")
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

    def test_basic_api_health(self):
        """Test basic API health endpoint"""
        return self.run_test(
            "Basic API Health",
            "GET",
            "",
            200
        )

    def test_mining_stats(self):
        """Test mining statistics endpoint"""
        return self.run_test(
            "Mining Statistics",
            "GET",
            "mining/stats",
            200
        )

    def test_mining_config(self):
        """Test mining configuration endpoint"""
        return self.run_test(
            "Mining Configuration",
            "GET",
            "mining/config",
            200
        )

    def test_update_mining_config(self):
        """Test updating mining configuration"""
        config_data = {
            "coin": "LTC",
            "intensity": 75,
            "threads": 4
        }
        return self.run_test(
            "Update Mining Configuration",
            "POST",
            "mining/config",
            200,
            data=config_data
        )

    def test_available_coins(self):
        """Test available coins endpoint"""
        return self.run_test(
            "Available Coins",
            "GET",
            "mining/coins",
            200
        )

    def test_popular_pools(self):
        """Test popular pools endpoint"""
        return self.run_test(
            "Popular Mining Pools",
            "GET",
            "mining/pools",
            200
        )

    def test_system_info(self):
        """Test system information endpoint"""
        return self.run_test(
            "System Information",
            "GET",
            "system/info",
            200
        )

    def test_mining_history(self):
        """Test mining history endpoint"""
        return self.run_test(
            "Mining History",
            "GET",
            "mining/history",
            200
        )

    def test_update_mining_stats(self):
        """Test updating mining statistics"""
        stats_data = {
            "hashrate": 1500.5,
            "threads": 4,
            "intensity": 80,
            "coin": "LTC",
            "pool_connected": True,
            "accepted_shares": 10,
            "rejected_shares": 1,
            "uptime": 3600,
            "difficulty": 1024,
            "ai_learning": 75.5,
            "ai_optimization": 60.2
        }
        return self.run_test(
            "Update Mining Statistics",
            "POST",
            "mining/update-stats",
            200,
            data=stats_data
        )

    def test_status_endpoints(self):
        """Test status check endpoints"""
        # Create status check
        status_data = {
            "client_name": "CryptoMiner_Test_Client"
        }
        success, response = self.run_test(
            "Create Status Check",
            "POST",
            "status",
            200,
            data=status_data
        )
        
        if success:
            # Get status checks
            self.run_test(
                "Get Status Checks",
                "GET",
                "status",
                200
            )

    def test_mining_control_start(self):
        """Test mining control start functionality"""
        control_data = {
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
        return self.run_test(
            "Mining Control - Start",
            "POST",
            "mining/control",
            200,
            data=control_data
        )

    def test_mining_control_start_already_running(self):
        """Test starting mining when already running"""
        control_data = {
            "action": "start",
            "config": {
                "coin": "LTC",
                "wallet": "LTC_TEST_WALLET_ADDRESS_123456789",
                "pool": "ltc.luckymonster.pro:4112",
                "intensity": 80,
                "threads": 2
            }
        }
        # This should return an error if mining is already running
        success, response = self.run_test(
            "Mining Control - Start (Already Running)",
            "POST",
            "mining/control",
            200,
            data=control_data
        )
        
        # Check if response indicates error for already running
        if success and isinstance(response, dict):
            if response.get("status") == "error" and "already running" in response.get("message", "").lower():
                print("   ✅ Correctly detected mining already running")
            elif response.get("status") == "success":
                print("   ⚠️  Started new mining process (previous may have been stopped)")
        
        return success, response

    def test_mining_status(self):
        """Test mining status endpoint"""
        return self.run_test(
            "Mining Status",
            "GET",
            "mining/status",
            200
        )

    def test_mining_control_stop(self):
        """Test mining control stop functionality"""
        control_data = {
            "action": "stop"
        }
        return self.run_test(
            "Mining Control - Stop",
            "POST",
            "mining/control",
            200,
            data=control_data
        )

    def test_mining_control_stop_not_running(self):
        """Test stopping mining when not running"""
        control_data = {
            "action": "stop"
        }
        success, response = self.run_test(
            "Mining Control - Stop (Not Running)",
            "POST",
            "mining/control",
            200,
            data=control_data
        )
        
        # Check if response indicates error for not running
        if success and isinstance(response, dict):
            if response.get("status") == "error" and "not currently running" in response.get("message", "").lower():
                print("   ✅ Correctly detected mining not running")
            elif response.get("status") == "success":
                print("   ⚠️  Stopped mining processes (some may have been running)")
        
        return success, response

    def test_mining_control_restart(self):
        """Test mining control restart functionality"""
        control_data = {
            "action": "restart",
            "config": {
                "coin": "DOGE",
                "wallet": "DOGE_TEST_WALLET_ADDRESS_987654321",
                "pool": "doge.luckymonster.pro:4112",
                "intensity": 85,
                "threads": 6
            }
        }
        return self.run_test(
            "Mining Control - Restart",
            "POST",
            "mining/control",
            200,
            data=control_data
        )

    def test_mining_control_invalid_action(self):
        """Test mining control with invalid action"""
        control_data = {
            "action": "invalid_action"
        }
        success, response = self.run_test(
            "Mining Control - Invalid Action",
            "POST",
            "mining/control",
            200,
            data=control_data
        )
        
        # Check if response indicates error for invalid action
        if success and isinstance(response, dict):
            if response.get("status") == "error" and "unknown action" in response.get("message", "").lower():
                print("   ✅ Correctly rejected invalid action")
            else:
                print("   ⚠️  Unexpected response for invalid action")
        
        return success, response

    def test_mining_control_log(self):
        """Test mining control log endpoint"""
        return self.run_test(
            "Mining Control Log",
            "GET",
            "mining/control-log",
            200
        )

    def test_mining_process_management_sequence(self):
        """Test complete mining process management sequence"""
        print("\n🔄 Testing Complete Mining Process Management Sequence...")
        
        # 1. Check initial status
        print("   Step 1: Check initial mining status")
        success, status_response = self.test_mining_status()
        if success:
            initial_active = status_response.get("is_active", False)
            print(f"   Initial mining active: {initial_active}")
        
        # 2. Stop any existing mining (cleanup)
        print("   Step 2: Stop any existing mining processes")
        self.test_mining_control_stop()
        time.sleep(2)  # Wait for cleanup
        
        # 3. Start mining with custom config
        print("   Step 3: Start mining with custom configuration")
        success, start_response = self.test_mining_control_start()
        if success and start_response.get("status") == "success":
            print("   ✅ Mining started successfully")
            time.sleep(3)  # Wait for process to initialize
            
            # 4. Check status shows active
            print("   Step 4: Verify mining status shows active")
            success, status_response = self.test_mining_status()
            if success:
                is_active = status_response.get("is_active", False)
                process_id = status_response.get("process_id")
                print(f"   Mining active: {is_active}, PID: {process_id}")
                
                if is_active and process_id:
                    print("   ✅ Mining process is active with valid PID")
                else:
                    print("   ⚠️  Mining may not be fully active yet")
            
            # 5. Test restart with different config
            print("   Step 5: Restart mining with different configuration")
            success, restart_response = self.test_mining_control_restart()
            if success and restart_response.get("status") == "success":
                print("   ✅ Mining restarted successfully")
                time.sleep(2)  # Wait for restart
                
                # 6. Final status check
                print("   Step 6: Final status check after restart")
                success, final_status = self.test_mining_status()
                if success:
                    final_active = final_status.get("is_active", False)
                    final_pid = final_status.get("process_id")
                    print(f"   Final mining active: {final_active}, PID: {final_pid}")
            
            # 7. Stop mining (cleanup)
            print("   Step 7: Stop mining (cleanup)")
            self.test_mining_control_stop()
            time.sleep(2)  # Wait for cleanup
            
            # 8. Verify stopped
            print("   Step 8: Verify mining is stopped")
            success, stopped_status = self.test_mining_status()
            if success:
                stopped_active = stopped_status.get("is_active", False)
                print(f"   Mining active after stop: {stopped_active}")
                if not stopped_active:
                    print("   ✅ Mining successfully stopped")
                else:
                    print("   ⚠️  Mining may still be running")
        
        print("   🏁 Process management sequence completed")

    def run_comprehensive_test(self):
        """Run all API tests"""
        print("🚀 Starting CryptoMiner Pro V30 API Testing")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # Test all endpoints
        test_methods = [
            self.test_basic_api_health,
            self.test_mining_stats,
            self.test_mining_config,
            self.test_update_mining_config,
            self.test_available_coins,
            self.test_popular_pools,
            self.test_system_info,
            self.test_mining_history,
            self.test_update_mining_stats,
            self.test_status_endpoints
        ]

        for test_method in test_methods:
            try:
                test_method()
                time.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test method {test_method.__name__} failed: {e}")

        # Print final results
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED!")
            return 0
        else:
            print("⚠️  SOME TESTS FAILED!")
            return 1

def main():
    """Main entry point"""
    tester = CryptoMinerAPITester()
    return tester.run_comprehensive_test()

if __name__ == "__main__":
    sys.exit(main())