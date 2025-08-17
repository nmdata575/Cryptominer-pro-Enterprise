"""
CryptoMiner Enterprise V30 - Real Scrypt Mining Implementation
Based on cgminer and real mining pool protocols (Stratum)
"""

import hashlib
import struct
import socket
import json
import time
import threading
import asyncio
import base64
import binascii
import scrypt  # High-performance scrypt library
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)

# Remove the old slow ScryptAlgorithm class - replaced with optimized scrypt library

class StratumClient:
    """Stratum mining protocol client for real pool communication"""
    
    def __init__(self):
        self.socket = None
        self.connected = False
        self.job_id = None
        self.extranonce1 = None
        self.extranonce2_size = 0
        self.difficulty = 1
        self.target = None
        self.message_id = 1
        self.username = None  # Store username for share submission
        self.password = None  # Store password for share submission
        
    async def connect_to_pool(self, host: str, port: int, username: str, password: str = "x") -> bool:
        """Connect to mining pool using Stratum protocol"""
        try:
            # Store credentials for later use and parse difficulty from password
            self.username = username
            self.password = password
            
            # Parse difficulty from password if specified (e.g., "d=1024" or just "1024")
            requested_difficulty = None
            auth_password = password  # Keep original for authorization
            
            if password and password != "x":
                # Check for d=NUMBER format
                if password.startswith("d="):
                    try:
                        requested_difficulty = float(password[2:])
                        # Validate difficulty range based on pool limits (ltc.millpools.cc observed limits)
                        if requested_difficulty <= 2400:
                            logger.warning(f"⚠️ Difficulty {requested_difficulty} is in problematic range (≤2400)")
                            logger.warning(f"   Pool may revert to difficulty 1. Consider using > 2400")
                        elif requested_difficulty > 750000:
                            logger.warning(f"⚠️ Difficulty {requested_difficulty} exceeds pool limits (>750000)")
                            logger.warning(f"   Pool may reject connection. Consider using ≤ 750000")
                            requested_difficulty = 750000  # Cap at pool maximum
                            logger.info(f"   Capped difficulty to pool maximum: {requested_difficulty}")
                            
                        auth_password = "x"  # Use standard password for auth
                        logger.info(f"Difficulty requested in password: {requested_difficulty}")
                    except ValueError:
                        logger.error(f"Invalid difficulty format in password: {password}")
                        pass
                # Check if password is just a number
                elif password.replace(".", "").isdigit():
                    try:
                        requested_difficulty = float(password)
                        # Validate difficulty range based on pool limits
                        if requested_difficulty <= 2400:
                            logger.warning(f"⚠️ Difficulty {requested_difficulty} is in problematic range (≤2400)")
                            logger.warning(f"   Pool may revert to difficulty 1. Consider using > 2400")
                        elif requested_difficulty > 750000:
                            logger.warning(f"⚠️ Difficulty {requested_difficulty} exceeds pool limits (>750000)")
                            logger.warning(f"   Pool may reject connection. Consider using ≤ 750000")
                            requested_difficulty = 750000  # Cap at pool maximum
                            logger.info(f"   Capped difficulty to pool maximum: {requested_difficulty}")
                            
                        auth_password = "x"  # Use standard password for auth 
                        logger.info(f"Difficulty requested as password: {requested_difficulty}")
                    except ValueError:
                        logger.error(f"Invalid difficulty value in password: {password}")
                        pass
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(60)  # Reduced to 60 seconds for better pool compatibility
            self.socket.connect((host, port))
            
            # Send mining.subscribe
            subscribe_msg = {
                "id": self.message_id,
                "method": "mining.subscribe",
                "params": ["CryptoMiner-V30/1.0", None]
            }
            self._send_message(subscribe_msg)
            response = self._receive_message()
            
            if response and 'result' in response:
                result = response['result']
                self.extranonce1 = result[1]
                self.extranonce2_size = result[2]
                logger.info(f"Subscribed to pool: extranonce1={self.extranonce1}")
                
                # Request lower difficulty for CPU mining (try multiple methods)
                try:
                    self.message_id += 1
                    
                    # Method 1: Use requested difficulty from password, or default to 16
                    target_difficulty = requested_difficulty if requested_difficulty else 16
                    
                    # Log the difficulty request attempt
                    logger.info(f"Attempting to request difficulty: {target_difficulty}")
                    
                    suggest_diff_msg = {
                        "id": self.message_id,
                        "method": "mining.suggest_difficulty",
                        "params": [target_difficulty]
                    }
                    self._send_message(suggest_diff_msg)
                    logger.info(f"Sent mining.suggest_difficulty: {target_difficulty}")
                    
                    # Method 2: Also try mining.suggest_target (some pools prefer this)
                    self.message_id += 1
                    try:
                        target_hex = hex(int(0x00000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF / target_difficulty))
                        suggest_target_msg = {
                            "id": self.message_id, 
                            "method": "mining.suggest_target",
                            "params": [target_hex]
                        }
                        self._send_message(suggest_target_msg)
                        logger.info(f"Sent mining.suggest_target for difficulty {target_difficulty}")
                    except Exception as target_error:
                        logger.debug(f"Could not send suggest_target: {target_error}")
                    
                except Exception as e:
                    logger.warning(f"Pool may not support difficulty suggestion: {e}")
            
            # Send mining.authorize
            self.message_id += 1
            authorize_msg = {
                "id": self.message_id,
                "method": "mining.authorize",
                "params": [username, auth_password]
            }
            self._send_message(authorize_msg)
            
            # Wait for authorization response (may receive difficulty updates first)
            auth_success = False
            max_attempts = 15  # Balanced approach for higher difficulties
            for attempt in range(max_attempts):
                response = self._receive_message(timeout=5.0)  # 5 second timeout per message
                if not response:
                    logger.debug(f"Authorization attempt {attempt + 1}/{max_attempts}: No response")
                    continue
                
                # Handle mining.set_difficulty messages that come before auth response
                if response.get('method') == 'mining.set_difficulty':
                    new_difficulty = response['params'][0]
                    old_difficulty = self.difficulty
                    self.difficulty = new_difficulty
                    self.target = self._difficulty_to_target(self.difficulty)
                    logger.info(f"🎯 Pool difficulty updated during auth: {old_difficulty} → {self.difficulty}")
                    
                    # Check if this matches our requested difficulty
                    if requested_difficulty and abs(self.difficulty - requested_difficulty) < 0.1:
                        logger.info(f"✅ Pool accepted requested difficulty: {requested_difficulty}")
                    elif requested_difficulty:
                        logger.warning(f"⚠️ Pool set difficulty {self.difficulty} instead of requested {requested_difficulty}")
                    
                    logger.info(f"🎯 New target: {hex(int.from_bytes(self.target[:8], 'little'))[:18]}...")
                    continue
                
                # Handle authorization response
                if response.get('id') == self.message_id and response.get('result') == True:
                    auth_success = True
                    logger.info(f"✅ Authorization successful on attempt {attempt + 1}")
                    break
                elif response.get('id') == self.message_id:
                    logger.error(f"❌ Authorization failed on attempt {attempt + 1}: {response}")
                    break
                else:
                    logger.debug(f"Received other message during auth: {response.get('method', 'unknown')}")
            
            if auth_success:
                self.connected = True
                # Initialize target if not already set by difficulty message
                if not self.target:
                    self.target = self._difficulty_to_target(self.difficulty)
                logger.info(f"✅ Authorized with pool as {username}")
                logger.info(f"🎯 Final difficulty: {self.difficulty}")
                logger.info(f"🎯 Final target: {hex(int.from_bytes(self.target[:8], 'little'))[:18]}...")
                return True
            else:
                logger.error(f"❌ Authorization timeout after {max_attempts} attempts ({max_attempts * 5}s)")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to pool {host}:{port} - {e}")
            return False
    
    def _send_message(self, message: Dict):
        """Send JSON message to pool"""
        msg_json = json.dumps(message) + '\n'
        self.socket.send(msg_json.encode('utf-8'))
        logger.debug(f"Sent: {message}")
    
    def _receive_message(self, timeout: float = 5.0) -> Optional[Dict]:
        """Receive JSON message from pool with timeout"""
        try:
            import select
            ready = select.select([self.socket], [], [], timeout)
            if ready[0]:
                data = self.socket.recv(4096).decode('utf-8').strip()
                if data:
                    # Handle multiple JSON messages in one response (common in Stratum)
                    lines = data.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line:
                            try:
                                message = json.loads(line)
                                logger.debug(f"Received: {message}")
                                return message
                            except json.JSONDecodeError:
                                continue
            else:
                logger.debug("No message received within timeout")
        except Exception as e:
            logger.error(f"Failed to receive message: {e}")
        return None
    
    def get_work(self) -> Optional[Dict]:
        """Wait for and parse mining.notify work from pool"""
        try:
            while True:
                message = self._receive_message()
                if not message:
                    continue
                
                if message.get('method') == 'mining.notify':
                    params = message['params']
                    work = {
                        'job_id': params[0],
                        'prev_hash': params[1],
                        'coinbase1': params[2],
                        'coinbase2': params[3],
                        'merkle_branches': params[4],
                        'version': params[5],
                        'nbits': params[6],
                        'ntime': params[7],
                        'clean_jobs': params[8]
                    }
                    self.job_id = work['job_id']
                    logger.info(f"New work received: job_id={self.job_id}, nbits={work['nbits']}")
                    return work
                
                elif message.get('method') == 'mining.set_difficulty':
                    # Handle pool difficulty updates during mining
                    new_difficulty = message['params'][0]
                    old_difficulty = self.difficulty
                    self.difficulty = new_difficulty
                    self.target = self._difficulty_to_target(self.difficulty)
                    logger.info(f"🎯 DIFFICULTY UPDATED DURING MINING: {old_difficulty} → {self.difficulty}")
                    logger.info(f"🎯 New target: {hex(int.from_bytes(self.target[:8], 'little'))[:18]}...")
                    
                    # Continue to get work after difficulty update
                    continue
                
        except Exception as e:
            logger.error(f"Failed to get work: {e}")
            return None
    
    def submit_share(self, job_id: str, extranonce2: str, ntime: str, nonce: str) -> bool:
        """Submit mining share to pool"""
        try:
            self.message_id += 1
            submit_msg = {
                "id": self.message_id,
                "method": "mining.submit",
                "params": [
                    self.username,  # Use stored username instead of hardcoded "worker1"
                    job_id,
                    extranonce2,
                    ntime, 
                    nonce
                ]
            }
            
            self._send_message(submit_msg)
            response = self._receive_message()
            
            if response and response.get('result') == True:
                logger.info(f"✅ Share accepted! Job: {job_id}, Nonce: {nonce}")
                return True
            else:
                error = response.get('error', 'Unknown error') if response else 'No response'
                logger.warning(f"❌ Share rejected: {error}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to submit share: {e}")
            return False
    
    def _difficulty_to_target(self, difficulty: float) -> bytes:
        """Convert pool difficulty to target hash using proper pool difficulty calculation
        
        Based on Bitcoin Wiki: https://en.bitcoin.it/wiki/Difficulty
        Pool mining uses pdiff (pool difficulty) with full target, not bdiff (Bitcoin difficulty)
        """
        if difficulty <= 0:
            difficulty = 1  # Fallback to minimum difficulty
        
        # Pool difficulty 1 target (pdiff) - CORRECTED: Full 256-bit value
        # This is the correct pool max target with proper leading zeros  
        pool_max_target = 0x00000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
        
        # Calculate target: target = max_target / difficulty  
        target_int = int(pool_max_target / difficulty)
        
        # Convert to 32-byte target in little-endian format for hash comparison
        target_bytes = target_int.to_bytes(32, byteorder='little')
        
        logger.info(f"Difficulty: {difficulty}")
        logger.info(f"Pool max target (256-bit): 0x{pool_max_target:064x}")
        logger.info(f"Calculated target (256-bit): 0x{target_int:064x}")
        logger.debug(f"Target bytes (LE): {target_bytes.hex()[:32]}...")
        
        return target_bytes

class RealScryptMiner:
    """Real scrypt miner compatible with cgminer and mining pools"""
    
    def __init__(self):
        self.stratum_client = StratumClient()
        self.is_mining = False
        self.shares_found = 0
        self.shares_accepted = 0
        self.hash_count = 0
        self.thread_count = 1
        self.mining_threads = []
        
    def set_thread_count(self, threads: int):
        """Set the number of mining threads"""
        self.thread_count = max(1, threads)
        logger.info(f"🧵 Set thread count to: {self.thread_count}")
        
    def create_block_header(self, work: Dict, extranonce2: str, ntime: str, nonce: int) -> bytes:
        """Create proper block header for scrypt hashing"""
        try:
            # Build coinbase transaction
            extranonce = self.stratum_client.extranonce1 + extranonce2
            coinbase = work['coinbase1'] + extranonce + work['coinbase2']
            
            # Calculate merkle root
            merkle_root = self._calculate_merkle_root(coinbase, work['merkle_branches'])
            
            # Build block header (80 bytes)
            header = (
                binascii.unhexlify(work['version'])[::-1] +  # version (4 bytes, little-endian)
                binascii.unhexlify(work['prev_hash'])[::-1] + # prev block hash (32 bytes, little-endian) 
                merkle_root[::-1] +                          # merkle root (32 bytes, little-endian)
                struct.pack('<I', int(ntime, 16)) +          # timestamp (4 bytes, little-endian)
                binascii.unhexlify(work['nbits'])[::-1] +    # bits (4 bytes, little-endian)
                struct.pack('<I', nonce)                     # nonce (4 bytes, little-endian)
            )
            
            return header
            
        except Exception as e:
            logger.error(f"Failed to create block header: {e}")
            return b'\x00' * 80
    
    def _calculate_merkle_root(self, coinbase: str, merkle_branches: List[str]) -> bytes:
        """Calculate merkle root from coinbase and merkle branches"""
        # Hash coinbase transaction (double SHA256)
        coinbase_bytes = binascii.unhexlify(coinbase)
        current_hash = hashlib.sha256(hashlib.sha256(coinbase_bytes).digest()).digest()
        
        # Apply merkle branches
        for branch in merkle_branches:
            branch_bytes = binascii.unhexlify(branch)
            combined = current_hash + branch_bytes
            current_hash = hashlib.sha256(hashlib.sha256(combined).digest()).digest()
        
        return current_hash
    
    def mine_work_threaded(self, work: Dict, thread_id: int, start_nonce: int, nonce_range: int) -> Optional[Dict]:
        """Mine work in a specific thread with nonce range"""
        logger.info(f"🧵 Thread {thread_id} starting: nonces {start_nonce:,} to {start_nonce + nonce_range:,}")
        
        # Generate extranonce2 for this thread
        extranonce2 = f"{thread_id:0{self.stratum_client.extranonce2_size * 2}x}"[-self.stratum_client.extranonce2_size * 2:]
        ntime = work['ntime']
        
        for nonce_offset in range(nonce_range):
            if not self.is_mining:  # Check if mining should continue
                logger.info(f"🛑 Thread {thread_id} stopping due to mining halt")
                break
                
            nonce = start_nonce + nonce_offset
            
            try:
                # Create block header
                logger.debug(f"Thread {thread_id}: Creating block header for nonce {nonce}")
                header = self.create_block_header(work, extranonce2, ntime, nonce)
                logger.debug(f"Thread {thread_id}: Block header created, length: {len(header)} bytes")
                
                # Apply scrypt hash - OPTIMIZED: Use high-performance scrypt library 
                logger.debug(f"Thread {thread_id}: Starting scrypt hash computation...")
                scrypt_hash = scrypt.hash(
                    password=header,
                    salt=header,
                    N=1024,  # Litecoin scrypt-N parameter
                    r=1,     # Litecoin scrypt-r parameter  
                    p=1,     # Litecoin scrypt-p parameter
                    buflen=32
                )
                logger.debug(f"Thread {thread_id}: Scrypt hash computed: {scrypt_hash.hex()[:16]}...")
                
                # Check if hash meets difficulty - FIXED: Use proper comparison
                # Convert hash to integer for comparison (little-endian)
                hash_int = int.from_bytes(scrypt_hash, byteorder='little')
                target_int = int.from_bytes(self.stratum_client.target, byteorder='little') if self.stratum_client.target else 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
                
                self.hash_count += 1
                
                # Log progress every 10000 hashes
                if nonce % 10000 == 0:
                    logger.info(f"⛏️  Thread {thread_id} progress: {nonce:,} hashes, difficulty: {self.stratum_client.difficulty}")
                    logger.debug(f"Thread {thread_id}: Current hash count: {self.hash_count}")
                
                # Check if we found a valid share - FIXED: Proper difficulty comparison
                if hash_int < target_int:
                    logger.info(f"🎯 SHARE FOUND by Thread {thread_id}! Nonce: {nonce}")
                    logger.info(f"   Hash: {scrypt_hash.hex()}")
                    logger.info(f"   Hash int: {hash_int}")
                    logger.info(f"   Target int: {target_int}")
                    logger.info(f"   Difficulty: {self.stratum_client.difficulty}")
                    
                    # Submit share to pool - only if connection is still active
                    if self.is_mining and self.stratum_client.socket:
                        nonce_hex = f"{nonce:08x}"
                        try:
                            success = self.stratum_client.submit_share(
                                work['job_id'],
                                extranonce2,
                                ntime,
                                nonce_hex
                            )
                            
                            self.shares_found += 1
                            if success:
                                self.shares_accepted += 1
                                logger.info(f"✅ Share accepted by pool!")
                            else:
                                logger.warning(f"❌ Share rejected by pool")
                        except Exception as submit_error:
                            logger.error(f"Share submission failed: {submit_error}")
                            # Don't break, just log and continue
                    else:
                        logger.warning(f"⚠️ Share found but pool connection lost - Thread {thread_id}")
                        self.shares_found += 1
                    
                    return {
                        'job_id': work['job_id'],
                        'nonce': nonce_hex if 'nonce_hex' in locals() else f"{nonce:08x}",
                        'hash': scrypt_hash.hex(),
                        'accepted': False,  # Will be updated by share submission
                        'thread_id': thread_id
                    }
                    
            except Exception as e:
                logger.error(f"Thread {thread_id} mining error at nonce {nonce}: {e}")
                logger.error(f"Thread {thread_id} exception details: {type(e).__name__}: {str(e)}")
                import traceback
                logger.error(f"Thread {thread_id} traceback: {traceback.format_exc()}")
                continue
        
        logger.info(f"🏁 Thread {thread_id} completed nonce range {start_nonce:,} to {start_nonce + nonce_range:,}")
        return None
    
    async def start_mining(self, pool_host: str, pool_port: int, username: str, password: str = "x"):
        """Start real scrypt mining with pool connection using multiple threads"""
        try:
            logger.info(f"🌐 Connecting to pool {pool_host}:{pool_port}")
            
            # Connect to pool
            if not await self.stratum_client.connect_to_pool(pool_host, pool_port, username, password):
                logger.error("❌ Failed to connect to mining pool")
                return False
            
            self.is_mining = True
            logger.info(f"✅ Connected to pool, starting scrypt mining with {self.thread_count} threads...")
            
            # Mining loop
            while self.is_mining:
                # Get work from pool
                work = self.stratum_client.get_work()
                if not work:
                    logger.warning("⚠️  No work received from pool")
                    await asyncio.sleep(1)
                    continue
                
                # Calculate nonce ranges for each thread
                max_nonce = 0x100000  # 1M nonces per work cycle
                nonce_range_per_thread = max_nonce // self.thread_count
                
                # Clear previous threads
                self.mining_threads.clear()
                
                # Start mining threads
                for thread_id in range(self.thread_count):
                    start_nonce = thread_id * nonce_range_per_thread
                    if thread_id == self.thread_count - 1:  # Last thread gets remainder
                        nonce_range = max_nonce - start_nonce
                    else:
                        nonce_range = nonce_range_per_thread
                    
                    # Start thread
                    mining_thread = threading.Thread(
                        target=self._mine_work_wrapper,
                        args=(work, thread_id, start_nonce, nonce_range),
                        daemon=True,
                        name=f"mining_thread_{thread_id}"
                    )
                    mining_thread.start()
                    self.mining_threads.append(mining_thread)
                
                # Wait for all threads to complete or find a share
                start_time = time.time()
                timeout = 30  # 30 second timeout per work
                
                while time.time() - start_time < timeout and self.is_mining:
                    # Check if any threads are still alive
                    alive_threads = [t for t in self.mining_threads if t.is_alive()]
                    if not alive_threads:
                        break
                    await asyncio.sleep(0.1)
                
                # Stop all threads for next work cycle
                for thread in self.mining_threads:
                    if thread.is_alive():
                        # Threads will stop when work changes or is_mining becomes False
                        pass
                
                logger.info(f"📊 Mining stats: {self.shares_found} shares found, {self.shares_accepted} accepted")
            
            logger.info("🛑 Mining stopped")
            return True
            
        except Exception as e:
            logger.error(f"❌ Mining failed: {e}")
            # Make sure to stop all mining threads
            self.is_mining = False
            return False
        finally:
            # Ensure clean shutdown
            self.is_mining = False
            
            # Wait for all threads to finish
            for thread in self.mining_threads:
                if thread.is_alive():
                    logger.info(f"⏳ Waiting for thread {thread.name} to finish...")
                    thread.join(timeout=5)
            
            # Close socket connection
            if self.stratum_client.socket:
                try:
                    self.stratum_client.socket.close()
                    logger.info("🔌 Pool connection closed")
                except:
                    pass
    
    def _mine_work_wrapper(self, work: Dict, thread_id: int, start_nonce: int, nonce_range: int):
        """Wrapper for mine_work_threaded to handle threading"""
        try:
            result = self.mine_work_threaded(work, thread_id, start_nonce, nonce_range)
            if result:
                logger.info(f"🎯 Thread {thread_id} found share!")
        except Exception as e:
            logger.error(f"Thread {thread_id} error: {e}")
    
    def stop_mining(self):
        """Stop mining and all threads"""
        logger.info("🛑 Stopping scrypt mining...")
        self.is_mining = False
        
        # Wait for all mining threads to finish
        for thread in self.mining_threads:
            if thread.is_alive():
                logger.info(f"⏳ Waiting for mining thread {thread.name}...")
                thread.join(timeout=3)
        
        self.mining_threads.clear()
        
        # Close socket if still open
        if hasattr(self.stratum_client, 'socket') and self.stratum_client.socket:
            try:
                self.stratum_client.socket.close()
            except:
                pass
                
        logger.info("🏁 All mining threads stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get mining statistics"""
        active_threads = len([t for t in self.mining_threads if t.is_alive()])
        return {
            "is_mining": self.is_mining,
            "hash_count": self.hash_count,
            "shares_found": self.shares_found,
            "shares_accepted": self.shares_accepted,
            "acceptance_rate": (self.shares_accepted / self.shares_found * 100) if self.shares_found > 0 else 0,
            "hashrate": self.hash_count / 60 if self.hash_count > 0 else 0,  # Rough estimate
            "active_threads": active_threads,
            "total_threads": self.thread_count
        }

# Test the real scrypt miner
if __name__ == "__main__":
    import asyncio
    
    async def test_real_mining():
        print("🧪 Testing Real Scrypt Mining Implementation")
        
        miner = RealScryptMiner()
        
        # Test with a real Litecoin pool (replace with actual pool details)
        pool_host = "ltc.pool.example.com"  # Replace with real pool
        pool_port = 3333
        username = "your_litecoin_address.worker1"
        
        print(f"⚠️  To test with real pool, update pool details in the code")
        print(f"   Pool: {pool_host}:{pool_port}")
        print(f"   Username: {username}")
        
        # For now, just test the scrypt algorithm
        print("\n🔍 Testing Scrypt Algorithm with Litecoin parameters:")
        
        test_data = b"test block header data for scrypt mining"
        scrypt_result = scrypt.hash(
            password=test_data,
            salt=test_data,
            N=1024,  # Litecoin parameters
            r=1,
            p=1,
            buflen=32
        )
        
        print(f"✅ Scrypt hash: {scrypt_result.hex()}")
        print(f"✅ Algorithm test completed")
        
        # Uncomment to test with real pool:
        # await miner.start_mining(pool_host, pool_port, username)
    
    asyncio.run(test_real_mining())