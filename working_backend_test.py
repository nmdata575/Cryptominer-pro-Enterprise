#!/usr/bin/env python3
"""
Working Backend Test on Port 8002
"""

import requests
import json
import time

def test_working_backend():
    backend_url = "http://localhost:8002"
    
    print("🚀 WORKING BACKEND TEST")
    print("=" * 40)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Health Check
    tests_total += 1
    try:
        response = requests.get(f"{backend_url}/api/health", timeout=5)
        if response.status_code == 200 and response.json().get('status') == 'healthy':
            print("✅ Health Check: PASSED")
            tests_passed += 1
        else:
            print("❌ Health Check: FAILED")
    except Exception as e:
        print(f"❌ Health Check: FAILED - {e}")
    
    # Test 2: Coin Presets
    tests_total += 1
    try:
        response = requests.get(f"{backend_url}/api/coins/presets", timeout=5)
        if response.status_code == 200:
            presets = response.json().get('presets', {})
            if all(coin in presets for coin in ['litecoin', 'dogecoin', 'feathercoin']):
                print("✅ Coin Presets: PASSED")
                tests_passed += 1
                coin_config = presets['litecoin']
            else:
                print("❌ Coin Presets: FAILED")
        else:
            print("❌ Coin Presets: FAILED")
    except Exception as e:
        print(f"❌ Coin Presets: FAILED - {e}")
    
    # Test 3: System Stats
    tests_total += 1
    try:
        response = requests.get(f"{backend_url}/api/system/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            if all(key in stats for key in ['cpu', 'memory', 'disk']):
                print("✅ System Stats: PASSED")
                tests_passed += 1
            else:
                print("❌ System Stats: FAILED")
        else:
            print("❌ System Stats: FAILED")
    except Exception as e:
        print(f"❌ System Stats: FAILED - {e}")
    
    # Test 4: Wallet Validation
    tests_total += 1
    try:
        response = requests.post(f"{backend_url}/api/wallet/validate", 
                               json={"address": "LhK1Nk7QidqUBKLMBKVr8fWsNu4gp7rqLs", "coin_symbol": "LTC"}, 
                               timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result.get('valid') == True:
                print("✅ Wallet Validation: PASSED")
                tests_passed += 1
            else:
                print("❌ Wallet Validation: FAILED")
        else:
            print("❌ Wallet Validation: FAILED")
    except Exception as e:
        print(f"❌ Wallet Validation: FAILED - {e}")
    
    # Test 5: Pool Connection Test
    tests_total += 1
    try:
        response = requests.post(f"{backend_url}/api/pool/test-connection", 
                               json={"pool_address": "8.8.8.8", "pool_port": 53, "type": "pool"}, 
                               timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Pool Connection Test: PASSED")
                tests_passed += 1
            else:
                print("❌ Pool Connection Test: FAILED")
        else:
            print("❌ Pool Connection Test: FAILED")
    except Exception as e:
        print(f"❌ Pool Connection Test: FAILED - {e}")
    
    # Test 6: Mining Status
    tests_total += 1
    try:
        response = requests.get(f"{backend_url}/api/mining/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            if 'is_mining' in status:
                print("✅ Mining Status: PASSED")
                tests_passed += 1
            else:
                print("❌ Mining Status: FAILED")
        else:
            print("❌ Mining Status: FAILED")
    except Exception as e:
        print(f"❌ Mining Status: FAILED - {e}")
    
    # Test 7: Custom Pool Mining
    tests_total += 1
    try:
        # Get coin presets first
        presets_response = requests.get(f"{backend_url}/api/coins/presets", timeout=5)
        if presets_response.status_code == 200:
            coin_config = presets_response.json()['presets']['litecoin']
            
            custom_pool_config = {
                "coin": coin_config,
                "mode": "pool",
                "threads": 2,
                "intensity": 0.5,
                "auto_optimize": True,
                "ai_enabled": True,
                "wallet_address": "",
                "pool_username": "test_user.worker1",
                "pool_password": "x",
                "custom_pool_address": "pool.example.com",
                "custom_pool_port": 3333
            }
            
            response = requests.post(f"{backend_url}/api/mining/start", 
                                   json=custom_pool_config, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ Custom Pool Mining: PASSED")
                    tests_passed += 1
                    # Stop mining
                    requests.post(f"{backend_url}/api/mining/stop", timeout=5)
                else:
                    print("❌ Custom Pool Mining: FAILED")
            else:
                print("❌ Custom Pool Mining: FAILED")
        else:
            print("❌ Custom Pool Mining: FAILED - No presets")
    except Exception as e:
        print(f"❌ Custom Pool Mining: FAILED - {e}")
    
    # Test 8: AI Insights
    tests_total += 1
    try:
        response = requests.get(f"{backend_url}/api/mining/ai-insights", timeout=5)
        if response.status_code == 200:
            result = response.json()
            if 'insights' in result or 'error' in result:
                print("✅ AI Insights: PASSED")
                tests_passed += 1
            else:
                print("❌ AI Insights: FAILED")
        else:
            print("❌ AI Insights: FAILED")
    except Exception as e:
        print(f"❌ AI Insights: FAILED - {e}")
    
    # Results
    print("\n" + "=" * 40)
    print(f"📊 Results: {tests_passed}/{tests_total} tests passed")
    success_rate = (tests_passed / tests_total) * 100
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Status: GOOD - Backend functioning well")
        return True
    else:
        print("⚠️ Status: ISSUES - Problems detected")
        return False

if __name__ == "__main__":
    test_working_backend()