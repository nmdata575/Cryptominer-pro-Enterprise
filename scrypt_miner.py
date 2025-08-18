"""
Scrypt Miner - Low-level Scrypt mining logic and Stratum protocol communication
Handles work processing, share submission, and pool communication
"""

import asyncio
import hashlib
import json
import logging
import socket
import struct
import time
from typing import Optional, Dict, Any, Callable
import binascii

# Import optimized scrypt library for performance
try:
    import scrypt
    SCRYPT_AVAILABLE = True
except ImportError:
    SCRYPT_AVAILABLE = False
    logging.warning("scrypt library not available, using fallback implementation")

logger = logging.getLogger(__name__)

class ScryptMiner:
    def __init__(self, thread_id: int, coin: str, wallet: str, pool: str, 
                 password: Optional[str] = None, stats_callback: Optional[Callable] = None):
        self.thread_id = thread_id
        self.coin = coin.upper()
        self.wallet = wallet
        self.pool = pool
        self.password = password or ""
        self.stats_callback = stats_callback
        
        # Parse pool URL
        self.pool_host, self.pool_port = self._parse_pool_url(pool)
        
        # Mining state
        self.running = False
        self.socket = None
        self.connected = False
        self.subscribed = False
        self.authorized = False
        
        # Work data
        self.current_work = None
        self.extranonce1 = None
        self.extranonce2_size = 0
        self.target = None
        self.difficulty = 1
        
        # Statistics
        self.stats = {
            'hashrate': 0,
            'accepted_shares': 0,
            'rejected_shares': 0,
            'hashes': 0,
            'connected': False,
            'difficulty': 1
        }
        
        # Performance tracking
        self.last_hash_time = time.time()
        self.hash_count = 0
        
        logger.info(f"ScryptMiner {self.thread_id} initialized for {self.coin}")

    def _parse_pool_url(self, pool_url: str) -> tuple:
        """Parse pool URL to extract host and port"""
        if "://" in pool_url:
            pool_url = pool_url.split("://")[1]
            
        if ":" in pool_url:
            host, port = pool_url.split(":")
            return host, int(port)
        else:
            # Default ports for common protocols
            return pool_url, 4444

    async def start_mining(self):
        """Start the mining process"""
        if self.running:
            return
            
        self.running = True
        logger.info(f"Thread {self.thread_id}: Starting mining")
        
        try:
            while self.running:
                try:
                    # Connect to pool
                    await self._connect_to_pool()
                    
                    # Subscribe to pool
                    await self._subscribe_to_pool()
                    
                    # Authorize worker
                    await self._authorize_worker()
                    
                    # Start mining loop
                    await self._mining_loop()
                    
                except Exception as e:
                    logger.error(f"Thread {self.thread_id}: Mining error: {e}")
                    await asyncio.sleep(5)  # Wait before retry
                    
        except Exception as e:
            logger.error(f"Thread {self.thread_id}: Fatal error: {e}")
        finally:
            await self.stop()

    async def stop(self):
        """Stop mining and cleanup"""
        self.running = False
        
        # Close socket connection properly
        if self.socket:
            try:
                # Shutdown socket before closing
                try:
                    self.socket.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass  # Already disconnected
                self.socket.close()
            except Exception as e:
                logger.debug(f"Thread {self.thread_id}: Socket cleanup error: {e}")
            finally:
                self.socket = None
            
        self.connected = False
        self.authorized = False
        self.subscribed = False
        logger.info(f"Thread {self.thread_id}: Stopped")

    async def _connect_to_pool(self):
        """Connect to mining pool with increased timeout"""
        if self.connected:
            return
            
        try:
            logger.info(f"Thread {self.thread_id}: Connecting to {self.pool_host}:{self.pool_port}")
            
            # Create socket with increased timeout
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(120)  # 2 minutes timeout
            
            # Connect to pool
            await asyncio.get_event_loop().run_in_executor(
                None, self.socket.connect, (self.pool_host, self.pool_port)
            )
            
            self.connected = True
            self.stats['connected'] = True
            logger.info(f"Thread {self.thread_id}: Connected to pool")
            
        except Exception as e:
            logger.error(f"Thread {self.thread_id}: Connection failed: {e}")
            self.connected = False
            self.stats['connected'] = False
            raise

    async def _subscribe_to_pool(self):
        """Subscribe to pool using Stratum protocol"""
        if not self.connected or self.subscribed:
            return
            
        try:
            # Send mining.subscribe
            subscribe_msg = {
                "id": 1,
                "method": "mining.subscribe",
                "params": [f"CryptoMinerPro/V30", None, self.pool_host, str(self.pool_port)]
            }
            
            response = await self._send_stratum_message(subscribe_msg)
            
            if response and 'result' in response:
                result = response['result']
                if len(result) >= 3:
                    self.extranonce1 = result[1]
                    self.extranonce2_size = result[2]
                    self.subscribed = True
                    logger.info(f"Thread {self.thread_id}: Subscribed to pool")
                    
                    # Request difficulty
                    await self._suggest_difficulty()
                    
        except Exception as e:
            logger.error(f"Thread {self.thread_id}: Subscription failed: {e}")
            raise

    async def _authorize_worker(self):
        """Authorize worker with pool"""
        if not self.subscribed or self.authorized:
            return
            
        try:
            # Send mining.authorize
            auth_msg = {
                "id": 2,
                "method": "mining.authorize",
                "params": [self.wallet, self.password]
            }
            
            response = await self._send_stratum_message(auth_msg)
            
            if response and response.get('result') is True:
                self.authorized = True
                logger.info(f"Thread {self.thread_id}: Authorized with pool")
            else:
                error = response.get('error', 'Unknown authorization error')
                logger.error(f"Thread {self.thread_id}: Authorization failed: {error}")
                raise Exception(f"Authorization failed: {error}")
                
        except Exception as e:
            logger.error(f"Thread {self.thread_id}: Authorization error: {e}")
            raise

    async def _suggest_difficulty(self):
        """Suggest mining difficulty to pool"""
        try:
            # Suggest a reasonable difficulty based on expected hashrate
            suggested_difficulty = 1024  # Start with moderate difficulty
            
            suggest_msg = {
                "id": 3,
                "method": "mining.suggest_difficulty",
                "params": [suggested_difficulty]
            }
            
            await self._send_stratum_message(suggest_msg)
            logger.info(f"Thread {self.thread_id}: Suggested difficulty {suggested_difficulty}")
            
        except Exception as e:
            logger.debug(f"Thread {self.thread_id}: Difficulty suggestion failed: {e}")

    async def _send_stratum_message(self, message: dict) -> Optional[dict]:
        """Send Stratum message and get response"""
        if not self.socket:
            return None
            
        try:
            # Send message
            msg_str = json.dumps(message) + "\n"
            await asyncio.get_event_loop().run_in_executor(
                None, self.socket.send, msg_str.encode('utf-8')
            )
            
            # Receive response
            response_data = await asyncio.get_event_loop().run_in_executor(
                None, self.socket.recv, 4096
            )
            
            if response_data:
                response_str = response_data.decode('utf-8').strip()
                if response_str:
                    return json.loads(response_str)
                    
        except Exception as e:
            logger.error(f"Thread {self.thread_id}: Stratum message error: {e}")
            
        return None

    async def _mining_loop(self):
        """Main mining loop"""
        if not self.authorized:
            return
            
        logger.info(f"Thread {self.thread_id}: Starting mining loop")
        
        # Initialize work data
        await self._get_work()
        
        nonce = 0
        while self.running and self.connected:
            try:
                # Mine with current work
                if self.current_work:
                    result = await self._mine_work(nonce)
                    
                    if result:
                        # Found valid share, submit it
                        await self._submit_share(result)
                    
                    nonce += 1
                    
                    # Update statistics
                    self._update_local_stats()
                    
                    # Get new work periodically or when needed
                    if nonce % 1000 == 0:  # Every 1000 nonces
                        await self._get_work()
                        
                else:
                    # No work available, wait and retry
                    await asyncio.sleep(1)
                    await self._get_work()
                    
            except Exception as e:
                logger.error(f"Thread {self.thread_id}: Mining loop error: {e}")
                await asyncio.sleep(1)

    async def _get_work(self):
        """Request work from pool"""
        try:
            # In Stratum, work comes via mining.notify
            # For now, create dummy work to keep mining
            if not self.current_work:
                self.current_work = {
                    'version': '00000002',
                    'prevhash': '0' * 64,
                    'merkleroot': '0' * 64,
                    'timestamp': hex(int(time.time()))[2:].zfill(8),
                    'bits': '1e0fffff',  # Minimum difficulty
                    'nonce': '00000000'
                }
                
                # Set target based on bits
                self.target = self._bits_to_target(self.current_work['bits'])
                
        except Exception as e:
            logger.error(f"Thread {self.thread_id}: Get work error: {e}")

    def _bits_to_target(self, bits_hex: str) -> int:
        """Convert difficulty bits to target value"""
        try:
            bits = int(bits_hex, 16)
            exponent = bits >> 24
            mantissa = bits & 0xffffff
            
            if exponent <= 3:
                target = mantissa >> (8 * (3 - exponent))
            else:
                target = mantissa << (8 * (exponent - 3))
                
            return target
            
        except Exception:
            return 0x00000000FFFF0000000000000000000000000000000000000000000000000000

    async def _mine_work(self, nonce: int) -> Optional[dict]:
        """Mine the current work with given nonce"""
        if not self.current_work:
            return None
            
        try:
            # Build block header
            header = self._build_block_header(nonce)
            
            # Compute Scrypt hash
            if SCRYPT_AVAILABLE:
                hash_result = scrypt.hash(header, header, 1024, 1, 1, 32)
            else:
                # Fallback to SHA256 (not real Scrypt, but for testing)
                hash_result = hashlib.sha256(header).digest()
            
            # Convert to integer for comparison
            hash_int = int.from_bytes(hash_result, 'big')
            
            self.hash_count += 1
            
            # Check if hash meets target
            if hash_int < self.target:
                return {
                    'nonce': nonce,
                    'hash': hash_result.hex(),
                    'header': header.hex()
                }
                
        except Exception as e:
            logger.error(f"Thread {self.thread_id}: Mining work error: {e}")
            
        return None

    def _build_block_header(self, nonce: int) -> bytes:
        """Build block header for hashing"""
        try:
            version = bytes.fromhex(self.current_work['version'])
            prevhash = bytes.fromhex(self.current_work['prevhash'])
            merkleroot = bytes.fromhex(self.current_work['merkleroot'])
            timestamp = bytes.fromhex(self.current_work['timestamp'])
            bits = bytes.fromhex(self.current_work['bits'])
            nonce_bytes = struct.pack('<I', nonce)
            
            header = version + prevhash + merkleroot + timestamp + bits + nonce_bytes
            return header
            
        except Exception as e:
            logger.error(f"Thread {self.thread_id}: Header build error: {e}")
            return b'\x00' * 80

    async def _submit_share(self, result: dict):
        """Submit mining share to pool"""
        try:
            submit_msg = {
                "id": 4,
                "method": "mining.submit",
                "params": [
                    self.wallet,
                    "1",  # Job ID (would come from mining.notify)
                    "00000000",  # Extranonce2
                    self.current_work['timestamp'],
                    hex(result['nonce'])[2:].zfill(8)
                ]
            }
            
            response = await self._send_stratum_message(submit_msg)
            
            if response:
                if response.get('result') is True:
                    self.stats['accepted_shares'] += 1
                    logger.info(f"Thread {self.thread_id}: Share accepted! ✅")
                else:
                    self.stats['rejected_shares'] += 1
                    error = response.get('error', 'Unknown error')
                    logger.warning(f"Thread {self.thread_id}: Share rejected: {error} ❌")
                    
        except Exception as e:
            logger.error(f"Thread {self.thread_id}: Share submission error: {e}")

    def _update_local_stats(self):
        """Update local statistics"""
        current_time = time.time()
        time_diff = current_time - self.last_hash_time
        
        if time_diff >= 1.0:  # Update every second
            # Calculate hashrate
            hashrate = self.hash_count / time_diff
            self.stats['hashrate'] = hashrate
            self.stats['hashes'] += self.hash_count
            self.stats['difficulty'] = self.difficulty
            
            # Reset counters
            self.hash_count = 0
            self.last_hash_time = current_time
            
            # Callback to mining engine
            if self.stats_callback:
                self.stats_callback(self.stats.copy())

    def adjust_difficulty(self, new_difficulty: float):
        """Adjust mining difficulty"""
        self.difficulty = new_difficulty
        # Recalculate target based on new difficulty
        base_target = 0x00000000FFFF0000000000000000000000000000000000000000000000000000
        self.target = int(base_target / new_difficulty)
        
        logger.info(f"Thread {self.thread_id}: Difficulty adjusted to {new_difficulty}")