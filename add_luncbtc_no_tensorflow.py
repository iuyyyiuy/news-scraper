"""
Add LUNCBTC extraction attack data without TensorFlow dependency
Uses only Isolation Forest and Random Forest models
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json

from trade_risk_analyzer.data_ingestion import TradeDataImporter, TradeDataValidator
from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage
from trade_risk_analyzer.feature_engineering import FeatureExtractor
from trade_risk_analyzer.models.isolation_forest import IsolationForestModel
from trade_risk_analyzer.models.random_forest import RandomForestModel
from sklearn.model_selection import train_test_split
from trade_risk_analyzer.core.logger import get_logger


logger = get_logger(__name__)


def add_labeled_user(storage, importer, validator, file_path, user_id, label, attack_type, notes):
    """Add a labeled user's trade data"""
    logger.info(f"Adding labeled user: {user_id} (label: {label})")
    
    try:
        # Import trade data
        logger.info(f"Importing data from: {file_path}")
        trades_df = importer.import_excel(file_path)
        
        if trades_df.empty:
            logger.error(f"No data imported from {file_path}")
            return False
        
        # Validate data
        validation_result = validator.validate(trades_df)
        
        if not validation_result.is_valid:
            logger.warning(f"Validation issues found: {len(validation_result.errors)} errors")
        
        # Ensure user_id is set
        if 'user_id' not in trades_df.columns or trades_df['user_id'].isna().all():
            trades_df['user_id'] = user_id
        
        # Save to database
        logger.info(f"Saving {len(trades_df)} trades to database")
        success = storage.save_trades_from_dataframe(trades_df)
        
        if not success:
            logger.error("Failed to save trades to database")
            return False
        
        # Save label metadata
        label_metadata = {
            'user_id': user_id,
            'label': label,
            'attack_type': attack_type,
            'notes': notes,
            'trade_count': len(trades_df),
            'date_range': f"{trades_df['timestamp'].min()} to {trades_df['timestamp'].max()}",
            'added_at': datetime.now().isoformat()
        }
        
        # Save to labels file
        labels_file = Path("labeled_users.json")
        
        if labels_file.exists():
            with open(labels_file, 'r') as f:
                labels = json.load(f)
        else:
            labels = []
        
        labels.append(label_metadata)
        
        with open(labels_file, 'w') as f:
            json.dump(labels, f, indent=2)
        
        logger.info(f"✓ Successfully added labeled user: {user_id}")
        logger.info(f"  Label: {label}")
        logger.info(f"  Trades: {len(trades_df)}")
        logger.info(f"  Attack Type: {attack_type}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to add labeled user: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def train_models_simple(storage, feature_extractor):
    """Train models without TensorFlow (Isolation Forest + Random Forest only)"""
    logger.info("Training models with labeled data...")
    
    # Load labels
    labels_file = Path("labeled_users.json")
    
    if not labels_file.exists():
        logger.error("No labeled data found")
        return {}
    
    with open(labels_file, 'r') as f:
        labels = json.load(f)
    
    logger.info(f"Found {len(labels)} labeled users")
    
    # Get trade data for each labeled user
    all_features = []
    all_labels = []
    
    for label_info in labels:
        user_id = label_info['user_id']
        label = label_info['label']
        
        # Get trades from database
        trades_df = storage.get_trades_as_dataframe({'user_id': user_id})
        
        if trades_df.empty:
            logger.warning(f"No trades found for user {user_id}")
            continue
        
        # Extract features
        features_df = feature_extractor.extract_features(trades_df)
        
        if not features_df.empty:
            # Add label (1 = anomaly, 0 = normal)
            label_value = 1 if label in ['attacker', 'victim'] else 0
            
            all_features.append(features_df)
            all_labels.extend([label_value] * len(features_df))
            
            logger.info(f"  {user_id}: {len(features_df)} feature vectors (label: {label})")
    
    if not all_features:
        logger.error("No features extracted from labeled data")
        return {}
    
    # Combine all features
    combined_df = pd.concat(all_features, ignore_index=True)
    
    # Prepare features and labels
    feature_cols = [col for col in combined_df.columns if col != 'user_id']
    X = combined_df[feature_cols].values
    y = np.array(all_labels)
    
    logger.info(f"Training data shape: X={X.shape}, y={y.shape}")
    logger.info(f"  Anomalous: {(y == 1).sum()}")
    logger.info(f"  Normal: {(y == 0).sum()}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
    )
    
    logger.info(f"Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")
    
    # Train Isolation Forest
    logger.info("\nTraining Isolation Forest...")
    if_model = IsolationForestModel(contamination=0.1, n_estimators=100)
    if_model.train(X_train)
    if_model.save("models_labeled/isolation_forest")
    logger.info("✓ Isolation Forest trained and saved")
    
    # Train Random Forest
    logger.info("\nTraining Random Forest...")
    rf_model = RandomForestModel(n_estimators=100, max_depth=10)
    rf_model.train(X_train, y_train)
    rf_model.save("models_labeled/random_forest")
    logger.info("✓ Random Forest trained and saved")
    
    # Evaluate Random Forest
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    
    y_pred = rf_model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    logger.info("\nRANDOM FOREST EVALUATION:")
    logger.info(f"  Accuracy:  {accuracy:.4f}")
    logger.info(f"  Precision: {precision:.4f}")
    logger.info(f"  Recall:    {recall:.4f}")
    logger.info(f"  F1-Score:  {f1:.4f}")
    
    # Save metadata
    Path("models_labeled").mkdir(exist_ok=True)
    
    metadata = {
        'models_trained': ['isolation_forest', 'random_forest'],
        'training_samples': int(X_train.shape[0]),
        'test_samples': int(X_test.shape[0]),
        'features': int(X.shape[1]),
        'trained_at': datetime.now().isoformat(),
        'random_forest_metrics': {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1)
        }
    }
    
    with open("models_labeled/training_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return metadata


def main():
    print("=" * 70)
    print("ADD LUNCBTC EXTRACTION ATTACK DATA")
    print("=" * 70)
    print("\nThis will add:")
    print("  Victim:   User 1445939 (Extraction_Attack_case1/1445939.xlsx)")
    print("  Attacker: User 4866868 (Extraction_Attack_case1/4866868.xlsx)")
    print("  Symbol:   LUNCBTC")
    print()
    
    # Initialize components
    db_url = "sqlite:///trade_risk_analyzer.db"
    storage = DatabaseStorage(db_url)
    storage.connect()
    
    importer = TradeDataImporter()
    validator = TradeDataValidator()
    feature_extractor = FeatureExtractor()
    
    # Add victim
    print("-" * 70)
    print("Adding Victim Data...")
    print("-" * 70)
    
    victim_success = add_labeled_user(
        storage, importer, validator,
        file_path="Extraction_Attack_case1/1445939.xlsx",
        user_id="1445939",
        label='victim',
        attack_type='extraction_attack',
        notes="Victim of extraction attack on LUNCBTC in spot market"
    )
    
    if not victim_success:
        print("\n✗ Failed to add victim data")
        return
    
    print("\n✓ Victim data added successfully")
    
    # Add attacker
    print("\n" + "-" * 70)
    print("Adding Attacker Data...")
    print("-" * 70)
    
    attacker_success = add_labeled_user(
        storage, importer, validator,
        file_path="Extraction_Attack_case1/4866868.xlsx",
        user_id="4866868",
        label='attacker',
        attack_type='extraction_attack',
        notes="Attacker in extraction attack on LUNCBTC, coordinated trades"
    )
    
    if not attacker_success:
        print("\n✗ Failed to add attacker data")
        return
    
    print("\n✓ Attacker data added successfully")
    
    # Train models
    print("\n" + "=" * 70)
    print("TRAINING MODELS")
    print("=" * 70)
    print("\nTraining Isolation Forest and Random Forest models...")
    print("(Skipping Autoencoder to avoid TensorFlow dependency)\n")
    
    try:
        results = train_models_simple(storage, feature_extractor)
        
        if results:
            print("\n" + "=" * 70)
            print("✓ TRAINING COMPLETE")
            print("=" * 70)
            print(f"\nModels saved to: models_labeled/")
            print(f"Models trained: {', '.join(results['models_trained'])}")
            print(f"\nThe models can now detect extraction attacks similar to")
            print(f"the LUNCBTC case (victim: 1445939, attacker: 4866868)")
        else:
            print("\n✗ Training failed")
    except Exception as e:
        print(f"\n✗ Training error: {e}")
        import traceback
        traceback.print_exc()
    
    storage.disconnect()
    
    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
