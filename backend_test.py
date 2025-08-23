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
    def __init__(self, base_url="https://ai-mining-hub.preview.emergentagent.com"):
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

    def test_multi_algorithm_stats(self):
        """Test multi-algorithm statistics endpoint"""
        success, response = self.run_test(
            "Multi-Algorithm Statistics",
            "GET",
            "mining/multi-stats",
            200
        )
        
        if success and isinstance(response, dict):
            # Verify required fields are present
            required_fields = [
                'current_algorithm', 'current_coin', 'is_mining', 'total_uptime',
                'current_stats', 'algorithm_comparison', 'ai_stats', 
                'supported_algorithms', 'supported_coins', 'auto_switching'
            ]
            
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                print(f"   ⚠️  Missing fields: {missing_fields}")
            else:
                print("   ✅ All required fields present")
                
            # Verify AI stats structure
            if 'ai_stats' in response:
                ai_stats = response['ai_stats']
                ai_required = ['learning_progress', 'optimization_progress', 'predictive_success_rate']
                ai_missing = [field for field in ai_required if field not in ai_stats]
                if ai_missing:
                    print(f"   ⚠️  Missing AI stats fields: {ai_missing}")
                else:
                    print("   ✅ AI statistics structure verified")
                    
            # Verify algorithm comparison
            if 'algorithm_comparison' in response:
                algorithms = response['algorithm_comparison']
                expected_algorithms = ['RandomX', 'Scrypt', 'CryptoNight']
                found_algorithms = [alg for alg in expected_algorithms if alg in algorithms]
                print(f"   ✅ Found algorithms: {found_algorithms}")
        
        return success, response

    def test_algorithm_switching_randomx(self):
        """Test switching to RandomX algorithm"""
        switch_data = {
            "algorithm": "RandomX",
            "coin": "XMR",
            "pool": "pool.supportxmr.com:3333",
            "threads": 8,
            "intensity": 80
        }
        success, response = self.run_test(
            "Algorithm Switch - RandomX",
            "POST",
            "mining/switch-algorithm",
            200,
            data=switch_data
        )
        
        if success and isinstance(response, dict):
            if response.get("status") == "success":
                print(f"   ✅ Successfully switched to {response.get('algorithm')} for {response.get('coin')}")
            else:
                print(f"   ⚠️  Switch response: {response.get('message', 'Unknown')}")
        
        return success, response

    def test_algorithm_switching_scrypt(self):
        """Test switching to Scrypt algorithm with LTC"""
        switch_data = {
            "algorithm": "Scrypt",
            "coin": "LTC",
            "pool": "ltc.luckymonster.pro:4112",
            "threads": 6,
            "intensity": 85
        }
        success, response = self.run_test(
            "Algorithm Switch - Scrypt (LTC)",
            "POST",
            "mining/switch-algorithm",
            200,
            data=switch_data
        )
        
        if success and isinstance(response, dict):
            if response.get("status") == "success":
                print(f"   ✅ Successfully switched to {response.get('algorithm')} for {response.get('coin')}")
            else:
                print(f"   ⚠️  Switch response: {response.get('message', 'Unknown')}")
        
        return success, response

    def test_algorithm_switching_cryptonight(self):
        """Test switching to CryptoNight algorithm"""
        switch_data = {
            "algorithm": "CryptoNight",
            "coin": "AEON",
            "pool": "aeon.luckymonster.pro:4112",
            "threads": 4,
            "intensity": 75
        }
        success, response = self.run_test(
            "Algorithm Switch - CryptoNight",
            "POST",
            "mining/switch-algorithm",
            200,
            data=switch_data
        )
        
        if success and isinstance(response, dict):
            if response.get("status") == "success":
                print(f"   ✅ Successfully switched to {response.get('algorithm')} for {response.get('coin')}")
            else:
                print(f"   ⚠️  Switch response: {response.get('message', 'Unknown')}")
        
        return success, response

    def test_algorithm_switching_invalid(self):
        """Test switching to invalid algorithm"""
        switch_data = {
            "algorithm": "InvalidAlgorithm",
            "coin": "INVALID",
            "pool": "invalid.pool.com:1234",
            "threads": 2,
            "intensity": 50
        }
        success, response = self.run_test(
            "Algorithm Switch - Invalid Algorithm",
            "POST",
            "mining/switch-algorithm",
            200,
            data=switch_data
        )
        
        # Note: The current implementation doesn't validate algorithms, so this might still succeed
        if success and isinstance(response, dict):
            print(f"   Response status: {response.get('status')}")
            print(f"   Response message: {response.get('message', 'No message')}")
        
        return success, response

    def test_ai_recommendation(self):
        """Test AI algorithm recommendation endpoint"""
        success, response = self.run_test(
            "AI Algorithm Recommendation",
            "GET",
            "mining/ai-recommendation",
            200
        )
        
        if success and isinstance(response, dict):
            # Verify required recommendation fields
            required_fields = ['algorithm', 'coin', 'hashrate', 'efficiency', 'confidence', 'reason']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"   ⚠️  Missing recommendation fields: {missing_fields}")
            else:
                print("   ✅ All recommendation fields present")
                print(f"   Recommended: {response.get('algorithm')} for {response.get('coin')}")
                print(f"   Confidence: {response.get('confidence')}%")
                print(f"   Reason: {response.get('reason', 'No reason provided')[:50]}...")
        
        return success, response

    def test_enhanced_mining_control_integration(self):
        """Test enhanced mining control with algorithm parameters"""
        control_data = {
            "action": "start",
            "config": {
                "coin": "XMR",
                "algorithm": "RandomX",
                "wallet": "XMR_TEST_WALLET_ADDRESS_123456789ABCDEF",
                "pool": "pool.supportxmr.com:3333",
                "intensity": 80,
                "threads": 6,
                "auto_switch": True
            }
        }
        success, response = self.run_test(
            "Enhanced Mining Control - Start with Algorithm",
            "POST",
            "mining/control",
            200,
            data=control_data
        )
        
        if success and isinstance(response, dict):
            if response.get("status") == "success":
                print("   ✅ Enhanced mining control with algorithm parameters working")
                config = response.get("config", {})
                print(f"   Started with: {config.get('algorithm', 'Unknown')} algorithm")
            else:
                print(f"   ⚠️  Enhanced control response: {response.get('message', 'Unknown')}")
        
        return success, response

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

    def test_randomx_mining_control_start(self):
        """Test RandomX mining control with live XMR configuration"""
        control_data = {
            "action": "start",
            "config": {
                "coin": "XMR",
                "wallet": "solo.4793trzeyXigW8qj9JZU1bVUuohVqn76EBpXUEJdDxJS5tAP4rjAdS7PzWFXzV3MtE3b9MKxMeHmE5X8J2oBk7cyNdE65j8",
                "pool": "stratum+tcp://us.fastpool.xyz:10055",
                "password": "x",
                "intensity": 80,
                "threads": "auto",
                "algorithm": "RandomX"
            }
        }
        success, response = self.run_test(
            "RandomX Mining Control - Start with Live XMR Config",
            "POST",
            "mining/control",
            200,
            data=control_data
        )
        
        if success and isinstance(response, dict):
            if response.get("status") == "success":
                print("   ✅ RandomX mining started with live XMR configuration")
                config = response.get("config", {})
                print(f"   Coin: {config.get('coin')}")
                print(f"   Pool: {config.get('pool')}")
                print(f"   Algorithm: {config.get('algorithm', 'Not specified')}")
            else:
                print(f"   ❌ RandomX mining start failed: {response.get('message', 'Unknown error')}")
        
        return success, response

    def test_randomx_stats_collection(self):
        """Test RandomX-specific mining stats collection"""
        success, response = self.run_test(
            "RandomX Stats Collection",
            "GET",
            "mining/stats",
            200
        )
        
        if success and isinstance(response, dict):
            # Check for RandomX-specific fields
            coin = response.get("coin")
            hashrate = response.get("hashrate", 0)
            pool_connected = response.get("pool_connected", False)
            
            print(f"   Current coin: {coin}")
            print(f"   Hashrate: {hashrate}")
            print(f"   Pool connected: {pool_connected}")
            
            if coin == "XMR":
                print("   ✅ RandomX (XMR) mining stats detected")
            else:
                print(f"   ⚠️  Expected XMR, got {coin}")
        
        return success, response

    def test_randomx_update_stats(self):
        """Test updating RandomX mining statistics"""
        randomx_stats = {
            "hashrate": 1200.5,
            "threads": 8,
            "intensity": 80,
            "coin": "XMR",
            "algorithm": "RandomX",
            "pool_connected": True,
            "accepted_shares": 15,
            "rejected_shares": 1,
            "uptime": 1800,
            "difficulty": 250000,
            "ai_learning": 85.2,
            "ai_optimization": 72.8,
            "temperature": 68.5,
            "power_consumption": 120.0,
            "efficiency": 10.0
        }
        success, response = self.run_test(
            "Update RandomX Mining Statistics",
            "POST",
            "mining/update-stats",
            200,
            data=randomx_stats
        )
        
        if success:
            print("   ✅ RandomX stats updated successfully")
            # Verify stats were stored
            time.sleep(1)
            stats_success, stats_response = self.test_randomx_stats_collection()
            if stats_success and isinstance(stats_response, dict):
                updated_hashrate = stats_response.get("hashrate", 0)
                if abs(updated_hashrate - randomx_stats["hashrate"]) < 0.1:
                    print("   ✅ RandomX stats persistence verified")
                else:
                    print(f"   ⚠️  Stats may not have persisted correctly")
        
        return success, response

    def test_randomx_process_management(self):
        """Test complete RandomX process management lifecycle"""
        print("\n🔄 Testing RandomX Process Management Lifecycle...")
        
        # 1. Stop any existing processes
        print("   Step 1: Clean up any existing mining processes")
        self.run_test("Stop Existing Processes", "POST", "mining/control", 200, {"action": "stop"})
        time.sleep(2)
        
        # 2. Start RandomX mining with live config
        print("   Step 2: Start RandomX mining with live XMR configuration")
        success, start_response = self.test_randomx_mining_control_start()
        
        if success and start_response.get("status") == "success":
            print("   ✅ RandomX mining process started")
            time.sleep(5)  # Wait for process initialization
            
            # 3. Check mining status
            print("   Step 3: Verify RandomX mining status")
            success, status_response = self.run_test("RandomX Mining Status", "GET", "mining/status", 200)
            if success:
                is_active = status_response.get("is_active", False)
                process_id = status_response.get("process_id")
                print(f"   Mining active: {is_active}, PID: {process_id}")
                
                if is_active and process_id:
                    print("   ✅ RandomX mining process is active")
                    
                    # 4. Test stats collection during mining
                    print("   Step 4: Test RandomX stats collection during active mining")
                    self.test_randomx_stats_collection()
                    
                    # 5. Test stats update
                    print("   Step 5: Test RandomX stats update")
                    self.test_randomx_update_stats()
                    
                    # 6. Test restart with different intensity
                    print("   Step 6: Test RandomX mining restart")
                    restart_config = {
                        "action": "restart",
                        "config": {
                            "coin": "XMR",
                            "wallet": "solo.4793trzeyXigW8qj9JZU1bVUuohVqn76EBpXUEJdDxJS5tAP4rjAdS7PzWFXzV3MtE3b9MKxMeHmE5X8J2oBk7cyNdE65j8",
                            "pool": "stratum+tcp://us.fastpool.xyz:10055",
                            "password": "x",
                            "intensity": 90,
                            "threads": 6,
                            "algorithm": "RandomX"
                        }
                    }
                    restart_success, restart_response = self.run_test(
                        "RandomX Mining Restart", "POST", "mining/control", 200, restart_config
                    )
                    
                    if restart_success and restart_response.get("status") == "success":
                        print("   ✅ RandomX mining restarted successfully")
                        time.sleep(3)
                    
                else:
                    print("   ⚠️  RandomX mining process may not be fully active")
            
            # 7. Final cleanup
            print("   Step 7: Stop RandomX mining (cleanup)")
            self.run_test("Stop RandomX Mining", "POST", "mining/control", 200, {"action": "stop"})
            time.sleep(2)
            
            # 8. Verify stopped
            print("   Step 8: Verify RandomX mining stopped")
            final_success, final_status = self.run_test("Final Status Check", "GET", "mining/status", 200)
            if final_success:
                final_active = final_status.get("is_active", False)
                if not final_active:
                    print("   ✅ RandomX mining successfully stopped")
                else:
                    print("   ⚠️  RandomX mining may still be running")
        
        print("   🏁 RandomX process management lifecycle completed")

    def test_ai_integration_with_randomx(self):
        """Test AI integration with RandomX mining data"""
        print("\n🧠 Testing AI Integration with RandomX Mining...")
        
        # Test AI recommendation for RandomX
        success, ai_response = self.run_test(
            "AI Recommendation for RandomX",
            "GET",
            "mining/ai-recommendation",
            200
        )
        
        if success and isinstance(ai_response, dict):
            recommended_algorithm = ai_response.get("algorithm")
            recommended_coin = ai_response.get("coin")
            confidence = ai_response.get("confidence", 0)
            
            print(f"   AI Recommended: {recommended_algorithm} for {recommended_coin}")
            print(f"   Confidence: {confidence}%")
            
            if recommended_algorithm == "RandomX" and recommended_coin == "XMR":
                print("   ✅ AI correctly recommends RandomX for XMR")
            else:
                print(f"   ⚠️  AI recommendation: {recommended_algorithm} for {recommended_coin}")
        
        # Test multi-algorithm stats with RandomX focus
        success, multi_stats = self.run_test(
            "Multi-Algorithm Stats with RandomX",
            "GET",
            "mining/multi-stats",
            200
        )
        
        if success and isinstance(multi_stats, dict):
            current_algorithm = multi_stats.get("current_algorithm")
            ai_stats = multi_stats.get("ai_stats", {})
            algorithm_comparison = multi_stats.get("algorithm_comparison", {})
            
            print(f"   Current algorithm: {current_algorithm}")
            
            if "RandomX" in algorithm_comparison:
                randomx_data = algorithm_comparison["RandomX"]
                print(f"   RandomX hashrate: {randomx_data.get('hashrate', 0)}")
                print(f"   RandomX efficiency: {randomx_data.get('efficiency', 0)}")
                print("   ✅ RandomX data found in algorithm comparison")
            
            if ai_stats:
                learning_progress = ai_stats.get("learning_progress", 0)
                optimization_progress = ai_stats.get("optimization_progress", 0)
                print(f"   AI Learning: {learning_progress}%")
                print(f"   AI Optimization: {optimization_progress}%")
                print("   ✅ AI stats integration working")

    def run_randomx_focused_test(self):
        """Run RandomX-focused testing for Phase 2"""
        print("🚀 Starting CryptoMiner V21 RandomX Integration Testing")
        print("=" * 70)
        print(f"Base URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print("🎯 FOCUS: RandomX (Monero) Mining Integration with Live Pool")
        print("📋 Configuration: XMR mining on us.fastpool.xyz:10055")
        print("=" * 70)

        # Test basic API health first
        print("\n📋 PHASE 1: Basic API Health Check")
        print("-" * 50)
        try:
            self.test_basic_api_health()
        except Exception as e:
            print(f"❌ Basic API health check failed: {e}")
            return 1

        # Test RandomX-specific functionality
        print("\n⚡ PHASE 2: RandomX Mining Control Integration")
        print("-" * 50)
        randomx_tests = [
            self.test_randomx_mining_control_start,
            self.test_randomx_stats_collection,
            self.test_randomx_update_stats,
        ]

        for test_method in randomx_tests:
            try:
                test_method()
                time.sleep(1)
            except Exception as e:
                print(f"❌ Test method {test_method.__name__} failed: {e}")

        # Test complete RandomX process management
        print("\n🔄 PHASE 3: RandomX Process Management Lifecycle")
        print("-" * 50)
        try:
            self.test_randomx_process_management()
        except Exception as e:
            print(f"❌ RandomX process management failed: {e}")

        # Test AI integration with RandomX
        print("\n🧠 PHASE 4: AI Integration with RandomX Mining")
        print("-" * 50)
        try:
            self.test_ai_integration_with_randomx()
        except Exception as e:
            print(f"❌ AI integration testing failed: {e}")

        # Print final results
        print("\n" + "=" * 70)
        print("📊 RANDOMX INTEGRATION TEST RESULTS")
        print("=" * 70)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL RANDOMX TESTS PASSED!")
            return 0
        else:
            print("⚠️  SOME RANDOMX TESTS FAILED!")
            return 1

    def run_comprehensive_test(self):
        """Run all API tests"""
        print("🚀 Starting CryptoMiner V21 API Testing")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # Test basic endpoints first
        basic_test_methods = [
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

        print("\n📋 PHASE 1: Basic API Endpoints Testing")
        print("-" * 50)
        for test_method in basic_test_methods:
            try:
                test_method()
                time.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test method {test_method.__name__} failed: {e}")

        # Test mining control functionality
        print("\n⚡ PHASE 2: Mining Control Functionality Testing")
        print("-" * 50)
        mining_control_tests = [
            self.test_mining_status,
            self.test_mining_control_stop_not_running,  # Ensure clean state
            self.test_mining_control_start,
            self.test_mining_control_start_already_running,
            self.test_mining_status,
            self.test_mining_control_restart,
            self.test_mining_status,
            self.test_mining_control_stop,
            self.test_mining_control_invalid_action,
            self.test_mining_control_log
        ]

        for test_method in mining_control_tests:
            try:
                test_method()
                time.sleep(1)  # Longer pause for process management tests
            except Exception as e:
                print(f"❌ Test method {test_method.__name__} failed: {e}")

        # Test complete process management sequence
        print("\n🔄 PHASE 3: Complete Process Management Sequence")
        print("-" * 50)
        try:
            self.test_mining_process_management_sequence()
        except Exception as e:
            print(f"❌ Process management sequence failed: {e}")

        # Test new multi-algorithm endpoints
        print("\n🧠 PHASE 4: Multi-Algorithm & AI Enhanced Features")
        print("-" * 50)
        multi_algorithm_tests = [
            self.test_multi_algorithm_stats,
            self.test_ai_recommendation,
            self.test_algorithm_switching_randomx,
            self.test_algorithm_switching_scrypt,
            self.test_algorithm_switching_cryptonight,
            self.test_algorithm_switching_invalid,
            self.test_enhanced_mining_control_integration
        ]

        for test_method in multi_algorithm_tests:
            try:
                test_method()
                time.sleep(1)  # Pause between algorithm tests
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