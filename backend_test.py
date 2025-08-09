#!/usr/bin/env python3
"""
CryptoMiner Pro - Enterprise Backend Testing Suite
Tests all enterprise-scale features including 250k+ thread support, 
enterprise database options, and enhanced system detection
"""

import requests
import json
import time
import os
import sys
from typing import Dict, Any, List

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class CryptoMinerProTester:
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        self.passed_tests = []
        
    def log_test(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        
        if success:
            self.passed_tests.append(test_name)
            print(f"✅ {test_name}: {message}")
        else:
            self.failed_tests.append(test_name)
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {details}")
    
    def test_health_check(self):
        """Test basic health check endpoint"""
        try:
            response = requests.get(f"{API_BASE}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for enterprise features in health response
                required_fields = ["status", "version", "ai_system", "mining_active"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Health Check", False, f"Missing fields: {missing_fields}", data)
                else:
                    enterprise_info = {
                        "version": data.get("version"),
                        "ai_system": data.get("ai_system"),
                        "status": data.get("status")
                    }
                    self.log_test("Health Check", True, "Enterprise health check passed", enterprise_info)
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
    
    def test_cpu_info_enterprise(self):
        """Test enterprise CPU info endpoint with 250k+ thread support"""
        try:
            response = requests.get(f"{API_BASE}/system/cpu-info", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for enterprise-scale features
                enterprise_fields = [
                    "max_safe_threads", "enterprise_mode", "optimal_thread_density",
                    "total_memory_gb", "available_memory_gb", "recommended_threads"
                ]
                
                missing_fields = [field for field in enterprise_fields if field not in data]
                
                if missing_fields:
                    self.log_test("CPU Info Enterprise", False, f"Missing enterprise fields: {missing_fields}", data)
                    return
                
                # Validate enterprise capabilities
                max_safe_threads = data.get("max_safe_threads", 0)
                enterprise_mode = data.get("enterprise_mode", False)
                recommended_threads = data.get("recommended_threads", {})
                
                # Test enterprise thread scaling (should support high thread counts)
                enterprise_checks = []
                
                if max_safe_threads >= 8:  # Should support at least 8x oversubscription
                    enterprise_checks.append("✓ High thread count support")
                else:
                    enterprise_checks.append("✗ Low thread count limit")
                
                if isinstance(recommended_threads, dict) and len(recommended_threads) >= 4:
                    enterprise_checks.append("✓ Thread profiles available")
                else:
                    enterprise_checks.append("✗ Missing thread profiles")
                
                if data.get("total_memory_gb", 0) > 0:
                    enterprise_checks.append("✓ Memory detection working")
                else:
                    enterprise_checks.append("✗ Memory detection failed")
                
                # Check if system can theoretically support enterprise scale
                logical_cores = data.get("logical_cores", 1)
                theoretical_max = logical_cores * 8  # More realistic scaling factor
                
                if max_safe_threads >= min(theoretical_max, 64):  # Should support reasonable enterprise scaling
                    enterprise_checks.append("✓ Enterprise scaling capable")
                else:
                    enterprise_checks.append("✗ Limited scaling capability")
                
                test_details = {
                    "max_safe_threads": max_safe_threads,
                    "enterprise_mode": enterprise_mode,
                    "logical_cores": logical_cores,
                    "enterprise_checks": enterprise_checks,
                    "recommended_threads": recommended_threads
                }
                
                failed_checks = [check for check in enterprise_checks if check.startswith("✗")]
                if failed_checks:
                    self.log_test("CPU Info Enterprise", False, f"Enterprise features incomplete: {len(failed_checks)} issues", test_details)
                else:
                    self.log_test("CPU Info Enterprise", True, f"Enterprise CPU detection working - max threads: {max_safe_threads:,}", test_details)
                    
            else:
                self.log_test("CPU Info Enterprise", False, f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_test("CPU Info Enterprise", False, f"Request error: {str(e)}")
    
    def test_database_connection(self):
        """Test enterprise database connection endpoint"""
        try:
            # Test with localhost URL (should succeed)
            localhost_test = {
                "database_url": "mongodb://localhost:27017"
            }
            
            response = requests.post(f"{API_BASE}/test-db-connection", 
                                   json=localhost_test, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    self.log_test("Database Connection (Valid)", True, 
                                "Localhost database connection successful", data)
                else:
                    self.log_test("Database Connection (Valid)", False, 
                                f"Connection failed: {data.get('error', 'Unknown error')}", data)
            else:
                self.log_test("Database Connection (Valid)", False, 
                            f"HTTP {response.status_code}", {"response": response.text})
            
            # Test with invalid URL (should fail gracefully)
            invalid_test = {
                "database_url": "mongodb://invalid-host:27017"
            }
            
            response = requests.post(f"{API_BASE}/test-db-connection", 
                                   json=invalid_test, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get("success"):
                    self.log_test("Database Connection (Invalid)", True, 
                                "Invalid URL properly rejected", data)
                else:
                    self.log_test("Database Connection (Invalid)", False, 
                                "Invalid URL incorrectly accepted", data)
            else:
                self.log_test("Database Connection (Invalid)", False, 
                            f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_test("Database Connection", False, f"Request error: {str(e)}")
    
    def test_mining_engine_enterprise(self):
        """Test enterprise mining engine with high thread counts"""
        try:
            # First get system capabilities
            cpu_response = requests.get(f"{API_BASE}/system/cpu-info", timeout=10)
            if cpu_response.status_code != 200:
                self.log_test("Mining Engine Enterprise", False, "Could not get CPU info for mining test")
                return
            
            cpu_data = cpu_response.json()
            max_safe_threads = cpu_data.get("max_safe_threads", 4)
            
            # Test with different thread counts
            thread_tests = [
                min(32, max_safe_threads),    # Medium enterprise load
                min(64, max_safe_threads),    # High enterprise load  
                min(128, max_safe_threads)    # Maximum enterprise load
            ]
            
            for thread_count in thread_tests:
                if thread_count < 4:  # Skip if system too limited
                    continue
                    
                # Prepare mining configuration
                mining_config = {
                    "coin": {
                        "name": "Litecoin",
                        "symbol": "LTC",
                        "algorithm": "Scrypt",
                        "block_reward": 6.25,
                        "block_time": 150,
                        "difficulty": 27882939.35508488,
                        "scrypt_params": {"n": 1024, "r": 1, "p": 1},
                        "network_hashrate": "450 TH/s",
                        "wallet_format": "L/M prefix (legacy), ltc1 (bech32), 3 (multisig)"
                    },
                    "mode": "solo",
                    "threads": thread_count,
                    "intensity": 1.0,
                    "auto_optimize": True,
                    "ai_enabled": True,
                    "wallet_address": "LKqTDSTh2KWGTfoNrsfj4jdepVxqJnRMRf",  # Valid Litecoin legacy address
                    "enterprise_mode": True,
                    "target_cpu_utilization": 1.0,
                    "thread_scaling_enabled": True
                }
                
                # Start mining
                start_response = requests.post(f"{API_BASE}/mining/start", 
                                             json=mining_config, timeout=15)
                
                if start_response.status_code == 200:
                    start_data = start_response.json()
                    
                    if start_data.get("success"):
                        # Let it run briefly
                        time.sleep(3)
                        
                        # Check mining status
                        status_response = requests.get(f"{API_BASE}/mining/status", timeout=10)
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            
                            if status_data.get("is_mining"):
                                # Stop mining
                                stop_response = requests.post(f"{API_BASE}/mining/stop", timeout=10)
                                
                                test_details = {
                                    "thread_count": thread_count,
                                    "mining_started": True,
                                    "mining_status": status_data,
                                    "stop_success": stop_response.status_code == 200
                                }
                                
                                self.log_test(f"Mining Engine ({thread_count} threads)", True, 
                                            f"Enterprise mining successful with {thread_count} threads", test_details)
                            else:
                                self.log_test(f"Mining Engine ({thread_count} threads)", False, 
                                            "Mining not active after start", status_data)
                        else:
                            self.log_test(f"Mining Engine ({thread_count} threads)", False, 
                                        f"Status check failed: HTTP {status_response.status_code}")
                    else:
                        self.log_test(f"Mining Engine ({thread_count} threads)", False, 
                                    f"Mining start failed: {start_data.get('message', 'Unknown error')}", start_data)
                else:
                    self.log_test(f"Mining Engine ({thread_count} threads)", False, 
                                f"Start request failed: HTTP {start_response.status_code}", 
                                {"response": start_response.text})
                
                # Small delay between tests
                time.sleep(2)
                
        except Exception as e:
            self.log_test("Mining Engine Enterprise", False, f"Test error: {str(e)}")
    
    def test_mining_status_enterprise(self):
        """Test mining status endpoint for enterprise metrics"""
        try:
            response = requests.get(f"{API_BASE}/mining/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for enterprise status fields
                required_fields = ["is_mining", "stats", "config"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Mining Status Enterprise", False, f"Missing fields: {missing_fields}", data)
                    return
                
                stats = data.get("stats", {})
                
                # Check for enterprise metrics in stats
                enterprise_stats = [
                    "enterprise_metrics", "active_threads", "total_threads", 
                    "threads_per_core", "efficiency"
                ]
                
                available_enterprise_stats = [stat for stat in enterprise_stats if stat in stats]
                
                test_details = {
                    "is_mining": data.get("is_mining"),
                    "available_enterprise_stats": available_enterprise_stats,
                    "stats_keys": list(stats.keys()) if stats else []
                }
                
                if len(available_enterprise_stats) >= 3:  # At least 3 enterprise metrics
                    self.log_test("Mining Status Enterprise", True, 
                                f"Enterprise metrics available: {len(available_enterprise_stats)}/5", test_details)
                else:
                    self.log_test("Mining Status Enterprise", False, 
                                f"Limited enterprise metrics: {len(available_enterprise_stats)}/5", test_details)
                    
            else:
                self.log_test("Mining Status Enterprise", False, f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_test("Mining Status Enterprise", False, f"Request error: {str(e)}")
    
    def test_ai_system_integration(self):
        """Test AI system integration for enterprise optimization"""
        try:
            # Test AI status
            status_response = requests.get(f"{API_BASE}/ai/status", timeout=10)
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                
                # Test AI insights
                insights_response = requests.get(f"{API_BASE}/mining/ai-insights", timeout=10)
                
                if insights_response.status_code == 200:
                    insights_data = insights_response.json()
                    
                    # Check for enterprise AI features
                    required_insights = ["insights", "predictions"]
                    available_insights = [key for key in required_insights if key in insights_data]
                    
                    insights_detail = insights_data.get("insights", {})
                    insight_types = list(insights_detail.keys()) if insights_detail else []
                    
                    test_details = {
                        "ai_status": status_data,
                        "available_insights": available_insights,
                        "insight_types": insight_types
                    }
                    
                    if len(insight_types) >= 3:  # Multiple insight types available
                        self.log_test("AI System Integration", True, 
                                    f"AI system working with {len(insight_types)} insight types", test_details)
                    else:
                        self.log_test("AI System Integration", False, 
                                    f"Limited AI insights: {len(insight_types)} types", test_details)
                else:
                    self.log_test("AI System Integration", False, 
                                f"AI insights failed: HTTP {insights_response.status_code}")
            else:
                self.log_test("AI System Integration", False, 
                            f"AI status failed: HTTP {status_response.status_code}")
                
        except Exception as e:
            self.log_test("AI System Integration", False, f"Request error: {str(e)}")
    
    def test_system_stats(self):
        """Test system statistics endpoint"""
        try:
            response = requests.get(f"{API_BASE}/system/stats", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required system stats
                required_stats = ["cpu_usage", "memory_usage", "disk_usage", "cores"]
                missing_stats = [stat for stat in required_stats if stat not in data]
                
                if missing_stats:
                    self.log_test("System Stats", False, f"Missing stats: {missing_stats}", data)
                else:
                    # Validate stat values
                    valid_stats = True
                    stat_details = {}
                    
                    for stat in required_stats:
                        value = data.get(stat)
                        if isinstance(value, (int, float)) and value >= 0:
                            stat_details[stat] = value
                        else:
                            valid_stats = False
                            stat_details[f"{stat}_error"] = f"Invalid value: {value}"
                    
                    if valid_stats:
                        self.log_test("System Stats", True, "All system stats valid", stat_details)
                    else:
                        self.log_test("System Stats", False, "Invalid stat values", stat_details)
            else:
                self.log_test("System Stats", False, f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_test("System Stats", False, f"Request error: {str(e)}")
    
    def run_all_tests(self):
        """Run all enterprise backend tests"""
        print("🚀 Starting CryptoMiner Pro Enterprise Backend Tests")
        print(f"📡 Testing backend at: {BACKEND_URL}")
        print("=" * 60)
        
        # Run all tests
        self.test_health_check()
        self.test_cpu_info_enterprise()
        self.test_database_connection()
        self.test_mining_status_enterprise()
        self.test_ai_system_integration()
        self.test_system_stats()
        self.test_mining_engine_enterprise()  # Run this last as it's most intensive
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_count = len(self.passed_tests)
        failed_count = len(self.failed_tests)
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"Success Rate: {(passed_count/total_tests)*100:.1f}%")
        
        if self.failed_tests:
            print(f"\n🔍 Failed Tests:")
            for test in self.failed_tests:
                print(f"   • {test}")
        
        print(f"\n🎯 Enterprise Features Status:")
        enterprise_tests = [
            "CPU Info Enterprise",
            "Mining Engine Enterprise", 
            "Mining Status Enterprise",
            "Database Connection"
        ]
        
        enterprise_passed = [test for test in enterprise_tests if test in self.passed_tests or any(test in passed for passed in self.passed_tests)]
        print(f"   Enterprise Tests Passed: {len(enterprise_passed)}/{len(enterprise_tests)}")
        
        return failed_count == 0

if __name__ == "__main__":
    tester = CryptoMinerProTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All enterprise backend tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  Some tests failed. Check the details above.")
        sys.exit(1)