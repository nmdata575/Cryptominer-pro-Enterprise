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
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import string
import secrets
import psutil
import socket
import struct
import time
import zlib
import aiofiles

# Logging setup
logger = logging.getLogger(__name__)

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
            from v30_protocol import DistributedMiningServer
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
                from mining_engine import mining_engine, CoinConfig
                
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
            from mining_engine import mining_engine
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
    'EnterpriseV30License',
    'EnterpriseHardwareValidator', 
    'CentralControlSystem'
]