"""
Structured Logging Infrastructure
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON
        
        Args:
            record: Log record
            
        Returns:
            JSON formatted log string
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """
    Custom text formatter for human-readable logging
    """
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


class StructuredLogger:
    """
    Structured logger with support for JSON and text formats
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize structured logger
        
        Args:
            name: Logger name
            config: Logging configuration dictionary
        """
        self.logger = logging.getLogger(name)
        self.config = config or {}
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Setup logger with handlers and formatters"""
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set log level
        level = self.config.get('level', 'INFO')
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Determine format
        log_format = self.config.get('format', 'text')
        formatter = JSONFormatter() if log_format == 'json' else TextFormatter()
        
        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Add file handler if output path specified
        output_path = self.config.get('output')
        if output_path:
            # Ensure directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(output_path)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def _log_with_extra(self, level: int, message: str, **kwargs) -> None:
        """
        Log message with extra fields
        
        Args:
            level: Log level
            message: Log message
            **kwargs: Extra fields to include in log
        """
        extra = {'extra_fields': kwargs} if kwargs else {}
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message"""
        self._log_with_extra(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message"""
        self._log_with_extra(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message"""
        self._log_with_extra(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message"""
        self._log_with_extra(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message"""
        self._log_with_extra(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback"""
        extra = {'extra_fields': kwargs} if kwargs else {}
        self.logger.exception(message, extra=extra)


class LoggerFactory:
    """
    Factory for creating structured loggers
    """
    
    _loggers: Dict[str, StructuredLogger] = {}
    _config: Optional[Dict[str, Any]] = None
    
    @classmethod
    def set_config(cls, config: Dict[str, Any]) -> None:
        """
        Set global logging configuration
        
        Args:
            config: Logging configuration dictionary
        """
        cls._config = config
    
    @classmethod
    def get_logger(cls, name: str) -> StructuredLogger:
        """
        Get or create logger instance
        
        Args:
            name: Logger name
            
        Returns:
            StructuredLogger instance
        """
        if name not in cls._loggers:
            cls._loggers[name] = StructuredLogger(name, cls._config)
        
        return cls._loggers[name]
    
    @classmethod
    def reset(cls) -> None:
        """Reset all loggers"""
        cls._loggers.clear()
        cls._config = None


def get_logger(name: str) -> StructuredLogger:
    """
    Get logger instance
    
    Args:
        name: Logger name
        
    Returns:
        StructuredLogger instance
    """
    return LoggerFactory.get_logger(name)


def init_logging(config: Dict[str, Any]) -> None:
    """
    Initialize logging system with configuration
    
    Args:
        config: Logging configuration dictionary
    """
    LoggerFactory.set_config(config)
