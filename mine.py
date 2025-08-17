#!/usr/bin/env python3
"""
CryptoMiner Pro V30 - Terminal Mining Application
Enhanced terminal-based mining with web monitoring interface
"""

import argparse
import asyncio
import json
import logging
import os
import signal
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

# Import existing modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from mining_engine import MiningEngine, SystemDetector
from ai_system import AISystem
from utils import get_coin_presets, validate_wallet_address
from enterprise_v30 import CentralControlSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('mining.log')
    ]
)

logger = logging.getLogger(__name__)

class TerminalMiner:
    def __init__(self):
        self.mining_engine = None
        self.ai_system = None
        self.v30_system = None
        self.web_monitor = None
        self.config = {}
        self.running = False
        self.stats = {
            'start_time': None,
            'total_hashes': 0,
            'blocks_found': 0,
            'shares_submitted': 0,
            'last_hashrate': 0
        }
        
    def setup_signal_handlers(self):
        """Setup graceful shutdown on Ctrl+C"""
        def signal_handler(sig, frame):
            print(f"\n🛑 Received signal {sig}. Shutting down gracefully...")
            self.stop_mining()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    def print_banner(self):
        """Display application banner"""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║                CryptoMiner Pro V30                        ║
║            Terminal Mining Application                    ║
║                                                          ║
║  🚀 Enterprise-Grade Mining Engine                       ║
║  🔗 Pool & Solo Mining Support                          ║
║  🤖 AI-Powered Optimization                             ║
║  📊 Real-time Web Monitoring                            ║
╚═══════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def load_config(self, config_file='mining_config.json'):
        """Load configuration from file"""
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"✅ Configuration loaded from {config_file}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load config: {e}")
                
    def save_config(self, config_file='mining_config.json'):
        """Save current configuration"""
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"✅ Configuration saved to {config_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save config: {e}")
            
    def initialize_components(self):
        """Initialize mining engine and AI system"""
        try:
            # Initialize system detector
            system_detector = SystemDetector()
            
            # Initialize mining engine
            self.mining_engine = MiningEngine(system_detector)
            logger.info("✅ Mining engine initialized")
            
            # Initialize AI system
            self.ai_system = AISystem()
            logger.info("✅ AI system initialized")
            
            # Initialize V30 enterprise features if available
            try:
                from enterprise_v30 import CentralControlSystem
                self.v30_system = CentralControlSystem()
                logger.info("✅ V30 Enterprise system initialized")
            except Exception as e:
                logger.warning(f"⚠️ V30 Enterprise features unavailable: {e}")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize components: {e}")
            raise
            
    def setup_interactive_mode(self):
        """Interactive configuration setup"""
        print("\n🔧 Interactive Mining Setup")
        print("=" * 50)
        
        # Coin selection
        coin_presets = get_coin_presets()
        print("\n📈 Available Coins:")
        for i, (coin_key, coin_data) in enumerate(coin_presets.items(), 1):
            print(f"  {i}. {coin_data['name']} ({coin_data['symbol']})")
            
        while True:
            try:
                choice = int(input(f"\nSelect coin (1-{len(coin_presets)}): ")) - 1
                coin_key = list(coin_presets.keys())[choice]
                coin_data = coin_presets[coin_key]
                break
            except (ValueError, IndexError):
                print("❌ Invalid choice. Please try again.")
                
        self.config['coin'] = coin_data
        
        # Wallet address
        while True:
            wallet = input(f"\n💰 Enter your {coin_data['symbol']} wallet address: ").strip()
            if wallet:
                is_valid, message = validate_wallet_address(wallet, coin_data['symbol'])
                if is_valid:
                    self.config['wallet_address'] = wallet
                    print(f"✅ {message}")
                    break
                else:
                    print(f"❌ {message}")
            else:
                print("❌ Wallet address cannot be empty.")
                
        # Mining mode
        print("\n⛏️ Mining Mode:")
        print("  1. Pool Mining (Recommended)")
        print("  2. Solo Mining")
        
        mode_choice = input("Select mode (1-2): ").strip()
        if mode_choice == "2":
            self.config['mode'] = 'solo'
            print("✅ Solo mining selected")
        else:
            self.config['mode'] = 'pool'
            print("✅ Pool mining selected")
            
            # Pool configuration
            pool_address = input(f"\n🏊 Pool address (default: {coin_data.get('default_pool', 'stratum+tcp://pool.com:4444')}): ").strip()
            if not pool_address:
                pool_address = coin_data.get('default_pool', 'stratum+tcp://pool.com:4444')
                
            self.config['pool_address'] = pool_address
            
            # Parse pool address and port
            if 'stratum+tcp://' in pool_address:
                pool_parts = pool_address.replace('stratum+tcp://', '').split(':')
                self.config['pool_host'] = pool_parts[0]
                self.config['pool_port'] = int(pool_parts[1]) if len(pool_parts) > 1 else 4444
            else:
                self.config['pool_host'] = pool_address
                self.config['pool_port'] = int(input("Pool port (default: 4444): ") or 4444)
                
        # Thread configuration  
        max_threads = self.mining_engine.system_detector.system_capabilities.get('max_safe_threads', 4)
        print(f"\n🧵 Thread Configuration (Max safe: {max_threads}):")
        print("  1. Auto-detect optimal threads")
        print("  2. Specify custom thread count")
        
        thread_choice = input("Select option (1-2): ").strip()
        if thread_choice == "2":
            while True:
                try:
                    threads = int(input(f"Enter thread count (1-{max_threads}): "))
                    if 1 <= threads <= max_threads:
                        self.config['threads'] = threads
                        break
                    else:
                        print(f"❌ Thread count must be between 1 and {max_threads}")
                except ValueError:
                    print("❌ Invalid number. Please try again.")
        else:
            self.config['threads'] = self.mining_engine.system_detector.get_recommended_threads(0.75)
            
        # Web monitoring
        web_port = input("\n📊 Web monitoring port (default: 3333): ").strip()
        self.config['web_port'] = int(web_port) if web_port else 3333
        
        print(f"\n✅ Configuration complete!")
        print(f"   Coin: {coin_data['name']} ({coin_data['symbol']})")
        print(f"   Mode: {self.config['mode']}")
        print(f"   Threads: {self.config['threads']}")
        print(f"   Web Monitor: http://localhost:{self.config['web_port']}")
        
        # Save configuration
        save_config = input("\n💾 Save configuration? (Y/n): ").strip().lower()
        if save_config != 'n':
            self.save_config()
            
    def start_mining(self):
        """Start the mining process"""
        if not self.config:
            logger.error("❌ No configuration found. Please run --setup first.")
            return False
            
        try:
            print(f"\n🚀 Starting mining...")
            print(f"   Coin: {self.config['coin']['name']} ({self.config['coin']['symbol']})")
            print(f"   Threads: {self.config['threads']}")
            print(f"   Mode: {self.config['mode']}")
            
            # Create coin config from existing coin data
            from mining_engine import CoinConfig
            coin_config = CoinConfig(**self.config['coin'])
            
            # Start mining
            success, message = self.mining_engine.start_mining(
                coin_config,
                self.config['wallet_address'],
                self.config['threads']
            )
            
            if success:
                self.running = True
                self.stats['start_time'] = datetime.now()
                print(f"✅ {message}")
                return True
            else:
                print(f"❌ Failed to start mining: {message}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Mining startup error: {e}")
            return False
            
    def stop_mining(self):
        """Stop the mining process"""
        if self.mining_engine and self.running:
            print("\n🛑 Stopping mining...")
            success, message = self.mining_engine.stop_mining()
            self.running = False
            
            if success:
                print(f"✅ {message}")
            else:
                print(f"⚠️ {message}")
                
            # Show final stats
            self.show_final_stats()
        else:
            print("⚠️ Mining is not currently running")
            
    def show_stats(self):
        """Display current mining statistics"""
        if not self.mining_engine or not self.running:
            return
            
        try:
            status = self.mining_engine.get_mining_status()
            stats = status.get('stats', {})
            
            # Update internal stats
            self.stats['last_hashrate'] = stats.get('hashrate', 0)
            self.stats['total_hashes'] += stats.get('hashes', 0)
            
            # Clear screen and show stats
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print("╔═══════════════════════════════════════════════════════════╗")
            print("║                    MINING STATISTICS                     ║")
            print("╠═══════════════════════════════════════════════════════════╣")
            
            # Runtime
            if self.stats['start_time']:
                runtime = datetime.now() - self.stats['start_time']
                print(f"║  ⏱️  Runtime: {str(runtime).split('.')[0]:<42} ║")
                
            # Hashrate
            hashrate = stats.get('hashrate', 0)
            if hashrate > 1000000:
                hashrate_str = f"{hashrate/1000000:.2f} MH/s"
            elif hashrate > 1000:
                hashrate_str = f"{hashrate/1000:.2f} KH/s"
            else:
                hashrate_str = f"{hashrate:.2f} H/s"
            print(f"║  ⚡ Hashrate: {hashrate_str:<43} ║")
            
            # System stats
            cpu_usage = stats.get('cpu_usage', 0)
            temp = stats.get('temperature', 0)
            print(f"║  🖥️  CPU Usage: {cpu_usage:.1f}%{'':<37} ║")
            print(f"║  🌡️  Temperature: {temp:.1f}°C{'':<35} ║")
            
            # Mining stats
            accepted = stats.get('accepted_shares', 0)
            rejected = stats.get('rejected_shares', 0)
            efficiency = (accepted / (accepted + rejected)) * 100 if (accepted + rejected) > 0 else 0
            print(f"║  ✅ Accepted: {accepted:<42} ║")
            print(f"║  ❌ Rejected: {rejected:<42} ║")
            print(f"║  📊 Efficiency: {efficiency:.2f}%{'':<36} ║")
            
            print("╠═══════════════════════════════════════════════════════════╣")
            print(f"║  📊 Web Monitor: http://localhost:{self.config.get('web_port', 3333):<25} ║")
            print("║  🛑 Press Ctrl+C to stop mining{:<27} ║")
            print("╚═══════════════════════════════════════════════════════════╝")
            
        except Exception as e:
            logger.error(f"Error displaying stats: {e}")
            
    def show_final_stats(self):
        """Show final mining statistics"""
        if self.stats['start_time']:
            runtime = datetime.now() - self.stats['start_time']
            print(f"\n📊 Final Mining Statistics:")
            print(f"   Runtime: {str(runtime).split('.')[0]}")
            print(f"   Average Hashrate: {self.stats['last_hashrate']:.2f} H/s")
            print(f"   Total Hashes: {self.stats['total_hashes']:,}")
            print(f"   Blocks Found: {self.stats['blocks_found']}")
            print(f"   Shares Submitted: {self.stats['shares_submitted']}")
            
    def run_mining_loop(self):
        """Main mining loop with stats display"""
        while self.running:
            try:
                self.show_stats()
                time.sleep(5)  # Update every 5 seconds
            except KeyboardInterrupt:
                break
                
        self.stop_mining()
        
def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description='CryptoMiner Pro V30 - Terminal Mining Application',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 mine.py --setup                          # Interactive setup
  python3 mine.py --coin LTC --wallet ltc1xxx... --pool stratum+tcp://pool.com:4444 --threads 8
  python3 mine.py --config my_config.json         # Use saved configuration
  python3 mine.py --list-coins                    # Show available coins
        """
    )
    
    parser.add_argument('--setup', action='store_true', help='Interactive configuration setup')
    parser.add_argument('--config', help='Configuration file to use')
    parser.add_argument('--coin', help='Coin symbol (LTC, DOGE, FTC)')
    parser.add_argument('--wallet', help='Wallet address')
    parser.add_argument('--pool', help='Pool address (stratum+tcp://pool:port)')
    parser.add_argument('--threads', type=int, help='Number of mining threads')
    parser.add_argument('--web-port', type=int, default=3333, help='Web monitor port')
    parser.add_argument('--list-coins', action='store_true', help='List available coins')
    parser.add_argument('--no-web', action='store_true', help='Disable web monitoring')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Create miner instance
    miner = TerminalMiner()
    miner.setup_signal_handlers()
    miner.print_banner()
    
    # Handle list coins command
    if args.list_coins:
        print("\n📈 Available Coins:")
        coin_presets = get_coin_presets()
        for coin_key, coin_data in coin_presets.items():
            print(f"  {coin_data['symbol']:<6} - {coin_data['name']}")
            print(f"         Algorithm: {coin_data['algorithm']}")
            print(f"         Default Pool: {coin_data.get('default_pool', 'N/A')}")
            print()
        return
        
    try:
        # Initialize components
        miner.initialize_components()
        
        # Load configuration
        if args.config:
            miner.load_config(args.config)
        else:
            miner.load_config()
            
        # Setup mode
        if args.setup:
            miner.setup_interactive_mode()
            return
            
        # Command line configuration
        if args.coin or args.wallet or args.pool:
            if not all([args.coin, args.wallet]):
                print("❌ --coin and --wallet are required when specifying mining parameters")
                return
                
            # Get coin data
            coin_presets = get_coin_presets()
            coin_data = None
            for coin_key, coin_info in coin_presets.items():
                if coin_info['symbol'].upper() == args.coin.upper():
                    coin_data = coin_info
                    break
                    
            if not coin_data:
                print(f"❌ Unsupported coin: {args.coin}")
                print("Use --list-coins to see available options")
                return
                
            # Validate wallet
            is_valid, message = validate_wallet_address(args.wallet, coin_data['symbol'])
            if not is_valid:
                print(f"❌ {message}")
                return
                
            # Build configuration
            miner.config = {
                'coin': coin_data,
                'wallet_address': args.wallet,
                'mode': 'pool' if args.pool else 'solo',
                'threads': args.threads or miner.mining_engine.system_detector.get_recommended_threads(0.75),
                'web_port': args.web_port
            }
            
            if args.pool:
                miner.config['pool_address'] = args.pool
                if 'stratum+tcp://' in args.pool:
                    pool_parts = args.pool.replace('stratum+tcp://', '').split(':')
                    miner.config['pool_host'] = pool_parts[0]
                    miner.config['pool_port'] = int(pool_parts[1]) if len(pool_parts) > 1 else 4444
                    
        # Check if we have configuration
        if not miner.config:
            print("\n⚠️  No configuration found!")
            print("Use one of these options:")
            print("  python3 mine.py --setup                    # Interactive setup")
            print("  python3 mine.py --coin LTC --wallet ...    # Command line setup")
            print("  python3 mine.py --config config.json       # Use saved config")
            return
            
        # Start web monitoring (if not disabled)
        if not args.no_web:
            try:
                from web_monitor import WebMonitor
                miner.web_monitor = WebMonitor(miner.mining_engine, port=miner.config['web_port'])
                miner.web_monitor.start()
                print(f"📊 Web monitor started: http://localhost:{miner.config['web_port']}")
            except Exception as e:
                logger.warning(f"⚠️ Web monitor failed to start: {e}")
                print("   Continuing without web monitoring...")
                
        # Start mining
        if miner.start_mining():
            print(f"\n⛏️ Mining in progress... Press Ctrl+C to stop")
            miner.run_mining_loop()
        else:
            print("❌ Failed to start mining")
            
    except Exception as e:
        logger.error(f"❌ Application error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())