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
    def __init__(self, base_url="https://cpu-mining-dash.preview.emergentagent.com"):
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

    def run_comprehensive_test(self):
        """Run all API tests"""
        print("🚀 Starting CryptoMiner Pro V30 API Testing")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # Test all endpoints
        test_methods = [
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

        for test_method in test_methods:
            try:
                test_method()
                time.sleep(0.5)  # Brief pause between tests
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