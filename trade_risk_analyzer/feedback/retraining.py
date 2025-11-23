"""
Model Retraining Pipeline

Handles model retraining with feedback data, versioning, and performance tracking.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
import json
import joblib

from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.feedback.collector import FeedbackCollector, FeedbackStatus
from trade_risk_analyzer.feature_engineering.extractor import FeatureExtractor
from trade_risk_analyzer.models.random_forest import RandomForestModel
from trade_risk_analyzer.models.isolation_forest import IsolationForestModel
from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage


logger = get_logger(__name__)


@dataclass
class PerformanceMetrics:
    """Model performance metrics"""
    version: str
    timestamp: datetime
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: Optional[float] = None
    training_samples: int = 0
    feedback_samples: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'version': self.version,
            'timestamp': self.timestamp.isoformat(),
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'f1_score': self.f1_score,
            'auc_roc': self.auc_roc,
            'training_samples': self.training_samples,
            'feedback_samples': self.feedback_samples
        }


@dataclass
class ModelVersion:
    """Model version information"""
    version: str
    created_at: datetime
    model_type: str
    model_path: str
    performance_metrics: PerformanceMetrics
    is_active: bool = False
    parent_version: Optional[str] = None
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'model_type': self.model_type,
            'model_path': self.model_path,
            'performance_metrics': self.performance_metrics.to_dict(),
            'is_active': self.is_active,
            'parent_version': self.parent_version,
            'notes': self.notes
        }


class RetrainingPipeline:
    """
    Pipeline for retraining models with feedback data
    """
    
    def __init__(
        self,
        storage: Optional[DatabaseStorage] = None,
        feedback_collector: Optional[FeedbackCollector] = None,
        model_dir: str = "models",
        version_dir: str = "model_versions"
    ):
        """
        Initialize retraining pipeline
        
        Args:
            storage: Database storage instance
            feedback_collector: Feedback collector instance
            model_dir: Directory for active models
            version_dir: Directory for model versions
        """
        self.storage = storage
        self.feedback_collector = feedback_collector or FeedbackCollector(storage)
        self.model_dir = Path(model_dir)
        self.version_dir = Path(version_dir)
        self.logger = logger
        
        # Create directories
        self.model_dir.mkdir(exist_ok=True)
        self.version_dir.mkdir(exist_ok=True)
        
        # Feature extractor
        self.feature_extractor = FeatureExtractor()
    
    def retrain_random_forest(
        self,
        min_feedback_samples: int = 50,
        min_confidence: float = 0.7,
        test_size: float = 0.2,
        incremental: bool = True
    ) -> Optional[ModelVersion]:
        """
        Retrain Random Forest model with feedback data
        
        Args:
            min_feedback_samples: Minimum feedback samples required
            min_confidence: Minimum confidence score for feedback
            test_size: Test set size for evaluation
            incremental: Whether to use incremental learning
            
        Returns:
            ModelVersion if successful, None otherwise
        """
        self.logger.info("Starting Random Forest retraining...")
        
        # Get labeled data from feedback
        labeled_df = self.feedback_collector.get_labeled_data_for_training(
            min_confidence=min_confidence,
            status=FeedbackStatus.REVIEWED
        )
        
        if len(labeled_df) < min_feedback_samples:
            self.logger.warning(
                f"Insufficient feedback samples: {len(labeled_df)} < {min_feedback_samples}"
            )
            return None
        
        self.logger.info(f"Retrieved {len(labeled_df)} labeled samples for training")
        
        # Get trades for feature extraction
        if not self.storage:
            self.logger.error("Storage not configured")
            return None
        
        # Extract features for labeled data
        features_df = self._extract_features_for_labeled_data(labeled_df)
        
        if features_df.empty:
            self.logger.error("Failed to extract features")
            return None
        
        # Prepare training data
        X, y = self._prepare_training_data(features_df, labeled_df)
        
        if X is None or y is None:
            self.logger.error("Failed to prepare training data")
            return None
        
        # Split into train/test
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        self.logger.info(
            f"Training set: {len(X_train)} samples, Test set: {len(X_test)} samples"
        )
        
        # Load existing model if incremental
        model = RandomForestModel()
        
        if incremental:
            existing_model_path = self.model_dir / "random_forest.joblib"
            if existing_model_path.exists():
                try:
                    model.load(str(existing_model_path))
                    self.logger.info("Loaded existing model for incremental learning")
                except Exception as e:
                    self.logger.warning(f"Failed to load existing model: {e}")
        
        # Train model
        self.logger.info("Training Random Forest model...")
        model.train(X_train, y_train)
        
        # Evaluate model
        metrics = self._evaluate_model(model, X_test, y_test, len(labeled_df))
        
        self.logger.info(
            f"Model performance: Accuracy={metrics.accuracy:.3f}, "
            f"Precision={metrics.precision:.3f}, Recall={metrics.recall:.3f}, "
            f"F1={metrics.f1_score:.3f}"
        )
        
        # Create model version
        version = self._create_model_version(
            model_type="random_forest",
            model=model,
            metrics=metrics,
            incremental=incremental
        )
        
        # Save model version
        self._save_model_version(version, model)
        
        # Update feedback status
        self._mark_feedback_as_incorporated(labeled_df)
        
        self.logger.info(f"Random Forest retraining complete: version {version.version}")
        
        return version
    
    def retrain_isolation_forest(
        self,
        min_feedback_samples: int = 100,
        contamination: float = 0.1
    ) -> Optional[ModelVersion]:
        """
        Retrain Isolation Forest model with feedback data
        
        Args:
            min_feedback_samples: Minimum feedback samples required
            contamination: Expected proportion of anomalies
            
        Returns:
            ModelVersion if successful, None otherwise
        """
        self.logger.info("Starting Isolation Forest retraining...")
        
        # Get labeled data from feedback
        labeled_df = self.feedback_collector.get_labeled_data_for_training(
            min_confidence=0.7,
            status=FeedbackStatus.REVIEWED
        )
        
        if len(labeled_df) < min_feedback_samples:
            self.logger.warning(
                f"Insufficient feedback samples: {len(labeled_df)} < {min_feedback_samples}"
            )
            return None
        
        # Extract features
        features_df = self._extract_features_for_labeled_data(labeled_df)
        
        if features_df.empty:
            self.logger.error("Failed to extract features")
            return None
        
        # Prepare training data
        X, y = self._prepare_training_data(features_df, labeled_df)
        
        if X is None:
            self.logger.error("Failed to prepare training data")
            return None
        
        # Train model
        model = IsolationForestModel(contamination=contamination)
        self.logger.info("Training Isolation Forest model...")
        model.train(X)
        
        # Evaluate model (if we have labels)
        if y is not None:
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            metrics = self._evaluate_model(model, X_test, y_test, len(labeled_df))
        else:
            # Create dummy metrics for unsupervised model
            metrics = PerformanceMetrics(
                version="",
                timestamp=datetime.now(),
                accuracy=0.0,
                precision=0.0,
                recall=0.0,
                f1_score=0.0,
                training_samples=len(X)
            )
        
        # Create model version
        version = self._create_model_version(
            model_type="isolation_forest",
            model=model,
            metrics=metrics,
            incremental=False
        )
        
        # Save model version
        self._save_model_version(version, model)
        
        self.logger.info(f"Isolation Forest retraining complete: version {version.version}")
        
        return version
    
    def activate_model_version(self, version: str) -> bool:
        """
        Activate a specific model version
        
        Args:
            version: Version to activate
            
        Returns:
            Success status
        """
        version_path = self.version_dir / version / "metadata.json"
        
        if not version_path.exists():
            self.logger.error(f"Version {version} not found")
            return False
        
        # Load version metadata
        with open(version_path, 'r') as f:
            metadata = json.load(f)
        
        model_type = metadata['model_type']
        model_file = f"{model_type}.joblib"
        
        # Copy model to active directory
        source = self.version_dir / version / model_file
        dest = self.model_dir / model_file
        
        if not source.exists():
            self.logger.error(f"Model file not found: {source}")
            return False
        
        # Copy model
        import shutil
        shutil.copy2(source, dest)
        
        # Update metadata
        metadata['is_active'] = True
        with open(version_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"Activated model version {version}")
        
        return True
    
    def rollback_to_version(self, version: str) -> bool:
        """
        Rollback to a previous model version
        
        Args:
            version: Version to rollback to
            
        Returns:
            Success status
        """
        self.logger.info(f"Rolling back to version {version}")
        return self.activate_model_version(version)
    
    def get_model_versions(
        self,
        model_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[ModelVersion]:
        """
        Get list of model versions
        
        Args:
            model_type: Filter by model type
            limit: Maximum number of versions
            
        Returns:
            List of ModelVersion objects
        """
        versions = []
        
        for version_dir in sorted(self.version_dir.iterdir(), reverse=True):
            if not version_dir.is_dir():
                continue
            
            metadata_path = version_dir / "metadata.json"
            if not metadata_path.exists():
                continue
            
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                # Filter by model type
                if model_type and metadata['model_type'] != model_type:
                    continue
                
                # Create ModelVersion object
                metrics = PerformanceMetrics(
                    version=metadata['version'],
                    timestamp=datetime.fromisoformat(metadata['performance_metrics']['timestamp']),
                    accuracy=metadata['performance_metrics']['accuracy'],
                    precision=metadata['performance_metrics']['precision'],
                    recall=metadata['performance_metrics']['recall'],
                    f1_score=metadata['performance_metrics']['f1_score'],
                    auc_roc=metadata['performance_metrics'].get('auc_roc'),
                    training_samples=metadata['performance_metrics'].get('training_samples', 0),
                    feedback_samples=metadata['performance_metrics'].get('feedback_samples', 0)
                )
                
                version = ModelVersion(
                    version=metadata['version'],
                    created_at=datetime.fromisoformat(metadata['created_at']),
                    model_type=metadata['model_type'],
                    model_path=metadata['model_path'],
                    performance_metrics=metrics,
                    is_active=metadata.get('is_active', False),
                    parent_version=metadata.get('parent_version'),
                    notes=metadata.get('notes')
                )
                
                versions.append(version)
                
                if limit and len(versions) >= limit:
                    break
                    
            except Exception as e:
                self.logger.error(f"Failed to load version {version_dir.name}: {e}")
        
        return versions
    
    def get_performance_history(
        self,
        model_type: str,
        limit: Optional[int] = None
    ) -> List[PerformanceMetrics]:
        """
        Get performance metrics history for a model type
        
        Args:
            model_type: Model type
            limit: Maximum number of entries
            
        Returns:
            List of PerformanceMetrics
        """
        versions = self.get_model_versions(model_type=model_type, limit=limit)
        return [v.performance_metrics for v in versions]
    
    def _extract_features_for_labeled_data(
        self,
        labeled_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Extract features for labeled data"""
        if not self.storage:
            return pd.DataFrame()
        
        # Get trades for each alert
        all_trades = []
        
        for _, row in labeled_df.iterrows():
            # Get trades from trade_ids
            trade_ids = row['trade_ids'].split(',') if row['trade_ids'] else []
            
            if trade_ids:
                trades_df = self.storage.get_trades_as_dataframe({
                    'trade_ids': trade_ids
                })
                all_trades.append(trades_df)
        
        if not all_trades:
            return pd.DataFrame()
        
        # Combine all trades
        trades_df = pd.concat(all_trades, ignore_index=True)
        
        # Extract features
        features_df = self.feature_extractor.extract_features(
            trades_df,
            group_by='user_id'
        )
        
        # Normalize features
        features_df = self.feature_extractor.normalize_features(
            features_df,
            exclude_columns=['user_id'],
            fit=True
        )
        
        return features_df
    
    def _prepare_training_data(
        self,
        features_df: pd.DataFrame,
        labeled_df: pd.DataFrame
    ) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Prepare training data from features and labels"""
        # Merge features with labels
        merged_df = features_df.merge(
            labeled_df[['user_id', 'is_true_positive']],
            on='user_id',
            how='inner'
        )
        
        if merged_df.empty:
            return None, None
        
        # Build feature vector
        X = self.feature_extractor.build_feature_vector(
            merged_df,
            exclude_columns=['user_id', 'is_true_positive']
        )
        
        # Get labels (1 for anomaly/true positive, 0 for normal/false positive)
        y = merged_df['is_true_positive'].values.astype(int)
        
        return X, y
    
    def _evaluate_model(
        self,
        model: Any,
        X_test: np.ndarray,
        y_test: np.ndarray,
        total_samples: int
    ) -> PerformanceMetrics:
        """Evaluate model performance"""
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score,
            f1_score, roc_auc_score
        )
        
        # Get predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        # Try to calculate AUC-ROC
        auc_roc = None
        try:
            if hasattr(model, 'predict_proba'):
                y_proba = model.predict_proba(X_test)[:, 1]
                auc_roc = roc_auc_score(y_test, y_proba)
        except Exception:
            pass
        
        metrics = PerformanceMetrics(
            version="",  # Will be set later
            timestamp=datetime.now(),
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            auc_roc=auc_roc,
            training_samples=len(X_test),
            feedback_samples=total_samples
        )
        
        return metrics
    
    def _create_model_version(
        self,
        model_type: str,
        model: Any,
        metrics: PerformanceMetrics,
        incremental: bool
    ) -> ModelVersion:
        """Create model version"""
        # Generate version string
        timestamp = datetime.now()
        version_str = f"{model_type}_v{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        # Get parent version if incremental
        parent_version = None
        if incremental:
            existing_versions = self.get_model_versions(model_type=model_type, limit=1)
            if existing_versions:
                parent_version = existing_versions[0].version
        
        # Update metrics version
        metrics.version = version_str
        
        # Create version directory
        version_path = self.version_dir / version_str
        version_path.mkdir(exist_ok=True)
        
        # Model path
        model_path = str(version_path / f"{model_type}.joblib")
        
        # Create ModelVersion
        version = ModelVersion(
            version=version_str,
            created_at=timestamp,
            model_type=model_type,
            model_path=model_path,
            performance_metrics=metrics,
            is_active=False,
            parent_version=parent_version,
            notes=f"Retrained with {metrics.feedback_samples} feedback samples"
        )
        
        return version
    
    def _save_model_version(self, version: ModelVersion, model: Any) -> None:
        """Save model version"""
        # Save model
        model.save(version.model_path)
        
        # Save metadata
        metadata_path = Path(version.model_path).parent / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(version.to_dict(), f, indent=2)
        
        self.logger.info(f"Saved model version: {version.version}")
    
    def _mark_feedback_as_incorporated(self, labeled_df: pd.DataFrame) -> None:
        """Mark feedback as incorporated"""
        for _, row in labeled_df.iterrows():
            alert_id = row['alert_id']
            
            # Get feedback for this alert
            feedback_list = self.feedback_collector.get_feedback(alert_id=alert_id)
            
            for feedback in feedback_list:
                if feedback.status == FeedbackStatus.REVIEWED:
                    self.feedback_collector.update_feedback_status(
                        feedback.feedback_id,
                        FeedbackStatus.INCORPORATED,
                        incorporated_at=datetime.now()
                    )
