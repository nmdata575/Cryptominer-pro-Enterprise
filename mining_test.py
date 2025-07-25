#!/usr/bin/env python3
"""
Mining Functionality Test
"""

import requests
import json
import time

def test_mining():
    backend_url = "https://72416a3e-b7a8-4313-a65e-1e93358dc495.preview.emergentagent.com"
    
    print("⛏️ Testing Mining Functionality")
    print("=" * 40)
    
    # Get coin presets first
    try:
        response = requests.get(f"{backend_url}/api/coins/presets", timeout=10)
        if response.status_code != 200:
            print("❌ Failed to get coin presets")
            return False
        
        presets = response.json()['presets']
        litecoin_config = presets['litecoin']
        print("✅ Got coin presets")
        
    except Exception as e:
        print(f"❌ Error getting presets: {e}")
        return False
    
    # Test pool mining configuration
    pool_config = {
        "coin": litecoin_config,
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
    
    # Test mining start
    try:
        response = requests.post(f"{backend_url}/api/mining/start", 
                               json=pool_config, timeout=15)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Mining start: PASSED")
                
                # Test mining status
                time.sleep(2)
                status_response = requests.get(f"{backend_url}/api/mining/status", timeout=10)
                if status_response.status_code == 200:
                    status = status_response.json()
                    if status.get('is_mining'):
                        print("✅ Mining status: PASSED - Mining active")
                    else:
                        print("⚠️ Mining status: Mining not active")
                
                # Stop mining
                stop_response = requests.post(f"{backend_url}/api/mining/stop", timeout=10)
                if stop_response.status_code == 200:
                    print("✅ Mining stop: PASSED")
                    return True
                else:
                    print("❌ Mining stop: FAILED")
                    return False
            else:
                print(f"❌ Mining start failed: {result}")
                return False
        else:
            print(f"❌ Mining start HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Mining test error: {e}")
        return False

if __name__ == "__main__":
    test_mining()