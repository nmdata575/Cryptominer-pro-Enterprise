#!/usr/bin/env python3
"""
Final Mining Control API Test - Quick verification of all endpoints
"""

import requests
import json
import time

def test_endpoint(name, method, url, data=None):
    """Test a single endpoint"""
    print(f"\n🔍 {name}")
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json=data, timeout=10)
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {json.dumps(result, default=str)[:150]}...")
            return True, result
        else:
            print(f"   ❌ Failed: {response.text[:100]}")
            return False, {}
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False, {}

def main():
    base_url = "https://cryptomine-central.preview.emergentagent.com/api"
    
    print("⚡ CryptoMiner Pro V30 - Final Mining Control Test")
    print("=" * 60)
    
    # Test all key endpoints
    tests = [
        ("Mining Status", "GET", f"{base_url}/mining/status", None),
        ("Mining Stats", "GET", f"{base_url}/mining/stats", None),
        ("Stop Mining", "POST", f"{base_url}/mining/control", {"action": "stop"}),
        ("Invalid Action", "POST", f"{base_url}/mining/control", {"action": "invalid"}),
        ("Control Log", "GET", f"{base_url}/mining/control-log", None),
        ("Start Mining", "POST", f"{base_url}/mining/control", {
            "action": "start", 
            "config": {
                "coin": "LTC", 
                "wallet": "LTC_FINAL_TEST_WALLET", 
                "pool": "ltc.luckymonster.pro:4112", 
                "intensity": 80, 
                "threads": 4
            }
        }),
        ("Status After Start", "GET", f"{base_url}/mining/status", None),
        ("Final Stop", "POST", f"{base_url}/mining/control", {"action": "stop"}),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, method, url, data in tests:
        success, result = test_endpoint(name, method, url, data)
        if success:
            passed += 1
        time.sleep(1)
    
    print(f"\n📊 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL MINING CONTROL TESTS PASSED!")
    else:
        print("⚠️  Some tests had issues")

if __name__ == "__main__":
    main()