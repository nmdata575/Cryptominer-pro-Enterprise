#!/usr/bin/env python3
"""
CryptoMiner Pro Real Mining Test Suite
Tests actual mining functionality with real EFL pool connection
Focus on share acceptance and mining performance under load
"""

import requests
import json
import time
import sys
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

# Backend URL from environment
BACKEND_URL = "https://0aecbcf7-d390-4bac-b616-167712cf354b.preview.emergentagent.com/api"

class RealMiningTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.session.timeout = 30
        self.test_results = []
        self.mining_active = False
        self.monitoring_active = False
        self.share_data = []
        self.performance_data = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": timestamp
        })
    
    def start_real_mining_session(self) -> bool:
        """Start real mining session with EFL coin"""
        try:
            print("\n🚀 Starting Real EFL Mining Session...")
            
            # EFL mining configuration as specified
            mining_config = {
                "coin_symbol": "EFL",
                "wallet_address": "LaEni1U9jb4A38frAbjj3UHMzM6vrre8Dd",
                "threads": 4,
                "custom_pool_address": "stratum.luckydogpool.com",
                "custom_pool_port": 7026,
                "mode": "pool",
                "pool_username": "LaEni1U9jb4A38frAbjj3UHMzM6vrre8Dd",
                "pool_password": "x",
                "auto_optimize": True,
                "ai_enabled": True,
                "intensity": 1.0
            }
            
            # Convert to the expected format
            start_config = {
                "coin": {
                    "symbol": "EFL",
                    "name": "Electronic Gulden",
                    "algorithm": "Scrypt"
                },
                "wallet_address": mining_config["wallet_address"],
                "threads": mining_config["threads"],
                "mode": "pool",
                "custom_pool_address": mining_config["custom_pool_address"],
                "custom_pool_port": mining_config["custom_pool_port"],
                "pool_username": mining_config["pool_username"],
                "pool_password": mining_config["pool_password"],
                "auto_optimize": mining_config["auto_optimize"],
                "ai_enabled": mining_config["ai_enabled"],
                "intensity": mining_config["intensity"]
            }
            
            response = self.session.post(f"{self.base_url}/mining/start", json=start_config)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.mining_active = True
                    self.log_test("Real Mining Start", True, 
                                f"EFL mining started with {mining_config['threads']} threads on {mining_config['custom_pool_address']}:{mining_config['custom_pool_port']}")
                    return True
                else:
                    self.log_test("Real Mining Start", False, f"Mining start failed: {data.get('message')}")
                    return False
            else:
                self.log_test("Real Mining Start", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Real Mining Start", False, f"Exception: {str(e)}")
            return False
    
    def monitor_mining_status(self, duration_minutes: int = 5) -> bool:
        """Monitor mining status for specified duration"""
        try:
            print(f"\n📊 Monitoring Mining Status for {duration_minutes} minutes...")
            
            start_time = datetime.now()
            end_time = start_time + timedelta(minutes=duration_minutes)
            check_interval = 30  # Check every 30 seconds
            
            status_checks = 0
            successful_checks = 0
            share_accepted = 0
            share_rejected = 0
            total_hashrate = 0
            hashrate_samples = 0
            
            while datetime.now() < end_time and self.mining_active:
                try:
                    response = self.session.get(f"{self.base_url}/mining/status")
                    
                    if response.status_code == 200:
                        data = response.json()
                        status_checks += 1
                        
                        if data.get("is_mining"):
                            successful_checks += 1
                            stats = data.get("stats", {})
                            
                            # Collect performance data
                            current_hashrate = stats.get("hashrate", 0)
                            if current_hashrate > 0:
                                total_hashrate += current_hashrate
                                hashrate_samples += 1
                            
                            # Look for share data
                            shares_accepted = stats.get("shares_accepted", 0)
                            shares_rejected = stats.get("shares_rejected", 0)
                            
                            if shares_accepted > share_accepted:
                                share_accepted = shares_accepted
                                print(f"    ✅ Share accepted! Total: {share_accepted}")
                            
                            if shares_rejected > share_rejected:
                                share_rejected = shares_rejected
                                print(f"    ❌ Share rejected! Total: {share_rejected}")
                            
                            # Log current status
                            elapsed = (datetime.now() - start_time).total_seconds() / 60
                            print(f"    [{elapsed:.1f}min] Mining: {data.get('is_mining')}, "
                                  f"Hashrate: {current_hashrate:.2f} H/s, "
                                  f"Accepted: {shares_accepted}, Rejected: {shares_rejected}")
                            
                            # Store performance data
                            self.performance_data.append({
                                "timestamp": datetime.now(),
                                "hashrate": current_hashrate,
                                "shares_accepted": shares_accepted,
                                "shares_rejected": shares_rejected,
                                "cpu_usage": stats.get("cpu_usage", 0),
                                "memory_usage": stats.get("memory_usage", 0)
                            })
                        else:
                            print(f"    ⚠️ Mining stopped unexpectedly")
                            self.mining_active = False
                            break
                    else:
                        print(f"    ❌ Status check failed: HTTP {response.status_code}")
                    
                    time.sleep(check_interval)
                    
                except Exception as e:
                    print(f"    ❌ Status check error: {str(e)}")
                    time.sleep(check_interval)
            
            # Calculate results
            avg_hashrate = total_hashrate / hashrate_samples if hashrate_samples > 0 else 0
            total_shares = share_accepted + share_rejected
            acceptance_rate = (share_accepted / total_shares * 100) if total_shares > 0 else 0
            
            success = (
                successful_checks > 0 and
                status_checks > 0 and
                (successful_checks / status_checks) >= 0.8  # 80% successful status checks
            )
            
            details = (f"Status checks: {successful_checks}/{status_checks}, "
                      f"Avg hashrate: {avg_hashrate:.2f} H/s, "
                      f"Shares: {share_accepted} accepted, {share_rejected} rejected, "
                      f"Acceptance rate: {acceptance_rate:.1f}%")
            
            self.log_test("Mining Status Monitoring", success, details)
            
            # Store share data for analysis
            self.share_data = {
                "accepted": share_accepted,
                "rejected": share_rejected,
                "total": total_shares,
                "acceptance_rate": acceptance_rate,
                "avg_hashrate": avg_hashrate,
                "duration_minutes": duration_minutes
            }
            
            return success
            
        except Exception as e:
            self.log_test("Mining Status Monitoring", False, f"Exception: {str(e)}")
            return False
    
    def test_enterprise_features_during_mining(self) -> bool:
        """Test enterprise features while mining is active"""
        try:
            print("\n🏢 Testing Enterprise Features During Mining...")
            
            if not self.mining_active:
                self.log_test("Enterprise Features During Mining", False, "Mining not active")
                return False
            
            tests_passed = 0
            total_tests = 0
            
            # Test V30 license validation
            total_tests += 1
            try:
                response = self.session.post(f"{self.base_url}/v30/license/validate", 
                                           json={"license_key": "V30-TEST-LICENSE-KEY"})
                if response.status_code == 200:
                    tests_passed += 1
                    print("    ✅ V30 license validation responsive during mining")
                else:
                    print("    ❌ V30 license validation failed during mining")
            except Exception as e:
                print(f"    ❌ V30 license validation error: {str(e)}")
            
            # Test hardware validation
            total_tests += 1
            try:
                response = self.session.get(f"{self.base_url}/v30/hardware/validate")
                if response.status_code == 200:
                    tests_passed += 1
                    print("    ✅ Hardware validation responsive during mining")
                else:
                    print("    ❌ Hardware validation failed during mining")
            except Exception as e:
                print(f"    ❌ Hardware validation error: {str(e)}")
            
            # Test AI insights with real mining data
            total_tests += 1
            try:
                response = self.session.get(f"{self.base_url}/mining/ai-insights")
                if response.status_code == 200:
                    data = response.json()
                    if "insights" in data:
                        tests_passed += 1
                        print("    ✅ AI insights working with real mining data")
                    else:
                        print("    ❌ AI insights missing data during mining")
                else:
                    print("    ❌ AI insights failed during mining")
            except Exception as e:
                print(f"    ❌ AI insights error: {str(e)}")
            
            # Test saved pools CRUD during mining
            total_tests += 1
            try:
                response = self.session.get(f"{self.base_url}/pools/saved")
                if response.status_code == 200:
                    tests_passed += 1
                    print("    ✅ Saved pools API responsive during mining")
                else:
                    print("    ❌ Saved pools API failed during mining")
            except Exception as e:
                print(f"    ❌ Saved pools API error: {str(e)}")
            
            success = tests_passed >= (total_tests * 0.75)  # 75% success rate
            details = f"Enterprise features: {tests_passed}/{total_tests} responsive during mining"
            
            self.log_test("Enterprise Features During Mining", success, details)
            return success
            
        except Exception as e:
            self.log_test("Enterprise Features During Mining", False, f"Exception: {str(e)}")
            return False
    
    def test_different_thread_counts(self) -> bool:
        """Test mining with different thread counts"""
        try:
            print("\n🔧 Testing Different Thread Counts...")
            
            thread_counts = [1, 4, 8, 16]
            successful_configs = 0
            
            for threads in thread_counts:
                print(f"    Testing with {threads} threads...")
                
                # Stop current mining
                if self.mining_active:
                    self.session.post(f"{self.base_url}/mining/stop")
                    time.sleep(2)
                
                # Start with new thread count
                config = {
                    "coin": {
                        "symbol": "EFL",
                        "name": "Electronic Gulden",
                        "algorithm": "Scrypt"
                    },
                    "wallet_address": "LaEni1U9jb4A38frAbjj3UHMzM6vrre8Dd",
                    "threads": threads,
                    "mode": "pool",
                    "custom_pool_address": "stratum.luckydogpool.com",
                    "custom_pool_port": 7026,
                    "pool_username": "LaEni1U9jb4A38frAbjj3UHMzM6vrre8Dd",
                    "pool_password": "x"
                }
                
                response = self.session.post(f"{self.base_url}/mining/start", json=config)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        successful_configs += 1
                        print(f"      ✅ {threads} threads: Started successfully")
                        
                        # Brief monitoring
                        time.sleep(10)
                        status_response = self.session.get(f"{self.base_url}/mining/status")
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            if status_data.get("is_mining"):
                                stats = status_data.get("stats", {})
                                hashrate = stats.get("hashrate", 0)
                                print(f"      📊 {threads} threads: Hashrate {hashrate:.2f} H/s")
                            else:
                                print(f"      ❌ {threads} threads: Mining stopped")
                        else:
                            print(f"      ❌ {threads} threads: Status check failed")
                    else:
                        print(f"      ❌ {threads} threads: Start failed - {data.get('message')}")
                else:
                    print(f"      ❌ {threads} threads: HTTP {response.status_code}")
                
                time.sleep(2)
            
            success = successful_configs >= len(thread_counts) * 0.75  # 75% success rate
            details = f"Thread configurations: {successful_configs}/{len(thread_counts)} successful"
            
            self.log_test("Different Thread Counts", success, details)
            
            # Restart with original config
            if successful_configs > 0:
                self.start_real_mining_session()
            
            return success
            
        except Exception as e:
            self.log_test("Different Thread Counts", False, f"Exception: {str(e)}")
            return False
    
    def test_system_stability_under_load(self) -> bool:
        """Test system stability and API responsiveness under mining load"""
        try:
            print("\n⚡ Testing System Stability Under Mining Load...")
            
            if not self.mining_active:
                self.log_test("System Stability Under Load", False, "Mining not active")
                return False
            
            # Test multiple concurrent API calls
            api_endpoints = [
                "/health",
                "/system/stats",
                "/system/cpu-info",
                "/mining/status",
                "/coins/presets",
                "/v30/system/status"
            ]
            
            successful_calls = 0
            total_calls = 0
            response_times = []
            
            for endpoint in api_endpoints:
                for _ in range(3):  # 3 calls per endpoint
                    total_calls += 1
                    start_time = time.time()
                    
                    try:
                        response = self.session.get(f"{self.base_url}{endpoint}")
                        response_time = time.time() - start_time
                        response_times.append(response_time)
                        
                        if response.status_code == 200:
                            successful_calls += 1
                        
                    except Exception as e:
                        print(f"    ❌ {endpoint} failed: {str(e)}")
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            success_rate = (successful_calls / total_calls) if total_calls > 0 else 0
            
            # Check if system remains stable (>90% success rate, <5s avg response time)
            success = success_rate >= 0.9 and avg_response_time < 5.0
            
            details = (f"API calls: {successful_calls}/{total_calls} successful, "
                      f"Avg response time: {avg_response_time:.2f}s, "
                      f"Success rate: {success_rate:.1%}")
            
            self.log_test("System Stability Under Load", success, details)
            return success
            
        except Exception as e:
            self.log_test("System Stability Under Load", False, f"Exception: {str(e)}")
            return False
    
    def verify_share_acceptance(self) -> bool:
        """Verify share acceptance and calculate acceptance rate"""
        try:
            print("\n🎯 Verifying Share Acceptance...")
            
            if not self.share_data:
                self.log_test("Share Acceptance Verification", False, "No share data collected")
                return False
            
            accepted = self.share_data["accepted"]
            rejected = self.share_data["rejected"]
            total = self.share_data["total"]
            acceptance_rate = self.share_data["acceptance_rate"]
            avg_hashrate = self.share_data["avg_hashrate"]
            
            # Success criteria:
            # - At least 1 share submitted
            # - Acceptance rate > 90% (if shares submitted)
            # - Average hashrate > 0
            
            if total == 0:
                success = False
                details = "No shares submitted to pool"
            elif acceptance_rate >= 90.0:
                success = True
                details = f"Excellent: {accepted}/{total} shares accepted ({acceptance_rate:.1f}%), Avg hashrate: {avg_hashrate:.2f} H/s"
            elif acceptance_rate >= 70.0:
                success = True
                details = f"Good: {accepted}/{total} shares accepted ({acceptance_rate:.1f}%), Avg hashrate: {avg_hashrate:.2f} H/s"
            else:
                success = False
                details = f"Poor: {accepted}/{total} shares accepted ({acceptance_rate:.1f}%), Avg hashrate: {avg_hashrate:.2f} H/s"
            
            self.log_test("Share Acceptance Verification", success, details)
            return success
            
        except Exception as e:
            self.log_test("Share Acceptance Verification", False, f"Exception: {str(e)}")
            return False
    
    def stop_mining(self) -> bool:
        """Stop mining session"""
        try:
            if self.mining_active:
                response = self.session.post(f"{self.base_url}/mining/stop")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.mining_active = False
                        self.log_test("Mining Stop", True, "Mining stopped successfully")
                        return True
                    else:
                        self.log_test("Mining Stop", False, f"Stop failed: {data.get('message')}")
                        return False
                else:
                    self.log_test("Mining Stop", False, f"HTTP {response.status_code}")
                    return False
            else:
                self.log_test("Mining Stop", True, "Mining was not active")
                return True
                
        except Exception as e:
            self.log_test("Mining Stop", False, f"Exception: {str(e)}")
            return False
    
    def run_real_mining_tests(self) -> Dict[str, Any]:
        """Run comprehensive real mining tests"""
        print("🚀 Starting CryptoMiner Pro Real Mining Tests")
        print(f"📡 Testing backend at: {self.base_url}")
        print(f"🎯 Target: EFL mining on stratum.luckydogpool.com:7026")
        print("=" * 70)
        
        try:
            # 1. Start real mining session
            if not self.start_real_mining_session():
                print("❌ Failed to start mining session. Aborting tests.")
                return self.get_results_summary()
            
            # 2. Test different thread counts
            self.test_different_thread_counts()
            
            # 3. Monitor mining for 5+ minutes
            self.monitor_mining_status(duration_minutes=5)
            
            # 4. Test enterprise features during mining
            self.test_enterprise_features_during_mining()
            
            # 5. Test system stability under load
            self.test_system_stability_under_load()
            
            # 6. Verify share acceptance
            self.verify_share_acceptance()
            
        finally:
            # Always stop mining at the end
            self.stop_mining()
        
        return self.get_results_summary()
    
    def get_results_summary(self) -> Dict[str, Any]:
        """Get comprehensive test results summary"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 70)
        print(f"📊 Real Mining Test Results Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        if self.share_data:
            print(f"\n🎯 Share Acceptance Results:")
            print(f"   Shares Accepted: {self.share_data['accepted']}")
            print(f"   Shares Rejected: {self.share_data['rejected']}")
            print(f"   Acceptance Rate: {self.share_data['acceptance_rate']:.1f}%")
            print(f"   Average Hashrate: {self.share_data['avg_hashrate']:.2f} H/s")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • [{result['timestamp']}] {result['test']}: {result['details']}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "share_data": self.share_data,
            "performance_data": self.performance_data,
            "test_results": self.test_results
        }

def main():
    """Main test execution"""
    tester = RealMiningTester()
    results = tester.run_real_mining_tests()
    
    # Determine success criteria
    success_criteria_met = (
        results["success_rate"] >= 80.0 and  # 80% test success rate
        results.get("share_data", {}).get("total", 0) > 0  # At least some shares submitted
    )
    
    if success_criteria_met:
        print("\n🎉 Real mining tests completed successfully!")
        print("✅ Mining engine works with real cryptocurrency networks")
        print("✅ Share submission and acceptance verified")
        print("✅ System remains stable under mining load")
        sys.exit(0)
    else:
        print(f"\n⚠️ Real mining tests completed with issues.")
        print(f"Success rate: {results['success_rate']:.1f}% (target: 80%+)")
        if results.get("share_data", {}).get("total", 0) == 0:
            print("❌ No shares were submitted to the mining pool")
        sys.exit(1)

if __name__ == "__main__":
    main()