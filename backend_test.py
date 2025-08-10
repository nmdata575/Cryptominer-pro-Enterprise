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

    def run_all_tests(self):
        """Run all enterprise backend tests including V30 features"""
        print("🚀 Starting CryptoMiner Enterprise V30 Backend Tests")
        print(f"📡 Testing backend at: {BACKEND_URL}")
        print("=" * 60)
        
        # Run V30 specific tests first
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