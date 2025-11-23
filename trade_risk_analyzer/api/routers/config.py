"""
Configuration Router

Endpoints for managing system configuration.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

from trade_risk_analyzer.core.logger import get_logger

# Placeholder imports
try:
    from trade_risk_analyzer.core.config import Config
except ImportError:
    Config = None

router = APIRouter()
logger = get_logger(__name__)


class ConfigUpdate(BaseModel):
    """Configuration update request"""
    detection_thresholds: Optional[Dict[str, Any]] = None
    model_parameters: Optional[Dict[str, Any]] = None
    monitoring_settings: Optional[Dict[str, Any]] = None


@router.get("")
async def get_config():
    """
    Get current system configuration
    
    Returns all configuration settings including:
    - Detection thresholds
    - Model parameters
    - Monitoring settings
    - Database configuration
    """
    try:
        if Config is None:
            raise HTTPException(status_code=501, detail="Configuration module not yet implemented")
        
        config = Config()
        
        return {
            "detection_thresholds": {
                "wash_trading": {
                    "time_window_seconds": config.get("detection.wash_trading.time_window", 300),
                    "min_probability": config.get("detection.wash_trading.min_probability", 0.7)
                },
                "pump_and_dump": {
                    "volume_spike_multiplier": config.get("detection.pump_and_dump.volume_multiplier", 3.0),
                    "price_change_threshold": config.get("detection.pump_and_dump.price_threshold", 0.2)
                },
                "hft_manipulation": {
                    "max_trades_per_minute": config.get("detection.hft.max_trades_per_minute", 100),
                    "layering_threshold": config.get("detection.hft.layering_threshold", 5)
                }
            },
            "model_parameters": {
                "isolation_forest": {
                    "n_estimators": config.get("models.isolation_forest.n_estimators", 100),
                    "contamination": config.get("models.isolation_forest.contamination", 0.1)
                },
                "random_forest": {
                    "n_estimators": config.get("models.random_forest.n_estimators", 100),
                    "max_depth": config.get("models.random_forest.max_depth", 10)
                },
                "autoencoder": {
                    "encoding_dim": config.get("models.autoencoder.encoding_dim", 32),
                    "epochs": config.get("models.autoencoder.epochs", 50)
                }
            },
            "monitoring_settings": {
                "check_interval_seconds": config.get("monitoring.check_interval", 60),
                "max_concurrent_markets": config.get("monitoring.max_concurrent", 10),
                "alert_cooldown_seconds": config.get("monitoring.alert_cooldown", 300)
            },
            "database": {
                "url": config.get("database.url", "sqlite:///trade_risk.db"),
                "pool_size": config.get("database.pool_size", 5)
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving configuration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve configuration: {str(e)}")


@router.put("")
async def update_config(update: ConfigUpdate):
    """
    Update system configuration
    
    - **detection_thresholds**: Update detection algorithm thresholds
    - **model_parameters**: Update ML model parameters
    - **monitoring_settings**: Update monitoring behavior settings
    
    Changes are applied immediately without requiring restart.
    """
    try:
        config = Config()
        updated_fields = []
        
        # Update detection thresholds
        if update.detection_thresholds:
            for key, value in update.detection_thresholds.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        config_key = f"detection.{key}.{sub_key}"
                        config.set(config_key, sub_value)
                        updated_fields.append(config_key)
                else:
                    config_key = f"detection.{key}"
                    config.set(config_key, value)
                    updated_fields.append(config_key)
        
        # Update model parameters
        if update.model_parameters:
            for model_name, params in update.model_parameters.items():
                for param_name, param_value in params.items():
                    config_key = f"models.{model_name}.{param_name}"
                    config.set(config_key, param_value)
                    updated_fields.append(config_key)
        
        # Update monitoring settings
        if update.monitoring_settings:
            for key, value in update.monitoring_settings.items():
                config_key = f"monitoring.{key}"
                config.set(config_key, value)
                updated_fields.append(config_key)
        
        # Save configuration
        config.save()
        
        logger.info(f"Configuration updated: {updated_fields}")
        
        return {
            "status": "success",
            "message": "Configuration updated successfully",
            "updated_fields": updated_fields
        }
        
    except Exception as e:
        logger.error(f"Error updating configuration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")


@router.post("/reset")
async def reset_config():
    """
    Reset configuration to default values
    
    This will restore all settings to their default values.
    Use with caution in production environments.
    """
    try:
        config = Config()
        config.reset_to_defaults()
        config.save()
        
        logger.warning("Configuration reset to defaults")
        
        return {
            "status": "success",
            "message": "Configuration reset to default values"
        }
        
    except Exception as e:
        logger.error(f"Error resetting configuration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to reset configuration: {str(e)}")
