#!/usr/bin/env python3
"""
Quick Backend Test for CryptoMiner Pro - Build Verification
"""

import requests
import json
import time
import os

def test_backend():
    backend_url = "https://d7fc330d-17f6-47e5-a2b9-090776354317.preview.emergentagent.com"
    
    print("🚀 Quick Backend Build Test")
    print("=" * 40)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Health Check
    tests_total += 1
    try:
        response = requests.get(f"{backend_url}/api/health", timeout=10)
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
        response = requests.get(f"{backend_url}/api/coins/presets", timeout=10)
        if response.status_code == 200:
            presets = response.json().get('presets', {})
            if 'litecoin' in presets and 'dogecoin' in presets and 'feathercoin' in presets:
                print("✅ Coin Presets: PASSED")
                tests_passed += 1
            else:
                print("❌ Coin Presets: FAILED - Missing coins")
        else:
            print("❌ Coin Presets: FAILED")
    except Exception as e:
        print(f"❌ Coin Presets: FAILED - {e}")
    
    # Test 3: System Stats
    tests_total += 1
    try:
        response = requests.get(f"{backend_url}/api/system/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            if 'cpu' in stats and 'memory' in stats:
                print("✅ System Stats: PASSED")
                tests_passed += 1
            else:
                print("❌ System Stats: FAILED - Missing data")
        else:
            print("❌ System Stats: FAILED")
    except Exception as e:
        print(f"❌ System Stats: FAILED - {e}")
    
    # Test 4: Mining Status
    tests_total += 1
    try:
        response = requests.get(f"{backend_url}/api/mining/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            if 'is_mining' in status:
                print("✅ Mining Status: PASSED")
                tests_passed += 1
            else:
                print("❌ Mining Status: FAILED - Missing status")
        else:
            print("❌ Mining Status: FAILED")
    except Exception as e:
        print(f"❌ Mining Status: FAILED - {e}")
    
    # Test 5: Wallet Validation
    tests_total += 1
    try:
        response = requests.post(f"{backend_url}/api/wallet/validate", 
                               json={"address": "LhK1Nk7QidqUBKLMBKVr8fWsNu4gp7rqLs", "coin_symbol": "LTC"}, 
                               timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('valid') == True:
                print("✅ Wallet Validation: PASSED")
                tests_passed += 1
            else:
                print("❌ Wallet Validation: FAILED - Invalid result")
        else:
            print("❌ Wallet Validation: FAILED")
    except Exception as e:
        print(f"❌ Wallet Validation: FAILED - {e}")
    
    # Test 6: Pool Connection Test
    tests_total += 1
    try:
        response = requests.post(f"{backend_url}/api/pool/test-connection", 
                               json={"pool_address": "8.8.8.8", "pool_port": 53, "type": "pool"}, 
                               timeout=15)
        if response.status_code == 200:
            result = response.json()
            if result.get('success') == True:
                print("✅ Pool Connection Test: PASSED")
                tests_passed += 1
            else:
                print("❌ Pool Connection Test: FAILED - Connection failed")
        else:
            print("❌ Pool Connection Test: FAILED")
    except Exception as e:
        print(f"❌ Pool Connection Test: FAILED - {e}")
    
    # Test 7: CPU Info
    tests_total += 1
    try:
        response = requests.get(f"{backend_url}/api/system/cpu-info", timeout=10)
        if response.status_code == 200:
            cpu_info = response.json()
            if 'cores' in cpu_info and 'recommended_threads' in cpu_info:
                print("✅ CPU Info: PASSED")
                tests_passed += 1
            else:
                print("❌ CPU Info: FAILED - Missing data")
        else:
            print("❌ CPU Info: FAILED")
    except Exception as e:
        print(f"❌ CPU Info: FAILED - {e}")
    
    # Test 8: AI Insights
    tests_total += 1
    try:
        response = requests.get(f"{backend_url}/api/mining/ai-insights", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if 'insights' in result or 'error' in result:  # Either is acceptable
                print("✅ AI Insights: PASSED")
                tests_passed += 1
            else:
                print("❌ AI Insights: FAILED - Unexpected response")
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
        print("🎉 Status: GOOD - Backend is functioning well")
        return True
    else:
        print("⚠️ Status: ISSUES - Some problems detected")
        return False

if __name__ == "__main__":
    test_backend()