#!/usr/bin/env python3
"""
Additional tests for custom pool address and port features
Focus on edge cases and error handling
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

class CustomFeaturesAPITester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url.rstrip('/')
        self.tests_run = 0
        self.tests_passed = 0
        
    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}: PASSED {details}")
        else:
            print(f"❌ {name}: FAILED {details}")
        return success

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, timeout: int = 10) -> tuple:
        """Make HTTP request and return success status and response"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            else:
                return False, {"error": f"Unsupported method: {method}"}
            
            return response.status_code < 400, response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}
        except json.JSONDecodeError:
            return False, {"error": "Invalid JSON response"}

    def test_pool_connection_edge_cases(self) -> bool:
        """Test edge cases for pool connection testing"""
        print("\n🔍 Testing Pool Connection Edge Cases...")
        
        edge_cases = [
            {
                "name": "Empty pool address",
                "data": {"pool_address": "", "pool_port": 3333, "type": "pool"},
                "should_succeed": False
            },
            {
                "name": "Zero port number",
                "data": {"pool_address": "pool.example.com", "pool_port": 0, "type": "pool"},
                "should_succeed": False
            },
            {
                "name": "Negative port number",
                "data": {"pool_address": "pool.example.com", "pool_port": -1, "type": "pool"},
                "should_succeed": False
            },
            {
                "name": "Port number too high",
                "data": {"pool_address": "pool.example.com", "pool_port": 70000, "type": "pool"},
                "should_succeed": False
            },
            {
                "name": "Invalid connection type",
                "data": {"pool_address": "pool.example.com", "pool_port": 3333, "type": "invalid"},
                "should_succeed": True  # Should default to pool type
            },
            {
                "name": "Missing connection type",
                "data": {"pool_address": "8.8.8.8", "pool_port": 53},
                "should_succeed": True  # Should default to pool type
            }
        ]
        
        passed_tests = 0
        total_tests = len(edge_cases)
        
        for i, test_case in enumerate(edge_cases):
            success, response = self.make_request('POST', '/api/pool/test-connection', test_case["data"])
            
            if test_case["should_succeed"]:
                if success and response.get("success"):
                    passed_tests += 1
                    print(f"  ✅ Test {i+1}: {test_case['name']} - Handled correctly")
                else:
                    print(f"  ❌ Test {i+1}: {test_case['name']} - Expected success: {response}")
            else:
                if not success or not response.get("success"):
                    passed_tests += 1
                    print(f"  ✅ Test {i+1}: {test_case['name']} - Correctly rejected")
                else:
                    print(f"  ❌ Test {i+1}: {test_case['name']} - Should have failed: {response}")
        
        success_rate = (passed_tests / total_tests) * 100
        return self.log_test("Pool Connection Edge Cases", passed_tests == total_tests,
                           f"- {passed_tests}/{total_tests} edge cases handled ({success_rate:.1f}%)")

    def test_mining_config_combinations(self) -> bool:
        """Test various combinations of custom mining configurations"""
        print("\n🔧 Testing Mining Config Combinations...")
        
        # Get coin presets
        success, presets_response = self.make_request('GET', '/api/coins/presets')
        if not success:
            return self.log_test("Mining Config Combinations", False, "- Failed to get coin presets")
        
        litecoin_config = presets_response['presets']['litecoin']
        
        config_tests = [
            {
                "name": "Pool mode with both custom pool and RPC settings",
                "config": {
                    "coin": litecoin_config,
                    "mode": "pool",
                    "threads": 1,
                    "pool_username": "test",
                    "custom_pool_address": "pool.example.com",
                    "custom_pool_port": 3333,
                    "custom_rpc_host": "rpc.example.com",  # Should be ignored in pool mode
                    "custom_rpc_port": 8332
                },
                "should_succeed": True,
                "expected_connection_type": "custom_pool"
            },
            {
                "name": "Solo mode with both custom pool and RPC settings",
                "config": {
                    "coin": litecoin_config,
                    "mode": "solo",
                    "threads": 1,
                    "wallet_address": "LhK1Nk7QidqUBKLMBKVr8fWsNu4gp7rqLs",
                    "custom_pool_address": "pool.example.com",  # Should be ignored in solo mode
                    "custom_pool_port": 3333,
                    "custom_rpc_host": "rpc.example.com",
                    "custom_rpc_port": 8332
                },
                "should_succeed": True,
                "expected_connection_type": "custom_rpc"
            },
            {
                "name": "Pool mode with only custom pool address (no port)",
                "config": {
                    "coin": litecoin_config,
                    "mode": "pool",
                    "threads": 1,
                    "pool_username": "test",
                    "custom_pool_address": "pool.example.com"
                    # Missing custom_pool_port
                },
                "should_succeed": False,
                "expected_connection_type": None
            },
            {
                "name": "Solo mode with only custom RPC host (no port)",
                "config": {
                    "coin": litecoin_config,
                    "mode": "solo",
                    "threads": 1,
                    "wallet_address": "LhK1Nk7QidqUBKLMBKVr8fWsNu4gp7rqLs",
                    "custom_rpc_host": "rpc.example.com"
                    # Missing custom_rpc_port
                },
                "should_succeed": False,
                "expected_connection_type": None
            }
        ]
        
        passed_tests = 0
        total_tests = len(config_tests)
        
        for i, test in enumerate(config_tests):
            start_success, start_response = self.make_request('POST', '/api/mining/start', test["config"])
            
            if test["should_succeed"]:
                if start_success and start_response.get('success'):
                    wallet_info = start_response.get('wallet_info', {})
                    connection_type = wallet_info.get('connection_type')
                    
                    if connection_type == test["expected_connection_type"]:
                        passed_tests += 1
                        print(f"  ✅ Test {i+1}: {test['name']} - Correct connection type: {connection_type}")
                    else:
                        print(f"  ❌ Test {i+1}: {test['name']} - Wrong connection type: {connection_type} (expected {test['expected_connection_type']})")
                    
                    # Stop mining
                    self.make_request('POST', '/api/mining/stop')
                    time.sleep(0.5)
                else:
                    print(f"  ❌ Test {i+1}: {test['name']} - Should have succeeded: {start_response}")
            else:
                if not start_success or not start_response.get('success'):
                    passed_tests += 1
                    print(f"  ✅ Test {i+1}: {test['name']} - Correctly rejected")
                else:
                    print(f"  ❌ Test {i+1}: {test['name']} - Should have failed")
                    self.make_request('POST', '/api/mining/stop')
        
        success_rate = (passed_tests / total_tests) * 100
        return self.log_test("Mining Config Combinations", passed_tests == total_tests,
                           f"- {passed_tests}/{total_tests} combinations tested ({success_rate:.1f}%)")

    def test_integration_workflow(self) -> bool:
        """Test complete integration workflow with custom settings"""
        print("\n🔄 Testing Complete Integration Workflow...")
        
        # Get coin presets
        success, presets_response = self.make_request('GET', '/api/coins/presets')
        if not success:
            return self.log_test("Integration Workflow", False, "- Failed to get coin presets")
        
        litecoin_config = presets_response['presets']['litecoin']
        
        # Step 1: Test pool connection
        pool_test_success, pool_test_response = self.make_request('POST', '/api/pool/test-connection', {
            "pool_address": "8.8.8.8",
            "pool_port": 53,
            "type": "pool"
        })
        
        if not pool_test_success or not pool_test_response.get("success"):
            return self.log_test("Integration Workflow", False, "- Pool connection test failed")
        
        print("  ✅ Step 1: Pool connection test passed")
        
        # Step 2: Start mining with custom pool settings
        custom_config = {
            "coin": litecoin_config,
            "mode": "pool",
            "threads": 1,
            "intensity": 0.1,
            "pool_username": "integration_test",
            "pool_password": "test123",
            "custom_pool_address": "test.pool.com",
            "custom_pool_port": 4444
        }
        
        start_success, start_response = self.make_request('POST', '/api/mining/start', custom_config)
        
        if not start_success or not start_response.get('success'):
            return self.log_test("Integration Workflow", False, f"- Mining start failed: {start_response}")
        
        print("  ✅ Step 2: Mining started with custom settings")
        
        # Step 3: Verify mining status
        time.sleep(2)
        status_success, status_response = self.make_request('GET', '/api/mining/status')
        
        if not status_success or not status_response.get('is_mining'):
            self.make_request('POST', '/api/mining/stop')
            return self.log_test("Integration Workflow", False, "- Mining status check failed")
        
        print("  ✅ Step 3: Mining status confirmed")
        
        # Step 4: Verify configuration in status
        config_in_status = status_response.get('config', {})
        if (config_in_status.get('custom_pool_address') == "test.pool.com" and
            config_in_status.get('custom_pool_port') == 4444):
            print("  ✅ Step 4: Custom configuration preserved in status")
        else:
            self.make_request('POST', '/api/mining/stop')
            return self.log_test("Integration Workflow", False, "- Custom config not preserved")
        
        # Step 5: Stop mining
        stop_success, stop_response = self.make_request('POST', '/api/mining/stop')
        
        if not stop_success or not stop_response.get('success'):
            return self.log_test("Integration Workflow", False, "- Mining stop failed")
        
        print("  ✅ Step 5: Mining stopped successfully")
        
        # Step 6: Verify mining stopped
        time.sleep(1)
        final_status_success, final_status_response = self.make_request('GET', '/api/mining/status')
        
        if final_status_success and not final_status_response.get('is_mining'):
            print("  ✅ Step 6: Mining stop confirmed")
            return self.log_test("Integration Workflow", True, "- Complete workflow successful")
        else:
            return self.log_test("Integration Workflow", False, "- Mining didn't stop properly")

    def run_custom_features_tests(self) -> bool:
        """Run all custom features tests"""
        print("🔥 Testing Custom Pool Address and Port Features")
        print("=" * 60)
        
        # Test edge cases and error handling
        self.test_pool_connection_edge_cases()
        self.test_mining_config_combinations()
        self.test_integration_workflow()
        
        # Results
        print("\n" + "=" * 60)
        print(f"📊 Custom Features Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 Custom Features Status: EXCELLENT - All features working perfectly")
            return True
        elif success_rate >= 80:
            print("✅ Custom Features Status: GOOD - Features working well")
            return True
        elif success_rate >= 60:
            print("⚠️  Custom Features Status: FAIR - Some issues detected")
            return False
        else:
            print("🚨 Custom Features Status: POOR - Major issues detected")
            return False

def main():
    """Main test runner for custom features"""
    import os
    backend_url = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
    
    print(f"Testing custom features at: {backend_url}")
    
    tester = CustomFeaturesAPITester(backend_url)
    success = tester.run_custom_features_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())