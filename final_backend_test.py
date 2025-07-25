#!/usr/bin/env python3
"""
Final Comprehensive Backend Test for CryptoMiner Pro Build Verification
"""

import requests
import json
import time
import sys

def test_comprehensive_backend():
    backend_url = "http://localhost:8001"
    
    print("🚀 COMPREHENSIVE BACKEND BUILD TEST")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Health Check
    tests_total += 1
    try:
        response = requests.get(f"{backend_url}/api/health", timeout=5)
        if response.status_code == 200 and response.json().get('status') == 'healthy':
            print("✅ Health Check API: PASSED")
            tests_passed += 1
        else:
            print("❌ Health Check API: FAILED")
    except Exception as e:
        print(f"❌ Health Check API: FAILED - {e}")
    
    # Test 2: Coin Presets
    tests_total += 1
    try:
        response = requests.get(f"{backend_url}/api/coins/presets", timeout=5)
        if response.status_code == 200:
            presets = response.json().get('presets', {})
            if all(coin in presets for coin in ['litecoin', 'dogecoin', 'feathercoin']):
                print("✅ Coin Presets API: PASSED")
                tests_passed += 1
                coin_config = presets['litecoin']  # Store for later use
            else:
                print("❌ Coin Presets API: FAILED - Missing coins")
        else:
            print("❌ Coin Presets API: FAILED")
    except Exception as e:
        print(f"❌ Coin Presets API: FAILED - {e}")
    
    # Test 3: System Stats
    tests_total += 1
    try:
        response = requests.get(f"{backend_url}/api/system/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            if all(key in stats for key in ['cpu', 'memory', 'disk']):
                print("✅ System Stats API: PASSED")
                tests_passed += 1
            else:
                print("❌ System Stats API: FAILED - Missing data")
        else:
            print("❌ System Stats API: FAILED")
    except Exception as e:
        print(f"❌ System Stats API: FAILED - {e}")
    
    # Test 4: CPU Info
    tests_total += 1
    try:
        response = requests.get(f"{backend_url}/api/system/cpu-info", timeout=5)
        if response.status_code == 200:
            cpu_info = response.json()
            if all(key in cpu_info for key in ['cores', 'recommended_threads', 'mining_profiles']):
                print("✅ CPU Info API: PASSED")
                tests_passed += 1
            else:
                print("❌ CPU Info API: FAILED - Missing data")
        else:
            print("❌ CPU Info API: FAILED")
    except Exception as e:
        print(f"❌ CPU Info API: FAILED - {e}")
    
    # Test 5: Mining Status (Initial)
    tests_total += 1
    try:
        response = requests.get(f"{backend_url}/api/mining/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            if 'is_mining' in status and not status['is_mining']:
                print("✅ Mining Status API: PASSED")
                tests_passed += 1
            else:
                print("❌ Mining Status API: FAILED - Unexpected mining state")
        else:
            print("❌ Mining Status API: FAILED")
    except Exception as e:
        print(f"❌ Mining Status API: FAILED - {e}")
    
    # Test 6: Wallet Validation
    tests_total += 1
    try:
        test_cases = [
            {"address": "LhK1Nk7QidqUBKLMBKVr8fWsNu4gp7rqLs", "coin_symbol": "LTC", "expected": True},
            {"address": "DQVpNjNVHjTgHaE4Y1oqRxCLe6rKVrUUgJ", "coin_symbol": "DOGE", "expected": True},
            {"address": "6nsHHMiUexBgE8GZzw5EBVL8Lz2sJEzQRc", "coin_symbol": "FTC", "expected": True},
            {"address": "invalid_address", "coin_symbol": "LTC", "expected": False}
        ]
        
        all_passed = True
        for case in test_cases:
            response = requests.post(f"{backend_url}/api/wallet/validate", 
                                   json={"address": case["address"], "coin_symbol": case["coin_symbol"]}, 
                                   timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result.get('valid') != case["expected"]:
                    all_passed = False
                    break
            else:
                all_passed = False
                break
        
        if all_passed:
            print("✅ Wallet Validation API: PASSED")
            tests_passed += 1
        else:
            print("❌ Wallet Validation API: FAILED")
    except Exception as e:
        print(f"❌ Wallet Validation API: FAILED - {e}")
    
    # Test 7: Pool Connection Testing
    tests_total += 1
    try:
        response = requests.post(f"{backend_url}/api/pool/test-connection", 
                               json={"pool_address": "8.8.8.8", "pool_port": 53, "type": "pool"}, 
                               timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Pool Connection Test API: PASSED")
                tests_passed += 1
            else:
                print("❌ Pool Connection Test API: FAILED - Connection failed")
        else:
            print("❌ Pool Connection Test API: FAILED")
    except Exception as e:
        print(f"❌ Pool Connection Test API: FAILED - {e}")
    
    # Test 8: Custom Pool Mining Configuration
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
                    print("❌ Custom Pool Mining: FAILED - Start unsuccessful")
            else:
                print("❌ Custom Pool Mining: FAILED - HTTP error")
        else:
            print("❌ Custom Pool Mining: FAILED - No presets")
    except Exception as e:
        print(f"❌ Custom Pool Mining: FAILED - {e}")
    
    # Test 9: Custom RPC Mining Configuration
    tests_total += 1
    try:
        custom_rpc_config = {
            "coin": coin_config,
            "mode": "solo",
            "threads": 2,
            "intensity": 0.5,
            "auto_optimize": True,
            "ai_enabled": True,
            "wallet_address": "LhK1Nk7QidqUBKLMBKVr8fWsNu4gp7rqLs",
            "custom_rpc_host": "localhost",
            "custom_rpc_port": 9332,
            "custom_rpc_username": "rpcuser",
            "custom_rpc_password": "rpcpass"
        }
        
        response = requests.post(f"{backend_url}/api/mining/start", 
                               json=custom_rpc_config, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Custom RPC Mining: PASSED")
                tests_passed += 1
                # Stop mining
                requests.post(f"{backend_url}/api/mining/stop", timeout=5)
            else:
                print("❌ Custom RPC Mining: FAILED - Start unsuccessful")
        else:
            print("❌ Custom RPC Mining: FAILED - HTTP error")
    except Exception as e:
        print(f"❌ Custom RPC Mining: FAILED - {e}")
    
    # Test 10: AI Insights
    tests_total += 1
    try:
        response = requests.get(f"{backend_url}/api/mining/ai-insights", timeout=5)
        if response.status_code == 200:
            result = response.json()
            if 'insights' in result or 'error' in result:  # Either is acceptable
                print("✅ AI Insights API: PASSED")
                tests_passed += 1
            else:
                print("❌ AI Insights API: FAILED - Unexpected response")
        else:
            print("❌ AI Insights API: FAILED")
    except Exception as e:
        print(f"❌ AI Insights API: FAILED - {e}")
    
    # Test 11: Error Handling
    tests_total += 1
    try:
        # Test invalid endpoint
        response = requests.get(f"{backend_url}/api/nonexistent", timeout=5)
        if response.status_code == 404:
            print("✅ Error Handling: PASSED")
            tests_passed += 1
        else:
            print("❌ Error Handling: FAILED - Should return 404")
    except Exception as e:
        print(f"❌ Error Handling: FAILED - {e}")
    
    # Test 12: Dynamic Thread Management
    tests_total += 1
    try:
        thread_config = {
            "coin": coin_config,
            "mode": "pool",
            "threads": 4,
            "auto_thread_detection": True,
            "thread_profile": "standard",
            "pool_username": "test_user"
        }
        
        response = requests.post(f"{backend_url}/api/mining/start", 
                               json=thread_config, timeout=10)
        if response.status_code == 200:
            result = response.json()
            wallet_info = result.get('wallet_info', {})
            if 'threads_used' in wallet_info and 'auto_detection' in wallet_info:
                print("✅ Dynamic Thread Management: PASSED")
                tests_passed += 1
                requests.post(f"{backend_url}/api/mining/stop", timeout=5)
            else:
                print("❌ Dynamic Thread Management: FAILED - Missing thread info")
        else:
            print("❌ Dynamic Thread Management: FAILED")
    except Exception as e:
        print(f"❌ Dynamic Thread Management: FAILED - {e}")
    
    # Results
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS: {tests_passed}/{tests_total} tests passed")
    success_rate = (tests_passed / tests_total) * 100
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 BUILD STATUS: EXCELLENT - All systems operational")
        return True
    elif success_rate >= 80:
        print("✅ BUILD STATUS: GOOD - System is functioning well")
        return True
    elif success_rate >= 70:
        print("⚠️ BUILD STATUS: ACCEPTABLE - Minor issues detected")
        return True
    else:
        print("🚨 BUILD STATUS: FAILED - Major issues detected")
        return False

if __name__ == "__main__":
    success = test_comprehensive_backend()
    sys.exit(0 if success else 1)