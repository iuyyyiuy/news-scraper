"""
Detection Engine

Core detection engine that orchestrates feature extraction, ML models,
and rule-based detection to identify suspicious trading patterns.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import time

from trade_risk_analyzer.core.base import Alert, RiskLevel, PatternType, DetectionResult
from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.core.config import get_config
from trade_risk_analyzer.feature_engineering.extractor import FeatureExtractor
from trade_risk_analyzer.models.ensemble import ModelEnsemble
from trade_risk_analyzer.detection.rule_based_detector import (
    RuleBasedDetector,
    RuleBasedThresholds
)
from trade_risk_analyzer.detection.alert_manager import AlertManager


logger = get_logger(__name__)


@dataclass
class DetectionConfig:
    """
    Configuration for detection engine
    """
    # Feature extraction settings
    use_feature_extraction: bool = True
    feature_time_windows: List[str] = field(default_factory=lambda: ['1H', '24H', '7D'])
    feature_scaler_type: str = 'standard'
    
    # ML model settings
    use_ml_models: bool = True
    ml_model_weights: Dict[str, float] = field(default_factory=lambda: {
        'isolation_forest': 0.3,
        'autoencoder': 0.4,
        'random_forest': 0.3
    })
    ml_high_risk_threshold: float = 0.8
    ml_medium_risk_threshold: float = 0.5
    
    # Rule-based detection settings
    use_rule_based: bool = True
    rule_based_thresholds: Optional[RuleBasedThresholds] = None
    
    # Score combination settings
    ml_weight: float = 0.5
    rule_weight: float = 0.5
    
    # Risk thresholds
    high_risk_score: float = 80.0
    medium_risk_score: float = 50.0


class DetectionEngine:
    """
    Main detection engine that orchestrates all detection components
    """
    
    def __init__(self, config: Optional[DetectionConfig] = None,
                 storage: Optional[Any] = None):
        """
        Initialize detection engine
        
        Args:
            config: Detection configuration
            storage: Database storage instance for alert management
        """
        self.config = config or DetectionConfig()
        self.logger = logger
        
        # Initialize components
        self.feature_extractor: Optional[FeatureExtractor] = None
        self.ml_ensemble: Optional[ModelEnsemble] = None
        self.rule_detector: Optional[RuleBasedDetector] = None
        self.alert_manager: Optional[AlertManager] = None
        
        # Storage for alert management
        self.storage = storage
        
        self._initialize_components()
    
    def _initialize_components(self) -> None:
        """Initialize detection components based on configuration"""
        self.logger.info("Initializing detection engine components...")
        
        # Initialize feature extractor
        if self.config.use_feature_extraction:
            self.feature_extractor = FeatureExtractor(
                time_windows=self.config.feature_time_windows,
                scaler_type=self.config.feature_scaler_type
            )
            self.logger.info("Feature extractor initialized")
        
        # Initialize ML ensemble
        if self.config.use_ml_models:
            self.ml_ensemble = ModelEnsemble(
                weights=self.config.ml_model_weights,
                high_risk_threshold=self.config.ml_high_risk_threshold,
                medium_risk_threshold=self.config.ml_medium_risk_threshold
            )
            self.logger.info("ML ensemble initialized")
        
        # Initialize rule-based detector
        if self.config.use_rule_based:
            thresholds = self.config.rule_based_thresholds or RuleBasedThresholds()
            self.rule_detector = RuleBasedDetector(thresholds=thresholds)
            self.logger.info("Rule-based detector initialized")
        
        # Initialize alert manager
        self.alert_manager = AlertManager(storage=self.storage)
        self.logger.info("Alert manager initialized")
        
        self.logger.info("Detection engine initialization complete")
    
    def detect(self, trades: pd.DataFrame,
               group_by: str = 'user_id',
               market_data: Optional[pd.DataFrame] = None) -> DetectionResult:
        """
        Run complete detection workflow
        
        Args:
            trades: DataFrame with trade data
            group_by: Column to group by for analysis
            market_data: Optional market data for price calculations
            
        Returns:
            DetectionResult with alerts and scores
        """
        start_time = time.time()
        self.logger.info(f"Starting detection on {len(trades)} trades")
        
        if trades.empty:
            self.logger.warning("No trades provided for detection")
            return DetectionResult(
                anomaly_scores=[],
                risk_flags=[],
                alerts=[]
            )
        
        # Step 1: Extract features (if ML models are enabled)
        features_df = None
        feature_array = None
        
        if self.config.use_feature_extraction and self.feature_extractor:
            self.logger.info("Step 1: Extracting features...")
            try:
                features_df = self.feature_extractor.extract_features(
                    trades,
                    group_by=group_by,
                    market_data=market_data
                )
                
                if not features_df.empty:
                    # Normalize features
                    features_df = self.feature_extractor.normalize_features(
                        features_df,
                        exclude_columns=[group_by],
                        fit=True
                    )
                    
                    # Build feature vectors
                    feature_array = self.feature_extractor.build_feature_vector(
                        features_df,
                        exclude_columns=[group_by]
                    )
                    
                    self.logger.info(f"Extracted features: {feature_array.shape}")
            except Exception as e:
                self.logger.error(f"Feature extraction failed: {str(e)}", exc_info=True)
        
        # Step 2: Run ML models (if enabled and features available)
        ml_scores = None
        ml_predictions = None
        ml_risk_levels = None
        
        if (self.config.use_ml_models and self.ml_ensemble and 
            feature_array is not None and len(feature_array) > 0):
            self.logger.info("Step 2: Running ML models...")
            try:
                ml_predictions, ml_scores, ml_risk_levels = \
                    self.ml_ensemble.predict_with_risk_level(feature_array)
                
                anomaly_count = np.sum(ml_predictions)
                self.logger.info(
                    f"ML models detected {anomaly_count} anomalies "
                    f"({anomaly_count/len(ml_predictions):.2%})"
                )
            except Exception as e:
                self.logger.error(f"ML prediction failed: {str(e)}", exc_info=True)
        
        # Step 3: Run rule-based detection (if enabled)
        rule_alerts = []
        
        if self.config.use_rule_based and self.rule_detector:
            self.logger.info("Step 3: Running rule-based detection...")
            try:
                rule_alerts = self.rule_detector.detect_all_patterns(trades)
                self.logger.info(f"Rule-based detection generated {len(rule_alerts)} alerts")
            except Exception as e:
                self.logger.error(f"Rule-based detection failed: {str(e)}", exc_info=True)
        
        # Step 4: Combine results and calculate final scores
        self.logger.info("Step 4: Combining results...")
        combined_alerts, anomaly_scores, risk_flags = self._combine_results(
            trades=trades,
            group_by=group_by,
            features_df=features_df,
            ml_scores=ml_scores,
            ml_risk_levels=ml_risk_levels,
            rule_alerts=rule_alerts
        )
        
        detection_time = time.time() - start_time
        self.logger.info(
            f"Detection complete: {len(combined_alerts)} total alerts "
            f"in {detection_time:.2f} seconds"
        )
        
        return DetectionResult(
            anomaly_scores=anomaly_scores,
            risk_flags=risk_flags,
            alerts=combined_alerts
        )
    
    def _combine_results(
        self,
        trades: pd.DataFrame,
        group_by: str,
        features_df: Optional[pd.DataFrame],
        ml_scores: Optional[np.ndarray],
        ml_risk_levels: Optional[List[RiskLevel]],
        rule_alerts: List[Alert]
    ) -> Tuple[List[Alert], List[float], List[RiskLevel]]:
        """
        Combine ML and rule-based results into unified alerts
        
        Args:
            trades: Original trade data
            group_by: Grouping column
            features_df: Extracted features
            ml_scores: ML anomaly scores
            ml_risk_levels: ML risk levels
            rule_alerts: Rule-based alerts
            
        Returns:
            Tuple of (combined_alerts, anomaly_scores, risk_flags)
        """
        combined_alerts = []
        
        # Start with rule-based alerts
        combined_alerts.extend(rule_alerts)
        
        # Create ML-based alerts if available
        if ml_scores is not None and features_df is not None:
            ml_alerts = self._create_ml_alerts(
                features_df,
                ml_scores,
                ml_risk_levels,
                trades,
                group_by
            )
            combined_alerts.extend(ml_alerts)
        
        # Calculate combined anomaly scores for each entity
        entity_scores = self._calculate_entity_scores(
            trades,
            group_by,
            ml_scores,
            features_df,
            rule_alerts
        )
        
        # Assign risk flags based on combined scores
        anomaly_scores = []
        risk_flags = []
        
        for entity_id in trades[group_by].unique():
            score = entity_scores.get(entity_id, 0.0)
            anomaly_scores.append(score)
            risk_flags.append(self._score_to_risk_level(score))
        
        return combined_alerts, anomaly_scores, risk_flags
    
    def _create_ml_alerts(
        self,
        features_df: pd.DataFrame,
        ml_scores: np.ndarray,
        ml_risk_levels: Optional[List[RiskLevel]],
        trades: pd.DataFrame,
        group_by: str
    ) -> List[Alert]:
        """
        Create alerts from ML model predictions
        
        Args:
            features_df: Features DataFrame with entity IDs
            ml_scores: ML anomaly scores
            ml_risk_levels: ML risk levels
            trades: Original trade data
            group_by: Grouping column
            
        Returns:
            List of ML-based alerts
        """
        ml_alerts = []
        
        # Get entity IDs from features
        entity_ids = features_df[group_by].values
        
        for idx, (entity_id, score) in enumerate(zip(entity_ids, ml_scores)):
            # Only create alerts for high-risk predictions
            risk_level = ml_risk_levels[idx] if ml_risk_levels else self._score_to_risk_level(score * 100)
            
            if risk_level in [RiskLevel.HIGH, RiskLevel.MEDIUM]:
                # Get trades for this entity
                entity_trades = trades[trades[group_by] == entity_id]
                trade_ids = entity_trades['trade_id'].tolist()
                
                # Get model contributions for explanation
                explanation = self._generate_ml_explanation(score, features_df.iloc[idx])
                
                alert = Alert(
                    alert_id=f"ml_anomaly_{entity_id}_{pd.Timestamp.now().timestamp()}",
                    timestamp=pd.Timestamp.now(),
                    user_id=str(entity_id),
                    trade_ids=trade_ids,
                    anomaly_score=score * 100,  # Convert to 0-100 scale
                    risk_level=risk_level,
                    pattern_type=PatternType.GENERAL_ANOMALY,
                    explanation=explanation,
                    recommended_action="Review trading patterns for potential anomalous behavior"
                )
                ml_alerts.append(alert)
        
        return ml_alerts
    
    def _generate_ml_explanation(self, score: float, features: pd.Series) -> str:
        """
        Generate explanation for ML-based alert
        
        Args:
            score: Anomaly score
            features: Feature values for the entity
            
        Returns:
            Explanation string
        """
        explanation_parts = [
            f"ML models detected anomalous behavior (score: {score*100:.1f}/100)"
        ]
        
        # Identify top anomalous features
        numeric_features = features.select_dtypes(include=[np.number])
        
        if len(numeric_features) > 0:
            # Get features with highest absolute values (normalized)
            top_features = numeric_features.abs().nlargest(3)
            
            if len(top_features) > 0:
                feature_names = top_features.index.tolist()
                explanation_parts.append(
                    f"Key indicators: {', '.join(feature_names[:3])}"
                )
        
        return ". ".join(explanation_parts)
    
    def _calculate_entity_scores(
        self,
        trades: pd.DataFrame,
        group_by: str,
        ml_scores: Optional[np.ndarray],
        features_df: Optional[pd.DataFrame],
        rule_alerts: List[Alert]
    ) -> Dict[str, float]:
        """
        Calculate combined anomaly scores for each entity
        
        Args:
            trades: Trade data
            group_by: Grouping column
            ml_scores: ML anomaly scores
            features_df: Features DataFrame
            rule_alerts: Rule-based alerts
            
        Returns:
            Dictionary mapping entity ID to combined score
        """
        entity_scores = {}
        
        # Get ML scores by entity
        ml_scores_dict = {}
        if ml_scores is not None and features_df is not None:
            entity_ids = features_df[group_by].values
            for entity_id, score in zip(entity_ids, ml_scores):
                ml_scores_dict[str(entity_id)] = score * 100  # Convert to 0-100
        
        # Get rule-based scores by entity
        rule_scores_dict = {}
        for alert in rule_alerts:
            # Handle multiple users in alert
            user_ids = alert.user_id.split(',')
            for user_id in user_ids:
                user_id = user_id.strip()
                if user_id not in rule_scores_dict:
                    rule_scores_dict[user_id] = []
                rule_scores_dict[user_id].append(alert.anomaly_score)
        
        # Average rule scores for each entity
        for user_id, scores in rule_scores_dict.items():
            rule_scores_dict[user_id] = np.mean(scores)
        
        # Combine scores
        all_entities = set(ml_scores_dict.keys()) | set(rule_scores_dict.keys())
        
        for entity_id in all_entities:
            ml_score = ml_scores_dict.get(entity_id, 0.0)
            rule_score = rule_scores_dict.get(entity_id, 0.0)
            
            # Weighted combination
            combined_score = (
                self.config.ml_weight * ml_score +
                self.config.rule_weight * rule_score
            )
            
            entity_scores[entity_id] = combined_score
        
        return entity_scores
    
    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """
        Convert anomaly score to risk level
        
        Args:
            score: Anomaly score (0-100)
            
        Returns:
            RiskLevel
        """
        if score >= self.config.high_risk_score:
            return RiskLevel.HIGH
        elif score >= self.config.medium_risk_score:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def load_models(self, model_dir: str) -> None:
        """
        Load trained ML models
        
        Args:
            model_dir: Directory containing model files
        """
        if not self.ml_ensemble:
            self.logger.warning("ML ensemble not initialized")
            return
        
        model_path = Path(model_dir)
        
        # Load Isolation Forest
        if (model_path / 'isolation_forest.joblib').exists():
            from trade_risk_analyzer.models.isolation_forest import IsolationForestModel
            iso_model = IsolationForestModel()
            iso_model.load(str(model_path / 'isolation_forest.joblib'))
            self.ml_ensemble.add_model('isolation_forest', iso_model)
            self.logger.info("Loaded Isolation Forest model")
        
        # Load Autoencoder
        if (model_path / 'autoencoder.h5').exists():
            from trade_risk_analyzer.models.autoencoder import AutoencoderModel
            ae_model = AutoencoderModel()
            ae_model.load(str(model_path / 'autoencoder.h5'))
            self.ml_ensemble.add_model('autoencoder', ae_model)
            self.logger.info("Loaded Autoencoder model")
        
        # Load Random Forest
        if (model_path / 'random_forest.joblib').exists():
            from trade_risk_analyzer.models.random_forest import RandomForestModel
            rf_model = RandomForestModel()
            rf_model.load(str(model_path / 'random_forest.joblib'))
            self.ml_ensemble.add_model('random_forest', rf_model)
            self.logger.info("Loaded Random Forest model")
    
    def update_config(self, new_config: DetectionConfig) -> None:
        """
        Update detection configuration and reinitialize components
        
        Args:
            new_config: New detection configuration
        """
        self.logger.info("Updating detection engine configuration")
        self.config = new_config
        self._initialize_components()
        self.logger.info("Configuration updated successfully")
    
    def get_config(self) -> DetectionConfig:
        """
        Get current detection configuration
        
        Returns:
            Current DetectionConfig
        """
        return self.config
    
    def get_detection_stats(self, result: DetectionResult) -> Dict[str, Any]:
        """
        Get statistics from detection result
        
        Args:
            result: Detection result
            
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_alerts': len(result.alerts),
            'alerts_by_pattern': {},
            'alerts_by_risk_level': {},
            'anomaly_score_stats': {}
        }
        
        # Count by pattern type
        for alert in result.alerts:
            pattern = alert.pattern_type.value
            stats['alerts_by_pattern'][pattern] = \
                stats['alerts_by_pattern'].get(pattern, 0) + 1
        
        # Count by risk level
        for alert in result.alerts:
            risk = alert.risk_level.value
            stats['alerts_by_risk_level'][risk] = \
                stats['alerts_by_risk_level'].get(risk, 0) + 1
        
        # Score statistics
        if result.anomaly_scores:
            scores = np.array(result.anomaly_scores)
            stats['anomaly_score_stats'] = {
                'mean': float(np.mean(scores)),
                'median': float(np.median(scores)),
                'std': float(np.std(scores)),
                'min': float(np.min(scores)),
                'max': float(np.max(scores))
            }
        
        return stats
    
    def save_alerts(self, alerts: List[Alert], 
                   check_duplicates: bool = True) -> Dict[str, int]:
        """
        Save alerts to database with deduplication
        
        Args:
            alerts: List of alerts to save
            check_duplicates: Whether to check for duplicates
            
        Returns:
            Dictionary with save results
        """
        if not self.alert_manager:
            self.logger.warning("Alert manager not initialized")
            return {'saved': 0, 'duplicates': 0, 'errors': len(alerts)}
        
        return self.alert_manager.save_alerts_batch(
            alerts, 
            check_duplicates=check_duplicates
        )
    
    def get_alerts(self, **kwargs) -> List[Alert]:
        """
        Retrieve alerts from database
        
        Args:
            **kwargs: Filter parameters (user_id, risk_level, pattern_type, etc.)
            
        Returns:
            List of alerts
        """
        if not self.alert_manager:
            self.logger.warning("Alert manager not initialized")
            return []
        
        return self.alert_manager.get_alerts(**kwargs)
