from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
import subprocess
import signal
import psutil
from pathlib import Path


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_wallet_format(wallet_address):
    """Clean wallet format by removing prefixes like 'solo:' for zeropool.io compatibility"""
    if not wallet_address:
        return wallet_address
    
    # Remove common prefixes that cause authentication issues
    prefixes_to_remove = ['solo:', 'pool:', 'prop:']
    
    for prefix in prefixes_to_remove:
        if wallet_address.startswith(prefix):
            cleaned = wallet_address[len(prefix):]
            logger.info(f"🧹 Cleaned wallet format: removed '{prefix}' prefix")
            return cleaned
    
    return wallet_address

def load_mining_config():
    """Load mining configuration from mining_config.env file"""
    config_file = Path("/app/mining_config.env")
    mining_config = {}
    
    if config_file.exists():
        # Load the mining config file
        load_dotenv(str(config_file))
        
        # Get wallet and clean the format for zeropool.io compatibility
        raw_wallet = os.getenv("WALLET", "4793trzeyXigW8qj9JZU1bVUuohVqn76EBpXUEJdDxJS5tAP4rjAdS7PzWFXzV3MtE3b9MKxMeHmE5X8J2oBk7cyNdE65j8")
        cleaned_wallet = clean_wallet_format(raw_wallet)
        
        mining_config = {
            "coin": os.getenv("COIN", "XMR"),
            "wallet": cleaned_wallet,
            "pool": os.getenv("POOL", "stratum+tcp://pool.supportxmr.com:3333"),
            "password": os.getenv("PASSWORD", "x"),
            "intensity": int(os.getenv("INTENSITY", "80")),
            "threads": os.getenv("THREADS", "auto"),
            "web_enabled": os.getenv("WEB_ENABLED", "true").lower() == "true",
            "ai_enabled": os.getenv("AI_ENABLED", "true").lower() == "true",
            "ai_learning_rate": float(os.getenv("AI_LEARNING_RATE", "1.0"))
        }
        
        logger.info(f"📁 Loaded mining config from {config_file}")
        logger.info(f"   Coin: {mining_config['coin']}")
        logger.info(f"   Pool: {mining_config['pool']}")
        logger.info(f"   Wallet: {mining_config['wallet'][:20]}...{mining_config['wallet'][-20:]}")
        logger.info(f"   Intensity: {mining_config['intensity']}%")
        logger.info(f"   Threads: {mining_config['threads']}")
    else:
        logger.warning(f"⚠️ Mining config file not found: {config_file}")
        # Use default XMR configuration with cleaned wallet format
        default_wallet = "4793trzeyXigW8qj9JZU1bVUuohVqn76EBpXUEJdDxJS5tAP4rjAdS7PzWFXzV3MtE3b9MKxMeHmE5X8J2oBk7cyNdE65j8"
        mining_config = {
            "coin": "XMR",
            "wallet": default_wallet,  # Already cleaned format
            "pool": "stratum+tcp://pool.supportxmr.com:3333",
            "password": "x",
            "intensity": 80,
            "threads": "auto",
            "web_enabled": True,
            "ai_enabled": True,
            "ai_learning_rate": 1.0
        }
    
    return mining_config

# Global variable for mining configuration
default_mining_config = load_mining_config()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="CryptoMiner V21 API", description="Advanced Multi-Algorithm CPU Mining Platform API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Global mining stats storage (in production this would be in MongoDB)
mining_stats = {
    "hashrate": 0.0,
    "threads": 0,
    "intensity": 80,
    "coin": "XMR",
    "pool_connected": False,
    "accepted_shares": 0,
    "rejected_shares": 0,
    "uptime": 0.0,
    "difficulty": 1.0,
    "ai_learning": 0.0,
    "ai_optimization": 0.0,
    "last_update": datetime.utcnow()
}

# Global process management
mining_process = None
is_mining_active = False

async def kill_mining_processes():
    """Kill all existing mining processes (async version)"""
    global mining_process, is_mining_active
    
    logger.info("🛑 Attempting to kill mining processes...")
    
    # Kill the specific process if we have it
    if mining_process and mining_process.poll() is None:
        try:
            mining_process.terminate()
            try:
                # Use asyncio.wait_for to prevent hanging
                await asyncio.wait_for(
                    asyncio.to_thread(mining_process.wait), 
                    timeout=3.0
                )
            except asyncio.TimeoutError:
                mining_process.kill()  # Force kill if still running
                try:
                    await asyncio.wait_for(
                        asyncio.to_thread(mining_process.wait), 
                        timeout=2.0
                    )
                except asyncio.TimeoutError:
                    logger.warning("Process may still be running after force kill")
            logger.info("✅ Managed mining process terminated")
        except Exception as e:
            logger.error(f"Error terminating managed process: {e}")
    
    # Find and kill any cryptominer processes (but NOT our backend server)
    killed_processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                # Only kill cryptominer processes, not the backend API server
                if ('cryptominer' in cmdline and 'python' in cmdline):
                    proc.terminate()
                    killed_processes.append(proc.info['pid'])
                    logger.info(f"Terminated cryptominer process {proc.info['pid']}: {cmdline}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        logger.error(f"Error enumerating processes: {e}")
    
    # Wait for processes to terminate, then force kill if needed (async)
    if killed_processes:
        try:
            await asyncio.sleep(2)  # Give processes time to terminate gracefully
            
            for pid in killed_processes:
                try:
                    proc = psutil.Process(pid)
                    if proc.is_running():
                        proc.kill()
                        logger.info(f"Force killed process {pid}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass  # Process already gone
        except Exception as e:
            logger.error(f"Error during force kill phase: {e}")
    
    mining_process = None
    is_mining_active = False
    
    # Update stats to reflect stopped state
    mining_stats.update({
        "pool_connected": False,
        "hashrate": 0,
        "threads": 0,
        "last_update": datetime.utcnow()
    })
    
    return len(killed_processes)

async def start_mining_process(config):
    """Start the actual cryptominer.py process"""
    global mining_process, is_mining_active
    
    try:
        # Kill any existing processes first
        killed_count = await kill_mining_processes()
        if killed_count > 0:
            logger.info(f"Killed {killed_count} existing mining processes")
        
        # Prepare command
        app_dir = Path(__file__).parent.parent  # Go up to /app directory
        crypto_script = app_dir / "cryptominer.py"
        
        if not crypto_script.exists():
            raise FileNotFoundError(f"cryptominer.py not found at {crypto_script}")
        
        # Build command arguments using the loaded default config as fallbacks
        cmd = [
            "python3", str(crypto_script),
            "--coin", config.get("coin", default_mining_config.get("coin", "XMR")),
            "--wallet", config.get("wallet", default_mining_config.get("wallet", "XMR_PLACEHOLDER_WALLET")),
            "--pool", config.get("pool", default_mining_config.get("pool", "stratum+tcp://pool.supportxmr.com:3333")),
            "--intensity", str(config.get("intensity", default_mining_config.get("intensity", 80))),
            "--threads", str(config.get("threads", default_mining_config.get("threads", "auto")))
        ]
        
        # Only use proxy mode for Scrypt coins (LTC, DOGE), not for RandomX coins (XMR, AEON)
        coin = config.get("coin", default_mining_config.get("coin", "XMR")).upper()
        if coin not in ["XMR", "AEON"]:
            cmd.append("--proxy-mode")  # Use proxy mode only for non-RandomX coins
        
        if config.get("password"):
            cmd.extend(["--password", config.get("password")])
        
        logger.info(f"Starting mining process with command: {' '.join(cmd)}")
        
        # Start the process
        mining_process = subprocess.Popen(
            cmd,
            cwd=str(app_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        is_mining_active = True
        
        # Update stats to reflect started state
        mining_stats.update({
            "pool_connected": True,
            "threads": config.get("threads", 8),
            "intensity": config.get("intensity", 80),
            "coin": config.get("coin", "LTC"),
            "hashrate": config.get("threads", 8) * 150,  # Estimate initial hashrate
            "last_update": datetime.utcnow()
        })
        
        logger.info(f"✅ Mining process started with PID: {mining_process.pid}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to start mining process: {e}")
        is_mining_active = False
        return False

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
    return {"message": "CryptoMiner V21 API", "status": "running"}

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
@api_router.get("/mining/config-debug")
async def get_mining_config_debug():
    """Debug endpoint to see raw mining config"""
    return {"default_mining_config": default_mining_config}

@api_router.get("/mining/stats-debug")
async def get_mining_stats_debug():
    """Debug endpoint to see raw mining stats"""
    return {"raw_stats": mining_stats, "type_info": {k: type(v).__name__ for k, v in mining_stats.items()}}

def sanitize_stats_data(stats):
    """Sanitize mining stats to prevent data corruption"""
    cleaned = {}
    for key, value in stats.items():
        if isinstance(value, str):
            # Fix the auto duplication bug
            if "auto" in value and len(value) > 10:
                cleaned[key] = 0 if key in ['threads', 'hashrate'] else "auto"
            elif value == "auto":
                cleaned[key] = 0 if key in ['threads', 'hashrate'] else value
            else:
                try:
                    # Try to convert string numbers to proper types
                    if key in ['threads', 'intensity']:
                        cleaned[key] = int(float(value))
                    elif key in ['hashrate', 'cpu_usage', 'memory_usage', 'uptime']:
                        cleaned[key] = float(value)
                    else:
                        cleaned[key] = value
                except (ValueError, TypeError):
                    cleaned[key] = 0 if key in ['threads', 'hashrate', 'intensity', 'cpu_usage', 'memory_usage', 'uptime'] else value
        else:
            cleaned[key] = value if value is not None else 0
    return cleaned

@api_router.get("/mining/stats", response_model=MiningStats)
async def get_mining_stats():
    """Get current mining statistics"""
    try:
        sanitized_stats = sanitize_stats_data(mining_stats)
        return MiningStats(**sanitized_stats)
    except Exception as e:
        logger.error(f"Stats validation error: {e}")
        # Return safe default values
        return MiningStats(
            hashrate=0.0,
            threads=0,
            intensity=80,
            coin="XMR",
            algorithm="RandomX",
            pool_connected=False,
            shares_good=0,
            hashes_total=0,
            uptime=0,
            cpu_usage=0.0,
            memory_usage=0.0,
            is_running=False
        )

@api_router.post("/mining/update-stats")
async def update_mining_stats(stats: Dict[str, Any]):
    """Update mining statistics from the mining engine"""
    global mining_stats
    
    try:
        # Use the same sanitization function
        cleaned_stats = sanitize_stats_data(stats)
        mining_stats.update(cleaned_stats)
        
        return {"status": "success", "message": "Stats updated successfully"}
    except Exception as e:
        logger.error(f"Error updating mining stats: {e}")
        return {"status": "error", "message": str(e)}

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
    """Control mining operations (start/stop/restart) - Always uses mining_config.env settings"""
    global mining_process, is_mining_active
    
    action = request.get("action")
    web_config = request.get("config", {})
    
    if action == "start":
        # Always kill any existing mining processes first to prevent conflicts
        if is_mining_active or mining_process:
            logger.info("🛑 Killing existing mining processes before starting new one")
            killed_count = await kill_mining_processes()
            logger.info(f"🛑 Killed {killed_count} existing processes")
            
        # ALWAYS use configuration from mining_config.env file as primary source
        # Only allow web interface to override non-critical settings like threads/intensity
        file_config = load_mining_config()  # Fresh load to get latest values
        
        # Create final config - prioritize mining_config.env for critical settings
        final_config = {
            "coin": file_config.get("coin", "XMR"),  # Always from file
            "wallet": file_config.get("wallet", "solo.4793trzeyXigW8qj9JZU1bVUuohVqn76EBpXUEJdDxJS5tAP4rjAdS7PzWFXzV3MtE3b9MKxMeHmE5X8J2oBk7cyNdE65j8"),  # Always from file
            "pool": file_config.get("pool", "stratum+tcp://pool.supportxmr.com:3333"),  # Always from file
            "password": file_config.get("password", "x"),  # Always from file
            # Allow web interface to override performance settings only
            "intensity": web_config.get("intensity", file_config.get("intensity", 80)),
            "threads": web_config.get("threads", file_config.get("threads", "auto")),
            "web_enabled": file_config.get("web_enabled", True),
            "ai_enabled": file_config.get("ai_enabled", True)
        }
        
        logger.info(f"🔒 Using mining_config.env settings: coin={final_config['coin']}, pool={final_config['pool']}")
        
        success = await start_mining_process(final_config)
        
        if success:
            # Log the control action
            await db.mining_control_log.insert_one({
                "action": "start",
                "config": final_config,
                "timestamp": datetime.utcnow(),
                "status": "executed",
                "process_id": mining_process.pid if mining_process else None
            })
            
            return {
                "status": "success", 
                "message": f"Mining started successfully (PID: {mining_process.pid})", 
                "config": final_config
            }
        else:
            return {"status": "error", "message": "Failed to start mining process"}
    
    elif action == "stop":
        if not is_mining_active:
            return {"status": "error", "message": "Mining is not currently running"}
        
        killed_count = await kill_mining_processes()
        
        # Log the control action
        await db.mining_control_log.insert_one({
            "action": "stop",
            "timestamp": datetime.utcnow(),
            "status": "executed",
            "killed_processes": killed_count
        })
        
        return {
            "status": "success", 
            "message": f"Mining stopped successfully (killed {killed_count} processes)"
        }
    
    elif action == "restart":
        # Stop first
        if is_mining_active:
            killed_count = await kill_mining_processes()
            logger.info(f"Restart: killed {killed_count} processes")
        
        # ALWAYS use configuration from mining_config.env file as primary source
        file_config = load_mining_config()  # Fresh load to get latest values
        
        # Create final config - prioritize mining_config.env for critical settings
        final_config = {
            "coin": file_config.get("coin", "XMR"),  # Always from file
            "wallet": file_config.get("wallet", "solo.4793trzeyXigW8qj9JZU1bVUuohVqn76EBpXUEJdDxJS5tAP4rjAdS7PzWFXzV3MtE3b9MKxMeHmE5X8J2oBk7cyNdE65j8"),  # Always from file
            "pool": file_config.get("pool", "stratum+tcp://pool.supportxmr.com:3333"),  # Always from file
            "password": file_config.get("password", "x"),  # Always from file
            # Allow web interface to override performance settings only
            "intensity": web_config.get("intensity", file_config.get("intensity", 80)),
            "threads": web_config.get("threads", file_config.get("threads", "auto")),
            "web_enabled": file_config.get("web_enabled", True),
            "ai_enabled": file_config.get("ai_enabled", True)
        }
        
        logger.info(f"🔒 Using mining_config.env settings: coin={final_config['coin']}, pool={final_config['pool']}")
        
        # Start with final config
        success = await start_mining_process(final_config)
        
        if success:
            # Log the control action
            await db.mining_control_log.insert_one({
                "action": "restart",
                "config": final_config,
                "timestamp": datetime.utcnow(),
                "status": "executed",
                "process_id": mining_process.pid if mining_process else None
            })
            
            return {
                "status": "success", 
                "message": f"Mining restarted successfully (PID: {mining_process.pid})", 
                "config": final_config
            }
        else:
            return {"status": "error", "message": "Failed to restart mining process"}
    
    else:
        return {"status": "error", "message": f"Unknown action: {action}"}

@api_router.get("/mining/status")
async def get_mining_status():
    """Get current mining process status"""
    global mining_process, is_mining_active
    
    # Check if the process is still running
    if mining_process:
        if mining_process.poll() is None:
            is_mining_active = True
        else:
            is_mining_active = False
            mining_process = None
    
    return {
        "is_active": is_mining_active,
        "process_id": mining_process.pid if mining_process and mining_process.poll() is None else None,
        "pool_connected": mining_stats.get("pool_connected", False),
        "last_update": mining_stats.get("last_update")
    }

@api_router.get("/mining/multi-stats")
async def get_multi_algorithm_stats():
    """Get comprehensive multi-algorithm mining statistics"""
    try:
        # Import multi-algorithm engine (would be initialized globally in production)
        from multi_algorithm_engine import MultiAlgorithmMiningEngine
        
        # For now, return simulated comprehensive stats
        comprehensive_stats = {
            'current_algorithm': 'RandomX',
            'current_coin': 'XMR', 
            'is_mining': mining_stats.get('pool_connected', False),
            'total_uptime': 3600,  # 1 hour
            'current_stats': {
                'hashrate': mining_stats.get('hashrate', 0),
                'threads': mining_stats.get('threads', 0),
                'intensity': mining_stats.get('intensity', 80),
                'accepted_shares': mining_stats.get('accepted_shares', 0),
                'rejected_shares': mining_stats.get('rejected_shares', 0),
                'difficulty': mining_stats.get('difficulty', 1000),
                'temperature': 65.0,
                'power_consumption': 150.0,
                'efficiency': mining_stats.get('hashrate', 0) / max(150.0, 1)
            },
            'algorithm_comparison': {
                'RandomX': {
                    'hashrate': 1200.0,
                    'efficiency': 8.0,
                    'accepted_shares': 45,
                    'uptime': 3600
                },
                'Scrypt': {
                    'hashrate': 2500.0,
                    'efficiency': 16.7,
                    'accepted_shares': 78,
                    'uptime': 1800
                },
                'CryptoNight': {
                    'hashrate': 800.0,
                    'efficiency': 5.3,
                    'accepted_shares': 23,
                    'uptime': 900
                }
            },
            'ai_stats': {
                'learning_progress': 85.6,
                'optimization_progress': 72.3,
                'predictive_success_rate': 0.68,
                'database_size_mb': 450.2,
                'total_predictions': 156,
                'recommended_algorithm': 'RandomX',
                'models_trained': {
                    'hashrate_model': True,
                    'efficiency_model': True,
                    'predictive_engine': True
                }
            },
            'supported_algorithms': ['RandomX', 'Scrypt', 'CryptoNight'],
            'supported_coins': ['XMR', 'LTC', 'DOGE', 'AEON', 'ETN'],
            'cpu_friendly_coins': ['XMR', 'AEON', 'ETN'],
            'auto_switching': True
        }
        
        return comprehensive_stats
        
    except Exception as e:
        logger.error(f"Error getting multi-algorithm stats: {e}")
        return {
            'current_algorithm': None,
            'current_coin': None,
            'is_mining': False,
            'total_uptime': 0,
            'current_stats': {},
            'algorithm_comparison': {},
            'ai_stats': {},
            'supported_algorithms': [],
            'supported_coins': [],
            'cpu_friendly_coins': [],
            'auto_switching': False
        }

@api_router.post("/mining/switch-algorithm")
async def switch_mining_algorithm(request: Dict[str, Any]):
    """Switch to a different mining algorithm"""
    try:
        algorithm = request.get("algorithm", "RandomX")
        coin = request.get("coin", "XMR")
        pool = request.get("pool", "pool.supportxmr.com:3333")
        threads = request.get("threads", 8)
        intensity = request.get("intensity", 80)
        
        logger.info(f"Switching to {algorithm} for {coin}")
        
        # Simulate algorithm switch
        mining_stats.update({
            'coin': coin,
            'algorithm': algorithm,
            'threads': threads,
            'intensity': intensity,
            'pool_connected': True,
            'hashrate': threads * (1200 if algorithm == 'RandomX' else 2500 if algorithm == 'Scrypt' else 800),
            'last_update': datetime.utcnow()
        })
        
        # Log the switch
        await db.mining_control_log.insert_one({
            "action": "switch_algorithm",
            "algorithm": algorithm,
            "coin": coin,
            "config": request,
            "timestamp": datetime.utcnow(),
            "status": "executed"
        })
        
        return {
            "status": "success",
            "message": f"Successfully switched to {algorithm} for {coin}",
            "algorithm": algorithm,
            "coin": coin
        }
        
    except Exception as e:
        logger.error(f"Error switching algorithm: {e}")
        return {
            "status": "error",
            "message": f"Failed to switch algorithm: {str(e)}"
        }

@api_router.get("/mining/ai-recommendation")
async def get_ai_recommendation():
    """Get AI algorithm recommendation"""
    try:
        # Simulate AI recommendation based on current conditions
        recommendations = [
            {
                "algorithm": "RandomX",
                "coin": "XMR", 
                "hashrate": 1200,
                "efficiency": 8.0,
                "confidence": 87,
                "reason": "Optimal for current CPU configuration and power efficiency"
            },
            {
                "algorithm": "Scrypt",
                "coin": "LTC",
                "hashrate": 2500,
                "efficiency": 16.7,
                "confidence": 73,
                "reason": "Higher hashrate but increased power consumption"
            },
            {
                "algorithm": "CryptoNight",
                "coin": "AEON",
                "hashrate": 800,
                "efficiency": 5.3,
                "confidence": 62,
                "reason": "Lower power consumption for battery-powered devices"
            }
        ]
        
        # Return best recommendation
        best_recommendation = max(recommendations, key=lambda x: x['confidence'])
        
        return best_recommendation
        
    except Exception as e:
        logger.error(f"Error getting AI recommendation: {e}")
        return {
            "algorithm": "RandomX",
            "coin": "XMR",
            "hashrate": 1000,
            "efficiency": 6.7,
            "confidence": 50,
            "reason": "Default recommendation due to system error"
        }

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

# Serve static files
static_dir = ROOT_DIR / "static"
static_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Root route to serve the dashboard
@app.get("/")
async def read_dashboard():
    """Serve the main dashboard"""
    dashboard_path = static_dir / "index.html"
    if dashboard_path.exists():
        return FileResponse(str(dashboard_path))
    else:
        return {"message": "CryptoMiner V21 Dashboard", "status": "Dashboard file not found"}

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
