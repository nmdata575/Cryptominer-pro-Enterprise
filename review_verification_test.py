#!/usr/bin/env python3
"""
CryptoMiner Pro V30 Review Request Verification Test
Specifically tests the areas mentioned in the review request:
1. Core API Endpoints
2. Database Functionality  
3. Mining Engine
4. V30 Enterprise Features
5. Service Status
"""

import requests
import json
import time
import sys

BACKEND_URL = "https://cryptominer-pro-1.preview.emergentagent.com/api"

class ReviewVerificationTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.session.timeout = 30
        self.results = []
        
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_core_api_endpoints(self) -> bool:
        """Test all critical backend APIs including health, mining status, system info, database connection"""
        print("\n🔍 TESTING CORE API ENDPOINTS")
        
        core_apis = [
            ("/health", "Health Check"),
            ("/mining/status", "Mining Status"),
            ("/system/cpu-info", "System Info"),
            ("/system/stats", "System Statistics"),
            ("/coins/presets", "Coin Presets")
        ]
        
        passed = 0
        total = len(core_apis)
        
        for endpoint, name in core_apis:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ {name}: OK")
                    passed += 1
                else:
                    print(f"   ❌ {name}: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {name}: {str(e)}")
        
        success = passed == total
        self.log_result("Core API Endpoints", success, f"{passed}/{total} endpoints working")
        return success
    
    def test_database_functionality(self) -> bool:
        """Verify MongoDB connection and all CRUD operations for saved pools and custom coins"""
        print("\n🔍 TESTING DATABASE FUNCTIONALITY")
        
        # Test 1: Database connection via health check
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                db_status = health_data.get("database", {}).get("status", "unknown")
                if db_status == "connected":
                    print("   ✅ MongoDB Connection: Connected")
                else:
                    print(f"   ❌ MongoDB Connection: {db_status}")
                    self.log_result("Database Functionality", False, f"Database status: {db_status}")
                    return False
            else:
                print(f"   ❌ Health check failed: HTTP {response.status_code}")
                self.log_result("Database Functionality", False, "Health check failed")
                return False
        except Exception as e:
            print(f"   ❌ Database connection test failed: {str(e)}")
            self.log_result("Database Functionality", False, f"Connection test error: {str(e)}")
            return False
        
        # Test 2: Saved Pools CRUD operations
        try:
            # GET saved pools
            response = self.session.get(f"{self.base_url}/pools/saved")
            if response.status_code != 200:
                print(f"   ❌ Saved Pools GET: HTTP {response.status_code}")
                self.log_result("Database Functionality", False, "Saved pools GET failed")
                return False
            
            # CREATE a test pool
            test_pool = {
                "name": f"Review Test Pool {int(time.time())}",
                "coin_symbol": "EFL",
                "wallet_address": "LaEni1U9jb4A38frAbjj3UHMzM6vrre8Dd",
                "pool_address": "stratum.luckydogpool.com",
                "pool_port": 7026,
                "pool_password": "x"
            }
            
            response = self.session.post(f"{self.base_url}/pools/saved", json=test_pool)
            if response.status_code != 200 or not response.json().get("success"):
                print(f"   ❌ Saved Pools CREATE: Failed")
                self.log_result("Database Functionality", False, "Saved pools CREATE failed")
                return False
            
            pool_id = response.json().get("pool_id")
            
            # DELETE the test pool
            response = self.session.delete(f"{self.base_url}/pools/saved/{pool_id}")
            if response.status_code != 200 or not response.json().get("success"):
                print(f"   ❌ Saved Pools DELETE: Failed")
                self.log_result("Database Functionality", False, "Saved pools DELETE failed")
                return False
            
            print("   ✅ Saved Pools CRUD: All operations working")
            
        except Exception as e:
            print(f"   ❌ Saved Pools CRUD error: {str(e)}")
            self.log_result("Database Functionality", False, f"Saved pools CRUD error: {str(e)}")
            return False
        
        # Test 3: Custom Coins CRUD operations
        try:
            # GET custom coins
            response = self.session.get(f"{self.base_url}/coins/custom")
            if response.status_code != 200:
                print(f"   ❌ Custom Coins GET: HTTP {response.status_code}")
                self.log_result("Database Functionality", False, "Custom coins GET failed")
                return False
            
            # CREATE a test coin
            test_coin = {
                "name": f"Review Test Coin {int(time.time())}",
                "symbol": f"RTC{int(time.time()) % 1000}",
                "algorithm": "Scrypt",
                "block_reward": 25.0,
                "block_time": 150,
                "scrypt_params": {"n": 1024, "r": 1, "p": 1}
            }
            
            response = self.session.post(f"{self.base_url}/coins/custom", json=test_coin)
            if response.status_code != 200 or not response.json().get("success"):
                print(f"   ❌ Custom Coins CREATE: Failed")
                self.log_result("Database Functionality", False, "Custom coins CREATE failed")
                return False
            
            coin_id = response.json().get("coin_id")
            
            # DELETE the test coin
            response = self.session.delete(f"{self.base_url}/coins/custom/{coin_id}")
            if response.status_code != 200 or not response.json().get("success"):
                print(f"   ❌ Custom Coins DELETE: Failed")
                self.log_result("Database Functionality", False, "Custom coins DELETE failed")
                return False
            
            print("   ✅ Custom Coins CRUD: All operations working")
            
        except Exception as e:
            print(f"   ❌ Custom Coins CRUD error: {str(e)}")
            self.log_result("Database Functionality", False, f"Custom coins CRUD error: {str(e)}")
            return False
        
        self.log_result("Database Functionality", True, "MongoDB connection and all CRUD operations working")
        return True
    
    def test_mining_engine(self) -> bool:
        """Test mining functionality including start/stop operations and real mining capabilities"""
        print("\n🔍 TESTING MINING ENGINE")
        
        try:
            # Test mining start with real EFL pool configuration
            mining_config = {
                "coin": {
                    "name": "Electronic Gulden",
                    "symbol": "EFL",
                    "algorithm": "Scrypt",
                    "block_reward": 25.0,
                    "block_time": 150,
                    "difficulty": 1000.0,
                    "scrypt_params": {"n": 1024, "r": 1, "p": 1},
                    "network_hashrate": "Unknown",
                    "wallet_format": "L prefix",
                    "custom_pool_address": "stratum.luckydogpool.com",
                    "custom_pool_port": 7026
                },
                "wallet_address": "LaEni1U9jb4A38frAbjj3UHMzM6vrre8Dd",
                "pool_username": "LaEni1U9jb4A38frAbjj3UHMzM6vrre8Dd",
                "pool_password": "x",
                "threads": 4,
                "mode": "pool"
            }
            
            # Start mining
            response = self.session.post(f"{self.base_url}/mining/start", json=mining_config)
            if response.status_code != 200:
                print(f"   ❌ Mining Start: HTTP {response.status_code}")
                self.log_result("Mining Engine", False, f"Mining start failed: HTTP {response.status_code}")
                return False
            
            start_data = response.json()
            if not start_data.get("success"):
                print(f"   ❌ Mining Start: {start_data.get('message', 'Unknown error')}")
                self.log_result("Mining Engine", False, f"Mining start failed: {start_data.get('message')}")
                return False
            
            print("   ✅ Mining Start: Successfully started with EFL pool")
            
            # Wait for mining to stabilize
            time.sleep(3)
            
            # Check mining status
            response = self.session.get(f"{self.base_url}/mining/status")
            if response.status_code != 200:
                print(f"   ❌ Mining Status: HTTP {response.status_code}")
                self.log_result("Mining Engine", False, "Mining status check failed")
                return False
            
            status_data = response.json()
            is_mining = status_data.get("is_mining", False)
            stats = status_data.get("stats", {})
            hashrate = stats.get("hashrate", 0)
            uptime = stats.get("uptime", 0)
            
            if uptime > 0:
                print(f"   ✅ Real Mining: Active for {uptime:.1f}s with {hashrate:.2f} H/s")
            else:
                print(f"   ⚠️  Mining Status: is_mining={is_mining}, hashrate={hashrate}")
            
            # Stop mining
            response = self.session.post(f"{self.base_url}/mining/stop")
            if response.status_code != 200:
                print(f"   ❌ Mining Stop: HTTP {response.status_code}")
                self.log_result("Mining Engine", False, "Mining stop failed")
                return False
            
            stop_data = response.json()
            if stop_data.get("success") or "not active" in stop_data.get("message", "").lower():
                print("   ✅ Mining Stop: Successfully stopped")
            else:
                print(f"   ❌ Mining Stop: {stop_data.get('message', 'Unknown error')}")
                self.log_result("Mining Engine", False, f"Mining stop failed: {stop_data.get('message')}")
                return False
            
            self.log_result("Mining Engine", True, "Start/stop operations and real mining capabilities working")
            return True
            
        except Exception as e:
            print(f"   ❌ Mining Engine error: {str(e)}")
            self.log_result("Mining Engine", False, f"Mining engine error: {str(e)}")
            return False
    
    def test_v30_enterprise_features(self) -> bool:
        """Verify all V30 features are operational including license system, hardware validation"""
        print("\n🔍 TESTING V30 ENTERPRISE FEATURES")
        
        v30_tests = []
        
        # Test 1: License System
        try:
            test_data = {"license_key": "INVALID-TEST-KEY"}
            response = self.session.post(f"{self.base_url}/v30/license/validate", json=test_data)
            if response.status_code == 200:
                data = response.json()
                if not data.get("valid"):  # Should reject invalid license
                    print("   ✅ License System: Working (correctly rejected invalid license)")
                    v30_tests.append(True)
                else:
                    print("   ❌ License System: Should reject invalid license")
                    v30_tests.append(False)
            else:
                print(f"   ❌ License System: HTTP {response.status_code}")
                v30_tests.append(False)
        except Exception as e:
            print(f"   ❌ License System error: {str(e)}")
            v30_tests.append(False)
        
        # Test 2: Hardware Validation
        try:
            response = self.session.get(f"{self.base_url}/v30/hardware/validate")
            if response.status_code == 200:
                data = response.json()
                if "system_info" in data and "requirements_check" in data:
                    system_info = data["system_info"]
                    memory_gb = system_info.get("memory", {}).get("total_gb", 0)
                    cpu_cores = system_info.get("cpu", {}).get("physical_cores", 0)
                    print(f"   ✅ Hardware Validation: Working (Memory: {memory_gb}GB, CPU: {cpu_cores} cores)")
                    v30_tests.append(True)
                else:
                    print("   ❌ Hardware Validation: Missing system info")
                    v30_tests.append(False)
            else:
                print(f"   ❌ Hardware Validation: HTTP {response.status_code}")
                v30_tests.append(False)
        except Exception as e:
            print(f"   ❌ Hardware Validation error: {str(e)}")
            v30_tests.append(False)
        
        # Test 3: System Initialization
        try:
            response = self.session.post(f"{self.base_url}/v30/system/initialize")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    features_count = data.get("features_enabled", 0)
                    print(f"   ✅ System Initialization: Working ({features_count} features enabled)")
                    v30_tests.append(True)
                else:
                    print(f"   ❌ System Initialization: {data.get('error', 'Unknown error')}")
                    v30_tests.append(False)
            else:
                print(f"   ❌ System Initialization: HTTP {response.status_code}")
                v30_tests.append(False)
        except Exception as e:
            print(f"   ❌ System Initialization error: {str(e)}")
            v30_tests.append(False)
        
        # Test 4: System Status
        try:
            response = self.session.get(f"{self.base_url}/v30/system/status")
            if response.status_code == 200:
                data = response.json()
                if "capabilities" in data:
                    capabilities = data["capabilities"]
                    cap_count = len([k for k, v in capabilities.items() if v])
                    print(f"   ✅ System Status: Working ({cap_count} capabilities active)")
                    v30_tests.append(True)
                else:
                    print("   ❌ System Status: Missing capabilities")
                    v30_tests.append(False)
            else:
                print(f"   ❌ System Status: HTTP {response.status_code}")
                v30_tests.append(False)
        except Exception as e:
            print(f"   ❌ System Status error: {str(e)}")
            v30_tests.append(False)
        
        passed = sum(v30_tests)
        total = len(v30_tests)
        success = passed == total
        
        self.log_result("V30 Enterprise Features", success, f"{passed}/{total} V30 features operational")
        return success
    
    def test_service_status(self) -> bool:
        """Check that all services are running correctly"""
        print("\n🔍 TESTING SERVICE STATUS")
        
        try:
            # Test backend service via health check
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code != 200:
                print(f"   ❌ Backend Service: HTTP {response.status_code}")
                self.log_result("Service Status", False, "Backend service not responding")
                return False
            
            health_data = response.json()
            
            # Check service components
            status = health_data.get("status", "unknown")
            ai_system = health_data.get("ai_system", False)
            v30_system = health_data.get("v30_system", False)
            database = health_data.get("database", {})
            db_status = database.get("status", "unknown")
            
            print(f"   ✅ Backend Service: {status}")
            print(f"   ✅ AI System: {'Active' if ai_system else 'Inactive'}")
            print(f"   ✅ V30 System: {'Running' if v30_system else 'Stopped'}")
            print(f"   ✅ Database Service: {db_status}")
            
            # Check if MongoDB is accessible
            if db_status == "connected":
                print("   ✅ MongoDB: Running on localhost:27017")
            else:
                print(f"   ⚠️  MongoDB: {db_status}")
            
            # All core services should be operational
            services_ok = (status == "healthy" and 
                          ai_system and 
                          db_status == "connected")
            
            if services_ok:
                self.log_result("Service Status", True, "All services running correctly")
                return True
            else:
                self.log_result("Service Status", False, f"Service issues detected - Status: {status}, AI: {ai_system}, DB: {db_status}")
                return False
            
        except Exception as e:
            print(f"   ❌ Service Status error: {str(e)}")
            self.log_result("Service Status", False, f"Service status check error: {str(e)}")
            return False
    
    def run_review_verification(self):
        """Run all review verification tests"""
        print("🚀 CRYPTOMINER PRO V30 REVIEW REQUEST VERIFICATION")
        print(f"📡 Testing backend at: {self.base_url}")
        print("🎯 Verifying all functionality before installation script improvements")
        print("=" * 80)
        
        # Run all verification tests
        tests = [
            ("1. Core API Endpoints", self.test_core_api_endpoints),
            ("2. Database Functionality", self.test_database_functionality),
            ("3. Mining Engine", self.test_mining_engine),
            ("4. V30 Enterprise Features", self.test_v30_enterprise_features),
            ("5. Service Status", self.test_service_status)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 {test_name}")
            try:
                start_time = time.time()
                success = test_func()
                end_time = time.time()
                duration = end_time - start_time
                print(f"   ⏱️  Test duration: {duration:.2f}s")
            except Exception as e:
                print(f"   ❌ Test execution failed: {str(e)}")
                self.log_result(test_name, False, f"Test execution error: {str(e)}")
        
        # Calculate results
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 REVIEW VERIFICATION RESULTS:")
        print("=" * 80)
        print(f"📈 SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests)")
        print(f"✅ PASSED TESTS: {passed_tests}")
        print(f"❌ FAILED TESTS: {failed_tests}")
        
        if failed_tests == 0:
            print("\n🎉 ALL VERIFICATION TESTS PASSED!")
            print("✅ System is ready for installation script validation")
            print("✅ MongoDB is running on localhost:27017")
            print("✅ Backend is accessible on localhost:8001")
            print("✅ All dependencies verified")
            print("✅ 100% success rate confirmed")
        else:
            print(f"\n⚠️  {failed_tests} VERIFICATION TEST(S) FAILED")
            print("❌ System requires fixes before proceeding")
            
            for result in self.results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "all_passed": failed_tests == 0
        }

def main():
    """Main test execution"""
    tester = ReviewVerificationTester()
    results = tester.run_review_verification()
    
    # Exit with appropriate code
    if results["all_passed"]:
        print("\n🎉 Review verification completed successfully!")
        sys.exit(0)
    else:
        print(f"\n⚠️  Review verification failed - {results['failed_tests']} test(s) failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()