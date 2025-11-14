"""
Configuration management for the news scraper.
"""
import json
import os
from typing import Optional, Dict, Any
from scraper.core.models import Config


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from JSON file or environment variables with defaults.
    
    Priority order:
    1. JSON file (if config_path provided)
    2. Environment variables
    3. Default values
    
    Args:
        config_path: Optional path to JSON configuration file
        
    Returns:
        Config object with loaded settings
        
    Raises:
        FileNotFoundError: If config_path is provided but file doesn't exist
        ValueError: If configuration is invalid
    """
    config_data: Dict[str, Any] = {}
    
    # Load from JSON file if provided
    if config_path:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config_data = json.load(f)
    
    # Override with environment variables if present
    env_config = _load_from_env()
    config_data.update(env_config)
    
    # Create Config object with defaults
    config = Config(
        target_url=config_data.get('target_url', ''),
        max_articles=config_data.get('max_articles', 10),
        request_delay=config_data.get('request_delay', 2.0),
        output_format=config_data.get('output_format', 'json'),
        output_path=config_data.get('output_path', 'scraped_articles.json'),
        timeout=config_data.get('timeout', 30),
        max_retries=config_data.get('max_retries', 3),
        selectors=config_data.get('selectors', {})
    )
    
    # Validate configuration
    config.validate()
    
    return config


def _load_from_env() -> Dict[str, Any]:
    """
    Load configuration from environment variables.
    
    Environment variables:
    - SCRAPER_TARGET_URL
    - SCRAPER_MAX_ARTICLES
    - SCRAPER_REQUEST_DELAY
    - SCRAPER_OUTPUT_FORMAT
    - SCRAPER_OUTPUT_PATH
    - SCRAPER_TIMEOUT
    - SCRAPER_MAX_RETRIES
    
    Returns:
        Dictionary with configuration values from environment
    """
    env_config: Dict[str, Any] = {}
    
    if target_url := os.getenv('SCRAPER_TARGET_URL'):
        env_config['target_url'] = target_url
    
    if max_articles := os.getenv('SCRAPER_MAX_ARTICLES'):
        env_config['max_articles'] = int(max_articles)
    
    if request_delay := os.getenv('SCRAPER_REQUEST_DELAY'):
        env_config['request_delay'] = float(request_delay)
    
    if output_format := os.getenv('SCRAPER_OUTPUT_FORMAT'):
        env_config['output_format'] = output_format
    
    if output_path := os.getenv('SCRAPER_OUTPUT_PATH'):
        env_config['output_path'] = output_path
    
    if timeout := os.getenv('SCRAPER_TIMEOUT'):
        env_config['timeout'] = int(timeout)
    
    if max_retries := os.getenv('SCRAPER_MAX_RETRIES'):
        env_config['max_retries'] = int(max_retries)
    
    return env_config


def save_config(config: Config, config_path: str) -> None:
    """
    Save configuration to JSON file.
    
    Args:
        config: Config object to save
        config_path: Path where to save the configuration file
    """
    config_data = {
        'target_url': config.target_url,
        'max_articles': config.max_articles,
        'request_delay': config.request_delay,
        'output_format': config.output_format,
        'output_path': config.output_path,
        'timeout': config.timeout,
        'max_retries': config.max_retries,
        'selectors': config.selectors
    }
    
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=2)
