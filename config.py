"""
CryptoMiner Pro V30 - Centralized Configuration Management
Handles all configuration loading, validation, and default values
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv


class CryptoMinerConfig:
    """Centralized configuration manager for CryptoMiner Pro V30"""
    
    # Default values
    DEFAULT_VALUES = {
        'INTENSITY': 80,
        'WEB_PORT': 8001,
        'THREADS': 'auto',
        'WEB_ENABLED': True,
        'AI_ENABLED': True,
        'AI_LEARNING_RATE': 0.1,
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': 'mining.log'
    }
    
    # Required fields for mining
    REQUIRED_FIELDS = ['COIN', 'WALLET', 'POOL']
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager"""
        self.config_file = config_file or 'mining_config.env'
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


# Global configuration instance
config = CryptoMinerConfig()