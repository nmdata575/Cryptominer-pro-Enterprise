#!/usr/bin/env python3
"""
CryptoMiner Pro Backend API Testing Suite
Tests all backend APIs after enterprise file consolidation
"""

import requests
import json
import time
import sys
import os
from typing import Dict, Any, List, Tuple

# Backend URL from environment
BACKEND_URL = "https://0aecbcf7-d390-4bac-b616-167712cf354b.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.session.timeout = 30
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_health_check(self) -> bool:
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ["status", "version", "edition", "ai_system", "mining_active"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Health Check API", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Verify V30 version and Enterprise edition
                if data.get("version") == "v30" and data.get("edition") == "Enterprise":
                    self.log_test("Health Check API", True, f"Status: {data['status']}, Version: {data['version']}, Edition: {data['edition']}")
                    return True
                else:
                    self.log_test("Health Check API", False, f"Expected v30/Enterprise, got {data.get('version')}/{data.get('edition')}")
                    return False
            else:
                self.log_test("Health Check API", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Health Check API", False, f"Exception: {str(e)}")
            return False
    
    def test_system_cpu_info(self) -> bool:
        """Test system CPU info endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/system/cpu-info")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ["physical_cores", "logical_cores", "max_safe_threads", "enterprise_mode"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("System CPU Info API", False, f"Missing fields: {missing_fields}")
                    return False
                
                cores = data.get("physical_cores", 0)
                threads = data.get("max_safe_threads", 0)
                enterprise = data.get("enterprise_mode", False)
                
                self.log_test("System CPU Info API", True, f"Cores: {cores}, Max threads: {threads}, Enterprise: {enterprise}")
                return True
            else:
                self.log_test("System CPU Info API", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("System CPU Info API", False, f"Exception: {str(e)}")
            return False
    
    def test_system_stats(self) -> bool:
        """Test system statistics endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/system/stats")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ["cpu_usage", "memory_usage", "disk_usage", "cores"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("System Stats API", False, f"Missing fields: {missing_fields}")
                    return False
                
                cpu = data.get("cpu_usage", 0)
                memory = data.get("memory_usage", 0)
                cores = data.get("cores", 0)
                
                self.log_test("System Stats API", True, f"CPU: {cpu}%, Memory: {memory}%, Cores: {cores}")
                return True
            else:
                self.log_test("System Stats API", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("System Stats API", False, f"Exception: {str(e)}")
            return False
    
    def test_mining_status(self) -> bool:
        """Test mining status endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/mining/status")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ["is_mining", "stats", "config"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Mining Status API", False, f"Missing fields: {missing_fields}")
                    return False
                
                is_mining = data.get("is_mining", False)
                stats = data.get("stats", {})
                
                self.log_test("Mining Status API", True, f"Mining: {is_mining}, Stats available: {len(stats) > 0}")
                return True
            else:
                self.log_test("Mining Status API", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Mining Status API", False, f"Exception: {str(e)}")
            return False
    
    def test_ai_insights(self) -> bool:
        """Test AI insights endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/mining/ai-insights")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for insights structure
                if "insights" in data:
                    insights = data["insights"]
                    expected_insights = [
                        "hash_pattern_prediction",
                        "network_difficulty_forecast", 
                        "optimization_suggestions",
                        "pool_performance_analysis",
                        "efficiency_recommendations"
                    ]
                    
                    available_insights = [insight for insight in expected_insights if insight in insights]
                    
                    if len(available_insights) >= 3:  # At least 3 insight types
                        self.log_test("AI Insights API", True, f"Available insights: {len(available_insights)}/5")
                        return True
                    else:
                        self.log_test("AI Insights API", False, f"Only {len(available_insights)}/5 insights available")
                        return False
                else:
                    self.log_test("AI Insights API", False, "No insights field in response")
                    return False
            else:
                self.log_test("AI Insights API", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("AI Insights API", False, f"Exception: {str(e)}")
            return False
    
    def test_coin_presets(self) -> bool:
        """Test coin presets endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/coins/presets")
            
            if response.status_code == 200:
                data = response.json()
                
                if "presets" in data:
                    presets = data["presets"]
                    preset_count = len(presets)
                    
                    if preset_count > 0:
                        self.log_test("Coin Presets API", True, f"Available presets: {preset_count}")
                        return True
                    else:
                        self.log_test("Coin Presets API", False, "No presets available")
                        return False
                else:
                    self.log_test("Coin Presets API", False, "No presets field in response")
                    return False
            else:
                self.log_test("Coin Presets API", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Coin Presets API", False, f"Exception: {str(e)}")
            return False
    
    def test_database_connection(self) -> bool:
        """Test database connection endpoint"""
        try:
            # Test with valid localhost connection
            test_data = {
                "database_url": "mongodb://localhost:27017"
            }
            
            response = self.session.post(f"{self.base_url}/test-db-connection", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    self.log_test("Database Connection API", True, f"Connection successful: {data.get('message')}")
                    return True
                else:
                    self.log_test("Database Connection API", False, f"Connection failed: {data.get('error')}")
                    return False
            else:
                self.log_test("Database Connection API", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Database Connection API", False, f"Exception: {str(e)}")
            return False
    
    def test_v30_license_validation(self) -> bool:
        """Test V30 license validation endpoint"""
        try:
            # Test with invalid license format
            test_data = {
                "license_key": "INVALID-LICENSE-KEY"
            }
            
            response = self.session.post(f"{self.base_url}/v30/license/validate", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return invalid for bad format
                if not data.get("valid"):
                    self.log_test("V30 License Validation API", True, f"Correctly rejected invalid license: {data.get('error')}")
                    return True
                else:
                    self.log_test("V30 License Validation API", False, "Should have rejected invalid license format")
                    return False
            else:
                self.log_test("V30 License Validation API", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("V30 License Validation API", False, f"Exception: {str(e)}")
            return False
    
    def test_v30_hardware_validation(self) -> bool:
        """Test V30 hardware validation endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/v30/hardware/validate")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ["meets_requirements", "validation_timestamp", "system_info", "requirements_check"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("V30 Hardware Validation API", False, f"Missing fields: {missing_fields}")
                    return False
                
                meets_req = data.get("meets_requirements", False)
                system_info = data.get("system_info", {})
                req_check = data.get("requirements_check", {})
                
                # Check if we have system info
                if "memory" in system_info and "cpu" in system_info:
                    memory_gb = system_info["memory"].get("total_gb", 0)
                    cpu_cores = system_info["cpu"].get("physical_cores", 0)
                    
                    self.log_test("V30 Hardware Validation API", True, 
                                f"Requirements met: {meets_req}, Memory: {memory_gb}GB, CPU: {cpu_cores} cores")
                    return True
                else:
                    self.log_test("V30 Hardware Validation API", False, "Missing system info details")
                    return False
            else:
                self.log_test("V30 Hardware Validation API", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("V30 Hardware Validation API", False, f"Exception: {str(e)}")
            return False
    
    def test_v30_system_initialization(self) -> bool:
        """Test V30 system initialization endpoint"""
        try:
            response = self.session.post(f"{self.base_url}/v30/system/initialize")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    features = data.get("features", [])
                    features_count = data.get("features_enabled", 0)
                    
                    self.log_test("V30 System Initialization API", True, 
                                f"Initialized with {features_count} features: {features[:3]}...")
                    return True
                else:
                    self.log_test("V30 System Initialization API", False, f"Initialization failed: {data.get('error')}")
                    return False
            else:
                self.log_test("V30 System Initialization API", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("V30 System Initialization API", False, f"Exception: {str(e)}")
            return False
    
    def test_v30_system_status(self) -> bool:
        """Test V30 system status endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/v30/system/status")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for status structure
                if "system_status" in data and "capabilities" in data:
                    system_status = data["system_status"]
                    capabilities = data["capabilities"]
                    
                    initialized = system_status.get("initialized", False)
                    version = system_status.get("version", "")
                    
                    # Check capabilities
                    expected_caps = ["distributed_mining", "gpu_acceleration", "license_management"]
                    available_caps = [cap for cap in expected_caps if capabilities.get(cap, False)]
                    
                    if len(available_caps) >= 2:  # At least 2 capabilities
                        self.log_test("V30 System Status API", True, 
                                    f"Initialized: {initialized}, Version: {version}, Capabilities: {len(available_caps)}/3")
                        return True
                    else:
                        self.log_test("V30 System Status API", False, f"Only {len(available_caps)}/3 capabilities available")
                        return False
                else:
                    self.log_test("V30 System Status API", False, "Missing status structure")
                    return False
            else:
                self.log_test("V30 System Status API", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("V30 System Status API", False, f"Exception: {str(e)}")
            return False
    
    def test_v30_nodes_list(self) -> bool:
        """Test V30 nodes list endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/v30/nodes/list")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ["nodes", "total", "active"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("V30 Nodes List API", False, f"Missing fields: {missing_fields}")
                    return False
                
                total_nodes = data.get("total", 0)
                active_nodes = data.get("active", 0)
                nodes = data.get("nodes", [])
                
                # In test environment, expect 0 remote nodes
                self.log_test("V30 Nodes List API", True, 
                            f"Total nodes: {total_nodes}, Active: {active_nodes}, Nodes list: {len(nodes)}")
                return True
            else:
                self.log_test("V30 Nodes List API", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("V30 Nodes List API", False, f"Exception: {str(e)}")
            return False
    
    def test_v30_comprehensive_stats(self) -> bool:
        """Test V30 comprehensive statistics endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/v30/stats/comprehensive")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for comprehensive stats structure
                if "system_status" in data and "server_info" in data and "capabilities" in data:
                    system_status = data["system_status"]
                    server_info = data["server_info"]
                    capabilities = data["capabilities"]
                    
                    hostname = server_info.get("hostname", "")
                    enterprise_features = server_info.get("enterprise_features", 0)
                    
                    self.log_test("V30 Comprehensive Stats API", True, 
                                f"Hostname: {hostname}, Enterprise features: {enterprise_features}, Capabilities: {len(capabilities)}")
                    return True
                else:
                    self.log_test("V30 Comprehensive Stats API", False, "Missing comprehensive stats structure")
                    return False
            else:
                self.log_test("V30 Comprehensive Stats API", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("V30 Comprehensive Stats API", False, f"Exception: {str(e)}")
            return False
    
    def test_saved_pools_api(self) -> bool:
        """Test saved pools CRUD operations"""
        try:
            # Test GET saved pools
            response = self.session.get(f"{self.base_url}/pools/saved")
            
            if response.status_code != 200:
                self.log_test("Saved Pools API", False, f"GET failed with HTTP {response.status_code}")
                return False
            
            data = response.json()
            if "pools" not in data or "count" not in data:
                self.log_test("Saved Pools API", False, "Missing pools or count field in GET response")
                return False
            
            initial_count = data["count"]
            
            # Test POST - Create new pool
            test_pool = {
                "name": f"Test Pool {int(time.time())}",
                "coin_symbol": "EFL",
                "wallet_address": "LaEni1U9jb4A38frAbjj3UHMzM6vrre8Dd",
                "pool_address": "stratum.luckydogpool.com",
                "pool_port": 7026,
                "pool_password": "x",
                "description": "Test pool for API validation"
            }
            
            response = self.session.post(f"{self.base_url}/pools/saved", json=test_pool)
            
            if response.status_code != 200:
                self.log_test("Saved Pools API", False, f"POST failed with HTTP {response.status_code}")
                return False
            
            create_data = response.json()
            if not create_data.get("success"):
                self.log_test("Saved Pools API", False, f"Pool creation failed: {create_data.get('message')}")
                return False
            
            pool_id = create_data.get("pool_id")
            if not pool_id:
                self.log_test("Saved Pools API", False, "No pool_id returned from creation")
                return False
            
            # Verify pool was created
            response = self.session.get(f"{self.base_url}/pools/saved")
            data = response.json()
            new_count = data["count"]
            
            if new_count != initial_count + 1:
                self.log_test("Saved Pools API", False, f"Pool count didn't increase: {initial_count} -> {new_count}")
                return False
            
            # Test DELETE - Remove the test pool
            response = self.session.delete(f"{self.base_url}/pools/saved/{pool_id}")
            
            if response.status_code != 200:
                self.log_test("Saved Pools API", False, f"DELETE failed with HTTP {response.status_code}")
                return False
            
            delete_data = response.json()
            if not delete_data.get("success"):
                self.log_test("Saved Pools API", False, f"Pool deletion failed: {delete_data.get('message')}")
                return False
            
            self.log_test("Saved Pools API", True, f"CRUD operations successful - Created and deleted pool {pool_id[:8]}...")
            return True
                
        except Exception as e:
            self.log_test("Saved Pools API", False, f"Exception: {str(e)}")
            return False
    
    def test_custom_coins_api(self) -> bool:
        """Test custom coins CRUD operations"""
        try:
            # Test GET custom coins
            response = self.session.get(f"{self.base_url}/coins/custom")
            
            if response.status_code != 200:
                self.log_test("Custom Coins API", False, f"GET failed with HTTP {response.status_code}")
                return False
            
            data = response.json()
            if "coins" not in data or "count" not in data:
                self.log_test("Custom Coins API", False, "Missing coins or count field in GET response")
                return False
            
            initial_count = data["count"]
            
            # Test POST - Create new custom coin
            test_coin = {
                "name": f"Test Coin {int(time.time())}",
                "symbol": f"TC{int(time.time()) % 10000}",
                "algorithm": "Scrypt",
                "block_reward": 50.0,
                "block_time": 120,
                "difficulty": 2000.0,
                "scrypt_params": {"n": 1024, "r": 1, "p": 1},
                "description": "Test coin for API validation"
            }
            
            response = self.session.post(f"{self.base_url}/coins/custom", json=test_coin)
            
            if response.status_code != 200:
                self.log_test("Custom Coins API", False, f"POST failed with HTTP {response.status_code}")
                return False
            
            create_data = response.json()
            if not create_data.get("success"):
                self.log_test("Custom Coins API", False, f"Coin creation failed: {create_data.get('message')}")
                return False
            
            coin_id = create_data.get("coin_id")
            if not coin_id:
                self.log_test("Custom Coins API", False, "No coin_id returned from creation")
                return False
            
            # Verify coin was created
            response = self.session.get(f"{self.base_url}/coins/custom")
            data = response.json()
            new_count = data["count"]
            
            if new_count != initial_count + 1:
                self.log_test("Custom Coins API", False, f"Coin count didn't increase: {initial_count} -> {new_count}")
                return False
            
            # Test GET all coins (preset + custom)
            response = self.session.get(f"{self.base_url}/coins/all")
            
            if response.status_code != 200:
                self.log_test("Custom Coins API", False, f"GET all coins failed with HTTP {response.status_code}")
                return False
            
            all_data = response.json()
            if "preset_coins" not in all_data or "custom_coins" not in all_data:
                self.log_test("Custom Coins API", False, "Missing preset_coins or custom_coins in GET all response")
                return False
            
            # Test DELETE - Remove the test coin
            response = self.session.delete(f"{self.base_url}/coins/custom/{coin_id}")
            
            if response.status_code != 200:
                self.log_test("Custom Coins API", False, f"DELETE failed with HTTP {response.status_code}")
                return False
            
            delete_data = response.json()
            if not delete_data.get("success"):
                self.log_test("Custom Coins API", False, f"Coin deletion failed: {delete_data.get('message')}")
                return False
            
            preset_count = len(all_data["preset_coins"])
            custom_count = len(all_data["custom_coins"])
            total_count = all_data["total_count"]
            
            self.log_test("Custom Coins API", True, 
                        f"CRUD operations successful - Preset: {preset_count}, Custom: {custom_count}, Total: {total_count}")
            return True
                
        except Exception as e:
            self.log_test("Custom Coins API", False, f"Exception: {str(e)}")
            return False
    
    def test_real_mining_start(self) -> bool:
        """Test real mining start with EFL pool"""
        try:
            # Real EFL pool configuration as specified in the review request
            mining_config = {
                "coin": {
                    "name": "Electronic Gulden", 
                    "symbol": "EFL",
                    "algorithm": "Scrypt",
                    "custom_pool_address": "stratum.luckydogpool.com",
                    "custom_pool_port": 7026
                },
                "wallet_address": "LaEni1U9jb4A38frAbjj3UHMzM6vrre8Dd",
                "threads": 4,
                "mode": "pool"
            }
            
            response = self.session.post(f"{self.base_url}/mining/start", json=mining_config)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    self.log_test("Real Mining Start API", True, 
                                f"Mining started successfully: {data.get('message')}")
                    return True
                else:
                    self.log_test("Real Mining Start API", False, 
                                f"Mining start failed: {data.get('message')}")
                    return False
            else:
                self.log_test("Real Mining Start API", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Real Mining Start API", False, f"Exception: {str(e)}")
            return False
    
    def test_real_mining_monitoring(self) -> bool:
        """Test real mining monitoring for sustained operation"""
        try:
            print("\n⏱️  Starting 5-minute real mining monitoring test...")
            print("   Checking mining status every 30 seconds for 10 cycles")
            
            monitoring_results = []
            
            for cycle in range(10):  # 10 cycles of 30 seconds = 5 minutes
                print(f"\n📊 Monitoring Cycle {cycle + 1}/10:")
                
                # Get mining status
                response = self.session.get(f"{self.base_url}/mining/status")
                
                if response.status_code == 200:
                    data = response.json()
                    is_mining = data.get("is_mining", False)
                    stats = data.get("stats", {})
                    
                    # Extract key metrics
                    hashrate = stats.get("hashrate", 0)
                    accepted_shares = stats.get("accepted_shares", 0)
                    uptime = stats.get("uptime", 0)
                    active_threads = stats.get("active_threads", 0)
                    
                    cycle_result = {
                        "cycle": cycle + 1,
                        "is_mining": is_mining,
                        "hashrate": hashrate,
                        "accepted_shares": accepted_shares,
                        "uptime": uptime,
                        "active_threads": active_threads
                    }
                    
                    monitoring_results.append(cycle_result)
                    
                    print(f"   ⛏️  Mining Active: {is_mining}")
                    print(f"   📈 Hashrate: {hashrate:.2f} H/s")
                    print(f"   ✅ Accepted Shares: {accepted_shares}")
                    print(f"   ⏰ Uptime: {uptime:.1f}s")
                    print(f"   🧵 Active Threads: {active_threads}")
                    
                    if not is_mining:
                        self.log_test("Real Mining Monitoring", False, 
                                    f"Mining stopped unexpectedly at cycle {cycle + 1}")
                        return False
                else:
                    self.log_test("Real Mining Monitoring", False, 
                                f"Status check failed at cycle {cycle + 1}: HTTP {response.status_code}")
                    return False
                
                # Wait 30 seconds before next check (except last cycle)
                if cycle < 9:
                    time.sleep(30)
            
            # Analyze results
            mining_stayed_active = all(result["is_mining"] for result in monitoring_results)
            final_shares = monitoring_results[-1]["accepted_shares"]
            final_uptime = monitoring_results[-1]["uptime"]
            
            if mining_stayed_active and final_uptime >= 270:  # At least 4.5 minutes
                self.log_test("Real Mining Monitoring", True, 
                            f"Mining stayed active for {final_uptime:.1f}s, {final_shares} shares accepted")
                return True
            else:
                self.log_test("Real Mining Monitoring", False, 
                            f"Mining instability detected - Active: {mining_stayed_active}, Uptime: {final_uptime:.1f}s")
                return False
                
        except Exception as e:
            self.log_test("Real Mining Monitoring", False, f"Exception: {str(e)}")
            return False
    
    def test_real_mining_statistics(self) -> bool:
        """Test real mining statistics accuracy"""
        try:
            response = self.session.get(f"{self.base_url}/mining/status")
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get("stats", {})
                
                # Check for required statistics fields
                required_stats = ["hashrate", "accepted_shares", "uptime", "active_threads"]
                missing_stats = [stat for stat in required_stats if stat not in stats]
                
                if missing_stats:
                    self.log_test("Real Mining Statistics", False, f"Missing stats: {missing_stats}")
                    return False
                
                # Validate statistics values
                hashrate = stats.get("hashrate", 0)
                accepted_shares = stats.get("accepted_shares", 0)
                uptime = stats.get("uptime", 0)
                
                # Check if statistics are reasonable
                if hashrate >= 0 and accepted_shares >= 0 and uptime >= 0:
                    # Calculate acceptance rate if shares found
                    shares_found = stats.get("blocks_found", 0)  # Using blocks_found as shares_found
                    acceptance_rate = (accepted_shares / shares_found * 100) if shares_found > 0 else 0
                    
                    self.log_test("Real Mining Statistics", True, 
                                f"Hashrate: {hashrate:.2f} H/s, Shares: {accepted_shares}, "
                                f"Acceptance: {acceptance_rate:.1f}%, Uptime: {uptime:.1f}s")
                    return True
                else:
                    self.log_test("Real Mining Statistics", False, 
                                f"Invalid statistics values: hashrate={hashrate}, shares={accepted_shares}, uptime={uptime}")
                    return False
            else:
                self.log_test("Real Mining Statistics", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Real Mining Statistics", False, f"Exception: {str(e)}")
            return False
    
    def test_real_mining_stop(self) -> bool:
        """Test real mining stop functionality"""
        try:
            response = self.session.post(f"{self.base_url}/mining/stop")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    # Wait a moment for mining to fully stop
                    time.sleep(2)
                    
                    # Verify mining has stopped
                    status_response = self.session.get(f"{self.base_url}/mining/status")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        is_mining = status_data.get("is_mining", True)
                        
                        if not is_mining:
                            self.log_test("Real Mining Stop API", True, 
                                        f"Mining stopped successfully: {data.get('message')}")
                            return True
                        else:
                            self.log_test("Real Mining Stop API", False, 
                                        "Mining status still shows active after stop command")
                            return False
                    else:
                        self.log_test("Real Mining Stop API", False, 
                                    f"Status check failed: HTTP {status_response.status_code}")
                        return False
                else:
                    self.log_test("Real Mining Stop API", False, 
                                f"Stop command failed: {data.get('message')}")
                    return False
            else:
                self.log_test("Real Mining Stop API", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Real Mining Stop API", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all backend API tests with focus on REAL MINING"""
        print("🚀 Starting CryptoMiner Pro Backend API Tests")
        print(f"📡 Testing backend at: {self.base_url}")
        print("🎯 FOCUS: Real Mining Functionality Testing")
        print("=" * 60)
        
        # Core API Tests (Quick verification)
        print("\n📋 Core API Tests (Quick Check):")
        self.test_health_check()
        self.test_mining_status()
        
        # CRITICAL: Real Mining Tests
        print("\n⛏️  REAL MINING TESTS (CRITICAL):")
        print("🔥 Testing FIXED real mining functionality after asyncio event loop fix")
        
        # Test 1: Start Real Mining
        mining_started = self.test_real_mining_start()
        
        if mining_started:
            # Test 2: Monitor Mining for 5+ minutes
            mining_sustained = self.test_real_mining_monitoring()
            
            # Test 3: Check Statistics
            self.test_real_mining_statistics()
            
            # Test 4: Stop Mining
            self.test_real_mining_stop()
        else:
            print("❌ Real mining failed to start - skipping monitoring tests")
            self.log_test("Real Mining Monitoring", False, "Skipped - mining failed to start")
            self.log_test("Real Mining Statistics", False, "Skipped - mining failed to start") 
            self.log_test("Real Mining Stop API", False, "Skipped - mining failed to start")
        
        # Additional Core Tests
        print("\n📋 Additional Core API Tests:")
        self.test_system_cpu_info()
        self.test_system_stats()
        self.test_ai_insights()
        self.test_coin_presets()
        self.test_database_connection()
        
        # V30 Enterprise Tests (Abbreviated)
        print("\n🏢 V30 Enterprise API Tests (Key Tests):")
        self.test_v30_license_validation()
        self.test_v30_hardware_validation()
        self.test_v30_system_initialization()
        
        # Data Management Tests
        print("\n💾 Data Management API Tests:")
        self.test_saved_pools_api()
        self.test_custom_coins_api()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "test_results": self.test_results
        }

def main():
    """Main test execution"""
    tester = BackendTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results["failed_tests"] == 0:
        print("\n🎉 All tests passed! Backend APIs are working correctly after consolidation.")
        sys.exit(0)
    else:
        print(f"\n⚠️  {results['failed_tests']} test(s) failed. Check the details above.")
        sys.exit(1)

if __name__ == "__main__":
    main()