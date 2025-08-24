#!/usr/bin/env python3
"""
🚀 CryptoMiner V21
Advanced Multi-Algorithm CPU Mining Platform with AI Optimization
Enterprise-grade distributed mining solution supporting 250,000+ cores
"""

import argparse
import asyncio
import signal
import sys
import os
import time
import threading
import logging
from pathlib import Path
from datetime import datetime

# Import consolidated modules
from config import config, BANNER, APP_NAME, APP_VERSION, format_uptime, SUPPORTED_COINS
from mining_engine import UnifiedMiningEngine
from ai_mining_optimizer import AdvancedAIMiningOptimizer

# Configure logging
config.setup_logging()
logger = logging.getLogger(__name__)

class CryptoMinerV21:
    """Main CryptoMiner V21 Application"""
    
    def __init__(self):
        self.mining_engine = UnifiedMiningEngine()
        self.ai_optimizer = None
        self.web_monitor = None
        self.is_running = False
        self.start_time = None
        
        # Signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.is_running = False
    
    async def start_mining(self, coin: str, wallet: str, pool: str, password: str = "x",
                          intensity: int = 80, threads: int = 0, web_enabled: bool = True,
                          ai_enabled: bool = True):
        """Start the mining operation with specified parameters"""
        
        try:
            self.is_running = True
            self.start_time = time.time()
            
            # Display startup banner
            print(BANNER)
            print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Display configuration
            print(f"\n⚙️ Configuration loaded from file:")
            print(f"  Coin: {coin}")
            print(f"  Wallet: {wallet}")
            print(f"  Pool: {pool}")
            print(f"  Intensity: {intensity}%")
            print(f"  Threads: {threads if threads > 0 else 'auto-detect'}")
            print()
            
            # Initialize AI optimizer if enabled
            if ai_enabled:
                logger.info("🤖 Initializing AI optimizer...")
                self.ai_optimizer = AdvancedAIMiningOptimizer()
                logger.info("✅ AI optimizer initialized")
            
            # Start mining with algorithm detection
            algorithm = config.get_algorithm(coin)
            logger.info(f"🔍 Detected algorithm: {algorithm} for coin {coin}")
            
            if algorithm == 'RandomX':
                logger.info("🚀 Initializing RandomX CPU mining for Monero-based coin")
            elif algorithm == 'Scrypt':
                logger.info("🚀 Initializing Scrypt CPU mining for Litecoin-based coin")
            
            # Start the mining engine
            success = self.mining_engine.start_mining(
                coin=coin,
                wallet=wallet,
                pool=pool,
                password=password,
                intensity=intensity,
                threads=threads
            )
            
            if not success:
                logger.error("❌ Failed to start mining engine")
                return False
            
            logger.info("✅ Mining started successfully")
            
            # Start monitoring tasks
            tasks = []
            
            if ai_enabled and self.ai_optimizer:
                tasks.append(asyncio.create_task(self._ai_monitoring()))
                logger.info("🤖 Starting AI monitoring and optimization...")
            
            if web_enabled:
                tasks.append(asyncio.create_task(self._web_monitoring()))
                logger.info("🌐 Starting web monitoring...")
            
            # Main monitoring loop
            tasks.append(asyncio.create_task(self._main_monitoring_loop()))
            
            # Wait for tasks or shutdown signal
            try:
                await asyncio.gather(*tasks)
            except asyncio.CancelledError:
                logger.info("📊 Monitoring tasks cancelled")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in start_mining: {e}")
            return False
        finally:
            await self._shutdown()
    
    async def _main_monitoring_loop(self):
        """Main monitoring and statistics loop"""
        while self.is_running:
            try:
                # Get current mining statistics
                stats = self.mining_engine.get_stats()
                
                if stats.get('is_running'):
                    # Log mining progress every 30 seconds
                    uptime = time.time() - self.start_time if self.start_time else 0
                    
                    logger.info(
                        f"⚡ Mining Status: {stats.get('hashrate', 0):.1f} H/s | "
                        f"Algorithm: {stats.get('algorithm', 'N/A')} | "
                        f"Threads: {stats.get('threads', 0)} | "
                        f"Shares: {stats.get('shares_good', 0)} | "
                        f"Uptime: {format_uptime(uptime)} | "
                        f"Pool: {'Connected' if stats.get('pool_connected') else 'Disconnected'}"
                    )
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(10)
    
    async def _ai_monitoring(self):
        """AI monitoring and optimization"""
        if not self.ai_optimizer:
            return
        
        logger.info("🧠 AI monitoring started")
        
        while self.is_running:
            try:
                # Get current mining stats
                stats = self.mining_engine.get_stats()
                
                if stats.get('is_running') and stats.get('hashrate', 0) > 0:
                    # Update AI with current mining data
                    mining_data = {
                        'hashrate': stats.get('hashrate', 0),
                        'threads': stats.get('threads', 0),
                        'cpu_usage': stats.get('cpu_usage', 0),
                        'shares_good': stats.get('shares_good', 0),
                        'uptime': time.time() - self.start_time if self.start_time else 0
                    }
                    
                    # Get AI recommendations
                    try:
                        recommendation = self.ai_optimizer.get_optimization_recommendation(mining_data)
                        
                        if recommendation and recommendation.get('confidence', 0) > 0.7:
                            logger.info(
                                f"🧠 AI Recommendation: {recommendation.get('action', 'optimize')} "
                                f"(Confidence: {recommendation.get('confidence', 0)*100:.1f}%)"
                            )
                    except Exception as e:
                        logger.debug(f"AI recommendation error: {e}")
                
                await asyncio.sleep(60)  # AI check every minute
                
            except Exception as e:
                logger.error(f"❌ Error in AI monitoring: {e}")
                await asyncio.sleep(30)
    
    async def _web_monitoring(self):
        """Web monitoring and statistics updates"""
        logger.info("🌐 Web monitoring started")
        
        while self.is_running:
            try:
                # Get current stats
                stats = self.mining_engine.get_stats()
                
                # Update web backend if available
                await self._update_web_backend(stats)
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in web monitoring: {e}")
                await asyncio.sleep(10)
    
    async def _update_web_backend(self, stats):
        """Update web backend with current statistics"""
        try:
            import aiohttp
            
            # Prepare stats data
            update_data = {
                'hashrate': stats.get('hashrate', 0),
                'algorithm': stats.get('algorithm', ''),
                'coin': stats.get('coin', ''),
                'threads': stats.get('threads', 0),
                'shares_good': stats.get('shares_good', 0),
                'pool_connected': stats.get('pool_connected', False),
                'cpu_usage': stats.get('cpu_usage', 0),
                'memory_usage': stats.get('memory_usage', 0),
                'uptime': time.time() - self.start_time if self.start_time else 0,
                'is_running': stats.get('is_running', False)
            }
            
            # Send to backend API
            web_port = config.get('web_port', 8001)
            async with aiohttp.ClientSession() as session:
                await session.post(
                    f'http://localhost:{web_port}/api/mining/update-stats',
                    json=update_data,
                    timeout=aiohttp.ClientTimeout(total=5)
                )
                
        except Exception as e:
            logger.debug(f"Web backend update failed: {e}")
    
    async def _shutdown(self):
        """Graceful shutdown of all components"""
        logger.info("🛑 Shutting down CryptoMiner V21...")
        
        self.is_running = False
        
        # Cancel all running tasks
        tasks = [task for task in asyncio.all_tasks() if not task.done()]
        if tasks:
            logger.info(f"Cancelling {len(tasks)} running tasks...")
            for task in tasks:
                task.cancel()
        
        # Stop mining engine
        if self.mining_engine:
            self.mining_engine.stop_mining()
        
        # Stop AI optimizer
        if self.ai_optimizer:
            try:
                logger.info("Stopping AI optimizer...")
                if hasattr(self.ai_optimizer, 'stop'):
                    self.ai_optimizer.stop()
            except Exception as e:
                logger.error(f"Error stopping AI optimizer: {e}")
        
        logger.info("✅ CryptoMiner V21 shutdown complete")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} - Advanced Multi-Algorithm CPU Mining Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --coin XMR --wallet YOUR_WALLET --pool stratum+tcp://pool.supportxmr.com:3333
  %(prog)s --coin LTC --wallet YOUR_WALLET --pool stratum+tcp://ltc.f2pool.com:4444 --threads 8
  %(prog)s --config  # Use settings from mining_config.env only
        """
    )
    
    parser.add_argument('--coin', type=str, help='Cryptocurrency to mine (XMR, LTC, DOGE)')
    parser.add_argument('--wallet', type=str, help='Your wallet address')
    parser.add_argument('--pool', type=str, help='Mining pool URL (stratum+tcp://...)')
    parser.add_argument('--password', type=str, default='x', help='Pool password/worker name')
    parser.add_argument('--intensity', type=int, default=80, help='Mining intensity 1-100 (default: 80)')
    parser.add_argument('--threads', type=int, default=0, help='Number of threads (0 = auto-detect)')
    parser.add_argument('--web-port', type=int, default=8001, help='Web monitoring port (default: 8001)')
    parser.add_argument('--no-web', action='store_true', help='Disable web monitoring')
    parser.add_argument('--no-ai', action='store_true', help='Disable AI optimization')
    parser.add_argument('--config-only', action='store_true', help='Use only mining_config.env settings')
    parser.add_argument('--version', action='version', version=f'{APP_NAME} {APP_VERSION}')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    return parser.parse_args()

def main():
    """Main application entry point"""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Enable debug logging if requested
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.info("🐛 Debug logging enabled")
        
        # Determine configuration source
        if args.config_only:
            # Use only configuration file
            if not config.is_complete():
                missing = config.get_missing_fields()
                logger.error(f"❌ Incomplete configuration file. Missing: {', '.join(missing)}")
                logger.error("Please edit mining_config.env with your mining details")
                sys.exit(1)
            
            # Get settings from config file
            mining_config = {
                'coin': config.get('coin'),
                'wallet': config.get('wallet'),
                'pool': config.get('pool'),
                'password': config.get('password', 'x'),
                'intensity': config.get('intensity', 80),
                'threads': config.get('threads') or 0,  # Convert None to 0
                'web_enabled': config.get('web_enabled', True) and not args.no_web,
                'ai_enabled': config.get('ai_enabled', True) and not args.no_ai
            }
        else:
            # Use command line arguments with config file as fallback
            mining_config = {
                'coin': args.coin or config.get('coin'),
                'wallet': args.wallet or config.get('wallet'),
                'pool': args.pool or config.get('pool'),
                'password': args.password or config.get('password', 'x'),
                'intensity': args.intensity or config.get('intensity', 80),
                'threads': args.threads or config.get('threads', 0),
                'web_enabled': not args.no_web and config.get('web_enabled', True),
                'ai_enabled': not args.no_ai and config.get('ai_enabled', True)
            }
        
        # Validate required parameters
        required = ['coin', 'wallet', 'pool']
        missing = [param for param in required if not mining_config.get(param)]
        
        if missing:
            logger.error(f"❌ Missing required parameters: {', '.join(missing)}")
            logger.error("Provide via command line or edit mining_config.env")
            sys.exit(1)
        
        # Validate coin support
        coin = mining_config['coin'].upper()
        if coin not in SUPPORTED_COINS:
            logger.error(f"❌ Unsupported coin: {coin}")
            logger.error(f"Supported coins: {', '.join(SUPPORTED_COINS.keys())}")
            sys.exit(1)
        
        # Create and start miner
        miner = CryptoMinerV21()
        
        # Start mining
        asyncio.run(miner.start_mining(
            coin=mining_config['coin'],
            wallet=mining_config['wallet'],
            pool=mining_config['pool'],
            password=mining_config['password'],
            intensity=mining_config['intensity'],
            threads=mining_config['threads'],
            web_enabled=mining_config['web_enabled'],
            ai_enabled=mining_config['ai_enabled']
        ))
        
    except KeyboardInterrupt:
        logger.info("⚠️ Mining interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()