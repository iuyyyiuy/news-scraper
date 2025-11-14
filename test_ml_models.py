"""
Test ML Models with Real Data

Train and evaluate all three models on the extracted features from real users.
"""

import pandas as pd
import numpy as np
from pathlib import Path

from trade_risk_analyzer.models import (
    IsolationForestModel,
    AutoencoderModel,
    RandomForestModel,
    ModelTrainer,
    ModelEnsemble
)


def load_extracted_features():
    """Load previously extracted features"""
    print("=" * 60)
    print("Loading Extracted Features")
    print("=" * 60)
    
    features_path = "extracted_features.csv"
    
    if not Path(features_path).exists():
        print(f"\n✗ Features file not found: {features_path}")
        print("Please run test_real_data.py first to extract features")
        return None
    
    df = pd.read_csv(features_path)
    
    print(f"\n✓ Loaded features for {len(df)} users")
    print(f"  Total features: {len(df.columns) - 1}")
    print(f"  Users: {df['user_id'].tolist()}")
    
    return df


def prepare_training_data(features_df):
    """Prepare data for training"""
    print(f"\n{'=' * 60}")
    print("Preparing Training Data")
    print(f"{'=' * 60}")
    
    # Separate features and user IDs
    user_ids = features_df['user_id'].values
    
    # Get numeric features only
    feature_cols = [col for col in features_df.columns if col != 'user_id']
    X = features_df[feature_cols].values
    
    print(f"\nFeature matrix shape: {X.shape}")
    print(f"Features: {X.shape[1]}")
    print(f"Samples: {X.shape[0]}")
    
    # Since we know these 4 users are anomalies, create labels
    # In real scenario, you'd have labeled data
    # For demonstration: all 4 users are labeled as anomalies (1)
    y = np.ones(len(X), dtype=int)
    
    print(f"\nLabels (all anomalies for this demo): {y}")
    print("\nNote: In production, you would have a mix of normal and anomalous users")
    
    return X, y, user_ids, feature_cols


def test_unsupervised_models(X, user_ids):
    """Test Isolation Forest and Autoencoder (unsupervised)"""
    print(f"\n{'=' * 60}")
    print("Testing Unsupervised Models")
    print(f"{'=' * 60}")
    
    # Test Isolation Forest
    print("\n1. Isolation Forest")
    print("-" * 40)
    
    if_model = IsolationForestModel(
        n_estimators=100,
        contamination=0.5,  # Expect 50% to be anomalies
        random_state=42
    )
    
    print("Training...")
    if_model.train(X)
    
    print("Predicting...")
    predictions = if_model.predict(X)
    scores = if_model.predict_anomaly_score(X)
    probabilities = if_model.predict_proba(X)
    
    print("\nResults:")
    for i, user_id in enumerate(user_ids):
        pred_label = "ANOMALY" if predictions[i] == -1 else "NORMAL"
        print(f"  {user_id}: {pred_label} (score: {scores[i]:.4f}, prob: {probabilities[i]:.4f})")
    
    # Save model
    if_model.save("models/isolation_forest_demo")
    print("\n✓ Model saved to models/isolation_forest_demo")
    
    # Test Autoencoder
    print("\n2. Autoencoder")
    print("-" * 40)
    
    ae_model = AutoencoderModel(
        encoding_dim=16,
        hidden_layers=[32, 24],
        epochs=50,
        batch_size=2,  # Small batch for small dataset
        early_stopping_patience=10,
        random_state=42
    )
    
    print("Training...")
    ae_model.train(X)
    
    print("\nPredicting...")
    predictions = ae_model.predict(X)
    scores = ae_model.calculate_reconstruction_error(X)
    probabilities = ae_model.predict_proba(X)
    
    print("\nResults:")
    print(f"Reconstruction threshold: {ae_model.reconstruction_threshold:.6f}")
    for i, user_id in enumerate(user_ids):
        pred_label = "ANOMALY" if predictions[i] == 1 else "NORMAL"
        print(f"  {user_id}: {pred_label} (error: {scores[i]:.6f}, prob: {probabilities[i]:.4f})")
    
    # Save model
    ae_model.save("models/autoencoder_demo")
    print("\n✓ Model saved to models/autoencoder_demo")
    
    return if_model, ae_model


def test_supervised_model(X, y, user_ids):
    """Test Random Forest (supervised)"""
    print(f"\n{'=' * 60}")
    print("Testing Supervised Model (Random Forest)")
    print(f"{'=' * 60}")
    
    print("\nNote: With only 4 samples (all anomalies), supervised learning is limited.")
    print("In production, you need a balanced dataset with normal and anomalous users.")
    
    # For demo purposes, let's create a synthetic normal user
    print("\nCreating synthetic normal user for demonstration...")
    
    # Create a "normal" user with average features
    X_normal = np.mean(X, axis=0, keepdims=True) * 0.3  # Much lower activity
    X_augmented = np.vstack([X, X_normal])
    y_augmented = np.append(y, 0)  # 0 = normal
    user_ids_augmented = np.append(user_ids, 'synthetic_normal_user')
    
    print(f"Augmented dataset: {X_augmented.shape[0]} samples")
    print(f"Labels: {np.bincount(y_augmented)} (0=normal, 1=anomaly)")
    
    rf_model = RandomForestModel(
        n_estimators=50,
        max_depth=5,
        class_weight='balanced',
        random_state=42
    )
    
    print("\nTraining...")
    rf_model.train(X_augmented, y_augmented)
    
    print("\nPredicting...")
    predictions = rf_model.predict(X_augmented)
    probabilities = rf_model.predict_proba(X_augmented)
    
    print("\nResults:")
    for i, user_id in enumerate(user_ids_augmented):
        pred_label = "ANOMALY" if predictions[i] == 1 else "NORMAL"
        true_label = "ANOMALY" if y_augmented[i] == 1 else "NORMAL"
        prob_anomaly = probabilities[i, 1] if probabilities.shape[1] > 1 else probabilities[i]
        print(f"  {user_id}:")
        print(f"    True: {true_label}, Predicted: {pred_label}")
        print(f"    Anomaly probability: {prob_anomaly:.4f}")
    
    # Feature importance
    print("\nTop 10 Most Important Features:")
    top_features = rf_model.get_top_features(n=10)
    for idx, (feat_idx, importance) in enumerate(top_features, 1):
        print(f"  {idx}. Feature {feat_idx}: {importance:.4f}")
    
    # Save model
    rf_model.save("models/random_forest_demo")
    print("\n✓ Model saved to models/random_forest_demo")
    
    return rf_model


def test_model_trainer(X, y):
    """Test the ModelTrainer orchestrator"""
    print(f"\n{'=' * 60}")
    print("Testing Model Trainer Orchestrator")
    print(f"{'=' * 60}")
    
    print("\nNote: With only 4 samples, train/val/test split is not meaningful.")
    print("This is for demonstration purposes only.")
    
    # Create synthetic data for better demonstration
    print("\nGenerating synthetic dataset for demonstration...")
    
    # Create 20 samples: 10 normal, 10 anomalous
    np.random.seed(42)
    
    # Normal users (lower values)
    X_normal = np.random.randn(10, X.shape[1]) * 0.5
    y_normal = np.zeros(10, dtype=int)
    
    # Anomalous users (higher values, similar to real data)
    X_anomaly = X[:4]  # Use real anomalous users
    # Add 6 more synthetic anomalies
    X_anomaly_synthetic = np.random.randn(6, X.shape[1]) * 2 + 1
    X_anomaly = np.vstack([X_anomaly, X_anomaly_synthetic])
    y_anomaly = np.ones(10, dtype=int)
    
    # Combine
    X_synthetic = np.vstack([X_normal, X_anomaly])
    y_synthetic = np.concatenate([y_normal, y_anomaly])
    
    print(f"Synthetic dataset: {X_synthetic.shape[0]} samples")
    print(f"Class distribution: {np.bincount(y_synthetic)}")
    
    # Initialize trainer
    trainer = ModelTrainer(
        train_split=0.60,
        val_split=0.20,
        test_split=0.20,
        random_state=42
    )
    
    # Train all models
    print("\nTraining all models...")
    models = trainer.train_all_models(
        X_synthetic,
        y_synthetic,
        isolation_forest_params={'contamination': 0.5},
        autoencoder_params={'epochs': 30, 'batch_size': 4},
        random_forest_params={'n_estimators': 50}
    )
    
    print(f"\n✓ Trained {len(models)} models")
    
    # Evaluate all models
    print("\nEvaluating models...")
    results = trainer.evaluate_all_models()
    
    print("\nEvaluation Results:")
    for model_name, metrics in results.items():
        print(f"\n{model_name}:")
        if 'accuracy' in metrics:
            print(f"  Accuracy: {metrics['accuracy']:.4f}")
            print(f"  Precision: {metrics['precision']:.4f}")
            print(f"  Recall: {metrics['recall']:.4f}")
            print(f"  F1-Score: {metrics['f1_score']:.4f}")
        else:
            print(f"  Anomaly ratio: {metrics.get('anomaly_ratio', 0):.4f}")
    
    # Select best model
    if 'random_forest' in results and 'f1_score' in results['random_forest']:
        best_name, best_model = trainer.select_best_model(metric='f1_score')
        print(f"\n✓ Best model: {best_name}")
    
    # Save all models
    trainer.save_models("models/trained_models")
    print("\n✓ All models saved to models/trained_models")
    
    return trainer


def test_ensemble(if_model, ae_model, rf_model, X, user_ids):
    """Test the Model Ensemble"""
    print(f"\n{'=' * 60}")
    print("Testing Model Ensemble")
    print(f"{'=' * 60}")
    
    # Create ensemble
    ensemble = ModelEnsemble(
        weights={
            'isolation_forest': 0.3,
            'autoencoder': 0.4,
            'random_forest': 0.3
        },
        high_risk_threshold=0.8,
        medium_risk_threshold=0.5
    )
    
    # Add models
    ensemble.add_model('isolation_forest', if_model)
    ensemble.add_model('autoencoder', ae_model)
    ensemble.add_model('random_forest', rf_model)
    
    print(f"\n✓ Ensemble created with {len(ensemble.models)} models")
    print(f"  Weights: {ensemble.weights}")
    
    # Get ensemble predictions
    print("\nGenerating ensemble predictions...")
    predictions, scores, risk_levels = ensemble.predict_with_risk_level(X)
    
    print("\nEnsemble Results:")
    for i, user_id in enumerate(user_ids):
        pred_label = "ANOMALY" if predictions[i] == 1 else "NORMAL"
        risk = risk_levels[i].value
        print(f"  {user_id}:")
        print(f"    Prediction: {pred_label}")
        print(f"    Score: {scores[i]:.4f}")
        print(f"    Risk Level: {risk}")
    
    # Get model contributions
    print("\nModel Contributions:")
    contributions = ensemble.get_model_contributions(X)
    for model_name, model_scores in contributions.items():
        print(f"\n  {model_name}:")
        for i, user_id in enumerate(user_ids):
            print(f"    {user_id}: {model_scores[i]:.4f}")
    
    # Explain prediction for first user
    print("\nDetailed Explanation for first user:")
    explanation = ensemble.explain_prediction(X, 0)
    print(f"  User: {user_ids[0]}")
    print(f"  Ensemble Score: {explanation['ensemble_score']:.4f}")
    print(f"  Risk Level: {explanation['risk_level']}")
    print(f"  Model Contributions:")
    for model_name, contrib in explanation['model_contributions'].items():
        print(f"    {model_name}:")
        print(f"      Score: {contrib['score']:.4f}")
        print(f"      Weight: {contrib['weight']:.2f}")
        print(f"      Contribution: {contrib['weighted_contribution']:.4f}")
    
    # Save ensemble config
    ensemble.save_config("models/ensemble_config.json")
    print("\n✓ Ensemble config saved to models/ensemble_config.json")
    
    return ensemble


def main():
    """Main test function"""
    try:
        # Load features
        features_df = load_extracted_features()
        if features_df is None:
            return
        
        # Prepare data
        X, y, user_ids, feature_cols = prepare_training_data(features_df)
        
        # Test unsupervised models
        if_model, ae_model = test_unsupervised_models(X, user_ids)
        
        # Test supervised model
        rf_model = test_supervised_model(X, y, user_ids)
        
        # Test model trainer
        trainer = test_model_trainer(X, y)
        
        # Test ensemble
        ensemble = test_ensemble(if_model, ae_model, rf_model, X, user_ids)
        
        print(f"\n{'=' * 60}")
        print("✓ All ML Model Tests Completed Successfully!")
        print(f"{'=' * 60}")
        
        print("\nSummary:")
        print("  ✓ Isolation Forest trained and tested")
        print("  ✓ Autoencoder trained and tested")
        print("  ✓ Random Forest trained and tested")
        print("  ✓ Model Trainer orchestrator tested")
        print("  ✓ Model Ensemble tested")
        print("\nModels saved to:")
        print("  - models/isolation_forest_demo")
        print("  - models/autoencoder_demo")
        print("  - models/random_forest_demo")
        print("  - models/trained_models/")
        print("  - models/ensemble_config.json")
        
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
