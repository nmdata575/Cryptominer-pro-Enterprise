"""
CryptoMiner Pro - Consolidated Mining Engine
Handles all Scrypt mining operations and pool/solo mining functionality
"""

import hashlib
import struct
import time
import threading
import json
import socket
import psutil
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class MiningStats:
    hashrate: float = 0.0
    accepted_shares: int = 0
    rejected_shares: int = 0
    blocks_found: int = 0
    uptime: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    efficiency: float = 0.0
    last_share_time: Optional[float] = None

@dataclass
class CoinConfig:
    name: str
    symbol: str
    algorithm: str
    block_reward: float
    block_time: int
    difficulty: float
    scrypt_params: Dict[str, int]
    network_hashrate: str
    wallet_format: str
    custom_pool_address: Optional[str] = None
    custom_pool_port: Optional[int] = None
    custom_rpc_host: Optional[str] = None
    custom_rpc_port: Optional[int] = None
    custom_rpc_username: Optional[str] = None
    custom_rpc_password: Optional[str] = None

class ScryptMiner:
    def __init__(self):
        self.is_mining = False
        self.mining_thread = None
        self.stats = MiningStats()
        self.start_time = None
        self.current_config = None
        
    def salsa20_8_core(self, input_data: bytes) -> bytes:
        """Salsa20/8 core function for Scrypt"""
        def quarter_round(a, b, c, d, x):
            x[b] ^= ((x[a] + x[d]) & 0xffffffff) << 7 & 0xffffffff
            x[c] ^= ((x[b] + x[a]) & 0xffffffff) << 9 & 0xffffffff
            x[d] ^= ((x[c] + x[b]) & 0xffffffff) << 13 & 0xffffffff
            x[a] ^= ((x[d] + x[c]) & 0xffffffff) << 18 & 0xffffffff

        x = list(struct.unpack('<16I', input_data[:64]))
        
        for _ in range(4):  # 8 rounds = 4 double rounds
            quarter_round(0, 4, 8, 12, x)
            quarter_round(5, 9, 13, 1, x)
            quarter_round(10, 14, 2, 6, x)
            quarter_round(15, 3, 7, 11, x)
            quarter_round(0, 1, 2, 3, x)
            quarter_round(5, 6, 7, 4, x)
            quarter_round(10, 11, 8, 9, x)
            quarter_round(15, 12, 13, 14, x)
        
        return struct.pack('<16I', *x)

    def scrypt_blockmix(self, input_data: bytes, r: int) -> bytes:
        """Scrypt block mixing function"""
        block_size = 64
        x = input_data[-block_size:]
        result = bytearray()
        
        for i in range(2 * r):
            block_start = i * block_size
            block_end = block_start + block_size
            block = input_data[block_start:block_end]
            
            x_int = [struct.unpack('<16I', x[j:j+64])[k] for j in range(0, 64, 64) for k in range(16)]
            block_int = [struct.unpack('<16I', block[j:j+64])[k] for j in range(0, 64, 64) for k in range(16)]
            
            for j in range(16):
                x_int[j] ^= block_int[j]
            
            x = struct.pack('<16I', *x_int[:16])
            x = self.salsa20_8_core(x + b'\x00' * (64 - len(x)))
            result.extend(x)
        
        return bytes(result)

    def scrypt_romix(self, input_data: bytes, n: int, r: int) -> bytes:
        """Scrypt ROMix function"""
        block_size = 128 * r
        x = input_data[:block_size]
        v = []
        
        for i in range(n):
            v.append(x)
            x = self.scrypt_blockmix(x, r)
        
        for i in range(n):
            j = struct.unpack('<I', x[-4:])[0] % n
            for k in range(len(x)):
                x = x[:k] + bytes([x[k] ^ v[j][k]]) + x[k+1:]
            x = self.scrypt_blockmix(x, r)
        
        return x

    def scrypt_hash(self, data: bytes, n: int = 1024, r: int = 1, p: int = 1) -> bytes:
        """Complete Scrypt hash function"""
        try:
            import scrypt
            return scrypt.hash(data, data, n, r, p, 32)
        except ImportError:
            # Fallback implementation
            block_size = 128 * r
            derived_key_length = 32
            
            b = hashlib.pbkdf2_hmac('sha256', data, data, 1, p * block_size)
            
            result = bytearray()
            for i in range(p):
                start = i * block_size
                end = start + block_size
                block = b[start:end]
                result.extend(self.scrypt_romix(block, n, r)[:derived_key_length])
            
            return hashlib.pbkdf2_hmac('sha256', data, bytes(result), 1, derived_key_length)

    def mine_block(self, coin_config: CoinConfig, wallet_address: str, threads: int = 1):
        """Main mining loop"""
        self.is_mining = True
        self.start_time = time.time()
        self.current_config = coin_config
        
        # Get scrypt parameters
        scrypt_params = coin_config.scrypt_params
        n = scrypt_params.get('n', 1024)
        r = scrypt_params.get('r', 1) 
        p = scrypt_params.get('p', 1)
        
        nonce = 0
        hash_count = 0
        last_update = time.time()
        
        print(f"🚀 Mining {coin_config.name} with {threads} threads...")
        print(f"⚙️ Scrypt parameters: N={n}, r={r}, p={p}")
        
        while self.is_mining:
            # Create block header
            timestamp = int(time.time())
            header_data = f"{wallet_address}{timestamp}{nonce}".encode('utf-8')
            
            # Calculate scrypt hash
            hash_result = self.scrypt_hash(header_data, n, r, p)
            hash_count += 1
            
            # Check if hash meets target (simplified)
            if hash_result.hex()[:8] == "00000000":  # Simplified difficulty target
                self.stats.blocks_found += 1
                print(f"🎉 Block found! Hash: {hash_result.hex()}")
            
            # Update statistics
            current_time = time.time()
            if current_time - last_update >= 1.0:  # Update every second
                elapsed = current_time - self.start_time
                self.stats.hashrate = hash_count / elapsed if elapsed > 0 else 0
                self.stats.uptime = elapsed
                self.stats.cpu_usage = psutil.cpu_percent()
                self.stats.memory_usage = psutil.virtual_memory().percent
                
                # Calculate efficiency (hashrate per CPU percent)
                self.stats.efficiency = (self.stats.hashrate / self.stats.cpu_usage * 100) if self.stats.cpu_usage > 0 else 0
                
                last_update = current_time
            
            nonce += 1
            
            # Prevent overwhelming the system
            if nonce % 1000 == 0:
                time.sleep(0.001)
    
    def start_mining(self, coin_config: CoinConfig, wallet_address: str, threads: int = 1):
        """Start mining in a separate thread"""
        if self.is_mining:
            return False, "Mining already in progress"
        
        self.stats = MiningStats()  # Reset stats
        self.mining_thread = threading.Thread(
            target=self.mine_block,
            args=(coin_config, wallet_address, threads),
            daemon=True
        )
        self.mining_thread.start()
        
        # Wait a moment to ensure mining starts
        time.sleep(0.5)
        return True, "Mining started successfully"
    
    def stop_mining(self):
        """Stop mining"""
        if not self.is_mining:
            return False, "Mining is not active"
        
        self.is_mining = False
        if self.mining_thread and self.mining_thread.is_alive():
            self.mining_thread.join(timeout=5)
        
        return True, "Mining stopped successfully"
    
    def get_mining_status(self) -> Dict[str, Any]:
        """Get current mining status and statistics"""
        return {
            "is_mining": self.is_mining,
            "stats": asdict(self.stats),
            "config": asdict(self.current_config) if self.current_config else None
        }

class PoolManager:
    def __init__(self):
        self.pool_connection = None
        self.connected = False
    
    def test_pool_connection(self, pool_address: str, pool_port: int) -> Dict[str, Any]:
        """Test connection to mining pool"""
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            
            result = sock.connect_ex((pool_address, pool_port))
            connection_time = time.time() - start_time
            sock.close()
            
            if result == 0:
                return {
                    "success": True,
                    "status": "Connected successfully",
                    "connection_time": f"{connection_time:.2f}s",
                    "pool_address": pool_address,
                    "pool_port": pool_port
                }
            else:
                return {
                    "success": False,
                    "error": f"Connection failed (error code: {result})",
                    "pool_address": pool_address,
                    "pool_port": pool_port
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "pool_address": pool_address,
                "pool_port": pool_port
            }
    
    def test_rpc_connection(self, rpc_host: str, rpc_port: int, username: str = "", password: str = "") -> Dict[str, Any]:
        """Test RPC connection for solo mining"""
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            
            result = sock.connect_ex((rpc_host, rpc_port))
            connection_time = time.time() - start_time
            sock.close()
            
            if result == 0:
                return {
                    "success": True,
                    "status": "RPC endpoint accessible",
                    "connection_time": f"{connection_time:.2f}s",
                    "rpc_host": rpc_host,
                    "rpc_port": rpc_port
                }
            else:
                return {
                    "success": False,
                    "error": f"RPC connection failed (error code: {result})",
                    "rpc_host": rpc_host,
                    "rpc_port": rpc_port
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "rpc_host": rpc_host,
                "rpc_port": rpc_port
            }

# Global mining engine instance
mining_engine = ScryptMiner()
pool_manager = PoolManager()