"""
CryptoMiner Pro V30 - Proxy Mining Engine
Uses connection manager for single pool connection with multiple internal threads
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional
from connection_manager import start_connection_manager, get_connection_manager_stats
from ai_optimizer import AIOptimizer

logger = logging.getLogger(__name__)


class ProxyMiningEngine:
    """Mining engine that uses connection manager for multi-threading through single pool connection"""
    
    def __init__(self, coin: str, wallet: str, pool_url: str, password: str = "x", intensity: int = 80):
        self.coin = coin.upper()
        self.wallet = wallet
        self.pool_url = pool_url
        self.password = password
        self.intensity = intensity
        self.thread_count = 8  # Internal threads
        
        # Parse pool URL
        self.pool_host, self.pool_port = self._parse_pool_url(pool_url)
        
        # Statistics
        self.start_time = time.time()
        self.running = False
        
        # AI Optimizer
        try:
            self.ai_optimizer = AIOptimizer(coin)
            logger.info("AI Optimizer initialized")
        except Exception as e:
            logger.warning(f"AI Optimizer failed to initialize: {e}")
            self.ai_optimizer = None
    
    def _parse_pool_url(self, pool_url: str) -> tuple:
        """Parse pool URL to extract host and port"""
        if "://" in pool_url:
            pool_url = pool_url.split("://")[1]
        
        if ":" in pool_url:
            host, port = pool_url.split(":")
            return host, int(port)
        else:
            return pool_url, 4444  # Default port
    
    def set_thread_count(self, count: int):
        """Set number of internal mining threads"""
        if count > 0:
            self.thread_count = count
            logger.info(f"Thread count set to: {count}")
    
    def set_intensity(self, intensity: int):
        """Set mining intensity (affects thread behavior)"""
        if 1 <= intensity <= 100:
            self.intensity = intensity
            logger.info(f"Mining intensity set to: {intensity}%")
    
    async def start_mining(self):
        """Start mining using connection manager"""
        if self.running:
            logger.warning("Mining already running")
            return
        
        logger.info(f"🚀 Starting proxy mining with {self.thread_count} threads through single connection")
        logger.info(f"Pool: {self.pool_host}:{self.pool_port}")
        logger.info(f"Wallet: {self.wallet}")
        logger.info(f"Intensity: {self.intensity}%")
        
        # Start connection manager
        success = await start_connection_manager(
            self.pool_host, 
            self.pool_port, 
            self.wallet, 
            self.password,
            self.thread_count
        )
        
        if success:
            self.running = True
            logger.info(f"✅ Proxy mining started successfully")
            
            # Start AI optimization if available
            if self.ai_optimizer:
                asyncio.create_task(self._ai_optimization_loop())
                logger.info("🤖 AI Optimizer started")
            
            return True
        else:
            logger.error("❌ Failed to start proxy mining")
            return False
    
    async def _ai_optimization_loop(self):
        """AI optimization loop"""
        while self.running:
            try:
                await asyncio.sleep(30)  # Optimize every 30 seconds
                
                stats = self.get_stats()
                if stats['hashrate'] > 0:
                    # Feed data to AI optimizer
                    self.ai_optimizer.update_performance(
                        hashrate=stats['hashrate'],
                        accepted_shares=stats['accepted_shares'],
                        rejected_shares=stats['rejected_shares'],
                        threads=stats['threads'],
                        intensity=self.intensity
                    )
                    
                    # Get AI recommendations
                    recommendations = self.ai_optimizer.get_recommendations()
                    if recommendations:
                        logger.info(f"🤖 AI recommendations: {recommendations}")
                        
                        # Apply intensity optimization if suggested
                        if 'intensity' in recommendations:
                            new_intensity = recommendations['intensity']
                            if 1 <= new_intensity <= 100 and new_intensity != self.intensity:
                                self.set_intensity(new_intensity)
                
            except Exception as e:
                logger.error(f"AI optimization error: {e}")
    
    async def stop_mining(self):
        """Stop mining operations"""
        if not self.running:
            return
        
        logger.info("⏹️ Stopping proxy mining...")
        self.running = False
        
        # Connection manager will be stopped by the global instance
        logger.info("Proxy mining stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive mining statistics"""
        uptime = time.time() - self.start_time
        
        # Get stats from connection manager
        cm_stats = get_connection_manager_stats()
        
        # Calculate acceptance rate
        total_shares = cm_stats['shares_accepted'] + cm_stats['shares_rejected']
        acceptance_rate = (cm_stats['shares_accepted'] / total_shares * 100) if total_shares > 0 else 0.0
        
        stats = {
            'running': self.running,
            'coin': self.coin,
            'pool': f"{self.pool_host}:{self.pool_port}",
            'pool_connected': cm_stats['pool_connected'],
            'threads': cm_stats['threads'],
            'hashrate': cm_stats['hashrate'],
            'intensity': self.intensity,
            'uptime': uptime,
            'accepted_shares': cm_stats['shares_accepted'],
            'rejected_shares': cm_stats['shares_rejected'],
            'total_shares': total_shares,
            'acceptance_rate': acceptance_rate,
            'difficulty': cm_stats['difficulty'],
            'shares_found': cm_stats['shares_found']
        }
        
        # Add AI optimizer stats if available
        if self.ai_optimizer:
            ai_stats = self.ai_optimizer.get_stats()
            stats.update({
                'ai_learning_progress': ai_stats.get('learning_progress', 0.0),
                'ai_optimization_level': ai_stats.get('optimization_level', 0.0),
                'ai_recommendations': ai_stats.get('recommendations', {}),
                'ai_performance_trend': ai_stats.get('performance_trend', 'stable')
            })
        else:
            stats.update({
                'ai_learning_progress': 0.0,
                'ai_optimization_level': 0.0,
                'ai_recommendations': {},
                'ai_performance_trend': 'disabled'
            })
        
        return stats
    
    def get_thread_info(self) -> Dict[str, Any]:
        """Get detailed thread information"""
        return {
            'configured_threads': self.thread_count,
            'connection_type': 'proxy',
            'pool_connections': 1,  # Single connection to pool
            'internal_threads': self.thread_count,
            'architecture': 'connection_manager'
        }


# Example usage and testing
async def test_proxy_mining():
    """Test the proxy mining system"""
    engine = ProxyMiningEngine(
        coin="LTC",
        wallet="ltc1qqvz2zw9hqd804a03xg95m4594p7v7thk25sztl",
        pool_url="ltc.luckymonster.pro:4112",
        password="_d=128"
    )
    
    engine.set_thread_count(8)
    engine.set_intensity(80)
    
    success = await engine.start_mining()
    if success:
        logger.info("Test mining started successfully")
        
        # Run for 60 seconds
        for i in range(12):
            await asyncio.sleep(5)
            stats = engine.get_stats()
            logger.info(f"Stats: {stats['hashrate']:.2f} H/s, {stats['threads']} threads, {stats['accepted_shares']} shares")
        
        await engine.stop_mining()
    else:
        logger.error("Test mining failed to start")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_proxy_mining())