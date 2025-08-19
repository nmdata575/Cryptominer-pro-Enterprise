"""
CryptoMiner Pro V30 - Utility Functions
Common utility functions used throughout the application
"""

import time
import psutil
import hashlib
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from constants import SUPPORTED_COINS, VALIDATION_LIMITS

logger = logging.getLogger(__name__)


def format_uptime(seconds: float) -> str:
    """Format uptime duration into human-readable format"""
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def format_hashrate(hashrate: float) -> str:
    """Format hashrate with appropriate units"""
    if hashrate >= 1_000_000_000:
        return f"{(hashrate / 1_000_000_000):.2f} GH/s"
    elif hashrate >= 1_000_000:
        return f"{(hashrate / 1_000_000):.2f} MH/s"
    elif hashrate >= 1_000:
        return f"{(hashrate / 1_000):.2f} KH/s"
    else:
        return f"{hashrate:.2f} H/s"


def format_number(number: int) -> str:
    """Format large numbers with comma separators"""
    return f"{number:,}"


def parse_pool_url(pool_url: str) -> Tuple[str, int]:
    """Parse pool URL to extract host and port"""
    if "://" in pool_url:
        pool_url = pool_url.split("://")[1]
        
    if ":" in pool_url:
        host, port = pool_url.split(":")
        return host, int(port)
    else:
        # Default port for common protocols
        return pool_url, 4444


def validate_intensity(intensity: int) -> bool:
    """Validate mining intensity value"""
    return VALIDATION_LIMITS['INTENSITY_MIN'] <= intensity <= VALIDATION_LIMITS['INTENSITY_MAX']


def validate_threads(threads: int, max_threads: int) -> bool:
    """Validate thread count"""
    return VALIDATION_LIMITS['THREADS_MIN'] <= threads <= min(max_threads, VALIDATION_LIMITS['THREADS_MAX'])


def validate_coin(coin: str) -> bool:
    """Validate coin symbol"""
    return coin.upper() in SUPPORTED_COINS


def validate_wallet_address(wallet: str, coin: str) -> bool:
    """Basic wallet address validation"""
    if not wallet or len(wallet) < 20:
        return False
    
    # Basic format validation based on coin
    coin = coin.upper()
    if coin == 'LTC':
        return wallet.startswith(('L', 'M', '3', 'ltc1'))
    elif coin == 'DOGE':
        return wallet.startswith('D')
    elif coin == 'XMR':
        return len(wallet) == 95 and wallet.startswith('4')
    
    # Default validation for unknown coins
    return True


def calculate_max_threads() -> int:
    """Calculate maximum safe thread count based on system resources"""
    cpu_count = psutil.cpu_count()
    memory_gb = psutil.virtual_memory().total / (1024**3)
    
    # Conservative calculation for stability
    max_safe = min(
        cpu_count * 4,  # 4 threads per CPU core
        int(memory_gb * 16),  # 16 threads per GB RAM
        VALIDATION_LIMITS['THREADS_MAX']  # Enterprise limit
    )
    
    logger.info(f"Max safe threads calculated: {max_safe} (cores: {cpu_count}, memory: {memory_gb:.1f}GB)")
    return max_safe


def calculate_optimal_threads(intensity: int, max_threads: int) -> int:
    """Calculate optimal thread count based on intensity"""
    cpu_count = psutil.cpu_count()
    
    # Base calculation on CPU cores and intensity
    base_threads = max(1, int(cpu_count * (intensity / 100)))
    
    # Apply enterprise scaling
    optimal = min(base_threads, max_threads)
    
    logger.debug(f"Optimal threads for {intensity}% intensity: {optimal}")
    return optimal


def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information"""
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
        
        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(),
            'memory_total': memory.total,
            'memory_available': memory.available,
            'memory_percent': memory.percent,
            'disk_total': disk.total,
            'disk_used': disk.used,
            'disk_percent': disk.percent,
            'load_average': load_avg,
            'boot_time': psutil.boot_time()
        }
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        return {}


def create_work_template(wallet: str) -> Dict[str, str]:
    """Create a basic work template for mining"""
    timestamp = int(time.time())
    
    return {
        'version': '20000000',  # Version 2
        'prevhash': '0' * 64,
        'merkleroot': hashlib.sha256(f"{wallet}{timestamp}".encode()).hexdigest(),
        'timestamp': hex(timestamp)[2:].zfill(8),
        'bits': '1e0fffff',  # Difficulty 1 target
        'nonce': '00000000'
    }


def bits_to_target(bits_hex: str) -> int:
    """Convert difficulty bits to target value"""
    try:
        bits = int(bits_hex, 16)
        exponent = bits >> 24
        mantissa = bits & 0xffffff
        
        if exponent <= 3:
            target = mantissa >> (8 * (3 - exponent))
        else:
            target = mantissa << (8 * (exponent - 3))
            
        return target
        
    except Exception:
        return VALIDATION_LIMITS['DIFFICULTY_MIN']


def calculate_difficulty_target(difficulty: float) -> int:
    """Calculate target hash value from difficulty"""
    from constants import MAX_TARGET
    
    if difficulty <= 0:
        difficulty = 1.0
    
    return MAX_TARGET // max(1, int(difficulty))


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float with default"""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int with default"""
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def timestamp_to_string(timestamp: float) -> str:
    """Convert Unix timestamp to readable string"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def get_current_timestamp() -> str:
    """Get current timestamp as formatted string"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def calculate_acceptance_rate(accepted: int, rejected: int) -> float:
    """Calculate share acceptance rate as percentage"""
    total = accepted + rejected
    if total == 0:
        return 0.0
    return (accepted / total) * 100


def is_high_rejection_rate(accepted: int, rejected: int, threshold: float = 50.0) -> bool:
    """Check if rejection rate is above threshold"""
    total = accepted + rejected
    if total < 10:  # Not enough samples
        return False
    
    rejection_rate = (rejected / total) * 100
    return rejection_rate > threshold


def create_backup_filename(base_name: str) -> str:
    """Create backup filename with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{base_name}.backup.{timestamp}"


def log_performance_stats(hashrate: float, threads: int, accepted: int, rejected: int):
    """Log performance statistics in a standardized format"""
    acceptance_rate = calculate_acceptance_rate(accepted, rejected)
    
    logger.info("=" * 60)
    logger.info(f"📊 PERFORMANCE STATS")
    logger.info(f"Hashrate: {format_hashrate(hashrate)}")
    logger.info(f"Threads: {threads}")
    logger.info(f"Shares: ✅ {accepted} | ❌ {rejected} ({acceptance_rate:.1f}% accepted)")
    logger.info("=" * 60)


def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """Calculate exponential backoff delay"""
    delay = base_delay * (2 ** min(attempt, 10))  # Cap at 2^10
    return min(delay, max_delay)