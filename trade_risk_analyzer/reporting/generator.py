"""
Report Generation Module

Generates various types of reports for trade risk analysis including
daily summaries, user risk profiles, and pattern analysis reports.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict

from trade_risk_analyzer.core.base import Alert, RiskLevel, PatternType
from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage


logger = get_logger(__name__)


@dataclass
class ReportMetadata:
    """Metadata for generated reports"""
    report_id: str
    report_type: str
    generated_at: datetime
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DailySummaryReport:
    """Daily summary report data"""
    metadata: ReportMetadata
    date: datetime
    total_trades: int
    total_alerts: int
    high_risk_alerts: int
    medium_risk_alerts: int
    low_risk_alerts: int
    alerts_by_pattern: Dict[str, int]
    top_risk_users: List[Dict[str, Any]]
    average_anomaly_score: float
    alerts: List[Alert]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'metadata': {
                'report_id': self.metadata.report_id,
                'report_type': self.metadata.report_type,
                'generated_at': self.metadata.generated_at.isoformat(),
                'date': self.date.isoformat()
            },
            'summary': {
                'total_trades': self.total_trades,
                'total_alerts': self.total_alerts,
                'high_risk_alerts': self.high_risk_alerts,
                'medium_risk_alerts': self.medium_risk_alerts,
                'low_risk_alerts': self.low_risk_alerts,
                'average_anomaly_score': self.average_anomaly_score
            },
            'alerts_by_pattern': self.alerts_by_pattern,
            'top_risk_users': self.top_risk_users,
            'alerts': [
                {
                    'alert_id': a.alert_id,
                    'user_id': a.user_id,
                    'timestamp': a.timestamp.isoformat(),
                    'anomaly_score': a.anomaly_score,
                    'risk_level': a.risk_level.value,
                    'pattern_type': a.pattern_type.value,
                    'explanation': a.explanation
                }
                for a in self.alerts
            ]
        }


@dataclass
class UserRiskProfile:
    """User risk profile report data"""
    metadata: ReportMetadata
    user_id: str
    total_trades: int
    total_alerts: int
    risk_score: float
    risk_level: RiskLevel
    alerts_by_pattern: Dict[str, int]
    recent_alerts: List[Alert]
    trading_statistics: Dict[str, Any]
    risk_trend: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'metadata': {
                'report_id': self.metadata.report_id,
                'report_type': self.metadata.report_type,
                'generated_at': self.metadata.generated_at.isoformat(),
                'user_id': self.user_id
            },
            'profile': {
                'user_id': self.user_id,
                'total_trades': self.total_trades,
                'total_alerts': self.total_alerts,
                'risk_score': self.risk_score,
                'risk_level': self.risk_level.value
            },
            'alerts_by_pattern': self.alerts_by_pattern,
            'trading_statistics': self.trading_statistics,
            'risk_trend': self.risk_trend,
            'recent_alerts': [
                {
                    'alert_id': a.alert_id,
                    'timestamp': a.timestamp.isoformat(),
                    'anomaly_score': a.anomaly_score,
                    'risk_level': a.risk_level.value,
                    'pattern_type': a.pattern_type.value,
                    'explanation': a.explanation
                }
                for a in self.recent_alerts
            ]
        }


@dataclass
class PatternAnalysisReport:
    """Pattern analysis report data"""
    metadata: ReportMetadata
    pattern_type: PatternType
    total_occurrences: int
    affected_users: int
    average_severity: float
    temporal_distribution: Dict[str, int]
    user_distribution: List[Dict[str, Any]]
    examples: List[Alert]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'metadata': {
                'report_id': self.metadata.report_id,
                'report_type': self.metadata.report_type,
                'generated_at': self.metadata.generated_at.isoformat(),
                'pattern_type': self.pattern_type.value
            },
            'analysis': {
                'pattern_type': self.pattern_type.value,
                'total_occurrences': self.total_occurrences,
                'affected_users': self.affected_users,
                'average_severity': self.average_severity
            },
            'temporal_distribution': self.temporal_distribution,
            'user_distribution': self.user_distribution,
            'examples': [
                {
                    'alert_id': a.alert_id,
                    'user_id': a.user_id,
                    'timestamp': a.timestamp.isoformat(),
                    'anomaly_score': a.anomaly_score,
                    'risk_level': a.risk_level.value,
                    'explanation': a.explanation
                }
                for a in self.examples
            ]
        }


class ReportGenerator:
    """
    Main report generator class for creating various types of reports
    """
    
    def __init__(self, storage: Optional[DatabaseStorage] = None):
        """
        Initialize report generator
        
        Args:
            storage: Database storage instance for retrieving data
        """
        self.storage = storage
        self.logger = logger
    
    def generate_daily_summary(
        self,
        date: Optional[datetime] = None,
        include_alerts: bool = True
    ) -> DailySummaryReport:
        """
        Generate daily summary report
        
        Args:
            date: Date for the report (default: yesterday)
            include_alerts: Whether to include full alert details
            
        Returns:
            DailySummaryReport
        """
        if date is None:
            date = datetime.now() - timedelta(days=1)
        
        # Set date to start of day
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        self.logger.info(f"Generating daily summary report for {date.date()}")
        
        # Generate report ID
        report_id = f"daily_summary_{date.strftime('%Y%m%d')}_{int(datetime.now().timestamp())}"
        
        # Create metadata
        metadata = ReportMetadata(
            report_id=report_id,
            report_type='daily_summary',
            generated_at=datetime.now(),
            start_date=date,
            end_date=date + timedelta(days=1)
        )
        
        # Get alerts for the day
        if self.storage:
            alerts = self.storage.get_alerts({
                'start_date': date,
                'end_date': date + timedelta(days=1)
            })
        else:
            alerts = []
        
        # Get trades count for the day
        total_trades = 0
        if self.storage:
            trades_df = self.storage.get_trades_as_dataframe({
                'start_date': date,
                'end_date': date + timedelta(days=1)
            })
            total_trades = len(trades_df)
        
        # Calculate statistics
        total_alerts = len(alerts)
        high_risk_alerts = sum(1 for a in alerts if a.risk_level == RiskLevel.HIGH)
        medium_risk_alerts = sum(1 for a in alerts if a.risk_level == RiskLevel.MEDIUM)
        low_risk_alerts = sum(1 for a in alerts if a.risk_level == RiskLevel.LOW)
        
        # Count alerts by pattern
        alerts_by_pattern = {}
        for pattern_type in PatternType:
            count = sum(1 for a in alerts if a.pattern_type == pattern_type)
            if count > 0:
                alerts_by_pattern[pattern_type.value] = count
        
        # Calculate average anomaly score
        average_anomaly_score = 0.0
        if alerts:
            average_anomaly_score = sum(a.anomaly_score for a in alerts) / len(alerts)
        
        # Get top risk users
        user_scores = defaultdict(list)
        for alert in alerts:
            user_scores[alert.user_id].append(alert.anomaly_score)
        
        top_risk_users = []
        for user_id, scores in user_scores.items():
            avg_score = sum(scores) / len(scores)
            top_risk_users.append({
                'user_id': user_id,
                'alert_count': len(scores),
                'average_score': avg_score,
                'max_score': max(scores)
            })
        
        # Sort by average score and take top 10
        top_risk_users.sort(key=lambda x: x['average_score'], reverse=True)
        top_risk_users = top_risk_users[:10]
        
        # Create report
        report = DailySummaryReport(
            metadata=metadata,
            date=date,
            total_trades=total_trades,
            total_alerts=total_alerts,
            high_risk_alerts=high_risk_alerts,
            medium_risk_alerts=medium_risk_alerts,
            low_risk_alerts=low_risk_alerts,
            alerts_by_pattern=alerts_by_pattern,
            top_risk_users=top_risk_users,
            average_anomaly_score=average_anomaly_score,
            alerts=alerts if include_alerts else []
        )
        
        self.logger.info(
            f"Daily summary report generated: {total_alerts} alerts, "
            f"{high_risk_alerts} high risk"
        )
        
        return report
    
    def generate_user_risk_profile(
        self,
        user_id: str,
        days: int = 30,
        include_recent_alerts: int = 10
    ) -> UserRiskProfile:
        """
        Generate user risk profile report
        
        Args:
            user_id: User ID to analyze
            days: Number of days to analyze
            include_recent_alerts: Number of recent alerts to include
            
        Returns:
            UserRiskProfile
        """
        self.logger.info(f"Generating risk profile for user {user_id}")
        
        # Generate report ID
        report_id = f"user_profile_{user_id}_{int(datetime.now().timestamp())}"
        
        # Create metadata
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        metadata = ReportMetadata(
            report_id=report_id,
            report_type='user_risk_profile',
            generated_at=datetime.now(),
            start_date=start_date,
            end_date=end_date,
            parameters={'user_id': user_id, 'days': days}
        )
        
        # Get user alerts
        if self.storage:
            alerts = self.storage.get_alerts({
                'user_id': user_id,
                'start_date': start_date,
                'end_date': end_date
            })
        else:
            alerts = []
        
        # Get user trades
        total_trades = 0
        trading_statistics = {}
        
        if self.storage:
            trades_df = self.storage.get_trades_as_dataframe({
                'user_id': user_id,
                'start_date': start_date,
                'end_date': end_date
            })
            total_trades = len(trades_df)
            
            # Calculate trading statistics
            if not trades_df.empty:
                trading_statistics = {
                    'total_volume': float(trades_df['volume'].sum()),
                    'average_volume': float(trades_df['volume'].mean()),
                    'total_symbols': int(trades_df['symbol'].nunique()),
                    'buy_count': int((trades_df['trade_type'] == 'BUY').sum()),
                    'sell_count': int((trades_df['trade_type'] == 'SELL').sum()),
                    'first_trade': trades_df['timestamp'].min().isoformat(),
                    'last_trade': trades_df['timestamp'].max().isoformat()
                }
        
        # Calculate risk metrics
        total_alerts = len(alerts)
        
        # Calculate overall risk score (average of alert scores)
        risk_score = 0.0
        if alerts:
            risk_score = sum(a.anomaly_score for a in alerts) / len(alerts)
        
        # Determine risk level
        if risk_score >= 80:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 50:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        # Count alerts by pattern
        alerts_by_pattern = {}
        for pattern_type in PatternType:
            count = sum(1 for a in alerts if a.pattern_type == pattern_type)
            if count > 0:
                alerts_by_pattern[pattern_type.value] = count
        
        # Calculate risk trend (weekly)
        risk_trend = []
        for week in range(min(4, days // 7)):
            week_start = end_date - timedelta(days=(week + 1) * 7)
            week_end = end_date - timedelta(days=week * 7)
            
            week_alerts = [
                a for a in alerts
                if week_start <= a.timestamp < week_end
            ]
            
            week_score = 0.0
            if week_alerts:
                week_score = sum(a.anomaly_score for a in week_alerts) / len(week_alerts)
            
            risk_trend.append({
                'week': f"Week {week + 1}",
                'start_date': week_start.isoformat(),
                'end_date': week_end.isoformat(),
                'alert_count': len(week_alerts),
                'average_score': week_score
            })
        
        risk_trend.reverse()  # Most recent first
        
        # Get recent alerts
        recent_alerts = sorted(alerts, key=lambda a: a.timestamp, reverse=True)
        recent_alerts = recent_alerts[:include_recent_alerts]
        
        # Create report
        report = UserRiskProfile(
            metadata=metadata,
            user_id=user_id,
            total_trades=total_trades,
            total_alerts=total_alerts,
            risk_score=risk_score,
            risk_level=risk_level,
            alerts_by_pattern=alerts_by_pattern,
            recent_alerts=recent_alerts,
            trading_statistics=trading_statistics,
            risk_trend=risk_trend
        )
        
        self.logger.info(
            f"User risk profile generated: {total_alerts} alerts, "
            f"risk score {risk_score:.1f}"
        )
        
        return report
    
    def generate_pattern_analysis(
        self,
        pattern_type: PatternType,
        days: int = 30,
        include_examples: int = 5
    ) -> PatternAnalysisReport:
        """
        Generate pattern analysis report
        
        Args:
            pattern_type: Pattern type to analyze
            days: Number of days to analyze
            include_examples: Number of example alerts to include
            
        Returns:
            PatternAnalysisReport
        """
        self.logger.info(f"Generating pattern analysis for {pattern_type.value}")
        
        # Generate report ID
        report_id = f"pattern_analysis_{pattern_type.value}_{int(datetime.now().timestamp())}"
        
        # Create metadata
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        metadata = ReportMetadata(
            report_id=report_id,
            report_type='pattern_analysis',
            generated_at=datetime.now(),
            start_date=start_date,
            end_date=end_date,
            parameters={'pattern_type': pattern_type.value, 'days': days}
        )
        
        # Get alerts for this pattern
        if self.storage:
            all_alerts = self.storage.get_alerts({
                'pattern_type': pattern_type.value,
                'start_date': start_date,
                'end_date': end_date
            })
        else:
            all_alerts = []
        
        # Calculate statistics
        total_occurrences = len(all_alerts)
        affected_users = len(set(a.user_id for a in all_alerts))
        
        average_severity = 0.0
        if all_alerts:
            average_severity = sum(a.anomaly_score for a in all_alerts) / len(all_alerts)
        
        # Calculate temporal distribution (by day)
        temporal_distribution = {}
        for alert in all_alerts:
            day_key = alert.timestamp.strftime('%Y-%m-%d')
            temporal_distribution[day_key] = temporal_distribution.get(day_key, 0) + 1
        
        # Calculate user distribution
        user_counts = defaultdict(int)
        user_scores = defaultdict(list)
        
        for alert in all_alerts:
            user_counts[alert.user_id] += 1
            user_scores[alert.user_id].append(alert.anomaly_score)
        
        user_distribution = []
        for user_id, count in user_counts.items():
            avg_score = sum(user_scores[user_id]) / len(user_scores[user_id])
            user_distribution.append({
                'user_id': user_id,
                'occurrence_count': count,
                'average_severity': avg_score
            })
        
        # Sort by occurrence count and take top 10
        user_distribution.sort(key=lambda x: x['occurrence_count'], reverse=True)
        user_distribution = user_distribution[:10]
        
        # Get example alerts (highest severity)
        examples = sorted(all_alerts, key=lambda a: a.anomaly_score, reverse=True)
        examples = examples[:include_examples]
        
        # Create report
        report = PatternAnalysisReport(
            metadata=metadata,
            pattern_type=pattern_type,
            total_occurrences=total_occurrences,
            affected_users=affected_users,
            average_severity=average_severity,
            temporal_distribution=temporal_distribution,
            user_distribution=user_distribution,
            examples=examples
        )
        
        self.logger.info(
            f"Pattern analysis generated: {total_occurrences} occurrences, "
            f"{affected_users} users affected"
        )
        
        return report
    
    def generate_multi_day_summary(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Generate summary report for multiple days
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary with summary data
        """
        self.logger.info(
            f"Generating multi-day summary from {start_date.date()} to {end_date.date()}"
        )
        
        # Get all alerts in range
        if self.storage:
            alerts = self.storage.get_alerts({
                'start_date': start_date,
                'end_date': end_date
            })
            trades_df = self.storage.get_trades_as_dataframe({
                'start_date': start_date,
                'end_date': end_date
            })
        else:
            alerts = []
            trades_df = pd.DataFrame()
        
        # Calculate daily statistics
        daily_stats = []
        current_date = start_date
        
        while current_date < end_date:
            next_date = current_date + timedelta(days=1)
            
            day_alerts = [
                a for a in alerts
                if current_date <= a.timestamp < next_date
            ]
            
            day_trades = 0
            if not trades_df.empty:
                day_trades = len(trades_df[
                    (trades_df['timestamp'] >= current_date) &
                    (trades_df['timestamp'] < next_date)
                ])
            
            daily_stats.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'total_trades': day_trades,
                'total_alerts': len(day_alerts),
                'high_risk': sum(1 for a in day_alerts if a.risk_level == RiskLevel.HIGH),
                'medium_risk': sum(1 for a in day_alerts if a.risk_level == RiskLevel.MEDIUM),
                'low_risk': sum(1 for a in day_alerts if a.risk_level == RiskLevel.LOW)
            })
            
            current_date = next_date
        
        # Overall statistics
        total_days = (end_date - start_date).days
        total_trades = len(trades_df) if not trades_df.empty else 0
        total_alerts = len(alerts)
        
        summary = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_days': total_days
            },
            'overall': {
                'total_trades': total_trades,
                'total_alerts': total_alerts,
                'average_alerts_per_day': total_alerts / total_days if total_days > 0 else 0,
                'high_risk_alerts': sum(1 for a in alerts if a.risk_level == RiskLevel.HIGH),
                'medium_risk_alerts': sum(1 for a in alerts if a.risk_level == RiskLevel.MEDIUM),
                'low_risk_alerts': sum(1 for a in alerts if a.risk_level == RiskLevel.LOW)
            },
            'daily_breakdown': daily_stats
        }
        
        self.logger.info(
            f"Multi-day summary generated: {total_alerts} alerts over {total_days} days"
        )
        
        return summary
