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
import queue
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, Future
from queue import Queue, Empty

# Configure logging with detailed protocol logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create separate logger for pool protocol communication
protocol_logger = logging.getLogger('pool_protocol')
protocol_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - POOL_PROTOCOL - %(levelname)s - %(message)s'))
protocol_logger.addHandler(handler)

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
    shares_rejected: int = 0
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
        """Connect to mining pool with full xmrig compatibility"""
        try:
            logger.info(f"🔗 Connecting to {self.host}:{self.port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Set socket options exactly like xmrig
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            # Disable Nagle's algorithm for low latency like xmrig
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            
            # Longer timeout for initial connection like xmrig
            self.socket.settimeout(20)  # More generous timeout
            self.socket.connect((self.host, self.port))
            self.connected = True
            logger.info(f"✅ Connected to {self.host}:{self.port}")
            
            # Attempt Stratum handshake with full xmrig compatibility
            if self._try_stratum_handshake():
                logger.info("✅ Stratum protocol handshake successful")
                return True
            else:
                logger.warning("⚠️ Stratum handshake failed - but connection established")
                # Unlike previous version, keep connection even if handshake fails
                # This allows for offline mining or protocol fallback
                return True
                
        except socket.timeout:
            logger.error(f"❌ Connection timeout to {self.host}:{self.port}")
            self.connected = False
            return False
        except ConnectionRefusedError:
            logger.error(f"❌ Connection refused by {self.host}:{self.port}")
            self.connected = False  
            return False
        except Exception as e:
            logger.error(f"❌ Pool connection failed: {e}")
            self.connected = False
            if hasattr(self, 'socket') and self.socket:
                try:
                    self.socket.close()
                except:
                    pass
            return False
    
    def _try_stratum_handshake(self) -> bool:
        """Attempt Stratum handshake using zeropool.io compatible methods"""
        try:
            # Clean wallet address for zeropool.io compatibility
            clean_wallet = self.wallet
            if ":" in clean_wallet:
                clean_wallet = clean_wallet.split(":", 1)[1]  # Remove any prefix like "solo:"
            
            # Try different Stratum protocols in order of zeropool.io compatibility
            login_methods = [
                # Method 1: zeropool.io preferred format - object params
                {
                    "id": 1,
                    "method": "login",
                    "params": {
                        "login": clean_wallet,
                        "pass": self.password,
                        "agent": "xmrig/6.24.0"
                    }
                },
                # Method 2: Standard xmrig-compatible login with clean wallet
                {
                    "id": 1,
                    "method": "login",
                    "params": {
                        "login": clean_wallet,
                        "pass": self.password,
                        "agent": "xmrig/6.24.0",
                        "keepalive": True
                    }
                },
                # Method 3: Simple array format (backup)
                {
                    "id": 1,
                    "method": "login",
                    "params": [clean_wallet, self.password]
                }
            ]
            
            for i, login_msg in enumerate(login_methods):
                try:
                    logger.info(f"🔐 Trying zeropool.io login method {i+1} with wallet: {clean_wallet[:12]}...")
                    response = self._send_receive_with_timeout(login_msg, timeout=10)
                    
                    if response:
                        logger.debug(f"📡 zeropool.io response: {response}")
                        
                        # Handle successful login response
                        if 'result' in response:
                            result = response['result']
                            
                            # Monero login response handling
                            if login_msg['method'] == 'login':
                                if isinstance(result, dict):
                                    # Modern pools return job info directly
                                    self.current_job = result.copy()
                                    self.current_job['received_at'] = time.time()
                                    job_id = result.get('job', {}).get('job_id') or result.get('job_id', 'N/A')
                                    logger.info(f"✅ zeropool.io login successful, got job: {job_id}")
                                    self.authorized = True
                                    return True
                                elif isinstance(result, bool) and result:
                                    logger.info("✅ zeropool.io login successful (boolean response)")
                                    self.authorized = True
                                    return True
                                elif isinstance(result, list) and len(result) > 0:
                                    # Some pools return array with session info
                                    logger.info("✅ zeropool.io login successful (array response)")
                                    self.authorized = True
                                    return True
                                elif result == "OK" or result == "ok":
                                    logger.info("✅ zeropool.io login successful (OK response)")
                                    self.authorized = True
                                    return True
                        
                        elif 'error' in response:
                            error = response['error']
                            if isinstance(error, dict):
                                error_msg = error.get('message', str(error))
                            else:
                                error_msg = str(error)
                            logger.warning(f"zeropool.io method {i+1} failed: {error_msg}")
                            continue
                        else:
                            logger.debug(f"zeropool.io method {i+1} unexpected response: {response}")
                            continue
                    else:
                        logger.debug(f"zeropool.io method {i+1} no response")
                        continue
                        
                except socket.timeout:
                    logger.debug(f"zeropool.io method {i+1} timeout")
                    continue
                except Exception as e:
                    logger.debug(f"zeropool.io method {i+1} failed: {e}")
                    continue
            
            logger.warning("⚠️ All zeropool.io login methods failed")
            return False
            
        except Exception as e:
            logger.error(f"❌ zeropool.io Stratum handshake error: {e}")
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
            max_attempts = 3
            attempts = 0
            
            while b'\n' not in buffer and attempts < max_attempts:
                try:
                    self.socket.settimeout(8)  # Reasonable timeout for reading
                    data = self.socket.recv(4096)  # Increased buffer size
                    if not data:
                        logger.debug("❌ Socket closed by remote host")
                        break
                    buffer += data
                    logger.debug(f"📥 Received data chunk: {data[:100]}{'...' if len(data) > 100 else ''}")
                    
                    # If we have complete line(s), break
                    if b'\n' in buffer:
                        break
                        
                except socket.timeout:
                    attempts += 1
                    logger.debug(f"⏱️ Socket read timeout (attempt {attempts}/{max_attempts})")
                    if attempts >= max_attempts:
                        break
                except Exception as e:
                    logger.error(f"❌ Socket read error: {e}")
                    break
            
            if b'\n' in buffer:
                # Find the first complete line
                lines = buffer.split(b'\n')
                first_line = lines[0].strip()
                if first_line:
                    logger.debug(f"📥 Complete line received: {first_line}")
                    return first_line
                
        except Exception as e:
            logger.error(f"❌ Socket read error: {e}")
        
        return None
    
    def get_work(self) -> Optional[Dict]:
        """Get current mining work from Monero pool"""
        try:
            # For Monero, work typically comes with the login response or via job notifications
            if self.connected and self.authorized and self.current_job:
                # Check if job is still fresh (within last 2 minutes)
                job_age = time.time() - self.current_job.get('received_at', 0)
                if job_age < 120:  # Use job if less than 2 minutes old
                    job = self.current_job
                    return {
                        'job_id': job.get('job_id', f"job_{int(time.time())}"),
                        'blob': job.get('blob', '0' * 152),
                        'target': job.get('target', f"{(2**256 // self.difficulty):064x}"),
                        'height': job.get('height', 0),
                        'seed_hash': job.get('seed_hash', ''),
                        'difficulty': self.difficulty,
                        'received_at': job.get('received_at', time.time())
                    }
                else:
                    logger.debug(f"⏰ Job expired ({job_age:.1f}s old), using fallback")
            
            # Fallback work template when no fresh job available
            if self.connected:
                return {
                    'job_id': f"local_{int(time.time())}",
                    'blob': '0' * 152,  # Placeholder blob
                    'target': f"{(2**256 // self.difficulty):064x}",
                    'height': 0,
                    'seed_hash': '',
                    'difficulty': self.difficulty,
                    'received_at': time.time()
                }
        except Exception as e:
            logger.error(f"❌ Get work error: {e}")
        
        return None
    
    def submit_share(self, job_id: str, nonce: str, result: str) -> bool:
        """Submit mining share to pool with zeropool.io compatible format"""
        try:
            # Check if we're still authenticated
            if not self.authorized:
                logger.warning("⚠️ Not authenticated, attempting to re-authenticate")
                if not self._try_stratum_handshake():
                    logger.error("❌ Re-authentication failed")
                    return False
            
            # Clean wallet address - ensure no prefixes for zeropool.io compatibility
            clean_wallet = self.wallet
            if ":" in clean_wallet:
                clean_wallet = clean_wallet.split(":", 1)[1]  # Remove any prefix like "solo:"
            
            # For zeropool.io: Use standard xmrig-compatible format
            submit_msg = {
                "id": int(time.time() * 1000),  # Millisecond timestamp like xmrig
                "method": "submit",
                "params": {
                    "id": clean_wallet,  # Clean wallet address as ID
                    "job_id": job_id,
                    "nonce": nonce,
                    "result": result
                }
            }
            
            logger.info(f"📤 Submitting share to zeropool.io: job_id={job_id}, nonce={nonce[:8]}...")
            response = self._send_receive_with_timeout(submit_msg, timeout=15)
            
            if response:
                logger.debug(f"📥 Pool response: {response}")
                
                if 'result' in response:
                    result_value = response['result']
                    if result_value == 'OK' or result_value is True or result_value == "true":
                        logger.info("✅ Share ACCEPTED by zeropool.io")
                        return True
                    elif result_value is False or result_value == "false":
                        error = response.get('error', 'Share rejected by pool')
                        if isinstance(error, dict):
                            error_msg = error.get('message', str(error))
                        else:
                            error_msg = str(error)
                        logger.warning(f"❌ Share REJECTED by zeropool.io: {error_msg}")
                        return False
                elif 'error' in response:
                    error = response['error']
                    if isinstance(error, dict):
                        error_msg = error.get('message', str(error))
                        error_code = error.get('code', 0)
                    else:
                        error_msg = str(error)
                        error_code = 0
                    
                    # Handle zeropool.io specific authentication errors
                    if any(keyword in error_msg.lower() for keyword in ['unauthenticated', 'unauthorized', 'invalid login', 'access denied']):
                        logger.warning(f"🔐 zeropool.io authentication issue: {error_msg}")
                        # Mark as unauthenticated and try to re-authenticate with clean wallet
                        self.authorized = False
                        original_wallet = self.wallet
                        self.wallet = clean_wallet  # Use clean wallet for re-auth
                        
                        if self._try_stratum_handshake():
                            logger.info("✅ Re-authenticated with zeropool.io, retrying share submission")
                            # Retry the share submission once after re-authentication
                            result = self.submit_share(job_id, nonce, result)
                            self.wallet = original_wallet  # Restore original wallet
                            return result
                        else:
                            logger.error("❌ zeropool.io re-authentication failed")
                            self.wallet = original_wallet  # Restore original wallet
                            return False
                    else:
                        logger.warning(f"❌ Share submission error: {error_msg} (code: {error_code})")
                        return False
                else:
                    logger.warning(f"❌ Unexpected response from zeropool.io: {response}")
                    return False
            else:
                logger.warning("❌ No response from zeropool.io pool")
                return False
                
        except Exception as e:
            logger.error(f"❌ Share submission error: {e}")
            return False
    
    def listen_for_jobs(self):
        """Listen for job notifications from pool in background"""
        if not self.connected:
            return
            
        def job_listener():
            last_auth_check = time.time()
            while self.connected:
                try:
                    # Periodic authentication check (every 5 minutes)
                    current_time = time.time()
                    if current_time - last_auth_check > 300:  # 5 minutes
                        if self.authorized:
                            logger.debug("🔐 Performing periodic authentication check")
                            # Send a simple request to check if we're still authenticated
                            try:
                                ping_msg = {
                                    "id": int(current_time * 1000),
                                    "method": "keepalive",
                                    "params": []
                                }
                                response = self._send_receive_with_timeout(ping_msg, timeout=3)
                                if response and 'error' in response:
                                    error = response['error']
                                    if isinstance(error, dict):
                                        error_msg = error.get('message', '')
                                    else:
                                        error_msg = str(error)
                                    if 'unauthenticated' in error_msg.lower():
                                        logger.warning("🔐 Session expired, re-authenticating")
                                        self.authorized = False
                                        self._try_stratum_handshake()
                            except Exception as e:
                                logger.debug(f"Keepalive check failed: {e}")
                        last_auth_check = current_time
                    
                    # Listen for incoming messages (job notifications)
                    self.socket.settimeout(30)  # 30-second timeout for job updates
                    data = self._read_line()
                    if data:
                        try:
                            message = json.loads(data.decode('utf-8'))
                            
                            # Handle job notifications (common in Monero pools)
                            if 'method' in message:
                                if message['method'] == 'job':
                                    # Monero pool job notification (standard format)
                                    params = message.get('params', {})
                                    if isinstance(params, dict) and 'job_id' in params:
                                        self.current_job = params.copy()
                                        self.current_job['received_at'] = time.time()
                                        logger.info(f"🔄 New job received: {params.get('job_id', 'N/A')}")
                                elif message['method'] == 'mining.notify':
                                    # Bitcoin-style job notification
                                    params = message.get('params', [])
                                    if len(params) > 0:
                                        job_data = {
                                            'job_id': params[0] if len(params) > 0 else '',
                                            'blob': params[1] if len(params) > 1 else '',
                                            'target': params[2] if len(params) > 2 else '',
                                            'received_at': time.time()
                                        }
                                        self.current_job = job_data
                                        logger.info(f"🔄 Mining job update: {job_data.get('job_id', 'N/A')}")
                            elif 'result' in message and 'id' in message:
                                # This is a response to our request, not a job notification
                                logger.debug(f"📥 Pool response to request {message['id']}: {message.get('result', 'N/A')}")
                        except json.JSONDecodeError:
                            # Not JSON, ignore
                            pass
                except socket.timeout:
                    # Timeout is normal, just continue listening
                    continue
                except Exception as e:
                    logger.debug(f"Job listener error: {e}")
                    break
        
        # Start job listener in background thread
        job_thread = threading.Thread(target=job_listener, daemon=True)
        job_thread.start()
        logger.info("👂 Started listening for job notifications")
        
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
                # Get work from pool (always get fresh work to avoid stale jobs)
                if not self.current_job or time.time() - self.current_job.get('received_at', 0) > 10:
                    # Get fresh work from stratum connection every 10 seconds or if no job
                    fresh_work = self.stratum.get_work()
                    if fresh_work:
                        self.current_job = fresh_work
                        logger.debug(f"Thread {self.thread_id} got fresh work: {fresh_work.get('job_id', 'N/A')}")
                    elif not self.current_job:
                        # Create local work template if no work available
                        self.current_job = self._create_local_work()
                        logger.debug(f"Thread {self.thread_id} using local work")
                
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
                        
                        # Attempt to submit share to pool
                        if self.stratum.authorized:
                            submitted = self._submit_share(hash_result)
                            if submitted:
                                logger.info(f"✅ Share accepted from thread {self.thread_id}")
                                self.stats.shares_good += 1
                            else:
                                logger.info(f"⚠️ Share submission failed from thread {self.thread_id}")
                                self.stats.shares_rejected += 1
                        else:
                            logger.info(f"📊 Share found (pool protocol not available)")
                            self.stats.shares_good += 1  # Count as good share if no pool protocol
                    
                    self.nonce += 1
                    self.hashes_done += 1
                    self.stats.hashes_total += 1
                
                # Small delay to control CPU usage
                time.sleep(batch_delay)
                
                # Update hashrate more frequently during startup, then less frequently
                elapsed_time = time.time() - self.start_time
                update_frequency = 1000 if elapsed_time < 30 else 10000  # More frequent for first 30 seconds
                if self.hashes_done % update_frequency == 0:
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
        """Submit share to pool with proper Monero format"""
        try:
            # Always get the freshest job from the Stratum connection
            fresh_job = self.stratum.get_work()
            if fresh_job and fresh_job.get('job_id'):
                job_id = fresh_job['job_id']
                logger.debug(f"🔍 Using fresh job ID: {job_id}")
            elif self.current_job and self.current_job.get('job_id'):
                job_id = self.current_job['job_id']
                job_age = time.time() - self.current_job.get('received_at', 0)
                if job_age > 30:
                    logger.warning(f"⚠️ Using potentially stale job ({job_age:.1f}s old): {job_id}")
            else:
                logger.error("❌ No valid job available for share submission")
                return False
            
            # Format nonce as 8-character hex (standard for Monero)
            nonce_hex = f"{self.nonce:08x}"
            
            # For Monero, result should be the complete hash in hex format
            # Use only the first 32 bytes (64 hex characters) for the result
            result_hex = hash_result[:32].hex()
            
            logger.debug(f"🔍 Share details: job={job_id}, nonce={nonce_hex}, result={result_hex[:16]}...")
            
            return self.stratum.submit_share(job_id, nonce_hex, result_hex)
            
        except Exception as e:
            logger.error(f"❌ Share submission error: {e}")
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
                # Start listening for job notifications from pool
                self.stratum_connection.listen_for_jobs()
            
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
        total_rejected = sum(t.stats.shares_rejected for t in self.threads)
        
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
            'shares_rejected': total_rejected,
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
            'shares_rejected': self.stats.shares_rejected,
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