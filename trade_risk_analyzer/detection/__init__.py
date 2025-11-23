"""
Detection Module - Applies ML models and rule-based detection for anomalies
"""

from trade_risk_analyzer.detection.wash_trading import WashTradingDetector
from trade_risk_analyzer.detection.pump_and_dump import PumpAndDumpDetector
from trade_risk_analyzer.detection.hft_manipulation import HFTManipulationDetector
from trade_risk_analyzer.detection.rule_based_detector import (
    RuleBasedDetector,
    RuleBasedThresholds,
    DetectionStats,
)
from trade_risk_analyzer.detection.engine import DetectionEngine, DetectionConfig
from trade_risk_analyzer.detection.alert_manager import AlertManager
from trade_risk_analyzer.detection.batch_processor import BatchProcessor, BatchProgress
from trade_risk_analyzer.detection.streaming_processor import (
    StreamingProcessor,
    StreamingConfig,
    StreamingStatistics,
    SlidingWindow,
    RedisCache,
)

__all__ = [
    "WashTradingDetector",
    "PumpAndDumpDetector",
    "HFTManipulationDetector",
    "RuleBasedDetector",
    "RuleBasedThresholds",
    "DetectionStats",
    "DetectionEngine",
    "DetectionConfig",
    "AlertManager",
    "BatchProcessor",
    "BatchProgress",
    "StreamingProcessor",
    "StreamingConfig",
    "StreamingStatistics",
    "SlidingWindow",
    "RedisCache",
]
