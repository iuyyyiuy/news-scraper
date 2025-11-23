"""
Alert Generation and Management System

Handles alert generation, deduplication, storage, and retrieval with detailed explanations.
"""

import pandas as pd
import hashlib
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import asdict

from trade_risk_analyzer.core.base import Alert, RiskLevel, PatternType
from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage


logger = get_logger(__name__)


class AlertManager:
    """
    Manages alert generation, deduplication, and storage
    """
    
    def __init__(self, storage: Optional[DatabaseStorage] = None,
                 deduplication_window_hours: int = 24):
        """
        Initialize alert manager
        
        Args:
            storage: Database storage instance
            deduplication_window_hours: Time window for deduplication (hours)
        """
        self.storage = storage
        self.deduplication_window_hours = deduplication_window_hours
        self.logger = logger
        
        # Cache for recent alerts (for deduplication)
        self._alert_cache: Dict[str, Alert] = {}
        self._cache_expiry: Dict[str, datetime] = {}
    
    def generate_alert(
        self,
        user_id: str,
        trade_ids: List[str],
        anomaly_score: float,
        risk_level: RiskLevel,
        pattern_type: PatternType,
        explanation: str,
        recommended_action: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Alert:
        """
        Generate a new alert with detailed information
        
        Args:
            user_id: User ID associated with the alert
            trade_ids: List of trade IDs involved
            anomaly_score: Anomaly score (0-100)
            risk_level: Risk level classification
            pattern_type: Type of pattern detected
            explanation: Detailed explanation of the alert
            recommended_action: Recommended action for the alert
            additional_context: Additional context information
            
        Returns:
            Generated Alert object
        """
        timestamp = datetime.now()
        
        # Generate unique alert ID
        alert_id = self._generate_alert_id(
            user_id, pattern_type, timestamp, trade_ids
        )
        
        # Enhance explanation with additional context
        enhanced_explanation = self._enhance_explanation(
            explanation, additional_context
        )
        
        # Create alert
        alert = Alert(
            alert_id=alert_id,
            timestamp=timestamp,
            user_id=user_id,
            trade_ids=trade_ids,
            anomaly_score=anomaly_score,
            risk_level=risk_level,
            pattern_type=pattern_type,
            explanation=enhanced_explanation,
            recommended_action=recommended_action
        )
        
        self.logger.info(
            f"Generated alert {alert_id} for user {user_id} "
            f"(pattern: {pattern_type.value}, risk: {risk_level.value})"
        )
        
        return alert
    
    def save_alert(self, alert: Alert, check_duplicate: bool = True) -> bool:
        """
        Save alert to database with optional deduplication
        
        Args:
            alert: Alert to save
            check_duplicate: Whether to check for duplicates
            
        Returns:
            True if saved, False if duplicate or error
        """
        # Check for duplicates
        if check_duplicate and self._is_duplicate(alert):
            self.logger.info(
                f"Alert {alert.alert_id} is a duplicate, skipping save"
            )
            return False
        
        # Save to database
        if self.storage:
            success = self.storage.save_alert(alert)
            
            if success:
                # Add to cache
                self._add_to_cache(alert)
                self.logger.info(f"Alert {alert.alert_id} saved successfully")
            else:
                self.logger.error(f"Failed to save alert {alert.alert_id}")
            
            return success
        else:
            self.logger.warning("No storage configured, alert not saved")
            return False
    
    def save_alerts_batch(
        self,
        alerts: List[Alert],
        check_duplicates: bool = True
    ) -> Dict[str, int]:
        """
        Save multiple alerts with deduplication
        
        Args:
            alerts: List of alerts to save
            check_duplicates: Whether to check for duplicates
            
        Returns:
            Dictionary with counts: {'saved': n, 'duplicates': n, 'errors': n}
        """
        results = {'saved': 0, 'duplicates': 0, 'errors': 0}
        
        self.logger.info(f"Saving batch of {len(alerts)} alerts")
        
        for alert in alerts:
            if check_duplicates and self._is_duplicate(alert):
                results['duplicates'] += 1
                continue
            
            if self.save_alert(alert, check_duplicate=False):
                results['saved'] += 1
            else:
                results['errors'] += 1
        
        self.logger.info(
            f"Batch save complete: {results['saved']} saved, "
            f"{results['duplicates']} duplicates, {results['errors']} errors"
        )
        
        return results
    
    def get_alerts(
        self,
        user_id: Optional[str] = None,
        risk_level: Optional[RiskLevel] = None,
        pattern_type: Optional[PatternType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        is_reviewed: Optional[bool] = None,
        limit: Optional[int] = None
    ) -> List[Alert]:
        """
        Retrieve alerts with filters
        
        Args:
            user_id: Filter by user ID
            risk_level: Filter by risk level
            pattern_type: Filter by pattern type
            start_date: Filter by start date
            end_date: Filter by end date
            is_reviewed: Filter by review status
            limit: Maximum number of alerts to return
            
        Returns:
            List of alerts matching filters
        """
        if not self.storage:
            self.logger.warning("No storage configured")
            return []
        
        # Build filters
        filters = {}
        if user_id:
            filters['user_id'] = user_id
        if risk_level:
            filters['risk_level'] = risk_level.value
        if pattern_type:
            filters['pattern_type'] = pattern_type.value
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        if is_reviewed is not None:
            filters['is_reviewed'] = is_reviewed
        if limit:
            filters['limit'] = limit
        
        alerts = self.storage.get_alerts(filters)
        
        self.logger.info(f"Retrieved {len(alerts)} alerts with filters: {filters}")
        
        return alerts
    
    def update_alert_review(
        self,
        alert_id: str,
        is_true_positive: bool,
        reviewer_notes: Optional[str] = None
    ) -> bool:
        """
        Update alert review status
        
        Args:
            alert_id: Alert ID to update
            is_true_positive: Whether the alert is a true positive
            reviewer_notes: Optional reviewer notes
            
        Returns:
            Success status
        """
        if not self.storage:
            self.logger.warning("No storage configured")
            return False
        
        # Get the alert
        alerts = self.storage.get_alerts({'alert_id': alert_id})
        
        if not alerts:
            self.logger.warning(f"Alert {alert_id} not found")
            return False
        
        alert = alerts[0]
        alert.is_reviewed = True
        alert.is_true_positive = is_true_positive
        alert.reviewer_notes = reviewer_notes
        
        # Save updated alert
        success = self.storage.save_alert(alert)
        
        if success:
            self.logger.info(f"Alert {alert_id} review updated")
        else:
            self.logger.error(f"Failed to update alert {alert_id}")
        
        return success
    
    def get_alert_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get alert statistics for a time period
        
        Args:
            start_date: Start date for statistics
            end_date: End date for statistics
            
        Returns:
            Dictionary with statistics
        """
        if not self.storage:
            self.logger.warning("No storage configured")
            return {}
        
        # Get all alerts in the period
        filters = {}
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        
        alerts = self.storage.get_alerts(filters)
        
        # Calculate statistics
        stats = {
            'total_alerts': len(alerts),
            'by_risk_level': {},
            'by_pattern_type': {},
            'by_user': {},
            'reviewed_count': 0,
            'true_positive_count': 0,
            'false_positive_count': 0,
            'average_anomaly_score': 0.0
        }
        
        if not alerts:
            return stats
        
        # Count by risk level
        for risk_level in RiskLevel:
            count = sum(1 for a in alerts if a.risk_level == risk_level)
            stats['by_risk_level'][risk_level.value] = count
        
        # Count by pattern type
        for pattern_type in PatternType:
            count = sum(1 for a in alerts if a.pattern_type == pattern_type)
            stats['by_pattern_type'][pattern_type.value] = count
        
        # Count by user (top 10)
        user_counts = {}
        for alert in alerts:
            user_counts[alert.user_id] = user_counts.get(alert.user_id, 0) + 1
        
        top_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        stats['by_user'] = dict(top_users)
        
        # Review statistics
        stats['reviewed_count'] = sum(1 for a in alerts if a.is_reviewed)
        stats['true_positive_count'] = sum(
            1 for a in alerts if a.is_true_positive is True
        )
        stats['false_positive_count'] = sum(
            1 for a in alerts if a.is_true_positive is False
        )
        
        # Average anomaly score
        stats['average_anomaly_score'] = sum(
            a.anomaly_score for a in alerts
        ) / len(alerts)
        
        self.logger.info(f"Generated statistics for {len(alerts)} alerts")
        
        return stats
    
    def _generate_alert_id(
        self,
        user_id: str,
        pattern_type: PatternType,
        timestamp: datetime,
        trade_ids: List[str]
    ) -> str:
        """
        Generate unique alert ID
        
        Args:
            user_id: User ID
            pattern_type: Pattern type
            timestamp: Timestamp
            trade_ids: Trade IDs
            
        Returns:
            Unique alert ID
        """
        # Create hash from key components
        hash_input = f"{user_id}_{pattern_type.value}_{timestamp.isoformat()}"
        
        # Add trade IDs to hash (sorted for consistency)
        if trade_ids:
            sorted_trades = sorted(trade_ids)
            hash_input += "_" + "_".join(sorted_trades[:5])  # Use first 5 trades
        
        # Generate hash
        hash_obj = hashlib.sha256(hash_input.encode())
        hash_hex = hash_obj.hexdigest()[:16]
        
        # Create readable ID
        alert_id = f"{pattern_type.value.lower()}_{user_id}_{hash_hex}"
        
        return alert_id
    
    def _enhance_explanation(
        self,
        base_explanation: str,
        additional_context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Enhance explanation with additional context
        
        Args:
            base_explanation: Base explanation text
            additional_context: Additional context information
            
        Returns:
            Enhanced explanation
        """
        if not additional_context:
            return base_explanation
        
        explanation_parts = [base_explanation]
        
        # Add context information
        if 'trade_count' in additional_context:
            explanation_parts.append(
                f"Number of trades involved: {additional_context['trade_count']}"
            )
        
        if 'time_window' in additional_context:
            explanation_parts.append(
                f"Time window: {additional_context['time_window']}"
            )
        
        if 'threshold_exceeded' in additional_context:
            explanation_parts.append(
                f"Threshold exceeded: {additional_context['threshold_exceeded']}"
            )
        
        if 'feature_values' in additional_context:
            feature_values = additional_context['feature_values']
            if isinstance(feature_values, dict):
                feature_str = ", ".join(
                    f"{k}: {v:.2f}" if isinstance(v, float) else f"{k}: {v}"
                    for k, v in list(feature_values.items())[:3]
                )
                explanation_parts.append(f"Key metrics: {feature_str}")
        
        return ". ".join(explanation_parts)
    
    def _is_duplicate(self, alert: Alert) -> bool:
        """
        Check if alert is a duplicate
        
        Args:
            alert: Alert to check
            
        Returns:
            True if duplicate, False otherwise
        """
        # Clean expired cache entries
        self._clean_cache()
        
        # Generate deduplication key
        dedup_key = self._generate_dedup_key(alert)
        
        # Check cache - look for all alerts with same key
        for cached_key, cached_alert in self._alert_cache.items():
            # Check if alerts are similar enough to be considered duplicates
            if self._are_alerts_similar(alert, cached_alert):
                self.logger.debug(
                    f"Alert is duplicate of {cached_alert.alert_id}"
                )
                return True
        
        return False
    
    def _generate_dedup_key(self, alert: Alert) -> str:
        """
        Generate deduplication key for alert
        
        Args:
            alert: Alert
            
        Returns:
            Deduplication key
        """
        # Key based on user and pattern type only (time checked separately)
        key = f"{alert.user_id}_{alert.pattern_type.value}"
        
        return key
    
    def _are_alerts_similar(self, alert1: Alert, alert2: Alert) -> bool:
        """
        Check if two alerts are similar enough to be duplicates
        
        Args:
            alert1: First alert
            alert2: Second alert
            
        Returns:
            True if similar, False otherwise
        """
        # Must have same user and pattern type
        if alert1.user_id != alert2.user_id:
            return False
        
        if alert1.pattern_type != alert2.pattern_type:
            return False
        
        # Must be within deduplication window
        time_diff = abs((alert1.timestamp - alert2.timestamp).total_seconds())
        if time_diff > self.deduplication_window_hours * 3600:
            return False
        
        # Check trade overlap
        trades1 = set(alert1.trade_ids) if alert1.trade_ids else set()
        trades2 = set(alert2.trade_ids) if alert2.trade_ids else set()
        
        if not trades1 and not trades2:
            return True  # If no trades in both, consider similar
        
        if not trades1 or not trades2:
            return False  # If one has trades and other doesn't, not similar
        
        # Calculate overlap percentage
        overlap = len(trades1 & trades2)
        min_size = min(len(trades1), len(trades2))
        
        overlap_pct = overlap / min_size if min_size > 0 else 0
        
        # Consider duplicate if >=50% overlap
        return overlap_pct >= 0.5
    
    def _add_to_cache(self, alert: Alert) -> None:
        """
        Add alert to cache for deduplication
        
        Args:
            alert: Alert to cache
        """
        dedup_key = self._generate_dedup_key(alert)
        self._alert_cache[dedup_key] = alert
        
        # Set expiry time
        expiry = alert.timestamp + timedelta(
            hours=self.deduplication_window_hours
        )
        self._cache_expiry[dedup_key] = expiry
    
    def _clean_cache(self) -> None:
        """Clean expired entries from cache"""
        now = datetime.now()
        expired_keys = [
            key for key, expiry in self._cache_expiry.items()
            if expiry < now
        ]
        
        for key in expired_keys:
            del self._alert_cache[key]
            del self._cache_expiry[key]
        
        if expired_keys:
            self.logger.debug(f"Cleaned {len(expired_keys)} expired cache entries")
    
    def clear_cache(self) -> None:
        """Clear all cached alerts"""
        self._alert_cache.clear()
        self._cache_expiry.clear()
        self.logger.info("Alert cache cleared")
