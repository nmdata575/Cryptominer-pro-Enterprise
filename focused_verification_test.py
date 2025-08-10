#!/usr/bin/env python3
"""
Focused Verification Test for Review Request Issues
Tests the specific fixes mentioned in the review request
"""

import requests
import json
import time
import sys

BACKEND_URL = "https://0aecbcf7-d390-4bac-b616-167712cf354b.preview.emergentagent.com/api"

def test_database_status_in_health():
    """Test that health endpoint includes database connectivity info"""
    print("🔍 Testing Database Status in Health Check...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if database field exists
            if "database" in data:
                db_info = data["database"]
                
                # Check required database fields
                if "status" in db_info and "url" in db_info:
                    db_status = db_info["status"]
                    
                    if db_status == "connected":
                        print(f"✅ Database status shows 'connected' - Fix verified!")
                        print(f"   Database URL: {db_info['url']}")
                        return True
                    else:
                        print(f"❌ Database status is '{db_status}', expected 'connected'")
                        return False
                else:
                    print("❌ Database info missing required fields (status, url)")
                    return False
            else:
                print("❌ Health check missing 'database' field")
                return False
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_backend_root_route():
    """Test that backend root route doesn't return 404"""
    print("🔍 Testing Backend Root Route...")
    
    try:
        response = requests.get(f"{BACKEND_URL}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if "message" in data and "CryptoMiner Pro API" in data["message"]:
                print("✅ Backend root route working - Fix verified!")
                print(f"   Message: {data['message']}")
                return True
            else:
                print("❌ Root route response doesn't contain expected message")
                return False
        else:
            print(f"❌ Root route failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_system_apis():
    """Test core system APIs are working"""
    print("🔍 Testing Core System APIs...")
    
    apis_to_test = [
        ("/health", "Health Check"),
        ("/system/cpu-info", "CPU Info"),
        ("/system/stats", "System Stats"),
        ("/mining/status", "Mining Status"),
        ("/coins/presets", "Coin Presets")
    ]
    
    passed = 0
    total = len(apis_to_test)
    
    for endpoint, name in apis_to_test:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ {name}: OK")
                passed += 1
            else:
                print(f"   ❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name}: Exception {str(e)}")
    
    if passed == total:
        print(f"✅ All {total} core APIs working - Fix verified!")
        return True
    else:
        print(f"❌ Only {passed}/{total} APIs working")
        return False

def test_database_operations():
    """Test database operations (pools and coins APIs)"""
    print("🔍 Testing Database Operations...")
    
    try:
        # Test saved pools API
        pools_response = requests.get(f"{BACKEND_URL}/pools/saved", timeout=10)
        
        if pools_response.status_code != 200:
            print(f"❌ Saved pools API failed: HTTP {pools_response.status_code}")
            return False
        
        pools_data = pools_response.json()
        if "pools" not in pools_data or "count" not in pools_data:
            print("❌ Saved pools API missing required fields")
            return False
        
        # Test custom coins API
        coins_response = requests.get(f"{BACKEND_URL}/coins/custom", timeout=10)
        
        if coins_response.status_code != 200:
            print(f"❌ Custom coins API failed: HTTP {coins_response.status_code}")
            return False
        
        coins_data = coins_response.json()
        if "coins" not in coins_data or "count" not in coins_data:
            print("❌ Custom coins API missing required fields")
            return False
        
        print("✅ Database operations working - Pools and Coins APIs functional!")
        print(f"   Saved pools: {pools_data['count']}")
        print(f"   Custom coins: {coins_data['count']}")
        return True
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_mining_functionality():
    """Test mining start/stop functionality"""
    print("🔍 Testing Mining Functionality...")
    
    try:
        # Test mining status first
        status_response = requests.get(f"{BACKEND_URL}/mining/status", timeout=10)
        
        if status_response.status_code != 200:
            print(f"❌ Mining status failed: HTTP {status_response.status_code}")
            return False
        
        status_data = status_response.json()
        if "is_mining" not in status_data or "stats" not in status_data:
            print("❌ Mining status missing required fields")
            return False
        
        # Test mining start with valid config
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
            "threads": 2,
            "mode": "pool"
        }
        
        start_response = requests.post(f"{BACKEND_URL}/mining/start", json=mining_config, timeout=15)
        
        if start_response.status_code != 200:
            print(f"❌ Mining start failed: HTTP {start_response.status_code}")
            return False
        
        start_data = start_response.json()
        if not start_data.get("success"):
            print(f"❌ Mining start unsuccessful: {start_data.get('message')}")
            return False
        
        # Wait a moment then stop mining
        time.sleep(2)
        
        stop_response = requests.post(f"{BACKEND_URL}/mining/stop", timeout=10)
        
        if stop_response.status_code != 200:
            print(f"❌ Mining stop failed: HTTP {stop_response.status_code}")
            return False
        
        stop_data = stop_response.json()
        if not stop_data.get("success"):
            print(f"❌ Mining stop unsuccessful: {stop_data.get('message')}")
            return False
        
        print("✅ Mining functionality working - Start/Stop operations successful!")
        return True
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_v30_features():
    """Test V30 enterprise features are operational"""
    print("🔍 Testing V30 Enterprise Features...")
    
    v30_endpoints = [
        ("/v30/hardware/validate", "Hardware Validation"),
        ("/v30/system/status", "System Status"),
        ("/v30/nodes/list", "Node Management"),
        ("/v30/stats/comprehensive", "Comprehensive Stats")
    ]
    
    passed = 0
    total = len(v30_endpoints)
    
    for endpoint, name in v30_endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Basic validation that response has content
                if data and len(data) > 0:
                    print(f"   ✅ {name}: OK")
                    passed += 1
                else:
                    print(f"   ❌ {name}: Empty response")
            else:
                print(f"   ❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name}: Exception {str(e)}")
    
    if passed == total:
        print(f"✅ All {total} V30 features operational - Fix verified!")
        return True
    else:
        print(f"❌ Only {passed}/{total} V30 features working")
        return False

def main():
    """Run focused verification tests"""
    print("🚀 FOCUSED VERIFICATION TEST - Review Request Issues")
    print("=" * 60)
    print("Testing specific fixes mentioned in review request:")
    print("1. Database Status in Health Check")
    print("2. Backend Root Route")
    print("3. System APIs")
    print("4. Database Operations")
    print("5. Mining Functionality")
    print("6. V30 Features")
    print("=" * 60)
    
    tests = [
        ("Database Status Enhancement", test_database_status_in_health),
        ("Backend Root Route Fix", test_backend_root_route),
        ("Core System APIs", test_system_apis),
        ("Database Operations", test_database_operations),
        ("Mining Functionality", test_mining_functionality),
        ("V30 Enterprise Features", test_v30_features)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} EXCEPTION: {str(e)}")
    
    print("\n" + "=" * 60)
    print("📊 FOCUSED VERIFICATION RESULTS")
    print("=" * 60)
    print(f"✅ PASSED: {passed}/{total} tests")
    print(f"❌ FAILED: {total - passed}/{total} tests")
    
    if passed == total:
        print("\n🎉 ALL FIXES VERIFIED SUCCESSFULLY!")
        print("✅ Database status returns 'connected'")
        print("✅ No 500/404 errors on standard endpoints")
        print("✅ All core functionality operational")
        print("✅ V30 features working correctly")
        return True
    else:
        print(f"\n⚠️  {total - passed} issue(s) still need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)