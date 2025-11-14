"""
Configuration Management System with YAML support and environment variable substitution
"""

import os
import yaml
from typing import Any, Dict, Optional
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class DetectionThresholds:
    """Detection threshold configuration"""
    high_risk_score: float = 80.0
    medium_risk_score: float = 50.0
    hft_trades_per_hour: int = 100
    wash_trading_time_window: int = 300  # seconds
    pump_dump_volume_spike: float = 3.0  # multiplier
    pump_dump_price_change: float = 0.5  # 50%


@dataclass
class ModelWeights:
    """ML model ensemble weights"""
    isolation_forest: float = 0.3
    autoencoder: float = 0.4
    random_forest: float = 0.3


@dataclass
class DetectionConfig:
    """Detection configuration"""
    thresholds: DetectionThresholds = field(default_factory=DetectionThresholds)
    model_weights: ModelWeights = field(default_factory=ModelWeights)
    feature_windows: list = field(default_factory=lambda: ["1H", "24H", "7D"])


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = "sqlite:///trade_risk_analyzer.db"
    pool_size: int = 10
    max_overflow: int = 20


@dataclass
class RedisConfig:
    """Redis configuration"""
    url: str = "redis://localhost:6379/0"
    ttl: int = 3600


@dataclass
class APIConfig:
    """API configuration"""
    rate_limit: int = 100  # requests per minute
    max_upload_size: int = 100  # MB
    cors_origins: list = field(default_factory=lambda: ["*"])


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "json"
    output: str = "logs/app.log"


@dataclass
class Config:
    """Main configuration class"""
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    api: APIConfig = field(default_factory=APIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


class ConfigManager:
    """
    Configuration manager that loads YAML config files with environment variable support
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path or self._find_config_file()
        self._config: Optional[Config] = None
    
    def _find_config_file(self) -> str:
        """Find configuration file in standard locations"""
        search_paths = [
            "config.yaml",
            "config/config.yaml",
            "trade_risk_analyzer/config.yaml",
            os.path.expanduser("~/.trade_risk_analyzer/config.yaml"),
        ]
        
        for path in search_paths:
            if os.path.exists(path):
                return path
        
        # Return default path if none found
        return "config.yaml"
    
    def _substitute_env_vars(self, value: Any) -> Any:
        """
        Recursively substitute environment variables in configuration values
        
        Args:
            value: Configuration value (can be dict, list, or string)
            
        Returns:
            Value with environment variables substituted
        """
        if isinstance(value, str):
            # Replace ${VAR_NAME} with environment variable value
            if value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                return os.getenv(env_var, value)
            return value
        elif isinstance(value, dict):
            return {k: self._substitute_env_vars(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._substitute_env_vars(item) for item in value]
        return value
    
    def _dict_to_dataclass(self, data_class, data: Dict) -> Any:
        """
        Convert dictionary to dataclass instance
        
        Args:
            data_class: Target dataclass type
            data: Dictionary data
            
        Returns:
            Dataclass instance
        """
        if not isinstance(data, dict):
            return data
        
        field_types = {f.name: f.type for f in data_class.__dataclass_fields__.values()}
        kwargs = {}
        
        for key, value in data.items():
            if key in field_types:
                field_type = field_types[key]
                # Handle nested dataclasses
                if hasattr(field_type, '__dataclass_fields__'):
                    kwargs[key] = self._dict_to_dataclass(field_type, value)
                else:
                    kwargs[key] = value
        
        return data_class(**kwargs)
    
    def load(self) -> Config:
        """
        Load configuration from YAML file
        
        Returns:
            Config instance
        """
        if self._config is not None:
            return self._config
        
        # Load default configuration
        config_dict = self._get_default_config()
        
        # Override with file configuration if exists
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    config_dict = self._merge_configs(config_dict, file_config)
        
        # Substitute environment variables
        config_dict = self._substitute_env_vars(config_dict)
        
        # Convert to Config dataclass
        self._config = self._build_config(config_dict)
        
        return self._config
    
    def _get_default_config(self) -> Dict:
        """Get default configuration as dictionary"""
        return {
            'detection': {
                'thresholds': {
                    'high_risk_score': 80.0,
                    'medium_risk_score': 50.0,
                    'hft_trades_per_hour': 100,
                    'wash_trading_time_window': 300,
                    'pump_dump_volume_spike': 3.0,
                    'pump_dump_price_change': 0.5,
                },
                'model_weights': {
                    'isolation_forest': 0.3,
                    'autoencoder': 0.4,
                    'random_forest': 0.3,
                },
                'feature_windows': ['1H', '24H', '7D'],
            },
            'database': {
                'url': 'sqlite:///trade_risk_analyzer.db',
                'pool_size': 10,
                'max_overflow': 20,
            },
            'redis': {
                'url': 'redis://localhost:6379/0',
                'ttl': 3600,
            },
            'api': {
                'rate_limit': 100,
                'max_upload_size': 100,
                'cors_origins': ['*'],
            },
            'logging': {
                'level': 'INFO',
                'format': 'json',
                'output': 'logs/app.log',
            },
        }
    
    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """
        Recursively merge two configuration dictionaries
        
        Args:
            base: Base configuration
            override: Override configuration
            
        Returns:
            Merged configuration
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _build_config(self, config_dict: Dict) -> Config:
        """
        Build Config object from dictionary
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            Config instance
        """
        # Build nested dataclasses
        detection_config = DetectionConfig(
            thresholds=self._dict_to_dataclass(
                DetectionThresholds, 
                config_dict.get('detection', {}).get('thresholds', {})
            ),
            model_weights=self._dict_to_dataclass(
                ModelWeights,
                config_dict.get('detection', {}).get('model_weights', {})
            ),
            feature_windows=config_dict.get('detection', {}).get('feature_windows', ['1H', '24H', '7D'])
        )
        
        database_config = self._dict_to_dataclass(
            DatabaseConfig,
            config_dict.get('database', {})
        )
        
        redis_config = self._dict_to_dataclass(
            RedisConfig,
            config_dict.get('redis', {})
        )
        
        api_config = self._dict_to_dataclass(
            APIConfig,
            config_dict.get('api', {})
        )
        
        logging_config = self._dict_to_dataclass(
            LoggingConfig,
            config_dict.get('logging', {})
        )
        
        return Config(
            detection=detection_config,
            database=database_config,
            redis=redis_config,
            api=api_config,
            logging=logging_config
        )
    
    def save(self, config: Config, output_path: Optional[str] = None) -> None:
        """
        Save configuration to YAML file
        
        Args:
            config: Config instance to save
            output_path: Output file path (defaults to config_path)
        """
        output_path = output_path or self.config_path
        
        # Convert config to dictionary
        config_dict = self._config_to_dict(config)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        # Write to file
        with open(output_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
    
    def _config_to_dict(self, obj: Any) -> Any:
        """
        Convert dataclass to dictionary recursively
        
        Args:
            obj: Object to convert
            
        Returns:
            Dictionary representation
        """
        if hasattr(obj, '__dataclass_fields__'):
            return {
                key: self._config_to_dict(getattr(obj, key))
                for key in obj.__dataclass_fields__.keys()
            }
        elif isinstance(obj, list):
            return [self._config_to_dict(item) for item in obj]
        else:
            return obj
    
    def reload(self) -> Config:
        """
        Reload configuration from file
        
        Returns:
            Reloaded Config instance
        """
        self._config = None
        return self.load()


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> Config:
    """
    Get global configuration instance
    
    Returns:
        Config instance
    """
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigManager()
    
    return _config_manager.load()


def init_config(config_path: Optional[str] = None) -> Config:
    """
    Initialize configuration with custom path
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Config instance
    """
    global _config_manager
    
    _config_manager = ConfigManager(config_path)
    return _config_manager.load()
