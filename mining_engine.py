"""
Mining Engine - Core mining orchestration and thread management
Handles high-level mining control and coordinates with scrypt_miner and AI optimizer
"""

import asyncio
import logging
import psutil
import threading
import time
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class MiningEngine:
    def __init__(self, coin: str, wallet: str, pool: str, password: Optional[str] = None, 
                 intensity: int = 80, ai_optimizer=None):
        self.coin = coin.upper()
        self.wallet = wallet
        self.pool = pool
        self.password = password
        self.intensity = intensity
        self.ai_optimizer = ai_optimizer
        
        # Mining state
        self.running = False
        self.threads = []
        self.stats = {
            'hashrate': 0,
            'accepted_shares': 0,
            'rejected_shares': 0,
            'total_hashes': 0,
            'uptime': 0,
            'difficulty': 1,
            'pool_connected': False
        }
        
        # Calculate optimal thread count
        self.max_threads = self._calculate_max_threads()
        self.thread_count = self._calculate_optimal_threads()
        
        # Performance monitoring
        self.last_stats_update = time.time()
        
        logger.info(f"Mining Engine initialized for {self.coin}")
        logger.info(f"Max threads: {self.max_threads}, Optimal: {self.thread_count}")

    def _calculate_max_threads(self) -> int:
        """Calculate maximum safe thread count"""
        cpu_count = psutil.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # Conservative calculation for stability
        max_safe = min(
            cpu_count * 4,  # 4 threads per CPU core
            int(memory_gb * 16),  # 16 threads per GB RAM
            250000  # Enterprise limit
        )
        
        logger.info(f"Max safe threads calculated: {max_safe} (cores: {cpu_count}, memory: {memory_gb:.1f}GB)")
        return max_safe

    def _calculate_optimal_threads(self) -> int:
        """Calculate optimal thread count based on intensity"""
        cpu_count = psutil.cpu_count()
        
        # Base calculation on CPU cores and intensity
        base_threads = max(1, int(cpu_count * (self.intensity / 100)))
        
        # Apply enterprise scaling
        optimal = min(base_threads, self.max_threads)
        
        logger.info(f"Optimal threads for {self.intensity}% intensity: {optimal}")
        return optimal

    def set_thread_count(self, count: int):
        """Set thread count manually"""
        self.thread_count = max(1, min(count, self.max_threads))
        logger.info(f"Thread count set to: {self.thread_count}")

    async def start(self):
        """Start mining operation"""
        if self.running:
            logger.warning("Mining already running")
            return
            
        self.running = True
        self.stats['uptime'] = time.time()
        self.start_time = time.time()  # Store start time for uptime calculation
        
        logger.info(f"🚀 Starting mining with {self.thread_count} threads")
        
        try:
            # Import here to avoid circular imports
            from scrypt_miner import ScryptMiner
            
            # Create miner instances
            self.miners = []
            for i in range(self.thread_count):
                miner = ScryptMiner(
                    thread_id=i,
                    coin=self.coin,
                    wallet=self.wallet,
                    pool=self.pool,
                    password=self.password,
                    stats_callback=self._update_stats
                )
                self.miners.append(miner)
            
            # Start all mining threads
            mining_tasks = []
            for miner in self.miners:
                task = asyncio.create_task(miner.start_mining())
                mining_tasks.append(task)
            
            # Start statistics monitoring
            stats_task = asyncio.create_task(self._monitor_stats())
            
            # Start AI optimization if available
            if self.ai_optimizer:
                ai_task = asyncio.create_task(self.ai_optimizer.start_optimization(self))
                mining_tasks.append(ai_task)
            
            # Wait for all tasks
            await asyncio.gather(*mining_tasks, stats_task, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Mining error: {e}")
            raise
        finally:
            self.running = False

    async def stop(self):
        """Stop mining operation"""
        if not self.running:
            return
            
        logger.info("Stopping mining engine...")
        self.running = False
        
        # Stop all miners
        if hasattr(self, 'miners'):
            for miner in self.miners:
                await miner.stop()
        
        # Clear threads
        self.threads.clear()
        
        logger.info("Mining engine stopped")

    def is_running(self) -> bool:
        """Check if mining is currently running"""
        return self.running

    def _update_stats(self, thread_stats: Dict[str, Any]):
        """Update mining statistics from thread callback"""
        # Aggregate stats from all threads
        self.stats['hashrate'] += thread_stats.get('hashrate', 0)
        self.stats['accepted_shares'] += thread_stats.get('accepted_shares', 0)
        self.stats['rejected_shares'] += thread_stats.get('rejected_shares', 0)
        self.stats['total_hashes'] += thread_stats.get('hashes', 0)
        
        # Update connection status
        if thread_stats.get('connected'):
            self.stats['pool_connected'] = True
            
        # Update difficulty
        if 'difficulty' in thread_stats:
            self.stats['difficulty'] = thread_stats['difficulty']

    async def _monitor_stats(self):
        """Monitor and display mining statistics"""
        while self.running:
            try:
                await asyncio.sleep(30)  # Update every 30 seconds
                
                if not self.running:
                    break
                    
                # Calculate uptime
                uptime_seconds = time.time() - self.stats['uptime']
                uptime_str = self._format_uptime(uptime_seconds)
                
                # Calculate hashrate (reset for next interval)
                hashrate = self.stats['hashrate']
                self.stats['hashrate'] = 0  # Reset for next calculation
                
                # Display stats
                logger.info("=" * 60)
                logger.info(f"📊 MINING STATS - {self.coin}")
                logger.info(f"Hashrate: {hashrate:.2f} H/s")
                logger.info(f"Threads: {self.thread_count}")
                logger.info(f"Intensity: {self.intensity}%")
                logger.info(f"Difficulty: {self.stats['difficulty']}")
                logger.info(f"Shares: ✅ {self.stats['accepted_shares']} | ❌ {self.stats['rejected_shares']}")
                logger.info(f"Total Hashes: {self.stats['total_hashes']:,}")
                logger.info(f"Pool Connected: {'✅' if self.stats['pool_connected'] else '❌'}")
                logger.info(f"Uptime: {uptime_str}")
                logger.info("=" * 60)
                
                # AI optimization metrics
                if self.ai_optimizer:
                    ai_stats = self.ai_optimizer.get_stats()
                    logger.info(f"🤖 AI Learning: {ai_stats['learning_progress']:.1f}%")
                    logger.info(f"🎯 Optimization: {ai_stats['optimization_progress']:.1f}%")
                
            except Exception as e:
                logger.error(f"Stats monitoring error: {e}")

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime duration"""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def get_stats(self) -> Dict[str, Any]:
        """Get current mining statistics"""
        stats = self.stats.copy()
        stats['thread_count'] = self.thread_count
        stats['intensity'] = self.intensity
        stats['coin'] = self.coin
        
        # Calculate actual uptime if mining started
        if hasattr(self, 'start_time'):
            stats['uptime'] = self.start_time
        else:
            stats['uptime'] = time.time()
        
        if self.ai_optimizer:
            stats['ai_stats'] = self.ai_optimizer.get_stats()
            
        return stats

    async def adjust_intensity(self, new_intensity: int):
        """Adjust mining intensity dynamically"""
        if not 1 <= new_intensity <= 100:
            logger.error(f"Invalid intensity: {new_intensity}. Must be 1-100")
            return
            
        self.intensity = new_intensity
        new_thread_count = self._calculate_optimal_threads()
        
        if new_thread_count != self.thread_count:
            logger.info(f"Adjusting threads from {self.thread_count} to {new_thread_count}")
            # TODO: Implement dynamic thread adjustment
            # For now, log the change
            self.thread_count = new_thread_count

    def adjust_threads(self, new_count: int):
        """Adjust thread count dynamically"""
        if new_count < 1 or new_count > self.max_threads:
            logger.error(f"Invalid thread count: {new_count}. Must be 1-{self.max_threads}")
            return
            
        logger.info(f"Adjusting threads from {self.thread_count} to {new_count}")
        self.thread_count = new_count
        # TODO: Implement dynamic thread adjustment