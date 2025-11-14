"""
Add Labeled Training Data for Extraction Attack

This script helps add labeled training data from real extraction attack events
to improve model accuracy. It supports labeling both victims and attackers.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import argparse

from trade_risk_analyzer.data_ingestion import TradeDataImporter, TradeDataValidator
from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage
from trade_risk_analyzer.feature_engineering import FeatureExtractor
from trade_risk_analyzer.models.trainer import ModelTrainer
from trade_risk_analyzer.core.logger import get_logger


logger = get_logger(__name__)


class LabeledDataManager:
    """
    Manages labeled training data for supervised learning
    """
    
    def __init__(self, database_url: str = "sqlite:///trade_risk_analyzer.db"):
        """
        Initialize labeled data manager
        
        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url
        self.storage = DatabaseStorage(database_url)
        self.importer = TradeDataImporter()
        self.validator = TradeDataValidator()
        self.feature_extractor = FeatureExtractor()
        self.logger = logger
        
        # Connect to database
        self.storage.connect()
    
    def add_labeled_user(self,
                        file_path: str,
                        user_id: str,
                        label: str,
                        attack_type: str = "extraction_attack",
                        notes: str = "") -> bool:
        """
        Add a labeled user's trade data
        
        Args:
            file_path: Path to Excel file with trade data
            user_id: User ID
            label: Label ('attacker', 'victim', or 'normal')
            attack_type: Type of attack pattern
            notes: Additional notes about this case
            
        Returns:
            Success status
        """
        self.logger.info(f"Adding labeled user: {user_id} (label: {label})")
        
        try:
            # Import trade data
            self.logger.info(f"Importing data from: {file_path}")
            trades_df = self.importer.import_excel(file_path)
            
            if trades_df.empty:
                self.logger.error(f"No data imported from {file_path}")
                return False
            
            # Validate data
            validation_result = self.validator.validate(trades_df)
            
            if not validation_result.is_valid:
                self.logger.warning(f"Validation issues found: {len(validation_result.errors)} errors")
                for error in validation_result.errors[:5]:  # Show first 5 errors
                    self.logger.warning(f"  - {error.field}: {error.message}")
            
            # Ensure user_id is set
            if 'user_id' not in trades_df.columns or trades_df['user_id'].isna().all():
                trades_df['user_id'] = user_id
            
            # Save to database
            self.logger.info(f"Saving {len(trades_df)} trades to database")
            success = self.storage.save_trades_from_dataframe(trades_df)
            
            if not success:
                self.logger.error("Failed to save trades to database")
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
            self._save_label_metadata(label_metadata)
            
            self.logger.info(f"✓ Successfully added labeled user: {user_id}")
            self.logger.info(f"  Label: {label}")
            self.logger.info(f"  Trades: {len(trades_df)}")
            self.logger.info(f"  Attack Type: {attack_type}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add labeled user: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _save_label_metadata(self, metadata: dict) -> None:
        """
        Save label metadata to JSON file
        
        Args:
            metadata: Label metadata dictionary
        """
        import json
        
        labels_file = Path("labeled_users.json")
        
        # Load existing labels
        if labels_file.exists():
            with open(labels_file, 'r') as f:
                labels = json.load(f)
        else:
            labels = []
        
        # Add new label
        labels.append(metadata)
        
        # Save updated labels
        with open(labels_file, 'w') as f:
            json.dump(labels, f, indent=2)
        
        self.logger.info(f"Label metadata saved to {labels_file}")
    
    def get_labeled_data(self) -> pd.DataFrame:
        """
        Get all labeled training data with labels
        
        Returns:
            DataFrame with features and labels
        """
        import json
        
        labels_file = Path("labeled_users.json")
        
        if not labels_file.exists():
            self.logger.warning("No labeled data found")
            return pd.DataFrame()
        
        # Load labels
        with open(labels_file, 'r') as f:
            labels = json.load(f)
        
        self.logger.info(f"Found {len(labels)} labeled users")
        
        # Get trade data for each labeled user
        all_features = []
        all_labels = []
        
        for label_info in labels:
            user_id = label_info['user_id']
            label = label_info['label']
            
            # Get trades from database
            trades_df = self.storage.get_trades_as_dataframe({'user_id': user_id})
            
            if trades_df.empty:
                self.logger.warning(f"No trades found for user {user_id}")
                continue
            
            # Extract features
            features_df = self.feature_extractor.extract_features(trades_df)
            
            if not features_df.empty:
                # Add label
                features_df['label'] = 1 if label in ['attacker', 'victim'] else 0
                features_df['label_type'] = label
                features_df['attack_type'] = label_info.get('attack_type', 'unknown')
                
                all_features.append(features_df)
                
                self.logger.info(f"  {user_id}: {len(features_df)} feature vectors (label: {label})")
        
        if not all_features:
            self.logger.warning("No features extracted from labeled data")
            return pd.DataFrame()
        
        # Combine all features
        combined_df = pd.concat(all_features, ignore_index=True)
        
        self.logger.info(f"Total labeled samples: {len(combined_df)}")
        self.logger.info(f"  Anomalous: {(combined_df['label'] == 1).sum()}")
        self.logger.info(f"  Normal: {(combined_df['label'] == 0).sum()}")
        
        return combined_df
    
    def train_with_labeled_data(self,
                               output_dir: str = "models_labeled",
                               include_unlabeled: bool = True) -> dict:
        """
        Train models with labeled data
        
        Args:
            output_dir: Directory to save trained models
            include_unlabeled: Whether to include unlabeled data for semi-supervised learning
            
        Returns:
            Dictionary of evaluation results
        """
        self.logger.info("Training models with labeled data...")
        
        # Get labeled data
        labeled_df = self.get_labeled_data()
        
        if labeled_df.empty:
            self.logger.error("No labeled data available for training")
            return {}
        
        # Prepare features and labels
        feature_cols = [col for col in labeled_df.columns 
                       if col not in ['user_id', 'label', 'label_type', 'attack_type']]
        
        X = labeled_df[feature_cols].values
        y = labeled_df['label'].values
        
        self.logger.info(f"Training data shape: X={X.shape}, y={y.shape}")
        
        # Initialize trainer
        trainer = ModelTrainer(
            train_split=0.70,
            val_split=0.15,
            test_split=0.15,
            random_state=42
        )
        
        # Train all models
        models = trainer.train_all_models(
            X=X,
            y=y,
            isolation_forest_params={'contamination': 0.1, 'n_estimators': 100},
            autoencoder_params={'encoding_dim': 10, 'epochs': 50},
            random_forest_params={'n_estimators': 100, 'max_depth': 10}
        )
        
        # Evaluate models
        results = trainer.evaluate_all_models()
        
        # Print results
        self.logger.info("\n" + "=" * 70)
        self.logger.info("MODEL EVALUATION RESULTS")
        self.logger.info("=" * 70)
        
        for model_name, metrics in results.items():
            self.logger.info(f"\n{model_name.upper()}:")
            if 'accuracy' in metrics:
                self.logger.info(f"  Accuracy:  {metrics['accuracy']:.4f}")
                self.logger.info(f"  Precision: {metrics['precision']:.4f}")
                self.logger.info(f"  Recall:    {metrics['recall']:.4f}")
                self.logger.info(f"  F1-Score:  {metrics['f1_score']:.4f}")
                if metrics.get('auc_roc'):
                    self.logger.info(f"  AUC-ROC:   {metrics['auc_roc']:.4f}")
        
        # Save models
        trainer.save_models(output_dir)
        self.logger.info(f"\n✓ Models saved to {output_dir}")
        
        return results
    
    def list_labeled_users(self) -> None:
        """
        List all labeled users
        """
        import json
        
        labels_file = Path("labeled_users.json")
        
        if not labels_file.exists():
            print("No labeled users found")
            return
        
        with open(labels_file, 'r') as f:
            labels = json.load(f)
        
        print("\n" + "=" * 70)
        print("LABELED USERS")
        print("=" * 70)
        
        for i, label_info in enumerate(labels, 1):
            print(f"\n{i}. User ID: {label_info['user_id']}")
            print(f"   Label: {label_info['label']}")
            print(f"   Attack Type: {label_info.get('attack_type', 'N/A')}")
            print(f"   Trades: {label_info.get('trade_count', 'N/A')}")
            print(f"   Date Range: {label_info.get('date_range', 'N/A')}")
            print(f"   Added: {label_info.get('added_at', 'N/A')}")
            if label_info.get('notes'):
                print(f"   Notes: {label_info['notes']}")
        
        print("\n" + "=" * 70)
        print(f"Total: {len(labels)} labeled users")
        print("=" * 70)


def main():
    """
    Main function for CLI
    """
    parser = argparse.ArgumentParser(description="Add labeled training data for extraction attacks")
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Add user command
    add_parser = subparsers.add_parser('add', help='Add a labeled user')
    add_parser.add_argument('--file', required=True, help='Path to Excel file with trade data')
    add_parser.add_argument('--user-id', required=True, help='User ID')
    add_parser.add_argument('--label', required=True, choices=['attacker', 'victim', 'normal'],
                           help='Label for this user')
    add_parser.add_argument('--attack-type', default='extraction_attack',
                           help='Type of attack pattern')
    add_parser.add_argument('--notes', default='', help='Additional notes')
    add_parser.add_argument('--db', default='sqlite:///trade_risk_analyzer.db',
                           help='Database URL')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all labeled users')
    list_parser.add_argument('--db', default='sqlite:///trade_risk_analyzer.db',
                            help='Database URL')
    
    # Train command
    train_parser = subparsers.add_parser('train', help='Train models with labeled data')
    train_parser.add_argument('--output-dir', default='models_labeled',
                             help='Output directory for trained models')
    train_parser.add_argument('--db', default='sqlite:///trade_risk_analyzer.db',
                             help='Database URL')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        manager = LabeledDataManager(args.db)
        success = manager.add_labeled_user(
            file_path=args.file,
            user_id=args.user_id,
            label=args.label,
            attack_type=args.attack_type,
            notes=args.notes
        )
        
        if success:
            print(f"\n✓ Successfully added labeled user: {args.user_id}")
        else:
            print(f"\n✗ Failed to add labeled user: {args.user_id}")
    
    elif args.command == 'list':
        manager = LabeledDataManager(args.db)
        manager.list_labeled_users()
    
    elif args.command == 'train':
        manager = LabeledDataManager(args.db)
        results = manager.train_with_labeled_data(output_dir=args.output_dir)
        
        if results:
            print("\n✓ Model training complete!")
        else:
            print("\n✗ Model training failed")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
