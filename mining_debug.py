#!/usr/bin/env python3
"""
Debug Real Mining Issue
Test the mining engine directly to identify the problem
"""

import requests
import json
import time
import sys

BACKEND_URL = "https://c6db4a82-7f00-4029-bb3a-ed7a73ef471c.preview.emergentagent.com/api"

def test_mining_debug():
    """Debug mining start/stop issue"""
    print("🔍 Debugging Real Mining Issue...")
    
    # Start mining
    print("\n1. Starting mining...")
    start_config = {
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
        "threads": 2,  # Use fewer threads for debugging
        "mode": "pool",
        "pool_username": "LaEni1U9jb4A38frAbjj3UHMzM6vrre8Dd",
        "pool_password": "x"
    }
    
    response = requests.post(f"{BACKEND_URL}/mining/start", json=start_config, timeout=30)
    print(f"Start response: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Message: {data.get('message')}")
    else:
        print(f"Error: {response.text}")
        return
    
    # Check status immediately and over time
    for i in range(10):  # Check for 10 seconds
        print(f"\n{i+1}. Checking status after {i+1} seconds...")
        time.sleep(1)
        
        try:
            status_response = requests.get(f"{BACKEND_URL}/mining/status", timeout=10)
            if status_response.status_code == 200:
                status_data = status_response.json()
                is_mining = status_data.get("is_mining", False)
                stats = status_data.get("stats", {})
                
                print(f"   Is Mining: {is_mining}")
                print(f"   Hashrate: {stats.get('hashrate', 0)}")
                print(f"   Active Threads: {stats.get('active_threads', 0)}")
                print(f"   Uptime: {stats.get('uptime', 0)}")
                
                if not is_mining and i > 2:  # If stopped after 3 seconds
                    print("   ❌ Mining stopped unexpectedly!")
                    break
                elif is_mining:
                    print("   ✅ Mining is active")
            else:
                print(f"   ❌ Status check failed: {status_response.status_code}")
        except Exception as e:
            print(f"   ❌ Status check error: {e}")
    
    # Try to stop mining
    print(f"\n11. Stopping mining...")
    try:
        stop_response = requests.post(f"{BACKEND_URL}/mining/stop", timeout=10)
        if stop_response.status_code == 200:
            stop_data = stop_response.json()
            print(f"Stop success: {stop_data.get('success')}")
            print(f"Stop message: {stop_data.get('message')}")
        else:
            print(f"Stop error: {stop_response.text}")
    except Exception as e:
        print(f"Stop exception: {e}")

if __name__ == "__main__":
    test_mining_debug()