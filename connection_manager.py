"""
CryptoMiner Pro V30 - Connection Manager
Single connection point that relays bidirectional communication between mining threads and pool
"""

import asyncio
import json
import logging
import socket
import threading
import time
from queue import Queue, Empty
from typing import Dict, List, Optional, Any
import struct

logger = logging.getLogger(__name__)


class PoolConnection:
    """Manages single connection to mining pool"""
    
    def __init__(self, pool_host: str, pool_port: int, wallet: str, password: str):
        self.host = pool_host
        self.port = pool_port
        self.wallet = wallet
        self.password = password
        self.socket = None
        self.connected = False
        self.authorized = False
        self.extranonce1 = None
        self.extranonce2_size = 4
        self.current_work = None
        self.difficulty = 1.0
        self.job_id = None
        
    async def connect(self):
        """Connect to mining pool"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            await asyncio.get_event_loop().run_in_executor(
                None, self.socket.connect, (self.host, self.port)
            )
            self.connected = True
            logger.info(f"Connected to pool {self.host}:{self.port}")
            
            # Subscribe to mining
            await self._subscribe()
            await self._authorize()
            
            return True
            
        except Exception as e:
            logger.error(f"Pool connection failed: {e}")
            self.connected = False
            return False
    
    async def _subscribe(self):
        """Subscribe to mining notifications"""
        subscribe_msg = {
            "id": 1,
            "method": "mining.subscribe",
            "params": ["CryptoMiner Pro V30", None]
        }
        
        response = await self._send_message(subscribe_msg)
        if response and 'result' in response:
            result = response['result']
            if len(result) >= 2:
                self.extranonce1 = result[1]
                self.extranonce2_size = result[2] if len(result) > 2 else 4
                logger.info(f"Subscribed: extranonce1={self.extranonce1}")
                return True
        
        logger.error("Subscription failed")
        return False
    
    async def _authorize(self):
        """Authorize with mining pool"""
        auth_msg = {
            "id": 2,
            "method": "mining.authorize",
            "params": [self.wallet, self.password]
        }
        
        response = await self._send_message(auth_msg)
        if response and response.get('result') is True:
            self.authorized = True
            logger.info("Authorized with pool")
            return True
        
        logger.error("Authorization failed")
        return False
    
    async def _send_message(self, message: Dict) -> Optional[Dict]:
        """Send JSON message to pool and get response"""
        try:
            json_msg = json.dumps(message) + '\n'
            await asyncio.get_event_loop().run_in_executor(
                None, self.socket.send, json_msg.encode('utf-8')
            )
            
            # Read response
            response_data = await asyncio.get_event_loop().run_in_executor(
                None, self._read_line
            )
            
            if response_data:
                return json.loads(response_data.decode('utf-8'))
                
        except Exception as e:
            logger.error(f"Message send error: {e}")
        
        return None
    
    def _read_line(self) -> Optional[bytes]:
        """Read line from socket"""
        try:
            buffer = b''
            while b'\n' not in buffer:
                data = self.socket.recv(1024)
                if not data:
                    break
                buffer += data
            
            if b'\n' in buffer:
                line, remainder = buffer.split(b'\n', 1)
                return line.strip()
                
        except Exception as e:
            logger.error(f"Socket read error: {e}")
        
        return None
    
    async def submit_share(self, job_id: str, extranonce2: str, nonce: str, ntime: str) -> bool:
        """Submit share to pool"""
        submit_msg = {
            "id": 3,
            "method": "mining.submit",
            "params": [self.wallet, job_id, extranonce2, ntime, nonce]
        }
        
        response = await self._send_message(submit_msg)
        if response and response.get('result') is True:
            logger.info("✅ Share accepted by pool")
            return True
        else:
            error = response.get('error', 'Unknown error') if response else 'No response'
            logger.warning(f"❌ Share rejected: {error}")
            return False
    
    def get_work_template(self) -> Optional[Dict]:
        """Get current work template for mining"""
        if not self.current_work:
            return None
        
        return {
            'job_id': self.job_id,
            'extranonce1': self.extranonce1,
            'extranonce2_size': self.extranonce2_size,
            'difficulty': self.difficulty,
            'work_data': self.current_work
        }
    
    def close(self):
        """Close connection"""
        if self.socket:
            self.socket.close()
        self.connected = False
        self.authorized = False


class WorkDistributor:
    """Distributes mining work to multiple threads through single pool connection"""
    
    def __init__(self, pool_host: str, pool_port: int, wallet: str, password: str):
        self.pool_connection = PoolConnection(pool_host, pool_port, wallet, password)
        self.mining_threads: List[MiningWorker] = []
        self.work_queue = Queue()
        self.result_queue = Queue()
        self.running = False
        self.shares_found = 0
        self.shares_accepted = 0
        self.shares_rejected = 0
        
    async def start(self, num_threads: int):
        """Start connection manager with specified number of threads"""
        # Connect to pool
        if not await self.pool_connection.connect():
            return False
        
        self.running = True
        
        # Create mining worker threads
        for i in range(num_threads):
            worker = MiningWorker(i, self.work_queue, self.result_queue)
            worker.start()
            self.mining_threads.append(worker)
            logger.info(f"Started mining worker {i}")
        
        # Start work distribution and result handling
        asyncio.create_task(self._distribute_work())
        asyncio.create_task(self._handle_results())
        
        logger.info(f"Connection manager started with {num_threads} threads")
        return True
    
    async def _distribute_work(self):
        """Continuously distribute work to mining threads"""
        while self.running:
            try:
                work = self.pool_connection.get_work_template()
                if work:
                    # Create work units for each thread
                    for i, worker in enumerate(self.mining_threads):
                        work_unit = work.copy()
                        work_unit['thread_id'] = i
                        work_unit['nonce_start'] = i * 1000000
                        work_unit['nonce_end'] = (i + 1) * 1000000
                        
                        try:
                            self.work_queue.put_nowait(work_unit)
                        except:
                            pass  # Queue full, try next iteration
                
                await asyncio.sleep(1)  # Distribute work every second
                
            except Exception as e:
                logger.error(f"Work distribution error: {e}")
                await asyncio.sleep(5)
    
    async def _handle_results(self):
        """Handle results from mining threads"""
        while self.running:
            try:
                result = self.result_queue.get(timeout=1)
                
                if result['type'] == 'share':
                    self.shares_found += 1
                    accepted = await self.pool_connection.submit_share(
                        result['job_id'],
                        result['extranonce2'],
                        result['nonce'],
                        result['ntime']
                    )
                    
                    if accepted:
                        self.shares_accepted += 1
                    else:
                        self.shares_rejected += 1
                
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Result handling error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get mining statistics"""
        total_hashrate = sum(worker.hashrate for worker in self.mining_threads)
        
        return {
            'threads': len(self.mining_threads),
            'pool_connected': self.pool_connection.connected and self.pool_connection.authorized,
            'hashrate': total_hashrate,
            'shares_found': self.shares_found,
            'shares_accepted': self.shares_accepted,
            'shares_rejected': self.shares_rejected,
            'difficulty': self.pool_connection.difficulty,
            'pool': f"{self.pool_connection.host}:{self.pool_connection.port}"
        }
    
    async def stop(self):
        """Stop all mining operations"""
        self.running = False
        
        # Stop worker threads
        for worker in self.mining_threads:
            worker.stop()
        
        # Close pool connection
        self.pool_connection.close()
        
        logger.info("Connection manager stopped")


class MiningWorker(threading.Thread):
    """Individual mining worker thread"""
    
    def __init__(self, thread_id: int, work_queue: Queue, result_queue: Queue):
        super().__init__(daemon=True)
        self.thread_id = thread_id
        self.work_queue = work_queue
        self.result_queue = result_queue
        self.running = False
        self.hashrate = 0.0
        self.hashes_done = 0
        self.last_time = time.time()
    
    def run(self):
        """Main mining loop"""
        self.running = True
        logger.info(f"Mining worker {self.thread_id} started")
        
        while self.running:
            try:
                # Get work from queue
                work = self.work_queue.get(timeout=1)
                
                # Perform mining
                self._mine_work(work)
                
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Worker {self.thread_id} error: {e}")
    
    def _mine_work(self, work: Dict):
        """Mine work unit"""
        # Simplified mining loop
        nonce_start = work['nonce_start']
        nonce_end = work['nonce_end']
        
        for nonce in range(nonce_start, nonce_end):
            if not self.running:
                break
            
            # Update hashrate tracking
            self.hashes_done += 1
            current_time = time.time()
            
            if current_time - self.last_time >= 1.0:
                self.hashrate = self.hashes_done / (current_time - self.last_time)
                self.hashes_done = 0
                self.last_time = current_time
            
            # Simulate hash checking (replace with actual Scrypt hashing)
            if nonce % 1000000 == 999999:  # Simulate finding share
                share_result = {
                    'type': 'share',
                    'thread_id': self.thread_id,
                    'job_id': work['job_id'],
                    'extranonce2': f"{nonce:08x}",
                    'nonce': f"{nonce:08x}",
                    'ntime': f"{int(time.time()):08x}"
                }
                
                try:
                    self.result_queue.put_nowait(share_result)
                    logger.info(f"Worker {self.thread_id} found potential share")
                except:
                    pass  # Queue full
    
    def stop(self):
        """Stop mining worker"""
        self.running = False
        logger.info(f"Mining worker {self.thread_id} stopped")


# Global work distributor instance
work_distributor = None


async def start_connection_manager(pool_host: str, pool_port: int, wallet: str, password: str, num_threads: int):
    """Start the connection manager system"""
    global work_distributor
    
    work_distributor = WorkDistributor(pool_host, pool_port, wallet, password)
    success = await work_distributor.start(num_threads)
    
    if success:
        logger.info(f"Connection manager started: {num_threads} threads through single pool connection")
    else:
        logger.error("Failed to start connection manager")
    
    return success


def get_connection_manager_stats() -> Dict[str, Any]:
    """Get statistics from connection manager"""
    if work_distributor:
        return work_distributor.get_stats()
    else:
        return {
            'threads': 0,
            'pool_connected': False,
            'hashrate': 0.0,
            'shares_found': 0,
            'shares_accepted': 0,
            'shares_rejected': 0,
            'difficulty': 0.0,
            'pool': 'Not connected'
        }