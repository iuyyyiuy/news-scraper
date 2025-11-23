"""
Train models with labeled data from database
Step 2: Extract features and train models
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json

from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage
from trade_risk_analyzer.feature_engineering import FeatureExtractor
from trade_risk_analyzer.models.isolation_forest import IsolationForestModel
from trade_risk_analyzer.models.random_forest import RandomForestModel
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from trade_risk_analyzer.core.logger import get_logger


logger = get_logger(__name__)


def load_labeled_data(storage, feature_extractor):
    """Load labeled data from database and extract features"""
    logger.info("Loading labeled data from database...")
    
    # Load labels
    labels_file = Path("labeled_users.json")
    
    if not labels_file.exists():
        logger.error("No labeled_users.json found. Run import_luncbtc_data.py first.")
        return None, None
    
    with open(labels_file, 'r') as f:
        labels = json.load(f)
    
    logger.info(f"Found {len(labels)} labeled users")
    
    # Get trade data and extract features for each user
    all_features = []
    all_labels = []
    all_user_ids = []
    
    for label_info in labels:
        user_id = label_info['user_id']
        label = label_info['label']
        
        logger.info(f"\nProcessing user {user_id} ({label})...")
        
        # Get trades from database
        trades_df = storage.get_trades_as_dataframe({'user_id': user_id})
        
        if trades_df.empty:
            logger.warning(f"  No trades found in database for user {user_id}")
            continue
        
        logger.info(f"  Loaded {len(trades_df)} trades")
        
        # Extract features
        try:
            features_df = feature_extractor.extract_features(trades_df)
            
            if features_df.empty:
                logger.warning(f"  No features extracted for user {user_id}")
                continue
            
            logger.info(f"  Extracted {len(features_df)} feature vectors with {len(features_df.columns)-1} features")
            
            # Add label (1 = anomaly for attacker/victim, 0 = normal)
            label_value = 1 if label in ['attacker', 'victim'] else 0
            
            all_features.append(features_df)
            all_labels.extend([label_value] * len(features_df))
            all_user_ids.extend([user_id] * len(features_df))
            
            logger.info(f"  ✓ Added to training set (label: {label_value})")
            
        except Exception as e:
            logger.error(f"  Failed to extract features: {str(e)}")
            continue
    
    if not all_features:
        logger.error("No features extracted from any user")
        return None, None
    
    # Combine all features
    combined_df = pd.concat(all_features, ignore_index=True)
    
    # Prepare features and labels
    feature_cols = [col for col in combined_df.columns if col != 'user_id']
    X = combined_df[feature_cols].values
    y = np.array(all_labels)
    
    logger.info(f"\n{'='*70}")
    logger.info("TRAINING DATA SUMMARY")
    logger.info(f"{'='*70}")
    logger.info(f"Total samples: {len(X)}")
    logger.info(f"Features: {X.shape[1]}")
    logger.info(f"Anomalous (attacker/victim): {(y == 1).sum()}")
    logger.info(f"Normal: {(y == 0).sum()}")
    logger.info(f"{'='*70}\n")
    
    return X, y


def train_models(X, y):
    """Train Isolation Forest and Random Forest models"""
    logger.info("Training models...")
    
    # Create output directory
    output_dir = Path("models_labeled")
    output_dir.mkdir(exist_ok=True)
    
    # Split data
    if len(np.unique(y)) > 1:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
    
    logger.info(f"Train samples: {X_train.shape[0]}")
    logger.info(f"Test samples: {X_test.shape[0]}")
    
    results = {}
    
    # Train Isolation Forest
    logger.info("\n" + "-" * 70)
    logger.info("TRAINING ISOLATION FOREST")
    logger.info("-" * 70)
    
    try:
        if_model = IsolationForestModel(contamination=0.1, n_estimators=100)
        if_model.train(X_train)
        if_model.save(str(output_dir / "isolation_forest"))
        logger.info("✓ Isolation Forest trained and saved")
        results['isolation_forest'] = 'success'
    except Exception as e:
        logger.error(f"✗ Isolation Forest training failed: {e}")
        results['isolation_forest'] = 'failed'
    
    # Train Random Forest
    logger.info("\n" + "-" * 70)
    logger.info("TRAINING RANDOM FOREST")
    logger.info("-" * 70)
    
    try:
        rf_model = RandomForestModel(n_estimators=100, max_depth=10)
        rf_model.train(X_train, y_train)
        rf_model.save(str(output_dir / "random_forest"))
        logger.info("✓ Random Forest trained and saved")
        
        # Evaluate Random Forest
        logger.info("\nEvaluating Random Forest on test set...")
        y_pred = rf_model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        logger.info("\n" + "=" * 70)
        logger.info("RANDOM FOREST EVALUATION RESULTS")
        logger.info("=" * 70)
        logger.info(f"Accuracy:  {accuracy:.4f}")
        logger.info(f"Precision: {precision:.4f}")
        logger.info(f"Recall:    {recall:.4f}")
        logger.info(f"F1-Score:  {f1:.4f}")
        logger.info("=" * 70)
        
        # Detailed classification report
        logger.info("\nClassification Report:")
        report = classification_report(y_test, y_pred, target_names=['Normal', 'Anomaly'])
        logger.info(f"\n{report}")
        
        results['random_forest'] = {
            'status': 'success',
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1)
        }
        
    except Exception as e:
        logger.error(f"✗ Random Forest training failed: {e}")
        import traceback
        traceback.print_exc()
        results['random_forest'] = {'status': 'failed'}
    
    # Save training metadata
    metadata = {
        'models_trained': list(results.keys()),
        'training_samples': int(X_train.shape[0]),
        'test_samples': int(X_test.shape[0]),
        'features': int(X.shape[1]),
        'trained_at': datetime.now().isoformat(),
        'results': results
    }
    
    with open(output_dir / "training_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"\n✓ Training metadata saved to {output_dir}/training_metadata.json")
    
    return results


def main():
    print("=" * 70)
    print("TRAIN MODELS WITH LABELED DATA")
    print("=" * 70)
    print("\nStep 2: Extract features and train models")
    print()
    
    # Initialize components
    db_url = "sqlite:///trade_risk_analyzer.db"
    storage = DatabaseStorage(db_url)
    storage.connect()
    
    feature_extractor = FeatureExtractor()
    
    # Load labeled data
    print("-" * 70)
    print("LOADING LABELED DATA")
    print("-" * 70)
    
    X, y = load_labeled_data(storage, feature_extractor)
    
    if X is None or y is None:
        print("\n✗ Failed to load labeled data")
        storage.disconnect()
        return
    
    print("\n✓ Labeled data loaded successfully")
    
    # Train models
    print("\n" + "-" * 70)
    print("TRAINING MODELS")
    print("-" * 70)
    print("\nTraining Isolation Forest and Random Forest...")
    print("(Skipping Autoencoder to avoid TensorFlow dependency)\n")
    
    try:
        results = train_models(X, y)
        
        print("\n" + "=" * 70)
        print("✓ TRAINING COMPLETE")
        print("=" * 70)
        print(f"\nModels saved to: models_labeled/")
        print(f"\nTrained models:")
        for model_name, result in results.items():
            if isinstance(result, dict):
                status = result.get('status', result)
            else:
                status = result
            print(f"  - {model_name}: {status}")
        
        print(f"\nThe models can now detect extraction attacks similar to")
        print(f"the LUNCBTC case (victim: 1445939, attacker: 4866868)")
        
    except Exception as e:
        print(f"\n✗ Training failed: {e}")
        import traceback
        traceback.print_exc()
    
    storage.disconnect()
    
    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
