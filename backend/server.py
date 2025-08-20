from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import json
import asyncio


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="CryptoMiner Pro V30 API", description="Enterprise Mining Platform API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Global mining stats storage (in production this would be in MongoDB)
mining_stats = {
    "hashrate": 0,
    "threads": 0,
    "intensity": 80,
    "coin": "LTC",
    "pool_connected": False,
    "accepted_shares": 0,
    "rejected_shares": 0,
    "uptime": 0,
    "difficulty": 1,
    "ai_learning": 0,
    "ai_optimization": 0,
    "last_update": datetime.utcnow()
}

# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class MiningStats(BaseModel):
    hashrate: float
    threads: int
    intensity: int
    coin: str
    pool_connected: bool
    accepted_shares: int
    rejected_shares: int
    uptime: float
    difficulty: float
    ai_learning: float
    ai_optimization: float
    last_update: datetime

class MiningConfig(BaseModel):
    coin: Optional[str] = None
    intensity: Optional[int] = None
    threads: Optional[int] = None

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "CryptoMiner Pro V30 API", "status": "running"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# CryptoMiner Pro V30 API endpoints
@api_router.get("/mining/stats", response_model=MiningStats)
async def get_mining_stats():
    """Get current mining statistics"""
    return MiningStats(**mining_stats)

@api_router.post("/mining/update-stats")
async def update_mining_stats(stats: Dict[str, Any]):
    """Update mining statistics from the mining engine"""
    global mining_stats
    
    # Update stats with provided data
    mining_stats.update(stats)
    mining_stats["last_update"] = datetime.utcnow()
    
    # Store in MongoDB for history
    await db.mining_stats.insert_one({
        **stats,
        "timestamp": datetime.utcnow()
    })
    
    return {"status": "updated"}

@api_router.get("/mining/config")
async def get_mining_config():
    """Get current mining configuration"""
    return {
        "coin": mining_stats.get("coin", "LTC"),
        "intensity": mining_stats.get("intensity", 80),
        "threads": mining_stats.get("threads", 4)
    }

@api_router.post("/mining/config")
async def update_mining_config(config: MiningConfig):
    """Update mining configuration"""
    global mining_stats
    
    if config.coin:
        mining_stats["coin"] = config.coin
    if config.intensity is not None:
        mining_stats["intensity"] = config.intensity  
    if config.threads is not None:
        mining_stats["threads"] = config.threads
    
    return {"status": "config updated", "config": config.dict()}

@api_router.get("/mining/history")
async def get_mining_history(limit: int = 100):
    """Get mining statistics history"""
    history = await db.mining_stats.find().sort("timestamp", -1).limit(limit).to_list(limit)
    
    # Convert ObjectId to string for JSON serialization
    for record in history:
        if '_id' in record:
            record['_id'] = str(record['_id'])
    
    return history

@api_router.get("/mining/coins")
async def get_available_coins():
    """Get list of available coins for mining"""
    return {
        "coins": [
            {"symbol": "LTC", "name": "Litecoin", "algorithm": "Scrypt"},
            {"symbol": "DOGE", "name": "Dogecoin", "algorithm": "Scrypt"},
            {"symbol": "VTC", "name": "Vertcoin", "algorithm": "Scrypt"},
            {"symbol": "XMR", "name": "Monero", "algorithm": "RandomX"}
        ]
    }

@api_router.post("/mining/control")
async def control_mining(request: Dict[str, Any]):
    """Control mining operations (start/stop/restart)"""
    action = request.get("action")
    config = request.get("config", {})
    
    if action == "start":
        # In a real implementation, this would start the mining process
        # For now, we'll simulate the response
        mining_stats.update({
            "pool_connected": True,
            "threads": config.get("threads", 8),
            "intensity": config.get("intensity", 80),
            "hashrate": config.get("threads", 8) * 150,  # Simulate hashrate
            "last_update": datetime.utcnow()
        })
        
        # Log the control action
        await db.mining_control_log.insert_one({
            "action": "start",
            "config": config,
            "timestamp": datetime.utcnow(),
            "status": "executed"
        })
        
        return {"status": "success", "message": "Mining started successfully", "config": config}
    
    elif action == "stop":
        mining_stats.update({
            "pool_connected": False,
            "hashrate": 0,
            "last_update": datetime.utcnow()
        })
        
        # Log the control action
        await db.mining_control_log.insert_one({
            "action": "stop",
            "timestamp": datetime.utcnow(),
            "status": "executed"
        })
        
        return {"status": "success", "message": "Mining stopped successfully"}
    
    elif action == "restart":
        # Simulate restart by resetting stats
        mining_stats.update({
            "pool_connected": True,
            "accepted_shares": 0,
            "rejected_shares": 0,
            "uptime": 0,
            "last_update": datetime.utcnow()
        })
        
        # Log the control action
        await db.mining_control_log.insert_one({
            "action": "restart",
            "config": config,
            "timestamp": datetime.utcnow(),
            "status": "executed"
        })
        
        return {"status": "success", "message": "Mining restarted successfully"}
    
    else:
        return {"status": "error", "message": f"Unknown action: {action}"}

@api_router.get("/mining/control-log")
async def get_control_log(limit: int = 50):
    """Get mining control action log"""
    log_entries = await db.mining_control_log.find().sort("timestamp", -1).limit(limit).to_list(limit)
    
    # Convert ObjectId to string for JSON serialization
    for entry in log_entries:
        if '_id' in entry:
            entry['_id'] = str(entry['_id'])
    
    return log_entries

@api_router.get("/mining/pools")
async def get_popular_pools():
    """Get list of popular mining pools"""
    return {
        "pools": [
            {"name": "LitecoinPool", "url": "stratum+tcp://stratum.litecoinpool.org:3333", "coin": "LTC"},
            {"name": "Prohashing", "url": "stratum+tcp://prohashing.com:3333", "coin": "MULTI"},
            {"name": "F2Pool", "url": "stratum+tcp://ltc.f2pool.com:4444", "coin": "LTC"},
            {"name": "ViaBTC", "url": "stratum+tcp://ltc.viabtc.com:3333", "coin": "LTC"}
        ]
    }

@api_router.get("/system/info")
async def get_system_info():
    """Get system information"""
    import psutil
    
    return {
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
        "disk_usage": psutil.disk_usage('/').percent,
        "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
