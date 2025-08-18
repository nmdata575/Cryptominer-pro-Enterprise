#!/usr/bin/env python3
"""
🚀 CryptoMiner Pro V30 🚀
Enterprise-scale distributed mining platform
Consolidated terminal-based mining application with optional web monitoring
"""

import argparse
import asyncio
import logging
import signal
import sys
import os
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('mining.log')
    ]
)
logger = logging.getLogger(__name__)

# Import mining components
try:
    from mining_engine import MiningEngine
    from ai_optimizer import AIOptimizer
except ImportError as e:
    logger.error(f"Failed to import mining components: {e}")
    sys.exit(1)

class CryptoMinerPro:
    def __init__(self):
        self.mining_engine = None
        self.ai_optimizer = None
        self.web_server_task = None
        self.running = False
        self.shutdown_event = asyncio.Event()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C and termination signals gracefully"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        if self.running:
            # Create shutdown task in the current event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.shutdown())
                else:
                    asyncio.run(self.shutdown())
            except RuntimeError:
                # No event loop running, create new one
                asyncio.run(self.shutdown())

    async def shutdown(self):
        """Gracefully shutdown all mining components"""
        logger.info("🛑 Shutting down CryptoMiner Pro V30...")
        self.running = False
        self.shutdown_event.set()
        
        # Cancel all running tasks
        try:
            # Get all running tasks except current one
            current_task = asyncio.current_task()
            tasks = [task for task in asyncio.all_tasks() if task is not current_task and not task.done()]
            
            if tasks:
                logger.info(f"Cancelling {len(tasks)} running tasks...")
                for task in tasks:
                    task.cancel()
                
                # Wait for tasks to complete cancellation
                try:
                    await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=5.0)
                except asyncio.TimeoutError:
                    logger.warning("Some tasks did not shutdown gracefully within timeout")
        
        except Exception as e:
            logger.error(f"Error during task cleanup: {e}")
        
        # Stop mining engine
        if self.mining_engine:
            logger.info("Stopping mining engine...")
            try:
                await asyncio.wait_for(self.mining_engine.stop(), timeout=3.0)
            except asyncio.TimeoutError:
                logger.warning("Mining engine shutdown timed out")
            except Exception as e:
                logger.error(f"Error stopping mining engine: {e}")
            
        # Stop AI optimizer
        if self.ai_optimizer:
            logger.info("Stopping AI optimizer...")
            try:
                self.ai_optimizer.stop()
            except Exception as e:
                logger.error(f"Error stopping AI optimizer: {e}")
            
        # Stop web server
        if self.web_server_task and not self.web_server_task.done():
            logger.info("Stopping web monitoring server...")
            try:
                self.web_server_task.cancel()
                await asyncio.wait_for(self.web_server_task, timeout=2.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
            except Exception as e:
                logger.error(f"Error stopping web server: {e}")
        
        # Force close any remaining connections
        try:
            # Close any open sockets or connections
            if hasattr(self, 'mining_engine') and self.mining_engine and hasattr(self.mining_engine, 'miners'):
                for miner in self.mining_engine.miners:
                    if hasattr(miner, 'socket') and miner.socket:
                        try:
                            miner.socket.close()
                        except:
                            pass
        except Exception as e:
            logger.error(f"Error during connection cleanup: {e}")
        
        logger.info("✅ CryptoMiner Pro V30 shutdown complete")
        
        # Force exit if we're in signal handler context
        try:
            loop = asyncio.get_running_loop()
            loop.stop()
        except RuntimeError:
            pass

    def print_banner(self):
        """Display the application banner"""
        banner = """
╔══════════════════════════════════════════════════════════╗
║              🚀 CryptoMiner Pro V30 🚀                  ║
║           Compact Terminal Mining Application            ║
║                                                         ║
║  ⚡ Enterprise Mining Engine    🤖 AI Optimization     ║
║  🔗 Pool & Solo Support         📊 Web Monitoring      ║
╚══════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def list_coins(self):
        """List available coins for mining"""
        coins = {
            'LTC': 'Litecoin - Scrypt algorithm',
            'DOGE': 'Dogecoin - Scrypt algorithm', 
            'VTC': 'Vertcoin - Scrypt algorithm',
            'XMR': 'Monero - RandomX algorithm (CPU-friendly)'
        }
        
        print("\n📋 Available Coins:")
        print("=" * 50)
        for symbol, description in coins.items():
            print(f"  {symbol:<6} - {description}")
        print()

    async def setup_interactive(self):
        """Interactive setup wizard"""
        print("\n🔧 CryptoMiner Pro V30 - Interactive Setup")
        print("=" * 50)
        
        # Get coin selection
        self.list_coins()
        coin = input("Enter coin symbol (e.g., LTC): ").upper().strip()
        
        # Get wallet address
        wallet = input("Enter your wallet address: ").strip()
        
        # Get pool information
        pool = input("Enter pool URL (e.g., stratum+tcp://pool.example.com:4444): ").strip()
        
        # Get optional password
        password = input("Enter pool password (optional, press Enter to skip): ").strip()
        if not password:
            password = None
            
        # Get mining intensity
        intensity = input("Enter mining intensity 1-100% (default: 80): ").strip()
        if not intensity:
            intensity = 80
        else:
            try:
                intensity = max(1, min(100, int(intensity)))
            except ValueError:
                intensity = 80
                
        # Get thread count
        threads = input("Enter number of threads (default: auto): ").strip()
        if not threads:
            threads = None
        else:
            try:
                threads = max(1, int(threads))
            except ValueError:
                threads = None
        
        # Save configuration
        config = f"""# CryptoMiner Pro V30 Configuration
COIN={coin}
WALLET={wallet}
POOL={pool}
PASSWORD={password or ''}
INTENSITY={intensity}
THREADS={threads or 'auto'}
"""
        
        with open('mining_config.env', 'w') as f:
            f.write(config)
            
        print(f"\n✅ Configuration saved to mining_config.env")
        
        # Ask if user wants to start mining
        start_now = input("\nStart mining now? (y/n): ").lower().strip()
        if start_now in ['y', 'yes']:
            await self.start_mining(coin, wallet, pool, password, intensity, threads)

    async def start_mining(self, coin, wallet, pool, password=None, intensity=80, threads=None):
        """Start the mining operation"""
        self.running = True
        
        logger.info(f"🚀 Starting CryptoMiner Pro V30")
        logger.info(f"Coin: {coin}")
        logger.info(f"Wallet: {wallet}")
        logger.info(f"Pool: {pool}")
        logger.info(f"Intensity: {intensity}%")
        logger.info(f"Threads: {threads or 'auto'}")
        
        try:
            # Initialize AI optimizer
            self.ai_optimizer = AIOptimizer()
            
            # Initialize mining engine
            self.mining_engine = MiningEngine(
                coin=coin,
                wallet=wallet, 
                pool=pool,
                password=password,
                intensity=intensity,
                ai_optimizer=self.ai_optimizer
            )
            
            # Set thread count if specified
            if threads:
                self.mining_engine.set_thread_count(threads)
            
            # Start web monitoring server
            self.web_server_task = asyncio.create_task(self.start_web_server())
            
            # Start mining in background task
            mining_task = asyncio.create_task(self.mining_engine.start())
            
            # Wait for shutdown signal or mining completion
            try:
                while self.running:
                    # Check if mining engine is still running
                    if mining_task.done():
                        logger.warning("Mining engine stopped unexpectedly")
                        break
                    
                    # Wait for shutdown signal or brief sleep
                    try:
                        await asyncio.wait_for(self.shutdown_event.wait(), timeout=1.0)
                        break  # Shutdown signal received
                    except asyncio.TimeoutError:
                        continue  # Normal operation, continue loop
                        
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt")
            except Exception as e:
                logger.error(f"Mining error: {e}")
            finally:
                # Ensure clean shutdown
                if self.running:
                    await self.shutdown()
                    
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Mining error: {e}")
        finally:
            await self.shutdown()

    async def start_web_server(self):
        """Start the web monitoring server"""
        try:
            # Import here to avoid circular imports
            import subprocess
            import os
            
            # Start the FastAPI backend for web monitoring
            backend_env = os.environ.copy()
            backend_env['MINING_MODE'] = 'true'
            
            logger.info("🌐 Starting web monitoring server on http://localhost:8001")
            
            # This would be handled by supervisor in production
            # For now, we'll integrate with the existing FastAPI setup
            
        except Exception as e:
            logger.error(f"Failed to start web server: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="CryptoMiner Pro V30 - Enterprise Mining Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 cryptominer.py --setup                    # Interactive setup
  python3 cryptominer.py --list-coins              # Show available coins
  python3 cryptominer.py --coin LTC --wallet LTC_ADDRESS --pool stratum+tcp://pool.example.com:4444
  python3 cryptominer.py --coin LTC --wallet LTC_ADDRESS --pool stratum+tcp://pool.example.com:4444 --password worker1 --intensity 90 --threads 8
        """
    )
    
    parser.add_argument('--setup', action='store_true', help='Run interactive setup wizard')
    parser.add_argument('--list-coins', action='store_true', help='List available coins')
    parser.add_argument('--coin', help='Coin to mine (e.g., LTC, DOGE)')
    parser.add_argument('--wallet', help='Wallet address')
    parser.add_argument('--pool', help='Mining pool URL')
    parser.add_argument('--password', help='Pool password (optional)')
    parser.add_argument('--intensity', type=int, default=80, help='Mining intensity 1-100%% (default: 80)')
    parser.add_argument('--threads', type=int, help='Number of threads (default: auto)')
    parser.add_argument('--web-port', type=int, default=8001, help='Web monitoring port (default: 8001)')
    
    args = parser.parse_args()
    
    # Create miner instance
    miner = CryptoMinerPro()
    
    # Show banner
    miner.print_banner()
    
    # Handle different modes
    if args.list_coins:
        miner.list_coins()
        return
        
    if args.setup:
        asyncio.run(miner.setup_interactive())
        return
        
    if args.coin and args.wallet and args.pool:
        # Direct mining mode
        asyncio.run(miner.start_mining(
            coin=args.coin,
            wallet=args.wallet,
            pool=args.pool,
            password=args.password,
            intensity=args.intensity,
            threads=args.threads
        ))
        return
    
    # No valid arguments provided
    print("⚠️  No configuration found!")
    print("Options:")
    print("  python3 cryptominer.py --setup           # Interactive setup")
    print("  python3 cryptominer.py --list-coins      # Show available coins")
    print("  python3 cryptominer.py --coin LTC --wallet ADDRESS --pool POOL:PORT")
    print("\nFor full help: python3 cryptominer.py --help")

if __name__ == "__main__":
    main()