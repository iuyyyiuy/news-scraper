"""
Feedback Collection Module

Handles collection, validation, and storage of user feedback on alerts.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import re

from trade_risk_analyzer.core.base import Alert, RiskLevel, PatternType
from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage


logger = get_logger(__name__)


class FeedbackType(Enum):
    """Type of feedback"""
    TRUE_POSITIVE = "true_positive"
    FALSE_POSITIVE = "false_positive"
    SEVERITY_ADJUSTMENT = "severity_adjustment"
    PATTERN_CORRECTION = "pattern_correction"


class FeedbackStatus(Enum):
    """Status of feedback"""
    PENDING = "pending"
    REVIEWED = "reviewed"
    INCORPORATED = "incorporated"
    REJECTED = "rejected"


@dataclass
class Feedback:
    """
    User feedback on an alert
    """
    feedback_id: str
    alert_id: str
    user_id: str  # User who provided feedback (reviewer)
    feedback_type: FeedbackType
    is_true_positive: bool
    timestamp: datetime
    reviewer_notes: Optional[str] = None
    suggested_risk_level: Optional[RiskLevel] = None
    suggested_pattern_type: Optional[PatternType] = None
    confidence_score: Optional[float] = None  # Reviewer's confidence (0-1)
    status: FeedbackStatus = FeedbackStatus.PENDING
    incorporated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'feedback_id': self.feedback_id,
            'alert_id': self.alert_id,
            'user_id': self.user_id,
            'feedback_type': self.feedback_type.value,
            'is_true_positive': self.is_true_positive,
            'timestamp': self.timestamp.isoformat(),
            'reviewer_notes': self.reviewer_notes,
            'suggested_risk_level': self.suggested_risk_level.value if self.suggested_risk_level else None,
            'suggested_pattern_type': self.suggested_pattern_type.value if self.suggested_pattern_type else None,
            'confidence_score': self.confidence_score,
            'status': self.status.value,
            'incorporated_at': self.incorporated_at.isoformat() if self.incorporated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Feedback':
        """Create from dictionary"""
        return cls(
            feedback_id=data['feedback_id'],
            alert_id=data['alert_id'],
            user_id=data['user_id'],
            feedback_type=FeedbackType(data['feedback_type']),
            is_true_positive=data['is_true_positive'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            reviewer_notes=data.get('reviewer_notes'),
            suggested_risk_level=RiskLevel(data['suggested_risk_level']) if data.get('suggested_risk_level') else None,
            suggested_pattern_type=PatternType(data['suggested_pattern_type']) if data.get('suggested_pattern_type') else None,
            confidence_score=data.get('confidence_score'),
            status=FeedbackStatus(data.get('status', 'pending')),
            incorporated_at=datetime.fromisoformat(data['incorporated_at']) if data.get('incorporated_at') else None
        )


class FeedbackCollector:
    """
    Collects and manages user feedback on alerts
    """
    
    def __init__(self, storage: Optional[DatabaseStorage] = None):
        """
        Initialize feedback collector
        
        Args:
            storage: Database storage instance
        """
        self.storage = storage
        self.logger = logger
    
    def submit_feedback(
        self,
        alert_id: str,
        reviewer_user_id: str,
        is_true_positive: bool,
        feedback_type: FeedbackType = FeedbackType.TRUE_POSITIVE,
        reviewer_notes: Optional[str] = None,
        suggested_risk_level: Optional[RiskLevel] = None,
        suggested_pattern_type: Optional[PatternType] = None,
        confidence_score: Optional[float] = None
    ) -> Feedback:
        """
        Submit feedback on an alert
        
        Args:
            alert_id: Alert ID being reviewed
            reviewer_user_id: User ID of the reviewer
            is_true_positive: Whether the alert is a true positive
            feedback_type: Type of feedback
            reviewer_notes: Optional notes from reviewer
            suggested_risk_level: Optional suggested risk level
            suggested_pattern_type: Optional suggested pattern type
            confidence_score: Reviewer's confidence (0-1)
            
        Returns:
            Feedback object
        """
        # Validate inputs
        self._validate_feedback_input(
            alert_id, reviewer_user_id, is_true_positive,
            reviewer_notes, confidence_score
        )
        
        # Generate feedback ID
        feedback_id = self._generate_feedback_id(alert_id, reviewer_user_id)
        
        # Create feedback object
        feedback = Feedback(
            feedback_id=feedback_id,
            alert_id=alert_id,
            user_id=reviewer_user_id,
            feedback_type=feedback_type,
            is_true_positive=is_true_positive,
            timestamp=datetime.now(),
            reviewer_notes=self._sanitize_notes(reviewer_notes) if reviewer_notes else None,
            suggested_risk_level=suggested_risk_level,
            suggested_pattern_type=suggested_pattern_type,
            confidence_score=confidence_score,
            status=FeedbackStatus.PENDING
        )
        
        # Store feedback
        if self.storage:
            self._store_feedback(feedback)
        
        self.logger.info(
            f"Feedback submitted: {feedback_id} for alert {alert_id} "
            f"(true_positive={is_true_positive})"
        )
        
        return feedback
    
    def get_feedback(
        self,
        alert_id: Optional[str] = None,
        reviewer_user_id: Optional[str] = None,
        feedback_type: Optional[FeedbackType] = None,
        status: Optional[FeedbackStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Feedback]:
        """
        Retrieve feedback with filters
        
        Args:
            alert_id: Filter by alert ID
            reviewer_user_id: Filter by reviewer user ID
            feedback_type: Filter by feedback type
            status: Filter by status
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of results
            
        Returns:
            List of Feedback objects
        """
        if not self.storage:
            self.logger.warning("No storage configured")
            return []
        
        # Build filters
        filters = {}
        if alert_id:
            filters['alert_id'] = alert_id
        if reviewer_user_id:
            filters['reviewer_user_id'] = reviewer_user_id
        if feedback_type:
            filters['feedback_type'] = feedback_type.value
        if status:
            filters['status'] = status.value
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        if limit:
            filters['limit'] = limit
        
        # Retrieve from storage
        feedback_list = self._retrieve_feedback(filters)
        
        self.logger.info(f"Retrieved {len(feedback_list)} feedback entries")
        
        return feedback_list
    
    def update_feedback_status(
        self,
        feedback_id: str,
        status: FeedbackStatus,
        incorporated_at: Optional[datetime] = None
    ) -> bool:
        """
        Update feedback status
        
        Args:
            feedback_id: Feedback ID to update
            status: New status
            incorporated_at: Optional timestamp when incorporated
            
        Returns:
            Success status
        """
        if not self.storage:
            self.logger.warning("No storage configured")
            return False
        
        # Update in storage
        success = self._update_feedback_status(feedback_id, status, incorporated_at)
        
        if success:
            self.logger.info(f"Feedback {feedback_id} status updated to {status.value}")
        else:
            self.logger.error(f"Failed to update feedback {feedback_id}")
        
        return success
    
    def get_feedback_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get feedback statistics
        
        Args:
            start_date: Start date for statistics
            end_date: End date for statistics
            
        Returns:
            Dictionary with statistics
        """
        feedback_list = self.get_feedback(start_date=start_date, end_date=end_date)
        
        if not feedback_list:
            return {
                'total_feedback': 0,
                'true_positives': 0,
                'false_positives': 0,
                'precision': 0.0,
                'by_type': {},
                'by_status': {},
                'average_confidence': 0.0
            }
        
        # Calculate statistics
        total = len(feedback_list)
        true_positives = sum(1 for f in feedback_list if f.is_true_positive)
        false_positives = total - true_positives
        
        precision = true_positives / total if total > 0 else 0.0
        
        # Count by type
        by_type = {}
        for feedback_type in FeedbackType:
            count = sum(1 for f in feedback_list if f.feedback_type == feedback_type)
            if count > 0:
                by_type[feedback_type.value] = count
        
        # Count by status
        by_status = {}
        for status in FeedbackStatus:
            count = sum(1 for f in feedback_list if f.status == status)
            if count > 0:
                by_status[status.value] = count
        
        # Average confidence
        confidence_scores = [f.confidence_score for f in feedback_list if f.confidence_score is not None]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        stats = {
            'total_feedback': total,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'precision': precision,
            'by_type': by_type,
            'by_status': by_status,
            'average_confidence': avg_confidence
        }
        
        self.logger.info(f"Feedback statistics: {total} total, {precision:.2%} precision")
        
        return stats
    
    def get_labeled_data_for_training(
        self,
        min_confidence: float = 0.7,
        status: FeedbackStatus = FeedbackStatus.REVIEWED
    ) -> pd.DataFrame:
        """
        Get labeled data for model training
        
        Args:
            min_confidence: Minimum confidence score to include
            status: Feedback status to include
            
        Returns:
            DataFrame with labeled data
        """
        # Get feedback
        feedback_list = self.get_feedback(status=status)
        
        if not feedback_list:
            self.logger.warning("No feedback available for training")
            return pd.DataFrame()
        
        # Filter by confidence
        if min_confidence > 0:
            feedback_list = [
                f for f in feedback_list
                if f.confidence_score is None or f.confidence_score >= min_confidence
            ]
        
        # Get corresponding alerts
        labeled_data = []
        
        for feedback in feedback_list:
            # Get alert from storage
            if self.storage:
                alerts = self.storage.get_alerts({'alert_id': feedback.alert_id})
                if alerts:
                    alert = alerts[0]
                    labeled_data.append({
                        'alert_id': alert.alert_id,
                        'user_id': alert.user_id,
                        'timestamp': alert.timestamp,
                        'anomaly_score': alert.anomaly_score,
                        'risk_level': alert.risk_level.value,
                        'pattern_type': alert.pattern_type.value,
                        'is_true_positive': feedback.is_true_positive,
                        'feedback_confidence': feedback.confidence_score,
                        'trade_ids': ','.join(alert.trade_ids) if alert.trade_ids else ''
                    })
        
        df = pd.DataFrame(labeled_data)
        
        self.logger.info(f"Retrieved {len(df)} labeled examples for training")
        
        return df
    
    def _validate_feedback_input(
        self,
        alert_id: str,
        reviewer_user_id: str,
        is_true_positive: bool,
        reviewer_notes: Optional[str],
        confidence_score: Optional[float]
    ) -> None:
        """Validate feedback input"""
        if not alert_id or not isinstance(alert_id, str):
            raise ValueError("Invalid alert_id")
        
        if not reviewer_user_id or not isinstance(reviewer_user_id, str):
            raise ValueError("Invalid reviewer_user_id")
        
        if not isinstance(is_true_positive, bool):
            raise ValueError("is_true_positive must be a boolean")
        
        if reviewer_notes and len(reviewer_notes) > 5000:
            raise ValueError("Reviewer notes too long (max 5000 characters)")
        
        if confidence_score is not None:
            if not isinstance(confidence_score, (int, float)):
                raise ValueError("confidence_score must be a number")
            if not 0 <= confidence_score <= 1:
                raise ValueError("confidence_score must be between 0 and 1")
    
    def _sanitize_notes(self, notes: str) -> str:
        """Sanitize reviewer notes"""
        # Remove any potentially harmful content
        # Remove HTML tags
        notes = re.sub(r'<[^>]+>', '', notes)
        
        # Remove excessive whitespace
        notes = ' '.join(notes.split())
        
        # Limit length
        if len(notes) > 5000:
            notes = notes[:5000]
        
        return notes.strip()
    
    def _generate_feedback_id(self, alert_id: str, reviewer_user_id: str) -> str:
        """Generate unique feedback ID"""
        timestamp = int(datetime.now().timestamp() * 1000)
        return f"feedback_{alert_id}_{reviewer_user_id}_{timestamp}"
    
    def _store_feedback(self, feedback: Feedback) -> bool:
        """Store feedback in database"""
        if not self.storage:
            return False
        
        try:
            # Store in database (implementation depends on storage backend)
            # For now, we'll use a simple approach
            self.storage.save_feedback(feedback)
            return True
        except Exception as e:
            self.logger.error(f"Failed to store feedback: {e}", exc_info=True)
            return False
    
    def _retrieve_feedback(self, filters: Dict[str, Any]) -> List[Feedback]:
        """Retrieve feedback from database"""
        if not self.storage:
            return []
        
        try:
            # Retrieve from database
            feedback_list = self.storage.get_feedback(filters)
            return feedback_list
        except Exception as e:
            self.logger.error(f"Failed to retrieve feedback: {e}", exc_info=True)
            return []
    
    def _update_feedback_status(
        self,
        feedback_id: str,
        status: FeedbackStatus,
        incorporated_at: Optional[datetime]
    ) -> bool:
        """Update feedback status in database"""
        if not self.storage:
            return False
        
        try:
            # Update in database
            self.storage.update_feedback_status(feedback_id, status.value, incorporated_at)
            return True
        except Exception as e:
            self.logger.error(f"Failed to update feedback status: {e}", exc_info=True)
            return False
