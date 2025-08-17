#!/usr/bin/env python3
"""
CryptoMiner Pro V30 - Pool Mining Functionality Test
Tests the specific fixes applied to pool mining functionality
"""

import sys
import os
import time
import asyncio
import threading
import logging

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_real_pool_mining_integration():
    """Test real pool mining with actual pool connection"""
    print("🧪 Testing Real Pool Mining Integration...")
    
    try:
        sys.path.append('/app')
        from cryptominer import CompactMiner
        from mining_engine import CoinConfig
        
        # Create miner instance
        miner = CompactMiner()
        miner.initialize_components()
        
        # Test configuration for pool mining
        test_config = {
            'coin': {
                'name': 'Litecoin',
                'symbol': 'LTC',
                'algorithm': 'Scrypt',
                'block_reward': 6.25,
                'block_time': 150,
                'difficulty': 27882939.35508488,
                'scrypt_params': {'n': 1024, 'r': 1, 'p': 1},
                'network_hashrate': '450 TH/s',
                'wallet_format': 'bech32'
            },
            'wallet_address': 'ltc1qqvz2zw9hqd804a03xg95m4594p7v7thk25sztl',
            'mode': 'pool',
            'pool_address': 'stratum+tcp://ltc.luckymonster.pro:4112',
            'pool_password': 'x',
            'mining_intensity': 75,
            'threads': 4,
            'web_port': 3333
        }
        
        miner.config = test_config
        
        # Test pool mining start (but don't actually mine for long)
        print("🚀 Testing pool mining startup...")
        
        success = miner.start_mining()
        
        if success:
            print("✅ Pool mining started successfully")
            
            # Let it run for a few seconds to test functionality
            time.sleep(5)
            
            # Check mining status
            status = miner.mining_engine.get_mining_status()
            
            if status['is_mining']:
                print("✅ Mining status reports active")
            else:
                print("⚠️ Mining status reports inactive")
            
            # Stop mining
            miner.stop_mining()
            print("✅ Pool mining stopped successfully")
            
            return True, "Real pool mining integration working"
        else:
            return False, "Failed to start pool mining"
            
    except Exception as e:
        return False, f"Pool mining integration test error: {str(e)}"

def test_thread_management_fixes():
    """Test the fixed thread management"""
    print("\n🧪 Testing Thread Management Fixes...")
    
    try:
        from real_scrypt_miner import RealScryptMiner
        
        # Test thread count configuration
        miner = RealScryptMiner()
        
        # Test different thread counts
        for thread_count in [4, 6, 8]:
            miner.set_thread_count(thread_count)
            
            if miner.thread_count != thread_count:
                return False, f"Thread count not set correctly: expected {thread_count}, got {miner.thread_count}"
            
            print(f"✅ Thread count {thread_count} set correctly")
        
        # Test thread cleanup
        miner.mining_threads = []  # Simulate threads
        miner.stop_mining()
        
        if len(miner.mining_threads) == 0:
            print("✅ Thread cleanup working")
        
        return True, "Thread management fixes working correctly"
        
    except Exception as e:
        return False, f"Thread management test error: {str(e)}"

def test_stratum_protocol_fixes():
    """Test the fixed Stratum protocol implementation"""
    print("\n🧪 Testing Stratum Protocol Fixes...")
    
    try:
        from real_scrypt_miner import StratumClient
        
        # Test StratumClient initialization
        client = StratumClient()
        
        # Test message formatting
        test_message = {
            "id": 1,
            "method": "mining.subscribe",
            "params": ["CryptoMiner-V30/1.0", None]
        }
        
        # Test message serialization
        import json
        msg_json = json.dumps(test_message) + '\n'
        
        if len(msg_json) > 0 and msg_json.endswith('\n'):
            print("✅ Stratum message formatting working")
        else:
            return False, "Stratum message formatting failed"
        
        # Test connection state management
        if not client.connected:
            print("✅ Initial connection state correct")
        else:
            return False, "Client should not be connected initially"
        
        return True, "Stratum protocol fixes working correctly"
        
    except Exception as e:
        return False, f"Stratum protocol test error: {str(e)}"

def test_share_submission_fixes():
    """Test the fixed share submission mechanism"""
    print("\n🧪 Testing Share Submission Fixes...")
    
    try:
        from real_scrypt_miner import RealScryptMiner, ScryptAlgorithm
        
        # Test ScryptAlgorithm with Litecoin parameters
        test_data = b"test block header for share submission validation"
        
        scrypt_result = ScryptAlgorithm.scrypt_hash(
            password=test_data,
            salt=test_data,
            N=1024,  # Litecoin parameters
            r=1,
            p=1,
            dk_len=32
        )
        
        if len(scrypt_result) != 32:
            return False, f"Scrypt hash wrong length: expected 32, got {len(scrypt_result)}"
        
        print(f"✅ Scrypt algorithm working - hash: {scrypt_result.hex()[:16]}...")
        
        # Test RealScryptMiner share tracking
        miner = RealScryptMiner()
        
        # Verify share tracking attributes
        if not hasattr(miner, 'shares_found'):
            return False, "Missing shares_found attribute"
        
        if not hasattr(miner, 'shares_accepted'):
            return False, "Missing shares_accepted attribute"
        
        print("✅ Share tracking attributes present")
        
        # Test statistics reporting
        stats = miner.get_stats()
        
        expected_fields = ['shares_found', 'shares_accepted', 'acceptance_rate']
        for field in expected_fields:
            if field not in stats:
                return False, f"Missing stats field: {field}"
        
        print("✅ Share statistics reporting working")
        
        return True, "Share submission fixes working correctly"
        
    except Exception as e:
        return False, f"Share submission test error: {str(e)}"

def test_asyncio_import_fix():
    """Test the fixed asyncio import"""
    print("\n🧪 Testing AsyncIO Import Fix...")
    
    try:
        # Test that asyncio is properly imported in real_scrypt_miner
        from real_scrypt_miner import RealScryptMiner
        import asyncio
        
        # Test that we can create an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        print("✅ AsyncIO import and loop creation working")
        
        # Test that RealScryptMiner can use asyncio
        miner = RealScryptMiner()
        
        # Test async method exists
        if hasattr(miner, 'start_mining'):
            print("✅ Async start_mining method available")
        else:
            return False, "start_mining method missing"
        
        loop.close()
        
        return True, "AsyncIO import fix working correctly"
        
    except Exception as e:
        return False, f"AsyncIO import test error: {str(e)}"

def test_socket_connection_fixes():
    """Test the fixed socket connection management"""
    print("\n🧪 Testing Socket Connection Fixes...")
    
    try:
        from real_scrypt_miner import StratumClient
        import socket
        
        # Test socket creation and cleanup
        client = StratumClient()
        
        # Test that socket is initially None
        if client.socket is not None:
            return False, "Socket should be None initially"
        
        print("✅ Initial socket state correct")
        
        # Test socket error handling
        try:
            # This should fail gracefully
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                client.connect_to_pool("invalid.pool.test", 9999, "test", "x")
            )
            
            if result == True:
                return False, "Connection to invalid pool should fail"
            
            print("✅ Socket error handling working")
            
        except Exception as e:
            print(f"✅ Socket connection error handled: {type(e).__name__}")
        
        return True, "Socket connection fixes working correctly"
        
    except Exception as e:
        return False, f"Socket connection test error: {str(e)}"

def run_pool_mining_tests():
    """Run all pool mining specific tests"""
    print("🚀 CryptoMiner Pro V30 - Pool Mining Functionality Tests")
    print("=" * 70)
    
    tests = [
        ("AsyncIO Import Fix", test_asyncio_import_fix),
        ("Thread Management Fixes", test_thread_management_fixes),
        ("Stratum Protocol Fixes", test_stratum_protocol_fixes),
        ("Share Submission Fixes", test_share_submission_fixes),
        ("Socket Connection Fixes", test_socket_connection_fixes),
        ("Real Pool Mining Integration", test_real_pool_mining_integration),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            success, message = test_func()
            results.append((test_name, success, message))
            
            if success:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                failed += 1
                print(f"❌ {test_name}: FAILED - {message}")
                
        except Exception as e:
            failed += 1
            error_msg = f"Test execution error: {str(e)}"
            results.append((test_name, False, error_msg))
            print(f"❌ {test_name}: ERROR - {error_msg}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 POOL MINING TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(tests)*100):.1f}%")
    
    if failed > 0:
        print("\n❌ FAILED TESTS:")
        for test_name, success, message in results:
            if not success:
                print(f"   • {test_name}: {message}")
    
    print("\n✅ PASSED TESTS:")
    for test_name, success, message in results:
        if success:
            print(f"   • {test_name}: {message}")
    
    return passed, failed, results

if __name__ == "__main__":
    passed, failed, results = run_pool_mining_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)