#!/usr/bin/env python3
"""
Test mining control with XMR and connection proxy
"""

import requests
import json
import time

BACKEND_URL = "https://smartcrypto-5.preview.emergentagent.com/api"

def test_mining_control():
    session = requests.Session()
    session.headers.update({'Content-Type': 'application/json'})
    
    print("🧪 Testing Mining Control with XMR and Connection Proxy")
    print("=" * 60)
    
    # 1. Start XMR mining
    print("1️⃣ Starting XMR mining with connection proxy...")
    try:
        mining_config = {
            "action": "start",
            "config": {
                "coin": "XMR",
                "wallet": "4793trzeyXigW8qj9JZU1bVUuohVqn76EBpXUEJdDxJS5tAP4rjAdS7PzWFXzV3MtE65j8",
                "pool": "stratum+tcp://xmr.zeropool.io:3333",
                "intensity": 90,
                "threads": 2,
                "password": "x"
            }
        }
        
        response = session.post(f"{BACKEND_URL}/mining/control", json=mining_config)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print(f"   ✅ PASS: Mining started - {data.get('message', '')}")
                process_id = data.get('process_id', 'N/A')
                print(f"   📊 Process ID: {process_id}")
            else:
                print(f"   ❌ FAIL: {data}")
        else:
            print(f"   ❌ FAIL: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
    
    # 2. Wait and check mining status
    print("\n2️⃣ Checking mining status after 10 seconds...")
    time.sleep(10)
    
    try:
        response = session.get(f"{BACKEND_URL}/mining/status")
        if response.status_code == 200:
            data = response.json()
            is_active = data.get('is_active', False)
            process_id = data.get('process_id')
            pool_connected = data.get('pool_connected', False)
            
            print(f"   📊 Active: {is_active}")
            print(f"   📊 Process ID: {process_id}")
            print(f"   📊 Pool Connected: {pool_connected}")
            
            if is_active and process_id:
                print("   ✅ PASS: Mining process is active")
            else:
                print("   ❌ FAIL: Mining process not active")
        else:
            print(f"   ❌ FAIL: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
    
    # 3. Check mining stats
    print("\n3️⃣ Checking mining statistics...")
    try:
        response = session.get(f"{BACKEND_URL}/mining/stats")
        if response.status_code == 200:
            data = response.json()
            
            hashrate = data.get('hashrate', 0)
            coin = data.get('coin', '')
            threads = data.get('threads', 0)
            pool_connected = data.get('pool_connected', False)
            shares_accepted = data.get('shares_accepted', 0)
            shares_submitted = data.get('shares_submitted', 0)
            queue_size = data.get('queue_size', 0)
            
            print(f"   📊 Coin: {coin}")
            print(f"   📊 Hashrate: {hashrate} H/s")
            print(f"   📊 Threads: {threads}")
            print(f"   📊 Pool Connected: {pool_connected}")
            print(f"   📊 Shares Accepted: {shares_accepted}")
            print(f"   📊 Shares Submitted: {shares_submitted}")
            print(f"   📊 Queue Size: {queue_size}")
            
            if coin == 'XMR' and threads > 0:
                print("   ✅ PASS: Mining stats show XMR mining active")
            else:
                print("   ❌ FAIL: Mining stats don't show active XMR mining")
        else:
            print(f"   ❌ FAIL: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
    
    # 4. Stop mining
    print("\n4️⃣ Stopping mining...")
    try:
        stop_config = {"action": "stop"}
        response = session.post(f"{BACKEND_URL}/mining/control", json=stop_config)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print(f"   ✅ PASS: Mining stopped - {data.get('message', '')}")
            else:
                print(f"   ❌ FAIL: {data}")
        else:
            print(f"   ❌ FAIL: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")

if __name__ == "__main__":
    test_mining_control()