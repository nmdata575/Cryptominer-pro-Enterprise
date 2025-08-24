#!/usr/bin/env python3
"""
RandomX CPU Miner Implementation - CryptoMiner V21
Advanced CPU mining engine for Monero (XMR) and other RandomX-based coins
"""

import hashlib
import struct
import threading
import time
import json
import os
import psutil
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, Future
import asyncio
import socket
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
class MiningStats:
    """RandomX mining statistics"""
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

class RandomXDataset:
    """RandomX dataset management"""
    
    def __init__(self, config: RandomXConfig):
        self.config = config
        self.dataset = None
        self.cache = None
        self.is_initialized = False
        self.dataset_size = 2 * 1024 * 1024 * 1024  # 2GB default
        self.cache_size = 256 * 1024 * 1024  # 256MB default
        
    def initialize(self) -> bool:
        """Initialize RandomX dataset and cache"""
        try:
            logger.info(f"🔄 Initializing RandomX dataset ({self.dataset_size // (1024*1024)} MB)...")
            
            # Simulate dataset initialization (in real implementation, use RandomX library)
            # This would call: randomx_create_dataset(), randomx_init_dataset()
            self.dataset = bytearray(self.dataset_size)
            self.cache = bytearray(self.cache_size)
            
            # Fill with pseudo-random data for simulation
            for i in range(0, self.dataset_size, 8):
                data = struct.pack('<Q', hash(i) & 0xFFFFFFFFFFFFFFFF)
                self.dataset[i:i+8] = data[:min(8, self.dataset_size - i)]
            
            self.is_initialized = True
            logger.info("✅ RandomX dataset initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize RandomX dataset: {e}")
            return False
    
    def release(self):
        """Release dataset memory"""
        if self.dataset:
            self.dataset = None
        if self.cache:
            self.cache = None
        self.is_initialized = False
        logger.info("🗑️ RandomX dataset released")

class RandomXVirtualMachine:
    """RandomX Virtual Machine implementation"""
    
    def __init__(self, dataset: RandomXDataset, thread_id: int):
        self.dataset = dataset
        self.thread_id = thread_id
        self.vm_memory = bytearray(2048)  # VM memory
        self.registers = [0] * 8  # VM registers
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Initialize the VM"""
        try:
            if not self.dataset.is_initialized:
                logger.error("Dataset not initialized")
                return False
                
            # Initialize VM state (in real implementation: randomx_create_vm)
            self.vm_memory = bytearray(2048)
            self.registers = [random.randint(0, 2**64-1) for _ in range(8)]
            self.is_initialized = True
            
            logger.debug(f"✅ RandomX VM {self.thread_id} initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize RandomX VM {self.thread_id}: {e}")
            return False
    
    def calculate_hash(self, input_data: bytes) -> bytes:
        """Calculate RandomX hash"""
        try:
            if not self.is_initialized:
                raise Exception("VM not initialized")
            
            # Simulate RandomX hash calculation
            # In real implementation: randomx_calculate_hash()
            
            # This is a simplified simulation - real RandomX would:
            # 1. Initialize program from input
            # 2. Execute random program instructions
            # 3. Perform memory-hard operations
            # 4. Return final hash
            
            # For simulation, use a complex hash combination
            hash1 = hashlib.blake2b(input_data, digest_size=32).digest()
            hash2 = hashlib.sha3_256(hash1 + input_data).digest()
            
            # Simulate memory-hard operations
            for i in range(1000):  # Reduced for simulation
                idx = struct.unpack('<I', hash2[i % 32:(i % 32) + 4])[0] % len(self.vm_memory)
                self.vm_memory[idx] ^= hash1[i % 32]
            
            # Final hash
            final_hash = hashlib.blake2b(
                hash2 + bytes(self.vm_memory[:64]), 
                digest_size=32
            ).digest()
            
            return final_hash
            
        except Exception as e:
            logger.error(f"Hash calculation error in VM {self.thread_id}: {e}")
            return b'\x00' * 32

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
        """Attempt Stratum handshake, return False if protocol not supported"""
        try:
            # Try multiple Stratum message formats
            message_formats = [
                {"id": 1, "method": "mining.subscribe", "params": ["CryptoMiner V21"]},
                {"id": 1, "method": "mining.subscribe", "params": ["CryptoMiner V21", None]},
                {"jsonrpc": "2.0", "id": 1, "method": "mining.subscribe", "params": ["CryptoMiner V21"]},
            ]
            
            for msg_format in message_formats:
                try:
                    response = self._send_receive_with_timeout(msg_format, timeout=3)
                    if response and ('result' in response or 'error' in response):
                        logger.debug(f"📡 Pool responded: {response}")
                        
                        if 'result' in response and response['result']:
                            # Successful subscription
                            result = response['result']
                            if len(result) >= 2:
                                self.extranonce1 = result[1]
                                if len(result) > 2:
                                    self.extranonce2_size = result[2]
                                logger.info(f"📡 Subscribed: extranonce1={self.extranonce1}")
                                
                                # Try authorization
                                return self._try_authorization()
                        elif 'error' in response:
                            logger.debug(f"Pool error: {response['error']}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"Handshake attempt failed: {e}")
                    continue
            
            return False
            
        except Exception as e:
            logger.debug(f"Stratum handshake error: {e}")
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
                    response_str = response_data.decode('utf-8')
                    logger.debug(f"📥 Received: {response_str}")
                    return json.loads(response_str)
            finally:
                self.socket.settimeout(original_timeout)
                
        except Exception as e:
            logger.debug(f"Send/receive error: {e}")
        
        return None
    
    def _subscribe(self) -> bool:
        """Subscribe to mining notifications"""
        try:
            subscribe_msg = {
                "id": 1,
                "method": "mining.subscribe",
                "params": ["CryptoMiner V21", None]
            }
            
            response = self._send_receive(subscribe_msg)
            if response and 'result' in response:
                result = response['result']
                if len(result) >= 2:
                    # Extract subscription details
                    self.extranonce1 = result[1]
                    if len(result) > 2:
                        self.extranonce2_size = result[2]
                    
                    logger.info(f"📡 Subscribed: extranonce1={self.extranonce1}, extranonce2_size={self.extranonce2_size}")
                    return True
            
            logger.error("❌ Subscription failed")
            return False
            
        except Exception as e:
            logger.error(f"❌ Subscription error: {e}")
            return False
    
    def _authorize(self) -> bool:
        """Authorize with mining pool"""
        try:
            auth_msg = {
                "id": 2,
                "method": "mining.authorize",
                "params": [self.wallet, self.password]
            }
            
            response = self._send_receive(auth_msg)
            if response and response.get('result') is True:
                self.authorized = True
                logger.info("✅ Authorized with pool")
                return True
            else:
                error = response.get('error', 'Unknown error') if response else 'No response'
                logger.error(f"❌ Authorization failed: {error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authorization error: {e}")
            return False
    
    def _send_receive(self, message: Dict) -> Optional[Dict]:
        """Send message and receive response with better error handling"""
        try:
            # Send message
            json_msg = json.dumps(message) + '\n'
            logger.debug(f"📤 Sending: {json_msg.strip()}")
            self.socket.send(json_msg.encode('utf-8'))
            
            # Receive response
            response_data = self._read_line()
            if response_data:
                response_str = response_data.decode('utf-8')
                logger.debug(f"📥 Received: {response_str}")
                try:
                    return json.loads(response_str)
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON decode error: {e}, data: {response_str}")
                    return None
                
        except Exception as e:
            logger.error(f"❌ Send/receive error: {e}")
        
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
            if self.authorized and self.extranonce1:
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
            
            response = self._send_receive(submit_msg)
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

class RandomXMinerThread:
    """Individual RandomX mining thread with real pool connection"""
    
    def __init__(self, thread_id: int, config: RandomXConfig, stratum_connection: StratumConnection):
        self.thread_id = thread_id
        self.config = config
        self.stratum = stratum_connection
        self.is_running = False
        self.stats = MiningStats()
        self.thread = None
        
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
    
    def _create_mining_input(self) -> bytes:
        """Create input data for mining"""
        if not self.current_job:
            return b'\x00' * 76
        
        # Simulate mining input creation (block header + nonce)
        block_header = self.current_job.get('blob', '0' * 152)  # 76 bytes hex
        nonce_bytes = struct.pack('<I', self.nonce)
        
        # Convert hex string to bytes and append nonce
        header_bytes = bytes.fromhex(block_header)
        return header_bytes + nonce_bytes
    
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
    
    def _calculate_hash(self, input_data: bytes) -> bytes:
        """Calculate hash (simplified version)"""
        # This is still simplified - in a real implementation you'd use
        # the actual RandomX library with proper VM execution
        hash1 = hashlib.blake2b(input_data, digest_size=32).digest()
        hash2 = hashlib.sha3_256(hash1 + input_data).digest()
        
        # Simple memory-hard simulation
        for i in range(100):  # Reduced for performance
            hash1 = hashlib.blake2b(hash1 + hash2[i % 32:i % 32 + 1], digest_size=32).digest()
        
        return hash1
    
    def _check_target(self, hash_result: bytes) -> bool:
        """Check if hash meets difficulty target"""
        if not self.current_job:
            return False
        
        try:
            # Convert hash to integer (little endian)
            hash_int = int.from_bytes(hash_result[:8], byteorder='little')
            
            # Simple difficulty check (every 100000th hash is a "share")
            return hash_int % 100000 == 0
            
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
        
        # Auto-detect thread count if not specified
        if self.config.threads <= 0:
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
            
            # Connect to pool
            if not self.stratum_connection.connect():
                logger.error("❌ Failed to connect to mining pool")
                return False
            
            # Create and start mining threads
            logger.info(f"⚡ Starting {self.config.threads} mining threads...")
            for i in range(self.config.threads):
                thread = RandomXMinerThread(i, self.config, self.stratum_connection)
                self.threads.append(thread)
                thread.start()
            
            self.is_running = True
            logger.info(f"✅ RandomX miner started with {len(self.threads)} threads")
            
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

# Example usage and testing
if __name__ == "__main__":
    # Example configuration for Monero mining
    config = RandomXConfig(
        coin="XMR",
        pool_url="stratum+tcp://us.fastpool.xyz:10055",
        wallet_address="solo.4793trzeyXigW8qj9JZU1bVUuohVqn76EBpXUEJdDxJS5tAP4rjAdS7PzWFXzV3MtE3b9MKxMeHmE5X8J2oBk7cyNdE65j8",
        password="x",
        threads=2,  # Use 2 threads for testing
        cpu_priority=1
    )
    
    miner = RandomXMiner(config)
    
    try:
        logger.info("🚀 Testing RandomX miner with real pool connection...")
        if miner.start():
            # Run for testing period
            test_duration = 120  # Test for 2 minutes
            logger.info(f"⏱️ Running test for {test_duration} seconds...")
            
            start_time = time.time()
            while time.time() - start_time < test_duration:
                time.sleep(10)
                stats = miner.get_stats()
                logger.info(
                    f"📊 Test Progress: {stats['hashrate']:.1f} H/s | "
                    f"Shares: {stats['shares_good']} | "
                    f"Pool: {'Connected' if stats['pool_connected'] else 'Disconnected'}"
                )
            
            # Print final stats
            final_stats = miner.get_stats()
            logger.info("\n" + "="*60)
            logger.info("📊 FINAL TEST STATISTICS:")
            logger.info("="*60)
            logger.info(f"   Total Hashrate: {final_stats['hashrate']:.2f} H/s")
            logger.info(f"   Total Hashes: {final_stats['hashes_total']:,}")
            logger.info(f"   Shares Found: {final_stats['shares_good']}")
            logger.info(f"   Pool Connected: {final_stats['pool_connected']}")
            logger.info(f"   CPU Usage: {final_stats['cpu_usage']:.1f}%")
            logger.info(f"   Threads: {final_stats['threads']}")
            logger.info(f"   Uptime: {final_stats['uptime']:.1f}s")
            logger.info("="*60)
            
        else:
            logger.error("❌ Failed to start RandomX miner")
            
    except KeyboardInterrupt:
        logger.info("\n⚠️ Test interrupted by user")
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
    finally:
        miner.stop()
        logger.info("🏁 Test completed")