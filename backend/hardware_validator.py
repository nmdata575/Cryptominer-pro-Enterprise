"""
CryptoMiner Enterprise V30 - Hardware Validation System
Validates enterprise hardware requirements and GPU detection
"""

import psutil
import subprocess
import re
import socket
import time
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class EnterpriseHardwareValidator:
    def __init__(self):
        self.min_ram_gb = 64
        self.recommended_ram_gb = 512
        self.min_cpu_cores = 32
        self.min_network_speed_mbps = 1000  # 1 Gbps
        
    def validate_memory(self) -> Dict:
        """Validate RAM requirements"""
        memory = psutil.virtual_memory()
        total_ram_gb = memory.total / (1024**3)
        available_ram_gb = memory.available / (1024**3)
        
        meets_minimum = total_ram_gb >= self.min_ram_gb
        meets_recommended = total_ram_gb >= self.recommended_ram_gb
        
        return {
            "total_ram_gb": round(total_ram_gb, 2),
            "available_ram_gb": round(available_ram_gb, 2),
            "meets_minimum": meets_minimum,
            "meets_recommended": meets_recommended,
            "requirement_minimum": self.min_ram_gb,
            "requirement_recommended": self.recommended_ram_gb,
            "status": "✅ PASSED" if meets_minimum else "❌ FAILED",
            "message": self._get_memory_message(total_ram_gb, meets_minimum, meets_recommended)
        }
    
    def validate_cpu(self) -> Dict:
        """Validate CPU core requirements"""
        logical_cores = psutil.cpu_count(logical=True)
        physical_cores = psutil.cpu_count(logical=False) or logical_cores
        
        meets_minimum = logical_cores >= self.min_cpu_cores
        
        # Get CPU info
        cpu_info = self._get_cpu_info()
        
        return {
            "logical_cores": logical_cores,
            "physical_cores": physical_cores,
            "meets_minimum": meets_minimum,
            "requirement_minimum": self.min_cpu_cores,
            "cpu_model": cpu_info.get("model", "Unknown"),
            "cpu_frequency": cpu_info.get("frequency", "Unknown"),
            "status": "✅ PASSED" if meets_minimum else "❌ FAILED",
            "message": self._get_cpu_message(logical_cores, meets_minimum)
        }
    
    def detect_nvidia_gpus(self) -> List[Dict]:
        """Detect NVIDIA GPUs using nvidia-smi"""
        gpus = []
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,driver_version,uuid,temperature.gpu,power.draw', 
                                   '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        parts = [part.strip() for part in line.split(',')]
                        if len(parts) >= 4:
                            gpus.append({
                                "id": i,
                                "type": "NVIDIA",
                                "name": parts[0],
                                "memory_mb": int(parts[1]) if parts[1].isdigit() else 0,
                                "memory_gb": round(int(parts[1]) / 1024, 2) if parts[1].isdigit() else 0,
                                "driver_version": parts[2] if len(parts) > 2 else "Unknown",
                                "uuid": parts[3] if len(parts) > 3 else "Unknown",
                                "temperature": int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else None,
                                "power_draw": float(parts[5]) if len(parts) > 5 and parts[5].replace('.','').isdigit() else None,
                                "cuda_capable": True
                            })
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return gpus
    
    def detect_amd_gpus(self) -> List[Dict]:
        """Detect AMD GPUs using rocm-smi or system info"""
        gpus = []
        
        # Try ROCm SMI first
        try:
            result = subprocess.run(['rocm-smi', '--showproductname', '--showmeminfo', 'vram'], 
                                   capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                gpu_id = 0
                for line in lines:
                    if 'Card series:' in line or 'GPU' in line:
                        # Parse ROCm output (simplified)
                        gpus.append({
                            "id": gpu_id,
                            "type": "AMD",
                            "name": f"AMD GPU {gpu_id}",
                            "memory_mb": 0,  # Would need more complex parsing
                            "memory_gb": 0,
                            "driver_version": "ROCm",
                            "uuid": f"amd-gpu-{gpu_id}",
                            "temperature": None,
                            "power_draw": None,
                            "opencl_capable": True
                        })
                        gpu_id += 1
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Fallback: try lspci for AMD GPUs
        if not gpus:
            try:
                result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    gpu_id = 0
                    for line in result.stdout.split('\n'):
                        if 'VGA' in line and ('AMD' in line or 'ATI' in line or 'Radeon' in line):
                            # Extract GPU name from lspci output
                            match = re.search(r':\s*(.+?)(?:\[|$)', line)
                            gpu_name = match.group(1).strip() if match else f"AMD GPU {gpu_id}"
                            
                            gpus.append({
                                "id": gpu_id,
                                "type": "AMD",
                                "name": gpu_name,
                                "memory_mb": 0,  # Cannot determine from lspci
                                "memory_gb": 0,
                                "driver_version": "Unknown",
                                "uuid": f"amd-gpu-{gpu_id}",
                                "temperature": None,
                                "power_draw": None,
                                "opencl_capable": True
                            })
                            gpu_id += 1
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                pass
        
        return gpus
    
    def validate_network(self) -> Dict:
        """Validate network speed requirements"""
        # This is a simplified check - in production you'd want more comprehensive testing
        interfaces = psutil.net_if_stats()
        
        max_speed_mbps = 0
        active_interfaces = []
        
        for interface_name, stats in interfaces.items():
            if stats.isup and stats.speed > 0:
                speed_mbps = stats.speed
                if speed_mbps >= self.min_network_speed_mbps:
                    active_interfaces.append({
                        "name": interface_name,
                        "speed_mbps": speed_mbps,
                        "speed_gbps": round(speed_mbps / 1000, 2)
                    })
                max_speed_mbps = max(max_speed_mbps, speed_mbps)
        
        meets_minimum = max_speed_mbps >= self.min_network_speed_mbps
        
        return {
            "max_speed_mbps": max_speed_mbps,
            "max_speed_gbps": round(max_speed_mbps / 1000, 2),
            "meets_minimum": meets_minimum,
            "requirement_minimum_mbps": self.min_network_speed_mbps,
            "requirement_minimum_gbps": self.min_network_speed_mbps / 1000,
            "active_interfaces": active_interfaces,
            "status": "✅ PASSED" if meets_minimum else "❌ FAILED",
            "message": self._get_network_message(max_speed_mbps, meets_minimum)
        }
    
    def comprehensive_validation(self) -> Dict:
        """Run complete enterprise hardware validation"""
        print("🔍 Running Enterprise Hardware Validation...")
        
        # Memory validation
        memory_result = self.validate_memory()
        print(f"💾 Memory: {memory_result['status']} - {memory_result['message']}")
        
        # CPU validation
        cpu_result = self.validate_cpu()
        print(f"🖥️  CPU: {cpu_result['status']} - {cpu_result['message']}")
        
        # GPU detection
        nvidia_gpus = self.detect_nvidia_gpus()
        amd_gpus = self.detect_amd_gpus()
        total_gpus = len(nvidia_gpus) + len(amd_gpus)
        
        print(f"🎮 GPU Detection:")
        print(f"   NVIDIA GPUs: {len(nvidia_gpus)}")
        for gpu in nvidia_gpus:
            print(f"     - {gpu['name']} ({gpu['memory_gb']}GB)")
        print(f"   AMD GPUs: {len(amd_gpus)}")
        for gpu in amd_gpus:
            print(f"     - {gpu['name']}")
        
        # Network validation
        network_result = self.validate_network()
        print(f"🌐 Network: {network_result['status']} - {network_result['message']}")
        
        # Overall enterprise readiness
        enterprise_ready = (
            memory_result["meets_minimum"] and 
            cpu_result["meets_minimum"] and 
            network_result["meets_minimum"]
        )
        
        print(f"\n🏢 Enterprise Readiness: {'✅ READY' if enterprise_ready else '❌ NOT READY'}")
        
        return {
            "enterprise_ready": enterprise_ready,
            "validation_timestamp": time.time(),
            "memory": memory_result,
            "cpu": cpu_result,
            "network": network_result,
            "gpus": {
                "nvidia": nvidia_gpus,
                "amd": amd_gpus,
                "total_count": total_gpus,
                "nvidia_count": len(nvidia_gpus),
                "amd_count": len(amd_gpus)
            },
            "summary": {
                "total_ram_gb": memory_result["total_ram_gb"],
                "total_cpu_cores": cpu_result["logical_cores"],
                "total_gpus": total_gpus,
                "max_network_gbps": network_result["max_speed_gbps"],
                "enterprise_features_available": enterprise_ready
            }
        }
    
    def _get_memory_message(self, total_ram_gb: float, meets_min: bool, meets_rec: bool) -> str:
        if meets_rec:
            return f"{total_ram_gb:.1f}GB RAM (Exceeds recommended {self.recommended_ram_gb}GB)"
        elif meets_min:
            return f"{total_ram_gb:.1f}GB RAM (Meets minimum {self.min_ram_gb}GB)"
        else:
            return f"{total_ram_gb:.1f}GB RAM (Below minimum {self.min_ram_gb}GB required)"
    
    def _get_cpu_message(self, cores: int, meets_min: bool) -> str:
        if meets_min:
            return f"{cores} cores (Meets minimum {self.min_cpu_cores} cores)"
        else:
            return f"{cores} cores (Below minimum {self.min_cpu_cores} cores required)"
    
    def _get_network_message(self, speed_mbps: float, meets_min: bool) -> str:
        if meets_min:
            return f"{speed_mbps/1000:.1f} Gbps (Meets minimum 1 Gbps)"
        else:
            return f"{speed_mbps/1000:.1f} Gbps (Below minimum 1 Gbps required)"
    
    def _get_cpu_info(self) -> Dict:
        """Get detailed CPU information"""
        cpu_info = {"model": "Unknown", "frequency": "Unknown"}
        
        try:
            # Try to get CPU model from /proc/cpuinfo
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                
            model_match = re.search(r'model name\s*:\s*(.+)', cpuinfo)
            if model_match:
                cpu_info["model"] = model_match.group(1).strip()
                
            # Get frequency
            freq_info = psutil.cpu_freq()
            if freq_info:
                cpu_info["frequency"] = f"{freq_info.max:.0f} MHz"
                
        except Exception:
            pass
        
        return cpu_info

# Test hardware validation when run directly
if __name__ == "__main__":
    validator = EnterpriseHardwareValidator()
    results = validator.comprehensive_validation()
    
    print(f"\n📊 Validation Summary:")
    print(f"   Enterprise Ready: {results['enterprise_ready']}")
    print(f"   Total RAM: {results['summary']['total_ram_gb']:.1f} GB")
    print(f"   Total CPU Cores: {results['summary']['total_cpu_cores']}")
    print(f"   Total GPUs: {results['summary']['total_gpus']}")
    print(f"   Max Network: {results['summary']['max_network_gbps']:.1f} Gbps")