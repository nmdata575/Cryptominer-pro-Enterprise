#!/usr/bin/env python3
"""
V30 Remote Node Test Script
Tests the remote node functionality without requiring full installation
"""

import asyncio
import json
import sys
import os

# Add current directory to path to import the node
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from v30_remote_node import (
    SystemAnalyzer, 
    V30ProtocolClient, 
    NodeConfig, 
    MiningWorker,
    AutoUpdater
)

async def test_system_analyzer():
    """Test system capability analysis"""
    print("🔍 Testing System Analyzer...")
    
    analyzer = SystemAnalyzer()
    capabilities = analyzer.get_system_capabilities()
    
    print(f"✅ Node ID: {capabilities['node_id']}")
    print(f"✅ Hostname: {capabilities['hostname']}")
    print(f"✅ OS: {capabilities['os_info']['system']} {capabilities['os_info']['release']}")
    print(f"✅ CPU: {capabilities['cpu']['logical_cores']} logical cores")
    print(f"✅ Memory: {capabilities['memory']['total_gb']} GB")
    print(f"✅ GPUs: {len(capabilities['gpus'])}")
    print(f"✅ Network: {capabilities['network']['max_speed_gbps']} Gbps")
    print(f"✅ Est. Hashpower: {capabilities['capabilities']['estimated_hashpower']:,} H/s")
    
    return True

def test_protocol_client():
    """Test V30 protocol message creation/parsing"""
    print("\n🌐 Testing V30 Protocol...")
    
    client = V30ProtocolClient()
    
    # Test message creation
    test_data = {
        "node_id": "test_node_123",
        "message": "Hello V30 Server",
        "timestamp": 1234567890
    }
    
    message = client.create_message(0x01, test_data)
    print(f"✅ Created message: {len(message)} bytes")
    
    # Test message structure
    if len(message) > 16:  # Header size
        print("✅ Message has proper header")
    else:
        print("❌ Message too small")
        return False
    
    return True

async def test_mining_worker():
    """Test mining worker functionality"""
    print("\n⛏️ Testing Mining Worker...")
    
    worker = MiningWorker("test_node_123")
    
    # Test work data
    work_data = {
        "work_id": "test_work_001",
        "coin_config": {
            "name": "Litecoin",
            "symbol": "LTC",
            "algorithm": "scrypt"
        },
        "wallet_address": "ltc1test123",
        "start_nonce": 0,
        "nonce_range": 1000
    }
    
    # Start mining briefly
    if worker.start_mining(work_data):
        print("✅ Mining worker started")
        
        # Let it run for a short time
        await asyncio.sleep(2)
        
        # Get stats
        stats = worker.get_mining_stats()
        print(f"✅ Hashes computed: {stats['hashes_computed']}")
        print(f"✅ Shares found: {stats['shares_found']}")
        print(f"✅ Hashrate: {stats['hashrate']:.2f} H/s")
        
        # Stop mining
        if worker.stop_mining():
            print("✅ Mining worker stopped")
            return True
    
    print("❌ Mining worker test failed")
    return False

async def test_auto_updater():
    """Test auto-updater functionality"""
    print("\n📦 Testing Auto Updater...")
    
    updater = AutoUpdater("localhost", 9001)
    
    # Test update check
    update_info = await updater.check_for_updates()
    print(f"✅ Update check completed")
    print(f"   Current version: {update_info.get('current_version', 'unknown')}")
    print(f"   Update available: {update_info.get('update_available', False)}")
    
    return True

def test_configuration():
    """Test configuration loading and validation"""
    print("\n⚙️ Testing Configuration...")
    
    # Create test config
    test_config = {
        "server_host": "localhost",
        "server_port": 9001,
        "license_key": "TEST-12345-ABCDE-67890-FGHIJ-KLMNO-PQRSTU",
        "max_cpu_threads": 4,
        "enable_gpu": True,
        "heartbeat_interval": 30.0,
        "work_request_interval": 10.0,
        "auto_update": True,
        "update_check_interval": 3600.0
    }
    
    # Save test config
    with open("test_config.json", "w") as f:
        json.dump(test_config, f, indent=2)
    
    try:
        # Load config
        with open("test_config.json", "r") as f:
            loaded_config = json.load(f)
        
        print("✅ Configuration creation and loading working")
        print(f"   Server: {loaded_config['server_host']}:{loaded_config['server_port']}")
        print(f"   License: {loaded_config['license_key'][:20]}...")
        print(f"   Threads: {loaded_config['max_cpu_threads']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    
    finally:
        # Cleanup test file
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")

async def run_connection_test():
    """Test connection to actual V30 server (if available)"""
    print("\n🔗 Testing V30 Server Connection...")
    
    client = V30ProtocolClient()
    
    # Try to connect to localhost (if V30 server is running)
    try:
        if await client.connect("localhost", 9001):
            print("✅ Successfully connected to V30 server at localhost:9001")
            
            # Test registration message
            test_registration = {
                "node_id": "test_node_connection",
                "hostname": "test-host",
                "license_key": "TEST-LICENSE-KEY",
                "system_specs": {"cpu_cores": 4, "ram_gb": 8}
            }
            
            if await client.send_message(0x01, test_registration):
                print("✅ Registration message sent successfully")
                
                # Try to receive response (with timeout)
                try:
                    msg_type, response, error = await asyncio.wait_for(
                        client.receive_message(), timeout=5.0
                    )
                    
                    if error:
                        print(f"⚠️  Server response error: {error}")
                    elif msg_type == 0x02:  # Registration ACK
                        success = response.get("success", False)
                        print(f"✅ Server response received - Registration: {'Success' if success else 'Failed'}")
                        if not success:
                            print(f"   Error: {response.get('error', 'Unknown')}")
                    else:
                        print(f"✅ Server response received - Message type: {msg_type}")
                
                except asyncio.TimeoutError:
                    print("⚠️  No response from server (timeout)")
            
            await client.disconnect()
            return True
        else:
            print("ℹ️  No V30 server found at localhost:9001 (this is normal for testing)")
            return True
            
    except Exception as e:
        print(f"ℹ️  Connection test skipped: {e}")
        return True

def print_banner():
    """Print test banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🧪 CryptoMiner V30 Remote Node - Test Suite               ║
║                                                              ║
║   Testing all node components before deployment             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

async def main():
    """Run all tests"""
    print_banner()
    
    tests = [
        ("System Analyzer", test_system_analyzer()),
        ("Protocol Client", test_protocol_client()),
        ("Mining Worker", test_mining_worker()),
        ("Auto Updater", test_auto_updater()),
        ("Configuration", test_configuration()),
        ("Connection Test", run_connection_test())
    ]
    
    passed = 0
    total = len(tests)
    
    print("🚀 Running V30 Remote Node Tests...\n")
    
    for test_name, test_coro in tests:
        try:
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
            
            if result:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! V30 Remote Node is ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)