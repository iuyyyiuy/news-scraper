"""
Autoencoder Model Implementation

Deep learning-based anomaly detection using reconstruction error.
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime

from trade_risk_analyzer.core.base import BaseModel
from trade_risk_analyzer.core.logger import get_logger


logger = get_logger(__name__)


class AutoencoderModel(BaseModel):
    """
    Autoencoder model for anomaly detection using reconstruction error
    """
    
    def __init__(self,
                 encoding_dim: int = 32,
                 hidden_layers: list = [64, 32],
                 activation: str = 'relu',
                 learning_rate: float = 0.001,
                 batch_size: int = 32,
                 epochs: int = 100,
                 validation_split: float = 0.2,
                 early_stopping_patience: int = 10,
                 random_state: int = 42):
        """
        Initialize Autoencoder model
        
        Args:
            encoding_dim: Dimension of the encoded representation
            hidden_layers: List of hidden layer sizes
            activation: Activation function
            learning_rate: Learning rate for optimizer
            batch_size: Batch size for training
            epochs: Maximum number of training epochs
            validation_split: Fraction of data for validation
            early_stopping_patience: Patience for early stopping
            random_state: Random seed
        """
        self.encoding_dim = encoding_dim
        self.hidden_layers = hidden_layers
        self.activation = activation
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.epochs = epochs
        self.validation_split = validation_split
        self.early_stopping_patience = early_stopping_patience
        self.random_state = random_state
        
        self.model = None
        self.encoder = None
        self.decoder = None
        self.is_trained = False
        self.input_dim = None
        self.training_history = None
        self.reconstruction_threshold = None
        self.training_metadata = {}
        
        self.logger = logger
        
        # Set random seeds
        tf.random.set_seed(random_state)
        np.random.seed(random_state)
    
    def _build_model(self, input_dim: int) -> None:
        """
        Build autoencoder architecture
        
        Args:
            input_dim: Input feature dimension
        """
        self.input_dim = input_dim
        
        # Input layer
        input_layer = layers.Input(shape=(input_dim,))
        
        # Encoder
        encoded = input_layer
        for units in self.hidden_layers:
            encoded = layers.Dense(units, activation=self.activation)(encoded)
            encoded = layers.Dropout(0.2)(encoded)
        
        # Bottleneck
        encoded = layers.Dense(self.encoding_dim, activation=self.activation, name='encoding')(encoded)
        
        # Decoder
        decoded = encoded
        for units in reversed(self.hidden_layers):
            decoded = layers.Dense(units, activation=self.activation)(decoded)
            decoded = layers.Dropout(0.2)(decoded)
        
        # Output layer
        decoded = layers.Dense(input_dim, activation='linear')(decoded)
        
        # Full autoencoder
        self.model = models.Model(inputs=input_layer, outputs=decoded, name='autoencoder')
        
        # Encoder model (for getting encodings)
        self.encoder = models.Model(inputs=input_layer, outputs=encoded, name='encoder')
        
        # Compile model
        optimizer = keras.optimizers.Adam(learning_rate=self.learning_rate)
        self.model.compile(
            optimizer=optimizer,
            loss='mse',
            metrics=['mae']
        )
        
        self.logger.info(f"Built autoencoder: {input_dim} -> {self.hidden_layers} -> {self.encoding_dim}")
    
    def train(self, X_train: np.ndarray, y_train: Optional[np.ndarray] = None) -> None:
        """
        Train the autoencoder model
        
        Args:
            X_train: Training features (n_samples, n_features)
            y_train: Not used (unsupervised learning)
        """
        self.logger.info(f"Training Autoencoder with {X_train.shape[0]} samples, {X_train.shape[1]} features")
        
        # Build model if not already built
        if self.model is None:
            self._build_model(X_train.shape[1])
        
        # Callbacks
        callback_list = [
            callbacks.EarlyStopping(
                monitor='val_loss',
                patience=self.early_stopping_patience,
                restore_best_weights=True,
                verbose=1
            ),
            callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7,
                verbose=1
            )
        ]
        
        # Train model (autoencoder learns to reconstruct input)
        history = self.model.fit(
            X_train, X_train,  # Input = Output for autoencoder
            batch_size=self.batch_size,
            epochs=self.epochs,
            validation_split=self.validation_split,
            callbacks=callback_list,
            verbose=1
        )
        
        self.training_history = history.history
        self.is_trained = True
        
        # Calculate reconstruction threshold (95th percentile of training errors)
        train_reconstructions = self.model.predict(X_train, verbose=0)
        train_errors = np.mean(np.square(X_train - train_reconstructions), axis=1)
        self.reconstruction_threshold = np.percentile(train_errors, 95)
        
        # Store training metadata
        self.training_metadata = {
            'n_samples': X_train.shape[0],
            'n_features': X_train.shape[1],
            'encoding_dim': self.encoding_dim,
            'hidden_layers': self.hidden_layers,
            'epochs_trained': len(history.history['loss']),
            'final_loss': float(history.history['loss'][-1]),
            'final_val_loss': float(history.history['val_loss'][-1]),
            'reconstruction_threshold': float(self.reconstruction_threshold),
            'trained_at': datetime.now().isoformat()
        }
        
        self.logger.info(f"Autoencoder training complete (epochs: {self.training_metadata['epochs_trained']})")
        self.logger.info(f"Reconstruction threshold: {self.reconstruction_threshold:.6f}")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict anomaly labels (1 for anomaly, 0 for normal)
        
        Args:
            X: Input features (n_samples, n_features)
            
        Returns:
            Predictions (1 for anomaly, 0 for normal)
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before prediction")
        
        # Calculate reconstruction errors
        reconstruction_errors = self.calculate_reconstruction_error(X)
        
        # Classify as anomaly if error exceeds threshold
        predictions = (reconstruction_errors > self.reconstruction_threshold).astype(int)
        
        self.logger.info(f"Predicted {np.sum(predictions)} anomalies out of {len(predictions)} samples")
        
        return predictions
    
    def calculate_reconstruction_error(self, X: np.ndarray) -> np.ndarray:
        """
        Calculate reconstruction error for each sample
        
        Args:
            X: Input features (n_samples, n_features)
            
        Returns:
            Reconstruction errors (MSE per sample)
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before prediction")
        
        # Reconstruct inputs
        reconstructions = self.model.predict(X, verbose=0)
        
        # Calculate MSE for each sample
        errors = np.mean(np.square(X - reconstructions), axis=1)
        
        return errors
    
    def predict_anomaly_score(self, X: np.ndarray) -> np.ndarray:
        """
        Calculate anomaly scores (higher = more anomalous)
        
        Args:
            X: Input features (n_samples, n_features)
            
        Returns:
            Anomaly scores (reconstruction errors)
        """
        return self.calculate_reconstruction_error(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Calculate anomaly probability (0 to 1, higher = more anomalous)
        
        Args:
            X: Input features (n_samples, n_features)
            
        Returns:
            Anomaly probabilities (0 to 1)
        """
        # Get reconstruction errors
        errors = self.calculate_reconstruction_error(X)
        
        # Normalize to 0-1 using sigmoid with threshold as midpoint
        probabilities = 1 / (1 + np.exp(-(errors - self.reconstruction_threshold) * 10))
        
        return probabilities
    
    def get_encoding(self, X: np.ndarray) -> np.ndarray:
        """
        Get encoded representation of inputs
        
        Args:
            X: Input features
            
        Returns:
            Encoded features
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before encoding")
        
        return self.encoder.predict(X, verbose=0)
    
    def save(self, path: str) -> None:
        """
        Save model to file
        
        Args:
            path: Output file path (without extension)
        """
        if not self.is_trained:
            raise RuntimeError("Cannot save untrained model")
        
        self.logger.info(f"Saving model to {path}")
        
        # Create directory if needed
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save Keras model
        model_path = f"{path}_model.keras"
        self.model.save(model_path)
        
        # Save encoder separately
        encoder_path = f"{path}_encoder.keras"
        self.encoder.save(encoder_path)
        
        # Save configuration and metadata
        config = {
            'encoding_dim': self.encoding_dim,
            'hidden_layers': self.hidden_layers,
            'activation': self.activation,
            'learning_rate': self.learning_rate,
            'batch_size': self.batch_size,
            'epochs': self.epochs,
            'validation_split': self.validation_split,
            'early_stopping_patience': self.early_stopping_patience,
            'random_state': self.random_state,
            'input_dim': self.input_dim,
            'reconstruction_threshold': float(self.reconstruction_threshold) if self.reconstruction_threshold else None,
            'training_metadata': self.training_metadata,
            'is_trained': self.is_trained
        }
        
        config_path = f"{path}_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.logger.info(f"Model saved successfully")
    
    def load(self, path: str) -> None:
        """
        Load model from file
        
        Args:
            path: Input file path (without extension)
        """
        self.logger.info(f"Loading model from {path}")
        
        # Load configuration
        config_path = f"{path}_config.json"
        if not Path(config_path).exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Restore configuration
        self.encoding_dim = config['encoding_dim']
        self.hidden_layers = config['hidden_layers']
        self.activation = config['activation']
        self.learning_rate = config['learning_rate']
        self.batch_size = config['batch_size']
        self.epochs = config['epochs']
        self.validation_split = config['validation_split']
        self.early_stopping_patience = config['early_stopping_patience']
        self.random_state = config['random_state']
        self.input_dim = config['input_dim']
        self.reconstruction_threshold = config['reconstruction_threshold']
        self.training_metadata = config['training_metadata']
        self.is_trained = config['is_trained']
        
        # Load Keras models
        model_path = f"{path}_model.keras"
        encoder_path = f"{path}_encoder.keras"
        
        self.model = keras.models.load_model(model_path)
        self.encoder = keras.models.load_model(encoder_path)
        
        self.logger.info(f"Model loaded successfully")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information
        
        Returns:
            Dictionary with model details
        """
        return {
            'model_type': 'Autoencoder',
            'encoding_dim': self.encoding_dim,
            'hidden_layers': self.hidden_layers,
            'input_dim': self.input_dim,
            'reconstruction_threshold': self.reconstruction_threshold,
            'is_trained': self.is_trained,
            'training_metadata': self.training_metadata
        }
