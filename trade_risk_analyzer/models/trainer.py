"""
Model Training Orchestrator

Handles data splitting, training pipeline, evaluation, and model selection.
"""

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    precision_score, recall_score, f1_score, accuracy_score,
    roc_auc_score, confusion_matrix, classification_report
)
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
import json
from datetime import datetime

from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.models.isolation_forest import IsolationForestModel
from trade_risk_analyzer.models.autoencoder import AutoencoderModel
from trade_risk_analyzer.models.random_forest import RandomForestModel


logger = get_logger(__name__)


class ModelTrainer:
    """
    Orchestrates training pipeline for all model types
    """
    
    def __init__(self,
                 train_split: float = 0.70,
                 val_split: float = 0.15,
                 test_split: float = 0.15,
                 random_state: int = 42):
        """
        Initialize model trainer
        
        Args:
            train_split: Fraction of data for training
            val_split: Fraction of data for validation
            test_split: Fraction of data for testing
            random_state: Random seed
        """
        if not np.isclose(train_split + val_split + test_split, 1.0):
            raise ValueError("Splits must sum to 1.0")
        
        self.train_split = train_split
        self.val_split = val_split
        self.test_split = test_split
        self.random_state = random_state
        
        self.logger = logger
        
        # Store split data
        self.X_train = None
        self.X_val = None
        self.X_test = None
        self.y_train = None
        self.y_val = None
        self.y_test = None
        
        # Store trained models
        self.models = {}
        self.evaluation_results = {}
    
    def split_data(self,
                   X: np.ndarray,
                   y: Optional[np.ndarray] = None) -> Tuple[np.ndarray, ...]:
        """
        Split data into train/val/test sets
        
        Args:
            X: Features (n_samples, n_features)
            y: Labels (n_samples,) - optional for unsupervised
            
        Returns:
            Tuple of (X_train, X_val, X_test, y_train, y_val, y_test)
        """
        self.logger.info(f"Splitting data: {X.shape[0]} samples")
        self.logger.info(f"Splits: train={self.train_split}, val={self.val_split}, test={self.test_split}")
        
        if y is not None:
            # Supervised split with stratification
            # First split: train+val vs test
            X_temp, X_test, y_temp, y_test = train_test_split(
                X, y,
                test_size=self.test_split,
                random_state=self.random_state,
                stratify=y
            )
            
            # Second split: train vs val
            val_size_adjusted = self.val_split / (self.train_split + self.val_split)
            X_train, X_val, y_train, y_val = train_test_split(
                X_temp, y_temp,
                test_size=val_size_adjusted,
                random_state=self.random_state,
                stratify=y_temp
            )
        else:
            # Unsupervised split
            X_temp, X_test = train_test_split(
                X,
                test_size=self.test_split,
                random_state=self.random_state
            )
            
            val_size_adjusted = self.val_split / (self.train_split + self.val_split)
            X_train, X_val = train_test_split(
                X_temp,
                test_size=val_size_adjusted,
                random_state=self.random_state
            )
            
            y_train = y_val = y_test = None
        
        # Store splits
        self.X_train = X_train
        self.X_val = X_val
        self.X_test = X_test
        self.y_train = y_train
        self.y_val = y_val
        self.y_test = y_test
        
        self.logger.info(f"Train: {X_train.shape[0]} samples")
        self.logger.info(f"Val: {X_val.shape[0]} samples")
        self.logger.info(f"Test: {X_test.shape[0]} samples")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def train_isolation_forest(self,
                               X_train: Optional[np.ndarray] = None,
                               **model_params) -> IsolationForestModel:
        """
        Train Isolation Forest model
        
        Args:
            X_train: Training features (uses stored if None)
            **model_params: Model hyperparameters
            
        Returns:
            Trained model
        """
        self.logger.info("Training Isolation Forest model...")
        
        X_train = X_train if X_train is not None else self.X_train
        
        if X_train is None:
            raise ValueError("No training data available. Call split_data first.")
        
        # Initialize model
        model = IsolationForestModel(**model_params)
        
        # Train
        model.train(X_train)
        
        # Store model
        self.models['isolation_forest'] = model
        
        self.logger.info("Isolation Forest training complete")
        
        return model
    
    def train_autoencoder(self,
                         X_train: Optional[np.ndarray] = None,
                         **model_params) -> AutoencoderModel:
        """
        Train Autoencoder model
        
        Args:
            X_train: Training features (uses stored if None)
            **model_params: Model hyperparameters
            
        Returns:
            Trained model
        """
        self.logger.info("Training Autoencoder model...")
        
        X_train = X_train if X_train is not None else self.X_train
        
        if X_train is None:
            raise ValueError("No training data available. Call split_data first.")
        
        # Initialize model
        model = AutoencoderModel(**model_params)
        
        # Train
        model.train(X_train)
        
        # Store model
        self.models['autoencoder'] = model
        
        self.logger.info("Autoencoder training complete")
        
        return model
    
    def train_random_forest(self,
                           X_train: Optional[np.ndarray] = None,
                           y_train: Optional[np.ndarray] = None,
                           **model_params) -> RandomForestModel:
        """
        Train Random Forest model
        
        Args:
            X_train: Training features (uses stored if None)
            y_train: Training labels (uses stored if None)
            **model_params: Model hyperparameters
            
        Returns:
            Trained model
        """
        self.logger.info("Training Random Forest model...")
        
        X_train = X_train if X_train is not None else self.X_train
        y_train = y_train if y_train is not None else self.y_train
        
        if X_train is None or y_train is None:
            raise ValueError("No training data/labels available. Call split_data first with labels.")
        
        # Initialize model
        model = RandomForestModel(**model_params)
        
        # Train
        model.train(X_train, y_train)
        
        # Store model
        self.models['random_forest'] = model
        
        self.logger.info("Random Forest training complete")
        
        return model
    
    def train_all_models(self,
                        X: np.ndarray,
                        y: Optional[np.ndarray] = None,
                        isolation_forest_params: Optional[Dict] = None,
                        autoencoder_params: Optional[Dict] = None,
                        random_forest_params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Train all three model types
        
        Args:
            X: Features
            y: Labels (optional, required for Random Forest)
            isolation_forest_params: Isolation Forest hyperparameters
            autoencoder_params: Autoencoder hyperparameters
            random_forest_params: Random Forest hyperparameters
            
        Returns:
            Dictionary of trained models
        """
        self.logger.info("Training all models...")
        
        # Split data
        self.split_data(X, y)
        
        # Train Isolation Forest
        if_params = isolation_forest_params or {}
        self.train_isolation_forest(**if_params)
        
        # Train Autoencoder
        ae_params = autoencoder_params or {}
        self.train_autoencoder(**ae_params)
        
        # Train Random Forest (if labels provided)
        if y is not None:
            rf_params = random_forest_params or {}
            self.train_random_forest(**rf_params)
        else:
            self.logger.info("Skipping Random Forest (no labels provided)")
        
        self.logger.info(f"Trained {len(self.models)} models")
        
        return self.models
    
    def evaluate_model(self,
                      model_name: str,
                      X_test: Optional[np.ndarray] = None,
                      y_test: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Evaluate a trained model
        
        Args:
            model_name: Name of model to evaluate
            X_test: Test features (uses stored if None)
            y_test: Test labels (uses stored if None)
            
        Returns:
            Evaluation metrics
        """
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found. Train it first.")
        
        X_test = X_test if X_test is not None else self.X_test
        y_test = y_test if y_test is not None else self.y_test
        
        if X_test is None:
            raise ValueError("No test data available")
        
        model = self.models[model_name]
        
        self.logger.info(f"Evaluating {model_name}...")
        
        # Get predictions
        y_pred = model.predict(X_test)
        y_scores = model.predict_anomaly_score(X_test)
        
        metrics = {
            'model_name': model_name,
            'n_test_samples': len(X_test)
        }
        
        # If we have true labels, calculate supervised metrics
        if y_test is not None:
            # Convert predictions to binary (1 = anomaly, 0 = normal)
            if model_name in ['isolation_forest']:
                y_pred_binary = (y_pred == -1).astype(int)
            else:
                y_pred_binary = y_pred
            
            metrics['accuracy'] = accuracy_score(y_test, y_pred_binary)
            metrics['precision'] = precision_score(y_test, y_pred_binary, zero_division=0)
            metrics['recall'] = recall_score(y_test, y_pred_binary, zero_division=0)
            metrics['f1_score'] = f1_score(y_test, y_pred_binary, zero_division=0)
            
            # ROC-AUC (if we have probability scores)
            try:
                if hasattr(model, 'predict_proba'):
                    y_proba = model.predict_proba(X_test)
                    if y_proba.ndim > 1 and y_proba.shape[1] > 1:
                        metrics['auc_roc'] = roc_auc_score(y_test, y_proba[:, 1])
                    else:
                        metrics['auc_roc'] = roc_auc_score(y_test, y_proba)
                else:
                    metrics['auc_roc'] = roc_auc_score(y_test, y_scores)
            except Exception as e:
                self.logger.warning(f"Could not calculate AUC-ROC: {str(e)}")
                metrics['auc_roc'] = None
            
            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred_binary)
            metrics['confusion_matrix'] = cm.tolist()
            
            # Classification report
            report = classification_report(y_test, y_pred_binary, output_dict=True, zero_division=0)
            metrics['classification_report'] = report
            
            self.logger.info(f"Accuracy: {metrics['accuracy']:.4f}")
            self.logger.info(f"Precision: {metrics['precision']:.4f}")
            self.logger.info(f"Recall: {metrics['recall']:.4f}")
            self.logger.info(f"F1-Score: {metrics['f1_score']:.4f}")
            if metrics['auc_roc']:
                self.logger.info(f"AUC-ROC: {metrics['auc_roc']:.4f}")
        else:
            # Unsupervised metrics
            anomaly_count = np.sum(y_pred == -1) if model_name == 'isolation_forest' else np.sum(y_pred == 1)
            metrics['anomaly_ratio'] = anomaly_count / len(X_test)
            metrics['mean_anomaly_score'] = float(np.mean(y_scores))
            metrics['std_anomaly_score'] = float(np.std(y_scores))
            
            self.logger.info(f"Anomaly ratio: {metrics['anomaly_ratio']:.4f}")
            self.logger.info(f"Mean anomaly score: {metrics['mean_anomaly_score']:.4f}")
        
        # Store results
        self.evaluation_results[model_name] = metrics
        
        return metrics
    
    def evaluate_all_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Evaluate all trained models
        
        Returns:
            Dictionary of evaluation results for each model
        """
        self.logger.info("Evaluating all models...")
        
        for model_name in self.models.keys():
            self.evaluate_model(model_name)
        
        return self.evaluation_results
    
    def select_best_model(self, metric: str = 'f1_score') -> Tuple[str, Any]:
        """
        Select best model based on validation performance
        
        Args:
            metric: Metric to use for selection
            
        Returns:
            Tuple of (best_model_name, best_model)
        """
        if not self.evaluation_results:
            raise ValueError("No evaluation results available. Run evaluate_all_models first.")
        
        self.logger.info(f"Selecting best model based on {metric}...")
        
        best_score = -np.inf
        best_model_name = None
        
        for model_name, metrics in self.evaluation_results.items():
            if metric in metrics:
                score = metrics[metric]
                if score > best_score:
                    best_score = score
                    best_model_name = model_name
        
        if best_model_name is None:
            raise ValueError(f"Metric '{metric}' not found in evaluation results")
        
        best_model = self.models[best_model_name]
        
        self.logger.info(f"Best model: {best_model_name} ({metric}={best_score:.4f})")
        
        return best_model_name, best_model
    
    def save_models(self, output_dir: str) -> None:
        """
        Save all trained models with metadata
        
        Args:
            output_dir: Output directory path
        """
        self.logger.info(f"Saving models to {output_dir}")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save each model
        for model_name, model in self.models.items():
            model_path = output_path / f"{model_name}"
            model.save(str(model_path))
            
            self.logger.info(f"Saved {model_name}")
        
        # Save evaluation results
        results_path = output_path / "evaluation_results.json"
        with open(results_path, 'w') as f:
            json.dump(self.evaluation_results, f, indent=2)
        
        # Save training metadata
        metadata = {
            'train_split': self.train_split,
            'val_split': self.val_split,
            'test_split': self.test_split,
            'random_state': self.random_state,
            'models_trained': list(self.models.keys()),
            'saved_at': datetime.now().isoformat()
        }
        
        metadata_path = output_path / "training_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"All models and metadata saved to {output_dir}")
    
    def load_models(self, input_dir: str) -> Dict[str, Any]:
        """
        Load trained models from directory
        
        Args:
            input_dir: Input directory path
            
        Returns:
            Dictionary of loaded models
        """
        self.logger.info(f"Loading models from {input_dir}")
        
        input_path = Path(input_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_dir}")
        
        # Load metadata
        metadata_path = input_path / "training_metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                self.logger.info(f"Models trained: {metadata.get('models_trained', [])}")
        
        # Load each model
        self.models = {}
        
        # Try to load Isolation Forest
        if_path = input_path / "isolation_forest"
        if if_path.exists():
            model = IsolationForestModel()
            model.load(str(if_path))
            self.models['isolation_forest'] = model
            self.logger.info("Loaded Isolation Forest")
        
        # Try to load Autoencoder
        ae_path = input_path / "autoencoder"
        if (ae_path.parent / f"{ae_path.name}_config.json").exists():
            model = AutoencoderModel()
            model.load(str(ae_path))
            self.models['autoencoder'] = model
            self.logger.info("Loaded Autoencoder")
        
        # Try to load Random Forest
        rf_path = input_path / "random_forest"
        if rf_path.exists():
            model = RandomForestModel()
            model.load(str(rf_path))
            self.models['random_forest'] = model
            self.logger.info("Loaded Random Forest")
        
        # Load evaluation results
        results_path = input_path / "evaluation_results.json"
        if results_path.exists():
            with open(results_path, 'r') as f:
                self.evaluation_results = json.load(f)
        
        self.logger.info(f"Loaded {len(self.models)} models")
        
        return self.models
