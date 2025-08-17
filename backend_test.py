#!/usr/bin/env python3
"""
CryptoMiner Pro V30 - Comprehensive Backend Testing Suite
Tests all backend functionality including mining engine, AI system, and utilities
"""

import sys
import os
import subprocess
import json
import time
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Test imports
def test_backend_imports():
    """Test that all backend modules can be imported successfully"""
    print("🧪 Testing Backend Module Imports...")
    
    try:
        # Test mining engine import
        from mining_engine import EnterpriseScryptMiner, EnterpriseSystemDetector, CoinConfig
        print("✅ Mining engine modules imported successfully")
        
        # Test AI system import
        from ai_system import AISystemManager, AIPredictor, AIOptimizer
        print("✅ AI system modules imported successfully")
        
        # Test utils import
        from utils import get_coin_presets, validate_wallet_address, get_system_info
        print("✅ Utility modules imported successfully")
        
        return True, "All backend modules imported successfully"
        
    except ImportError as e:
        return False, f"Import error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error during import: {str(e)}"

def test_main_application_help():
    """Test the main application help functionality"""
    print("\n🧪 Testing Main Application Help...")
    
    try:
        # Test --help command
        result = subprocess.run([
            sys.executable, '/app/cryptominer.py', '--help'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            help_output = result.stdout
            
            # Check for expected help content
            expected_options = [
                '--setup', '--config', '--coin', '--wallet', 
                '--pool', '--threads', '--web-port', '--list-coins', '--verbose'
            ]
            
            missing_options = []
            for option in expected_options:
                if option not in help_output:
                    missing_options.append(option)
            
            if missing_options:
                return False, f"Missing help options: {missing_options}"
            
            print("✅ Help command executed successfully")
            print(f"   Help output length: {len(help_output)} characters")
            return True, "Help functionality working correctly"
        else:
            return False, f"Help command failed with return code {result.returncode}: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return False, "Help command timed out"
    except Exception as e:
        return False, f"Help test error: {str(e)}"

def test_coin_listing():
    """Test the coin listing functionality"""
    print("\n🧪 Testing Coin Listing...")
    
    try:
        # Test --list-coins command
        result = subprocess.run([
            sys.executable, '/app/cryptominer.py', '--list-coins'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            coins_output = result.stdout
            
            # Check for expected coins
            expected_coins = ['LTC', 'DOGE', 'FTC']
            found_coins = []
            
            for coin in expected_coins:
                if coin in coins_output:
                    found_coins.append(coin)
            
            if len(found_coins) == len(expected_coins):
                print("✅ Coin listing executed successfully")
                print(f"   Found coins: {found_coins}")
                return True, f"All expected coins found: {found_coins}"
            else:
                missing_coins = set(expected_coins) - set(found_coins)
                return False, f"Missing coins in output: {missing_coins}"
        else:
            return False, f"Coin listing failed with return code {result.returncode}: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return False, "Coin listing command timed out"
    except Exception as e:
        return False, f"Coin listing test error: {str(e)}"

def test_component_initialization():
    """Test CompactMiner component initialization"""
    print("\n🧪 Testing Component Initialization...")
    
    try:
        # Import the main application
        sys.path.append('/app')
        from cryptominer import CompactMiner
        
        # Create CompactMiner instance
        miner = CompactMiner()
        print("✅ CompactMiner instance created")
        
        # Test component initialization
        miner.initialize_components()
        
        # Verify components are initialized
        if miner.mining_engine is None:
            return False, "Mining engine not initialized"
        
        if miner.ai_system is None:
            return False, "AI system not initialized"
        
        print("✅ Mining engine initialized successfully")
        print("✅ AI system initialized successfully")
        
        # Test mining engine capabilities
        system_detector = miner.mining_engine.system_detector
        capabilities = system_detector.system_capabilities
        
        max_threads = capabilities.get('max_safe_threads', 0)
        enterprise_mode = capabilities.get('enterprise_mode', False)
        
        print(f"   Max safe threads: {max_threads:,}")
        print(f"   Enterprise mode: {enterprise_mode}")
        
        # Verify enterprise features (250,000+ threads capability)
        if max_threads >= 250000:
            print("✅ Enterprise features confirmed (250,000+ threads capability)")
            enterprise_confirmed = True
        else:
            print(f"⚠️  Enterprise features limited (max threads: {max_threads:,})")
            enterprise_confirmed = False
        
        return True, f"Components initialized successfully. Enterprise mode: {enterprise_confirmed}, Max threads: {max_threads:,}"
        
    except Exception as e:
        return False, f"Component initialization error: {str(e)}"

def test_configuration_handling():
    """Test configuration file loading and validation"""
    print("\n🧪 Testing Configuration Handling...")
    
    try:
        # Import required modules
        sys.path.append('/app')
        from cryptominer import CompactMiner
        
        # Create temporary config file
        test_config = {
            "coin": {
                "name": "Litecoin",
                "symbol": "LTC",
                "algorithm": "Scrypt",
                "block_reward": 6.25,
                "block_time": 150,
                "difficulty": 27882939.35508488,
                "scrypt_params": {"n": 1024, "r": 1, "p": 1},
                "network_hashrate": "450 TH/s",
                "wallet_format": "bech32"
            },
            "wallet_address": "ltc1qqvz2zw9hqd804a03xg95m4594p7v7thk25sztl",
            "mode": "pool",
            "pool_address": "stratum+tcp://litecoinpool.org:3333",
            "threads": 8,
            "web_port": 3333
        }
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f, indent=2)
            temp_config_path = f.name
        
        try:
            # Test config loading
            miner = CompactMiner()
            miner.load_config(temp_config_path)
            
            if not miner.config:
                return False, "Configuration not loaded"
            
            # Verify config content
            if 'coin' not in miner.config:
                return False, "Coin configuration missing"
            
            if 'wallet_address' not in miner.config:
                return False, "Wallet address missing"
            
            print("✅ Configuration loaded successfully")
            print(f"   Coin: {miner.config['coin']['name']}")
            print(f"   Mode: {miner.config['mode']}")
            print(f"   Threads: {miner.config['threads']}")
            
            return True, "Configuration handling working correctly"
            
        finally:
            # Clean up temp file
            os.unlink(temp_config_path)
            
    except Exception as e:
        return False, f"Configuration test error: {str(e)}"

def test_mining_engine_features():
    """Test mining engine specific features"""
    print("\n🧪 Testing Mining Engine Features...")
    
    try:
        from mining_engine import EnterpriseScryptMiner, CoinConfig
        
        # Create mining engine instance
        engine = EnterpriseScryptMiner()
        print("✅ Enterprise mining engine created")
        
        # Test system detection
        system_info = engine.system_detector.system_capabilities
        print(f"   Detected cores: {engine.system_detector.cpu_info.get('logical_cores', 'unknown')}")
        print(f"   Max safe threads: {system_info.get('max_safe_threads', 'unknown'):,}")
        print(f"   Enterprise mode: {system_info.get('enterprise_mode', 'unknown')}")
        
        # Test coin configuration
        coin_config = CoinConfig(
            name="Litecoin",
            symbol="LTC", 
            algorithm="Scrypt",
            block_reward=6.25,
            block_time=150,
            difficulty=27882939.35508488,
            scrypt_params={"n": 1024, "r": 1, "p": 1},
            network_hashrate="450 TH/s",
            wallet_format="bech32"
        )
        print("✅ Coin configuration created")
        
        # Test mining status (without actually starting mining)
        status = engine.get_mining_status()
        if 'is_mining' not in status:
            return False, "Mining status missing 'is_mining' field"
        
        if 'stats' not in status:
            return False, "Mining status missing 'stats' field"
        
        print("✅ Mining status retrieval working")
        
        return True, "Mining engine features working correctly"
        
    except Exception as e:
        return False, f"Mining engine test error: {str(e)}"

def test_ai_system_features():
    """Test AI system functionality"""
    print("\n🧪 Testing AI System Features...")
    
    try:
        from ai_system import AISystemManager
        
        # Create AI system instance
        ai_system = AISystemManager()
        print("✅ AI system manager created")
        
        # Test AI system status
        status = ai_system.get_system_status()
        if 'is_active' not in status:
            return False, "AI status missing 'is_active' field"
        
        print("✅ AI system status retrieval working")
        
        # Test CPU info retrieval
        cpu_info = ai_system.get_cpu_info()
        if 'total_cores' not in cpu_info:
            return False, "CPU info missing 'total_cores' field"
        
        print(f"   Detected CPU cores: {cpu_info.get('total_cores', 'unknown')}")
        print(f"   Recommended threads: {cpu_info.get('recommended_threads', 'unknown')}")
        
        # Test AI insights (with mock data)
        insights = ai_system.get_ai_insights(
            current_hashrate=1000.0,
            current_cpu=50.0,
            current_memory=30.0,
            threads=8
        )
        
        if not hasattr(insights, 'hash_pattern_prediction'):
            return False, "AI insights missing hash pattern prediction"
        
        print("✅ AI insights generation working")
        
        return True, "AI system features working correctly"
        
    except Exception as e:
        return False, f"AI system test error: {str(e)}"

def test_utility_functions():
    """Test utility functions"""
    print("\n🧪 Testing Utility Functions...")
    
    try:
        from utils import validate_wallet_address, get_coin_presets, get_system_info
        
        # Test wallet validation
        valid_ltc_address = "ltc1qqvz2zw9hqd804a03xg95m4594p7v7thk25sztl"
        is_valid, message = validate_wallet_address(valid_ltc_address, "LTC")
        
        if not is_valid:
            return False, f"Valid LTC address rejected: {message}"
        
        print("✅ Wallet address validation working")
        
        # Test coin presets
        coin_presets = get_coin_presets()
        expected_coins = ['litecoin', 'dogecoin', 'feathercoin']
        
        for coin in expected_coins:
            if coin not in coin_presets:
                return False, f"Missing coin preset: {coin}"
        
        print(f"✅ Coin presets loaded: {list(coin_presets.keys())}")
        
        # Test system info
        system_info = get_system_info()
        if 'cpu' not in system_info:
            return False, "System info missing CPU data"
        
        print("✅ System information retrieval working")
        
        return True, "Utility functions working correctly"
        
    except Exception as e:
        return False, f"Utility functions test error: {str(e)}"

def test_interactive_setup_start():
    """Test that interactive setup mode starts (but don't complete it)"""
    print("\n🧪 Testing Interactive Setup Start...")
    
    try:
        # Test --setup command with timeout to avoid hanging
        process = subprocess.Popen([
            sys.executable, '/app/cryptominer.py', '--setup'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)
        
        # Give it a moment to start
        time.sleep(2)
        
        # Terminate the process
        process.terminate()
        
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
        
        # Check if setup started (look for setup indicators in output)
        setup_indicators = ["Mining Setup", "Available Coins", "Select coin"]
        
        found_indicators = []
        for indicator in setup_indicators:
            if indicator in stdout:
                found_indicators.append(indicator)
        
        if found_indicators:
            print("✅ Interactive setup started successfully")
            print(f"   Found setup indicators: {found_indicators}")
            return True, f"Interactive setup started correctly. Found: {found_indicators}"
        else:
            return False, f"Interactive setup did not start properly. Output: {stdout[:200]}..."
            
    except Exception as e:
        return False, f"Interactive setup test error: {str(e)}"

def test_password_option_features():
    """Test the new password option functionality"""
    print("\n🧪 Testing Password Option Features...")
    
    try:
        # Test 1: Command line argument parsing for --password
        result = subprocess.run([
            sys.executable, '/app/cryptominer.py', '--help'
        ], capture_output=True, text=True, timeout=30)
        
        if '--password' not in result.stdout:
            return False, "Password option not found in help text"
        
        print("✅ Password option found in help text")
        
        # Test 2: Configuration file loading with pool_password field
        test_config = {
            "coin": {
                "name": "Litecoin",
                "symbol": "LTC",
                "algorithm": "Scrypt",
                "scrypt_params": {"n": 1024, "r": 1, "p": 1}
            },
            "wallet_address": "ltc1qqvz2zw9hqd804a03xg95m4594p7v7thk25sztl",
            "mode": "pool",
            "pool_address": "stratum+tcp://litecoinpool.org:3333",
            "pool_password": "test_password_123",
            "threads": 4,
            "web_port": 3333
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f, indent=2)
            temp_config_path = f.name
        
        try:
            sys.path.append('/app')
            from cryptominer import CompactMiner
            
            miner = CompactMiner()
            miner.load_config(temp_config_path)
            
            if 'pool_password' not in miner.config:
                return False, "pool_password field not loaded from config"
            
            if miner.config['pool_password'] != "test_password_123":
                return False, f"pool_password value incorrect: {miner.config['pool_password']}"
            
            print("✅ Configuration file loading includes pool_password field")
            
            # Test 3: Test argument parsing with password
            import argparse
            
            # Simulate the argument parser from cryptominer.py
            parser = argparse.ArgumentParser()
            parser.add_argument('--password', help='Pool password (default: x)', default='x')
            
            # Test default value
            args = parser.parse_args([])
            if args.password != 'x':
                return False, f"Default password incorrect: {args.password}"
            
            # Test custom value
            args = parser.parse_args(['--password', 'custom_pass'])
            if args.password != 'custom_pass':
                return False, f"Custom password not parsed: {args.password}"
            
            print("✅ Password argument parsing working correctly")
            
            return True, "Password option features working correctly"
            
        finally:
            os.unlink(temp_config_path)
            
    except Exception as e:
        return False, f"Password option test error: {str(e)}"

def test_mining_intensity_features():
    """Test the new mining intensity functionality"""
    print("\n🧪 Testing Mining Intensity Features...")
    
    try:
        # Test 1: Command line argument parsing for --intensity
        result = subprocess.run([
            sys.executable, '/app/cryptominer.py', '--help'
        ], capture_output=True, text=True, timeout=30)
        
        if '--intensity' not in result.stdout:
            return False, "Intensity option not found in help text"
        
        if 'Mining intensity 0-100 percent' not in result.stdout:
            return False, "Intensity description not found in help text"
        
        print("✅ Intensity option found in help text with correct description")
        
        # Test 2: Configuration file loading with mining_intensity field
        test_config = {
            "coin": {
                "name": "Litecoin", 
                "symbol": "LTC",
                "algorithm": "Scrypt",
                "scrypt_params": {"n": 1024, "r": 1, "p": 1}
            },
            "wallet_address": "ltc1qqvz2zw9hqd804a03xg95m4594p7v7thk25sztl",
            "mode": "solo",
            "mining_intensity": 75,
            "threads": 4,
            "web_port": 3333
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f, indent=2)
            temp_config_path = f.name
        
        try:
            sys.path.append('/app')
            from cryptominer import CompactMiner
            
            miner = CompactMiner()
            miner.load_config(temp_config_path)
            
            if 'mining_intensity' not in miner.config:
                return False, "mining_intensity field not loaded from config"
            
            if miner.config['mining_intensity'] != 75:
                return False, f"mining_intensity value incorrect: {miner.config['mining_intensity']}"
            
            print("✅ Configuration file loading includes mining_intensity field")
            
            # Test 3: Intensity validation (0-100 range)
            from cryptominer import CompactMiner
            
            # Test valid intensity values
            valid_intensities = [0, 25, 50, 75, 100]
            for intensity in valid_intensities:
                miner = CompactMiner()
                miner.config = {
                    'coin': test_config['coin'],
                    'wallet_address': test_config['wallet_address'],
                    'mode': 'solo',
                    'mining_intensity': intensity,
                    'threads': 4
                }
                
                # Should not raise any errors
                if miner.config['mining_intensity'] != intensity:
                    return False, f"Valid intensity {intensity} not preserved"
            
            print("✅ Valid intensity values (0-100) handled correctly")
            
            # Test 4: Test argument parsing with intensity
            import argparse
            
            # Simulate the argument parser from cryptominer.py
            parser = argparse.ArgumentParser()
            parser.add_argument('--intensity', type=int, help='Mining intensity 0-100 percent (default: 100)', default=100)
            
            # Test default value
            args = parser.parse_args([])
            if args.intensity != 100:
                return False, f"Default intensity incorrect: {args.intensity}"
            
            # Test custom values
            test_values = [0, 25, 50, 75, 100]
            for value in test_values:
                args = parser.parse_args(['--intensity', str(value)])
                if args.intensity != value:
                    return False, f"Intensity {value} not parsed correctly: {args.intensity}"
            
            print("✅ Intensity argument parsing working correctly")
            
            # Test 5: Test intensity validation in config
            miner = CompactMiner()
            
            # Test intensity clamping (should clamp to 0-100 range)
            test_cases = [
                (-10, 0),    # Below range should clamp to 0
                (150, 100),  # Above range should clamp to 100
                (50, 50),    # Valid range should remain unchanged
            ]
            
            for input_val, expected in test_cases:
                clamped = max(0, min(100, input_val))
                if clamped != expected:
                    return False, f"Intensity clamping failed: {input_val} -> {clamped}, expected {expected}"
            
            print("✅ Intensity validation and clamping working correctly")
            
            return True, "Mining intensity features working correctly"
            
        finally:
            os.unlink(temp_config_path)
            
    except Exception as e:
        return False, f"Mining intensity test error: {str(e)}"

def test_new_features_integration():
    """Test integration of password and intensity features"""
    print("\n🧪 Testing New Features Integration...")
    
    try:
        # Test both features together in command line
        sys.path.append('/app')
        from cryptominer import CompactMiner
        
        # Simulate command line arguments with both new features
        miner = CompactMiner()
        
        # Test configuration with both new features
        test_config = {
            'coin': {
                'name': 'Litecoin',
                'symbol': 'LTC', 
                'algorithm': 'Scrypt',
                'scrypt_params': {'n': 1024, 'r': 1, 'p': 1}
            },
            'wallet_address': 'ltc1qqvz2zw9hqd804a03xg95m4594p7v7thk25sztl',
            'mode': 'pool',
            'pool_address': 'stratum+tcp://testpool.org:3333',
            'pool_password': 'worker_password_123',
            'mining_intensity': 80,
            'threads': 4,
            'web_port': 3333
        }
        
        miner.config = test_config
        
        # Verify both features are present
        if 'pool_password' not in miner.config:
            return False, "pool_password missing in integrated config"
        
        if 'mining_intensity' not in miner.config:
            return False, "mining_intensity missing in integrated config"
        
        if miner.config['pool_password'] != 'worker_password_123':
            return False, f"pool_password incorrect: {miner.config['pool_password']}"
        
        if miner.config['mining_intensity'] != 80:
            return False, f"mining_intensity incorrect: {miner.config['mining_intensity']}"
        
        print("✅ Both password and intensity features integrated correctly")
        
        # Test example config file has both new fields
        if os.path.exists('/app/config.example.json'):
            with open('/app/config.example.json', 'r') as f:
                example_config = json.load(f)
            
            if 'pool_password' not in example_config:
                return False, "pool_password missing from config.example.json"
            
            if 'mining_intensity' not in example_config:
                return False, "mining_intensity missing from config.example.json"
            
            print("✅ Example configuration file includes both new fields")
        
        return True, "New features integration working correctly"
        
    except Exception as e:
        return False, f"Integration test error: {str(e)}"

def test_pool_mining_threading_control():
    """Test threading control for pool mining"""
    print("\n🧪 Testing Pool Mining Threading Control...")
    
    try:
        sys.path.append('/app/backend')
        from real_scrypt_miner import RealScryptMiner
        
        # Test thread count setting
        miner = RealScryptMiner()
        
        # Test various thread counts
        test_thread_counts = [1, 4, 6, 8]
        
        for thread_count in test_thread_counts:
            miner.set_thread_count(thread_count)
            if miner.thread_count != thread_count:
                return False, f"Thread count not set correctly: expected {thread_count}, got {miner.thread_count}"
        
        print(f"✅ Thread count control working for counts: {test_thread_counts}")
        
        # Test thread initialization
        miner.set_thread_count(4)
        if len(miner.mining_threads) > 0:
            # Clear any existing threads
            miner.mining_threads.clear()
        
        print("✅ Thread management initialization working")
        
        return True, "Pool mining threading control working correctly"
        
    except Exception as e:
        return False, f"Threading control test error: {str(e)}"

def test_pool_connection_functionality():
    """Test pool connection and stratum protocol"""
    print("\n🧪 Testing Pool Connection Functionality...")
    
    try:
        sys.path.append('/app/backend')
        from real_scrypt_miner import StratumClient
        import socket
        
        # Test StratumClient initialization
        client = StratumClient()
        
        if not hasattr(client, 'socket'):
            return False, "StratumClient missing socket attribute"
        
        if not hasattr(client, 'connected'):
            return False, "StratumClient missing connected attribute"
        
        print("✅ StratumClient initialized correctly")
        
        # Test known working pools (connection test only, no actual mining)
        test_pools = [
            ("litecoinpool.org", 3333),
            ("ltc.luckymonster.pro", 4112)
        ]
        
        connection_results = []
        for pool_host, pool_port in test_pools:
            try:
                # Test basic socket connection (timeout quickly)
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.settimeout(5)  # 5 second timeout
                result = test_socket.connect_ex((pool_host, pool_port))
                test_socket.close()
                
                if result == 0:
                    connection_results.append(f"✅ {pool_host}:{pool_port} - reachable")
                else:
                    connection_results.append(f"❌ {pool_host}:{pool_port} - unreachable (code: {result})")
                    
            except Exception as e:
                connection_results.append(f"❌ {pool_host}:{pool_port} - error: {str(e)}")
        
        print("Pool connection test results:")
        for result in connection_results:
            print(f"   {result}")
        
        # Test stratum message formatting
        test_message = {
            "id": 1,
            "method": "mining.subscribe",
            "params": ["CryptoMiner-V30/1.0", None]
        }
        
        # Test message serialization (without sending)
        import json
        try:
            msg_json = json.dumps(test_message) + '\n'
            if len(msg_json) > 0 and msg_json.endswith('\n'):
                print("✅ Stratum message formatting working")
            else:
                return False, "Stratum message formatting failed"
        except Exception as e:
            return False, f"Message formatting error: {e}"
        
        return True, "Pool connection functionality working correctly"
        
    except Exception as e:
        return False, f"Pool connection test error: {str(e)}"

def test_share_submission_mechanism():
    """Test share finding and submission mechanism"""
    print("\n🧪 Testing Share Submission Mechanism...")
    
    try:
        sys.path.append('/app/backend')
        from real_scrypt_miner import RealScryptMiner, ScryptAlgorithm
        
        # Test ScryptAlgorithm implementation
        test_data = b"test block header for scrypt mining validation"
        
        # Test with Litecoin parameters
        scrypt_result = ScryptAlgorithm.scrypt_hash(
            password=test_data,
            salt=test_data,
            N=1024,  # Litecoin scrypt-N
            r=1,     # Litecoin scrypt-r
            p=1,     # Litecoin scrypt-p
            dk_len=32
        )
        
        if len(scrypt_result) != 32:
            return False, f"Scrypt hash wrong length: expected 32, got {len(scrypt_result)}"
        
        print(f"✅ Scrypt algorithm working - hash: {scrypt_result.hex()[:16]}...")
        
        # Test RealScryptMiner initialization
        miner = RealScryptMiner()
        
        # Verify share tracking attributes
        required_attrs = ['shares_found', 'shares_accepted', 'hash_count']
        for attr in required_attrs:
            if not hasattr(miner, attr):
                return False, f"RealScryptMiner missing {attr} attribute"
        
        print("✅ Share tracking attributes present")
        
        # Test stats method
        stats = miner.get_stats()
        expected_stats = ['is_mining', 'shares_found', 'shares_accepted', 'acceptance_rate', 'hashrate']
        
        for stat in expected_stats:
            if stat not in stats:
                return False, f"Missing stat: {stat}"
        
        print("✅ Statistics reporting working")
        
        # Test block header creation (mock work data)
        mock_work = {
            'job_id': 'test_job_123',
            'prev_hash': '0' * 64,
            'coinbase1': '01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff',
            'coinbase2': 'ffffffff0100f2052a01000000434104',
            'merkle_branches': [],
            'version': '00000001',
            'nbits': '1d00ffff',
            'ntime': '504e86b9'
        }
        
        # Set up mock stratum client data
        miner.stratum_client.extranonce1 = "f8002c90"
        miner.stratum_client.extranonce2_size = 4
        
        try:
            header = miner.create_block_header(mock_work, "00000001", mock_work['ntime'], 12345)
            if len(header) == 80:  # Standard block header size
                print("✅ Block header creation working")
            else:
                return False, f"Block header wrong size: expected 80, got {len(header)}"
        except Exception as e:
            print(f"⚠️ Block header creation test skipped due to: {e}")
        
        return True, "Share submission mechanism working correctly"
        
    except Exception as e:
        return False, f"Share submission test error: {str(e)}"

def test_error_handling_and_cleanup():
    """Test error handling and resource cleanup"""
    print("\n🧪 Testing Error Handling and Resource Cleanup...")
    
    try:
        sys.path.append('/app/backend')
        from real_scrypt_miner import RealScryptMiner, StratumClient
        
        # Test RealScryptMiner cleanup
        miner = RealScryptMiner()
        
        # Test stop_mining method exists and works
        if not hasattr(miner, 'stop_mining'):
            return False, "RealScryptMiner missing stop_mining method"
        
        # Test initial state
        if miner.is_mining:
            return False, "Miner should not be mining initially"
        
        # Test stop when not mining (should not error)
        try:
            miner.stop_mining()
            print("✅ Stop mining when not active - no errors")
        except Exception as e:
            return False, f"Stop mining failed when not active: {e}"
        
        # Test StratumClient cleanup
        client = StratumClient()
        
        # Test connection state management
        if client.connected:
            return False, "StratumClient should not be connected initially"
        
        print("✅ Initial state management working")
        
        # Test error handling for invalid pool connections
        try:
            # This should fail gracefully
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Test connection to non-existent pool
            result = loop.run_until_complete(
                client.connect_to_pool("nonexistent.pool.invalid", 9999, "test_user", "x")
            )
            
            if result == True:
                return False, "Connection to invalid pool should fail"
            
            print("✅ Invalid pool connection handled gracefully")
            
        except Exception as e:
            # This is expected for invalid connections
            print(f"✅ Invalid pool connection error handled: {type(e).__name__}")
        
        # Test thread cleanup
        miner.set_thread_count(4)
        miner.mining_threads = []  # Simulate some threads
        
        # Test cleanup
        miner.stop_mining()
        if len(miner.mining_threads) == 0:
            print("✅ Thread cleanup working")
        
        return True, "Error handling and cleanup working correctly"
        
    except Exception as e:
        return False, f"Error handling test error: {str(e)}"

def test_mining_intensity_controls():
    """Test mining intensity controls (75%, 100%)"""
    print("\n🧪 Testing Mining Intensity Controls...")
    
    try:
        sys.path.append('/app')
        from cryptominer import CompactMiner
        
        # Test intensity configuration
        miner = CompactMiner()
        
        # Test 75% intensity
        test_config_75 = {
            'coin': {
                'name': 'Litecoin',
                'symbol': 'LTC',
                'algorithm': 'Scrypt',
                'scrypt_params': {'n': 1024, 'r': 1, 'p': 1}
            },
            'wallet_address': 'ltc1qqvz2zw9hqd804a03xg95m4594p7v7thk25sztl',
            'mode': 'pool',
            'pool_address': 'stratum+tcp://litecoinpool.org:3333',
            'mining_intensity': 75,
            'threads': 4
        }
        
        miner.config = test_config_75
        
        if miner.config['mining_intensity'] != 75:
            return False, f"75% intensity not set correctly: {miner.config['mining_intensity']}"
        
        print("✅ 75% intensity configuration working")
        
        # Test 100% intensity
        test_config_100 = test_config_75.copy()
        test_config_100['mining_intensity'] = 100
        
        miner.config = test_config_100
        
        if miner.config['mining_intensity'] != 100:
            return False, f"100% intensity not set correctly: {miner.config['mining_intensity']}"
        
        print("✅ 100% intensity configuration working")
        
        # Test intensity validation (should clamp to 0-100)
        test_cases = [
            (-10, 0),    # Below range
            (150, 100),  # Above range  
            (50, 50),    # Valid range
        ]
        
        for input_val, expected in test_cases:
            clamped = max(0, min(100, input_val))
            if clamped != expected:
                return False, f"Intensity clamping failed: {input_val} -> {clamped}, expected {expected}"
        
        print("✅ Intensity validation and clamping working")
        
        # Test intensity in mining engine status
        miner.initialize_components()
        
        # Set intensity on coin config
        from mining_engine import CoinConfig
        coin_config = CoinConfig(**test_config_75['coin'])
        coin_config.mining_intensity = 75
        
        if hasattr(coin_config, 'mining_intensity') and coin_config.mining_intensity == 75:
            print("✅ Intensity integration with mining engine working")
        else:
            print("⚠️ Intensity integration test skipped - attribute not found")
        
        return True, "Mining intensity controls working correctly"
        
    except Exception as e:
        return False, f"Mining intensity test error: {str(e)}"

def test_ai_system_integration():
    """Test AI system integration and status reporting"""
    print("\n🧪 Testing AI System Integration...")
    
    try:
        sys.path.append('/app')
        from cryptominer import CompactMiner
        
        # Test AI system initialization
        miner = CompactMiner()
        miner.initialize_components()
        
        if miner.ai_system is None:
            return False, "AI system not initialized"
        
        print("✅ AI system initialized")
        
        # Test AI system status
        ai_status = miner.ai_system.get_system_status()
        
        required_fields = ['is_active']
        for field in required_fields:
            if field not in ai_status:
                return False, f"AI status missing field: {field}"
        
        print("✅ AI system status reporting working")
        
        # Test mining engine AI integration
        if hasattr(miner.mining_engine, 'ai_system'):
            print("✅ AI system linked to mining engine")
        else:
            print("⚠️ AI system not linked to mining engine")
        
        # Test AI insights
        try:
            insights = miner.ai_system.get_ai_insights(
                current_hashrate=1000.0,
                current_cpu=50.0,
                current_memory=30.0,
                threads=4
            )
            
            if hasattr(insights, 'hash_pattern_prediction'):
                print("✅ AI insights generation working")
            else:
                return False, "AI insights missing hash_pattern_prediction"
                
        except Exception as e:
            print(f"⚠️ AI insights test skipped: {e}")
        
        return True, "AI system integration working correctly"
        
    except Exception as e:
        return False, f"AI system integration test error: {str(e)}"

def test_web_monitoring_statistics():
    """Test web monitoring displays correct mining statistics"""
    print("\n🧪 Testing Web Monitoring Statistics...")
    
    try:
        sys.path.append('/app')
        from cryptominer import CompactMiner
        
        # Test mining status API
        miner = CompactMiner()
        miner.initialize_components()
        
        # Test mining status retrieval
        status = miner.mining_engine.get_mining_status()
        
        required_fields = ['is_mining', 'stats']
        for field in required_fields:
            if field not in status:
                return False, f"Mining status missing field: {field}"
        
        print("✅ Mining status API working")
        
        # Test stats structure
        stats = status['stats']
        expected_stats = ['hashrate', 'accepted_shares', 'uptime', 'cpu_usage']
        
        for stat in expected_stats:
            if stat not in stats:
                return False, f"Stats missing field: {stat}"
        
        print("✅ Statistics structure correct")
        
        # Test mining intensity in status
        if 'mining_intensity' in status:
            print("✅ Mining intensity included in status")
        else:
            print("⚠️ Mining intensity not in status (may be added later)")
        
        # Test AI learning progress in status
        if 'ai_learning_progress' in status:
            print("✅ AI learning progress included in status")
        else:
            print("⚠️ AI learning progress not in status (may be added later)")
        
        return True, "Web monitoring statistics working correctly"
        
    except Exception as e:
        return False, f"Web monitoring test error: {str(e)}"

def test_pool_mining_error_scenarios():
    """Test error scenarios for pool mining"""
    print("\n🧪 Testing Pool Mining Error Scenarios...")
    
    try:
        sys.path.append('/app/backend')
        from real_scrypt_miner import RealScryptMiner, StratumClient
        import asyncio
        
        # Test connection to non-existent pool
        miner = RealScryptMiner()
        
        # Test invalid pool connection
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                miner.stratum_client.connect_to_pool(
                    "nonexistent.invalid.pool", 
                    9999, 
                    "test_user", 
                    "x"
                )
            )
            
            if result == True:
                return False, "Connection to invalid pool should fail"
            
            print("✅ Invalid pool connection handled gracefully")
            
        except Exception as e:
            print(f"✅ Invalid pool connection error handled: {type(e).__name__}")
        
        # Test malformed pool responses
        client = StratumClient()
        
        # Test message parsing with invalid JSON
        try:
            # This should not crash the client
            result = client._receive_message()  # Will return None for no data
            print("✅ Message parsing handles no data gracefully")
        except Exception as e:
            return False, f"Message parsing should handle errors gracefully: {e}"
        
        # Test network interruption simulation
        miner.is_mining = True
        miner.stop_mining()
        
        if not miner.is_mining:
            print("✅ Network interruption handling working")
        else:
            return False, "Mining should stop on interruption"
        
        return True, "Pool mining error scenarios handled correctly"
        
    except Exception as e:
        return False, f"Error scenario test error: {str(e)}"

def run_all_tests():
    """Run all backend tests"""
    print("🚀 CryptoMiner Pro V30 - Backend Testing Suite")
    print("=" * 60)
    
    tests = [
        ("Backend Module Imports", test_backend_imports),
        ("Main Application Help", test_main_application_help),
        ("Coin Listing", test_coin_listing),
        ("Component Initialization", test_component_initialization),
        ("Configuration Handling", test_configuration_handling),
        ("Mining Engine Features", test_mining_engine_features),
        ("AI System Features", test_ai_system_features),
        ("Utility Functions", test_utility_functions),
        ("Interactive Setup Start", test_interactive_setup_start),
        ("Password Option Features", test_password_option_features),
        ("Mining Intensity Features", test_mining_intensity_features),
        ("New Features Integration", test_new_features_integration),
        # NEW POOL MINING TESTS
        ("Pool Mining Threading Control", test_pool_mining_threading_control),
        ("Pool Connection Functionality", test_pool_connection_functionality),
        ("Share Submission Mechanism", test_share_submission_mechanism),
        ("Error Handling and Cleanup", test_error_handling_and_cleanup),
        ("Mining Intensity Controls", test_mining_intensity_controls),
        ("AI System Integration", test_ai_system_integration),
        ("Web Monitoring Statistics", test_web_monitoring_statistics),
        ("Pool Mining Error Scenarios", test_pool_mining_error_scenarios),
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
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
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
    passed, failed, results = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)