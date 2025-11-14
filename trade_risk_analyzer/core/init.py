"""
Initialization utilities for Trade Risk Analyzer
"""

from typing import Optional
from .config import ConfigManager, Config, init_config
from .logger import LoggerFactory, init_logging, get_logger


def initialize_system(config_path: Optional[str] = None) -> Config:
    """
    Initialize the Trade Risk Analyzer system
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Config instance
    """
    # Load configuration
    config = init_config(config_path)
    
    # Initialize logging
    logging_config = {
        'level': config.logging.level,
        'format': config.logging.format,
        'output': config.logging.output,
    }
    init_logging(logging_config)
    
    # Log initialization
    logger = get_logger(__name__)
    logger.info("Trade Risk Analyzer initialized", 
                config_path=config_path or "default",
                log_level=config.logging.level)
    
    return config
