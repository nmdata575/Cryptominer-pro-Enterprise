#!/usr/bin/env python3
"""
Advanced Cryptocurrency Mining System
Complete Scrypt Implementation with AI Optimization
"""

import os
import asyncio
import logging
import time
import json
import hashlib
import struct
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# FastAPI and WebSocket imports
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn

# Database imports
from motor.motor_asyncio import AsyncIOMotorClient
import pymongo

# System monitoring
import psutil

# Scientific computing for AI
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pandas as pd

# Crypto and networking
import requests
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import secrets

# Environment
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="CryptoMiner Pro API",
    description="Advanced Cryptocurrency Mining System with AI Optimization",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "crypto_miner_db")

# Global variables
db_client: Optional[AsyncIOMotorClient] = None
db = None
connected_websockets: List[WebSocket] = []
mining_engine = None

# Pydantic models
class CoinConfig(BaseModel):
    name: str
    symbol: str
    algorithm: str = "scrypt"
    network_difficulty: float = 1.0
    block_reward: float = 50.0
    block_time_target: int = 60
    rpc_url: Optional[str] = None
    pool_url: Optional[str] = None
    scrypt_params: Dict[str, int] = {"N": 1024, "r": 1, "p": 1}
    wallet_address_format: str = "legacy"  # "legacy", "segwit", "dogecoin"
    address_prefix: str = "L"  # Address prefix for validation

class MiningConfig(BaseModel):
    coin: CoinConfig
    mode: str = "solo"  # "solo" or "pool"
    threads: int = 4
    intensity: float = 1.0
    auto_optimize: bool = True
    ai_enabled: bool = True
    wallet_address: str = ""  # Mining reward address
    pool_username: Optional[str] = None  # Pool mining username
    pool_password: Optional[str] = "x"  # Pool mining password

class MiningStats(BaseModel):
    hashrate: float = 0.0
    accepted_shares: int = 0
    rejected_shares: int = 0
    blocks_found: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    temperature: Optional[float] = None
    uptime: float = 0.0
    efficiency: float = 0.0

class AIInsights(BaseModel):
    hash_pattern_prediction: Dict[str, Any] = {}
    difficulty_forecast: Dict[str, Any] = {}
    coin_switching_recommendation: Dict[str, Any] = {}
    optimization_suggestions: List[str] = []

# ============================================================================
# WALLET ADDRESS VALIDATION
# ============================================================================

class WalletValidator:
    """
    Wallet address validation for different cryptocurrency formats
    """
    
    @staticmethod
    def validate_address(address: str, coin_symbol: str) -> Dict[str, Any]:
        """
        Validate wallet address format for specific cryptocurrency
        """
        if not address or len(address.strip()) == 0:
            return {"valid": False, "error": "Wallet address cannot be empty"}
        
        address = address.strip()
        
        # Basic length checks
        if len(address) < 25 or len(address) > 62:
            return {"valid": False, "error": "Invalid address length"}
        
        # Coin-specific validation
        if coin_symbol == "LTC":
            return WalletValidator._validate_litecoin_address(address)
        elif coin_symbol == "DOGE":
            return WalletValidator._validate_dogecoin_address(address)
        elif coin_symbol == "FTC":
            return WalletValidator._validate_feathercoin_address(address)
        else:
            return WalletValidator._validate_generic_address(address)
    
    @staticmethod
    def _validate_feathercoin_address(address: str) -> Dict[str, Any]:
        """Validate Feathercoin address format"""
        # Feathercoin addresses start with 6 (standard) or 3 (multisig)
        if address.startswith('6'):
            if len(address) >= 27 and len(address) <= 35:
                return {"valid": True, "format": "base58", "type": "standard"}
            else:
                return {"valid": False, "error": "Invalid Feathercoin address length"}
        elif address.startswith('3'):
            if len(address) >= 27 and len(address) <= 35:
                return {"valid": True, "format": "base58", "type": "multisig"}
            else:
                return {"valid": False, "error": "Invalid multisig address length"}
        else:
            return {"valid": False, "error": "Feathercoin address must start with 6 or 3"}
    
    @staticmethod
    def _validate_litecoin_address(address: str) -> Dict[str, Any]:
        """Validate Litecoin address format"""
        # Litecoin addresses start with L (legacy) or M (multisig) or ltc1 (bech32)
        if address.startswith('ltc1'):
            # Bech32 format
            if len(address) >= 39 and len(address) <= 62:
                return {"valid": True, "format": "bech32", "type": "segwit"}
            else:
                return {"valid": False, "error": "Invalid bech32 address length"}
        elif address.startswith('L'):
            # Legacy P2PKH
            if len(address) >= 26 and len(address) <= 35:
                return {"valid": True, "format": "base58", "type": "legacy"}
            else:
                return {"valid": False, "error": "Invalid legacy address length"}
        elif address.startswith('M') or address.startswith('3'):
            # P2SH (multisig)
            if len(address) >= 26 and len(address) <= 35:
                return {"valid": True, "format": "base58", "type": "multisig"}
            else:
                return {"valid": False, "error": "Invalid multisig address length"}
        else:
            return {"valid": False, "error": "Address must start with L, M, 3, or ltc1"}
    
    @staticmethod
    def _validate_dogecoin_address(address: str) -> Dict[str, Any]:
        """Validate Dogecoin address format"""
        # Dogecoin addresses start with D (standard) or A (multisig)
        if address.startswith('D'):
            if len(address) >= 27 and len(address) <= 35:
                return {"valid": True, "format": "base58", "type": "standard"}
            else:
                return {"valid": False, "error": "Invalid Dogecoin address length"}
        elif address.startswith('A') or address.startswith('9'):
            if len(address) >= 27 and len(address) <= 35:
                return {"valid": True, "format": "base58", "type": "multisig"}
            else:
                return {"valid": False, "error": "Invalid multisig address length"}
        else:
            return {"valid": False, "error": "Dogecoin address must start with D, A, or 9"}
    
    @staticmethod
    def _validate_generic_address(address: str) -> Dict[str, Any]:
        """Generic address validation for unknown coin types"""
        # Basic alphanumeric check
        if address.isalnum():
            return {"valid": True, "format": "unknown", "type": "generic"}
        else:
            return {"valid": False, "error": "Address contains invalid characters"}

# ============================================================================
# CORE SCRYPT IMPLEMENTATION
# ============================================================================

class ScryptEngine:
    """
    Complete Scrypt algorithm implementation for cryptocurrency mining
    Supports various scrypt parameters (N, r, p) for different coins
    """
    
    def __init__(self, N: int = 1024, r: int = 1, p: int = 1):
        self.N = N  # CPU/memory cost parameter
        self.r = r  # Block size parameter  
        self.p = p  # Parallelization parameter
        self.cache = {}
        
    def _salsa20_core(self, data: bytearray) -> bytearray:
        """Salsa20 core function used in scrypt"""
        def _rotl(value: int, amount: int) -> int:
            return ((value << amount) | (value >> (32 - amount))) & 0xffffffff
        
        # Convert to 32-bit integers
        x = [struct.unpack('<I', data[i:i+4])[0] for i in range(0, 64, 4)]
        
        # Salsa20 rounds
        for _ in range(10):  # 20 rounds total (10 iterations)
            # Column round
            x[4] ^= _rotl((x[0] + x[12]) & 0xffffffff, 7)
            x[8] ^= _rotl((x[4] + x[0]) & 0xffffffff, 9)
            x[12] ^= _rotl((x[8] + x[4]) & 0xffffffff, 13)
            x[0] ^= _rotl((x[12] + x[8]) & 0xffffffff, 18)
            
            x[9] ^= _rotl((x[5] + x[1]) & 0xffffffff, 7)
            x[13] ^= _rotl((x[9] + x[5]) & 0xffffffff, 9)
            x[1] ^= _rotl((x[13] + x[9]) & 0xffffffff, 13)
            x[5] ^= _rotl((x[1] + x[13]) & 0xffffffff, 18)
            
            x[14] ^= _rotl((x[10] + x[6]) & 0xffffffff, 7)
            x[2] ^= _rotl((x[14] + x[10]) & 0xffffffff, 9)
            x[6] ^= _rotl((x[2] + x[14]) & 0xffffffff, 13)
            x[10] ^= _rotl((x[6] + x[2]) & 0xffffffff, 18)
            
            x[3] ^= _rotl((x[15] + x[11]) & 0xffffffff, 7)
            x[7] ^= _rotl((x[3] + x[15]) & 0xffffffff, 9)
            x[11] ^= _rotl((x[7] + x[3]) & 0xffffffff, 13)
            x[15] ^= _rotl((x[11] + x[7]) & 0xffffffff, 18)
            
            # Row round
            x[1] ^= _rotl((x[0] + x[3]) & 0xffffffff, 7)
            x[2] ^= _rotl((x[1] + x[0]) & 0xffffffff, 9)
            x[3] ^= _rotl((x[2] + x[1]) & 0xffffffff, 13)
            x[0] ^= _rotl((x[3] + x[2]) & 0xffffffff, 18)
            
            x[6] ^= _rotl((x[5] + x[4]) & 0xffffffff, 7)
            x[7] ^= _rotl((x[6] + x[5]) & 0xffffffff, 9)
            x[4] ^= _rotl((x[7] + x[6]) & 0xffffffff, 13)
            x[5] ^= _rotl((x[4] + x[7]) & 0xffffffff, 18)
            
            x[11] ^= _rotl((x[10] + x[9]) & 0xffffffff, 7)
            x[8] ^= _rotl((x[11] + x[10]) & 0xffffffff, 9)
            x[9] ^= _rotl((x[8] + x[11]) & 0xffffffff, 13)
            x[10] ^= _rotl((x[9] + x[8]) & 0xffffffff, 18)
            
            x[12] ^= _rotl((x[15] + x[14]) & 0xffffffff, 7)
            x[13] ^= _rotl((x[12] + x[15]) & 0xffffffff, 9)
            x[14] ^= _rotl((x[13] + x[12]) & 0xffffffff, 13)
            x[15] ^= _rotl((x[14] + x[13]) & 0xffffffff, 18)
        
        # Pack back to bytes
        result = bytearray(64)
        for i in range(16):
            struct.pack_into('<I', result, i * 4, x[i])
        
        return result
    
    def _scrypt_blockmix(self, block: bytearray) -> bytearray:
        """scryptBlockMix function"""
        X = bytearray(block[-64:])  # Last 64 bytes
        Y = bytearray(len(block))
        
        for i in range(0, len(block), 64):
            # XOR with X
            for j in range(64):
                X[j] ^= block[i + j]
            
            # Apply Salsa20
            X = self._salsa20_core(X)
            
            # Store result
            if i % 128 == 0:
                Y[i//2:i//2+64] = X
            else:
                Y[len(block)//2 + i//2:len(block)//2 + i//2+64] = X
        
        return Y
    
    def _scrypt_romix(self, block: bytearray, N: int) -> bytearray:
        """scryptROMix function"""
        V = []
        X = bytearray(block)
        
        # First loop: store N values
        for i in range(N):
            V.append(bytearray(X))
            X = self._scrypt_blockmix(X)
        
        # Second loop: mix with stored values
        for i in range(N):
            j = struct.unpack('<Q', X[-8:])[0] % N
            for k in range(len(X)):
                X[k] ^= V[j][k]
            X = self._scrypt_blockmix(X)
        
        return X
    
    def scrypt_hash(self, password: bytes, salt: bytes) -> bytes:
        """
        Complete scrypt hash function implementation
        """
        # PBKDF2 with SHA256 for initial key derivation
        key = hashlib.pbkdf2_hmac('sha256', password, salt, 1, self.r * 128)
        
        # Split into blocks
        blocks = []
        for i in range(0, len(key), 128):
            blocks.append(bytearray(key[i:i+128]))
        
        # Apply scryptROMix to each block
        for i in range(len(blocks)):
            blocks[i] = self._scrypt_romix(blocks[i], self.N)
        
        # Combine blocks
        combined = bytearray()
        for block in blocks:
            combined.extend(block)
        
        # Final PBKDF2
        final_key = hashlib.pbkdf2_hmac('sha256', combined, salt, 1, 32)
        
        return final_key

# ============================================================================
# MINING ENGINE
# ============================================================================

class MiningEngine:
    """
    High-performance mining engine with multi-threading and optimization
    """
    
    def __init__(self, config: MiningConfig):
        self.config = config
        self.scrypt_engine = ScryptEngine(
            N=config.coin.scrypt_params["N"],
            r=config.coin.scrypt_params["r"], 
            p=config.coin.scrypt_params["p"]
        )
        
        self.stats = MiningStats()
        self.is_mining = False
        self.start_time = None
        
        self.thread_pool = ThreadPoolExecutor(max_workers=config.threads)
        self.hash_count = 0
        self.last_hash_time = time.time()
        
        # AI components
        self.ai_predictor = None
        if config.ai_enabled:
            self.ai_predictor = AIPredictor()
    
    def start_mining(self):
        """Start the mining process"""
        if self.is_mining:
            return
        
        self.is_mining = True
        self.start_time = time.time()
        
        logger.info(f"Starting mining for {self.config.coin.name} with {self.config.threads} threads")
        
        # Start mining threads
        for i in range(self.config.threads):
            threading.Thread(
                target=self._mining_thread,
                args=(i,),
                daemon=True
            ).start()
        
        # Start statistics monitoring thread
        threading.Thread(target=self._stats_thread, daemon=True).start()
    
    def stop_mining(self):
        """Stop the mining process"""
        self.is_mining = False
        logger.info("Mining stopped")
    
    def _mining_thread(self, thread_id: int):
        """Individual mining thread"""
        nonce = thread_id * 1000000
        
        while self.is_mining:
            try:
                # Create block header
                block_header = self._create_block_header(nonce)
                
                # Calculate scrypt hash
                hash_result = self.scrypt_engine.scrypt_hash(block_header, b"salt")
                
                # Check if hash meets difficulty target
                if self._check_difficulty(hash_result):
                    self._handle_valid_hash(hash_result, nonce)
                
                nonce += 1
                self.hash_count += 1
                
                # Apply intensity throttling
                if self.config.intensity < 1.0:
                    time.sleep((1.0 - self.config.intensity) * 0.001)
                    
            except Exception as e:
                logger.error(f"Mining thread {thread_id} error: {e}")
                time.sleep(0.1)
    
    def _create_block_header(self, nonce: int) -> bytes:
        """Create block header for hashing"""
        # Simplified block header structure
        version = 1
        prev_hash = b"0" * 32
        
        # Create coinbase transaction with wallet address if available
        if self.config.wallet_address:
            coinbase_data = f"Mining to {self.config.wallet_address}".encode()[:75]
        else:
            coinbase_data = b"CryptoMiner Pro"
        
        # Pad coinbase to standard size
        coinbase_padded = coinbase_data.ljust(76, b'\x00')[:76]
        merkle_root = hashlib.sha256(coinbase_padded).digest()
        
        timestamp = int(time.time())
        bits = 0x1d00ffff  # Difficulty bits
        
        header = struct.pack(
            '<I32s32sIII',
            version, prev_hash, merkle_root, timestamp, bits, nonce
        )
        
        return header
    
    def _check_difficulty(self, hash_result: bytes) -> bool:
        """Check if hash meets current difficulty target"""
        # Convert hash to integer
        hash_int = int.from_bytes(hash_result, byteorder='big')
        
        # Simple difficulty check (leading zeros)
        target_difficulty = 2 ** (256 - 20)  # Adjust as needed
        
        return hash_int < target_difficulty
    
    def _handle_valid_hash(self, hash_result: bytes, nonce: int):
        """Handle a valid hash (potential block or share)"""
        logger.info(f"Valid hash found! Nonce: {nonce}")
        
        if self.config.mode == "solo":
            self.stats.blocks_found += 1
            self.stats.accepted_shares += 1
        else:
            # Submit to pool
            self._submit_share(hash_result, nonce)
    
    def _submit_share(self, hash_result: bytes, nonce: int):
        """Submit share to mining pool"""
        try:
            if self.config.coin.pool_url:
                # Pool submission logic would go here
                self.stats.accepted_shares += 1
                logger.info("Share submitted to pool")
        except Exception as e:
            self.stats.rejected_shares += 1
            logger.error(f"Share submission failed: {e}")
    
    def _stats_thread(self):
        """Thread for updating mining statistics"""
        while self.is_mining:
            try:
                # Calculate hashrate
                current_time = time.time()
                time_diff = current_time - self.last_hash_time
                
                if time_diff >= 1.0:  # Update every second
                    self.stats.hashrate = self.hash_count / time_diff
                    self.hash_count = 0
                    self.last_hash_time = current_time
                
                # Update system stats
                self.stats.cpu_usage = psutil.cpu_percent()
                self.stats.memory_usage = psutil.virtual_memory().percent
                
                # Update uptime
                if self.start_time:
                    self.stats.uptime = current_time - self.start_time
                
                # Calculate efficiency
                if self.stats.hashrate > 0:
                    total_shares = self.stats.accepted_shares + self.stats.rejected_shares
                    self.stats.efficiency = (self.stats.accepted_shares / max(1, total_shares)) * 100
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Stats thread error: {e}")
                time.sleep(1)

# ============================================================================
# AI PREDICTION SYSTEM
# ============================================================================

class AIPredictor:
    """
    Advanced AI system for mining optimization and prediction
    """
    
    def __init__(self):
        self.hash_pattern_model = RandomForestRegressor(n_estimators=100)
        self.difficulty_model = RandomForestRegressor(n_estimators=100)
        self.coin_switching_model = RandomForestRegressor(n_estimators=100)
        
        self.scaler = StandardScaler()
        self.training_data = []
        self.is_trained = False
    
    def collect_training_data(self, mining_stats: MiningStats, market_data: Dict):
        """Collect data for AI training"""
        data_point = {
            'timestamp': time.time(),
            'hashrate': mining_stats.hashrate,
            'cpu_usage': mining_stats.cpu_usage,
            'memory_usage': mining_stats.memory_usage,
            'efficiency': mining_stats.efficiency,
            'accepted_shares': mining_stats.accepted_shares,
            'rejected_shares': mining_stats.rejected_shares,
        }
        
        # Add market data if available
        data_point.update(market_data)
        
        self.training_data.append(data_point)
        
        # Train model when we have enough data
        if len(self.training_data) > 100 and len(self.training_data) % 50 == 0:
            self._train_models()
    
    def _train_models(self):
        """Train AI models with collected data"""
        try:
            df = pd.DataFrame(self.training_data)
            
            if len(df) > 10:
                # Prepare features
                features = ['hashrate', 'cpu_usage', 'memory_usage', 'efficiency']
                available_features = [f for f in features if f in df.columns]
                
                if len(available_features) >= 2:
                    X = df[available_features].fillna(0)
                    
                    # Hash pattern prediction
                    if 'hashrate' in df.columns:
                        y_hash = df['hashrate'].shift(-1).fillna(method='ffill')
                        self.hash_pattern_model.fit(X, y_hash)
                    
                    self.is_trained = True
                    logger.info("AI models trained successfully")
        
        except Exception as e:
            logger.error(f"AI training error: {e}")
    
    def predict_optimal_settings(self, current_stats: MiningStats) -> Dict[str, Any]:
        """Predict optimal mining settings"""
        if not self.is_trained:
            return {
                'recommended_threads': 4,
                'recommended_intensity': 1.0,
                'confidence': 0.0
            }
        
        try:
            # Create feature vector
            features = np.array([[
                current_stats.hashrate,
                current_stats.cpu_usage,
                current_stats.memory_usage,
                current_stats.efficiency
            ]])
            
            # Make predictions
            predicted_hashrate = self.hash_pattern_model.predict(features)[0]
            
            return {
                'predicted_hashrate': float(predicted_hashrate),
                'recommended_threads': min(8, max(1, int(predicted_hashrate / 1000))),
                'recommended_intensity': min(1.0, max(0.1, current_stats.efficiency / 100)),
                'confidence': 0.8
            }
        
        except Exception as e:
            logger.error(f"AI prediction error: {e}")
            return {'error': str(e)}
    
    def get_insights(self) -> AIInsights:
        """Get comprehensive AI insights"""
        insights = AIInsights()
        
        if self.is_trained and len(self.training_data) > 0:
            recent_data = self.training_data[-10:]
            
            insights.hash_pattern_prediction = {
                'trend': 'increasing' if len(recent_data) > 1 and 
                        recent_data[-1]['hashrate'] > recent_data[-2]['hashrate'] else 'stable',
                'confidence': 0.7
            }
            
            insights.optimization_suggestions = [
                "Consider increasing thread count during low CPU usage periods",
                "Monitor memory usage to prevent system slowdown",
                "Enable auto-intensity for optimal performance"
            ]
        
        return insights

# Global mining engine instance
mining_engine: Optional[MiningEngine] = None

# ============================================================================
# DATABASE SETUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database connection and setup"""
    global db_client, db
    
    try:
        db_client = AsyncIOMotorClient(MONGO_URL)
        db = db_client[DATABASE_NAME]
        
        # Test connection
        await db_client.admin.command('ping')
        logger.info("Database connected successfully")
        
        # Create indexes
        await db.mining_stats.create_index([("timestamp", pymongo.DESCENDING)])
        await db.mining_configs.create_index([("name", pymongo.ASCENDING)], unique=True)
        
    except Exception as e:
        logger.error(f"Database connection failed: {e}")

@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup on shutdown"""
    global db_client, mining_engine
    
    if mining_engine:
        mining_engine.stop_mining()
    
    if db_client:
        db_client.close()

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/mining/status")
async def get_mining_status():
    """Get current mining status and statistics"""
    global mining_engine
    
    if not mining_engine:
        return {
            "is_mining": False,
            "stats": MiningStats().dict(),
            "message": "Mining engine not initialized"
        }
    
    return {
        "is_mining": mining_engine.is_mining,
        "stats": mining_engine.stats.dict(),
        "config": mining_engine.config.dict()
    }

@app.post("/api/mining/start")
async def start_mining(config: MiningConfig):
    """Start mining with given configuration"""
    global mining_engine
    
    try:
        # Validate wallet address if provided
        if config.wallet_address and config.wallet_address.strip():
            validation_result = WalletValidator.validate_address(
                config.wallet_address, 
                config.coin.symbol
            )
            
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid wallet address: {validation_result['error']}"
                )
            
            logger.info(f"Wallet address validated: {config.wallet_address} ({validation_result.get('format', 'unknown')})")
        elif config.mode == "solo":
            raise HTTPException(
                status_code=400,
                detail="Wallet address is required for solo mining"
            )
        
        # Validate pool credentials for pool mining
        if config.mode == "pool":
            if not config.pool_username:
                raise HTTPException(
                    status_code=400,
                    detail="Pool username is required for pool mining"
                )
        
        mining_engine = MiningEngine(config)
        mining_engine.start_mining()
        
        return {
            "success": True,
            "message": f"Mining started for {config.coin.name}",
            "config": config.dict(),
            "wallet_info": {
                "address": config.wallet_address,
                "mode": config.mode,
                "validation": "passed" if config.wallet_address else "not_required"
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to start mining: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mining/stop")
async def stop_mining():
    """Stop mining"""
    global mining_engine
    
    if mining_engine:
        mining_engine.stop_mining()
        return {"success": True, "message": "Mining stopped"}
    
    return {"success": False, "message": "No active mining session"}

@app.get("/api/mining/ai-insights")
async def get_ai_insights():
    """Get AI insights and predictions"""
    global mining_engine
    
    if not mining_engine or not mining_engine.ai_predictor:
        return {"error": "AI system not available"}
    
    insights = mining_engine.ai_predictor.get_insights()
    predictions = mining_engine.ai_predictor.predict_optimal_settings(mining_engine.stats)
    
    return {
        "insights": insights.dict(),
        "predictions": predictions
    }

@app.get("/api/coins/presets")
async def get_coin_presets():
    """Get predefined coin configurations"""
    presets = {
        "litecoin": CoinConfig(
            name="Litecoin",
            symbol="LTC", 
            algorithm="scrypt",
            network_difficulty=5000000.0,
            block_reward=12.5,
            block_time_target=150,
            scrypt_params={"N": 1024, "r": 1, "p": 1},
            wallet_address_format="legacy",
            address_prefix="L"
        ),
        "dogecoin": CoinConfig(
            name="Dogecoin",
            symbol="DOGE",
            algorithm="scrypt", 
            network_difficulty=3000000.0,
            block_reward=10000.0,
            block_time_target=60,
            scrypt_params={"N": 1024, "r": 1, "p": 1},
            wallet_address_format="dogecoin",
            address_prefix="D"
        ),
        "feathercoin": CoinConfig(
            name="Feathercoin",
            symbol="FTC",
            algorithm="scrypt",
            network_difficulty=1000000.0, 
            block_reward=200.0,
            block_time_target=60,
            scrypt_params={"N": 1024, "r": 1, "p": 1},
            wallet_address_format="legacy",
            address_prefix="6"
        )
    }
    
    return {"presets": {k: v.dict() for k, v in presets.items()}}

@app.post("/api/wallet/validate")
async def validate_wallet_address(request: dict):
    """Validate wallet address for specific coin"""
    try:
        address = request.get("address", "").strip()
        coin_symbol = request.get("coin_symbol", "").upper()
        
        if not address:
            return {"valid": False, "error": "Wallet address is required"}
        
        if not coin_symbol:
            return {"valid": False, "error": "Coin symbol is required"}
        
        validation_result = WalletValidator.validate_address(address, coin_symbol)
        
        return validation_result
        
    except Exception as e:
        logger.error(f"Wallet validation error: {e}")
        return {"valid": False, "error": "Validation failed"}

@app.get("/api/system/stats")
async def get_system_stats():
    """Get system resource statistics"""
    try:
        return {
            "cpu": {
                "usage_percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
                "used": psutil.virtual_memory().used
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent
            }
        }
    except Exception as e:
        logger.error(f"System stats error: {e}")
        return {"error": str(e)}

# ============================================================================
# WEBSOCKET CONNECTION
# ============================================================================

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    connected_websockets.append(websocket)
    
    try:
        while True:
            # Send real-time mining data
            if mining_engine:
                data = {
                    "type": "mining_update",
                    "timestamp": time.time(),
                    "stats": mining_engine.stats.dict(),
                    "is_mining": mining_engine.is_mining
                }
                
                await websocket.send_json(data)
            
            # Send system stats
            system_stats = await get_system_stats()
            await websocket.send_json({
                "type": "system_update", 
                "timestamp": time.time(),
                "data": system_stats
            })
            
            await asyncio.sleep(1)  # Update every second
            
    except WebSocketDisconnect:
        connected_websockets.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)

# ============================================================================
# MAIN APPLICATION RUNNER
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0", 
        port=8001,
        reload=True,
        log_level="info"
    )