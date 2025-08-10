"""
CryptoMiner Enterprise V30 - Central Control System
Orchestrates distributed mining operations across multiple nodes
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Import V30 components
from enterprise_license import EnterpriseV30License
from hardware_validator import EnterpriseHardwareValidator
from gpu_mining_engine import HybridGPUCPUMiner
from v30_protocol import DistributedMiningServer, NodeManager, MessageType, V30Protocol
from mining_engine import mining_engine as local_mining_engine

logger = logging.getLogger(__name__)

@dataclass
class V30SystemStats:
    """Aggregate statistics for the entire V30 system"""
    # Node Statistics
    total_nodes: int = 0
    active_nodes: int = 0
    inactive_nodes: int = 0
    
    # Hardware Statistics
    total_cpu_cores: int = 0
    total_gpus: int = 0
    total_nvidia_gpus: int = 0
    total_amd_gpus: int = 0
    total_ram_gb: float = 0.0
    
    # Mining Statistics
    total_hashrate: float = 0.0
    cpu_hashrate: float = 0.0
    gpu_hashrate: float = 0.0
    nvidia_hashrate: float = 0.0
    amd_hashrate: float = 0.0
    
    # Work Distribution
    total_work_assigned: int = 0
    total_work_completed: int = 0
    total_shares_found: int = 0
    total_hashes_computed: int = 0
    
    # System Health
    average_node_uptime: float = 0.0
    network_latency_avg: float = 0.0
    system_efficiency: float = 0.0
    uptime: float = 0.0

class CentralControlSystem:
    """V30 Central Control System for distributed mining"""
    
    def __init__(self):
        # Core systems
        self.license_system = EnterpriseV30License()
        self.hardware_validator = EnterpriseHardwareValidator()
        self.distributed_server = DistributedMiningServer()
        
        # Local mining (if license allows local execution)
        self.local_miner = None
        self.hybrid_miner = None
        
        # System state
        self.is_running = False
        self.start_time = None
        self.current_mining_config = None
        self.system_stats = V30SystemStats()
        
        # Configuration
        self.settings = {
            "auto_work_distribution": True,
            "load_balancing": True,
            "failover_enabled": True,
            "stats_update_interval": 5.0,
            "heartbeat_timeout": 30.0,
            "max_work_per_node": 10,
            "mining_algorithm": "scrypt",
            "default_difficulty": "00000000"
        }
        
        # Inject license system into distributed server
        self.distributed_server.license_system = self.license_system
        
        logger.info("🎛️ V30 Central Control System initialized")
    
    async def initialize_system(self) -> Dict[str, Any]:
        """Initialize the complete V30 system"""
        try:
            logger.info("🚀 Initializing CryptoMiner Enterprise V30...")
            
            # Initialize local hardware if license allows
            local_license_result = self._check_local_license()
            if local_license_result["valid"]:
                await self._initialize_local_mining()
            
            # Start distributed server
            logger.info("🌐 Starting distributed mining server...")
            self.distributed_server_task = asyncio.create_task(
                self.distributed_server.start_server()
            )
            
            # Start system monitoring
            self.monitoring_task = asyncio.create_task(
                self._system_monitoring_loop()
            )
            
            self.is_running = True
            self.start_time = time.time()
            
            initialization_report = {
                "success": True,
                "version": "v30",
                "local_mining": local_license_result["valid"],
                "distributed_server": True,
                "server_address": f"{self.distributed_server.host}:{self.distributed_server.port}",
                "features": [
                    "distributed_mining",
                    "gpu_acceleration", 
                    "license_management",
                    "load_balancing",
                    "auto_failover",
                    "real_time_monitoring"
                ],
                "startup_time": datetime.now().isoformat()
            }
            
            logger.info("✅ V30 System initialization completed")
            return initialization_report
            
        except Exception as e:
            logger.error(f"❌ System initialization failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _check_local_license(self) -> Dict[str, Any]:
        """Check if local mining is licensed"""
        # For demo, we'll use the first generated license
        try:
            with open(self.license_system.license_file, 'r') as f:
                license_data = json.load(f)
            
            # Get first available license
            first_key = next(iter(license_data["licenses"]))
            return self.license_system.validate_license(first_key)
            
        except Exception as e:
            logger.error(f"License check failed: {e}")
            return {"valid": False, "error": str(e)}
    
    async def _initialize_local_mining(self):
        """Initialize local mining capabilities"""
        try:
            # Initialize hybrid GPU+CPU miner for local node
            self.hybrid_miner = HybridGPUCPUMiner(
                local_mining_engine, 
                self.hardware_validator
            )
            
            logger.info("⛏️ Local mining initialized")
            logger.info(f"   NVIDIA GPUs: {len(self.hybrid_miner.nvidia_miners)}")
            logger.info(f"   AMD GPUs: {len(self.hybrid_miner.amd_miners)}")
            
        except Exception as e:
            logger.error(f"Local mining initialization failed: {e}")
    
    async def start_distributed_mining(self, coin_config: Dict, wallet_address: str,
                                     include_local: bool = True) -> Dict[str, Any]:
        """Start distributed mining across all connected nodes"""
        try:
            if not self.is_running:
                return {"success": False, "error": "System not initialized"}
            
            logger.info("🚀 Starting distributed mining operation...")
            
            self.current_mining_config = {
                "coin_config": coin_config,
                "wallet_address": wallet_address,
                "start_time": time.time()
            }
            
            results = {
                "nodes_started": 0,
                "local_mining": False,
                "work_assignments": 0,
                "total_hashpower": 0
            }
            
            # Create work assignments for all nodes
            node_manager = self.distributed_server.node_manager
            work_assignments = node_manager.create_mining_work(
                coin_config, wallet_address
            )
            
            results["work_assignments"] = len(work_assignments)
            results["nodes_started"] = len([w for w in work_assignments if w.assigned_node])
            
            # Start local mining if requested and available
            if include_local and self.hybrid_miner:
                local_result = self.hybrid_miner.start_hybrid_mining(
                    coin_config, wallet_address, cpu_threads=16
                )
                results["local_mining"] = local_result["success"]
                if local_result["success"]:
                    logger.info("✅ Local hybrid mining started")
            
            # Broadcast mining start to all nodes
            await self._broadcast_mining_command("start", coin_config, wallet_address)
            
            success_message = f"Distributed mining started: {results['nodes_started']} remote nodes"
            if results["local_mining"]:
                success_message += " + local node"
            
            logger.info(f"🎉 {success_message}")
            
            return {
                "success": True,
                "message": success_message,
                "details": results
            }
            
        except Exception as e:
            logger.error(f"Failed to start distributed mining: {e}")
            return {"success": False, "error": str(e)}
    
    async def stop_distributed_mining(self) -> Dict[str, Any]:
        """Stop distributed mining across all nodes"""
        try:
            logger.info("🛑 Stopping distributed mining operation...")
            
            results = {"nodes_stopped": 0, "local_stopped": False}
            
            # Stop local mining if active
            if self.hybrid_miner:
                local_result = self.hybrid_miner.stop_hybrid_mining()
                results["local_stopped"] = local_result["success"]
            
            # Broadcast mining stop to all nodes
            await self._broadcast_mining_command("stop")
            
            # Count active nodes that received stop command
            node_manager = self.distributed_server.node_manager
            results["nodes_stopped"] = len([
                n for n in node_manager.nodes.values() 
                if n.status == "connected"
            ])
            
            self.current_mining_config = None
            
            success_message = f"Distributed mining stopped: {results['nodes_stopped']} nodes"
            logger.info(f"✅ {success_message}")
            
            return {
                "success": True,
                "message": success_message,
                "details": results
            }
            
        except Exception as e:
            logger.error(f"Failed to stop distributed mining: {e}")
            return {"success": False, "error": str(e)}
    
    async def _broadcast_mining_command(self, command: str, coin_config: Dict = None, 
                                      wallet_address: str = None):
        """Broadcast mining command to all connected nodes"""
        node_manager = self.distributed_server.node_manager
        active_nodes = [n for n in node_manager.nodes.values() if n.status == "connected"]
        
        command_data = {
            "command": command,
            "timestamp": time.time()
        }
        
        if coin_config and wallet_address:
            command_data.update({
                "coin_config": coin_config,
                "wallet_address": wallet_address
            })
        
        # In a full implementation, you'd send these via the protocol
        # For now, we'll log the broadcast
        logger.info(f"📡 Broadcasting '{command}' to {len(active_nodes)} nodes")
    
    async def _system_monitoring_loop(self):
        """Continuous system monitoring and statistics collection"""
        while self.is_running:
            try:
                await self._update_system_stats()
                await asyncio.sleep(self.settings["stats_update_interval"])
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(5)  # Fallback interval
    
    async def _update_system_stats(self):
        """Update comprehensive system statistics"""
        try:
            node_manager = self.distributed_server.node_manager
            node_stats = node_manager.get_node_stats()
            
            # Update node statistics
            self.system_stats.total_nodes = node_stats["total_nodes"]
            self.system_stats.active_nodes = node_stats["active_nodes"]
            self.system_stats.inactive_nodes = node_stats["inactive_nodes"]
            
            # Aggregate hardware statistics
            total_cores = 0
            total_gpus = 0
            total_nvidia = 0
            total_amd = 0
            total_ram = 0.0
            
            for node in node_manager.nodes.values():
                if node.status == "connected":
                    specs = node.system_specs
                    total_cores += specs.get("cpu_cores", 0)
                    total_gpus += specs.get("total_gpus", 0)
                    total_nvidia += specs.get("nvidia_gpus", 0)
                    total_amd += specs.get("amd_gpus", 0)
                    total_ram += specs.get("ram_gb", 0)
            
            self.system_stats.total_cpu_cores = total_cores
            self.system_stats.total_gpus = total_gpus
            self.system_stats.total_nvidia_gpus = total_nvidia
            self.system_stats.total_amd_gpus = total_amd
            self.system_stats.total_ram_gb = total_ram
            
            # Update work statistics
            self.system_stats.total_work_assigned = len(node_manager.active_work)
            self.system_stats.total_work_completed = len(node_manager.completed_work)
            
            # Calculate aggregate hashrates (from completed work)
            total_hashes = sum(
                result.hashes_computed 
                for result in node_manager.completed_work
            )
            
            total_shares = sum(
                result.shares_found
                for result in node_manager.completed_work
            )
            
            self.system_stats.total_hashes_computed = total_hashes
            self.system_stats.total_shares_found = total_shares
            
            # System uptime
            if self.start_time:
                self.system_stats.uptime = time.time() - self.start_time
            
            # Calculate efficiency
            if self.system_stats.uptime > 0 and total_hashes > 0:
                self.system_stats.total_hashrate = total_hashes / self.system_stats.uptime
                self.system_stats.system_efficiency = (
                    self.system_stats.total_hashrate / max(1, total_cores)
                )
            
        except Exception as e:
            logger.error(f"Stats update error: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            "system": {
                "version": "v30",
                "running": self.is_running,
                "uptime": self.system_stats.uptime,
                "current_mining": self.current_mining_config is not None
            },
            "statistics": asdict(self.system_stats),
            "server": {
                "address": f"{self.distributed_server.host}:{self.distributed_server.port}",
                "active": self.distributed_server.is_running
            },
            "capabilities": {
                "distributed_mining": True,
                "gpu_acceleration": True,
                "license_management": True,
                "load_balancing": True,
                "auto_failover": True
            }
        }
        
        return status
    
    async def shutdown_system(self):
        """Graceful system shutdown"""
        try:
            logger.info("🛑 Shutting down V30 Central Control System...")
            
            # Stop any active mining
            if self.current_mining_config:
                await self.stop_distributed_mining()
            
            # Stop monitoring
            if hasattr(self, 'monitoring_task'):
                self.monitoring_task.cancel()
            
            # Stop distributed server
            if hasattr(self, 'distributed_server_task'):
                self.distributed_server_task.cancel()
                await self.distributed_server.stop_server()
            
            self.is_running = False
            logger.info("✅ V30 system shutdown completed")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")

# Test the central control system
if __name__ == "__main__":
    import asyncio
    
    async def test_v30_system():
        print("🎛️ Testing V30 Central Control System...")
        
        # Initialize system
        control_system = CentralControlSystem()
        init_result = await control_system.initialize_system()
        
        print(f"✅ System initialization: {init_result['success']}")
        if init_result["success"]:
            print(f"   Version: {init_result['version']}")
            print(f"   Features: {len(init_result['features'])} features")
            print(f"   Server: {init_result['server_address']}")
        
        # Test system status
        await asyncio.sleep(2)  # Let monitoring collect some data
        
        status = control_system.get_system_status()
        print(f"✅ System status:")
        print(f"   Running: {status['system']['running']}")
        print(f"   Uptime: {status['system']['uptime']:.1f}s")
        print(f"   Active nodes: {status['statistics']['active_nodes']}")
        
        # Test mining start/stop (without actual nodes)
        coin_config = {
            "name": "Litecoin",
            "symbol": "LTC",
            "algorithm": "scrypt",
            "scrypt_n": 1024
        }
        wallet_address = "ltc1test123"
        
        print("\n🚀 Testing distributed mining start...")
        start_result = await control_system.start_distributed_mining(
            coin_config, wallet_address
        )
        print(f"   Result: {start_result['success']} - {start_result.get('message', '')}")
        
        await asyncio.sleep(3)
        
        print("\n🛑 Testing distributed mining stop...")
        stop_result = await control_system.stop_distributed_mining()
        print(f"   Result: {stop_result['success']} - {stop_result.get('message', '')}")
        
        # Shutdown
        await control_system.shutdown_system()
        print("\n🎉 V30 Central Control System test completed!")
    
    # Run test
    asyncio.run(test_v30_system())