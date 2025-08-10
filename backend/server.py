#!/usr/bin/env python3
"""
CryptoMiner Pro - Consolidated FastAPI Server
Integrates with consolidated mining_engine, ai_system, and utils modules
"""

import os
import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

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

# Import consolidated modules
from mining_engine import mining_engine, pool_manager, MiningStats, CoinConfig
from ai_system import ai_system
from utils import (
    validate_wallet_address, 
    get_system_info, 
    get_coin_presets,
    validate_mining_config,
    performance_monitor
)

# Import V30 Enterprise components
from enterprise_license import EnterpriseV30License
from hardware_validator import EnterpriseHardwareValidator
from gpu_mining_engine import HybridGPUCPUMiner
from v30_protocol import DistributedMiningServer
from v30_central_control import CentralControlSystem

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
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
REMOTE_DB_ENABLED = os.getenv("REMOTE_DB_ENABLED", "false").lower() == "true"
REMOTE_MONGO_URL = os.getenv("REMOTE_MONGO_URL", "mongodb://localhost:27017")

# Use remote database if enabled
if REMOTE_DB_ENABLED and REMOTE_MONGO_URL != "mongodb://localhost:27017":
    MONGO_URL = REMOTE_MONGO_URL
    logger.info(f"Using remote database: {REMOTE_MONGO_URL[:20]}...")

DATABASE_NAME = os.getenv("DATABASE_NAME", "crypto_miner_db")

# Global variables
db_client: Optional[AsyncIOMotorClient] = None
db = None
connected_websockets: List[WebSocket] = []

# V30 Enterprise System
v30_control_system: Optional[CentralControlSystem] = None
enterprise_license_system = EnterpriseV30License()
hardware_validator = EnterpriseHardwareValidator()

# Pydantic models
class MiningConfig(BaseModel):
    coin: Dict[str, Any]
    mode: str = "solo"
    threads: int = 4
    intensity: float = 1.0
    auto_optimize: bool = True
    ai_enabled: bool = True
    wallet_address: str = ""
    pool_username: Optional[str] = None
    pool_password: Optional[str] = "x"
    custom_pool_address: Optional[str] = None
    custom_pool_port: Optional[int] = None
    custom_rpc_host: Optional[str] = None
    custom_rpc_port: Optional[int] = None
    custom_rpc_username: Optional[str] = None
    custom_rpc_password: Optional[str] = None
    auto_thread_detection: bool = True
    thread_profile: str = "standard"
    # Enterprise configurations
    enterprise_mode: bool = False
    target_cpu_utilization: float = 1.0
    thread_scaling_enabled: bool = True

class WalletAddress(BaseModel):
    address: str
    coin_symbol: str

class SavedPool(BaseModel):
    name: str
    coin_symbol: str
    wallet_address: str
    pool_address: str
    pool_port: int
    pool_password: str = "x"
    pool_username: Optional[str] = None
    description: Optional[str] = ""

class CustomCoin(BaseModel):
    name: str
    symbol: str
    algorithm: str = "Scrypt"
    block_reward: float = 25.0
    block_time: int = 150
    difficulty: float = 1000.0
    scrypt_params: dict = {"n": 1024, "r": 1, "p": 1}
    network_hashrate: str = "Unknown"
    wallet_format: str = "Standard"
    description: Optional[str] = ""

# ============================================================================
# DATABASE SETUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database connection and AI system"""
    global db_client, db, v30_control_system
    
    try:
        db_client = AsyncIOMotorClient(MONGO_URL)
        db = db_client[DATABASE_NAME]
        
        # Test connection
        await db_client.admin.command('ping')
        logger.info("Database connected successfully")
        
        # Create indexes
        await db.mining_stats.create_index([("timestamp", pymongo.DESCENDING)])
        await db.mining_configs.create_index([("name", pymongo.ASCENDING)], unique=True)
        
        # Start AI system
        ai_system.start_ai_system()
        logger.info("AI system started")
        
        # Initialize V30 Enterprise System
        v30_control_system = CentralControlSystem()
        # Note: V30 system will be initialized when first accessed to avoid port conflicts
        logger.info("V30 Enterprise System ready for initialization")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup on shutdown"""
    global db_client, v30_control_system
    
    # Stop mining
    if mining_engine.is_mining:
        mining_engine.stop_mining()
    
    # Stop V30 system
    if v30_control_system and v30_control_system.is_running:
        await v30_control_system.shutdown_system()
    
    # Stop AI system
    ai_system.stop_ai_system()
    
    # Close database connection
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
        "version": "v30",
        "edition": "Enterprise",
        "ai_system": ai_system.status.is_active,
        "mining_active": mining_engine.is_mining,
        "v30_system": v30_control_system.is_running if v30_control_system else False
    }

@app.get("/api/mining/status")
async def get_mining_status():
    """Get current mining status and statistics"""
    status = mining_engine.get_mining_status()
    
    return {
        "is_mining": status["is_mining"],
        "stats": status["stats"],
        "config": status["config"]
    }

@app.post("/api/mining/start")
async def start_mining(config: MiningConfig):
    """Start mining with given configuration"""
    try:
        # Convert config to CoinConfig object
        coin_config = CoinConfig(**config.coin)
        
        # Validate wallet address if provided
        if config.wallet_address and config.wallet_address.strip():
            is_valid, message = validate_wallet_address(
                config.wallet_address, 
                coin_config.symbol
            )
            
            if not is_valid:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid wallet address: {message}"
                )
            
            logger.info(f"Wallet address validated: {config.wallet_address}")
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
        
        # Start mining
        success, message = mining_engine.start_mining(
            coin_config,
            config.wallet_address,
            config.threads
        )
        
        if not success:
            raise HTTPException(status_code=500, detail=message)
        
        return {
            "success": True,
            "message": message,
            "config": config.dict(),
            "wallet_info": {
                "address": config.wallet_address,
                "mode": config.mode,
                "threads_used": config.threads,
                "validation": "passed"
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to start mining: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mining/stop")
async def stop_mining():
    """Stop mining"""
    success, message = mining_engine.stop_mining()
    
    return {
        "success": success,
        "message": message
    }

@app.get("/api/mining/ai-insights")
async def get_ai_insights():
    """Get AI insights and predictions"""
    try:
        # Get current mining stats
        mining_status = mining_engine.get_mining_status()
        stats = mining_status.get("stats", {})
        
        # Get AI insights
        insights = ai_system.get_ai_insights(
            current_hashrate=stats.get("hashrate", 0),
            current_cpu=stats.get("cpu_usage", 0),
            current_memory=stats.get("memory_usage", 0),
            threads=1
        )
        
        return {
            "insights": {
                "hash_pattern_prediction": insights.hash_pattern_prediction,
                "network_difficulty_forecast": insights.network_difficulty_forecast,
                "optimization_suggestions": insights.optimization_suggestions,
                "pool_performance_analysis": insights.pool_performance_analysis,
                "efficiency_recommendations": insights.efficiency_recommendations
            },
            "predictions": insights.hash_pattern_prediction
        }
    
    except Exception as e:
        logger.error(f"AI insights error: {e}")
        return {"error": "AI system not available"}

@app.get("/api/ai/status")
async def get_ai_status():
    """Get AI system status"""
    return ai_system.get_system_status()

@app.post("/api/ai/auto-optimize")
async def auto_optimize():
    """Trigger AI auto-optimization"""
    # This would trigger AI optimization logic
    return {"success": True, "message": "Auto-optimization triggered"}

@app.get("/api/coins/presets")
async def get_coin_presets_endpoint():
    """Get predefined coin configurations"""
    presets = get_coin_presets()
    return {"presets": presets}

@app.post("/api/validate_wallet")
async def validate_wallet_endpoint(wallet: WalletAddress):
    """Validate wallet address"""
    is_valid, message = validate_wallet_address(wallet.address, wallet.coin_symbol)
    
    return {
        "valid": is_valid,
        "message": message if not is_valid else "Address is valid",
        "format": "validated" if is_valid else "invalid"
    }

@app.post("/api/pool/test-connection")
async def test_pool_connection(request: dict):
    """Test pool or RPC connection"""
    try:
        pool_address = request.get("pool_address")
        pool_port = request.get("pool_port")
        connection_type = request.get("type", "pool")
        
        if not pool_address or not pool_port:
            raise HTTPException(status_code=400, detail="Pool address and port are required")
        
        if connection_type == "pool":
            result = pool_manager.test_pool_connection(pool_address, pool_port)
        else:  # RPC
            username = request.get("username", "")
            password = request.get("password", "")
            result = pool_manager.test_rpc_connection(pool_address, pool_port, username, password)
        
        return result
        
    except Exception as e:
        logger.error(f"Pool connection test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/cpu-info")
async def get_cpu_info():
    """Get detailed CPU information including enterprise capabilities"""
    try:
        system_detector = mining_engine.system_detector
        system_detector.refresh_system_info()
        
        cpu_info = {
            "physical_cores": system_detector.cpu_info.get("physical_cores", 1),
            "logical_cores": system_detector.cpu_info.get("logical_cores", 1),
            "frequency": system_detector.cpu_info.get("frequency", {}),
            "architecture": system_detector.cpu_info.get("architecture", "unknown"),
            "max_safe_threads": system_detector.system_capabilities.get("max_safe_threads", 1),
            "enterprise_mode": system_detector.system_capabilities.get("enterprise_mode", False),
            "optimal_thread_density": system_detector.system_capabilities.get("optimal_thread_density", 1.0),
            "total_memory_gb": system_detector.system_capabilities.get("total_memory_gb", 1),
            "available_memory_gb": system_detector.system_capabilities.get("available_memory_gb", 1),
            "recommended_threads": {
                "low": system_detector.get_recommended_threads(0.25),
                "medium": system_detector.get_recommended_threads(0.5),
                "high": system_detector.get_recommended_threads(0.75),
                "maximum": system_detector.get_recommended_threads(1.0)
            }
        }
        
        return cpu_info
        
    except Exception as e:
        logger.error(f"CPU info error: {e}")
        # Fallback to basic info
        return {
            "physical_cores": psutil.cpu_count(logical=False) or 1,
            "logical_cores": psutil.cpu_count(logical=True) or 1,
            "frequency": {},
            "architecture": "unknown",
            "max_safe_threads": psutil.cpu_count(logical=True) or 1,
            "enterprise_mode": False,
            "optimal_thread_density": 1.0,
            "error": str(e)
        }

@app.post("/api/test-db-connection")
async def test_database_connection(request: dict):
    """Test connection to a MongoDB database URL"""
    try:
        database_url = request.get("database_url")
        if not database_url:
            raise HTTPException(status_code=400, detail="Database URL is required")
        
        # Test connection
        test_client = AsyncIOMotorClient(database_url, serverSelectionTimeoutMS=5000)
        
        # Attempt to connect and ping
        await test_client.admin.command('ping')
        
        # Close test connection
        test_client.close()
        
        return {
            "success": True,
            "message": "Database connection successful",
            "url": database_url[:20] + "..." if len(database_url) > 20 else database_url
        }
        
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Database connection failed"
        }

@app.get("/api/system/stats")
async def get_system_stats():
    """Get system resource statistics"""
    try:
        stats = get_system_info()
        
        return {
            "cpu_usage": stats["cpu"]["usage"],
            "memory_usage": stats["memory"]["percentage"],
            "disk_usage": stats["disk"]["percentage"],
            "uptime": stats["uptime"],
            "cores": stats["cpu"]["cores"]
        }
        
    except Exception as e:
        logger.error(f"System stats error: {e}")
        return {"error": str(e)}

# ============================================================================
# SAVED POOLS API ENDPOINTS
# ============================================================================

@app.get("/api/pools/saved")
async def get_saved_pools():
    """Get all saved pool configurations"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        pools = []
        async for pool in db.saved_pools.find().sort("name", 1):
            # Convert ObjectId to string for JSON serialization
            pool["_id"] = str(pool["_id"])
            pools.append(pool)
        
        return {"pools": pools, "count": len(pools)}
        
    except Exception as e:
        logger.error(f"Get saved pools error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pools/saved")
async def save_pool_configuration(pool: SavedPool):
    """Save a new pool configuration"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        # Check if pool name already exists
        existing = await db.saved_pools.find_one({"name": pool.name})
        if existing:
            raise HTTPException(status_code=400, detail="Pool name already exists")
        
        # Validate wallet address
        if pool.wallet_address:
            is_valid, message = validate_wallet_address(pool.wallet_address, pool.coin_symbol)
            if not is_valid:
                raise HTTPException(status_code=400, detail=f"Invalid wallet address: {message}")
        
        pool_data = pool.dict()
        pool_data["created_at"] = datetime.utcnow()
        pool_data["last_used"] = None
        
        result = await db.saved_pools.insert_one(pool_data)
        
        return {
            "success": True,
            "message": "Pool configuration saved successfully",
            "pool_id": str(result.inserted_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Save pool error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/pools/saved/{pool_id}")
async def update_saved_pool(pool_id: str, pool: SavedPool):
    """Update an existing saved pool configuration"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        # Validate wallet address
        if pool.wallet_address:
            is_valid, message = validate_wallet_address(pool.wallet_address, pool.coin_symbol)
            if not is_valid:
                raise HTTPException(status_code=400, detail=f"Invalid wallet address: {message}")
        
        from bson import ObjectId
        
        pool_data = pool.dict()
        pool_data["updated_at"] = datetime.utcnow()
        
        result = await db.saved_pools.update_one(
            {"_id": ObjectId(pool_id)},
            {"$set": pool_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Pool configuration not found")
        
        return {
            "success": True,
            "message": "Pool configuration updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update pool error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/pools/saved/{pool_id}")
async def delete_saved_pool(pool_id: str):
    """Delete a saved pool configuration"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        from bson import ObjectId
        
        result = await db.saved_pools.delete_one({"_id": ObjectId(pool_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Pool configuration not found")
        
        return {
            "success": True,
            "message": "Pool configuration deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Delete pool error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pools/saved/{pool_id}/use")
async def use_saved_pool(pool_id: str):
    """Mark a saved pool as recently used and return its configuration"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        from bson import ObjectId
        
        # Update last used timestamp
        result = await db.saved_pools.update_one(
            {"_id": ObjectId(pool_id)},
            {"$set": {"last_used": datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Pool configuration not found")
        
        # Get the updated pool configuration
        pool = await db.saved_pools.find_one({"_id": ObjectId(pool_id)})
        if not pool:
            raise HTTPException(status_code=404, detail="Pool configuration not found")
        
        # Convert to dict and format for mining config
        pool["_id"] = str(pool["_id"])
        
        return {
            "success": True,
            "pool": pool,
            "mining_config": {
                "coin": {
                    "symbol": pool["coin_symbol"],
                    "custom_pool_address": pool["pool_address"],
                    "custom_pool_port": pool["pool_port"]
                },
                "wallet_address": pool["wallet_address"],
                "pool_username": pool.get("pool_username", pool["wallet_address"]),
                "pool_password": pool["pool_password"],
                "mode": "pool"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Use saved pool error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CUSTOM COINS API ENDPOINTS
# ============================================================================

@app.get("/api/coins/custom")
async def get_custom_coins():
    """Get all custom coin configurations"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        coins = []
        async for coin in db.custom_coins.find().sort("name", 1):
            # Convert ObjectId to string for JSON serialization
            coin["_id"] = str(coin["_id"])
            coins.append(coin)
        
        return {"coins": coins, "count": len(coins)}
        
    except Exception as e:
        logger.error(f"Get custom coins error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/coins/custom")
async def create_custom_coin(coin: CustomCoin):
    """Create a new custom coin configuration"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        # Check if coin symbol already exists
        existing = await db.custom_coins.find_one({"symbol": coin.symbol.upper()})
        if existing:
            raise HTTPException(status_code=400, detail="Coin symbol already exists")
        
        coin_data = coin.dict()
        coin_data["symbol"] = coin_data["symbol"].upper()  # Normalize symbol
        coin_data["created_at"] = datetime.utcnow()
        coin_data["usage_count"] = 0
        
        result = await db.custom_coins.insert_one(coin_data)
        
        return {
            "success": True,
            "message": "Custom coin created successfully",
            "coin_id": str(result.inserted_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create custom coin error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/coins/custom/{coin_id}")
async def update_custom_coin(coin_id: str, coin: CustomCoin):
    """Update an existing custom coin configuration"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        from bson import ObjectId
        
        coin_data = coin.dict()
        coin_data["symbol"] = coin_data["symbol"].upper()  # Normalize symbol
        coin_data["updated_at"] = datetime.utcnow()
        
        result = await db.custom_coins.update_one(
            {"_id": ObjectId(coin_id)},
            {"$set": coin_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Custom coin not found")
        
        return {
            "success": True,
            "message": "Custom coin updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update custom coin error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/coins/custom/{coin_id}")
async def delete_custom_coin(coin_id: str):
    """Delete a custom coin configuration"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        from bson import ObjectId
        
        result = await db.custom_coins.delete_one({"_id": ObjectId(coin_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Custom coin not found")
        
        return {
            "success": True,
            "message": "Custom coin deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Delete custom coin error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/coins/all")
async def get_all_coins():
    """Get both preset and custom coins combined"""
    try:
        # Get preset coins
        presets = get_coin_presets()
        
        # Get custom coins
        custom_coins = []
        if db is not None:
            async for coin in db.custom_coins.find().sort("name", 1):
                coin["_id"] = str(coin["_id"])
                coin["is_custom"] = True
                custom_coins.append(coin)
        
        # Mark presets as not custom
        for preset in presets:
            preset["is_custom"] = False
        
        return {
            "preset_coins": presets,
            "custom_coins": custom_coins,
            "total_count": len(presets) + len(custom_coins)
        }
        
    except Exception as e:
        logger.error(f"Get all coins error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# V30 ENTERPRISE API ENDPOINTS
# ============================================================================

@app.post("/api/v30/license/validate")
async def validate_v30_license(request: dict):
    """Validate V30 Enterprise license key"""
    try:
        license_key = request.get("license_key")
        if not license_key:
            raise HTTPException(status_code=400, detail="License key required")
        
        validation = enterprise_license_system.validate_license(license_key)
        return validation
        
    except Exception as e:
        logger.error(f"License validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v30/license/activate")
async def activate_v30_license(request: dict):
    """Activate V30 Enterprise license"""
    try:
        license_key = request.get("license_key")
        node_info = request.get("node_info", {})
        
        if not license_key:
            raise HTTPException(status_code=400, detail="License key required")
        
        activation = enterprise_license_system.activate_license(license_key, node_info)
        return activation
        
    except Exception as e:
        logger.error(f"License activation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v30/hardware/validate")
async def validate_v30_hardware():
    """Validate enterprise hardware requirements"""
    try:
        validation_result = hardware_validator.comprehensive_validation()
        return validation_result
        
    except Exception as e:
        logger.error(f"Hardware validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v30/system/initialize")
async def initialize_v30_system():
    """Initialize V30 Enterprise system"""
    global v30_control_system
    
    try:
        if not v30_control_system:
            v30_control_system = CentralControlSystem()
        
        if v30_control_system.is_running:
            return {"success": True, "message": "V30 system already running"}
        
        init_result = await v30_control_system.initialize_system()
        return init_result
        
    except Exception as e:
        logger.error(f"V30 system initialization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v30/system/status")
async def get_v30_system_status():
    """Get V30 Enterprise system status"""
    try:
        if not v30_control_system:
            return {
                "initialized": False,
                "message": "V30 system not initialized"
            }
        
        status = v30_control_system.get_system_status()
        return status
        
    except Exception as e:
        logger.error(f"V30 system status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v30/mining/distributed/start")
async def start_v30_distributed_mining(request: dict):
    """Start V30 distributed mining"""
    global v30_control_system
    
    try:
        if not v30_control_system or not v30_control_system.is_running:
            raise HTTPException(
                status_code=400, 
                detail="V30 system not initialized. Call /api/v30/system/initialize first."
            )
        
        coin_config = request.get("coin_config", {})
        wallet_address = request.get("wallet_address", "")
        include_local = request.get("include_local", True)
        
        if not coin_config or not wallet_address:
            raise HTTPException(
                status_code=400, 
                detail="coin_config and wallet_address required"
            )
        
        result = await v30_control_system.start_distributed_mining(
            coin_config, wallet_address, include_local
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"V30 distributed mining start error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v30/mining/distributed/stop")
async def stop_v30_distributed_mining():
    """Stop V30 distributed mining"""
    global v30_control_system
    
    try:
        if not v30_control_system:
            raise HTTPException(status_code=400, detail="V30 system not initialized")
        
        result = await v30_control_system.stop_distributed_mining()
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"V30 distributed mining stop error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v30/nodes/list")
async def list_v30_nodes():
    """List all connected V30 mining nodes"""
    try:
        if not v30_control_system or not v30_control_system.distributed_server:
            return {"nodes": [], "total": 0}
        
        node_manager = v30_control_system.distributed_server.node_manager
        nodes_data = []
        
        for node_id, node_info in node_manager.nodes.items():
            nodes_data.append({
                "node_id": node_id,
                "hostname": node_info.hostname,
                "ip_address": node_info.ip_address,
                "status": node_info.status,
                "connected_time": node_info.connected_time,
                "last_heartbeat": node_info.last_heartbeat,
                "system_specs": node_info.system_specs,
                "capabilities": node_info.capabilities
            })
        
        return {
            "nodes": nodes_data,
            "total": len(nodes_data),
            "active": len([n for n in nodes_data if n["status"] == "connected"])
        }
        
    except Exception as e:
        logger.error(f"V30 nodes list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v30/stats/comprehensive")
async def get_v30_comprehensive_stats():
    """Get comprehensive V30 system statistics"""
    try:
        if not v30_control_system:
            return {"error": "V30 system not initialized"}
        
        # Force stats update
        await v30_control_system._update_system_stats()
        
        status = v30_control_system.get_system_status()
        return status
        
    except Exception as e:
        logger.error(f"V30 comprehensive stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v30/updates/remote-node")
async def get_remote_node_update():
    """Get latest remote node update information"""
    try:
        # In production, this would check actual versions and serve updates
        current_version = "1.0.0"
        latest_version = "1.0.0"
        
        update_info = {
            "current_version": current_version,
            "latest_version": latest_version,
            "update_available": False,
            "update_url": f"/api/v30/downloads/remote-node/{latest_version}",
            "changelog": [
                "Initial V30 remote node release",
                "Distributed mining support",
                "Automatic updates",
                "GPU detection",
                "Enterprise licensing"
            ],
            "requirements": {
                "min_python": "3.8",
                "min_server_version": "30.0.0"
            },
            "release_date": "2025-01-08",
            "size_bytes": 37282
        }
        
        return update_info
        
    except Exception as e:
        logger.error(f"Remote node update check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v30/downloads/remote-node/{version}")
async def download_remote_node(version: str):
    """Download remote node package"""
    try:
        # In production, this would serve the actual package file
        # For now, return download information
        
        if version == "1.0.0":
            return {
                "message": "Remote node download",
                "version": version,
                "filename": f"v30-remote-node-v{version}.tar.gz",
                "download_instructions": [
                    "1. Download the package from your V30 server",
                    "2. Extract: tar -xzf v30-remote-node-v1.0.0.tar.gz",
                    "3. Run installer: sudo ./install.sh", 
                    "4. Configure with your license key",
                    "5. Start the service: sudo systemctl start cryptominer-v30-node"
                ]
            }
        else:
            raise HTTPException(status_code=404, detail="Version not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Remote node download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# WEBSOCKET CONNECTION
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    connected_websockets.append(websocket)
    
    try:
        while True:
            # Send mining updates
            mining_status = mining_engine.get_mining_status()
            
            await websocket.send_json({
                "type": "mining_update",
                "timestamp": time.time(),
                "stats": mining_status["stats"],
                "is_mining": mining_status["is_mining"]
            })
            
            # Send system stats
            system_stats = await get_system_stats()
            await websocket.send_json({
                "type": "system_update", 
                "timestamp": time.time(),
                "data": system_stats
            })
            
            await asyncio.sleep(2)  # Update every 2 seconds
            
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
        reload=False,
        log_level="info"
    )