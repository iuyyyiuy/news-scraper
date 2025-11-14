"""
Streaming Analysis Module

Handles real-time trade processing with sliding window analysis,
Redis integration for caching, and near real-time alert generation.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Callable, Deque
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque
import time
import threading
import json

from trade_risk_analyzer.core.base import Trade, Alert, DetectionResult
from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.detection.engine import DetectionEngine, DetectionConfig
from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage


logger = get_logger(__name__)


@dataclass
class StreamingConfig:
    """
    Configuration for streaming processor
    """
    # Sliding window settings
    window_size_minutes: int = 5
    slide_interval_seconds: int = 30
    max_window_size: int = 10000
    
    # Processing settings
    batch_size: int = 100
    min_trades_for_analysis: int = 10
    
    # Alert settings
    alert_threshold_score: float = 50.0
    enable_immediate_alerts: bool = True
    
    # Redis settings
    enable_redis: bool = False
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_db: int = 0
    redis_key_prefix: str = 'trade_risk:'
    redis_ttl_seconds: int = 3600
    
    # Auto-processing settings
    enable_auto_processing: bool = False
    auto_process_interval_seconds: int = 30


@dataclass
class StreamingStatistics:
    """
    Statistics for streaming processor
    """
    trades_processed: int = 0
    windows_analyzed: int = 0
    alerts_generated: int = 0
    last_analysis_time: Optional[datetime] = None
    average_analysis_time_ms: float = 0.0
    current_window_size: int = 0
    errors: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'trades_processed': self.trades_processed,
            'windows_analyzed': self.windows_analyzed,
            'alerts_generated': self.alerts_generated,
            'last_analysis_time': self.last_analysis_time.isoformat() if self.last_analysis_time else None,
            'average_analysis_time_ms': self.average_analysis_time_ms,
            'current_window_size': self.current_window_size,
            'errors': self.errors
        }


class SlidingWindow:
    """
    Sliding window for maintaining recent trades
    """
    
    def __init__(self, window_size_minutes: int = 5, max_size: int = 10000):
        """
        Initialize sliding window
        
        Args:
            window_size_minutes: Size of the time window in minutes
            max_size: Maximum number of trades to keep
        """
        self.window_size_minutes = window_size_minutes
        self.max_size = max_size
        self.trades: Deque[Trade] = deque(maxlen=max_size)
        self.logger = logger
        self._lock = threading.Lock()
    
    def add_trade(self, trade: Trade) -> None:
        """
        Add trade to window
        
        Args:
            trade: Trade to add
        """
        with self._lock:
            self.trades.append(trade)
            
            # Remove old trades if window is full
            if len(self.trades) >= self.max_size:
                self._remove_old_trades()
    
    def add_trades_batch(self, trades: List[Trade]) -> None:
        """
        Add multiple trades to window
        
        Args:
            trades: List of trades to add
        """
        with self._lock:
            for trade in trades:
                self.trades.append(trade)
            
            # Remove old trades if needed
            if len(self.trades) >= self.max_size:
                self._remove_old_trades()
    
    def get_window_trades(self, reference_time: Optional[datetime] = None) -> List[Trade]:
        """
        Get trades within the time window
        
        Args:
            reference_time: Reference time for window (default: most recent trade time or now)
            
        Returns:
            List of trades within window
        """
        with self._lock:
            if reference_time is None:
                # Use the most recent trade's timestamp if available, otherwise now
                if self.trades:
                    reference_time = max(trade.timestamp for trade in self.trades)
                else:
                    reference_time = datetime.now()
            
            # Window goes backwards from reference time
            window_start = reference_time - timedelta(minutes=self.window_size_minutes)
            
            # Get trades within the window [window_start, reference_time]
            window_trades = [
                trade for trade in self.trades
                if window_start <= trade.timestamp <= reference_time
            ]
        
        return window_trades
    
    def get_trades_dataframe(self, reference_time: Optional[datetime] = None) -> pd.DataFrame:
        """
        Get window trades as DataFrame
        
        Args:
            reference_time: Reference time for window (default: now)
            
        Returns:
            DataFrame with trades
        """
        window_trades = self.get_window_trades(reference_time)
        
        if not window_trades:
            return pd.DataFrame()
        
        # Convert to DataFrame
        trades_data = []
        for trade in window_trades:
            trades_data.append({
                'trade_id': trade.trade_id,
                'user_id': trade.user_id,
                'timestamp': trade.timestamp,
                'symbol': trade.symbol,
                'price': trade.price,
                'volume': trade.volume,
                'trade_type': trade.trade_type.value,
                'order_id': trade.order_id
            })
        
        return pd.DataFrame(trades_data)
    
    def size(self) -> int:
        """Get current window size"""
        with self._lock:
            return len(self.trades)
    
    def clear(self) -> None:
        """Clear all trades from window"""
        with self._lock:
            self.trades.clear()
    
    def _remove_old_trades(self) -> None:
        """Remove trades older than window size"""
        if not self.trades:
            return
        
        cutoff_time = datetime.now() - timedelta(minutes=self.window_size_minutes * 2)
        
        # Remove from left (oldest)
        while self.trades and self.trades[0].timestamp < cutoff_time:
            self.trades.popleft()


class RedisCache:
    """
    Redis cache for recent trades and analysis results
    """
    
    def __init__(self, config: StreamingConfig):
        """
        Initialize Redis cache
        
        Args:
            config: Streaming configuration
        """
        self.config = config
        self.logger = logger
        self.redis_client = None
        
        if config.enable_redis:
            self._connect()
    
    def _connect(self) -> None:
        """Connect to Redis"""
        try:
            import redis
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            self.logger.info("Connected to Redis")
        except ImportError:
            self.logger.warning("Redis library not installed, caching disabled")
            self.redis_client = None
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def cache_trade(self, trade: Trade) -> bool:
        """
        Cache trade in Redis
        
        Args:
            trade: Trade to cache
            
        Returns:
            Success status
        """
        if not self.redis_client:
            return False
        
        try:
            key = f"{self.config.redis_key_prefix}trade:{trade.trade_id}"
            value = json.dumps({
                'trade_id': trade.trade_id,
                'user_id': trade.user_id,
                'timestamp': trade.timestamp.isoformat(),
                'symbol': trade.symbol,
                'price': trade.price,
                'volume': trade.volume,
                'trade_type': trade.trade_type.value,
                'order_id': trade.order_id
            })
            
            self.redis_client.setex(
                key,
                self.config.redis_ttl_seconds,
                value
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to cache trade: {e}")
            return False
    
    def get_recent_trades(self, user_id: Optional[str] = None,
                         limit: int = 1000) -> List[Trade]:
        """
        Get recent trades from cache
        
        Args:
            user_id: Filter by user ID
            limit: Maximum number of trades
            
        Returns:
            List of trades
        """
        if not self.redis_client:
            return []
        
        try:
            pattern = f"{self.config.redis_key_prefix}trade:*"
            keys = self.redis_client.keys(pattern)
            
            trades = []
            for key in keys[:limit]:
                value = self.redis_client.get(key)
                if value:
                    trade_data = json.loads(value)
                    
                    # Filter by user if specified
                    if user_id and trade_data['user_id'] != user_id:
                        continue
                    
                    # Convert to Trade object
                    from trade_risk_analyzer.core.base import TradeType
                    trade = Trade(
                        trade_id=trade_data['trade_id'],
                        user_id=trade_data['user_id'],
                        timestamp=datetime.fromisoformat(trade_data['timestamp']),
                        symbol=trade_data['symbol'],
                        price=trade_data['price'],
                        volume=trade_data['volume'],
                        trade_type=TradeType(trade_data['trade_type']),
                        order_id=trade_data['order_id']
                    )
                    trades.append(trade)
            
            return trades
        except Exception as e:
            self.logger.error(f"Failed to get recent trades: {e}")
            return []
    
    def cache_alert(self, alert: Alert) -> bool:
        """
        Cache alert in Redis
        
        Args:
            alert: Alert to cache
            
        Returns:
            Success status
        """
        if not self.redis_client:
            return False
        
        try:
            key = f"{self.config.redis_key_prefix}alert:{alert.alert_id}"
            value = json.dumps({
                'alert_id': alert.alert_id,
                'timestamp': alert.timestamp.isoformat(),
                'user_id': alert.user_id,
                'anomaly_score': alert.anomaly_score,
                'risk_level': alert.risk_level.value,
                'pattern_type': alert.pattern_type.value,
                'explanation': alert.explanation
            })
            
            self.redis_client.setex(
                key,
                self.config.redis_ttl_seconds,
                value
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to cache alert: {e}")
            return False


class StreamingProcessor:
    """
    Real-time streaming processor for trade analysis
    """
    
    def __init__(
        self,
        detection_engine: DetectionEngine,
        config: Optional[StreamingConfig] = None,
        storage: Optional[DatabaseStorage] = None
    ):
        """
        Initialize streaming processor
        
        Args:
            detection_engine: Detection engine instance
            config: Streaming configuration
            storage: Database storage for saving alerts
        """
        self.detection_engine = detection_engine
        self.config = config or StreamingConfig()
        self.storage = storage
        self.logger = logger
        
        # Initialize components
        self.sliding_window = SlidingWindow(
            window_size_minutes=self.config.window_size_minutes,
            max_size=self.config.max_window_size
        )
        
        self.redis_cache = RedisCache(self.config)
        
        # Statistics
        self.statistics = StreamingStatistics()
        
        # Callbacks
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        
        # Auto-processing
        self._auto_process_thread: Optional[threading.Thread] = None
        self._stop_auto_process = threading.Event()
        
        # Last analysis time
        self._last_analysis_time: Optional[datetime] = None
        
        self.logger.info(
            f"Streaming processor initialized with {self.config.window_size_minutes}min window"
        )
    
    def process_trade(self, trade: Trade) -> Optional[List[Alert]]:
        """
        Process a single trade in real-time
        
        Args:
            trade: Trade to process
            
        Returns:
            List of alerts if analysis triggered, None otherwise
        """
        # Add to sliding window
        self.sliding_window.add_trade(trade)
        self.statistics.trades_processed += 1
        self.statistics.current_window_size = self.sliding_window.size()
        
        # Cache in Redis if enabled
        if self.config.enable_redis:
            self.redis_cache.cache_trade(trade)
        
        # Check if we should trigger analysis
        if self.config.enable_immediate_alerts:
            if self._should_analyze():
                result = self.analyze_current_window()
                if result and result.alerts:
                    return result.alerts
        
        return None
    
    def process_trades_batch(self, trades: List[Trade]) -> Optional[DetectionResult]:
        """
        Process multiple trades at once
        
        Args:
            trades: List of trades to process
            
        Returns:
            Detection result if analysis triggered
        """
        # Add all trades to window
        self.sliding_window.add_trades_batch(trades)
        self.statistics.trades_processed += len(trades)
        self.statistics.current_window_size = self.sliding_window.size()
        
        # Cache in Redis if enabled
        if self.config.enable_redis:
            for trade in trades:
                self.redis_cache.cache_trade(trade)
        
        # Analyze window
        return self.analyze_current_window()
    
    def analyze_current_window(self, force: bool = False) -> Optional[DetectionResult]:
        """
        Analyze current sliding window
        
        Args:
            force: Force analysis even if conditions not met
            
        Returns:
            Detection result or None
        """
        # Check if we have enough trades
        if not force and self.sliding_window.size() < self.config.min_trades_for_analysis:
            return None
        
        # Get window trades as DataFrame
        trades_df = self.sliding_window.get_trades_dataframe()
        
        if trades_df.empty:
            return None
        
        start_time = time.time()
        
        try:
            # Run detection
            result = self.detection_engine.detect(trades_df, group_by='user_id')
            
            # Update statistics
            analysis_time_ms = (time.time() - start_time) * 1000
            self.statistics.windows_analyzed += 1
            self.statistics.last_analysis_time = datetime.now()
            
            # Update average analysis time
            if self.statistics.average_analysis_time_ms == 0:
                self.statistics.average_analysis_time_ms = analysis_time_ms
            else:
                self.statistics.average_analysis_time_ms = (
                    self.statistics.average_analysis_time_ms * 0.9 +
                    analysis_time_ms * 0.1
                )
            
            # Process alerts
            if result.alerts:
                self._process_alerts(result.alerts)
            
            self._last_analysis_time = datetime.now()
            
            self.logger.info(
                f"Window analysis complete: {len(result.alerts)} alerts "
                f"in {analysis_time_ms:.1f}ms"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing window: {e}", exc_info=True)
            self.statistics.errors += 1
            return None
    
    def _process_alerts(self, alerts: List[Alert]) -> None:
        """
        Process generated alerts
        
        Args:
            alerts: List of alerts to process
        """
        for alert in alerts:
            # Filter by threshold
            if alert.anomaly_score < self.config.alert_threshold_score:
                continue
            
            self.statistics.alerts_generated += 1
            
            # Cache in Redis
            if self.config.enable_redis:
                self.redis_cache.cache_alert(alert)
            
            # Save to database
            if self.storage:
                try:
                    self.detection_engine.save_alerts([alert], check_duplicates=True)
                except Exception as e:
                    self.logger.error(f"Failed to save alert: {e}")
            
            # Call callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    self.logger.error(f"Error in alert callback: {e}")
    
    def _should_analyze(self) -> bool:
        """
        Check if we should trigger analysis
        
        Returns:
            True if should analyze
        """
        # Check minimum trades
        if self.sliding_window.size() < self.config.min_trades_for_analysis:
            return False
        
        # Check time since last analysis
        if self._last_analysis_time:
            elapsed = (datetime.now() - self._last_analysis_time).total_seconds()
            if elapsed < self.config.slide_interval_seconds:
                return False
        
        return True
    
    def add_alert_callback(self, callback: Callable[[Alert], None]) -> None:
        """
        Add callback for alert notifications
        
        Args:
            callback: Function to call when alert generated
        """
        self.alert_callbacks.append(callback)
        self.logger.info("Added alert callback")
    
    def start_auto_processing(self) -> None:
        """Start automatic periodic window analysis"""
        if not self.config.enable_auto_processing:
            self.logger.warning("Auto-processing not enabled in config")
            return
        
        if self._auto_process_thread and self._auto_process_thread.is_alive():
            self.logger.warning("Auto-processing already running")
            return
        
        self._stop_auto_process.clear()
        self._auto_process_thread = threading.Thread(
            target=self._auto_process_loop,
            daemon=True
        )
        self._auto_process_thread.start()
        
        self.logger.info(
            f"Started auto-processing with {self.config.auto_process_interval_seconds}s interval"
        )
    
    def stop_auto_processing(self) -> None:
        """Stop automatic processing"""
        if not self._auto_process_thread or not self._auto_process_thread.is_alive():
            self.logger.warning("Auto-processing not running")
            return
        
        self._stop_auto_process.set()
        self._auto_process_thread.join(timeout=5)
        
        self.logger.info("Stopped auto-processing")
    
    def _auto_process_loop(self) -> None:
        """Auto-processing loop"""
        while not self._stop_auto_process.is_set():
            try:
                # Analyze current window
                self.analyze_current_window()
                
                # Wait for next interval
                self._stop_auto_process.wait(
                    timeout=self.config.auto_process_interval_seconds
                )
                
            except Exception as e:
                self.logger.error(f"Error in auto-processing loop: {e}", exc_info=True)
                self.statistics.errors += 1
    
    def get_statistics(self) -> StreamingStatistics:
        """
        Get current statistics
        
        Returns:
            StreamingStatistics
        """
        self.statistics.current_window_size = self.sliding_window.size()
        return self.statistics
    
    def reset_statistics(self) -> None:
        """Reset statistics"""
        self.statistics = StreamingStatistics()
        self.logger.info("Statistics reset")
    
    def clear_window(self) -> None:
        """Clear sliding window"""
        self.sliding_window.clear()
        self.statistics.current_window_size = 0
        self.logger.info("Sliding window cleared")
