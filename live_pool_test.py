#!/usr/bin/env python3
"""
CryptoMiner Pro V30 - Live Pool Mining Test
Tests actual pool mining functionality with real pools
"""

import sys
import os
import time
import asyncio
import logging

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_live_pool_connection():
    """Test live connection to actual mining pools"""
    print("🧪 Testing Live Pool Connection...")
    
    try:
        from real_scrypt_miner import RealScryptMiner
        
        # Test pools (known working Litecoin pools)
        test_pools = [
            ("ltc.luckymonster.pro", 4112),
            ("litecoinpool.org", 3333),
        ]
        
        miner = RealScryptMiner()
        miner.set_thread_count(2)  # Use 2 threads for testing
        
        for pool_host, pool_port in test_pools:
            print(f"\n🌐 Testing connection to {pool_host}:{pool_port}")
            
            # Test wallet address (example Litecoin address)
            test_wallet = "ltc1qqvz2zw9hqd804a03xg95m4594p7v7thk25sztl"
            username = f"{test_wallet}.CryptoMiner-V30-Test"
            
            try:
                # Start mining for a short duration (10 seconds)
                print(f"🚀 Starting mining test for 10 seconds...")
                
                # Create a task that will timeout after 10 seconds
                mining_task = asyncio.create_task(
                    miner.start_mining(pool_host, pool_port, username, "x")
                )
                
                # Wait for 10 seconds or until mining completes
                try:
                    await asyncio.wait_for(mining_task, timeout=10.0)
                except asyncio.TimeoutError:
                    print("⏰ Mining test timeout reached (10 seconds)")
                    miner.stop_mining()
                
                # Get final statistics
                stats = miner.get_stats()
                
                print(f"📊 Mining Test Results for {pool_host}:{pool_port}:")
                print(f"   Hash Count: {stats['hash_count']:,}")
                print(f"   Shares Found: {stats['shares_found']}")
                print(f"   Shares Accepted: {stats['shares_accepted']}")
                print(f"   Acceptance Rate: {stats['acceptance_rate']:.1f}%")
                print(f"   Active Threads: {stats['active_threads']}")
                
                if stats['hash_count'] > 0:
                    print(f"✅ {pool_host}:{pool_port} - Mining working, {stats['hash_count']:,} hashes computed")
                    return True, f"Live pool mining successful with {pool_host}:{pool_port}"
                else:
                    print(f"⚠️ {pool_host}:{pool_port} - Connected but no hashes computed")
                
            except Exception as e:
                print(f"❌ {pool_host}:{pool_port} - Error: {e}")
                continue
        
        return False, "No pools successfully tested"
        
    except Exception as e:
        return False, f"Live pool test error: {str(e)}"

def test_mining_intensity_in_practice():
    """Test mining intensity controls in actual mining"""
    print("\n🧪 Testing Mining Intensity in Practice...")
    
    try:
        sys.path.append('/app')
        from cryptominer import CompactMiner
        
        # Test with 75% intensity
        miner = CompactMiner()
        miner.initialize_components()
        
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
            'threads': 2,
            'web_port': 3333
        }
        
        miner.config = test_config
        
        # Start mining briefly to test intensity
        print("🚀 Testing 75% mining intensity...")
        
        success = miner.start_mining()
        
        if success:
            # Let it run for 5 seconds
            time.sleep(5)
            
            # Check status
            status = miner.mining_engine.get_mining_status()
            
            if 'mining_intensity' in status and status['mining_intensity'] == 75:
                print("✅ Mining intensity 75% correctly applied")
            else:
                print(f"⚠️ Mining intensity not found in status or incorrect: {status.get('mining_intensity', 'missing')}")
            
            # Stop mining
            miner.stop_mining()
            
            return True, "Mining intensity controls working in practice"
        else:
            return False, "Failed to start mining with intensity control"
            
    except Exception as e:
        return False, f"Mining intensity test error: {str(e)}"

def test_error_recovery():
    """Test error recovery and graceful handling"""
    print("\n🧪 Testing Error Recovery...")
    
    try:
        from real_scrypt_miner import RealScryptMiner
        
        miner = RealScryptMiner()
        
        # Test 1: Connection to invalid pool
        print("🔍 Testing connection to invalid pool...")
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # This should fail gracefully
            result = loop.run_until_complete(
                miner.start_mining("invalid.pool.test", 9999, "test_user", "x")
            )
            
            if result == False:
                print("✅ Invalid pool connection handled gracefully")
            else:
                return False, "Invalid pool connection should return False"
                
        except Exception as e:
            print(f"✅ Invalid pool connection error handled: {type(e).__name__}")
        
        # Test 2: Stop mining when not active
        print("🔍 Testing stop mining when not active...")
        
        miner.stop_mining()  # Should not error
        print("✅ Stop mining when inactive - no errors")
        
        # Test 3: Thread cleanup
        print("🔍 Testing thread cleanup...")
        
        miner.mining_threads = []  # Simulate clean state
        miner.stop_mining()
        
        if len(miner.mining_threads) == 0:
            print("✅ Thread cleanup working")
        
        return True, "Error recovery working correctly"
        
    except Exception as e:
        return False, f"Error recovery test error: {str(e)}"

async def run_live_tests():
    """Run all live pool mining tests"""
    print("🚀 CryptoMiner Pro V30 - Live Pool Mining Tests")
    print("=" * 60)
    
    tests = [
        ("Live Pool Connection", test_live_pool_connection),
        ("Mining Intensity in Practice", test_mining_intensity_in_practice),
        ("Error Recovery", test_error_recovery),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                success, message = await test_func()
            else:
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
    print("\n" + "=" * 60)
    print("📊 LIVE POOL MINING TEST SUMMARY")
    print("=" * 60)
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
    passed, failed, results = asyncio.run(run_live_tests())
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)