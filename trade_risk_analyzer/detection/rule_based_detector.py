"""
Rule-Based Detector Orchestrator

Orchestrates all pattern detectors and aggregates results into unified alerts.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from trade_risk_analyzer.core.base import Alert, PatternType, RiskLevel
from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.detection.wash_trading import WashTradingDetector
from trade_risk_analyzer.detection.pump_and_dump import PumpAndDumpDetector
from trade_risk_analyzer.detection.hft_manipulation import HFTManipulationDetector


logger = get_logger(__name__)


@dataclass
class RuleBasedThresholds:
    """
    Configurable thresholds for all rule-based detectors
    """
    # Wash Trading thresholds
    wash_trading_time_window_seconds: int = 300
    wash_trading_price_tolerance: float = 0.001
    wash_trading_min_trades: int = 3
    wash_trading_circular_depth: int = 3
    
    # Pump and Dump thresholds
    pump_dump_volume_spike_threshold: float = 3.0
    pump_dump_price_increase_threshold: float = 0.5
    pump_dump_price_decline_threshold: float = 0.3
    pump_dump_lookback_days: int = 7
    pump_dump_pump_window_hours: int = 24
    pump_dump_dump_window_hours: int = 48
    pump_dump_coordinated_accounts_threshold: int = 3
    pump_dump_coordinated_time_window_minutes: int = 30
    
    # HFT Manipulation thresholds
    hft_trade_frequency_threshold: int = 100
    hft_frequency_window_hours: int = 1
    hft_cancellation_ratio_threshold: float = 0.8
    hft_quote_stuffing_threshold: int = 50
    hft_quote_stuffing_window_minutes: int = 1
    hft_layering_price_levels: int = 3
    hft_layering_time_window_seconds: int = 60
    hft_spoofing_cancel_time_seconds: int = 5
    hft_min_pattern_occurrences: int = 3


@dataclass
class DetectionStats:
    """
    Statistics from detection run
    """
    total_trades_analyzed: int = 0
    total_alerts_generated: int = 0
    alerts_by_pattern: Dict[str, int] = field(default_factory=dict)
    alerts_by_risk_level: Dict[str, int] = field(default_factory=dict)
    detection_time_seconds: float = 0.0


class RuleBasedDetector:
    """
    Orchestrator that runs all pattern detectors and aggregates results
    """
    
    def __init__(self, thresholds: Optional[RuleBasedThresholds] = None):
        """
        Initialize rule-based detector orchestrator
        
        Args:
            thresholds: Configurable thresholds for all detectors
        """
        self.thresholds = thresholds or RuleBasedThresholds()
        self.logger = logger
        
        # Initialize individual detectors with configured thresholds
        self._init_detectors()
    
    def _init_detectors(self) -> None:
        """Initialize all pattern detectors with configured thresholds"""
        self.wash_trading_detector = WashTradingDetector(
            time_window_seconds=self.thresholds.wash_trading_time_window_seconds,
            price_tolerance=self.thresholds.wash_trading_price_tolerance,
            min_wash_trades=self.thresholds.wash_trading_min_trades,
            circular_depth=self.thresholds.wash_trading_circular_depth
        )
        
        self.pump_and_dump_detector = PumpAndDumpDetector(
            volume_spike_threshold=self.thresholds.pump_dump_volume_spike_threshold,
            price_increase_threshold=self.thresholds.pump_dump_price_increase_threshold,
            price_decline_threshold=self.thresholds.pump_dump_price_decline_threshold,
            lookback_days=self.thresholds.pump_dump_lookback_days,
            pump_window_hours=self.thresholds.pump_dump_pump_window_hours,
            dump_window_hours=self.thresholds.pump_dump_dump_window_hours,
            coordinated_accounts_threshold=self.thresholds.pump_dump_coordinated_accounts_threshold,
            coordinated_time_window_minutes=self.thresholds.pump_dump_coordinated_time_window_minutes
        )
        
        self.hft_manipulation_detector = HFTManipulationDetector(
            trade_frequency_threshold=self.thresholds.hft_trade_frequency_threshold,
            frequency_window_hours=self.thresholds.hft_frequency_window_hours,
            cancellation_ratio_threshold=self.thresholds.hft_cancellation_ratio_threshold,
            quote_stuffing_threshold=self.thresholds.hft_quote_stuffing_threshold,
            quote_stuffing_window_minutes=self.thresholds.hft_quote_stuffing_window_minutes,
            layering_price_levels=self.thresholds.hft_layering_price_levels,
            layering_time_window_seconds=self.thresholds.hft_layering_time_window_seconds,
            spoofing_cancel_time_seconds=self.thresholds.hft_spoofing_cancel_time_seconds,
            min_pattern_occurrences=self.thresholds.hft_min_pattern_occurrences
        )
        
        self.logger.info("Initialized all pattern detectors with configured thresholds")
    
    def detect_all_patterns(self, trades: pd.DataFrame) -> List[Alert]:
        """
        Run all pattern detectors and aggregate results
        
        Args:
            trades: DataFrame with trade data
            
        Returns:
            List of all alerts from all detectors
        """
        import time
        start_time = time.time()
        
        self.logger.info(f"Starting rule-based detection on {len(trades)} trades")
        
        if trades.empty:
            self.logger.warning("No trades provided for detection")
            return []
        
        all_alerts = []
        
        # Run wash trading detection
        try:
            self.logger.info("Running wash trading detection...")
            wash_alerts = self.wash_trading_detector.detect(trades)
            all_alerts.extend(wash_alerts)
            self.logger.info(f"Wash trading detection completed: {len(wash_alerts)} alerts")
        except Exception as e:
            self.logger.error(f"Error in wash trading detection: {str(e)}", exc_info=True)
        
        # Run pump and dump detection
        try:
            self.logger.info("Running pump and dump detection...")
            pump_alerts = self.pump_and_dump_detector.detect(trades)
            all_alerts.extend(pump_alerts)
            self.logger.info(f"Pump and dump detection completed: {len(pump_alerts)} alerts")
        except Exception as e:
            self.logger.error(f"Error in pump and dump detection: {str(e)}", exc_info=True)
        
        # Run HFT manipulation detection
        try:
            self.logger.info("Running HFT manipulation detection...")
            hft_alerts = self.hft_manipulation_detector.detect(trades)
            all_alerts.extend(hft_alerts)
            self.logger.info(f"HFT manipulation detection completed: {len(hft_alerts)} alerts")
        except Exception as e:
            self.logger.error(f"Error in HFT manipulation detection: {str(e)}", exc_info=True)
        
        # Deduplicate alerts if needed
        all_alerts = self._deduplicate_alerts(all_alerts)
        
        detection_time = time.time() - start_time
        self.logger.info(
            f"Rule-based detection completed: {len(all_alerts)} total alerts "
            f"in {detection_time:.2f} seconds"
        )
        
        return all_alerts
    
    def detect_by_pattern(
        self, 
        trades: pd.DataFrame, 
        pattern_type: PatternType
    ) -> List[Alert]:
        """
        Run detection for a specific pattern type
        
        Args:
            trades: DataFrame with trade data
            pattern_type: Type of pattern to detect
            
        Returns:
            List of alerts for the specified pattern
        """
        self.logger.info(f"Running detection for pattern: {pattern_type.value}")
        
        if trades.empty:
            return []
        
        alerts = []
        
        try:
            if pattern_type == PatternType.WASH_TRADING:
                alerts = self.wash_trading_detector.detect(trades)
            elif pattern_type == PatternType.PUMP_AND_DUMP:
                alerts = self.pump_and_dump_detector.detect(trades)
            elif pattern_type == PatternType.HFT_MANIPULATION:
                alerts = self.hft_manipulation_detector.detect(trades)
            else:
                self.logger.warning(f"Unknown pattern type: {pattern_type.value}")
        except Exception as e:
            self.logger.error(
                f"Error detecting pattern {pattern_type.value}: {str(e)}", 
                exc_info=True
            )
        
        self.logger.info(f"Pattern detection completed: {len(alerts)} alerts")
        return alerts
    
    def get_detection_stats(self, alerts: List[Alert], total_trades: int) -> DetectionStats:
        """
        Calculate statistics from detection results
        
        Args:
            alerts: List of alerts generated
            total_trades: Total number of trades analyzed
            
        Returns:
            DetectionStats with aggregated statistics
        """
        stats = DetectionStats(
            total_trades_analyzed=total_trades,
            total_alerts_generated=len(alerts)
        )
        
        # Count alerts by pattern type
        for alert in alerts:
            pattern_name = alert.pattern_type.value
            stats.alerts_by_pattern[pattern_name] = \
                stats.alerts_by_pattern.get(pattern_name, 0) + 1
        
        # Count alerts by risk level
        for alert in alerts:
            risk_name = alert.risk_level.value
            stats.alerts_by_risk_level[risk_name] = \
                stats.alerts_by_risk_level.get(risk_name, 0) + 1
        
        return stats
    
    def update_thresholds(self, new_thresholds: RuleBasedThresholds) -> None:
        """
        Update detection thresholds and reinitialize detectors
        
        Args:
            new_thresholds: New threshold configuration
        """
        self.logger.info("Updating detection thresholds")
        self.thresholds = new_thresholds
        self._init_detectors()
        self.logger.info("Detection thresholds updated successfully")
    
    def get_thresholds(self) -> RuleBasedThresholds:
        """
        Get current threshold configuration
        
        Returns:
            Current RuleBasedThresholds
        """
        return self.thresholds
    
    def _deduplicate_alerts(self, alerts: List[Alert]) -> List[Alert]:
        """
        Remove duplicate alerts based on user_id, pattern_type, and trade overlap
        
        Args:
            alerts: List of alerts to deduplicate
            
        Returns:
            Deduplicated list of alerts
        """
        if not alerts:
            return alerts
        
        # Group alerts by user_id and pattern_type
        alert_groups: Dict[tuple, List[Alert]] = {}
        
        for alert in alerts:
            key = (alert.user_id, alert.pattern_type.value)
            if key not in alert_groups:
                alert_groups[key] = []
            alert_groups[key].append(alert)
        
        deduplicated = []
        
        for key, group_alerts in alert_groups.items():
            if len(group_alerts) == 1:
                deduplicated.append(group_alerts[0])
            else:
                # Check for overlapping trade_ids
                seen_trade_sets = []
                
                for alert in group_alerts:
                    trade_set = set(alert.trade_ids)
                    
                    # Check if this alert significantly overlaps with existing ones
                    is_duplicate = False
                    for seen_set in seen_trade_sets:
                        overlap = len(trade_set & seen_set)
                        overlap_ratio = overlap / max(len(trade_set), len(seen_set))
                        
                        # If more than 80% overlap, consider it a duplicate
                        if overlap_ratio > 0.8:
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        deduplicated.append(alert)
                        seen_trade_sets.append(trade_set)
        
        if len(deduplicated) < len(alerts):
            self.logger.info(
                f"Deduplicated {len(alerts) - len(deduplicated)} alerts "
                f"({len(alerts)} -> {len(deduplicated)})"
            )
        
        return deduplicated
    
    def create_unified_alert_format(
        self, 
        alerts: List[Alert]
    ) -> List[Dict[str, Any]]:
        """
        Convert alerts to unified dictionary format for API/reporting
        
        Args:
            alerts: List of Alert objects
            
        Returns:
            List of alert dictionaries in unified format
        """
        unified_alerts = []
        
        for alert in alerts:
            unified_alert = {
                'alert_id': alert.alert_id,
                'timestamp': alert.timestamp.isoformat(),
                'user_id': alert.user_id,
                'trade_ids': alert.trade_ids,
                'anomaly_score': round(alert.anomaly_score, 2),
                'risk_level': alert.risk_level.value,
                'pattern_type': alert.pattern_type.value,
                'explanation': alert.explanation,
                'recommended_action': alert.recommended_action,
                'is_reviewed': alert.is_reviewed,
                'is_true_positive': alert.is_true_positive,
                'reviewer_notes': alert.reviewer_notes
            }
            unified_alerts.append(unified_alert)
        
        return unified_alerts
    
    def filter_alerts(
        self,
        alerts: List[Alert],
        min_risk_level: Optional[RiskLevel] = None,
        pattern_types: Optional[List[PatternType]] = None,
        user_ids: Optional[List[str]] = None,
        min_score: Optional[float] = None
    ) -> List[Alert]:
        """
        Filter alerts based on various criteria
        
        Args:
            alerts: List of alerts to filter
            min_risk_level: Minimum risk level (filters out lower levels)
            pattern_types: List of pattern types to include
            user_ids: List of user IDs to include
            min_score: Minimum anomaly score
            
        Returns:
            Filtered list of alerts
        """
        filtered = alerts
        
        # Filter by risk level
        if min_risk_level:
            risk_order = {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 1, RiskLevel.HIGH: 2}
            min_level_value = risk_order[min_risk_level]
            filtered = [
                a for a in filtered 
                if risk_order[a.risk_level] >= min_level_value
            ]
        
        # Filter by pattern types
        if pattern_types:
            filtered = [
                a for a in filtered 
                if a.pattern_type in pattern_types
            ]
        
        # Filter by user IDs
        if user_ids:
            user_id_set = set(user_ids)
            filtered = [
                a for a in filtered 
                if a.user_id in user_id_set or 
                   any(uid in user_id_set for uid in a.user_id.split(','))
            ]
        
        # Filter by minimum score
        if min_score is not None:
            filtered = [
                a for a in filtered 
                if a.anomaly_score >= min_score
            ]
        
        self.logger.info(
            f"Filtered alerts: {len(alerts)} -> {len(filtered)} "
            f"(risk_level={min_risk_level}, patterns={pattern_types}, "
            f"users={len(user_ids) if user_ids else 'all'}, min_score={min_score})"
        )
        
        return filtered
