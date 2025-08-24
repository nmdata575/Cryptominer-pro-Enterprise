"""
CryptoMiner V21 - Unified Configuration and Constants
Centralized configuration management and application constants
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# ============================================================================
# APPLICATION CONSTANTS
# ============================================================================

# Application Information
APP_NAME = "CryptoMiner V21"
APP_VERSION = "21.0.0"
APP_DESCRIPTION = "Advanced Multi-Algorithm CPU Mining Platform with AI Optimization"

# Mining Constants
DEFAULT_INTENSITY = 80
DEFAULT_THREADS_PER_CPU = 4
MAX_ENTERPRISE_THREADS = 250000
DEFAULT_DIFFICULTY = 1.0
HASHRATE_UPDATE_INTERVAL = 1.0  # seconds
STATS_DISPLAY_INTERVAL = 30  # seconds

# Network Constants
DEFAULT_POOL_PORT = 4444
POOL_CONNECTION_TIMEOUT = 120  # seconds
MAX_RETRY_ATTEMPTS = 5
RETRY_BACKOFF_MAX = 15  # seconds
POOL_RECONNECT_DELAY = 5  # seconds

# Stratum Protocol Constants
STRATUM_SUBSCRIBE_ID = 1
STRATUM_AUTHORIZE_ID = 2
STRATUM_SUGGEST_DIFFICULTY_ID = 3
STRATUM_SUBMIT_ID = 4
DEFAULT_SUGGESTED_DIFFICULTY = 1024
EXTRANONCE2_DEFAULT = "00000000"

# Mining Work Constants
NONCE_MAX_VALUE = 0xFFFFFFFF
WORK_REFRESH_INTERVAL = 30  # seconds
SHARES_PER_WORK_REFRESH = 10
HASH_UPDATE_BATCH_SIZE = 1000

# Difficulty and Target Constants
MAX_TARGET = 0x00000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
DIFFICULTY_1_TARGET = 0x00000000FFFF0000000000000000000000000000000000000000000000000000

# AI Optimization Constants
AI_OPTIMIZATION_INTERVAL = 30  # seconds
AI_TRAINING_INTERVAL = 10  # iterations
MIN_TRAINING_SAMPLES = 10
MAX_TRAINING_SAMPLES = 1000
AI_IMPROVEMENT_THRESHOLD = 5  # percent
AI_UPDATE_BATCH_SIZE = 100

# Performance Monitoring
HIGH_REJECTION_THRESHOLD = 0.5  # 50% rejection rate
MEMORY_PER_THREAD_GB = 16  # threads per GB RAM
CPU_THREADS_MULTIPLIER = 4  # threads per CPU core

# Web Monitoring Constants
WEB_UPDATE_INTERVAL = 5  # seconds
WEB_API_TIMEOUT = 5  # seconds
DEFAULT_WEB_PORT = 3333
FRONTEND_UPDATE_INTERVAL = 5000  # milliseconds

# Supported Coins
SUPPORTED_COINS = {
    'LTC': {
        'name': 'Litecoin',
        'algorithm': 'Scrypt',
        'block_time': 150,  # seconds
        'description': 'Litecoin - Scrypt algorithm'
    },
    'DOGE': {
        'name': 'Dogecoin',
        'algorithm': 'Scrypt',
        'block_time': 60,  # seconds
        'description': 'Dogecoin - Scrypt algorithm'
    },
    'VTC': {
        'name': 'Vertcoin',
        'algorithm': 'Scrypt',
        'block_time': 150,  # seconds
        'description': 'Vertcoin - Scrypt algorithm'
    },
    'XMR': {
        'name': 'Monero',
        'algorithm': 'RandomX',
        'block_time': 120,  # seconds
        'description': 'Monero - RandomX algorithm (CPU-friendly)'
    },
    'AEON': {
        'name': 'Aeon',
        'algorithm': 'RandomX',
        'block_time': 240,  # seconds
        'description': 'Aeon - RandomX algorithm (CPU-friendly)'
    }
}

# Default Mining Pools
DEFAULT_POOLS = {
    'XMR': [
        {'name': 'SupportXMR', 'url': 'stratum+tcp://pool.supportxmr.com:3333'},
        {'name': 'MonerOcean', 'url': 'stratum+tcp://gulf.moneroocean.stream:10001'},
        {'name': 'MoneroHash', 'url': 'stratum+tcp://monerohash.com:3333'}
    ],
    'LTC': [
        {'name': 'LitecoinPool', 'url': 'stratum+tcp://stratum.litecoinpool.org:3333'},
        {'name': 'F2Pool', 'url': 'stratum+tcp://ltc.f2pool.com:4444'},
        {'name': 'ViaBTC', 'url': 'stratum+tcp://ltc.viabtc.com:3333'}
    ],
    'DOGE': [
        {'name': 'F2Pool', 'url': 'stratum+tcp://doge.f2pool.com:4444'},
        {'name': 'ViaBTC', 'url': 'stratum+tcp://doge.viabtc.com:3333'}
    ]
}

# File and Path Constants
DEFAULT_CONFIG_FILE = 'mining_config.env'
CONFIG_TEMPLATE_FILE = 'mining_config.template'
DEFAULT_LOG_FILE = 'mining.log'
AI_MODEL_FILE = 'ai_mining_model.pkl'
AI_SCALER_FILE = 'ai_scaler.pkl'

# Banner and Display
BANNER = f"""
╔══════════════════════════════════════════════════════════╗
║                   🚀 {APP_NAME} 🚀                 ║
║         Advanced Multi-Algorithm CPU Mining             ║
║                                                         ║
║  ⚡ Enterprise Mining Engine    🤖 AI Optimization     ║
║  🔀 Multi-Algorithm Support    📊 Performance Tracking ║
║  🧠 Machine Learning           ⚙️ Advanced Controls    ║
╚══════════════════════════════════════════════════════════╝
"""

# Error Messages
ERROR_MESSAGES = {
    'PYTHON_VERSION': "Python 3.8 or higher is required",
    'MISSING_CONFIG': "Incomplete configuration",
    'CONNECTION_FAILED': "Failed to connect to mining pool",
    'AUTHORIZATION_FAILED': "Pool authorization failed",
    'HIGH_REJECTION': "High share rejection rate detected",
    'AI_TRAINING_FAILED': "AI model training failed",
    'WEB_UPDATE_FAILED': "Web monitoring update failed"
}

# Success Messages
SUCCESS_MESSAGES = {
    'CONFIG_LOADED': "Configuration loaded successfully",
    'POOL_CONNECTED': "Connected to mining pool",
    'AUTHORIZED': "Authorized with pool",
    'MINING_STARTED': "Mining started successfully",
    'AI_OPTIMIZED': "AI optimization applied",
    'SHARE_ACCEPTED': "Share accepted by pool"
}

# Validation Limits
VALIDATION_LIMITS = {
    'INTENSITY_MIN': 1,
    'INTENSITY_MAX': 100,
    'THREADS_MIN': 1,
    'THREADS_MAX': MAX_ENTERPRISE_THREADS,
    'WEB_PORT_MIN': 1024,
    'WEB_PORT_MAX': 65535,
    'DIFFICULTY_MIN': 0.000001,
    'DIFFICULTY_MAX': 1000000000
}

# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

class CryptoMinerConfig:
    """Centralized configuration manager for CryptoMiner V21"""
    
    # Default values
    DEFAULT_VALUES = {
        'INTENSITY': DEFAULT_INTENSITY,
        'WEB_PORT': DEFAULT_WEB_PORT,
        'THREADS': 'auto',
        'WEB_ENABLED': True,
        'AI_ENABLED': True,
        'AI_LEARNING_RATE': 0.1,
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': DEFAULT_LOG_FILE
    }
    
    # Required fields for mining
    REQUIRED_FIELDS = ['COIN', 'WALLET', 'POOL']
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager"""
        self.config_file = config_file or DEFAULT_CONFIG_FILE
        self.config = {}
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from file and environment"""
        config_path = Path(self.config_file)
        
        if config_path.exists():
            load_dotenv(config_path)
            print(f"📁 Loaded configuration from {config_path}")
        else:
            print(f"📁 No {self.config_file} found, using defaults")
        
        # Load all configuration values
        self.config = {
            'coin': os.getenv('COIN'),
            'wallet': os.getenv('WALLET'),
            'pool': os.getenv('POOL'),
            'password': os.getenv('PASSWORD'),
            'intensity': self._get_int_env('INTENSITY', self.DEFAULT_VALUES['INTENSITY']),
            'threads': self._get_threads_env(),
            'web_port': self._get_int_env('WEB_PORT', self.DEFAULT_VALUES['WEB_PORT']),
            'web_enabled': self._get_bool_env('WEB_ENABLED', self.DEFAULT_VALUES['WEB_ENABLED']),
            'ai_enabled': self._get_bool_env('AI_ENABLED', self.DEFAULT_VALUES['AI_ENABLED']),
            'ai_learning_rate': self._get_float_env('AI_LEARNING_RATE', self.DEFAULT_VALUES['AI_LEARNING_RATE']),
            'log_level': os.getenv('LOG_LEVEL', self.DEFAULT_VALUES['LOG_LEVEL']),
            'log_file': os.getenv('LOG_FILE', self.DEFAULT_VALUES['LOG_FILE'])
        }
    
    def _get_int_env(self, key: str, default: int) -> int:
        """Get integer environment variable with default"""
        try:
            value = os.getenv(key)
            return int(value) if value else default
        except (ValueError, TypeError):
            return default
    
    def _get_float_env(self, key: str, default: float) -> float:
        """Get float environment variable with default"""
        try:
            value = os.getenv(key)
            return float(value) if value else default
        except (ValueError, TypeError):
            return default
    
    def _get_bool_env(self, key: str, default: bool) -> bool:
        """Get boolean environment variable with default"""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def _get_threads_env(self) -> Optional[int]:
        """Get threads configuration with special handling for 'auto'"""
        threads = os.getenv('THREADS', self.DEFAULT_VALUES['THREADS'])
        if threads and threads.lower() != 'auto':
            try:
                return max(1, int(threads))
            except ValueError:
                return None
        return None
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def is_complete(self) -> bool:
        """Check if all required fields are present"""
        for field in self.REQUIRED_FIELDS:
            if not self.config.get(field.lower()):
                return False
        return True
    
    def get_missing_fields(self) -> list:
        """Get list of missing required fields"""
        missing = []
        for field in self.REQUIRED_FIELDS:
            if not self.config.get(field.lower()):
                missing.append(field)
        return missing
    
    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return self.config.copy()
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config['log_level'].upper(), logging.INFO)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.config['log_file'])
            ]
        )
    
    def display_config(self):
        """Display current configuration"""
        print("\n⚙️ Current Configuration:")
        print("=" * 40)
        for key, value in self.config.items():
            if key == 'password' and value:
                display_value = '*' * len(str(value))  # Hide password
            else:
                display_value = value or 'Not set'
            print(f"  {key.capitalize()}: {display_value}")
        print("=" * 40)
    
    def validate_config(self) -> Dict[str, str]:
        """Validate configuration and return errors"""
        errors = {}
        
        # Validate intensity
        intensity = self.config.get('intensity', 0)
        if not (VALIDATION_LIMITS['INTENSITY_MIN'] <= intensity <= VALIDATION_LIMITS['INTENSITY_MAX']):
            errors['intensity'] = f"Intensity must be between {VALIDATION_LIMITS['INTENSITY_MIN']} and {VALIDATION_LIMITS['INTENSITY_MAX']}"
        
        # Validate threads
        threads = self.config.get('threads')
        if threads and not (VALIDATION_LIMITS['THREADS_MIN'] <= threads <= VALIDATION_LIMITS['THREADS_MAX']):
            errors['threads'] = f"Threads must be between {VALIDATION_LIMITS['THREADS_MIN']} and {VALIDATION_LIMITS['THREADS_MAX']}"
        
        # Validate web port
        web_port = self.config.get('web_port', 0)
        if not (VALIDATION_LIMITS['WEB_PORT_MIN'] <= web_port <= VALIDATION_LIMITS['WEB_PORT_MAX']):
            errors['web_port'] = f"Web port must be between {VALIDATION_LIMITS['WEB_PORT_MIN']} and {VALIDATION_LIMITS['WEB_PORT_MAX']}"
        
        # Validate coin
        coin = self.config.get('coin', '').upper()
        if coin and coin not in SUPPORTED_COINS:
            errors['coin'] = f"Unsupported coin. Supported coins: {', '.join(SUPPORTED_COINS.keys())}"
        
        return errors
    
    def get_default_pool(self, coin: str) -> Optional[str]:
        """Get default pool for a coin"""
        coin = coin.upper()
        if coin in DEFAULT_POOLS and DEFAULT_POOLS[coin]:
            return DEFAULT_POOLS[coin][0]['url']
        return None
    
    def get_algorithm(self, coin: str) -> str:
        """Get algorithm for a coin"""
        coin = coin.upper()
        if coin in SUPPORTED_COINS:
            return SUPPORTED_COINS[coin]['algorithm']
        return 'Scrypt'  # Default fallback

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_uptime(seconds: float) -> str:
    """Format uptime seconds into human readable format"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

def format_hashrate(hashrate: float) -> str:
    """Format hashrate with appropriate units"""
    if hashrate >= 1000000000:  # GH/s
        return f"{hashrate / 1000000000:.2f} GH/s"
    elif hashrate >= 1000000:  # MH/s
        return f"{hashrate / 1000000:.2f} MH/s"
    elif hashrate >= 1000:  # KH/s
        return f"{hashrate / 1000:.2f} KH/s"
    else:
        return f"{hashrate:.2f} H/s"

def validate_pool_url(pool_url: str) -> bool:
    """Validate pool URL format"""
    if not pool_url:
        return False
    
    # Check for stratum prefix
    if not pool_url.startswith(('stratum+tcp://', 'stratum+ssl://', 'stratum://')):
        return False
    
    # Extract host:port part
    try:
        url_part = pool_url.split('://', 1)[1]
        if ':' not in url_part:
            return False
        
        host, port = url_part.split(':', 1)
        port = int(port)
        
        if not host or not (1 <= port <= 65535):
            return False
        
        return True
    except (ValueError, IndexError):
        return False

def validate_wallet_address(address: str, coin: str) -> bool:
    """Basic wallet address validation"""
    if not address or len(address) < 10:
        return False
    
    coin = coin.upper()
    
    # Basic length checks based on coin type
    if coin == 'XMR':
        return len(address) >= 95  # Monero addresses are quite long
    elif coin in ['LTC', 'DOGE']:
        return 25 <= len(address) <= 62  # Typical for Bitcoin-based coins
    
    return True  # Default to true for unknown coins

# Global configuration instance
config = CryptoMinerConfig()

# Export important symbols
__all__ = [
    'config',
    'CryptoMinerConfig',
    'APP_NAME',
    'APP_VERSION',
    'APP_DESCRIPTION',
    'BANNER',
    'SUPPORTED_COINS',
    'DEFAULT_POOLS',
    'VALIDATION_LIMITS',
    'ERROR_MESSAGES',
    'SUCCESS_MESSAGES',
    'format_uptime',
    'format_hashrate',
    'validate_pool_url',
    'validate_wallet_address'
]