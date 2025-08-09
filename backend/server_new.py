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
DATABASE_NAME = os.getenv("DATABASE_NAME", "crypto_miner_db")

# Global variables
db_client: Optional[AsyncIOMotorClient] = None
db = None
connected_websockets: List[WebSocket] = []

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

class WalletAddress(BaseModel):
    address: str
    coin_symbol: str

# ============================================================================
# DATABASE SETUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database connection and AI system"""
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
        
        # Start AI system
        ai_system.start_ai_system()
        logger.info("AI system started")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup on shutdown"""
    global db_client
    
    # Stop mining
    if mining_engine.is_mining:
        mining_engine.stop_mining()
    
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
        "version": "2.0.0",
        "ai_system": ai_system.status.is_active,
        "mining_active": mining_engine.is_mining
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
    """Get detailed CPU information"""
    cpu_info = ai_system.get_cpu_info()
    return cpu_info

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