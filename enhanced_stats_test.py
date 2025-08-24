#!/usr/bin/env python3
"""
Quick test for enhanced statistics API with proxy fields
"""

import requests
import json
import time

BACKEND_URL = "https://smartcrypto-5.preview.emergentagent.com/api"

def test_enhanced_stats():
    session = requests.Session()
    session.headers.update({'Content-Type': 'application/json'})
    
    print("🧪 Testing Enhanced Statistics API with Proxy Fields")
    print("=" * 60)
    
    # 1. Test GET /api/mining/stats for enhanced fields
    print("1️⃣ Testing GET /api/mining/stats for proxy fields...")
    try:
        response = session.get(f"{BACKEND_URL}/mining/stats")
        if response.status_code == 200:
            data = response.json()
            
            # Check for enhanced proxy fields
            proxy_fields = ['shares_accepted', 'shares_submitted', 'queue_size', 'last_share_time']
            found_fields = [field for field in proxy_fields if field in data]
            
            print(f"   📊 Found proxy fields: {found_fields}")
            print(f"   📊 Data: {json.dumps(data, indent=2, default=str)}")
            
            if len(found_fields) == 4:
                print("   ✅ PASS: All enhanced proxy fields present")
            else:
                print(f"   ❌ FAIL: Missing proxy fields: {set(proxy_fields) - set(found_fields)}")
        else:
            print(f"   ❌ FAIL: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
    
    # 2. Test POST /api/mining/update-stats with enhanced format
    print("\n2️⃣ Testing POST /api/mining/update-stats with enhanced format...")
    try:
        enhanced_stats = {
            "hashrate": 1200.5,
            "threads": 4,
            "intensity": 90,
            "coin": "XMR",
            "pool_connected": True,
            "accepted_shares": 25,
            "rejected_shares": 2,
            "uptime": 300.0,
            "difficulty": 350000.0,
            "ai_learning": 85.5,
            "ai_optimization": 78.2,
            # Enhanced proxy fields
            "shares_accepted": 25,
            "shares_submitted": 27,
            "queue_size": 1,
            "last_share_time": int(time.time())
        }
        
        response = session.post(f"{BACKEND_URL}/mining/update-stats", json=enhanced_stats)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print("   ✅ PASS: Enhanced stats update successful")
            else:
                print(f"   ❌ FAIL: {data}")
        else:
            print(f"   ❌ FAIL: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
    
    # 3. Verify the updated stats are returned
    print("\n3️⃣ Verifying updated stats are returned...")
    try:
        time.sleep(1)
        response = session.get(f"{BACKEND_URL}/mining/stats")
        if response.status_code == 200:
            data = response.json()
            
            shares_accepted = data.get('shares_accepted', -1)
            shares_submitted = data.get('shares_submitted', -1)
            queue_size = data.get('queue_size', -1)
            
            print(f"   📊 Shares Accepted: {shares_accepted}")
            print(f"   📊 Shares Submitted: {shares_submitted}")
            print(f"   📊 Queue Size: {queue_size}")
            
            if shares_accepted == 25 and shares_submitted == 27:
                print("   ✅ PASS: Enhanced stats properly persisted and returned")
            else:
                print("   ❌ FAIL: Enhanced stats not properly persisted")
        else:
            print(f"   ❌ FAIL: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")

if __name__ == "__main__":
    test_enhanced_stats()