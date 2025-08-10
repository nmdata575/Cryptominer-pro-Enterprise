#!/usr/bin/env python3
"""
CryptoMiner V30 Remote Node
Lightweight terminal-based mining node that connects to V30 central server
"""

import asyncio
import json
import time
import hashlib
import socket
import sys
import os
import signal
import logging
import platform
import psutil
import struct
import zlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class NodeConfig:
    """Configuration for the remote mining node"""
    node_id: str
    server_host: str
    server_port: int
    license_key: str
    max_cpu_threads: int
    enable_gpu: bool
    heartbeat_interval: float
    work_request_interval: float
    auto_update: bool
    update_check_interval: float

class V30ProtocolClient:
    """Client implementation of V30 protocol for remote nodes"""
    
    MAGIC_BYTES = b'\x43\x4D\x50\x33'  # CMP3
    VERSION = 1
    HEADER_SIZE = 16
    
    def __init__(self):
        self.reader = None
        self.writer = None
        self.connected = False
    
    async def connect(self, host: str, port: int) -> bool:
        """Connect to V30 server"""
        try:
            self.reader, self.writer = await asyncio.open_connection(host, port)
            self.connected = True
            logger.info(f"✅ Connected to V30 server at {host}:{port}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to {host}:{port}: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from server"""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        self.connected = False
        logger.info("🔌 Disconnected from V30 server")
    
    def create_message(self, msg_type: int, data: Dict[str, Any], compress: bool = True) -> bytes:
        """Create a V30 protocol message"""
        try:
            # Serialize payload
            json_data = json.dumps(data, separators=(',', ':'))
            payload = json_data.encode('utf-8')
            
            # Compress if enabled and payload is large
            compressed = False
            if compress and len(payload) > 256:
                compressed_payload = zlib.compress(payload, level=6)
                if len(compressed_payload) < len(payload):
                    payload = compressed_payload
                    compressed = True
            
            # Calculate payload hash
            payload_hash = hashlib.sha256(payload).digest()[:4]
            
            # Create header
            flags = 0x01 if compressed else 0x00
            header = struct.pack(
                '<4s B B H I 4s',
                self.MAGIC_BYTES,
                self.VERSION,
                msg_type,
                flags,
                len(payload),
                payload_hash
            )
            
            return header + payload
            
        except Exception as e:
            logger.error(f"Failed to create message: {e}")
            return b''
    
    async def send_message(self, msg_type: int, data: Dict[str, Any]) -> bool:
        """Send message to server"""
        if not self.connected or not self.writer:
            return False
        
        try:
            message = self.create_message(msg_type, data)
            if not message:
                return False
            
            self.writer.write(message)
            await self.writer.drain()
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    async def receive_message(self) -> Tuple[Optional[int], Optional[Dict], str]:
        """Receive message from server"""
        if not self.connected or not self.reader:
            return None, None, "Not connected"
        
        try:
            # Read header
            header_data = await self.reader.readexactly(self.HEADER_SIZE)
            if not header_data:
                return None, None, "Connection closed"
            
            # Parse header
            header = struct.unpack('<4s B B H I 4s', header_data)
            magic, version, msg_type, flags, payload_len, payload_hash = header
            
            # Validate
            if magic != self.MAGIC_BYTES:
                return None, None, "Invalid magic bytes"
            
            if version != self.VERSION:
                return None, None, f"Unsupported version: {version}"
            
            # Read payload
            payload = await self.reader.readexactly(payload_len)
            
            # Verify hash
            calculated_hash = hashlib.sha256(payload).digest()[:4]
            if calculated_hash != payload_hash:
                return None, None, "Payload hash mismatch"
            
            # Decompress if needed
            if flags & 0x01:
                try:
                    payload = zlib.decompress(payload)
                except Exception as e:
                    return None, None, f"Decompression failed: {e}"
            
            # Parse JSON
            try:
                json_data = json.loads(payload.decode('utf-8'))
                return msg_type, json_data, ""
            except json.JSONDecodeError as e:
                return None, None, f"JSON parse error: {e}"
                
        except Exception as e:
            return None, None, f"Receive error: {e}"

class SystemAnalyzer:
    """Analyzes local system capabilities"""
    
    def __init__(self):
        self.node_id = self._generate_node_id()
        self.hostname = platform.node()
        self.os_info = self._get_os_info()
    
    def _generate_node_id(self) -> str:
        """Generate unique node ID"""
        mac_address = hex(uuid.getnode())[2:].upper()
        hostname = platform.node()[:8]
        timestamp = str(int(time.time()))[-6:]
        return f"NODE-{hostname}-{mac_address[-6:]}-{timestamp}"
    
    def _get_os_info(self) -> Dict[str, str]:
        """Get operating system information"""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor()
        }
    
    def get_system_capabilities(self) -> Dict[str, Any]:
        """Get comprehensive system capabilities"""
        # CPU information
        logical_cores = psutil.cpu_count(logical=True)
        physical_cores = psutil.cpu_count(logical=False) or logical_cores
        cpu_freq = psutil.cpu_freq()
        
        # Memory information
        memory = psutil.virtual_memory()
        
        # Disk information
        disk = psutil.disk_usage('/')
        
        # Network interfaces
        network_stats = psutil.net_if_stats()
        max_network_speed = 0
        active_interfaces = []
        
        for interface, stats in network_stats.items():
            if stats.isup and stats.speed > 0:
                max_network_speed = max(max_network_speed, stats.speed)
                active_interfaces.append({
                    "name": interface,
                    "speed_mbps": stats.speed
                })
        
        # GPU detection (simplified)
        gpus = self._detect_gpus()
        
        return {
            "node_id": self.node_id,
            "hostname": self.hostname,
            "os_info": self.os_info,
            "cpu": {
                "logical_cores": logical_cores,
                "physical_cores": physical_cores,
                "frequency_mhz": cpu_freq.max if cpu_freq else 0,
                "architecture": platform.architecture()[0]
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percentage_used": memory.percent
            },
            "storage": {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percentage_used": round((disk.used / disk.total) * 100, 1)
            },
            "network": {
                "max_speed_mbps": max_network_speed,
                "max_speed_gbps": round(max_network_speed / 1000, 2),
                "active_interfaces": len(active_interfaces)
            },
            "gpus": gpus,
            "capabilities": {
                "cpu_mining": True,
                "gpu_mining": len(gpus) > 0,
                "total_processing_units": logical_cores + len(gpus),
                "estimated_hashpower": self._estimate_hashpower(logical_cores, len(gpus))
            }
        }
    
    def _detect_gpus(self) -> List[Dict[str, Any]]:
        """Detect available GPUs"""
        gpus = []
        
        # Try NVIDIA first
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', 
                                   '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        parts = [part.strip() for part in line.split(',')]
                        if len(parts) >= 2:
                            gpus.append({
                                "id": i,
                                "type": "NVIDIA",
                                "name": parts[0],
                                "memory_mb": int(parts[1]) if parts[1].isdigit() else 0
                            })
        except:
            pass
        
        # Try AMD (simplified)
        try:
            result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                amd_count = 0
                for line in result.stdout.split('\n'):
                    if 'VGA' in line and ('AMD' in line or 'ATI' in line or 'Radeon' in line):
                        gpus.append({
                            "id": len(gpus),
                            "type": "AMD",
                            "name": f"AMD GPU {amd_count}",
                            "memory_mb": 0
                        })
                        amd_count += 1
        except:
            pass
        
        return gpus
    
    def _estimate_hashpower(self, cpu_cores: int, gpu_count: int) -> int:
        """Estimate mining hashpower"""
        # Simplified estimation: CPU cores * base rate + GPU boost
        cpu_hashpower = cpu_cores * 1000  # 1000 H/s per core (rough estimate)
        gpu_hashpower = gpu_count * 10000  # 10,000 H/s per GPU (rough estimate)
        return cpu_hashpower + gpu_hashpower

class MiningWorker:
    """Handles actual mining work"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.is_mining = False
        self.current_work = None
        self.mining_task = None
        self.stats = {
            "hashes_computed": 0,
            "shares_found": 0,
            "uptime": 0,
            "start_time": None
        }
    
    def start_mining(self, work_data: Dict[str, Any]) -> bool:
        """Start mining with given work"""
        if self.is_mining:
            return False
        
        self.current_work = work_data
        self.is_mining = True
        self.stats["start_time"] = time.time()
        self.stats["hashes_computed"] = 0
        self.stats["shares_found"] = 0
        
        # Start mining task
        self.mining_task = asyncio.create_task(self._mining_loop())
        
        logger.info(f"🚀 Mining started - Work ID: {work_data.get('work_id', 'unknown')}")
        return True
    
    def stop_mining(self) -> bool:
        """Stop mining"""
        if not self.is_mining:
            return False
        
        self.is_mining = False
        if self.mining_task:
            self.mining_task.cancel()
        
        logger.info("🛑 Mining stopped")
        return True
    
    async def _mining_loop(self):
        """Main mining loop"""
        try:
            work = self.current_work
            coin_config = work.get("coin_config", {})
            wallet_address = work.get("wallet_address", "")
            start_nonce = work.get("start_nonce", 0)
            nonce_range = work.get("nonce_range", 10000)
            
            logger.info(f"⛏️ Mining {coin_config.get('name', 'Unknown')} coin")
            logger.info(f"📊 Nonce range: {start_nonce} - {start_nonce + nonce_range}")
            
            # Simple mining simulation
            for nonce_offset in range(nonce_range):
                if not self.is_mining:
                    break
                
                nonce = start_nonce + nonce_offset
                timestamp = int(time.time())
                
                # Create work data
                header_data = f"{wallet_address}{timestamp}{nonce}".encode('utf-8')
                
                # Simple hash calculation (in production this would be Scrypt)
                hash_result = hashlib.sha256(header_data).hexdigest()
                self.stats["hashes_computed"] += 1
                
                # Check if we found a share (simplified)
                if hash_result.startswith("0000"):
                    self.stats["shares_found"] += 1
                    logger.info(f"🎯 Share found! Hash: {hash_result[:16]}...")
                
                # Update uptime
                if self.stats["start_time"]:
                    self.stats["uptime"] = time.time() - self.stats["start_time"]
                
                # Don't overwhelm the system
                if nonce_offset % 1000 == 0:
                    await asyncio.sleep(0.001)
            
            logger.info(f"✅ Mining work completed - {self.stats['hashes_computed']} hashes, {self.stats['shares_found']} shares")
            
        except asyncio.CancelledError:
            logger.info("🛑 Mining task cancelled")
        except Exception as e:
            logger.error(f"❌ Mining error: {e}")
        finally:
            self.is_mining = False
    
    def get_mining_stats(self) -> Dict[str, Any]:
        """Get current mining statistics"""
        return {
            "node_id": self.node_id,
            "is_mining": self.is_mining,
            "work_id": self.current_work.get("work_id") if self.current_work else None,
            "hashes_computed": self.stats["hashes_computed"],
            "shares_found": self.stats["shares_found"],
            "uptime": self.stats["uptime"],
            "hashrate": (
                self.stats["hashes_computed"] / self.stats["uptime"] 
                if self.stats["uptime"] > 0 else 0
            )
        }

class AutoUpdater:
    """Handles automatic updates from central server"""
    
    def __init__(self, server_host: str, server_port: int):
        self.server_host = server_host
        self.server_port = server_port
        self.current_version = "1.0.0"
    
    async def check_for_updates(self) -> Dict[str, Any]:
        """Check for updates from central server"""
        try:
            # In a full implementation, this would check a version endpoint
            # For now, we'll simulate the check
            logger.info("🔍 Checking for updates...")
            
            # Simulate version check
            await asyncio.sleep(1)
            
            return {
                "update_available": False,
                "current_version": self.current_version,
                "latest_version": self.current_version,
                "message": "Node is up to date"
            }
            
        except Exception as e:
            logger.error(f"Update check failed: {e}")
            return {"update_available": False, "error": str(e)}
    
    async def perform_update(self) -> bool:
        """Download and apply updates"""
        try:
            logger.info("📦 Downloading update...")
            # Simulate update process
            await asyncio.sleep(2)
            
            logger.info("✅ Update completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Update failed: {e}")
            return False

class RemoteNode:
    """Main V30 Remote Mining Node class"""
    
    def __init__(self, config: NodeConfig):
        self.config = config
        self.protocol = V30ProtocolClient()
        self.system_analyzer = SystemAnalyzer()
        self.mining_worker = MiningWorker(config.node_id)
        self.auto_updater = AutoUpdater(config.server_host, config.server_port)
        
        self.running = False
        self.registered = False
        self.system_capabilities = None
        
        # Tasks
        self.heartbeat_task = None
        self.work_request_task = None
        self.update_check_task = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"🛑 Received signal {signum}, initiating shutdown...")
        asyncio.create_task(self.shutdown())
    
    async def initialize(self) -> bool:
        """Initialize the remote node"""
        try:
            logger.info("🚀 Initializing CryptoMiner V30 Remote Node...")
            logger.info(f"   Node ID: {self.config.node_id}")
            logger.info(f"   Server: {self.config.server_host}:{self.config.server_port}")
            
            # Analyze system capabilities
            logger.info("🔍 Analyzing system capabilities...")
            self.system_capabilities = self.system_analyzer.get_system_capabilities()
            
            # Log system info
            caps = self.system_capabilities
            logger.info(f"   CPU Cores: {caps['cpu']['logical_cores']} logical, {caps['cpu']['physical_cores']} physical")
            logger.info(f"   Memory: {caps['memory']['total_gb']} GB total")
            logger.info(f"   GPUs: {len(caps['gpus'])} detected")
            logger.info(f"   Network: {caps['network']['max_speed_gbps']} Gbps")
            logger.info(f"   Est. Hashpower: {caps['capabilities']['estimated_hashpower']:,} H/s")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    async def connect_to_server(self) -> bool:
        """Connect and register with V30 server"""
        try:
            # Connect to server
            if not await self.protocol.connect(self.config.server_host, self.config.server_port):
                return False
            
            # Register with server
            registration_data = {
                "node_id": self.config.node_id,
                "hostname": self.system_capabilities["hostname"],
                "license_key": self.config.license_key,
                "system_specs": {
                    "cpu_cores": self.system_capabilities["cpu"]["logical_cores"],
                    "ram_gb": self.system_capabilities["memory"]["total_gb"],
                    "total_gpus": len(self.system_capabilities["gpus"]),
                    "nvidia_gpus": len([g for g in self.system_capabilities["gpus"] if g["type"] == "NVIDIA"]),
                    "amd_gpus": len([g for g in self.system_capabilities["gpus"] if g["type"] == "AMD"]),
                    "network_speed_gbps": self.system_capabilities["network"]["max_speed_gbps"]
                },
                "capabilities": self.system_capabilities["capabilities"],
                "version": "1.0.0"
            }
            
            # Send registration
            if not await self.protocol.send_message(0x01, registration_data):  # NODE_REGISTER
                return False
            
            # Wait for registration response
            msg_type, response, error = await self.protocol.receive_message()
            
            if error:
                logger.error(f"Registration failed: {error}")
                return False
            
            if msg_type == 0x02:  # NODE_REGISTER_ACK
                if response.get("success"):
                    self.registered = True
                    logger.info("✅ Successfully registered with V30 server")
                    logger.info(f"   Server Version: {response.get('server_info', {}).get('version', 'unknown')}")
                    return True
                else:
                    logger.error(f"Registration rejected: {response.get('error', 'Unknown error')}")
                    return False
            else:
                logger.error(f"Unexpected response type: {msg_type}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Server connection failed: {e}")
            return False
    
    async def start_operations(self):
        """Start all node operations"""
        if not self.registered:
            logger.error("❌ Cannot start operations - node not registered")
            return
        
        self.running = True
        logger.info("🎯 Starting node operations...")
        
        # Start heartbeat task
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        # Start work request task
        self.work_request_task = asyncio.create_task(self._work_request_loop())
        
        # Start update check task if enabled
        if self.config.auto_update:
            self.update_check_task = asyncio.create_task(self._update_check_loop())
        
        # Main message handling loop
        await self._message_handling_loop()
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats to server"""
        try:
            while self.running:
                heartbeat_data = {
                    "node_id": self.config.node_id,
                    "timestamp": time.time(),
                    "status": "active",
                    "mining_stats": self.mining_worker.get_mining_stats()
                }
                
                await self.protocol.send_message(0x03, heartbeat_data)  # NODE_HEARTBEAT
                await asyncio.sleep(self.config.heartbeat_interval)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
    
    async def _work_request_loop(self):
        """Periodically request work from server"""
        try:
            while self.running:
                if not self.mining_worker.is_mining:
                    work_request = {
                        "node_id": self.config.node_id,
                        "timestamp": time.time(),
                        "capabilities": self.system_capabilities["capabilities"]
                    }
                    
                    await self.protocol.send_message(0x10, work_request)  # WORK_REQUEST
                
                await asyncio.sleep(self.config.work_request_interval)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Work request error: {e}")
    
    async def _update_check_loop(self):
        """Periodically check for updates"""
        try:
            while self.running:
                update_info = await self.auto_updater.check_for_updates()
                
                if update_info.get("update_available"):
                    logger.info(f"📦 Update available: {update_info.get('latest_version')}")
                    if await self.auto_updater.perform_update():
                        logger.info("🔄 Update completed, restart required")
                        await self.shutdown()
                        return
                
                await asyncio.sleep(self.config.update_check_interval)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Update check error: {e}")
    
    async def _message_handling_loop(self):
        """Main message handling loop"""
        try:
            while self.running:
                msg_type, data, error = await self.protocol.receive_message()
                
                if error:
                    logger.error(f"Message receive error: {error}")
                    break
                
                if msg_type is None:
                    continue
                
                # Handle different message types
                if msg_type == 0x04:  # NODE_HEARTBEAT_ACK
                    pass  # Heartbeat acknowledged
                
                elif msg_type == 0x11:  # WORK_ASSIGNMENT
                    await self._handle_work_assignment(data)
                
                elif msg_type == 0x31:  # CONTROL_COMMAND
                    await self._handle_control_command(data)
                
                elif msg_type == 0xE0:  # ERROR
                    logger.error(f"Server error: {data.get('error', 'Unknown error')}")
                
                else:
                    logger.warning(f"Unknown message type: {msg_type}")
                
        except Exception as e:
            logger.error(f"Message handling error: {e}")
        finally:
            self.running = False
    
    async def _handle_work_assignment(self, data: Dict[str, Any]):
        """Handle work assignment from server"""
        if data.get("no_work"):
            logger.info("⏳ No work available from server")
            return
        
        # Stop current mining if active
        if self.mining_worker.is_mining:
            self.mining_worker.stop_mining()
        
        # Start new mining work
        if self.mining_worker.start_mining(data):
            logger.info(f"📋 New work assignment received: {data.get('work_id', 'unknown')}")
        else:
            logger.error("❌ Failed to start mining work")
    
    async def _handle_control_command(self, data: Dict[str, Any]):
        """Handle control commands from server"""
        command = data.get("command")
        
        if command == "stop_mining":
            if self.mining_worker.stop_mining():
                logger.info("🛑 Mining stopped by server command")
        
        elif command == "restart":
            logger.info("🔄 Restart requested by server")
            await self.shutdown()
        
        elif command == "update":
            logger.info("📦 Update requested by server")
            if await self.auto_updater.perform_update():
                await self.shutdown()
        
        else:
            logger.warning(f"Unknown control command: {command}")
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down V30 Remote Node...")
        
        self.running = False
        
        # Stop mining
        if self.mining_worker.is_mining:
            self.mining_worker.stop_mining()
        
        # Cancel tasks
        for task in [self.heartbeat_task, self.work_request_task, self.update_check_task]:
            if task and not task.done():
                task.cancel()
        
        # Disconnect from server
        if self.protocol.connected:
            await self.protocol.send_message(0x05, {"node_id": self.config.node_id})  # NODE_DISCONNECT
            await self.protocol.disconnect()
        
        logger.info("✅ V30 Remote Node shutdown completed")

def load_config(config_file: str = "node_config.json") -> Optional[NodeConfig]:
    """Load node configuration from file"""
    try:
        if not os.path.exists(config_file):
            logger.info("📄 Creating default configuration...")
            
            default_config = {
                "server_host": "localhost",
                "server_port": 9001,
                "license_key": "",
                "max_cpu_threads": psutil.cpu_count(logical=True) or 4,
                "enable_gpu": True,
                "heartbeat_interval": 30.0,
                "work_request_interval": 10.0,
                "auto_update": True,
                "update_check_interval": 3600.0
            }
            
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            logger.info(f"✅ Default configuration saved to {config_file}")
            logger.info("⚠️  Please edit the configuration file with your license key and server details")
            return None
        
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        # Generate node ID if not present
        node_id = config_data.get("node_id")
        if not node_id:
            analyzer = SystemAnalyzer()
            node_id = analyzer.node_id
            config_data["node_id"] = node_id
            
            # Save updated config
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        
        config = NodeConfig(
            node_id=node_id,
            server_host=config_data["server_host"],
            server_port=config_data["server_port"],
            license_key=config_data["license_key"],
            max_cpu_threads=config_data["max_cpu_threads"],
            enable_gpu=config_data["enable_gpu"],
            heartbeat_interval=config_data["heartbeat_interval"],
            work_request_interval=config_data["work_request_interval"],
            auto_update=config_data["auto_update"],
            update_check_interval=config_data["update_check_interval"]
        )
        
        return config
        
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return None

def print_banner():
    """Print application banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🚀 CryptoMiner Enterprise V30 - Remote Mining Node        ║
║                                                              ║
║   Distributed cryptocurrency mining node                    ║
║   Connects to V30 central control system                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

async def main():
    """Main application entry point"""
    print_banner()
    
    # Load configuration
    config = load_config()
    if not config:
        logger.error("❌ Configuration required. Please edit node_config.json and restart.")
        return 1
    
    if not config.license_key:
        logger.error("❌ License key required. Please edit node_config.json with your V30 enterprise license key.")
        return 1
    
    # Initialize and start node
    node = RemoteNode(config)
    
    try:
        # Initialize
        if not await node.initialize():
            return 1
        
        # Connect to server
        if not await node.connect_to_server():
            return 1
        
        # Start operations
        logger.info("🎯 V30 Remote Node is now operational")
        await node.start_operations()
        
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        return 1
    finally:
        await node.shutdown()
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user")
        sys.exit(0)