"""
Model Ensemble System

Combines predictions from multiple models using weighted voting.
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import json

from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.core.base import RiskLevel
from trade_risk_analyzer.models.isolation_forest import IsolationForestModel
from trade_risk_analyzer.models.autoencoder import AutoencoderModel
from trade_risk_analyzer.models.random_forest import RandomForestModel


logger = get_logger(__name__)


class ModelEnsemble:
    """
    Ensemble system that combines predictions from multiple models
    """
    
    def __init__(self,
                 weights: Optional[Dict[str, float]] = None,
                 high_risk_threshold: float = 0.8,
                 medium_risk_threshold: float = 0.5):
        """
        Initialize model ensemble
        
        Args:
            weights: Dictionary of model weights (must sum to 1.0)
            high_risk_threshold: Threshold for high risk classification
            medium_risk_threshold: Threshold for medium risk classification
        """
        self.weights = weights or {
            'isolation_forest': 0.3,
            'autoencoder': 0.4,
            'random_forest': 0.3
        }
        
        # Validate weights
        if not np.isclose(sum(self.weights.values()), 1.0):
            raise ValueError("Weights must sum to 1.0")
        
        self.high_risk_threshold = high_risk_threshold
        self.medium_risk_threshold = medium_risk_threshold
        
        self.models = {}
        self.logger = logger
    
    def add_model(self, model_name: str, model: Any) -> None:
        """
        Add a model to the ensemble
        
        Args:
            model_name: Name of the model
            model: Model instance
        """
        self.models[model_name] = model
        self.logger.info(f"Added model: {model_name}")
    
    def set_weights(self, weights: Dict[str, float]) -> None:
        """
        Update model weights
        
        Args:
            weights: Dictionary of model weights
        """
        if not np.isclose(sum(weights.values()), 1.0):
            raise ValueError("Weights must sum to 1.0")
        
        self.weights = weights
        self.logger.info(f"Updated weights: {weights}")
    
    def predict_single(self, X: np.ndarray, model_name: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get predictions from a single model
        
        Args:
            X: Input features
            model_name: Name of model to use
            
        Returns:
            Tuple of (predictions, scores)
        """
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found in ensemble")
        
        model = self.models[model_name]
        
        try:
            predictions = model.predict(X)
            scores = model.predict_anomaly_score(X)
            
            # Normalize predictions to 0/1 (0=normal, 1=anomaly)
            if model_name == 'isolation_forest':
                predictions = (predictions == -1).astype(int)
            
            return predictions, scores
        except Exception as e:
            self.logger.error(f"Error predicting with {model_name}: {str(e)}")
            raise
    
    def predict_ensemble(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get ensemble predictions using weighted voting
        
        Args:
            X: Input features (n_samples, n_features)
            
        Returns:
            Tuple of (predictions, ensemble_scores)
        """
        if not self.models:
            raise ValueError("No models in ensemble. Add models first.")
        
        self.logger.info(f"Generating ensemble predictions for {X.shape[0]} samples")
        
        # Collect predictions and scores from each model
        all_predictions = {}
        all_scores = {}
        
        for model_name in self.weights.keys():
            if model_name in self.models:
                try:
                    predictions, scores = self.predict_single(X, model_name)
                    all_predictions[model_name] = predictions
                    all_scores[model_name] = scores
                except Exception as e:
                    self.logger.warning(f"Skipping {model_name} due to error: {str(e)}")
                    continue
        
        if not all_scores:
            raise RuntimeError("No models produced valid predictions")
        
        # Normalize scores to 0-1 range for each model
        normalized_scores = {}
        for model_name, scores in all_scores.items():
            # Convert to probabilities (0-1 range where 1 = anomaly)
            if model_name == 'isolation_forest':
                # Isolation Forest scores are negative for anomalies
                probs = 1 / (1 + np.exp(scores * 2))
            elif model_name == 'autoencoder':
                # Autoencoder uses reconstruction error
                model = self.models[model_name]
                threshold = model.reconstruction_threshold
                probs = 1 / (1 + np.exp(-(scores - threshold) * 10))
            else:
                # Random Forest already provides probabilities
                model = self.models[model_name]
                probs = model.predict_proba(X)
                if probs.ndim > 1:
                    probs = probs[:, 1]  # Probability of anomaly class
            
            normalized_scores[model_name] = probs
        
        # Calculate weighted ensemble scores
        ensemble_scores = np.zeros(X.shape[0])
        total_weight = 0
        
        for model_name, weight in self.weights.items():
            if model_name in normalized_scores:
                ensemble_scores += weight * normalized_scores[model_name]
                total_weight += weight
        
        # Normalize by actual total weight (in case some models failed)
        if total_weight > 0:
            ensemble_scores /= total_weight
        
        # Convert scores to binary predictions
        ensemble_predictions = (ensemble_scores > 0.5).astype(int)
        
        anomaly_count = np.sum(ensemble_predictions)
        self.logger.info(f"Ensemble detected {anomaly_count} anomalies ({anomaly_count/len(X):.2%})")
        
        return ensemble_predictions, ensemble_scores
    
    def predict_with_risk_level(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, List[RiskLevel]]:
        """
        Predict with risk level classification
        
        Args:
            X: Input features
            
        Returns:
            Tuple of (predictions, scores, risk_levels)
        """
        predictions, scores = self.predict_ensemble(X)
        
        # Classify risk levels
        risk_levels = []
        for score in scores:
            if score >= self.high_risk_threshold:
                risk_levels.append(RiskLevel.HIGH)
            elif score >= self.medium_risk_threshold:
                risk_levels.append(RiskLevel.MEDIUM)
            else:
                risk_levels.append(RiskLevel.LOW)
        
        # Count risk levels
        high_count = sum(1 for r in risk_levels if r == RiskLevel.HIGH)
        medium_count = sum(1 for r in risk_levels if r == RiskLevel.MEDIUM)
        low_count = sum(1 for r in risk_levels if r == RiskLevel.LOW)
        
        self.logger.info(f"Risk levels: HIGH={high_count}, MEDIUM={medium_count}, LOW={low_count}")
        
        return predictions, scores, risk_levels
    
    def predict_with_fallback(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict with fallback logic when models fail
        
        Args:
            X: Input features
            
        Returns:
            Tuple of (predictions, scores)
        """
        try:
            # Try ensemble prediction first
            return self.predict_ensemble(X)
        except Exception as e:
            self.logger.error(f"Ensemble prediction failed: {str(e)}")
            
            # Fallback: try each model individually
            for model_name in ['isolation_forest', 'autoencoder', 'random_forest']:
                if model_name in self.models:
                    try:
                        self.logger.info(f"Falling back to {model_name}")
                        predictions, scores = self.predict_single(X, model_name)
                        
                        # Normalize scores
                        if model_name == 'isolation_forest':
                            scores = 1 / (1 + np.exp(scores * 2))
                        elif model_name == 'autoencoder':
                            model = self.models[model_name]
                            threshold = model.reconstruction_threshold
                            scores = 1 / (1 + np.exp(-(scores - threshold) * 10))
                        
                        return predictions, scores
                    except Exception as e2:
                        self.logger.error(f"{model_name} also failed: {str(e2)}")
                        continue
            
            # If all models fail, return conservative predictions
            self.logger.error("All models failed. Returning conservative predictions.")
            return np.zeros(X.shape[0], dtype=int), np.zeros(X.shape[0])
    
    def get_model_contributions(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Get individual model contributions to ensemble prediction
        
        Args:
            X: Input features
            
        Returns:
            Dictionary of model scores
        """
        contributions = {}
        
        for model_name in self.weights.keys():
            if model_name in self.models:
                try:
                    _, scores = self.predict_single(X, model_name)
                    
                    # Normalize scores
                    if model_name == 'isolation_forest':
                        scores = 1 / (1 + np.exp(scores * 2))
                    elif model_name == 'autoencoder':
                        model = self.models[model_name]
                        threshold = model.reconstruction_threshold
                        scores = 1 / (1 + np.exp(-(scores - threshold) * 10))
                    else:
                        model = self.models[model_name]
                        probs = model.predict_proba(X)
                        if probs.ndim > 1:
                            scores = probs[:, 1]
                        else:
                            scores = probs
                    
                    contributions[model_name] = scores
                except Exception as e:
                    self.logger.warning(f"Could not get contribution from {model_name}: {str(e)}")
        
        return contributions
    
    def explain_prediction(self, X: np.ndarray, sample_idx: int) -> Dict[str, Any]:
        """
        Explain ensemble prediction for a single sample
        
        Args:
            X: Input features
            sample_idx: Index of sample to explain
            
        Returns:
            Dictionary with explanation details
        """
        # Get ensemble prediction
        predictions, scores = self.predict_ensemble(X)
        
        # Get individual model contributions
        contributions = self.get_model_contributions(X)
        
        # Build explanation
        explanation = {
            'sample_index': sample_idx,
            'ensemble_prediction': int(predictions[sample_idx]),
            'ensemble_score': float(scores[sample_idx]),
            'risk_level': self._score_to_risk_level(scores[sample_idx]).value,
            'model_contributions': {}
        }
        
        for model_name, model_scores in contributions.items():
            weight = self.weights.get(model_name, 0)
            contribution = weight * model_scores[sample_idx]
            
            explanation['model_contributions'][model_name] = {
                'score': float(model_scores[sample_idx]),
                'weight': weight,
                'weighted_contribution': float(contribution)
            }
        
        return explanation
    
    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert anomaly score to risk level"""
        if score >= self.high_risk_threshold:
            return RiskLevel.HIGH
        elif score >= self.medium_risk_threshold:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def save_config(self, path: str) -> None:
        """
        Save ensemble configuration
        
        Args:
            path: Output file path
        """
        config = {
            'weights': self.weights,
            'high_risk_threshold': self.high_risk_threshold,
            'medium_risk_threshold': self.medium_risk_threshold,
            'models': list(self.models.keys())
        }
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.logger.info(f"Ensemble config saved to {path}")
    
    def load_config(self, path: str) -> None:
        """
        Load ensemble configuration
        
        Args:
            path: Input file path
        """
        with open(path, 'r') as f:
            config = json.load(f)
        
        self.weights = config['weights']
        self.high_risk_threshold = config['high_risk_threshold']
        self.medium_risk_threshold = config['medium_risk_threshold']
        
        self.logger.info(f"Ensemble config loaded from {path}")
    
    def get_ensemble_info(self) -> Dict[str, Any]:
        """
        Get ensemble information
        
        Returns:
            Dictionary with ensemble details
        """
        return {
            'n_models': len(self.models),
            'models': list(self.models.keys()),
            'weights': self.weights,
            'high_risk_threshold': self.high_risk_threshold,
            'medium_risk_threshold': self.medium_risk_threshold
        }
