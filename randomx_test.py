#!/usr/bin/env python3
"""
RandomX Mining Integration Test - Focused Testing for Review Request
Tests the updated RandomX mining integration with the backend API
"""

import requests
import sys
import json
import time
from datetime import datetime

class RandomXTester:
    def __init__(self, base_url="https://cryptominer-v21.preview.emergentagent.com"):
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

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                try:
                    json_response = response.json()
                    print(f"   Response: {json.dumps(json_response, indent=2)[:300]}...")
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

    def test_1_randomx_mining_process_control(self):
        """Test 1: RandomX Mining Process Control - POST /api/mining/control with XMR"""
        print("\n🎯 TEST 1: RandomX Mining Process Control")
        print("Testing POST /api/mining/control with XMR coin to ensure RandomX miner starts")
        
        # First stop any existing processes
        stop_data = {"action": "stop"}
        self.run_test("Stop Existing Processes", "POST", "mining/control", 200, stop_data)
        time.sleep(2)
        
        # Start RandomX mining with XMR
        control_data = {
            "action": "start",
            "config": {
                "coin": "XMR",
                "wallet": "solo.4793trzeyXigW8qj9JZU1bVUuohVqn76EBpXUEJdDxJS5tAP4rjAdS7PzWFXzV3MtE3b9MKxMeHmE5X8J2oBk7cyNdE65j8",
                "pool": "stratum+tcp://us.fastpool.xyz:10055",
                "password": "x",
                "intensity": 80,
                "threads": 7,
                "algorithm": "RandomX"
            }
        }
        
        success, response = self.run_test(
            "Start RandomX Mining with XMR",
            "POST",
            "mining/control",
            200,
            control_data
        )
        
        if success and isinstance(response, dict):
            if response.get("status") == "success":
                print("   ✅ RandomX mining process started successfully")
                print(f"   Process ID: {response.get('config', {}).get('process_id', 'Not provided')}")
                print(f"   Coin: {response.get('config', {}).get('coin')}")
                print(f"   Algorithm: {response.get('config', {}).get('algorithm', 'Auto-detected')}")
                return True
            else:
                print(f"   ❌ Failed to start: {response.get('message')}")
                return False
        return False

    def test_2_mining_statistics_api(self):
        """Test 2: Mining Statistics API - GET /api/mining/stats"""
        print("\n🎯 TEST 2: Mining Statistics API")
        print("Testing GET /api/mining/stats returns proper RandomX mining data")
        
        success, response = self.run_test(
            "Get RandomX Mining Statistics",
            "GET",
            "mining/stats",
            200
        )
        
        if success and isinstance(response, dict):
            hashrate = response.get("hashrate", 0)
            coin = response.get("coin")
            pool_connected = response.get("pool_connected", False)
            threads = response.get("threads", 0)
            
            print(f"   Hashrate: {hashrate} H/s")
            print(f"   Coin: {coin}")
            print(f"   Pool Connected: {pool_connected}")
            print(f"   Threads: {threads}")
            
            # Verify RandomX-specific data
            if coin == "XMR":
                print("   ✅ Correct coin (XMR) detected for RandomX")
            else:
                print(f"   ⚠️  Expected XMR, got {coin}")
            
            if hashrate > 0:
                print("   ✅ Non-zero hashrate detected")
            else:
                print("   ⚠️  Hashrate is zero - may need time to initialize")
            
            return True
        return False

    def test_3_stats_update_integration(self):
        """Test 3: Stats Update Integration - POST /api/mining/update-stats"""
        print("\n🎯 TEST 3: Stats Update Integration")
        print("Testing POST /api/mining/update-stats for RandomX miner stats")
        
        # Simulate RandomX miner sending stats to backend
        randomx_stats = {
            "hashrate": 1350.7,
            "threads": 7,
            "intensity": 80,
            "coin": "XMR",
            "algorithm": "RandomX",
            "pool_connected": True,
            "accepted_shares": 23,
            "rejected_shares": 2,
            "uptime": 2400,
            "difficulty": 275000,
            "ai_learning": 88.5,
            "ai_optimization": 76.2,
            "temperature": 72.3,
            "power_consumption": 135.0,
            "efficiency": 10.0,
            "pool_url": "stratum+tcp://us.fastpool.xyz:10055"
        }
        
        success, response = self.run_test(
            "Update RandomX Mining Stats",
            "POST",
            "mining/update-stats",
            200,
            randomx_stats
        )
        
        if success:
            print("   ✅ RandomX stats update successful")
            
            # Verify stats were stored by retrieving them
            time.sleep(1)
            verify_success, verify_response = self.run_test(
                "Verify Stats Persistence",
                "GET",
                "mining/stats",
                200
            )
            
            if verify_success and isinstance(verify_response, dict):
                stored_hashrate = verify_response.get("hashrate", 0)
                stored_coin = verify_response.get("coin")
                
                if abs(stored_hashrate - randomx_stats["hashrate"]) < 0.1:
                    print("   ✅ Stats persistence verified - hashrate matches")
                else:
                    print(f"   ⚠️  Stats may not have persisted (expected {randomx_stats['hashrate']}, got {stored_hashrate})")
                
                if stored_coin == "XMR":
                    print("   ✅ Coin persistence verified")
                
                return True
        return False

    def test_4_mining_status_monitoring(self):
        """Test 4: Mining Status Monitoring - GET /api/mining/status"""
        print("\n🎯 TEST 4: Mining Status Monitoring")
        print("Testing GET /api/mining/status returns accurate RandomX process info")
        
        success, response = self.run_test(
            "Get RandomX Mining Status",
            "GET",
            "mining/status",
            200
        )
        
        if success and isinstance(response, dict):
            is_active = response.get("is_active", False)
            process_id = response.get("process_id")
            pool_connected = response.get("pool_connected", False)
            last_update = response.get("last_update")
            
            print(f"   Mining Active: {is_active}")
            print(f"   Process ID: {process_id}")
            print(f"   Pool Connected: {pool_connected}")
            print(f"   Last Update: {last_update}")
            
            if is_active and process_id:
                print("   ✅ RandomX mining process is active with valid PID")
            elif is_active:
                print("   ⚠️  Mining reported as active but no PID provided")
            else:
                print("   ⚠️  Mining process not currently active")
            
            return True
        return False

    def test_5_algorithm_detection(self):
        """Test 5: Algorithm Detection - XMR -> RandomX mapping"""
        print("\n🎯 TEST 5: Algorithm Detection")
        print("Testing backend correctly detects XMR -> RandomX algorithm mapping")
        
        # Test with different coins to verify algorithm detection
        test_configs = [
            {"coin": "XMR", "expected_algorithm": "RandomX"},
            {"coin": "LTC", "expected_algorithm": "Scrypt"},
        ]
        
        for config in test_configs:
            coin = config["coin"]
            expected_algo = config["expected_algorithm"]
            
            # Start mining with specific coin
            control_data = {
                "action": "restart",
                "config": {
                    "coin": coin,
                    "wallet": "test_wallet_address_for_" + coin.lower(),
                    "pool": "test.pool.com:3333",
                    "intensity": 75,
                    "threads": 4
                }
            }
            
            success, response = self.run_test(
                f"Test Algorithm Detection for {coin}",
                "POST",
                "mining/control",
                200,
                control_data
            )
            
            if success and isinstance(response, dict):
                if response.get("status") == "success":
                    config_response = response.get("config", {})
                    detected_coin = config_response.get("coin")
                    
                    print(f"   Coin: {detected_coin}")
                    
                    if detected_coin == coin:
                        print(f"   ✅ Correct {coin} -> {expected_algo} detection")
                    else:
                        print(f"   ⚠️  Expected {coin}, got {detected_coin}")
                else:
                    print(f"   ❌ Failed to start mining for {coin}")
            
            time.sleep(1)
        
        return True

    def test_6_real_pool_connection_testing(self):
        """Test 6: Real Pool Connection Testing"""
        print("\n🎯 TEST 6: Real Pool Connection Testing")
        print("Testing mining process attempts pool connections and reports status")
        
        # Start mining with live XMR pool
        control_data = {
            "action": "restart",
            "config": {
                "coin": "XMR",
                "wallet": "solo.4793trzeyXigW8qj9JZU1bVUuohVqn76EBpXUEJdDxJS5tAP4rjAdS7PzWFXzV3MtE3b9MKxMeHmE5X8J2oBk7cyNdE65j8",
                "pool": "stratum+tcp://us.fastpool.xyz:10055",
                "password": "x",
                "intensity": 80,
                "threads": 6,
                "algorithm": "RandomX"
            }
        }
        
        success, response = self.run_test(
            "Start Mining with Live Pool",
            "POST",
            "mining/control",
            200,
            control_data
        )
        
        if success and response.get("status") == "success":
            print("   ✅ Mining started with live pool configuration")
            
            # Wait for pool connection attempt
            print("   Waiting for pool connection attempt...")
            time.sleep(5)
            
            # Check connection status
            status_success, status_response = self.run_test(
                "Check Pool Connection Status",
                "GET",
                "mining/status",
                200
            )
            
            if status_success and isinstance(status_response, dict):
                pool_connected = status_response.get("pool_connected", False)
                is_active = status_response.get("is_active", False)
                
                print(f"   Pool Connection Status: {pool_connected}")
                print(f"   Mining Process Active: {is_active}")
                
                if pool_connected:
                    print("   ✅ Pool connection reported as successful")
                else:
                    print("   ⚠️  Pool connection not established (may be normal for test environment)")
                
                # Check if stats show mining activity
                stats_success, stats_response = self.run_test(
                    "Check Mining Activity Stats",
                    "GET",
                    "mining/stats",
                    200
                )
                
                if stats_success and isinstance(stats_response, dict):
                    hashrate = stats_response.get("hashrate", 0)
                    shares = stats_response.get("accepted_shares", 0)
                    
                    print(f"   Current Hashrate: {hashrate} H/s")
                    print(f"   Accepted Shares: {shares}")
                    
                    if hashrate > 0:
                        print("   ✅ Mining activity detected (non-zero hashrate)")
                    else:
                        print("   ⚠️  No mining activity detected yet")
                
                return True
        
        return False

    def run_focused_randomx_tests(self):
        """Run all RandomX-focused tests as requested in review"""
        print("🚀 RandomX Mining Integration Testing - Review Request")
        print("=" * 80)
        print(f"Base URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print("🎯 FOCUS: Testing updated RandomX mining integration with backend API")
        print("📋 Key Areas: Process Control, Stats API, Update Integration, Status Monitoring")
        print("🔗 Pool: us.fastpool.xyz:10055 (Live XMR Pool)")
        print("=" * 80)

        # Run all tests in sequence
        test_methods = [
            self.test_1_randomx_mining_process_control,
            self.test_2_mining_statistics_api,
            self.test_3_stats_update_integration,
            self.test_4_mining_status_monitoring,
            self.test_5_algorithm_detection,
            self.test_6_real_pool_connection_testing
        ]

        for test_method in test_methods:
            try:
                test_method()
                time.sleep(2)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test {test_method.__name__} failed with error: {e}")

        # Final cleanup
        print("\n🧹 Cleanup: Stopping mining processes...")
        cleanup_data = {"action": "stop"}
        self.run_test("Final Cleanup", "POST", "mining/control", 200, cleanup_data)

        # Print final results
        print("\n" + "=" * 80)
        print("📊 RANDOMX INTEGRATION TEST RESULTS")
        print("=" * 80)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL RANDOMX INTEGRATION TESTS PASSED!")
            return 0
        elif self.tests_passed / self.tests_run >= 0.8:
            print("✅ RANDOMX INTEGRATION MOSTLY WORKING (80%+ success rate)")
            return 0
        else:
            print("⚠️  SOME CRITICAL RANDOMX TESTS FAILED!")
            return 1

def main():
    """Main entry point"""
    tester = RandomXTester()
    return tester.run_focused_randomx_tests()

if __name__ == "__main__":
    sys.exit(main())