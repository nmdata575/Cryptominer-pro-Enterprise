#!/usr/bin/env python3
"""
CryptoMiner Pro - Comprehensive Backend Testing
Tests all consolidated modules and API endpoints
"""

import requests
import json
import time
import sys
import os
from typing import Dict, Any, List

# Add backend to path for imports
sys.path.append('/app/backend')

# Test configuration
BACKEND_URL = "https://d7fc330d-17f6-47e5-a2b9-090776354317.preview.emergentagent.com/api"
TEST_WALLET_LTC = "ltc1qqvz2zw9hqd804a03xg95m4594p7v7thk25sztl"
TEST_POOL_ADDRESS = "ltc.luckymonster.pro"
TEST_POOL_PORT = 4112

class CryptoMinerTester:
    def __init__(self):
        self.results = {}
        self.session = requests.Session()
        self.session.timeout = 30
        
    def log_test(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test results"""
        self.results[test_name] = {
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": time.time()
        }
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   Details: {json.dumps(details, indent=2)}")
        print()

    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify required fields
                required_fields = ["status", "timestamp", "version", "ai_system", "mining_active"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Health Check API", False, f"Missing fields: {missing_fields}", data)
                    return False
                
                if data["status"] == "healthy":
                    self.log_test("Health Check API", True, "Health check passed", data)
                    return True
                else:
                    self.log_test("Health Check API", False, f"Unhealthy status: {data['status']}", data)
                    return False
            else:
                self.log_test("Health Check API", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Health Check API", False, f"Request failed: {str(e)}")
            return False

    def test_mining_status(self):
        """Test mining status endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/mining/status")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify structure
                required_fields = ["is_mining", "stats", "config"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Mining Status API", False, f"Missing fields: {missing_fields}", data)
                    return False
                
                # Verify stats structure
                stats = data.get("stats", {})
                expected_stats = ["hashrate", "accepted_shares", "rejected_shares", "blocks_found", "uptime"]
                
                self.log_test("Mining Status API", True, "Mining status retrieved successfully", data)
                return True
            else:
                self.log_test("Mining Status API", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Mining Status API", False, f"Request failed: {str(e)}")
            return False

    def test_coin_presets(self):
        """Test coin presets endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/coins/presets")
            
            if response.status_code == 200:
                data = response.json()
                
                if "presets" not in data:
                    self.log_test("Coin Presets API", False, "Missing 'presets' field", data)
                    return False
                
                presets = data["presets"]
                expected_coins = ["litecoin", "dogecoin", "feathercoin"]
                
                # Verify all expected coins are present
                missing_coins = [coin for coin in expected_coins if coin not in presets]
                if missing_coins:
                    self.log_test("Coin Presets API", False, f"Missing coins: {missing_coins}", presets)
                    return False
                
                # Verify coin structure
                for coin_name, coin_data in presets.items():
                    required_fields = ["name", "symbol", "algorithm", "block_reward", "scrypt_params"]
                    missing_fields = [field for field in required_fields if field not in coin_data]
                    
                    if missing_fields:
                        self.log_test("Coin Presets API", False, f"Missing fields in {coin_name}: {missing_fields}", coin_data)
                        return False
                
                self.log_test("Coin Presets API", True, f"All {len(presets)} coin presets loaded successfully", 
                            {"coins": list(presets.keys())})
                return True
            else:
                self.log_test("Coin Presets API", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Coin Presets API", False, f"Request failed: {str(e)}")
            return False

    def test_wallet_validation(self):
        """Test wallet validation endpoint"""
        try:
            # Test valid Litecoin address
            test_data = {
                "address": TEST_WALLET_LTC,
                "coin_symbol": "LTC"
            }
            
            response = self.session.post(f"{BACKEND_URL}/validate_wallet", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["valid", "message", "format"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Wallet Validation API", False, f"Missing fields: {missing_fields}", data)
                    return False
                
                if data["valid"]:
                    self.log_test("Wallet Validation API", True, "Wallet validation working correctly", data)
                    
                    # Test invalid address
                    invalid_test = {
                        "address": "invalid_address_123",
                        "coin_symbol": "LTC"
                    }
                    
                    invalid_response = self.session.post(f"{BACKEND_URL}/validate_wallet", json=invalid_test)
                    if invalid_response.status_code == 200:
                        invalid_data = invalid_response.json()
                        if not invalid_data.get("valid", True):
                            self.log_test("Wallet Validation API - Invalid Test", True, "Invalid address correctly rejected", invalid_data)
                            return True
                        else:
                            self.log_test("Wallet Validation API - Invalid Test", False, "Invalid address incorrectly accepted", invalid_data)
                            return False
                    
                    return True
                else:
                    self.log_test("Wallet Validation API", False, f"Valid address rejected: {data['message']}", data)
                    return False
            else:
                self.log_test("Wallet Validation API", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Wallet Validation API", False, f"Request failed: {str(e)}")
            return False

    def test_ai_system(self):
        """Test AI system endpoints"""
        try:
            # Test AI status
            response = self.session.get(f"{BACKEND_URL}/ai/status")
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["is_active", "learning_progress", "data_points_collected"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("AI System Status", False, f"Missing fields: {missing_fields}", data)
                    return False
                
                self.log_test("AI System Status", True, "AI system status retrieved", data)
                
                # Test AI insights
                insights_response = self.session.get(f"{BACKEND_URL}/mining/ai-insights")
                
                if insights_response.status_code == 200:
                    insights_data = insights_response.json()
                    
                    if "insights" in insights_data:
                        insights = insights_data["insights"]
                        expected_insights = ["hash_pattern_prediction", "network_difficulty_forecast", 
                                           "optimization_suggestions", "pool_performance_analysis"]
                        
                        missing_insights = [insight for insight in expected_insights if insight not in insights]
                        if missing_insights:
                            self.log_test("AI Insights API", False, f"Missing insights: {missing_insights}", insights)
                            return False
                        
                        self.log_test("AI Insights API", True, "AI insights working correctly", insights_data)
                        return True
                    else:
                        self.log_test("AI Insights API", False, "Missing 'insights' field", insights_data)
                        return False
                else:
                    self.log_test("AI Insights API", False, f"HTTP {insights_response.status_code}: {insights_response.text}")
                    return False
            else:
                self.log_test("AI System Status", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("AI System Integration", False, f"Request failed: {str(e)}")
            return False

    def test_system_stats(self):
        """Test system statistics endpoints"""
        try:
            # Test system stats
            response = self.session.get(f"{BACKEND_URL}/system/stats")
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["cpu_usage", "memory_usage", "disk_usage", "uptime", "cores"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("System Stats API", False, f"Missing fields: {missing_fields}", data)
                    return False
                
                self.log_test("System Stats API", True, "System stats retrieved successfully", data)
                
                # Test CPU info
                cpu_response = self.session.get(f"{BACKEND_URL}/system/cpu-info")
                
                if cpu_response.status_code == 200:
                    cpu_data = cpu_response.json()
                    
                    cpu_required = ["total_cores", "physical_cores", "thread_profiles", "recommended_threads"]
                    cpu_missing = [field for field in cpu_required if field not in cpu_data]
                    
                    if cpu_missing:
                        self.log_test("CPU Info API", False, f"Missing CPU fields: {cpu_missing}", cpu_data)
                        return False
                    
                    self.log_test("CPU Info API", True, "CPU info retrieved successfully", cpu_data)
                    return True
                else:
                    self.log_test("CPU Info API", False, f"HTTP {cpu_response.status_code}: {cpu_response.text}")
                    return False
            else:
                self.log_test("System Stats API", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("System Stats API", False, f"Request failed: {str(e)}")
            return False

    def test_pool_connection(self):
        """Test pool connection testing"""
        try:
            test_data = {
                "pool_address": TEST_POOL_ADDRESS,
                "pool_port": TEST_POOL_PORT,
                "type": "pool"
            }
            
            response = self.session.post(f"{BACKEND_URL}/pool/test-connection", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["success", "pool_address", "pool_port"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Pool Connection Testing", False, f"Missing fields: {missing_fields}", data)
                    return False
                
                # Connection success/failure is acceptable - we're testing the API works
                self.log_test("Pool Connection Testing", True, f"Pool connection test completed: {data.get('status', 'tested')}", data)
                return True
            else:
                self.log_test("Pool Connection Testing", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Pool Connection Testing", False, f"Request failed: {str(e)}")
            return False

    def test_mining_operations(self):
        """Test mining start/stop operations"""
        try:
            # Get coin presets first
            presets_response = self.session.get(f"{BACKEND_URL}/coins/presets")
            if presets_response.status_code != 200:
                self.log_test("Mining Operations", False, "Could not get coin presets for mining test")
                return False
            
            presets = presets_response.json()["presets"]
            ltc_config = presets["litecoin"]
            
            # Test mining start
            mining_config = {
                "coin": ltc_config,
                "mode": "solo",
                "threads": 1,
                "intensity": 0.5,
                "auto_optimize": True,
                "ai_enabled": True,
                "wallet_address": TEST_WALLET_LTC,
                "auto_thread_detection": True,
                "thread_profile": "light"
            }
            
            start_response = self.session.post(f"{BACKEND_URL}/mining/start", json=mining_config)
            
            if start_response.status_code == 200:
                start_data = start_response.json()
                
                if start_data.get("success"):
                    self.log_test("Mining Start API", True, "Mining started successfully", start_data)
                    
                    # Wait a moment then test stop
                    time.sleep(2)
                    
                    stop_response = self.session.post(f"{BACKEND_URL}/mining/stop")
                    
                    if stop_response.status_code == 200:
                        stop_data = stop_response.json()
                        
                        if stop_data.get("success"):
                            self.log_test("Mining Stop API", True, "Mining stopped successfully", stop_data)
                            return True
                        else:
                            self.log_test("Mining Stop API", False, f"Stop failed: {stop_data.get('message')}", stop_data)
                            return False
                    else:
                        self.log_test("Mining Stop API", False, f"HTTP {stop_response.status_code}: {stop_response.text}")
                        return False
                else:
                    self.log_test("Mining Start API", False, f"Start failed: {start_data.get('message')}", start_data)
                    return False
            else:
                self.log_test("Mining Start API", False, f"HTTP {start_response.status_code}: {start_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Mining Operations", False, f"Request failed: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting CryptoMiner Pro Backend Tests")
        print(f"🔗 Testing against: {BACKEND_URL}")
        print("=" * 60)
        
        # Test order based on dependencies
        tests = [
            ("Health Check", self.test_health_check),
            ("Mining Status", self.test_mining_status),
            ("Coin Presets", self.test_coin_presets),
            ("Wallet Validation", self.test_wallet_validation),
            ("AI System", self.test_ai_system),
            ("System Stats", self.test_system_stats),
            ("Pool Connection", self.test_pool_connection),
            ("Mining Operations", self.test_mining_operations),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"🧪 Running {test_name} test...")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test execution failed: {str(e)}")
            
            time.sleep(1)  # Brief pause between tests
        
        print("=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! CryptoMiner Pro backend is working correctly.")
        else:
            print(f"⚠️  {total - passed} tests failed. Check the details above.")
        
        return passed, total, self.results

def main():
    """Main test execution"""
    tester = CryptoMinerTester()
    passed, total, results = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            "summary": {
                "passed": passed,
                "total": total,
                "success_rate": (passed / total) * 100 if total > 0 else 0
            },
            "detailed_results": results,
            "test_timestamp": time.time()
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/backend_test_results.json")
    
    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()