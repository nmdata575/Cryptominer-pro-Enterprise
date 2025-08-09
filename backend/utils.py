"""
CryptoMiner Pro - Utility Functions
Common utility functions for validation, formatting, and system operations
"""

import re
import hashlib
import base58
import psutil
import time
from typing import Dict, Any, Optional, Tuple, List

def validate_wallet_address(address: str, coin_symbol: str) -> Tuple[bool, str]:
    """Validate cryptocurrency wallet addresses"""
    if not address or not address.strip():
        return False, "Wallet address cannot be empty"
    
    address = address.strip()
    coin_symbol = coin_symbol.upper()
    
    try:
        if coin_symbol == "LTC":  # Litecoin
            return validate_litecoin_address(address)
        elif coin_symbol == "DOGE":  # Dogecoin
            return validate_dogecoin_address(address)
        elif coin_symbol == "FTC":  # Feathercoin
            return validate_feathercoin_address(address)
        else:
            return False, f"Unsupported coin: {coin_symbol}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def validate_litecoin_address(address: str) -> Tuple[bool, str]:
    """Validate Litecoin wallet addresses"""
    # Legacy addresses (L or M prefix)
    if address.startswith(('L', 'M')):
        if len(address) >= 26 and len(address) <= 35:
            if validate_base58_checksum(address):
                return True, "Valid Litecoin legacy address"
            else:
                return False, "Invalid Litecoin legacy address checksum"
        else:
            return False, "Invalid Litecoin legacy address length"
    
    # Bech32 addresses (ltc1 prefix)  
    elif address.startswith('ltc1'):
        if len(address) >= 39 and len(address) <= 59:
            if validate_bech32_address(address, 'ltc'):
                return True, "Valid Litecoin bech32 address"
            else:
                return False, "Invalid Litecoin bech32 address"
        else:
            return False, "Invalid Litecoin bech32 address length"
    
    # Multisig addresses (3 prefix)
    elif address.startswith('3'):
        if len(address) >= 26 and len(address) <= 35:
            if validate_base58_checksum(address):
                return True, "Valid Litecoin multisig address"
            else:
                return False, "Invalid Litecoin multisig address checksum"
        else:
            return False, "Invalid Litecoin multisig address length"
    
    else:
        return False, "Invalid Litecoin address format"

def validate_dogecoin_address(address: str) -> Tuple[bool, str]:
    """Validate Dogecoin wallet addresses"""
    # Standard addresses (D prefix)
    if address.startswith('D'):
        if len(address) >= 26 and len(address) <= 34:
            if validate_base58_checksum(address):
                return True, "Valid Dogecoin address"
            else:
                return False, "Invalid Dogecoin address checksum"
        else:
            return False, "Invalid Dogecoin address length"
    
    # Multisig addresses (9 or A prefix)
    elif address.startswith(('9', 'A')):
        if len(address) >= 26 and len(address) <= 34:
            if validate_base58_checksum(address):
                return True, "Valid Dogecoin multisig address"
            else:
                return False, "Invalid Dogecoin multisig address checksum"
        else:
            return False, "Invalid Dogecoin multisig address length"
    
    else:
        return False, "Invalid Dogecoin address format"

def validate_feathercoin_address(address: str) -> Tuple[bool, str]:
    """Validate Feathercoin wallet addresses"""
    # Standard addresses (6 or 7 prefix)
    if address.startswith(('6', '7')):
        if len(address) >= 26 and len(address) <= 34:
            if validate_base58_checksum(address):
                return True, "Valid Feathercoin address"
            else:
                return False, "Invalid Feathercoin address checksum"
        else:
            return False, "Invalid Feathercoin address length"
    
    else:
        return False, "Invalid Feathercoin address format (must start with 6 or 7)"

def validate_base58_checksum(address: str) -> bool:
    """Validate Base58Check encoded address"""
    try:
        decoded = base58.b58decode(address)
        if len(decoded) < 4:
            return False
        
        # Verify checksum
        data = decoded[:-4]
        checksum = decoded[-4:]
        hash_result = hashlib.sha256(hashlib.sha256(data).digest()).digest()
        
        return checksum == hash_result[:4]
    except Exception:
        return False

def validate_bech32_address(address: str, hrp: str) -> bool:
    """Validate Bech32 encoded address (simplified)"""
    try:
        # Basic bech32 validation
        if not address.startswith(hrp + '1'):
            return False
        
        # Check allowed characters
        allowed_chars = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
        data_part = address[len(hrp)+1:]
        
        for char in data_part.lower():
            if char not in allowed_chars:
                return False
        
        # Length check
        return len(data_part) >= 6
    except Exception:
        return False

def format_hashrate(hashrate: float) -> str:
    """Format hashrate with appropriate units"""
    if hashrate >= 1e12:
        return f"{hashrate/1e12:.2f} TH/s"
    elif hashrate >= 1e9:
        return f"{hashrate/1e9:.2f} GH/s"
    elif hashrate >= 1e6:
        return f"{hashrate/1e6:.2f} MH/s"
    elif hashrate >= 1e3:
        return f"{hashrate/1e3:.2f} KH/s"
    else:
        return f"{hashrate:.2f} H/s"

def format_uptime(seconds: float) -> str:
    """Format uptime in human readable format"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds/60)}m {int(seconds%60)}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"

def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information"""
    cpu_freq = psutil.cpu_freq()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "cpu": {
            "cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "frequency": {
                "current": cpu_freq.current if cpu_freq else 0,
                "max": cpu_freq.max if cpu_freq else 0,
                "min": cpu_freq.min if cpu_freq else 0
            },
            "usage": psutil.cpu_percent(interval=1)
        },
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percentage": memory.percent
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percentage": (disk.used / disk.total) * 100
        },
        "uptime": time.time() - psutil.boot_time()
    }

def calculate_mining_efficiency(hashrate: float, cpu_usage: float, power_usage: float = 0) -> Dict[str, float]:
    """Calculate mining efficiency metrics"""
    efficiency = {
        "hashrate_per_cpu": hashrate / cpu_usage if cpu_usage > 0 else 0,
        "efficiency_score": 0
    }
    
    if power_usage > 0:
        efficiency["hashrate_per_watt"] = hashrate / power_usage
        efficiency["efficiency_score"] = (hashrate / (cpu_usage * power_usage)) * 1000
    else:
        efficiency["efficiency_score"] = efficiency["hashrate_per_cpu"]
    
    return efficiency

def sanitize_input(input_str: str, max_length: int = 100) -> str:
    """Sanitize user input"""
    if not isinstance(input_str, str):
        return ""
    
    # Remove potentially harmful characters
    sanitized = re.sub(r'[<>"\';\\]', '', input_str)
    
    # Limit length
    return sanitized[:max_length].strip()

def validate_mining_config(config: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate mining configuration"""
    required_fields = ['coin', 'mode', 'threads']
    
    for field in required_fields:
        if field not in config:
            return False, f"Missing required field: {field}"
    
    # Validate thread count
    threads = config.get('threads', 1)
    max_threads = psutil.cpu_count()
    
    if not isinstance(threads, int) or threads < 1:
        return False, "Thread count must be a positive integer"
    
    if threads > max_threads:
        return False, f"Thread count cannot exceed system cores ({max_threads})"
    
    # Validate intensity
    intensity = config.get('intensity', 1.0)
    if not isinstance(intensity, (int, float)) or intensity <= 0 or intensity > 1:
        return False, "Intensity must be between 0 and 1"
    
    # Validate mode
    mode = config.get('mode', '').lower()
    if mode not in ['solo', 'pool']:
        return False, "Mode must be either 'solo' or 'pool'"
    
    return True, "Configuration is valid"

def get_coin_presets() -> Dict[str, Dict[str, Any]]:
    """Get predefined coin configurations"""
    return {
        "litecoin": {
            "name": "Litecoin",
            "symbol": "LTC",
            "algorithm": "Scrypt",
            "block_reward": 6.25,
            "block_time": 150,
            "difficulty": 27882939.35508488,
            "scrypt_params": {"n": 1024, "r": 1, "p": 1},
            "network_hashrate": "450 TH/s",
            "wallet_format": "L/M prefix (legacy), ltc1 (bech32), 3 (multisig)"
        },
        "dogecoin": {
            "name": "Dogecoin",
            "symbol": "DOGE", 
            "algorithm": "Scrypt",
            "block_reward": 10000.0,
            "block_time": 60,
            "difficulty": 15719073.20395687,
            "scrypt_params": {"n": 1024, "r": 1, "p": 1},
            "network_hashrate": "850 TH/s",
            "wallet_format": "D prefix (standard), 9/A prefix (multisig)"
        },
        "feathercoin": {
            "name": "Feathercoin",
            "symbol": "FTC",
            "algorithm": "Scrypt",
            "block_reward": 40.0,
            "block_time": 150,
            "difficulty": 156.89234567,
            "scrypt_params": {"n": 1024, "r": 1, "p": 1},
            "network_hashrate": "2.1 GH/s",
            "wallet_format": "6/7 prefix"
        }
    }

# Performance monitoring utilities
class PerformanceMonitor:
    def __init__(self):
        self.metrics_history = []
        self.max_history = 100
    
    def record_metrics(self, hashrate: float, cpu_usage: float, memory_usage: float, timestamp: float = None):
        """Record performance metrics"""
        if timestamp is None:
            timestamp = time.time()
        
        metrics = {
            'timestamp': timestamp,
            'hashrate': hashrate,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'efficiency': hashrate / cpu_usage if cpu_usage > 0 else 0
        }
        
        self.metrics_history.append(metrics)
        
        # Keep only recent metrics
        if len(self.metrics_history) > self.max_history:
            self.metrics_history = self.metrics_history[-self.max_history:]
    
    def get_average_metrics(self, duration_minutes: int = 5) -> Dict[str, float]:
        """Get average metrics for specified duration"""
        if not self.metrics_history:
            return {}
        
        cutoff_time = time.time() - (duration_minutes * 60)
        recent_metrics = [m for m in self.metrics_history if m['timestamp'] >= cutoff_time]
        
        if not recent_metrics:
            recent_metrics = self.metrics_history[-1:]
        
        return {
            'avg_hashrate': sum(m['hashrate'] for m in recent_metrics) / len(recent_metrics),
            'avg_cpu_usage': sum(m['cpu_usage'] for m in recent_metrics) / len(recent_metrics),
            'avg_memory_usage': sum(m['memory_usage'] for m in recent_metrics) / len(recent_metrics),
            'avg_efficiency': sum(m['efficiency'] for m in recent_metrics) / len(recent_metrics),
            'sample_count': len(recent_metrics)
        }

# Global performance monitor
performance_monitor = PerformanceMonitor()