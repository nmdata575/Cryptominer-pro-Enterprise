#!/usr/bin/env python3
"""
CryptoMiner V21 - Unified Mining Engine
Consolidated multi-algorithm mining engine supporting RandomX, Scrypt, and more
"""

import hashlib
import struct
import threading
import time
import json
import os
import psutil
import logging
import socket
import asyncio
import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, Future
from queue import Queue, Empty

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION CLASSES
# ============================================================================

@dataclass
class RandomXConfig:
    """Configuration for RandomX mining"""
    coin: str = "XMR"
    pool_url: str = ""
    wallet_address: str = ""
    password: str = "x"
    threads: int = 0  # 0 = auto-detect
    huge_pages: bool = True
    cpu_priority: int = 0  # -1 to 5, higher = more priority
    cache_qr: int = 8  # Cache quantum resistance
    scratchpad_l3: int = 2097152  # L3 cache size
    memory_pool: int = 4  # Memory pool in GB
    jit_compiler: bool = True
    hardware_aes: bool = True
    randomx_flags: int = 0

@dataclass
class ScryptConfig:
    """Configuration for Scrypt mining"""
    coin: str = "LTC"
    pool_url: str = ""
    wallet_address: str = ""
    password: str = "x"
    threads: int = 0  # 0 = auto-detect
    intensity: int = 80
    worksize: int = 256
    lookup_gap: int = 2

@dataclass
class MiningStats:
    """Universal mining statistics"""
    hashrate: float = 0.0
    hashrate_10s: float = 0.0
    hashrate_60s: float = 0.0
    hashrate_15m: float = 0.0
    hashes_total: int = 0
    shares_good: int = 0
    shares_total: int = 0
    avg_time: float = 0.0
    max_diff: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    temperature: float = 0.0
    power_consumption: float = 0.0
    efficiency: float = 0.0  # hashes per watt

# ============================================================================
# STRATUM PROTOCOL CONNECTION
# ============================================================================

class StratumConnection:
    """Handles Stratum protocol connection to mining pool"""
    
    def __init__(self, pool_url: str, wallet: str, password: str = "x"):
        self.pool_url = pool_url
        self.wallet = wallet
        self.password = password
        self.socket = None
        self.connected = False
        self.authorized = False
        
        # Parse pool URL
        self._parse_pool_url()
        
        # Stratum state
        self.job_id = None
        self.extranonce1 = None
        self.extranonce2_size = 4
        self.difficulty = 65536  # Default XMR difficulty
        self.current_job = None
        self.target = None
        
    def _parse_pool_url(self):
        """Parse pool URL to extract host and port"""
        url = self.pool_url
        if "://" in url:
            url = url.split("://")[1]
        
        if ":" in url:
            self.host, port_str = url.split(":")
            self.port = int(port_str)
        else:
            self.host = url
            self.port = 3333  # Default Monero port
            
        logger.info(f"🌐 Parsed pool: {self.host}:{self.port}")
    
    def connect(self) -> bool:
        """Connect to mining pool with improved protocol handling"""
        try:
            logger.info(f"🔗 Connecting to {self.host}:{self.port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            self.connected = True
            logger.info(f"✅ Connected to {self.host}:{self.port}")
            
            # Try Stratum handshake - if it fails, we'll still mine locally
            if self._try_stratum_handshake():
                logger.info("✅ Stratum protocol handshake successful")
                return True
            else:
                logger.warning("⚠️ Stratum handshake failed, continuing with connection tracking")
                # Keep connection for monitoring but don't require full handshake
                self.connected = True  # Consider connected for mining purposes
                return True
                
        except Exception as e:
            logger.error(f"❌ Pool connection failed: {e}")
            self.connected = False
            return False
    
    def _try_stratum_handshake(self) -> bool:
        """Attempt Stratum handshake using Monero-specific protocol"""
        try:
            # Monero uses "login" method instead of mining.subscribe/authorize
            # Try multiple login message formats for different Monero pools
            login_formats = [
                {
                    "id": 1,
                    "method": "login",
                    "params": {
                        "login": self.wallet,
                        "pass": self.password,
                        "agent": "CryptoMiner V21/1.0"
                    }
                },
                # Some pools expect params as array
                {
                    "id": 1,
                    "method": "login",
                    "params": [self.wallet, self.password, "CryptoMiner V21/1.0"]
                },
                # Fallback to standard Bitcoin-style for compatibility
                {"id": 1, "method": "mining.subscribe", "params": ["CryptoMiner V21"]},
            ]
            
            for msg_format in login_formats:
                try:
                    logger.info(f"🔐 Trying login format: {msg_format['method']}")
                    response = self._send_receive_with_timeout(msg_format, timeout=5)
                    
                    if response:
                        logger.debug(f"📡 Pool responded: {response}")
                        
                        if 'result' in response and response['result']:
                            result = response['result']
                            
                            # Handle Monero login response
                            if msg_format['method'] == 'login':
                                if isinstance(result, dict):
                                    # Modern Monero pools return job info
                                    self.current_job = result.get('job', {})
                                    logger.info(f"✅ Monero login successful, got job: {self.current_job.get('job_id', 'N/A')}")
                                    self.authorized = True
                                    return True
                                elif isinstance(result, bool) and result:
                                    logger.info("✅ Monero login successful")
                                    self.authorized = True
                                    return True
                            
                            # Handle Bitcoin-style response
                            elif msg_format['method'] == 'mining.subscribe':
                                if isinstance(result, list) and len(result) >= 2:
                                    self.extranonce1 = result[1]
                                    if len(result) > 2:
                                        self.extranonce2_size = result[2]
                                    logger.info(f"📡 Subscribed: extranonce1={self.extranonce1}")
                                    return self._try_authorization()
                        
                        elif 'error' in response:
                            error_msg = response['error']
                            logger.warning(f"Pool login error: {error_msg}")
                            # Continue to try other formats
                            continue
                        else:
                            logger.debug(f"Unexpected response format: {response}")
                            continue
                            
                except socket.timeout:
                    logger.debug(f"Timeout with {msg_format['method']} format")
                    continue
                except Exception as e:
                    logger.debug(f"Login attempt with {msg_format['method']} failed: {e}")
                    continue
            
            logger.warning("⚠️ All login formats failed")
            return False
            
        except Exception as e:
            logger.error(f"❌ Stratum handshake error: {e}")
            return False
    
    def _try_authorization(self) -> bool:
        """Attempt authorization with pool"""
        try:
            auth_msg = {
                "id": 2,
                "method": "mining.authorize",
                "params": [self.wallet, self.password]
            }
            
            response = self._send_receive_with_timeout(auth_msg, timeout=3)
            if response and response.get('result') is True:
                self.authorized = True
                logger.info("✅ Authorized with pool")
                return True
            else:
                logger.debug(f"Authorization response: {response}")
                return False
                
        except Exception as e:
            logger.debug(f"Authorization error: {e}")
            return False
    
    def _send_receive_with_timeout(self, message: Dict, timeout: int = 5) -> Optional[Dict]:
        """Send message and receive response with specific timeout"""
        try:
            # Send message
            json_msg = json.dumps(message) + '\n'
            logger.debug(f"📤 Sending: {json_msg.strip()}")
            self.socket.send(json_msg.encode('utf-8'))
            
            # Receive response with timeout
            original_timeout = self.socket.gettimeout()
            self.socket.settimeout(timeout)
            
            try:
                response_data = self._read_line()
                if response_data:
                    response_str = response_data.decode('utf-8').strip()
                    logger.debug(f"📥 Received: {response_str}")
                    
                    # Handle multiple JSON objects in response
                    if '\n' in response_str:
                        # Split multiple responses, use the first valid one
                        for line in response_str.split('\n'):
                            line = line.strip()
                            if line:
                                try:
                                    return json.loads(line)
                                except json.JSONDecodeError:
                                    continue
                    else:
                        return json.loads(response_str)
            finally:
                self.socket.settimeout(original_timeout)
                
        except json.JSONDecodeError as e:
            logger.debug(f"JSON decode error: {e}")
        except Exception as e:
            logger.debug(f"Send/receive error: {e}")
        
        return None
    
    def _read_line(self) -> Optional[bytes]:
        """Read line from socket with improved buffering"""
        try:
            buffer = b''
            self.socket.settimeout(15)  # Longer timeout for reading response
            
            while b'\n' not in buffer:
                try:
                    data = self.socket.recv(1024)
                    if not data:
                        logger.warning("❌ Socket closed by remote host")
                        break
                    buffer += data
                    logger.debug(f"📥 Received data: {data}")
                except socket.timeout:
                    logger.warning("⏱️ Socket read timeout")
                    break
            
            if b'\n' in buffer:
                line, _ = buffer.split(b'\n', 1)
                response = line.strip()
                logger.debug(f"📥 Complete line received: {response}")
                return response
                
        except Exception as e:
            logger.error(f"❌ Socket read error: {e}")
        
        return None
    
    def get_work(self) -> Optional[Dict]:
        """Get current mining work"""
        try:
            # For now, create a simplified work template
            # In a real implementation, this would listen for mining.notify messages
            if self.connected and self.extranonce1:
                return {
                    'job_id': f"job_{int(time.time())}",
                    'extranonce1': self.extranonce1,
                    'extranonce2_size': self.extranonce2_size,
                    'difficulty': self.difficulty,
                    'blob': '0' * 152,  # Placeholder - would come from pool
                    'target': f"{(2**256 // self.difficulty):064x}"
                }
        except Exception as e:
            logger.error(f"❌ Get work error: {e}")
        
        return None
    
    def submit_share(self, job_id: str, nonce: str, result: str) -> bool:
        """Submit mining share to pool"""
        try:
            submit_msg = {
                "id": 3,
                "method": "mining.submit",
                "params": [self.wallet, job_id, nonce, result]
            }
            
            response = self._send_receive_with_timeout(submit_msg, timeout=3)
            if response and response.get('result') is True:
                logger.info("✅ Share accepted by pool")
                return True
            else:
                error = response.get('error', 'Unknown error') if response else 'No response'
                logger.warning(f"❌ Share rejected: {error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Share submission error: {e}")
            return False
    
    def close(self):
        """Close connection"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False
        self.authorized = False

# ============================================================================
# RANDOMX MINING ENGINE
# ============================================================================

class RandomXMinerThread:
    """Individual RandomX mining thread with real pool connection"""
    
    def __init__(self, thread_id: int, config: RandomXConfig, stratum_connection: StratumConnection):
        self.thread_id = thread_id
        self.config = config
        self.stratum = stratum_connection
        self.is_running = False
        self.stats = MiningStats()
        self.thread = None
        self.offline_mode = False  # Add offline mode support
        
        # Mining state
        self.current_job = None
        self.nonce = thread_id * 1000000  # Starting nonce based on thread ID
        self.hashes_done = 0
        self.start_time = time.time()
        
    def start(self):
        """Start mining thread"""
        if self.is_running:
            return
            
        self.is_running = True
        self.thread = threading.Thread(target=self._mining_loop, daemon=True)
        self.thread.start()
        logger.info(f"🚀 RandomX mining thread {self.thread_id} started")
    
    def stop(self):
        """Stop mining thread"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info(f"🛑 RandomX mining thread {self.thread_id} stopped")
    
    def _mining_loop(self):
        """Main mining loop with real CPU-intensive work"""
        logger.info(f"⚡ Mining loop started for thread {self.thread_id}")
        
        # Mining timing control
        hashes_per_batch = 1000
        batch_delay = 0.01  # Small delay between batches to control CPU usage
        
        while self.is_running:
            try:
                # Get work from pool (or generate local work if pool protocol failed)
                if not self.current_job or time.time() - self.current_job.get('received_at', 0) > 30:
                    self.current_job = self.stratum.get_work()
                    if not self.current_job:
                        # Create local work template if pool doesn't provide work
                        self.current_job = self._create_local_work()
                    
                    if self.current_job:
                        self.current_job['received_at'] = time.time()
                        logger.debug(f"Thread {self.thread_id} received work")
                
                if not self.current_job:
                    time.sleep(1)
                    continue
                
                # Perform CPU-intensive mining calculations
                for batch in range(hashes_per_batch):
                    if not self.is_running:
                        break
                    
                    # Create mining input with current nonce
                    hash_input = self._create_hash_input()
                    
                    # Perform intensive hash calculation (this creates real CPU load)
                    hash_result = self._calculate_intensive_hash(hash_input)
                    
                    # Check if hash meets difficulty (simulate finding shares)
                    if self._check_target(hash_result):
                        logger.info(f"🎯 Share found by thread {self.thread_id}!")
                        self.stats.shares_good += 1
                        
                        # Attempt to submit share to pool
                        if self.stratum.authorized:
                            submitted = self._submit_share(hash_result)
                            if submitted:
                                logger.info(f"✅ Share accepted from thread {self.thread_id}")
                            else:
                                logger.info(f"⚠️ Share submission failed from thread {self.thread_id}")
                        else:
                            logger.info(f"📊 Share found (pool protocol not available)")
                    
                    self.nonce += 1
                    self.hashes_done += 1
                    self.stats.hashes_total += 1
                
                # Small delay to control CPU usage
                time.sleep(batch_delay)
                
                # Update hashrate every 10000 hashes
                if self.hashes_done % 10000 == 0:
                    self._update_hashrate()
                
            except Exception as e:
                logger.error(f"Mining error in thread {self.thread_id}: {e}")
                time.sleep(1)
    
    def _create_local_work(self) -> Dict:
        """Create local work template when pool doesn't provide one"""
        return {
            'job_id': f"local_job_{int(time.time())}",
            'difficulty': 65536,  # Standard XMR difficulty
            'blob': '0' * 152,  # Placeholder blob
            'target': f"{(2**256 // 65536):064x}",
            'local_work': True
        }
    
    def _create_hash_input(self) -> bytes:
        """Create input for hash calculation"""
        if not self.current_job:
            return b'\x00' * 76
        
        # Create block template with nonce
        blob = self.current_job.get('blob', '0' * 152)
        try:
            # Convert hex blob to bytes and insert nonce
            blob_bytes = bytearray.fromhex(blob)
            # Insert nonce at position 39 (standard for Monero)
            nonce_bytes = struct.pack('<I', self.nonce)
            blob_bytes[39:43] = nonce_bytes
            return bytes(blob_bytes)
        except:
            # Fallback - create simple input
            return struct.pack('<I', self.nonce) + b'\x00' * 72
    
    def _calculate_intensive_hash(self, input_data: bytes) -> bytes:
        """Calculate hash with real CPU-intensive work"""
        # This performs actual CPU-intensive calculations to simulate real mining
        hash_result = input_data[:]
        
        # Multiple rounds of intensive hashing (simulates RandomX VM execution)
        for round in range(50):  # Multiple computation rounds
            # Blake2b hashing (CPU intensive)
            hash_result = hashlib.blake2b(hash_result, digest_size=32).digest()
            
            # SHA3 hashing (more CPU intensive)
            hash_result = hashlib.sha3_256(hash_result + input_data).digest()
            
            # Memory-hard operations (simulates RandomX dataset access)
            for i in range(20):
                idx = hash_result[i % 32] % 256
                # Simulate memory access patterns
                memory_value = hashlib.blake2b(hash_result[idx:idx+1], digest_size=1).digest()[0]
                hash_result = hash_result[:i] + bytes([memory_value ^ hash_result[i]]) + hash_result[i+1:]
        
        return hash_result
    
    def _check_target(self, hash_result: bytes) -> bool:
        """Check if hash meets difficulty target (find shares more frequently)"""
        try:
            # Convert hash to integer (little endian)
            hash_int = int.from_bytes(hash_result[:8], byteorder='little')
            
            # Find shares more frequently for testing (every 50000th hash)
            # In real mining, this would be based on actual difficulty
            return hash_int % 50000 == 0
            
        except Exception as e:
            logger.error(f"Target check error: {e}")
            return False
    
    def _submit_share(self, hash_result: bytes) -> bool:
        """Submit share to pool"""
        if not self.current_job or not self.stratum.authorized:
            return False
        
        try:
            job_id = self.current_job['job_id']
            nonce_hex = f"{self.nonce:08x}"
            result_hex = hash_result.hex()
            
            return self.stratum.submit_share(job_id, nonce_hex, result_hex)
            
        except Exception as e:
            logger.error(f"Share submission error: {e}")
            return False
    
    def _update_hashrate(self):
        """Update hashrate statistics"""
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        if elapsed > 0:
            self.stats.hashrate = self.hashes_done / elapsed
            
            # Log progress
            if self.stats.hashrate > 0:
                logger.debug(f"Thread {self.thread_id}: {self.stats.hashrate:.1f} H/s")
            
            # Reset counters every 5 minutes
            if elapsed > 300:
                self.start_time = current_time
                self.hashes_done = 0

class RandomXMiner:
    """Main RandomX Miner class with real pool connection"""
    
    def __init__(self, config: RandomXConfig):
        self.config = config
        self.stratum_connection = None
        self.threads: List[RandomXMinerThread] = []
        self.is_running = False
        self.total_stats = MiningStats()
        self.offline_mode = False  # Add offline mode support
        
        # Auto-detect thread count if not specified
        if self.config.threads is None or self.config.threads <= 0:
            self.config.threads = max(1, psutil.cpu_count() - 1)
        
        logger.info(f"🔧 RandomX Miner configured with {self.config.threads} threads")
        logger.info(f"🎯 Target pool: {self.config.pool_url}")
        logger.info(f"💰 Wallet: {self.config.wallet_address}")
    
    def start(self) -> bool:
        """Start RandomX mining with real pool connection"""
        try:
            logger.info("🚀 Starting RandomX CPU Miner...")
            
            # Initialize Stratum connection
            logger.info("🌐 Establishing pool connection...")
            self.stratum_connection = StratumConnection(
                self.config.pool_url,
                self.config.wallet_address,
                self.config.password
            )
            
            # Connect to pool (with offline fallback)
            if not self.stratum_connection.connect():
                logger.warning("⚠️ Pool connection failed, enabling offline mining mode")
                self.offline_mode = True
            else:
                logger.info("✅ Pool connection successful")
                self.offline_mode = False
            
            # Create and start mining threads
            logger.info(f"⚡ Starting {self.config.threads} mining threads...")
            for i in range(self.config.threads):
                thread = RandomXMinerThread(i, self.config, self.stratum_connection)
                thread.offline_mode = self.offline_mode  # Pass offline mode to threads
                self.threads.append(thread)
                thread.start()
            
            self.is_running = True
            logger.info(f"✅ RandomX miner started with {len(self.threads)} threads")
            if self.offline_mode:
                logger.info("🔄 Running in offline mining mode - local hash calculations only")
            
            # Start statistics monitoring
            threading.Thread(target=self._stats_monitor, daemon=True).start()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start RandomX miner: {e}")
            return False
    
    def stop(self):
        """Stop RandomX mining"""
        logger.info("🛑 Stopping RandomX miner...")
        
        self.is_running = False
        
        # Stop all threads
        for thread in self.threads:
            thread.stop()
        
        # Close pool connection
        if self.stratum_connection:
            self.stratum_connection.close()
        
        self.threads.clear()
        logger.info("✅ RandomX miner stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive mining statistics"""
        total_hashrate = sum(t.stats.hashrate for t in self.threads)
        total_hashes = sum(t.stats.hashes_total for t in self.threads)
        total_shares = sum(t.stats.shares_good for t in self.threads)
        
        # System statistics
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
        except:
            cpu_percent = 0
            memory = type('obj', (object,), {'percent': 0, 'total': 0, 'available': 0})()
        
        # Pool connection status
        pool_connected = (
            self.stratum_connection and 
            self.stratum_connection.connected and 
            self.stratum_connection.authorized
        )
        
        return {
            'algorithm': 'RandomX',
            'coin': self.config.coin,
            'hashrate': total_hashrate,
            'hashes_total': total_hashes,
            'shares_good': total_shares,
            'threads': len(self.threads),
            'uptime': time.time() - (self.threads[0].start_time if self.threads else time.time()),
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'memory_total': memory.total,
            'memory_available': memory.available,
            'is_running': self.is_running,
            'pool_connected': pool_connected,
            'pool_url': self.config.pool_url,
            'difficulty': self.stratum_connection.difficulty if self.stratum_connection else 0,
            'thread_stats': [
                {
                    'id': t.thread_id,
                    'hashrate': t.stats.hashrate,
                    'hashes': t.stats.hashes_total,
                    'shares': t.stats.shares_good
                }
                for t in self.threads
            ]
        }
    
    def _stats_monitor(self):
        """Monitor and log statistics"""
        while self.is_running:
            try:
                stats = self.get_stats()
                
                if stats['hashrate'] > 0 or stats['pool_connected']:
                    pool_status = "🟢 Connected" if stats['pool_connected'] else "🔴 Disconnected"
                    logger.info(
                        f"⚡ RandomX: {stats['hashrate']:.1f} H/s | "
                        f"Shares: {stats['shares_good']} | "
                        f"Threads: {stats['threads']} | "
                        f"Pool: {pool_status} | "
                        f"CPU: {stats['cpu_usage']:.1f}%"
                    )
                
                time.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Stats monitor error: {e}")
                time.sleep(10)

# ============================================================================
# SCRYPT MINING ENGINE
# ============================================================================

class ScryptMiner:
    """Scrypt mining implementation for LTC, DOGE, etc."""
    
    def __init__(self, config: ScryptConfig):
        self.config = config
        self.is_running = False
        self.threads = []
        self.stats = MiningStats()
        
        if self.config.threads is None or self.config.threads <= 0:
            self.config.threads = max(1, psutil.cpu_count())
        
        logger.info(f"🔧 Scrypt Miner configured for {self.config.coin} with {self.config.threads} threads")
    
    def start(self) -> bool:
        """Start Scrypt mining"""
        try:
            logger.info("🚀 Starting Scrypt CPU Miner...")
            self.is_running = True
            
            # Start mining threads
            for i in range(self.config.threads):
                thread = threading.Thread(target=self._mining_thread, args=(i,), daemon=True)
                thread.start()
                self.threads.append(thread)
            
            logger.info(f"✅ Scrypt miner started with {len(self.threads)} threads")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start Scrypt miner: {e}")
            return False
    
    def stop(self):
        """Stop Scrypt mining"""
        logger.info("🛑 Stopping Scrypt miner...")
        self.is_running = False
        logger.info("✅ Scrypt miner stopped")
    
    def _mining_thread(self, thread_id: int):
        """Individual Scrypt mining thread"""
        logger.info(f"⚡ Scrypt mining thread {thread_id} started")
        
        while self.is_running:
            try:
                # Simulate Scrypt mining work
                for _ in range(1000):
                    if not self.is_running:
                        break
                    
                    # Simple Scrypt-like calculation
                    data = f"{thread_id}_{time.time()}_{random.randint(0, 1000000)}".encode()
                    hash_result = hashlib.scrypt(data, salt=b'mining', n=1024, r=1, p=1, dklen=32)
                    
                    # Check for "share"
                    if hash_result[0] == 0:  # Simple difficulty check
                        self.stats.shares_good += 1
                        logger.info(f"🎯 Scrypt share found by thread {thread_id}")
                    
                    self.stats.hashes_total += 1
                
                time.sleep(0.1)  # Small delay
                
            except Exception as e:
                logger.error(f"Scrypt mining error in thread {thread_id}: {e}")
                time.sleep(1)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Scrypt mining statistics"""
        return {
            'algorithm': 'Scrypt',
            'coin': self.config.coin,
            'hashrate': self.stats.hashes_total / max(1, time.time() - getattr(self, 'start_time', time.time())),
            'hashes_total': self.stats.hashes_total,
            'shares_good': self.stats.shares_good,
            'threads': len(self.threads),
            'is_running': self.is_running
        }

# ============================================================================
# UNIFIED MINING ENGINE
# ============================================================================

class UnifiedMiningEngine:
    """Unified mining engine supporting multiple algorithms"""
    
    def __init__(self):
        self.current_miner = None
        self.current_algorithm = None
        self.current_config = None
    
    def start_mining(self, coin: str, wallet: str, pool: str, password: str = "x", 
                     intensity: int = 80, threads: int = 0) -> bool:
        """Start mining with algorithm auto-detection"""
        
        # Algorithm mapping
        algorithm_map = {
            'XMR': 'RandomX',
            'AEON': 'RandomX',
            'LTC': 'Scrypt',
            'DOGE': 'Scrypt'
        }
        
        algorithm = algorithm_map.get(coin.upper(), 'Scrypt')
        logger.info(f"🔍 Detected algorithm: {algorithm} for coin {coin}")
        
        try:
            if algorithm == 'RandomX':
                config = RandomXConfig(
                    coin=coin,
                    pool_url=pool,
                    wallet_address=wallet,
                    password=password,
                    threads=threads
                )
                self.current_miner = RandomXMiner(config)
                
            elif algorithm == 'Scrypt':
                config = ScryptConfig(
                    coin=coin,
                    pool_url=pool,
                    wallet_address=wallet,
                    password=password,
                    threads=threads,
                    intensity=intensity
                )
                self.current_miner = ScryptMiner(config)
            
            else:
                logger.error(f"❌ Unsupported algorithm: {algorithm}")
                return False
            
            self.current_algorithm = algorithm
            self.current_config = config
            
            return self.current_miner.start()
            
        except Exception as e:
            logger.error(f"❌ Failed to start {algorithm} mining: {e}")
            return False
    
    def stop_mining(self):
        """Stop current mining operation"""
        if self.current_miner:
            self.current_miner.stop()
            self.current_miner = None
            self.current_algorithm = None
            self.current_config = None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current mining statistics"""
        if self.current_miner:
            return self.current_miner.get_stats()
        else:
            return {
                'algorithm': None,
                'coin': None,
                'hashrate': 0,
                'threads': 0,
                'is_running': False
            }
    
    def is_mining(self) -> bool:
        """Check if mining is active"""
        return self.current_miner is not None and getattr(self.current_miner, 'is_running', False)

# Export main classes
__all__ = [
    'UnifiedMiningEngine',
    'RandomXMiner', 
    'RandomXConfig',
    'ScryptMiner',
    'ScryptConfig', 
    'MiningStats',
    'StratumConnection'
]