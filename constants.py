"""
CryptoMiner V21 - Constants and Configuration Values
Centralized location for all constants used throughout the application
"""

# Application Information
APP_NAME = "CryptoMiner V21"
APP_VERSION = "21.0.0"
APP_DESCRIPTION = "Enterprise-scale distributed mining platform"

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
DEFAULT_WEB_PORT = 8001
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
    }
}

# Default Mining Pools
DEFAULT_POOLS = {
    'LTC': [
        {'name': 'LitecoinPool', 'url': 'stratum+tcp://stratum.litecoinpool.org:3333'},
        {'name': 'F2Pool', 'url': 'stratum+tcp://ltc.f2pool.com:4444'},
        {'name': 'ViaBTC', 'url': 'stratum+tcp://ltc.viabtc.com:3333'}
    ],
    'DOGE': [
        {'name': 'F2Pool', 'url': 'stratum+tcp://doge.f2pool.com:4444'},
        {'name': 'ViaBTC', 'url': 'stratum+tcp://doge.viabtc.com:3333'}
    ],
    'MULTI': [
        {'name': 'Prohashing', 'url': 'stratum+tcp://prohashing.com:3333'}
    ]
}

# File and Path Constants
DEFAULT_CONFIG_FILE = 'mining_config.env'
CONFIG_TEMPLATE_FILE = 'mining_config.template'
DEFAULT_LOG_FILE = 'mining.log'
AI_MODEL_FILE = 'ai_mining_model.pkl'
AI_SCALER_FILE = 'ai_scaler.pkl'

# Banner and Display
BANNER = """
╔══════════════════════════════════════════════════════════╗
║              🚀 CryptoMiner Pro V30 🚀                  ║
║           Compact Terminal Mining Application            ║
║                                                         ║
║  ⚡ Enterprise Mining Engine    🤖 AI Optimization     ║
║  🔗 Pool & Solo Support         📊 Web Monitoring      ║
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