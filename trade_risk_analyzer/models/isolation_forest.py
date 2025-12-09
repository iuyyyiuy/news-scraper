"""
Isolation Forest Model Implementation

Unsupervised anomaly detection using Isolation Forest algorithm.
"""

import numpy as np
import joblib
from sklearn.ensemble import IsolationForest as SklearnIsolationForest
from sklearn.model_selection import GridSearchCV, cross_val_score
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime

from trade_risk_analyzer.core.base import BaseModel
from trade_risk_analyzer.core.logger import get_logger


logger = get_logger(__name__)


class IsolationForestModel(BaseModel):
    """
    Isolation Forest model for anomaly detection
    """
    
    def __init__(self, 
                 n_estimators: int = 100,
                 max_samples: str = 'auto',
                 contamination: float = 0.1,
                 max_features: float = 1.0,
                 random_state: int = 42):
        """
        Initialize Isolation Forest model
        
        Args:
            n_estimators: Number of trees in the forest
            max_samples: Number of samples to draw for each tree
            contamination: Expected proportion of outliers
            max_features: Number of features to draw for each tree
            random_state: Random seed for reproducibility
        """
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.contamination = contamination
        self.max_features = max_features
        self.random_state = random_state
        
        self.model = None
        self.is_trained = False
        self.feature_names = None
        self.training_metadata = {}
        
        self.logger = logger
    
    def train(self, X_train: np.ndarray, y_train: Optional[np.ndarray] = None) -> None:
        """
        Train the Isolation Forest model
        
        Args:
            X_train: Training features (n_samples, n_features)
            y_train: Not used (unsupervised learning)
        """
        self.logger.info(f"Training Isolation Forest with {X_train.shape[0]} samples, {X_train.shape[1]} features")
        
        # Initialize model
        self.model = SklearnIsolationForest(
            n_estimators=self.n_estimators,
            max_samples=self.max_samples,
            contamination=self.contamination,
            max_features=self.max_features,
            random_state=self.random_state,
            n_jobs=-1,  # Use all CPU cores
            verbose=0
        )
        
        # Train model
        self.model.fit(X_train)
        
        self.is_trained = True
        
        # Store training metadata
        self.training_metadata = {
            'n_samples': X_train.shape[0],
            'n_features': X_train.shape[1],
            'n_estimators': self.n_estimators,
            'contamination': self.contamination,
            'trained_at': datetime.now().isoformat()
        }
        
        self.logger.info("Isolation Forest training complete")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict anomaly labels (-1 for anomaly, 1 for normal)
        
        Args:
            X: Input features (n_samples, n_features)
            
        Returns:
            Predictions (-1 for anomaly, 1 for normal)
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before prediction")
        
        predictions = self.model.predict(X)
        
        self.logger.info(f"Predicted {np.sum(predictions == -1)} anomalies out of {len(predictions)} samples")
        
        return predictions
    
    def predict_anomaly_score(self, X: np.ndarray) -> np.ndarray:
        """
        Calculate anomaly scores (lower = more anomalous)
        
        Args:
            X: Input features (n_samples, n_features)
            
        Returns:
            Anomaly scores (range: typically -0.5 to 0.5)
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before prediction")
        
        # decision_function returns the anomaly score
        # Negative scores indicate anomalies
        scores = self.model.decision_function(X)
        
        return scores
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Calculate anomaly probability (0 to 1, higher = more anomalous)
        
        Args:
            X: Input features (n_samples, n_features)
            
        Returns:
            Anomaly probabilities (0 to 1)
        """
        # Get anomaly scores
        scores = self.predict_anomaly_score(X)
        
        # Convert to probabilities using sigmoid-like transformation
        # Normalize scores to 0-1 range where 1 = anomaly
        probabilities = 1 / (1 + np.exp(scores * 2))  # Scale factor of 2 for better separation
        
        return probabilities
    
    def tune_hyperparameters(self, 
                            X_train: np.ndarray,
                            param_grid: Optional[Dict[str, list]] = None,
                            cv: int = 5) -> Dict[str, Any]:
        """
        Tune hyperparameters using cross-validation
        
        Args:
            X_train: Training features
            param_grid: Parameter grid for search
            cv: Number of cross-validation folds
            
        Returns:
            Best parameters found
        """
        self.logger.info("Starting hyperparameter tuning...")
        
        if param_grid is None:
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_samples': ['auto', 256, 512],
                'contamination': [0.05, 0.1, 0.15],
                'max_features': [0.5, 0.75, 1.0]
            }
        
        # Create base model
        base_model = SklearnIsolationForest(random_state=self.random_state, n_jobs=-1)
        
        # Grid search
        grid_search = GridSearchCV(
            base_model,
            param_grid,
            cv=cv,
            scoring='neg_mean_squared_error',  # Use MSE as proxy
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train)
        
        best_params = grid_search.best_params_
        
        self.logger.info(f"Best parameters: {best_params}")
        
        # Update model parameters
        self.n_estimators = best_params.get('n_estimators', self.n_estimators)
        self.max_samples = best_params.get('max_samples', self.max_samples)
        self.contamination = best_params.get('contamination', self.contamination)
        self.max_features = best_params.get('max_features', self.max_features)
        
        return best_params
    
    def cross_validate(self, X: np.ndarray, cv: int = 5) -> Dict[str, float]:
        """
        Perform cross-validation
        
        Args:
            X: Input features
            cv: Number of folds
            
        Returns:
            Cross-validation scores
        """
        self.logger.info(f"Performing {cv}-fold cross-validation...")
        
        model = SklearnIsolationForest(
            n_estimators=self.n_estimators,
            max_samples=self.max_samples,
            contamination=self.contamination,
            max_features=self.max_features,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        scores = cross_val_score(model, X, cv=cv, scoring='neg_mean_squared_error', n_jobs=-1)
        
        results = {
            'mean_score': scores.mean(),
            'std_score': scores.std(),
            'scores': scores.tolist()
        }
        
        self.logger.info(f"Cross-validation mean score: {results['mean_score']:.4f} (+/- {results['std_score']:.4f})")
        
        return results
    
    def save(self, path: str) -> None:
        """
        Save model to file
        
        Args:
            path: Output file path
        """
        if not self.is_trained:
            raise RuntimeError("Cannot save untrained model")
        
        self.logger.info(f"Saving model to {path}")
        
        # Create directory if needed
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save model
        model_data = {
            'model': self.model,
            'n_estimators': self.n_estimators,
            'max_samples': self.max_samples,
            'contamination': self.contamination,
            'max_features': self.max_features,
            'random_state': self.random_state,
            'feature_names': self.feature_names,
            'training_metadata': self.training_metadata,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, path)
        
        # Save metadata separately
        metadata_path = Path(path).with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(self.training_metadata, f, indent=2)
        
        self.logger.info(f"Model saved successfully")
    
    def load(self, path: str) -> None:
        """
        Load model from file
        
        Args:
            path: Input file path
        """
        self.logger.info(f"Loading model from {path}")
        
        if not Path(path).exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        
        # Load model
        model_data = joblib.load(path)
        
        self.model = model_data['model']
        self.n_estimators = model_data['n_estimators']
        self.max_samples = model_data['max_samples']
        self.contamination = model_data['contamination']
        self.max_features = model_data['max_features']
        self.random_state = model_data['random_state']
        self.feature_names = model_data.get('feature_names')
        self.training_metadata = model_data.get('training_metadata', {})
        self.is_trained = model_data['is_trained']
        
        self.logger.info(f"Model loaded successfully (trained on {self.training_metadata.get('n_samples', 'unknown')} samples)")
    
    def get_feature_importance(self) -> Optional[np.ndarray]:
        """
        Get feature importance scores
        
        Note: Isolation Forest doesn't provide direct feature importance,
        but we can estimate it using permutation importance
        
        Returns:
            Feature importance scores (or None if not available)
        """
        self.logger.warning("Isolation Forest doesn't provide direct feature importance")
        return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information
        
        Returns:
            Dictionary with model details
        """
        return {
            'model_type': 'IsolationForest',
            'n_estimators': self.n_estimators,
            'max_samples': self.max_samples,
            'contamination': self.contamination,
            'max_features': self.max_features,
            'is_trained': self.is_trained,
            'training_metadata': self.training_metadata
        }
