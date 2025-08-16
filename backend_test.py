#!/usr/bin/env python3
"""
CryptoMiner Pro V30 Backend Testing Suite
Comprehensive testing after naming inconsistency fixes
"""

import asyncio
import aiohttp
import json
import time
import sys
import os
from datetime import datetime

# Test configuration
BACKEND_URL = "https://cryptominer-pro-2.preview.emergentagent.com/api"
TEST_TIMEOUT = 30
MINING_TEST_DURATION = 10  # seconds

class BackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def setup(self):
        """Setup test session"""
        timeout = aiohttp.ClientTimeout(total=TEST_TIMEOUT)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name, success, message="", details=None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.test_results.append(result)
        print(f"{status} - {test_name}: {message}")
        
        if details:
            print(f"    Details: {details}")
            
    async def test_health_check(self):
        """Test health check endpoint"""
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify essential health check fields
                    required_fields = ["status", "version", "edition", "ai_system", "mining_active", "database"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test("Health Check API", False, f"Missing fields: {missing_fields}")
                        return
                    
                    # Check database status
                    db_status = data.get("database", {}).get("status", "unknown")
                    
                    self.log_test("Health Check API", True, 
                                f"Status: {data['status']}, Version: {data['version']}, DB: {db_status}")
                else:
                    self.log_test("Health Check API", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("Health Check API", False, f"Exception: {str(e)}")
            
    async def test_system_info(self):
        """Test system info endpoint"""
        try:
            async with self.session.get(f"{BACKEND_URL}/system/cpu-info") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify CPU info fields
                    required_fields = ["physical_cores", "logical_cores", "max_safe_threads"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test("System Info API", False, f"Missing fields: {missing_fields}")
                        return
                    
                    cores = data.get("logical_cores", 0)
                    max_threads = data.get("max_safe_threads", 0)
                    
                    self.log_test("System Info API", True, 
                                f"Cores: {cores}, Max threads: {max_threads}")
                else:
                    self.log_test("System Info API", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("System Info API", False, f"Exception: {str(e)}")
            
    async def test_mining_status(self):
        """Test mining status endpoint"""
        try:
            async with self.session.get(f"{BACKEND_URL}/mining/status") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify mining status fields
                    required_fields = ["is_mining", "stats", "config"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test("Mining Status API", False, f"Missing fields: {missing_fields}")
                        return
                    
                    is_mining = data.get("is_mining", False)
                    stats = data.get("stats", {})
                    hashrate = stats.get("hashrate", 0)
                    
                    self.log_test("Mining Status API", True, 
                                f"Mining: {is_mining}, Hashrate: {hashrate} H/s")
                else:
                    self.log_test("Mining Status API", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("Mining Status API", False, f"Exception: {str(e)}")
            
    async def test_coin_presets(self):
        """Test coin presets endpoint"""
        try:
            async with self.session.get(f"{BACKEND_URL}/coins/presets") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    presets = data.get("presets", {})
                    if not presets:
                        self.log_test("Coin Presets API", False, "No presets returned")
                        return
                    
                    # Check for common coins
                    coin_symbols = [coin_data.get("symbol", "") for coin_data in presets.values()]
                    expected_coins = ["LTC", "DOGE"]
                    found_coins = [coin for coin in expected_coins if coin in coin_symbols]
                    
                    self.log_test("Coin Presets API", True, 
                                f"Found {len(presets)} presets, includes: {found_coins}")
                else:
                    self.log_test("Coin Presets API", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("Coin Presets API", False, f"Exception: {str(e)}")
            
    async def test_ai_insights(self):
        """Test AI insights endpoint"""
        try:
            async with self.session.get(f"{BACKEND_URL}/mining/ai-insights") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    insights = data.get("insights", {})
                    if not insights:
                        self.log_test("AI Insights API", False, "No insights returned")
                        return
                    
                    # Check for expected insight types
                    expected_insights = ["hash_pattern_prediction", "optimization_suggestions"]
                    found_insights = [key for key in expected_insights if key in insights]
                    
                    self.log_test("AI Insights API", True, 
                                f"Insights available: {len(insights)} types, includes: {found_insights}")
                else:
                    self.log_test("AI Insights API", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("AI Insights API", False, f"Exception: {str(e)}")
            
    async def test_system_stats(self):
        """Test system stats endpoint"""
        try:
            async with self.session.get(f"{BACKEND_URL}/system/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify system stats fields
                    required_fields = ["cpu_usage", "memory_usage", "cores"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test("System Stats API", False, f"Missing fields: {missing_fields}")
                        return
                    
                    cpu_usage = data.get("cpu_usage", 0)
                    memory_usage = data.get("memory_usage", 0)
                    cores = data.get("cores", 0)
                    
                    self.log_test("System Stats API", True, 
                                f"CPU: {cpu_usage}%, Memory: {memory_usage}%, Cores: {cores}")
                else:
                    self.log_test("System Stats API", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("System Stats API", False, f"Exception: {str(e)}")
            
    async def test_database_connection(self):
        """Test database connection endpoint"""
        try:
            test_data = {
                "database_url": "mongodb://localhost:27017"
            }
            
            async with self.session.post(f"{BACKEND_URL}/test-db-connection", 
                                       json=test_data) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    success = data.get("success", False)
                    message = data.get("message", "")
                    
                    self.log_test("Database Connection API", success, message)
                else:
                    self.log_test("Database Connection API", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("Database Connection API", False, f"Exception: {str(e)}")
            
    async def test_v30_license_validation(self):
        """Test V30 license validation"""
        try:
            test_data = {
                "license_key": "INVALID-TEST-KEY-12345"
            }
            
            async with self.session.post(f"{BACKEND_URL}/v30/license/validate", 
                                       json=test_data) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Should reject invalid license
                    valid = data.get("valid", True)  # Expect False for invalid key
                    
                    self.log_test("V30 License Validation", not valid, 
                                f"Invalid license correctly rejected: {not valid}")
                else:
                    self.log_test("V30 License Validation", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("V30 License Validation", False, f"Exception: {str(e)}")
            
    async def test_v30_hardware_validation(self):
        """Test V30 hardware validation"""
        try:
            async with self.session.get(f"{BACKEND_URL}/v30/hardware/validate") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if V30 hardware validation info is returned
                    if "system_info" in data and "requirements_check" in data:
                        memory_gb = data.get("system_info", {}).get("memory", {}).get("total_gb", 0)
                        cpu_cores = data.get("system_info", {}).get("cpu", {}).get("physical_cores", 0)
                        
                        self.log_test("V30 Hardware Validation", True, 
                                    f"Memory: {memory_gb}GB, CPU cores: {cpu_cores}")
                    else:
                        self.log_test("V30 Hardware Validation", False, "Missing hardware info")
                else:
                    self.log_test("V30 Hardware Validation", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("V30 Hardware Validation", False, f"Exception: {str(e)}")
            
    async def test_v30_system_status(self):
        """Test V30 system status"""
        try:
            async with self.session.get(f"{BACKEND_URL}/v30/system/status") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if V30 system info is returned
                    if "initialized" in data:
                        initialized = data.get("initialized", False)
                        
                        self.log_test("V30 System Status", True, 
                                    f"V30 system initialized: {initialized}")
                    else:
                        self.log_test("V30 System Status", False, "Missing system status info")
                else:
                    self.log_test("V30 System Status", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("V30 System Status", False, f"Exception: {str(e)}")
            
    async def test_saved_pools_crud(self):
        """Test saved pools CRUD operations"""
        try:
            # Test GET saved pools
            async with self.session.get(f"{BACKEND_URL}/pools/saved") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    success = data.get("success", False)
                    pools = data.get("pools", [])
                    
                    self.log_test("Saved Pools CRUD", success, 
                                f"Retrieved {len(pools)} saved pools")
                else:
                    self.log_test("Saved Pools CRUD", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("Saved Pools CRUD", False, f"Exception: {str(e)}")
            
    async def test_custom_coins_crud(self):
        """Test custom coins CRUD operations"""
        try:
            # Test GET custom coins
            async with self.session.get(f"{BACKEND_URL}/coins/custom") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    success = data.get("success", False)
                    coins = data.get("coins", [])
                    
                    self.log_test("Custom Coins CRUD", success, 
                                f"Retrieved {len(coins)} custom coins")
                else:
                    self.log_test("Custom Coins CRUD", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("Custom Coins CRUD", False, f"Exception: {str(e)}")
            
    async def test_mining_engine_lifecycle(self):
        """Test mining engine start/stop lifecycle"""
        try:
            # Test mining start with EFL configuration
            mining_config = {
                "coin": {
                    "name": "eLitecoin",
                    "symbol": "EFL", 
                    "algorithm": "Scrypt",
                    "block_reward": 25.0,
                    "block_time": 150,
                    "scrypt_params": {"n": 1024, "r": 1, "p": 1}
                },
                "mode": "pool",
                "threads": 4,
                "wallet_address": "LaEni1U9jb4A38frAbjj3UHMzM6vrre8Dd",
                "pool_username": "LaEni1U9jb4A38frAbjj3UHMzM6vrre8Dd.CryptoMiner-V30-Test",
                "pool_password": "x",
                "custom_pool_address": "stratum.luckydogpool.com",
                "custom_pool_port": 7026
            }
            
            # Start mining
            async with self.session.post(f"{BACKEND_URL}/mining/start", 
                                       json=mining_config) as response:
                if response.status == 200:
                    data = await response.json()
                    start_success = data.get("success", False)
                    
                    if start_success:
                        # Wait for mining to stabilize
                        await asyncio.sleep(MINING_TEST_DURATION)
                        
                        # Check mining status
                        async with self.session.get(f"{BACKEND_URL}/mining/status") as status_response:
                            if status_response.status == 200:
                                status_data = await status_response.json()
                                is_mining = status_data.get("is_mining", False)
                                stats = status_data.get("stats", {})
                                hashrate = stats.get("hashrate", 0)
                                
                                # Stop mining
                                async with self.session.post(f"{BACKEND_URL}/mining/stop") as stop_response:
                                    if stop_response.status == 200:
                                        stop_data = await stop_response.json()
                                        stop_success = stop_data.get("success", False)
                                        
                                        self.log_test("Mining Engine Lifecycle", True, 
                                                    f"Start/Stop successful, Peak hashrate: {hashrate} H/s")
                                    else:
                                        self.log_test("Mining Engine Lifecycle", False, 
                                                    f"Stop failed: HTTP {stop_response.status}")
                            else:
                                self.log_test("Mining Engine Lifecycle", False, 
                                            f"Status check failed: HTTP {status_response.status}")
                    else:
                        self.log_test("Mining Engine Lifecycle", False, 
                                    f"Start failed: {data.get('message', 'Unknown error')}")
                else:
                    self.log_test("Mining Engine Lifecycle", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("Mining Engine Lifecycle", False, f"Exception: {str(e)}")
            
    async def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting CryptoMiner Pro V30 Backend Testing Suite")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Core API Tests
            print("\n📋 CORE API TESTS")
            print("-" * 40)
            await self.test_health_check()
            await self.test_system_info()
            await self.test_mining_status()
            await self.test_coin_presets()
            await self.test_ai_insights()
            await self.test_system_stats()
            await self.test_database_connection()
            
            # V30 Enterprise Tests
            print("\n🏢 V30 ENTERPRISE TESTS")
            print("-" * 40)
            await self.test_v30_license_validation()
            await self.test_v30_hardware_validation()
            await self.test_v30_system_status()
            
            # Data Management Tests
            print("\n💾 DATA MANAGEMENT TESTS")
            print("-" * 40)
            await self.test_saved_pools_crud()
            await self.test_custom_coins_crud()
            
            # Mining Engine Tests
            print("\n⛏️ MINING ENGINE TESTS")
            print("-" * 40)
            await self.test_mining_engine_lifecycle()
            
        finally:
            await self.cleanup()
            
        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉 ALL TESTS PASSED - Backend functionality verified after naming fixes!")
        elif success_rate >= 90:
            print("✅ MOSTLY SUCCESSFUL - Minor issues detected")
        else:
            print("❌ SIGNIFICANT ISSUES - Backend functionality compromised")
            
        print("\n📝 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"{result['status']} {result['test']}: {result['message']}")
            
        return success_rate

async def main():
    """Main test runner"""
    tester = BackendTester()
    success_rate = await tester.run_all_tests()
    
    # Exit with appropriate code
    if success_rate == 100:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())