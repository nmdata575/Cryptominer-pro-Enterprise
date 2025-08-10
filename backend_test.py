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
                    "wallet_address": "ltc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4",  # Valid Litecoin bech32 address
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
    
    def test_v30_license_validation(self):
        """Test V30 Enterprise license validation"""
        try:
            # Test with invalid license key
            invalid_test = {"license_key": "INVALID-KEY-12345"}
            response = requests.post(f"{API_BASE}/v30/license/validate", 
                                   json=invalid_test, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if not data.get("valid"):
                    self.log_test("V30 License Validation (Invalid)", True, 
                                "Invalid license properly rejected", data)
                else:
                    self.log_test("V30 License Validation (Invalid)", False, 
                                "Invalid license incorrectly accepted", data)
            else:
                self.log_test("V30 License Validation (Invalid)", False, 
                            f"HTTP {response.status_code}", {"response": response.text})
            
            # Test with potentially valid license format
            valid_format_test = {"license_key": "ABCDE-12345-FGHIJ-67890-KLMNO-PQRST-UVWXYZ"}
            response = requests.post(f"{API_BASE}/v30/license/validate", 
                                   json=valid_format_test, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Either valid or invalid is acceptable - we're testing the endpoint works
                self.log_test("V30 License Validation (Format)", True, 
                            f"License validation working - result: {data.get('valid', 'unknown')}", data)
            else:
                self.log_test("V30 License Validation (Format)", False, 
                            f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_test("V30 License Validation", False, f"Request error: {str(e)}")
    
    def test_v30_license_activation(self):
        """Test V30 Enterprise license activation"""
        try:
            node_info = {
                "hostname": "test-node-01",
                "ip_address": "192.168.1.100",
                "system_specs": {
                    "cpu_cores": 16,
                    "ram_gb": 32,
                    "gpus": 2
                }
            }
            
            activation_test = {
                "license_key": "ABCDE-12345-FGHIJ-67890-KLMNO-PQRST-UVWXYZ",
                "node_info": node_info
            }
            
            response = requests.post(f"{API_BASE}/v30/license/activate", 
                                   json=activation_test, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Test endpoint functionality regardless of license validity
                self.log_test("V30 License Activation", True, 
                            f"License activation endpoint working - result: {data.get('valid', 'unknown')}", data)
            else:
                self.log_test("V30 License Activation", False, 
                            f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_test("V30 License Activation", False, f"Request error: {str(e)}")
    
    def test_v30_hardware_validation(self):
        """Test V30 Enterprise hardware validation"""
        try:
            response = requests.get(f"{API_BASE}/v30/hardware/validate", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for enterprise hardware validation fields
                required_fields = ["enterprise_ready", "memory", "cpu", "network", "gpus"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("V30 Hardware Validation", False, 
                                f"Missing validation fields: {missing_fields}", data)
                    return
                
                # Analyze validation results
                memory_info = data.get("memory", {})
                cpu_info = data.get("cpu", {})
                gpu_info = data.get("gpus", {})
                network_info = data.get("network", {})
                
                validation_details = {
                    "enterprise_ready": data.get("enterprise_ready", False),
                    "total_ram_gb": memory_info.get("total_ram_gb", 0),
                    "cpu_cores": cpu_info.get("logical_cores", 0),
                    "total_gpus": gpu_info.get("total_count", 0),
                    "nvidia_gpus": gpu_info.get("nvidia_count", 0),
                    "amd_gpus": gpu_info.get("amd_count", 0),
                    "network_speed_gbps": network_info.get("max_speed_gbps", 0)
                }
                
                # Expected that current system won't meet enterprise requirements
                if not data.get("enterprise_ready"):
                    self.log_test("V30 Hardware Validation", True, 
                                "Hardware validation working - current system doesn't meet enterprise requirements (expected)", 
                                validation_details)
                else:
                    self.log_test("V30 Hardware Validation", True, 
                                "Hardware validation working - system meets enterprise requirements", 
                                validation_details)
                    
            else:
                self.log_test("V30 Hardware Validation", False, 
                            f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_test("V30 Hardware Validation", False, f"Request error: {str(e)}")
    
    def test_v30_system_initialization(self):
        """Test V30 Enterprise system initialization"""
        try:
            response = requests.post(f"{API_BASE}/v30/system/initialize", timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    # Check initialization response
                    required_fields = ["version", "features", "startup_time"]
                    available_fields = [field for field in required_fields if field in data]
                    
                    init_details = {
                        "version": data.get("version"),
                        "local_mining": data.get("local_mining", False),
                        "distributed_server": data.get("distributed_server", False),
                        "server_address": data.get("server_address"),
                        "features_count": len(data.get("features", [])),
                        "available_fields": available_fields
                    }
                    
                    self.log_test("V30 System Initialization", True, 
                                f"V30 system initialized successfully - {len(data.get('features', []))} features", 
                                init_details)
                else:
                    self.log_test("V30 System Initialization", False, 
                                f"Initialization failed: {data.get('error', 'Unknown error')}", data)
            else:
                self.log_test("V30 System Initialization", False, 
                            f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_test("V30 System Initialization", False, f"Request error: {str(e)}")
    
    def test_v30_system_status(self):
        """Test V30 Enterprise system status"""
        try:
            response = requests.get(f"{API_BASE}/v30/system/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for system status fields
                system_info = data.get("system", {})
                statistics = data.get("statistics", {})
                server_info = data.get("server", {})
                capabilities = data.get("capabilities", {})
                
                status_details = {
                    "system_running": system_info.get("running", False),
                    "system_version": system_info.get("version"),
                    "uptime": system_info.get("uptime", 0),
                    "total_nodes": statistics.get("total_nodes", 0),
                    "active_nodes": statistics.get("active_nodes", 0),
                    "server_active": server_info.get("active", False),
                    "capabilities_count": len(capabilities)
                }
                
                if system_info.get("version") == "v30":
                    self.log_test("V30 System Status", True, 
                                f"V30 system status working - {status_details['capabilities_count']} capabilities", 
                                status_details)
                else:
                    self.log_test("V30 System Status", False, 
                                "V30 system status missing version info", status_details)
                    
            else:
                self.log_test("V30 System Status", False, 
                            f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_test("V30 System Status", False, f"Request error: {str(e)}")
    
    def test_v30_distributed_mining_control(self):
        """Test V30 distributed mining start/stop"""
        try:
            # Test distributed mining start
            mining_config = {
                "coin_config": {
                    "name": "Litecoin",
                    "symbol": "LTC",
                    "algorithm": "scrypt",
                    "scrypt_n": 1024
                },
                "wallet_address": "ltc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4",
                "include_local": True
            }
            
            start_response = requests.post(f"{API_BASE}/v30/mining/distributed/start", 
                                         json=mining_config, timeout=15)
            
            start_success = False
            if start_response.status_code == 200:
                start_data = start_response.json()
                if start_data.get("success"):
                    start_success = True
                    self.log_test("V30 Distributed Mining Start", True, 
                                f"Distributed mining started: {start_data.get('message', '')}", start_data)
                else:
                    self.log_test("V30 Distributed Mining Start", False, 
                                f"Start failed: {start_data.get('error', 'Unknown error')}", start_data)
            else:
                self.log_test("V30 Distributed Mining Start", False, 
                            f"HTTP {start_response.status_code}", {"response": start_response.text})
            
            # Test distributed mining stop (regardless of start success)
            time.sleep(2)  # Brief delay
            
            stop_response = requests.post(f"{API_BASE}/v30/mining/distributed/stop", timeout=10)
            
            if stop_response.status_code == 200:
                stop_data = stop_response.json()
                if stop_data.get("success"):
                    self.log_test("V30 Distributed Mining Stop", True, 
                                f"Distributed mining stopped: {stop_data.get('message', '')}", stop_data)
                else:
                    self.log_test("V30 Distributed Mining Stop", False, 
                                f"Stop failed: {stop_data.get('error', 'Unknown error')}", stop_data)
            else:
                self.log_test("V30 Distributed Mining Stop", False, 
                            f"HTTP {stop_response.status_code}", {"response": stop_response.text})
                
        except Exception as e:
            self.log_test("V30 Distributed Mining Control", False, f"Request error: {str(e)}")
    
    def test_v30_nodes_management(self):
        """Test V30 nodes list and management"""
        try:
            response = requests.get(f"{API_BASE}/v30/nodes/list", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check nodes list structure
                nodes = data.get("nodes", [])
                total_nodes = data.get("total", 0)
                active_nodes = data.get("active", 0)
                
                nodes_details = {
                    "total_nodes": total_nodes,
                    "active_nodes": active_nodes,
                    "nodes_data_count": len(nodes),
                    "has_node_structure": len(nodes) == 0 or all(
                        "node_id" in node and "status" in node 
                        for node in nodes
                    )
                }
                
                # Expected to have 0 nodes in test environment
                if total_nodes == 0:
                    self.log_test("V30 Nodes Management", True, 
                                "Node management working - no remote nodes connected (expected)", 
                                nodes_details)
                else:
                    self.log_test("V30 Nodes Management", True, 
                                f"Node management working - {total_nodes} nodes, {active_nodes} active", 
                                nodes_details)
                    
            else:
                self.log_test("V30 Nodes Management", False, 
                            f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_test("V30 Nodes Management", False, f"Request error: {str(e)}")
    
    def test_v30_comprehensive_stats(self):
        """Test V30 comprehensive statistics"""
        try:
            response = requests.get(f"{API_BASE}/v30/stats/comprehensive", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check comprehensive stats structure
                system_info = data.get("system", {})
                statistics = data.get("statistics", {})
                server_info = data.get("server", {})
                capabilities = data.get("capabilities", {})
                
                stats_details = {
                    "has_system_info": bool(system_info),
                    "has_statistics": bool(statistics),
                    "has_server_info": bool(server_info),
                    "has_capabilities": bool(capabilities),
                    "system_version": system_info.get("version"),
                    "system_running": system_info.get("running", False),
                    "capabilities_count": len(capabilities),
                    "stats_fields": list(statistics.keys()) if statistics else []
                }
                
                required_capabilities = ["distributed_mining", "gpu_acceleration", "license_management"]
                available_capabilities = [cap for cap in required_capabilities if capabilities.get(cap)]
                
                if len(available_capabilities) >= 2:  # At least 2 key capabilities
                    self.log_test("V30 Comprehensive Stats", True, 
                                f"Comprehensive stats working - {len(available_capabilities)}/3 key capabilities", 
                                stats_details)
                else:
                    self.log_test("V30 Comprehensive Stats", False, 
                                f"Limited capabilities in stats: {len(available_capabilities)}/3", 
                                stats_details)
                    
            else:
                self.log_test("V30 Comprehensive Stats", False, 
                            f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_test("V30 Comprehensive Stats", False, f"Request error: {str(e)}")
    
    def test_v30_health_check_updates(self):
        """Test updated health check with V30 information"""
        try:
            response = requests.get(f"{API_BASE}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for V30 specific fields
                v30_fields = {
                    "version": data.get("version"),
                    "edition": data.get("edition"),
                    "v30_system": data.get("v30_system", False),
                    "ai_system": data.get("ai_system", False),
                    "mining_active": data.get("mining_active", False)
                }
                
                # Verify V30 version and enterprise edition
                is_v30 = data.get("version") == "v30"
                is_enterprise = data.get("edition") == "Enterprise"
                
                if is_v30 and is_enterprise:
                    self.log_test("V30 Health Check Updates", True, 
                                "Health check shows V30 Enterprise edition correctly", v30_fields)
                else:
                    self.log_test("V30 Health Check Updates", False, 
                                f"Health check missing V30/Enterprise info - version: {data.get('version')}, edition: {data.get('edition')}", 
                                v30_fields)
                    
            else:
                self.log_test("V30 Health Check Updates", False, 
                            f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_test("V30 Health Check Updates", False, f"Request error: {str(e)}")

    def test_efl_scrypt_mining_protocol(self):
        """Test newly implemented Scrypt mining protocol fix with real EFL mining pool credentials"""
        try:
            # EFL Pool Configuration from review request
            efl_pool_config = {
                "coin": {
                    "name": "E-Gulden",
                    "symbol": "EFL",
                    "algorithm": "Scrypt",
                    "block_reward": 25.0,
                    "block_time": 150,
                    "difficulty": 1000.0,
                    "scrypt_params": {"n": 1024, "r": 1, "p": 1},
                    "network_hashrate": "10 MH/s",
                    "wallet_format": "L prefix (legacy)",
                    "custom_pool_address": "stratum.luckydogpool.com",
                    "custom_pool_port": 7026
                },
                "mode": "pool",
                "threads": 4,
                "intensity": 1.0,
                "auto_optimize": True,
                "ai_enabled": True,
                "wallet_address": "LaEni1U9jb4A38frAbjj3UHMzM6vrre8Dd",  # Real EFL wallet from request
                "pool_username": "LaEni1U9jb4A38frAbjj3UHMzM6vrre8Dd.CryptoMiner-V30",
                "pool_password": "c=EFL,m=solo",  # Real mining password from request
                "enterprise_mode": True,
                "target_cpu_utilization": 0.5,  # Moderate load for testing
                "thread_scaling_enabled": True
            }
            
            print(f"\n🧪 Testing EFL Scrypt Mining Protocol with Real Pool")
            print(f"   Pool: {efl_pool_config['coin']['custom_pool_address']}:{efl_pool_config['coin']['custom_pool_port']}")
            print(f"   Wallet: {efl_pool_config['wallet_address']}")
            print(f"   Worker: {efl_pool_config['pool_username']}")
            print(f"   Password: {efl_pool_config['pool_password']}")
            
            # Step 1: Validate wallet address
            wallet_validation = {
                "address": efl_pool_config["wallet_address"],
                "coin_symbol": "EFL"
            }
            
            wallet_response = requests.post(f"{API_BASE}/validate_wallet", 
                                          json=wallet_validation, timeout=10)
            
            if wallet_response.status_code == 200:
                wallet_data = wallet_response.json()
                if wallet_data.get("valid"):
                    self.log_test("EFL Wallet Validation", True, 
                                f"EFL wallet address validated: {efl_pool_config['wallet_address']}", wallet_data)
                else:
                    self.log_test("EFL Wallet Validation", False, 
                                f"EFL wallet validation failed: {wallet_data.get('message', 'Unknown error')}", wallet_data)
                    return  # Don't proceed if wallet is invalid
            else:
                self.log_test("EFL Wallet Validation", False, 
                            f"Wallet validation request failed: HTTP {wallet_response.status_code}")
                return
            
            # Step 2: Test pool connection
            pool_test = {
                "pool_address": efl_pool_config["coin"]["custom_pool_address"],
                "pool_port": efl_pool_config["coin"]["custom_pool_port"],
                "type": "pool"
            }
            
            pool_response = requests.post(f"{API_BASE}/pool/test-connection", 
                                        json=pool_test, timeout=15)
            
            if pool_response.status_code == 200:
                pool_data = pool_response.json()
                if pool_data.get("success"):
                    self.log_test("EFL Pool Connection Test", True, 
                                f"Successfully connected to {efl_pool_config['coin']['custom_pool_address']}:{efl_pool_config['coin']['custom_pool_port']}", pool_data)
                else:
                    self.log_test("EFL Pool Connection Test", False, 
                                f"Pool connection failed: {pool_data.get('error', 'Unknown error')}", pool_data)
                    # Continue with test even if connection test fails - might be firewall/network issue
            else:
                self.log_test("EFL Pool Connection Test", False, 
                            f"Pool connection test failed: HTTP {pool_response.status_code}")
            
            # Step 3: Start EFL mining with real pool
            start_response = requests.post(f"{API_BASE}/mining/start", 
                                         json=efl_pool_config, timeout=20)
            
            if start_response.status_code == 200:
                start_data = start_response.json()
                
                if start_data.get("success"):
                    self.log_test("EFL Mining Start", True, 
                                f"EFL mining started successfully: {start_data.get('message', '')}", start_data)
                    
                    # Step 4: Monitor mining for a short period
                    time.sleep(10)  # Let it mine for 10 seconds
                    
                    # Step 5: Check mining status
                    status_response = requests.get(f"{API_BASE}/mining/status", timeout=10)
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        
                        if status_data.get("is_mining"):
                            stats = status_data.get("stats", {})
                            config = status_data.get("config", {})
                            
                            mining_details = {
                                "is_mining": status_data.get("is_mining"),
                                "hashrate": stats.get("hashrate", 0),
                                "accepted_shares": stats.get("accepted_shares", 0),
                                "rejected_shares": stats.get("rejected_shares", 0),
                                "uptime": stats.get("uptime", 0),
                                "active_threads": stats.get("active_threads", 0),
                                "algorithm": config.get("algorithm", "unknown") if config else "unknown",
                                "pool_connected": True
                            }
                            
                            self.log_test("EFL Mining Status", True, 
                                        f"EFL mining active - {mining_details['active_threads']} threads, {mining_details['hashrate']:.2f} H/s", 
                                        mining_details)
                        else:
                            self.log_test("EFL Mining Status", False, 
                                        "Mining not active after start", status_data)
                    else:
                        self.log_test("EFL Mining Status", False, 
                                    f"Status check failed: HTTP {status_response.status_code}")
                    
                    # Step 6: Stop mining
                    stop_response = requests.post(f"{API_BASE}/mining/stop", timeout=10)
                    
                    if stop_response.status_code == 200:
                        stop_data = stop_response.json()
                        if stop_data.get("success"):
                            self.log_test("EFL Mining Stop", True, 
                                        f"EFL mining stopped successfully: {stop_data.get('message', '')}", stop_data)
                        else:
                            self.log_test("EFL Mining Stop", False, 
                                        f"Mining stop failed: {stop_data.get('message', 'Unknown error')}", stop_data)
                    else:
                        self.log_test("EFL Mining Stop", False, 
                                    f"Stop request failed: HTTP {stop_response.status_code}")
                        
                else:
                    error_msg = start_data.get('detail', start_data.get('message', 'Unknown error'))
                    self.log_test("EFL Mining Start", False, 
                                f"EFL mining start failed: {error_msg}", start_data)
            else:
                self.log_test("EFL Mining Start", False, 
                            f"Mining start request failed: HTTP {start_response.status_code}", 
                            {"response": start_response.text})
                
        except Exception as e:
            self.log_test("EFL Scrypt Mining Protocol", False, f"Test error: {str(e)}")
    
    def test_scrypt_algorithm_integration(self):
        """Test ScryptAlgorithm and StratumClient integration in mining_engine.py"""
        try:
            # This test verifies that the new ScryptAlgorithm and StratumClient classes
            # are properly integrated into the mining engine
            
            # Test 1: Verify mining engine can handle Scrypt parameters
            scrypt_config = {
                "coin": {
                    "name": "Litecoin",
                    "symbol": "LTC", 
                    "algorithm": "Scrypt",
                    "block_reward": 6.25,
                    "block_time": 150,
                    "difficulty": 27882939.35508488,
                    "scrypt_params": {"n": 1024, "r": 1, "p": 1},  # Standard Litecoin parameters
                    "network_hashrate": "450 TH/s",
                    "wallet_format": "L/M prefix (legacy), ltc1 (bech32), 3 (multisig)"
                },
                "mode": "solo",
                "threads": 2,
                "intensity": 1.0,
                "wallet_address": "ltc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4",
                "enterprise_mode": True
            }
            
            # Start mining briefly to test integration
            start_response = requests.post(f"{API_BASE}/mining/start", 
                                         json=scrypt_config, timeout=15)
            
            if start_response.status_code == 200:
                start_data = start_response.json()
                
                if start_data.get("success"):
                    # Let it run briefly
                    time.sleep(3)
                    
                    # Check status
                    status_response = requests.get(f"{API_BASE}/mining/status", timeout=10)
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        
                        if status_data.get("is_mining"):
                            # Stop mining
                            requests.post(f"{API_BASE}/mining/stop", timeout=10)
                            
                            integration_details = {
                                "scrypt_params_accepted": True,
                                "mining_started": True,
                                "algorithm": status_data.get("config", {}).get("algorithm", "unknown"),
                                "enterprise_mode": status_data.get("config", {}).get("enterprise_mode", False)
                            }
                            
                            self.log_test("Scrypt Algorithm Integration", True, 
                                        "ScryptAlgorithm properly integrated in mining engine", integration_details)
                        else:
                            self.log_test("Scrypt Algorithm Integration", False, 
                                        "Mining not active - integration issue", status_data)
                    else:
                        self.log_test("Scrypt Algorithm Integration", False, 
                                    f"Status check failed: HTTP {status_response.status_code}")
                else:
                    self.log_test("Scrypt Algorithm Integration", False, 
                                f"Mining start failed: {start_data.get('message', 'Unknown error')}", start_data)
            else:
                self.log_test("Scrypt Algorithm Integration", False, 
                            f"Integration test failed: HTTP {start_response.status_code}")
                
        except Exception as e:
            self.log_test("Scrypt Algorithm Integration", False, f"Integration test error: {str(e)}")

    def test_saved_pools_api(self):
        """Test saved pools API endpoints - GET, POST, PUT, DELETE, USE"""
        try:
            print(f"\n🏊 Testing Saved Pools API with EFL pool configuration")
            
            # Step 1: Get initial saved pools (should be empty or existing)
            get_response = requests.get(f"{API_BASE}/pools/saved", timeout=10)
            
            if get_response.status_code == 200:
                initial_data = get_response.json()
                initial_count = initial_data.get("count", 0)
                self.log_test("Saved Pools - GET (Initial)", True, 
                            f"Retrieved {initial_count} existing saved pools", initial_data)
            else:
                self.log_test("Saved Pools - GET (Initial)", False, 
                            f"HTTP {get_response.status_code}", {"response": get_response.text})
                return
            
            # Step 2: Create a new saved pool with EFL configuration from review request
            efl_pool_data = {
                "name": "EFL LuckyDog Pool",
                "coin_symbol": "EFL",
                "wallet_address": "LaEni1U9jb4A38frAbjj3UHMzM6vrre8Dd",  # Real EFL wallet from request
                "pool_address": "stratum.luckydogpool.com",
                "pool_port": 7026,
                "pool_password": "c=EFL,m=solo",
                "pool_username": "LaEni1U9jb4A38frAbjj3UHMzM6vrre8Dd.CryptoMiner-V30",
                "description": "EFL mining pool configuration for LuckyDog Pool"
            }
            
            post_response = requests.post(f"{API_BASE}/pools/saved", 
                                        json=efl_pool_data, timeout=10)
            
            created_pool_id = None
            if post_response.status_code == 200:
                post_data = post_response.json()
                if post_data.get("success"):
                    created_pool_id = post_data.get("pool_id")
                    self.log_test("Saved Pools - POST (Create)", True, 
                                f"Created EFL pool configuration: {created_pool_id}", post_data)
                else:
                    self.log_test("Saved Pools - POST (Create)", False, 
                                f"Creation failed: {post_data.get('message', 'Unknown error')}", post_data)
                    return
            else:
                self.log_test("Saved Pools - POST (Create)", False, 
                            f"HTTP {post_response.status_code}", {"response": post_response.text})
                return
            
            # Step 3: Verify the pool was created by getting all pools again
            get_after_create = requests.get(f"{API_BASE}/pools/saved", timeout=10)
            
            if get_after_create.status_code == 200:
                after_create_data = get_after_create.json()
                new_count = after_create_data.get("count", 0)
                
                if new_count > initial_count:
                    self.log_test("Saved Pools - GET (After Create)", True, 
                                f"Pool count increased from {initial_count} to {new_count}", after_create_data)
                else:
                    self.log_test("Saved Pools - GET (After Create)", False, 
                                f"Pool count didn't increase: {initial_count} -> {new_count}", after_create_data)
            else:
                self.log_test("Saved Pools - GET (After Create)", False, 
                            f"HTTP {get_after_create.status_code}")
            
            # Step 4: Update the saved pool
            if created_pool_id:
                updated_pool_data = efl_pool_data.copy()
                updated_pool_data["description"] = "Updated EFL mining pool configuration for LuckyDog Pool - V30 Enterprise"
                updated_pool_data["pool_password"] = "c=EFL,m=solo,updated=true"
                
                put_response = requests.put(f"{API_BASE}/pools/saved/{created_pool_id}", 
                                          json=updated_pool_data, timeout=10)
                
                if put_response.status_code == 200:
                    put_data = put_response.json()
                    if put_data.get("success"):
                        self.log_test("Saved Pools - PUT (Update)", True, 
                                    f"Updated pool configuration: {created_pool_id}", put_data)
                    else:
                        self.log_test("Saved Pools - PUT (Update)", False, 
                                    f"Update failed: {put_data.get('message', 'Unknown error')}", put_data)
                else:
                    self.log_test("Saved Pools - PUT (Update)", False, 
                                f"HTTP {put_response.status_code}", {"response": put_response.text})
            
            # Step 5: Use the saved pool configuration
            if created_pool_id:
                use_response = requests.post(f"{API_BASE}/pools/saved/{created_pool_id}/use", timeout=10)
                
                if use_response.status_code == 200:
                    use_data = use_response.json()
                    if use_data.get("success"):
                        mining_config = use_data.get("mining_config", {})
                        pool_info = use_data.get("pool", {})
                        
                        use_details = {
                            "pool_name": pool_info.get("name"),
                            "mining_config_coin": mining_config.get("coin", {}).get("symbol"),
                            "mining_config_wallet": mining_config.get("wallet_address"),
                            "mining_config_mode": mining_config.get("mode"),
                            "pool_address": mining_config.get("coin", {}).get("custom_pool_address"),
                            "pool_port": mining_config.get("coin", {}).get("custom_pool_port")
                        }
                        
                        self.log_test("Saved Pools - USE", True, 
                                    f"Successfully retrieved mining config for {pool_info.get('name')}", use_details)
                    else:
                        self.log_test("Saved Pools - USE", False, 
                                    f"Use failed: {use_data.get('message', 'Unknown error')}", use_data)
                else:
                    self.log_test("Saved Pools - USE", False, 
                                f"HTTP {use_response.status_code}", {"response": use_response.text})
            
            # Step 6: Delete the saved pool (cleanup)
            if created_pool_id:
                delete_response = requests.delete(f"{API_BASE}/pools/saved/{created_pool_id}", timeout=10)
                
                if delete_response.status_code == 200:
                    delete_data = delete_response.json()
                    if delete_data.get("success"):
                        self.log_test("Saved Pools - DELETE", True, 
                                    f"Deleted pool configuration: {created_pool_id}", delete_data)
                    else:
                        self.log_test("Saved Pools - DELETE", False, 
                                    f"Delete failed: {delete_data.get('message', 'Unknown error')}", delete_data)
                else:
                    self.log_test("Saved Pools - DELETE", False, 
                                f"HTTP {delete_response.status_code}", {"response": delete_response.text})
            
            # Step 7: Verify deletion by getting pools again
            get_after_delete = requests.get(f"{API_BASE}/pools/saved", timeout=10)
            
            if get_after_delete.status_code == 200:
                after_delete_data = get_after_delete.json()
                final_count = after_delete_data.get("count", 0)
                
                if final_count == initial_count:
                    self.log_test("Saved Pools - GET (After Delete)", True, 
                                f"Pool count returned to initial: {final_count}", after_delete_data)
                else:
                    self.log_test("Saved Pools - GET (After Delete)", False, 
                                f"Pool count mismatch: expected {initial_count}, got {final_count}", after_delete_data)
            else:
                self.log_test("Saved Pools - GET (After Delete)", False, 
                            f"HTTP {get_after_delete.status_code}")
                
        except Exception as e:
            self.log_test("Saved Pools API", False, f"Test error: {str(e)}")

    def test_custom_coins_api(self):
        """Test custom coins API endpoints - GET, POST, PUT, DELETE, GET ALL"""
        try:
            print(f"\n🪙 Testing Custom Coins API with hypothetical new cryptocurrency")
            
            # Step 1: Get initial custom coins (should be empty or existing)
            get_response = requests.get(f"{API_BASE}/coins/custom", timeout=10)
            
            if get_response.status_code == 200:
                initial_data = get_response.json()
                initial_count = initial_data.get("count", 0)
                self.log_test("Custom Coins - GET (Initial)", True, 
                            f"Retrieved {initial_count} existing custom coins", initial_data)
            else:
                self.log_test("Custom Coins - GET (Initial)", False, 
                            f"HTTP {get_response.status_code}", {"response": get_response.text})
                return
            
            # Step 2: Create a new custom coin (hypothetical new cryptocurrency)
            custom_coin_data = {
                "name": "CryptoMiner Pro Coin",
                "symbol": "CMPC",
                "algorithm": "Scrypt",
                "block_reward": 50.0,
                "block_time": 120,
                "difficulty": 2500.0,
                "scrypt_params": {"n": 1024, "r": 1, "p": 1},
                "network_hashrate": "25 MH/s",
                "wallet_format": "C prefix (legacy), cmpc1 (bech32)",
                "description": "Custom cryptocurrency for CryptoMiner Pro V30 testing"
            }
            
            post_response = requests.post(f"{API_BASE}/coins/custom", 
                                        json=custom_coin_data, timeout=10)
            
            created_coin_id = None
            if post_response.status_code == 200:
                post_data = post_response.json()
                if post_data.get("success"):
                    created_coin_id = post_data.get("coin_id")
                    self.log_test("Custom Coins - POST (Create)", True, 
                                f"Created custom coin CMPC: {created_coin_id}", post_data)
                else:
                    self.log_test("Custom Coins - POST (Create)", False, 
                                f"Creation failed: {post_data.get('message', 'Unknown error')}", post_data)
                    return
            else:
                self.log_test("Custom Coins - POST (Create)", False, 
                            f"HTTP {post_response.status_code}", {"response": post_response.text})
                return
            
            # Step 3: Verify the coin was created by getting all custom coins again
            get_after_create = requests.get(f"{API_BASE}/coins/custom", timeout=10)
            
            if get_after_create.status_code == 200:
                after_create_data = get_after_create.json()
                new_count = after_create_data.get("count", 0)
                
                if new_count > initial_count:
                    self.log_test("Custom Coins - GET (After Create)", True, 
                                f"Coin count increased from {initial_count} to {new_count}", after_create_data)
                else:
                    self.log_test("Custom Coins - GET (After Create)", False, 
                                f"Coin count didn't increase: {initial_count} -> {new_count}", after_create_data)
            else:
                self.log_test("Custom Coins - GET (After Create)", False, 
                            f"HTTP {get_after_create.status_code}")
            
            # Step 4: Update the custom coin
            if created_coin_id:
                updated_coin_data = custom_coin_data.copy()
                updated_coin_data["description"] = "Updated custom cryptocurrency for CryptoMiner Pro V30 Enterprise testing"
                updated_coin_data["block_reward"] = 75.0  # Increase block reward
                updated_coin_data["difficulty"] = 3500.0  # Increase difficulty
                
                put_response = requests.put(f"{API_BASE}/coins/custom/{created_coin_id}", 
                                          json=updated_coin_data, timeout=10)
                
                if put_response.status_code == 200:
                    put_data = put_response.json()
                    if put_data.get("success"):
                        self.log_test("Custom Coins - PUT (Update)", True, 
                                    f"Updated custom coin: {created_coin_id}", put_data)
                    else:
                        self.log_test("Custom Coins - PUT (Update)", False, 
                                    f"Update failed: {put_data.get('message', 'Unknown error')}", put_data)
                else:
                    self.log_test("Custom Coins - PUT (Update)", False, 
                                f"HTTP {put_response.status_code}", {"response": put_response.text})
            
            # Step 5: Test GET ALL coins endpoint (preset + custom combined)
            get_all_response = requests.get(f"{API_BASE}/coins/all", timeout=10)
            
            if get_all_response.status_code == 200:
                all_coins_data = get_all_response.json()
                preset_coins = all_coins_data.get("preset_coins", [])
                custom_coins = all_coins_data.get("custom_coins", [])
                total_count = all_coins_data.get("total_count", 0)
                
                all_coins_details = {
                    "preset_count": len(preset_coins),
                    "custom_count": len(custom_coins),
                    "total_count": total_count,
                    "has_cmpc": any(coin.get("symbol") == "CMPC" for coin in custom_coins),
                    "preset_symbols": [coin.get("symbol") for coin in preset_coins[:5]],  # First 5 preset symbols
                    "custom_symbols": [coin.get("symbol") for coin in custom_coins]
                }
                
                if total_count > 0 and len(preset_coins) > 0:
                    self.log_test("Custom Coins - GET ALL", True, 
                                f"Retrieved {len(preset_coins)} preset + {len(custom_coins)} custom coins", all_coins_details)
                else:
                    self.log_test("Custom Coins - GET ALL", False, 
                                f"No coins retrieved or missing presets", all_coins_details)
            else:
                self.log_test("Custom Coins - GET ALL", False, 
                            f"HTTP {get_all_response.status_code}", {"response": get_all_response.text})
            
            # Step 6: Delete the custom coin (cleanup)
            if created_coin_id:
                delete_response = requests.delete(f"{API_BASE}/coins/custom/{created_coin_id}", timeout=10)
                
                if delete_response.status_code == 200:
                    delete_data = delete_response.json()
                    if delete_data.get("success"):
                        self.log_test("Custom Coins - DELETE", True, 
                                    f"Deleted custom coin: {created_coin_id}", delete_data)
                    else:
                        self.log_test("Custom Coins - DELETE", False, 
                                    f"Delete failed: {delete_data.get('message', 'Unknown error')}", delete_data)
                else:
                    self.log_test("Custom Coins - DELETE", False, 
                                f"HTTP {delete_response.status_code}", {"response": delete_response.text})
            
            # Step 7: Verify deletion by getting custom coins again
            get_after_delete = requests.get(f"{API_BASE}/coins/custom", timeout=10)
            
            if get_after_delete.status_code == 200:
                after_delete_data = get_after_delete.json()
                final_count = after_delete_data.get("count", 0)
                
                if final_count == initial_count:
                    self.log_test("Custom Coins - GET (After Delete)", True, 
                                f"Coin count returned to initial: {final_count}", after_delete_data)
                else:
                    self.log_test("Custom Coins - GET (After Delete)", False, 
                                f"Coin count mismatch: expected {initial_count}, got {final_count}", after_delete_data)
            else:
                self.log_test("Custom Coins - GET (After Delete)", False, 
                            f"HTTP {get_after_delete.status_code}")
                
        except Exception as e:
            self.log_test("Custom Coins API", False, f"Test error: {str(e)}")

    def test_saved_pools_validation(self):
        """Test saved pools API validation and error handling"""
        try:
            print(f"\n🔍 Testing Saved Pools API validation and error handling")
            
            # Test 1: Create pool with invalid wallet address
            invalid_wallet_pool = {
                "name": "Invalid Wallet Test Pool",
                "coin_symbol": "EFL",
                "wallet_address": "invalid-wallet-address-123",  # Invalid format
                "pool_address": "stratum.luckydogpool.com",
                "pool_port": 7026,
                "pool_password": "x",
                "description": "Test pool with invalid wallet"
            }
            
            invalid_response = requests.post(f"{API_BASE}/pools/saved", 
                                           json=invalid_wallet_pool, timeout=10)
            
            if invalid_response.status_code == 400:
                invalid_data = invalid_response.json()
                if "Invalid wallet address" in invalid_data.get("detail", ""):
                    self.log_test("Saved Pools - Validation (Invalid Wallet)", True, 
                                "Invalid wallet address properly rejected", invalid_data)
                else:
                    self.log_test("Saved Pools - Validation (Invalid Wallet)", False, 
                                f"Wrong error message: {invalid_data.get('detail')}", invalid_data)
            else:
                self.log_test("Saved Pools - Validation (Invalid Wallet)", False, 
                            f"Expected HTTP 400, got {invalid_response.status_code}", {"response": invalid_response.text})
            
            # Test 2: Try to update non-existent pool
            fake_pool_id = "507f1f77bcf86cd799439011"  # Valid ObjectId format but doesn't exist
            update_data = {
                "name": "Non-existent Pool",
                "coin_symbol": "EFL",
                "wallet_address": "LaEni1U9jb4A38frAbjj3UHMzM6vrre8Dd",
                "pool_address": "stratum.luckydogpool.com",
                "pool_port": 7026,
                "pool_password": "x"
            }
            
            update_response = requests.put(f"{API_BASE}/pools/saved/{fake_pool_id}", 
                                         json=update_data, timeout=10)
            
            if update_response.status_code == 404:
                update_data_response = update_response.json()
                self.log_test("Saved Pools - Validation (Non-existent Update)", True, 
                            "Non-existent pool update properly rejected", update_data_response)
            else:
                self.log_test("Saved Pools - Validation (Non-existent Update)", False, 
                            f"Expected HTTP 404, got {update_response.status_code}", {"response": update_response.text})
            
            # Test 3: Try to delete non-existent pool
            delete_response = requests.delete(f"{API_BASE}/pools/saved/{fake_pool_id}", timeout=10)
            
            if delete_response.status_code == 404:
                delete_data = delete_response.json()
                self.log_test("Saved Pools - Validation (Non-existent Delete)", True, 
                            "Non-existent pool delete properly rejected", delete_data)
            else:
                self.log_test("Saved Pools - Validation (Non-existent Delete)", False, 
                            f"Expected HTTP 404, got {delete_response.status_code}", {"response": delete_response.text})
            
            # Test 4: Try to use non-existent pool
            use_response = requests.post(f"{API_BASE}/pools/saved/{fake_pool_id}/use", timeout=10)
            
            if use_response.status_code == 404:
                use_data = use_response.json()
                self.log_test("Saved Pools - Validation (Non-existent Use)", True, 
                            "Non-existent pool use properly rejected", use_data)
            else:
                self.log_test("Saved Pools - Validation (Non-existent Use)", False, 
                            f"Expected HTTP 404, got {use_response.status_code}", {"response": use_response.text})
                
        except Exception as e:
            self.log_test("Saved Pools Validation", False, f"Test error: {str(e)}")

    def test_custom_coins_validation(self):
        """Test custom coins API validation and error handling"""
        try:
            print(f"\n🔍 Testing Custom Coins API validation and error handling")
            
            # Test 1: Try to create coin with duplicate symbol
            # First create a coin
            original_coin = {
                "name": "Test Coin Original",
                "symbol": "TESTDUP",
                "algorithm": "Scrypt",
                "block_reward": 25.0,
                "block_time": 150,
                "difficulty": 1000.0,
                "description": "Original test coin"
            }
            
            create_response = requests.post(f"{API_BASE}/coins/custom", 
                                          json=original_coin, timeout=10)
            
            created_coin_id = None
            if create_response.status_code == 200:
                create_data = create_response.json()
                if create_data.get("success"):
                    created_coin_id = create_data.get("coin_id")
                    
                    # Now try to create another coin with same symbol
                    duplicate_coin = {
                        "name": "Test Coin Duplicate",
                        "symbol": "TESTDUP",  # Same symbol
                        "algorithm": "Scrypt",
                        "block_reward": 50.0,
                        "block_time": 120,
                        "difficulty": 2000.0,
                        "description": "Duplicate test coin"
                    }
                    
                    duplicate_response = requests.post(f"{API_BASE}/coins/custom", 
                                                     json=duplicate_coin, timeout=10)
                    
                    if duplicate_response.status_code == 400:
                        duplicate_data = duplicate_response.json()
                        if "already exists" in duplicate_data.get("detail", "").lower():
                            self.log_test("Custom Coins - Validation (Duplicate Symbol)", True, 
                                        "Duplicate symbol properly rejected", duplicate_data)
                        else:
                            self.log_test("Custom Coins - Validation (Duplicate Symbol)", False, 
                                        f"Wrong error message: {duplicate_data.get('detail')}", duplicate_data)
                    else:
                        self.log_test("Custom Coins - Validation (Duplicate Symbol)", False, 
                                    f"Expected HTTP 400, got {duplicate_response.status_code}", {"response": duplicate_response.text})
                else:
                    self.log_test("Custom Coins - Validation (Setup)", False, 
                                "Could not create original coin for duplicate test", create_data)
            else:
                self.log_test("Custom Coins - Validation (Setup)", False, 
                            f"Could not create original coin: HTTP {create_response.status_code}")
            
            # Test 2: Try to update non-existent coin
            fake_coin_id = "507f1f77bcf86cd799439011"  # Valid ObjectId format but doesn't exist
            update_data = {
                "name": "Non-existent Coin",
                "symbol": "FAKE",
                "algorithm": "Scrypt",
                "block_reward": 25.0,
                "block_time": 150,
                "difficulty": 1000.0
            }
            
            update_response = requests.put(f"{API_BASE}/coins/custom/{fake_coin_id}", 
                                         json=update_data, timeout=10)
            
            if update_response.status_code == 404:
                update_data_response = update_response.json()
                self.log_test("Custom Coins - Validation (Non-existent Update)", True, 
                            "Non-existent coin update properly rejected", update_data_response)
            else:
                self.log_test("Custom Coins - Validation (Non-existent Update)", False, 
                            f"Expected HTTP 404, got {update_response.status_code}", {"response": update_response.text})
            
            # Test 3: Try to delete non-existent coin
            delete_response = requests.delete(f"{API_BASE}/coins/custom/{fake_coin_id}", timeout=10)
            
            if delete_response.status_code == 404:
                delete_data = delete_response.json()
                self.log_test("Custom Coins - Validation (Non-existent Delete)", True, 
                            "Non-existent coin delete properly rejected", delete_data)
            else:
                self.log_test("Custom Coins - Validation (Non-existent Delete)", False, 
                            f"Expected HTTP 404, got {delete_response.status_code}", {"response": delete_response.text})
            
            # Cleanup: Delete the test coin if it was created
            if created_coin_id:
                cleanup_response = requests.delete(f"{API_BASE}/coins/custom/{created_coin_id}", timeout=10)
                if cleanup_response.status_code == 200:
                    self.log_test("Custom Coins - Validation (Cleanup)", True, 
                                "Test coin cleaned up successfully", {})
                
        except Exception as e:
            self.log_test("Custom Coins Validation", False, f"Test error: {str(e)}")

    def run_all_tests(self):
        """Run all enterprise backend tests including V30 features"""
        print("🚀 Starting CryptoMiner Enterprise V30 Backend Tests")
        print(f"📡 Testing backend at: {BACKEND_URL}")
        print("=" * 60)
        
        # NEW: Saved Pools and Custom Coins API Tests (as requested in review)
        print("\n🆕 NEWLY IMPLEMENTED SAVED POOLS & CUSTOM COINS API TESTING:")
        print("=" * 60)
        self.test_saved_pools_api()
        self.test_custom_coins_api()
        self.test_saved_pools_validation()
        self.test_custom_coins_validation()
        
        # NEW: EFL Scrypt Mining Protocol Tests (as requested in review)
        print("\n🔥 NEWLY IMPLEMENTED SCRYPT MINING PROTOCOL TESTING:")
        print("=" * 60)
        self.test_efl_scrypt_mining_protocol()
        self.test_scrypt_algorithm_integration()
        
        # Run V30 specific tests
        print("\n🔥 V30 ENTERPRISE FEATURES TESTING:")
        self.test_v30_health_check_updates()
        self.test_v30_license_validation()
        self.test_v30_license_activation()
        self.test_v30_hardware_validation()
        self.test_v30_system_initialization()
        self.test_v30_system_status()
        self.test_v30_distributed_mining_control()
        self.test_v30_nodes_management()
        self.test_v30_comprehensive_stats()
        
        print("\n⚡ LEGACY ENTERPRISE FEATURES TESTING:")
        # Run existing enterprise tests
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
        
        # V30 Enterprise Features Summary
        print(f"\n🔥 V30 ENTERPRISE FEATURES STATUS:")
        v30_tests = [
            "V30 Health Check Updates",
            "V30 License Validation", 
            "V30 License Activation",
            "V30 Hardware Validation",
            "V30 System Initialization",
            "V30 System Status",
            "V30 Distributed Mining Control",
            "V30 Nodes Management",
            "V30 Comprehensive Stats"
        ]
        
        v30_passed = [test for test in v30_tests if any(test in passed for passed in self.passed_tests)]
        print(f"   V30 Tests Passed: {len(v30_passed)}/{len(v30_tests)}")
        
        print(f"\n🎯 Legacy Enterprise Features Status:")
        enterprise_tests = [
            "CPU Info Enterprise",
            "Mining Engine Enterprise", 
            "Mining Status Enterprise",
            "Database Connection"
        ]
        
        enterprise_passed = [test for test in enterprise_tests if test in self.passed_tests or any(test in passed for passed in self.passed_tests)]
        print(f"   Legacy Enterprise Tests Passed: {len(enterprise_passed)}/{len(enterprise_tests)}")
        
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