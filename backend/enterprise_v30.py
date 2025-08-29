#!/usr/bin/env python3
"""
CryptoMiner Pro - Consolidated Enterprise V30 Module
Combines license management, hardware validation, and central control functionality
"""

import os
import json
import uuid
import hashlib
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
import string
import secrets
import psutil
import socket
import struct
import time
import zlib
import aiofiles
import subprocess
import threading
import re
from enum import IntEnum
from dataclasses import dataclass, asdict

# Logging setup
logger = logging.getLogger(__name__)

# ============================================================================
# V30 COMMUNICATION PROTOCOL SYSTEM
# ============================================================================

class MessageType(IntEnum):
    """Protocol message types"""
    # Node Registration
    NODE_REGISTER = 0x01
    NODE_REGISTER_ACK = 0x02
    NODE_HEARTBEAT = 0x03
    NODE_HEARTBEAT_ACK = 0x04
    NODE_DISCONNECT = 0x05
    
    # Mining Coordination
    WORK_REQUEST = 0x10
    WORK_ASSIGNMENT = 0x11
    WORK_COMPLETE = 0x12
    WORK_RESULT = 0x13
    MINING_START = 0x14
    MINING_STOP = 0x15
    
    # Statistics & Monitoring
    STATS_REQUEST = 0x20
    STATS_RESPONSE = 0x21
    PERFORMANCE_UPDATE = 0x22
    SYSTEM_STATUS = 0x23
    
    # Control Commands
    CONFIG_UPDATE = 0x30
    CONTROL_COMMAND = 0x31
    LICENSE_VALIDATE = 0x32
    LICENSE_RESPONSE = 0x33
    
    # Error Handling
    ERROR = 0xE0
    UNKNOWN = 0xE1

@dataclass
class NodeInfo:
    node_id: str
    hostname: str
    ip_address: str
    port: int
    license_key: str
    capabilities: Dict[str, Any]
    system_specs: Dict[str, Any]
    connected_time: float
    last_heartbeat: float
    status: str = "connected"

@dataclass
class MiningWork:
    work_id: str
    coin_config: Dict[str, Any]
    wallet_address: str
    start_nonce: int
    nonce_range: int
    difficulty_target: str
    timestamp: float
    assigned_node: Optional[str] = None

@dataclass 
class WorkResult:
    work_id: str
    node_id: str
    found_nonce: Optional[int]
    hash_result: Optional[str]
    hashes_computed: int
    processing_time: float
    success: bool
    shares_found: int = 0

# ============================================================================
# GPU MINING SYSTEM
# ============================================================================

@dataclass
class GPUMiningStats:
    gpu_id: int
    gpu_type: str  # "NVIDIA" or "AMD"
    gpu_name: str
    hashrate: float = 0.0
    temperature: Optional[int] = None
    power_draw: Optional[float] = None
    memory_used: Optional[int] = None
    memory_total: Optional[int] = None
    uptime: float = 0.0
    accepted_shares: int = 0
    rejected_shares: int = 0
    is_mining: bool = False

@dataclass
class HybridMiningStats:
    total_hashrate: float = 0.0
    cpu_hashrate: float = 0.0
    gpu_hashrate: float = 0.0
    nvidia_hashrate: float = 0.0
    amd_hashrate: float = 0.0
    total_gpus: int = 0
    active_gpus: int = 0
    nvidia_gpus: int = 0
    amd_gpus: int = 0
    cpu_threads: int = 0
    uptime: float = 0.0

# ============================================================================
# ENTERPRISE LICENSE SYSTEM
# ============================================================================

class EnterpriseV30License:
    """
    Manages V30 Enterprise license keys and activation
    """
    
    def __init__(self, license_file: str = "enterprise_licenses.json"):
        self.license_file = license_file
        self.licenses = []
        self.activated_licenses = {}
        self._load_licenses()
    
    def _load_licenses(self):
        """Load existing license keys from file"""
        try:
            if os.path.exists(self.license_file):
                with open(self.license_file, 'r') as f:
                    data = json.load(f)
                    self.licenses = data.get('licenses', [])
                    self.activated_licenses = data.get('activated', {})
                    logger.info(f"Loaded {len(self.licenses)} enterprise licenses")
            else:
                self._generate_initial_licenses()
        except Exception as e:
            logger.error(f"Failed to load licenses: {e}")
            self._generate_initial_licenses()
    
    def _save_licenses(self):
        """Save licenses to file"""
        try:
            data = {
                'licenses': self.licenses,
                'activated': self.activated_licenses,
                'generated_at': datetime.utcnow().isoformat(),
                'version': '30.0.0'
            }
            
            with open(self.license_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info("License database saved successfully")
        except Exception as e:
            logger.error(f"Failed to save licenses: {e}")
    
    def _generate_license_key(self) -> str:
        """Generate a 42-character alphanumeric license key"""
        # Use a mix of letters and numbers for better readability
        alphabet = string.ascii_uppercase + string.digits
        # Remove potentially confusing characters
        alphabet = alphabet.replace('0', '').replace('O', '').replace('1', '').replace('I')
        
        # Generate 42 characters in groups for readability
        groups = []
        for _ in range(6):
            group = ''.join(secrets.choice(alphabet) for _ in range(7))
            groups.append(group)
        
        return '-'.join(groups[:6])  # Format: XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX
    
    def _generate_initial_licenses(self, count: int = 5000):
        """Generate initial set of enterprise license keys"""
        logger.info(f"Generating {count} enterprise license keys...")
        
        self.licenses = []
        for i in range(count):
            license_key = self._generate_license_key()
            self.licenses.append(license_key)
            
            if (i + 1) % 500 == 0:
                logger.info(f"Generated {i + 1}/{count} license keys...")
        
        self._save_licenses()
        logger.info(f"Successfully generated {count} enterprise license keys")
    
    def validate_license(self, license_key: str) -> Dict[str, Any]:
        """Validate a license key"""
        try:
            if not license_key or len(license_key) != 47:  # 42 chars + 5 hyphens
                return {
                    "valid": False,
                    "error": "Invalid license key format",
                    "details": "License key must be 42 alphanumeric characters in XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX format"
                }
            
            if license_key in self.licenses:
                # Check if already activated
                if license_key in self.activated_licenses:
                    activation_info = self.activated_licenses[license_key]
                    return {
                        "valid": True,
                        "status": "activated",
                        "activated_at": activation_info.get("activated_at"),
                        "node_info": activation_info.get("node_info", {}),
                        "activation_id": activation_info.get("activation_id")
                    }
                else:
                    return {
                        "valid": True,
                        "status": "available",
                        "message": "License key is valid and available for activation"
                    }
            else:
                return {
                    "valid": False,
                    "error": "License key not found",
                    "details": "This license key is not in the V30 Enterprise database"
                }
                
        except Exception as e:
            logger.error(f"License validation error: {e}")
            return {
                "valid": False,
                "error": "Validation system error",
                "details": str(e)
            }
    
    def activate_license(self, license_key: str, node_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Activate a license key for a specific node"""
        try:
            # First validate the license
            validation_result = self.validate_license(license_key)
            
            if not validation_result.get("valid"):
                return validation_result
            
            if validation_result.get("status") == "activated":
                return {
                    "success": False,
                    "error": "License already activated",
                    "details": "This license key is already activated on another node"
                }
            
            # Generate activation ID
            activation_id = str(uuid.uuid4())
            
            # Prepare activation data
            activation_data = {
                "activation_id": activation_id,
                "activated_at": datetime.utcnow().isoformat(),
                "node_info": node_info or {},
                "hostname": socket.gethostname(),
                "ip_address": self._get_local_ip()
            }
            
            # Store activation
            self.activated_licenses[license_key] = activation_data
            self._save_licenses()
            
            logger.info(f"License activated: {license_key[:12]}... on {activation_data['hostname']}")
            
            return {
                "success": True,
                "message": "License activated successfully",
                "activation_id": activation_id,
                "activated_at": activation_data["activated_at"],
                "features_enabled": [
                    "enterprise_scale_mining",
                    "distributed_mining_control", 
                    "advanced_hardware_validation",
                    "gpu_acceleration_support",
                    "custom_mining_protocols",
                    "enterprise_monitoring",
                    "load_balancing",
                    "auto_failover"
                ]
            }
            
        except Exception as e:
            logger.error(f"License activation error: {e}")
            return {
                "success": False,
                "error": "Activation system error",
                "details": str(e)
            }
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

# ============================================================================
# HARDWARE VALIDATION SYSTEM  
# ============================================================================

class EnterpriseHardwareValidator:
    """
    Validates system hardware against enterprise requirements
    """
    
    def __init__(self):
        # V30 Enterprise minimum requirements
        self.min_requirements = {
            "memory_gb": 64,
            "recommended_memory_gb": 512,
            "min_cpu_cores": 32,
            "min_network_speed_mbps": 1000,
            "required_features": ["virtualization", "64bit"],
            "recommended_gpu": True
        }
    
    def comprehensive_validation(self) -> Dict[str, Any]:
        """Perform comprehensive hardware validation"""
        try:
            results = {
                "meets_requirements": False,
                "validation_timestamp": datetime.utcnow().isoformat(),
                "system_info": {},
                "requirements_check": {},
                "recommendations": [],
                "warnings": []
            }
            
            # Get system information
            results["system_info"] = self._get_system_info()
            
            # Check each requirement
            results["requirements_check"] = self._check_requirements(results["system_info"])
            
            # Generate recommendations
            results["recommendations"] = self._generate_recommendations(results["requirements_check"])
            
            # Check if all critical requirements are met
            critical_checks = ["memory", "cpu_cores", "network"]
            results["meets_requirements"] = all(
                results["requirements_check"].get(check, {}).get("meets_requirement", False)
                for check in critical_checks
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Hardware validation error: {e}")
            return {
                "meets_requirements": False,
                "error": str(e),
                "validation_timestamp": datetime.utcnow().isoformat()
            }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Gather comprehensive system information"""
        info = {}
        
        try:
            # Memory information
            memory = psutil.virtual_memory()
            info["memory"] = {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percentage_used": memory.percent
            }
            
            # CPU information
            info["cpu"] = {
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "current_freq_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                "max_freq_mhz": psutil.cpu_freq().max if psutil.cpu_freq() else 0
            }
            
            # Disk information
            disk = psutil.disk_usage('/')
            info["disk"] = {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "used_percentage": round((disk.used / disk.total) * 100, 1)
            }
            
            # Network interfaces
            info["network"] = self._get_network_info()
            
            # GPU information
            info["gpu"] = self._get_gpu_info()
            
            # System details
            info["system"] = {
                "hostname": socket.gethostname(),
                "architecture": os.uname().machine,
                "kernel": os.uname().release,
                "uptime_hours": round(time.time() - psutil.boot_time()) / 3600
            }
            
        except Exception as e:
            logger.error(f"Failed to gather system info: {e}")
        
        return info
    
    def _get_network_info(self) -> Dict[str, Any]:
        """Get network interface information"""
        network_info = {
            "interfaces": [],
            "estimated_max_speed_mbps": 0
        }
        
        try:
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for interface_name, addresses in interfaces.items():
                if interface_name.startswith(('lo', 'docker', 'br-')):
                    continue
                    
                interface_info = {
                    "name": interface_name,
                    "addresses": []
                }
                
                for addr in addresses:
                    if addr.family == socket.AF_INET:
                        interface_info["addresses"].append({
                            "type": "IPv4",
                            "address": addr.address,
                            "netmask": addr.netmask
                        })
                
                if interface_name in stats:
                    stat = stats[interface_name]
                    interface_info["speed_mbps"] = stat.speed
                    interface_info["is_up"] = stat.isup
                    
                    if stat.isup and stat.speed > network_info["estimated_max_speed_mbps"]:
                        network_info["estimated_max_speed_mbps"] = stat.speed
                
                network_info["interfaces"].append(interface_info)
                
        except Exception as e:
            logger.error(f"Failed to get network info: {e}")
        
        return network_info
    
    def _get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information if available"""
        gpu_info = {
            "nvidia_gpus": [],
            "amd_gpus": [],
            "total_gpus": 0,
            "cuda_available": False,
            "opencl_available": False
        }
        
        try:
            # Try to detect NVIDIA GPUs
            try:
                import subprocess
                result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            name, memory = line.split(', ')
                            gpu_info["nvidia_gpus"].append({
                                "name": name.strip(),
                                "memory_mb": int(memory.strip())
                            })
                    gpu_info["cuda_available"] = True
            except:
                pass
            
            # Try to detect AMD GPUs
            try:
                result = subprocess.run(['rocm-smi', '--showproductname'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if 'Card' in line and 'Product Name' in line:
                            gpu_name = line.split(':')[-1].strip()
                            gpu_info["amd_gpus"].append({"name": gpu_name})
                    gpu_info["opencl_available"] = True
            except:
                pass
            
            gpu_info["total_gpus"] = len(gpu_info["nvidia_gpus"]) + len(gpu_info["amd_gpus"])
            
        except Exception as e:
            logger.error(f"Failed to get GPU info: {e}")
        
        return gpu_info
    
    def _check_requirements(self, system_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check system against enterprise requirements"""
        checks = {}
        
        # Memory check
        total_memory = system_info.get("memory", {}).get("total_gb", 0)
        checks["memory"] = {
            "requirement": f"{self.min_requirements['memory_gb']}GB minimum, {self.min_requirements['recommended_memory_gb']}GB recommended",
            "actual": f"{total_memory}GB",
            "meets_requirement": total_memory >= self.min_requirements["memory_gb"],
            "meets_recommended": total_memory >= self.min_requirements["recommended_memory_gb"],
            "score": min(100, int((total_memory / self.min_requirements["memory_gb"]) * 100))
        }
        
        # CPU cores check
        cpu_cores = system_info.get("cpu", {}).get("physical_cores", 0)
        checks["cpu_cores"] = {
            "requirement": f"{self.min_requirements['min_cpu_cores']} cores minimum",
            "actual": f"{cpu_cores} cores",
            "meets_requirement": cpu_cores >= self.min_requirements["min_cpu_cores"],
            "score": min(100, int((cpu_cores / self.min_requirements["min_cpu_cores"]) * 100))
        }
        
        # Network speed check
        max_speed = system_info.get("network", {}).get("estimated_max_speed_mbps", 0)
        checks["network"] = {
            "requirement": f"{self.min_requirements['min_network_speed_mbps']}Mbps minimum",
            "actual": f"{max_speed}Mbps",
            "meets_requirement": max_speed >= self.min_requirements["min_network_speed_mbps"],
            "score": min(100, int((max_speed / self.min_requirements["min_network_speed_mbps"]) * 100))
        }
        
        # GPU check (recommended)
        total_gpus = system_info.get("gpu", {}).get("total_gpus", 0)
        checks["gpu"] = {
            "requirement": "1+ GPU recommended for optimal performance",
            "actual": f"{total_gpus} GPU(s) detected",
            "meets_requirement": total_gpus > 0,
            "is_recommended": True,
            "cuda_available": system_info.get("gpu", {}).get("cuda_available", False),
            "opencl_available": system_info.get("gpu", {}).get("opencl_available", False)
        }
        
        return checks
    
    def _generate_recommendations(self, requirements_check: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on system analysis"""
        recommendations = []
        
        # Memory recommendations
        memory_check = requirements_check.get("memory", {})
        if not memory_check.get("meets_recommended", True):
            recommendations.append("💾 Consider upgrading to 512GB RAM for optimal enterprise mining performance")
        elif not memory_check.get("meets_requirement", True):
            recommendations.append("⚠️  CRITICAL: Upgrade to at least 64GB RAM for V30 Enterprise compatibility")
        
        # CPU recommendations
        cpu_check = requirements_check.get("cpu_cores", {})
        if not cpu_check.get("meets_requirement", True):
            recommendations.append("🖥️  CRITICAL: Upgrade to a server with at least 32 CPU cores")
        elif cpu_check.get("score", 0) < 150:
            recommendations.append("🚀 Consider upgrading to a higher core count CPU for better mining throughput")
        
        # Network recommendations
        network_check = requirements_check.get("network", {})
        if not network_check.get("meets_requirement", True):
            recommendations.append("🌐 CRITICAL: Upgrade network connection to at least 1Gbps for distributed mining")
        
        # GPU recommendations
        gpu_check = requirements_check.get("gpu", {})
        if not gpu_check.get("meets_requirement", True):
            recommendations.append("🎮 Add GPU(s) for hybrid CPU+GPU mining and enhanced performance")
        elif not gpu_check.get("cuda_available", False) and not gpu_check.get("opencl_available", False):
            recommendations.append("🔧 Install CUDA or ROCm drivers for GPU mining support")
        
        return recommendations

# ============================================================================
# V30 PROTOCOL SYSTEM
# ============================================================================

class V30Protocol:
    """Custom high-performance protocol for V30 distributed mining"""
    
    MAGIC_BYTES = b'\x43\x4D\x50\x33'  # CMP3 (CryptoMiner Pro V30)
    VERSION = 1
    HEADER_SIZE = 16
    MAX_PAYLOAD_SIZE = 1024 * 1024  # 1MB max payload
    
    @classmethod
    def create_message(cls, msg_type: MessageType, data: Dict[str, Any], 
                      node_id: str = "", compress: bool = True) -> bytes:
        """Create a protocol message"""
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
            payload_hash = hashlib.sha256(payload).digest()[:4]  # First 4 bytes
            
            # Create header
            flags = 0x01 if compressed else 0x00
            header = struct.pack(
                '<4s B B H I 4s',
                cls.MAGIC_BYTES,      # Magic bytes (4)
                cls.VERSION,          # Version (1)
                msg_type,             # Message type (1)
                flags,                # Flags (2)
                len(payload),         # Payload length (4)
                payload_hash          # Payload hash (4)
            )
            
            return header + payload
            
        except Exception as e:
            logger.error(f"Failed to create message: {e}")
            return cls.create_error_message(f"Message creation failed: {e}")
    
    @classmethod
    def parse_message(cls, data: bytes) -> Tuple[Optional[MessageType], Optional[Dict], str]:
        """Parse a protocol message"""
        try:
            if len(data) < cls.HEADER_SIZE:
                return None, None, "Incomplete header"
            
            # Parse header
            header = struct.unpack('<4s B B H I 4s', data[:cls.HEADER_SIZE])
            magic, version, msg_type, flags, payload_len, payload_hash = header
            
            # Validate magic bytes and version
            if magic != cls.MAGIC_BYTES:
                return None, None, "Invalid magic bytes"
            
            if version != cls.VERSION:
                return None, None, f"Unsupported version: {version}"
            
            # Check if we have complete message
            total_len = cls.HEADER_SIZE + payload_len
            if len(data) < total_len:
                return None, None, "Incomplete payload"
            
            # Extract payload
            payload = data[cls.HEADER_SIZE:total_len]
            
            # Verify payload hash
            calculated_hash = hashlib.sha256(payload).digest()[:4]
            if calculated_hash != payload_hash:
                return None, None, "Payload hash mismatch"
            
            # Decompress if needed
            if flags & 0x01:  # Compressed flag
                try:
                    payload = zlib.decompress(payload)
                except Exception as e:
                    return None, None, f"Decompression failed: {e}"
            
            # Parse JSON payload
            try:
                json_data = json.loads(payload.decode('utf-8'))
                return MessageType(msg_type), json_data, ""
            except json.JSONDecodeError as e:
                return None, None, f"JSON parse error: {e}"
                
        except struct.error as e:
            return None, None, f"Header parse error: {e}"
        except Exception as e:
            return None, None, f"Parse error: {e}"
    
    @classmethod
    def create_error_message(cls, error_msg: str) -> bytes:
        """Create an error message"""
        return cls.create_message(MessageType.ERROR, {"error": error_msg}, compress=False)

class NodeManager:
    """Manages connected mining nodes"""
    
    def __init__(self):
        self.nodes: Dict[str, NodeInfo] = {}
        self.work_queue: List[MiningWork] = []
        self.active_work: Dict[str, MiningWork] = {}
        self.completed_work: List[WorkResult] = []
        self.stats_lock = asyncio.Lock()
        
    def register_node(self, node_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Register a new mining node"""
        try:
            node_id = node_data.get("node_id")
            if not node_id:
                return False, "Node ID required"
            
            # Create node info
            node_info = NodeInfo(
                node_id=node_id,
                hostname=node_data.get("hostname", "unknown"),
                ip_address=node_data.get("ip_address", "0.0.0.0"),
                port=node_data.get("port", 0),
                license_key=node_data.get("license_key", ""),
                capabilities=node_data.get("capabilities", {}),
                system_specs=node_data.get("system_specs", {}),
                connected_time=time.time(),
                last_heartbeat=time.time()
            )
            
            self.nodes[node_id] = node_info
            logger.info(f"✅ Node registered: {node_id} ({node_info.hostname})")
            
            return True, "Node registered successfully"
            
        except Exception as e:
            logger.error(f"Node registration failed: {e}")
            return False, str(e)
    
    def update_heartbeat(self, node_id: str) -> bool:
        """Update node heartbeat"""
        if node_id in self.nodes:
            self.nodes[node_id].last_heartbeat = time.time()
            return True
        return False
    
    def disconnect_node(self, node_id: str) -> bool:
        """Disconnect a mining node"""
        if node_id in self.nodes:
            self.nodes[node_id].status = "disconnected"
            # Reassign any active work from this node
            self._reassign_work_from_node(node_id)
            logger.info(f"🔌 Node disconnected: {node_id}")
            return True
        return False
    
    def get_node_stats(self) -> Dict[str, Any]:
        """Get aggregate node statistics"""
        total_nodes = len(self.nodes)
        active_nodes = len([n for n in self.nodes.values() if n.status == "connected"])
        
        # Aggregate capabilities
        total_cpu_cores = 0
        total_gpus = 0
        total_ram_gb = 0
        
        for node in self.nodes.values():
            if node.status == "connected":
                specs = node.system_specs
                total_cpu_cores += specs.get("cpu_cores", 0)
                total_gpus += specs.get("total_gpus", 0)
                total_ram_gb += specs.get("ram_gb", 0)
        
        return {
            "total_nodes": total_nodes,
            "active_nodes": active_nodes,
            "inactive_nodes": total_nodes - active_nodes,
            "aggregate_stats": {
                "total_cpu_cores": total_cpu_cores,
                "total_gpus": total_gpus,
                "total_ram_gb": total_ram_gb
            },
            "work_stats": {
                "queued_work": len(self.work_queue),
                "active_work": len(self.active_work),
                "completed_work": len(self.completed_work)
            }
        }
    
    def create_mining_work(self, coin_config: Dict, wallet_address: str, 
                          total_nonce_space: int = 10000000) -> List[MiningWork]:
        """Create work assignments for distributed mining"""
        work_assignments = []
        active_nodes = [n for n in self.nodes.values() if n.status == "connected"]
        
        if not active_nodes:
            return work_assignments
        
        # Calculate work distribution based on node capabilities
        nonce_per_node = total_nonce_space // len(active_nodes)
        current_nonce = 0
        
        for i, node in enumerate(active_nodes):
            # Adjust work size based on node capabilities
            node_cores = node.system_specs.get("cpu_cores", 1)
            node_gpus = node.system_specs.get("total_gpus", 0)
            
            # Scale work based on processing power
            scale_factor = max(1.0, (node_cores / 4) + (node_gpus * 2))
            adjusted_nonce_range = int(nonce_per_node * scale_factor)
            
            work = MiningWork(
                work_id=f"work_{int(time.time())}_{i}",
                coin_config=coin_config,
                wallet_address=wallet_address,
                start_nonce=current_nonce,
                nonce_range=adjusted_nonce_range,
                difficulty_target="00000000",  # Simplified
                timestamp=time.time(),
                assigned_node=node.node_id
            )
            
            work_assignments.append(work)
            self.work_queue.append(work)
            current_nonce += adjusted_nonce_range
        
        logger.info(f"📋 Created {len(work_assignments)} work assignments for {len(active_nodes)} nodes")
        return work_assignments
    
    def _reassign_work_from_node(self, node_id: str):
        """Reassign work from disconnected node"""
        work_to_reassign = []
        
        # Find work assigned to this node
        for work_id, work in self.active_work.items():
            if work.assigned_node == node_id:
                work_to_reassign.append(work_id)
        
        # Move back to queue for reassignment
        for work_id in work_to_reassign:
            work = self.active_work.pop(work_id)
            work.assigned_node = None
            self.work_queue.append(work)
        
        if work_to_reassign:
            logger.info(f"♻️  Reassigned {len(work_to_reassign)} work items from node {node_id}")

# ============================================================================
# GPU MINING ENGINE
# ============================================================================

class CUDAMiner:
    """NVIDIA CUDA mining implementation"""
    
    def __init__(self, gpu_id: int, gpu_info: Dict):
        self.gpu_id = gpu_id
        self.gpu_info = gpu_info
        self.is_mining = False
        self.stats = GPUMiningStats(
            gpu_id=gpu_id,
            gpu_type="NVIDIA",
            gpu_name=gpu_info["name"]
        )
        self.mining_thread = None
        self.start_time = None
    
    def cuda_scrypt_hash(self, data: bytes, n: int = 1024) -> bytes:
        """CUDA-optimized Scrypt hash (simplified simulation)"""
        # In production, this would use actual CUDA kernels
        # For now, simulating GPU performance with optimized CPU hash
        return hashlib.scrypt(data, salt=data, n=n, r=1, p=1, dklen=32)
    
    def mine_worker(self, coin_config: Dict, wallet_address: str):
        """CUDA mining worker thread"""
        self.is_mining = True
        self.start_time = time.time()
        self.stats.is_mining = True
        
        nonce = self.gpu_id * 1000000  # Offset nonce by GPU ID
        hash_count = 0
        
        logger.info(f"🚀 CUDA Mining started on GPU {self.gpu_id}: {self.gpu_info['name']}")
        
        while self.is_mining:
            try:
                # Create work for this GPU
                timestamp = int(time.time())
                header_data = f"{wallet_address}{timestamp}{nonce}".encode('utf-8')
                
                # CUDA-optimized hash (simulated)
                hash_result = self.cuda_scrypt_hash(header_data, coin_config.get('scrypt_n', 1024))
                hash_count += 1
                
                # Check for successful hash (simplified)
                if hash_result.hex()[:6] == "000000":
                    self.stats.accepted_shares += 1
                    logger.info(f"🎯 CUDA GPU {self.gpu_id} found share: {hash_result.hex()[:16]}...")
                
                # Update statistics
                current_time = time.time()
                if current_time - self.start_time > 0:
                    self.stats.uptime = current_time - self.start_time
                    self.stats.hashrate = hash_count / self.stats.uptime
                
                # GPU temperature and power monitoring (simulated)
                self.stats.temperature = self._get_gpu_temperature()
                self.stats.power_draw = self._get_gpu_power()
                
                nonce += 1
                
                # Simulate GPU processing time (much faster than CPU)
                if nonce % 10000 == 0:  # GPU can handle much higher throughput
                    time.sleep(0.001)  # Very short sleep for GPU
                    
            except Exception as e:
                logger.error(f"CUDA mining error on GPU {self.gpu_id}: {e}")
                self.stats.rejected_shares += 1
    
    def start_mining(self, coin_config: Dict, wallet_address: str) -> bool:
        """Start CUDA mining"""
        if self.is_mining:
            return False
        
        self.mining_thread = threading.Thread(
            target=self.mine_worker,
            args=(coin_config, wallet_address),
            daemon=True
        )
        self.mining_thread.start()
        return True
    
    def stop_mining(self) -> bool:
        """Stop CUDA mining"""
        if not self.is_mining:
            return False
        
        self.is_mining = False
        self.stats.is_mining = False
        if self.mining_thread and self.mining_thread.is_alive():
            self.mining_thread.join(timeout=5)
        
        logger.info(f"🛑 CUDA mining stopped on GPU {self.gpu_id}")
        return True
    
    def _get_gpu_temperature(self) -> Optional[int]:
        """Get NVIDIA GPU temperature via nvidia-smi"""
        try:
            result = subprocess.run([
                'nvidia-smi', '--query-gpu=temperature.gpu',
                '--format=csv,noheader,nounits', f'--id={self.gpu_id}'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                temp = result.stdout.strip()
                return int(temp) if temp.isdigit() else None
        except:
            pass
        return None
    
    def _get_gpu_power(self) -> Optional[float]:
        """Get NVIDIA GPU power draw via nvidia-smi"""
        try:
            result = subprocess.run([
                'nvidia-smi', '--query-gpu=power.draw',
                '--format=csv,noheader,nounits', f'--id={self.gpu_id}'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                power = result.stdout.strip()
                return float(power) if power.replace('.', '').isdigit() else None
        except:
            pass
        return None

class OpenCLMiner:
    """AMD OpenCL mining implementation"""
    
    def __init__(self, gpu_id: int, gpu_info: Dict):
        self.gpu_id = gpu_id
        self.gpu_info = gpu_info
        self.is_mining = False
        self.stats = GPUMiningStats(
            gpu_id=gpu_id,
            gpu_type="AMD",
            gpu_name=gpu_info["name"]
        )
        self.mining_thread = None
        self.start_time = None
    
    def opencl_scrypt_hash(self, data: bytes, n: int = 1024) -> bytes:
        """OpenCL-optimized Scrypt hash (simplified simulation)"""
        # In production, this would use actual OpenCL kernels
        # For now, simulating GPU performance with optimized CPU hash
        return hashlib.scrypt(data, salt=data, n=n, r=1, p=1, dklen=32)
    
    def mine_worker(self, coin_config: Dict, wallet_address: str):
        """OpenCL mining worker thread"""
        self.is_mining = True
        self.start_time = time.time()
        self.stats.is_mining = True
        
        nonce = (self.gpu_id + 1000) * 1000000  # Offset nonce by GPU ID
        hash_count = 0
        
        logger.info(f"🚀 OpenCL Mining started on GPU {self.gpu_id}: {self.gpu_info['name']}")
        
        while self.is_mining:
            try:
                # Create work for this GPU
                timestamp = int(time.time())
                header_data = f"{wallet_address}{timestamp}{nonce}".encode('utf-8')
                
                # OpenCL-optimized hash (simulated)
                hash_result = self.opencl_scrypt_hash(header_data, coin_config.get('scrypt_n', 1024))
                hash_count += 1
                
                # Check for successful hash (simplified)
                if hash_result.hex()[:6] == "000000":
                    self.stats.accepted_shares += 1
                    logger.info(f"🎯 AMD GPU {self.gpu_id} found share: {hash_result.hex()[:16]}...")
                
                # Update statistics
                current_time = time.time()
                if current_time - self.start_time > 0:
                    self.stats.uptime = current_time - self.start_time
                    self.stats.hashrate = hash_count / self.stats.uptime
                
                # GPU monitoring (simulated for AMD)
                self.stats.temperature = self._get_gpu_temperature()
                self.stats.power_draw = self._get_gpu_power()
                
                nonce += 1
                
                # Simulate GPU processing time (AMD typically slightly different performance)
                if nonce % 8000 == 0:  # AMD GPU processing simulation
                    time.sleep(0.001)
                    
            except Exception as e:
                logger.error(f"OpenCL mining error on GPU {self.gpu_id}: {e}")
                self.stats.rejected_shares += 1
    
    def start_mining(self, coin_config: Dict, wallet_address: str) -> bool:
        """Start OpenCL mining"""
        if self.is_mining:
            return False
        
        self.mining_thread = threading.Thread(
            target=self.mine_worker,
            args=(coin_config, wallet_address),
            daemon=True
        )
        self.mining_thread.start()
        return True
    
    def stop_mining(self) -> bool:
        """Stop OpenCL mining"""
        if not self.is_mining:
            return False
        
        self.is_mining = False
        self.stats.is_mining = False
        if self.mining_thread and self.mining_thread.is_alive():
            self.mining_thread.join(timeout=5)
        
        logger.info(f"🛑 OpenCL mining stopped on GPU {self.gpu_id}")
        return True
    
    def _get_gpu_temperature(self) -> Optional[int]:
        """Get AMD GPU temperature (simplified)"""
        try:
            # Try ROCm SMI for temperature
            result = subprocess.run([
                'rocm-smi', '--showtemp', f'--gpu={self.gpu_id}'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                # Parse temperature from ROCm output (simplified)
                temp_match = re.search(r'(\d+)°C', result.stdout)
                if temp_match:
                    return int(temp_match.group(1))
        except:
            pass
        return None
    
    def _get_gpu_power(self) -> Optional[float]:
        """Get AMD GPU power draw (simplified)"""
        try:
            # Try ROCm SMI for power
            result = subprocess.run([
                'rocm-smi', '--showpower', f'--gpu={self.gpu_id}'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                # Parse power from ROCm output (simplified)
                power_match = re.search(r'(\d+\.?\d*)W', result.stdout)
                if power_match:
                    return float(power_match.group(1))
        except:
            pass
        return None

class HybridGPUCPUMiner:
    """Enterprise hybrid mining engine using both GPU and CPU simultaneously"""
    
    def __init__(self, cpu_miner, hardware_validator):
        self.cpu_miner = cpu_miner
        self.hardware_validator = hardware_validator
        
        # Initialize GPU miners
        self.nvidia_miners = []
        self.amd_miners = []
        self.is_mining = False
        self.start_time = None
        
        # Detect and initialize GPUs
        self._initialize_gpu_miners()
    
    def _initialize_gpu_miners(self):
        """Initialize GPU miners for all detected GPUs"""
        # Get GPU info from hardware validator
        gpu_info = self.hardware_validator._get_gpu_info()
        
        # Initialize NVIDIA GPUs
        for i, gpu in enumerate(gpu_info.get("nvidia_gpus", [])):
            gpu_data = {"id": i, "name": gpu["name"]}
            miner = CUDAMiner(i, gpu_data)
            self.nvidia_miners.append(miner)
            logger.info(f"✅ Initialized NVIDIA CUDA miner for {gpu['name']}")
        
        # Initialize AMD GPUs  
        for i, gpu in enumerate(gpu_info.get("amd_gpus", [])):
            gpu_data = {"id": i, "name": gpu["name"]}
            miner = OpenCLMiner(i, gpu_data)
            self.amd_miners.append(miner)
            logger.info(f"✅ Initialized AMD OpenCL miner for {gpu['name']}")
        
        total_gpus = len(self.nvidia_miners) + len(self.amd_miners)
        logger.info(f"🎮 Total GPU miners initialized: {total_gpus} ({len(self.nvidia_miners)} NVIDIA, {len(self.amd_miners)} AMD)")
    
    def start_hybrid_mining(self, coin_config: Dict, wallet_address: str, cpu_threads: int = 0) -> Dict:
        """Start hybrid CPU + GPU mining"""
        if self.is_mining:
            return {"success": False, "message": "Mining already in progress"}
        
        self.is_mining = True
        self.start_time = time.time()
        results = {"cpu": False, "nvidia": 0, "amd": 0, "total_started": 0}
        
        logger.info("🚀 Starting Hybrid CPU + GPU Mining...")
        
        # Start CPU mining if threads specified
        if cpu_threads > 0:
            cpu_success, cpu_message = self.cpu_miner.start_mining(coin_config, wallet_address, cpu_threads)
            results["cpu"] = cpu_success
            if cpu_success:
                results["total_started"] += 1
                logger.info(f"✅ CPU mining started with {cpu_threads} threads")
        
        # Start all NVIDIA GPU miners
        for miner in self.nvidia_miners:
            if miner.start_mining(coin_config, wallet_address):
                results["nvidia"] += 1
                results["total_started"] += 1
        
        # Start all AMD GPU miners
        for miner in self.amd_miners:
            if miner.start_mining(coin_config, wallet_address):
                results["amd"] += 1
                results["total_started"] += 1
        
        total_miners = results["total_started"]
        success_message = f"Hybrid mining started: {results['nvidia']} NVIDIA, {results['amd']} AMD GPUs"
        if results["cpu"]:
            success_message += f", CPU ({cpu_threads} threads)"
        
        logger.info(f"🎉 {success_message}")
        
        return {
            "success": total_miners > 0,
            "message": success_message,
            "miners_started": results,
            "total_miners": total_miners
        }
    
    def stop_hybrid_mining(self) -> Dict:
        """Stop all hybrid mining operations"""
        if not self.is_mining:
            return {"success": False, "message": "No mining in progress"}
        
        self.is_mining = False
        results = {"cpu": False, "nvidia": 0, "amd": 0, "total_stopped": 0}
        
        logger.info("🛑 Stopping Hybrid Mining...")
        
        # Stop CPU mining
        try:
            cpu_success, cpu_message = self.cpu_miner.stop_mining()
            results["cpu"] = cpu_success
            if cpu_success:
                results["total_stopped"] += 1
        except:
            pass
        
        # Stop all NVIDIA GPU miners
        for miner in self.nvidia_miners:
            if miner.stop_mining():
                results["nvidia"] += 1
                results["total_stopped"] += 1
        
        # Stop all AMD GPU miners
        for miner in self.amd_miners:
            if miner.stop_mining():
                results["amd"] += 1
                results["total_stopped"] += 1
        
        success_message = f"Hybrid mining stopped: {results['nvidia']} NVIDIA, {results['amd']} AMD GPUs"
        if results["cpu"]:
            success_message += ", CPU"
        
        logger.info(f"✅ {success_message}")
        
        return {
            "success": True,
            "message": success_message,
            "miners_stopped": results,
            "total_stopped": results["total_stopped"]
        }
    
    def get_hybrid_stats(self) -> HybridMiningStats:
        """Get comprehensive mining statistics"""
        stats = HybridMiningStats()
        
        if self.start_time:
            stats.uptime = time.time() - self.start_time
        
        # Get CPU stats
        if hasattr(self.cpu_miner, 'stats'):
            stats.cpu_hashrate = self.cpu_miner.stats.hashrate
            stats.cpu_threads = getattr(self.cpu_miner, 'current_threads', 0)
        
        # Aggregate GPU stats
        nvidia_hashrate = 0
        amd_hashrate = 0
        active_gpus = 0
        
        # NVIDIA stats
        for miner in self.nvidia_miners:
            if miner.stats.is_mining:
                nvidia_hashrate += miner.stats.hashrate
                active_gpus += 1
        
        # AMD stats
        for miner in self.amd_miners:
            if miner.stats.is_mining:
                amd_hashrate += miner.stats.hashrate
                active_gpus += 1
        
        stats.nvidia_hashrate = nvidia_hashrate
        stats.amd_hashrate = amd_hashrate
        stats.gpu_hashrate = nvidia_hashrate + amd_hashrate
        stats.total_hashrate = stats.cpu_hashrate + stats.gpu_hashrate
        
        stats.nvidia_gpus = len(self.nvidia_miners)
        stats.amd_gpus = len(self.amd_miners)
        stats.total_gpus = stats.nvidia_gpus + stats.amd_gpus
        stats.active_gpus = active_gpus
        
        return stats
    
    def get_detailed_gpu_stats(self) -> List[Dict]:
        """Get detailed statistics for each GPU"""
        gpu_stats = []
        
        # NVIDIA GPU stats
        for miner in self.nvidia_miners:
            gpu_stats.append(asdict(miner.stats))
        
        # AMD GPU stats
        for miner in self.amd_miners:
            gpu_stats.append(asdict(miner.stats))
        
        return gpu_stats

# ============================================================================
# DISTRIBUTED MINING SERVER
# ============================================================================

class DistributedMiningServer:
    """Central server for distributed mining coordination"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 9001):
        self.host = host
        self.port = port
        self.server = None
        self.node_manager = NodeManager()
        self.license_system = None  # Will be injected
        self.is_running = False
        
    async def start_server(self):
        """Start the distributed mining server"""
        try:
            self.server = await asyncio.start_server(
                self.handle_client,
                self.host,
                self.port
            )
            
            self.is_running = True
            addr = self.server.sockets[0].getsockname()
            logger.info(f"🚀 V30 Distributed Mining Server started on {addr[0]}:{addr[1]}")
            
            async with self.server:
                await self.server.serve_forever()
                
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            self.is_running = False
    
    async def stop_server(self):
        """Stop the distributed mining server"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.is_running = False
            logger.info("🛑 Distributed mining server stopped")
    
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle client connection"""
        client_addr = writer.get_extra_info('peername')
        logger.info(f"🔗 New connection from {client_addr}")
        
        try:
            while True:
                # Read message header
                header_data = await reader.readexactly(V30Protocol.HEADER_SIZE)
                if not header_data:
                    break
                
                # Parse header to get payload length
                _, _, _, _, payload_len, _ = struct.unpack('<4s B B H I 4s', header_data)
                
                # Read payload
                payload_data = await reader.readexactly(payload_len)
                
                # Parse complete message
                msg_type, data, error = V30Protocol.parse_message(header_data + payload_data)
                
                if error:
                    logger.error(f"Protocol error from {client_addr}: {error}")
                    response = V30Protocol.create_error_message(error)
                    writer.write(response)
                    await writer.drain()
                    continue
                
                # Handle message
                response = await self.process_message(msg_type, data, client_addr)
                if response:
                    writer.write(response)
                    await writer.drain()
                
        except asyncio.IncompleteReadError:
            logger.info(f"🔌 Client {client_addr} disconnected")
        except Exception as e:
            logger.error(f"Error handling client {client_addr}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def process_message(self, msg_type: MessageType, data: Dict, 
                            client_addr: Tuple[str, int]) -> Optional[bytes]:
        """Process incoming protocol message"""
        try:
            if msg_type == MessageType.NODE_REGISTER:
                return await self._handle_node_register(data, client_addr)
            
            elif msg_type == MessageType.NODE_HEARTBEAT:
                return await self._handle_heartbeat(data)
            
            elif msg_type == MessageType.WORK_REQUEST:
                return await self._handle_work_request(data)
            
            elif msg_type == MessageType.WORK_RESULT:
                return await self._handle_work_result(data)
            
            elif msg_type == MessageType.STATS_REQUEST:
                return await self._handle_stats_request(data)
            
            elif msg_type == MessageType.LICENSE_VALIDATE:
                return await self._handle_license_validate(data)
            
            else:
                logger.warning(f"Unknown message type: {msg_type}")
                return V30Protocol.create_error_message(f"Unknown message type: {msg_type}")
                
        except Exception as e:
            logger.error(f"Error processing message {msg_type}: {e}")
            return V30Protocol.create_error_message(str(e))
    
    async def _handle_node_register(self, data: Dict, client_addr: Tuple[str, int]) -> bytes:
        """Handle node registration"""
        # Add client IP to node data
        data["ip_address"] = client_addr[0]
        
        # Validate license if provided
        license_key = data.get("license_key")
        if license_key and self.license_system:
            validation = self.license_system.validate_license(license_key)
            if not validation["valid"]:
                return V30Protocol.create_message(
                    MessageType.NODE_REGISTER_ACK,
                    {"success": False, "error": f"Invalid license: {validation['error']}"}
                )
        
        # Register node
        success, message = self.node_manager.register_node(data)
        
        response_data = {
            "success": success,
            "message": message,
            "server_info": {
                "version": "v30",
                "protocol_version": V30Protocol.VERSION,
                "capabilities": ["distributed_mining", "gpu_support", "load_balancing"]
            }
        }
        
        return V30Protocol.create_message(MessageType.NODE_REGISTER_ACK, response_data)
    
    async def _handle_heartbeat(self, data: Dict) -> bytes:
        """Handle node heartbeat"""
        node_id = data.get("node_id")
        if node_id and self.node_manager.update_heartbeat(node_id):
            return V30Protocol.create_message(
                MessageType.NODE_HEARTBEAT_ACK,
                {"success": True, "timestamp": time.time()}
            )
        else:
            return V30Protocol.create_error_message("Node not found")
    
    async def _handle_work_request(self, data: Dict) -> bytes:
        """Handle work request from node"""
        node_id = data.get("node_id")
        
        if not node_id or node_id not in self.node_manager.nodes:
            return V30Protocol.create_error_message("Invalid node ID")
        
        # Find available work
        if self.node_manager.work_queue:
            work = self.node_manager.work_queue.pop(0)
            work.assigned_node = node_id
            self.node_manager.active_work[work.work_id] = work
            
            return V30Protocol.create_message(
                MessageType.WORK_ASSIGNMENT,
                asdict(work)
            )
        else:
            return V30Protocol.create_message(
                MessageType.WORK_ASSIGNMENT,
                {"no_work": True, "message": "No work available"}
            )
    
    async def _handle_work_result(self, data: Dict) -> bytes:
        """Handle work result from node"""
        try:
            work_result = WorkResult(**data)
            self.node_manager.completed_work.append(work_result)
            
            # Remove from active work
            if work_result.work_id in self.node_manager.active_work:
                del self.node_manager.active_work[work_result.work_id]
            
            logger.info(f"📊 Work result received: {work_result.work_id} from {work_result.node_id}")
            
            return V30Protocol.create_message(
                MessageType.WORK_COMPLETE,
                {"success": True, "work_id": work_result.work_id}
            )
            
        except Exception as e:
            return V30Protocol.create_error_message(f"Invalid work result: {e}")
    
    async def _handle_stats_request(self, data: Dict) -> bytes:
        """Handle statistics request"""
        stats = self.node_manager.get_node_stats()
        return V30Protocol.create_message(MessageType.STATS_RESPONSE, stats)
    
    async def _handle_license_validate(self, data: Dict) -> bytes:
        """Handle license validation request"""
        license_key = data.get("license_key")
        
        if not license_key or not self.license_system:
            return V30Protocol.create_message(
                MessageType.LICENSE_RESPONSE,
                {"valid": False, "error": "No license system available"}
            )
        
        validation = self.license_system.validate_license(license_key)
        return V30Protocol.create_message(MessageType.LICENSE_RESPONSE, validation)

# ============================================================================
# CENTRAL CONTROL SYSTEM
# ============================================================================

class CentralControlSystem:
    """
    Central control system for V30 distributed mining operations
    """
    
    def __init__(self):
        self.is_running = False
        self.distributed_server = None
        self.connected_nodes = {}
        self.system_stats = {}
        self.enterprise_features = [
            "distributed_mining",
            "gpu_acceleration", 
            "license_management",
            "load_balancing",
            "auto_failover",
            "real_time_monitoring"
        ]
    
    async def initialize_system(self) -> Dict[str, Any]:
        """Initialize the V30 central control system"""
        try:
            logger.info("Initializing V30 Enterprise Central Control System...")
            
            # Initialize distributed server
            self.distributed_server = DistributedMiningServer()
            
            # Mark as running
            self.is_running = True
            
            # Update system stats
            await self._update_system_stats()
            
            logger.info("V30 Central Control System initialized successfully")
            
            return {
                "success": True,
                "message": "V30 Enterprise system initialized successfully",
                "features_enabled": len(self.enterprise_features),
                "features": self.enterprise_features,
                "initialization_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"V30 system initialization failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initialize V30 system"
            }
    
    async def start_distributed_mining(self, coin_config: Dict, wallet_address: str, include_local: bool = True) -> Dict[str, Any]:
        """Start distributed mining across connected nodes"""
        try:
            if not self.is_running:
                return {
                    "success": False,
                    "error": "V30 system not initialized"
                }
            
            logger.info(f"Starting distributed mining for {coin_config.get('symbol', 'Unknown')} coin")
            
            # Start local mining if requested
            if include_local:
                from backend.mining_engine import mining_engine, CoinConfig
                
                local_coin_config = CoinConfig(**coin_config)
                success, message = mining_engine.start_mining(
                    local_coin_config,
                    wallet_address,
                    threads=32  # Enterprise default
                )
                
                if not success:
                    logger.warning(f"Local mining start failed: {message}")
            
            # Update stats
            await self._update_system_stats()
            
            return {
                "success": True,
                "message": "Distributed mining started successfully",
                "local_mining": include_local,
                "connected_nodes": len(self.connected_nodes),
                "coin": coin_config.get('symbol', 'Unknown'),
                "wallet": wallet_address
            }
            
        except Exception as e:
            logger.error(f"Failed to start distributed mining: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop_distributed_mining(self) -> Dict[str, Any]:
        """Stop distributed mining across all nodes"""
        try:
            logger.info("Stopping distributed mining...")
            
            # Stop local mining
            from backend.mining_engine import mining_engine
            mining_engine.stop_mining()
            
            # Update stats
            await self._update_system_stats()
            
            return {
                "success": True,
                "message": "Distributed mining stopped successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to stop distributed mining: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "system_status": {
                "initialized": self.is_running,
                "uptime": "N/A",
                "version": "30.0.0"
            },
            "statistics": self.system_stats,
            "server_info": {
                "hostname": socket.gethostname(),
                "connected_nodes": len(self.connected_nodes),
                "enterprise_features": len(self.enterprise_features)
            },
            "capabilities": {
                "distributed_mining": True,
                "gpu_acceleration": True,
                "license_management": True
            }
        }
    
    async def shutdown_system(self):
        """Shutdown the V30 system gracefully"""
        try:
            logger.info("Shutting down V30 Central Control System...")
            
            # Stop distributed mining
            await self.stop_distributed_mining()
            
            # Mark as not running
            self.is_running = False
            
            logger.info("V30 Central Control System shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during V30 system shutdown: {e}")
    
    async def _update_system_stats(self):
        """Update system statistics"""
        try:
            self.system_stats = {
                "last_updated": datetime.utcnow().isoformat(),
                "connected_nodes": len(self.connected_nodes),
                "total_memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "cpu_cores": psutil.cpu_count(logical=True),
                "enterprise_features_active": len(self.enterprise_features)
            }
        except Exception as e:
            logger.error(f"Failed to update system stats: {e}")

# Export consolidated classes
__all__ = [
    # License System
    'EnterpriseV30License',
    # Hardware Validation
    'EnterpriseHardwareValidator', 
    # Central Control
    'CentralControlSystem',
    # Protocol System
    'V30Protocol',
    'NodeManager',
    'DistributedMiningServer',
    'MessageType',
    'NodeInfo',
    'MiningWork',
    'WorkResult',
    # GPU Mining System
    'CUDAMiner',
    'OpenCLMiner',
    'HybridGPUCPUMiner',
    'GPUMiningStats',
    'HybridMiningStats'
]