"""
Random Forest Classifier Implementation

Supervised classification for anomaly detection with labeled data.
"""

import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier as SklearnRandomForest
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.utils.class_weight import compute_class_weight
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime

from trade_risk_analyzer.core.base import BaseModel
from trade_risk_analyzer.core.logger import get_logger


logger = get_logger(__name__)


class RandomForestModel(BaseModel):
    """
    Random Forest classifier for supervised anomaly detection
    """
    
    def __init__(self,
                 n_estimators: int = 100,
                 max_depth: Optional[int] = None,
                 min_samples_split: int = 2,
                 min_samples_leaf: int = 1,
                 max_features: str = 'sqrt',
                 class_weight: str = 'balanced',
                 random_state: int = 42):
        """
        Initialize Random Forest classifier
        
        Args:
            n_estimators: Number of trees in the forest
            max_depth: Maximum depth of trees
            min_samples_split: Minimum samples required to split a node
            min_samples_leaf: Minimum samples required at leaf node
            max_features: Number of features to consider for best split
            class_weight: Weights for class balancing ('balanced' or None)
            random_state: Random seed
        """
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.max_features = max_features
        self.class_weight = class_weight
        self.random_state = random_state
        
        self.model = None
        self.is_trained = False
        self.feature_names = None
        self.feature_importances = None
        self.classes = None
        self.training_metadata = {}
        
        self.logger = logger
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """
        Train the Random Forest classifier
        
        Args:
            X_train: Training features (n_samples, n_features)
            y_train: Training labels (n_samples,)
        """
        self.logger.info(f"Training Random Forest with {X_train.shape[0]} samples, {X_train.shape[1]} features")
        
        # Check class distribution
        unique, counts = np.unique(y_train, return_counts=True)
        class_dist = dict(zip(unique, counts))
        self.logger.info(f"Class distribution: {class_dist}")
        
        # Initialize model
        self.model = SklearnRandomForest(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            max_features=self.max_features,
            class_weight=self.class_weight,
            random_state=self.random_state,
            n_jobs=-1,
            verbose=0
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        
        self.is_trained = True
        self.classes = self.model.classes_
        self.feature_importances = self.model.feature_importances_
        
        # Store training metadata
        self.training_metadata = {
            'n_samples': X_train.shape[0],
            'n_features': X_train.shape[1],
            'n_estimators': self.n_estimators,
            'class_distribution': class_dist,
            'classes': self.classes.tolist(),
            'trained_at': datetime.now().isoformat()
        }
        
        self.logger.info("Random Forest training complete")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class labels
        
        Args:
            X: Input features (n_samples, n_features)
            
        Returns:
            Predicted class labels
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before prediction")
        
        predictions = self.model.predict(X)
        
        unique, counts = np.unique(predictions, return_counts=True)
        pred_dist = dict(zip(unique, counts))
        self.logger.info(f"Predicted distribution: {pred_dist}")
        
        return predictions
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities
        
        Args:
            X: Input features (n_samples, n_features)
            
        Returns:
            Class probabilities (n_samples, n_classes)
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before prediction")
        
        probabilities = self.model.predict_proba(X)
        
        return probabilities
    
    def predict_anomaly_score(self, X: np.ndarray) -> np.ndarray:
        """
        Calculate anomaly scores (probability of anomaly class)
        
        Args:
            X: Input features (n_samples, n_features)
            
        Returns:
            Anomaly scores (probability of positive class)
        """
        probabilities = self.predict_proba(X)
        
        # Assuming binary classification where 1 = anomaly
        # Return probability of anomaly class
        if probabilities.shape[1] == 2:
            return probabilities[:, 1]
        else:
            # For multi-class, return max probability
            return np.max(probabilities, axis=1)
    
    def get_feature_importance(self) -> np.ndarray:
        """
        Get feature importance scores
        
        Returns:
            Feature importance scores
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained first")
        
        return self.feature_importances
    
    def get_top_features(self, n: int = 10) -> list:
        """
        Get top N most important features
        
        Args:
            n: Number of top features to return
            
        Returns:
            List of (feature_index, importance_score) tuples
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained first")
        
        # Sort features by importance
        indices = np.argsort(self.feature_importances)[::-1]
        
        top_features = [
            (int(idx), float(self.feature_importances[idx]))
            for idx in indices[:n]
        ]
        
        return top_features
    
    def tune_hyperparameters(self,
                            X_train: np.ndarray,
                            y_train: np.ndarray,
                            param_grid: Optional[Dict[str, list]] = None,
                            cv: int = 5) -> Dict[str, Any]:
        """
        Tune hyperparameters using cross-validation
        
        Args:
            X_train: Training features
            y_train: Training labels
            param_grid: Parameter grid for search
            cv: Number of cross-validation folds
            
        Returns:
            Best parameters found
        """
        self.logger.info("Starting hyperparameter tuning...")
        
        if param_grid is None:
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4],
                'max_features': ['sqrt', 'log2']
            }
        
        # Create base model
        base_model = SklearnRandomForest(
            class_weight=self.class_weight,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        # Grid search
        grid_search = GridSearchCV(
            base_model,
            param_grid,
            cv=cv,
            scoring='f1',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        best_params = grid_search.best_params_
        
        self.logger.info(f"Best parameters: {best_params}")
        self.logger.info(f"Best F1 score: {grid_search.best_score_:.4f}")
        
        # Update model parameters
        self.n_estimators = best_params.get('n_estimators', self.n_estimators)
        self.max_depth = best_params.get('max_depth', self.max_depth)
        self.min_samples_split = best_params.get('min_samples_split', self.min_samples_split)
        self.min_samples_leaf = best_params.get('min_samples_leaf', self.min_samples_leaf)
        self.max_features = best_params.get('max_features', self.max_features)
        
        return best_params
    
    def cross_validate(self, X: np.ndarray, y: np.ndarray, cv: int = 5) -> Dict[str, float]:
        """
        Perform cross-validation
        
        Args:
            X: Input features
            y: Labels
            cv: Number of folds
            
        Returns:
            Cross-validation scores
        """
        self.logger.info(f"Performing {cv}-fold cross-validation...")
        
        model = SklearnRandomForest(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            max_features=self.max_features,
            class_weight=self.class_weight,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        # Multiple scoring metrics
        scoring = ['accuracy', 'precision', 'recall', 'f1']
        results = {}
        
        for metric in scoring:
            scores = cross_val_score(model, X, y, cv=cv, scoring=metric, n_jobs=-1)
            results[f'{metric}_mean'] = scores.mean()
            results[f'{metric}_std'] = scores.std()
            results[f'{metric}_scores'] = scores.tolist()
            
            self.logger.info(f"{metric}: {scores.mean():.4f} (+/- {scores.std():.4f})")
        
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
            'max_depth': self.max_depth,
            'min_samples_split': self.min_samples_split,
            'min_samples_leaf': self.min_samples_leaf,
            'max_features': self.max_features,
            'class_weight': self.class_weight,
            'random_state': self.random_state,
            'feature_names': self.feature_names,
            'feature_importances': self.feature_importances,
            'classes': self.classes,
            'training_metadata': self.training_metadata,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, path)
        
        # Save metadata separately
        metadata_path = Path(path).with_suffix('.json')
        
        # Convert numpy types to Python types for JSON serialization
        training_metadata_json = {}
        for key, value in self.training_metadata.items():
            if isinstance(value, dict):
                training_metadata_json[key] = {str(k): int(v) if isinstance(v, (np.integer, np.int64)) else v 
                                              for k, v in value.items()}
            elif isinstance(value, (list, np.ndarray)):
                training_metadata_json[key] = [int(x) if isinstance(x, (np.integer, np.int64)) else x for x in value]
            else:
                training_metadata_json[key] = value
        
        metadata = {
            **training_metadata_json,
            'feature_importances': self.feature_importances.tolist() if self.feature_importances is not None else None
        }
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
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
        self.max_depth = model_data['max_depth']
        self.min_samples_split = model_data['min_samples_split']
        self.min_samples_leaf = model_data['min_samples_leaf']
        self.max_features = model_data['max_features']
        self.class_weight = model_data['class_weight']
        self.random_state = model_data['random_state']
        self.feature_names = model_data.get('feature_names')
        self.feature_importances = model_data.get('feature_importances')
        self.classes = model_data.get('classes')
        self.training_metadata = model_data.get('training_metadata', {})
        self.is_trained = model_data['is_trained']
        
        self.logger.info(f"Model loaded successfully")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information
        
        Returns:
            Dictionary with model details
        """
        return {
            'model_type': 'RandomForest',
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'min_samples_split': self.min_samples_split,
            'min_samples_leaf': self.min_samples_leaf,
            'max_features': self.max_features,
            'class_weight': self.class_weight,
            'classes': self.classes.tolist() if self.classes is not None else None,
            'is_trained': self.is_trained,
            'training_metadata': self.training_metadata
        }
