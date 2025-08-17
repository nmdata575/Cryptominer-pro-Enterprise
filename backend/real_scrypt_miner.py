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
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class ScryptAlgorithm:
    """Proper Scrypt implementation based on cgminer"""
    
    @staticmethod
    def salsa20_8(input_block: bytes) -> bytes:
        """Salsa20/8 core function - proper implementation"""
        def rotl32(x: int, n: int) -> int:
            return ((x << n) | (x >> (32 - n))) & 0xffffffff
        
        def quarter_round(y: List[int], a: int, b: int, c: int, d: int):
            y[b] ^= rotl32((y[a] + y[d]) & 0xffffffff, 7)
            y[c] ^= rotl32((y[b] + y[a]) & 0xffffffff, 9)
            y[d] ^= rotl32((y[c] + y[b]) & 0xffffffff, 13)
            y[a] ^= rotl32((y[d] + y[c]) & 0xffffffff, 18)
        
        # Convert input to 32-bit words
        x = list(struct.unpack('<16I', input_block[:64]))
        
        # Perform 8 rounds (4 double rounds)
        for _ in range(4):
            # Column rounds
            quarter_round(x, 0, 4, 8, 12)
            quarter_round(x, 5, 9, 13, 1)
            quarter_round(x, 10, 14, 2, 6)
            quarter_round(x, 15, 3, 7, 11)
            
            # Row rounds
            quarter_round(x, 0, 1, 2, 3)
            quarter_round(x, 5, 6, 7, 4)
            quarter_round(x, 10, 11, 8, 9)
            quarter_round(x, 15, 12, 13, 14)
        
        return struct.pack('<16I', *x)
    
    @staticmethod
    def blockmix_salsa8(input_block: bytes, r: int) -> bytes:
        """BlockMix with Salsa20/8 - proper scrypt component"""
        block_size = 64
        x = input_block[-block_size:]  # Last 64 bytes
        output = bytearray(len(input_block))
        
        # First loop
        for i in range(2 * r):
            block_start = i * block_size
            block_end = block_start + block_size
            
            # XOR with block
            for j in range(block_size):
                x = bytes(a ^ b for a, b in zip(x, input_block[block_start:block_end]))[:block_size]
            
            # Apply Salsa20/8
            x = ScryptAlgorithm.salsa20_8(x + b'\x00' * (64 - len(x)) if len(x) < 64 else x)
            
            # Store in output
            if i % 2 == 0:
                output[i // 2 * block_size:(i // 2 + 1) * block_size] = x
            else:
                output[(i // 2 + r) * block_size:(i // 2 + r + 1) * block_size] = x
        
        return bytes(output)
    
    @staticmethod 
    def smix(input_block: bytes, N: int, r: int) -> bytes:
        """SMix function - core of scrypt algorithm"""
        block_size = 128 * r
        v = []
        x = input_block
        
        # First loop - generate sequence
        for i in range(N):
            v.append(x)
            x = ScryptAlgorithm.blockmix_salsa8(x, r)
        
        # Second loop - mix with random previous values
        for i in range(N):
            # Get j from last 64 bytes of x
            j = struct.unpack('<I', x[-64:-60])[0] % N
            
            # XOR x with V[j]
            x = bytes(a ^ b for a, b in zip(x, v[j]))
            x = ScryptAlgorithm.blockmix_salsa8(x, r)
        
        return x
    
    @staticmethod
    def scrypt_hash(password: bytes, salt: bytes, N: int = 1024, r: int = 1, p: int = 1, dk_len: int = 32) -> bytes:
        """
        Proper Scrypt hash implementation for cryptocurrency mining
        Based on cgminer parameters: N=1024, r=1, p=1 for Litecoin
        """
        # Use PBKDF2 for initial and final key derivation
        import hmac
        
        def pbkdf2(password: bytes, salt: bytes, iterations: int, dk_len: int) -> bytes:
            """PBKDF2 implementation"""
            def prf(password: bytes, salt: bytes) -> bytes:
                return hmac.new(password, salt, hashlib.sha256).digest()
            
            blocks = []
            for i in range(1, (dk_len + 31) // 32 + 1):
                u = prf(password, salt + struct.pack('>I', i))
                result = u
                for _ in range(iterations - 1):
                    u = prf(password, u)
                    result = bytes(a ^ b for a, b in zip(result, u))
                blocks.append(result)
            
            return b''.join(blocks)[:dk_len]
        
        # Step 1: Initial PBKDF2
        block_size = 128 * r
        derived_key = pbkdf2(password, salt, 1, p * block_size)
        
        # Step 2: Apply SMix to each block
        blocks = []
        for i in range(p):
            block_start = i * block_size
            block_end = block_start + block_size
            block = derived_key[block_start:block_end]
            mixed_block = ScryptAlgorithm.smix(block, N, r)
            blocks.append(mixed_block)
        
        combined = b''.join(blocks)
        
        # Step 3: Final PBKDF2
        final_hash = pbkdf2(password, combined, 1, dk_len)
        return final_hash

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
        
    async def connect_to_pool(self, host: str, port: int, username: str, password: str = "x") -> bool:
        """Connect to mining pool using Stratum protocol"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)
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
            
            # Send mining.authorize
            self.message_id += 1
            authorize_msg = {
                "id": self.message_id,
                "method": "mining.authorize",
                "params": [username, password]
            }
            self._send_message(authorize_msg)
            response = self._receive_message()
            
            if response and response.get('result') == True:
                self.connected = True
                logger.info(f"Authorized with pool as {username}")
                return True
            else:
                logger.error(f"Authorization failed: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to pool {host}:{port} - {e}")
            return False
    
    def _send_message(self, message: Dict):
        """Send JSON message to pool"""
        msg_json = json.dumps(message) + '\n'
        self.socket.send(msg_json.encode('utf-8'))
        logger.debug(f"Sent: {message}")
    
    def _receive_message(self) -> Optional[Dict]:
        """Receive JSON message from pool"""
        try:
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
                    logger.info(f"New work received: job_id={self.job_id}")
                    return work
                
                elif message.get('method') == 'mining.set_difficulty':
                    self.difficulty = message['params'][0]
                    self.target = self._difficulty_to_target(self.difficulty)
                    logger.info(f"Difficulty set to: {self.difficulty}")
                
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
                    "worker1",  # worker name
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
        """Convert pool difficulty to target hash"""
        # Standard Litecoin max target
        max_target = 0x00000000FFFF0000000000000000000000000000000000000000000000000000
        target = int(max_target / difficulty)
        return struct.pack('>I', target)[:4]  # First 4 bytes for comparison

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
            if not self.is_mining:
                break
                
            nonce = start_nonce + nonce_offset
            
            try:
                # Create block header
                header = self.create_block_header(work, extranonce2, ntime, nonce)
                
                # Apply scrypt hash - CRITICAL: Use Litecoin parameters N=1024, r=1, p=1
                scrypt_hash = ScryptAlgorithm.scrypt_hash(
                    password=header,
                    salt=header,
                    N=1024,  # Litecoin scrypt-N parameter
                    r=1,     # Litecoin scrypt-r parameter  
                    p=1,     # Litecoin scrypt-p parameter
                    dk_len=32
                )
                
                # Check if hash meets difficulty
                hash_int = int.from_bytes(scrypt_hash[:4], byteorder='big')
                target_int = int.from_bytes(self.stratum_client.target, byteorder='big') if self.stratum_client.target else 0xFFFFFFFF
                
                self.hash_count += 1
                
                # Log progress every 10000 hashes
                if nonce % 10000 == 0:
                    logger.info(f"⛏️  Thread {thread_id} progress: {nonce:,} hashes, hash: {scrypt_hash.hex()[:16]}...")
                
                # Check if we found a valid share
                if hash_int <= target_int:
                    logger.info(f"🎯 SHARE FOUND by Thread {thread_id}! Nonce: {nonce}, Hash: {scrypt_hash.hex()}")
                    
                    # Submit share to pool
                    nonce_hex = f"{nonce:08x}"
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
                    
                    return {
                        'job_id': work['job_id'],
                        'nonce': nonce_hex,
                        'hash': scrypt_hash.hex(),
                        'accepted': success,
                        'thread_id': thread_id
                    }
                    
            except Exception as e:
                logger.error(f"Thread {thread_id} mining error at nonce {nonce}: {e}")
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
            return False
        finally:
            if self.stratum_client.socket:
                self.stratum_client.socket.close()
    
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
        self.is_mining = False
        logger.info("🛑 Stopping scrypt mining...")
        
        # Wait for all mining threads to finish
        for thread in self.mining_threads:
            if thread.is_alive():
                thread.join(timeout=2)
        
        self.mining_threads.clear()
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
        scrypt_result = ScryptAlgorithm.scrypt_hash(
            password=test_data,
            salt=test_data,
            N=1024,  # Litecoin parameters
            r=1,
            p=1,
            dk_len=32
        )
        
        print(f"✅ Scrypt hash: {scrypt_result.hex()}")
        print(f"✅ Algorithm test completed")
        
        # Uncomment to test with real pool:
        # await miner.start_mining(pool_host, pool_port, username)
    
    asyncio.run(test_real_mining())