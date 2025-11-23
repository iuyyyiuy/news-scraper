"""
Import LUNCBTC extraction attack data to database
Step 1: Import and clean data, save to database
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

from trade_risk_analyzer.data_ingestion import TradeDataImporter, TradeDataValidator
from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage
from trade_risk_analyzer.core.logger import get_logger


logger = get_logger(__name__)


def clean_trade_data(df):
    """Clean trade data to handle missing values"""
    logger.info(f"Cleaning {len(df)} trade records...")
    
    # Fill missing prices with forward fill, then backward fill
    if 'price' in df.columns:
        df['price'] = df['price'].fillna(method='ffill').fillna(method='bfill')
        # If still NaN, use median
        if df['price'].isna().any():
            median_price = df['price'].median()
            df['price'] = df['price'].fillna(median_price)
    
    # Fill missing volumes with median
    if 'volume' in df.columns:
        df['volume'] = df['volume'].fillna(df['volume'].median())
        # If still NaN, use 0
        df['volume'] = df['volume'].fillna(0)
    
    # Remove rows with critical missing data
    before_count = len(df)
    df = df.dropna(subset=['timestamp', 'symbol'])
    after_count = len(df)
    
    if before_count != after_count:
        logger.warning(f"Removed {before_count - after_count} rows with missing critical data")
    
    # Ensure trade_type is valid
    if 'trade_type' in df.columns:
        df['trade_type'] = df['trade_type'].fillna('BUY')
        df['trade_type'] = df['trade_type'].str.upper()
        df.loc[~df['trade_type'].isin(['BUY', 'SELL']), 'trade_type'] = 'BUY'
    
    logger.info(f"Cleaned data: {len(df)} records remaining")
    
    return df


def import_user_data(storage, importer, file_path, user_id, label, attack_type, notes):
    """Import a user's trade data to database"""
    logger.info(f"\nImporting {label} data: {user_id}")
    logger.info(f"File: {file_path}")
    
    try:
        # Import trade data
        trades_df = importer.import_excel(file_path)
        
        if trades_df.empty:
            logger.error(f"No data imported from {file_path}")
            return False
        
        logger.info(f"Imported {len(trades_df)} records")
        
        # Clean data
        trades_df = clean_trade_data(trades_df)
        
        if trades_df.empty:
            logger.error("No valid data after cleaning")
            return False
        
        # Set user_id
        trades_df['user_id'] = user_id
        
        # Save to database
        logger.info(f"Saving to database...")
        success = storage.save_trades_from_dataframe(trades_df)
        
        if not success:
            logger.error("Failed to save to database")
            return False
        
        logger.info(f"✓ Successfully saved {len(trades_df)} trades for user {user_id}")
        
        # Save label metadata
        import json
        
        label_metadata = {
            'user_id': user_id,
            'label': label,
            'attack_type': attack_type,
            'notes': notes,
            'trade_count': len(trades_df),
            'symbols': trades_df['symbol'].unique().tolist(),
            'date_range': f"{trades_df['timestamp'].min()} to {trades_df['timestamp'].max()}",
            'added_at': datetime.now().isoformat()
        }
        
        labels_file = Path("labeled_users.json")
        
        if labels_file.exists():
            with open(labels_file, 'r') as f:
                labels = json.load(f)
        else:
            labels = []
        
        # Check if user already exists
        existing_idx = None
        for i, existing in enumerate(labels):
            if existing['user_id'] == user_id:
                existing_idx = i
                break
        
        if existing_idx is not None:
            logger.info(f"Updating existing label for user {user_id}")
            labels[existing_idx] = label_metadata
        else:
            labels.append(label_metadata)
        
        with open(labels_file, 'w') as f:
            json.dump(labels, f, indent=2)
        
        logger.info(f"✓ Label metadata saved")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to import user data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 70)
    print("IMPORT LUNCBTC EXTRACTION ATTACK DATA")
    print("=" * 70)
    print("\nStep 1: Import data to database")
    print("\nThis will import:")
    print("  Victim:   User 1445939 (Extraction_Attack_case1/1445939.xlsx)")
    print("  Attacker: User 4866868 (Extraction_Attack_case1/4866868.xlsx)")
    print("  Symbol:   LUNCBTC")
    print()
    
    # Initialize components
    db_url = "sqlite:///trade_risk_analyzer.db"
    storage = DatabaseStorage(db_url)
    storage.connect()
    
    importer = TradeDataImporter()
    
    # Import victim data
    print("-" * 70)
    print("IMPORTING VICTIM DATA")
    print("-" * 70)
    
    victim_success = import_user_data(
        storage, importer,
        file_path="Extraction_Attack_case1/1445939.xlsx",
        user_id="1445939",
        label='victim',
        attack_type='extraction_attack',
        notes="Victim of extraction attack on LUNCBTC in spot market"
    )
    
    if not victim_success:
        print("\n✗ Failed to import victim data")
        storage.disconnect()
        return
    
    print("\n✓ Victim data imported successfully")
    
    # Import attacker data
    print("\n" + "-" * 70)
    print("IMPORTING ATTACKER DATA")
    print("-" * 70)
    
    attacker_success = import_user_data(
        storage, importer,
        file_path="Extraction_Attack_case1/4866868.xlsx",
        user_id="4866868",
        label='attacker',
        attack_type='extraction_attack',
        notes="Attacker in extraction attack on LUNCBTC, coordinated trades"
    )
    
    if not attacker_success:
        print("\n✗ Failed to import attacker data")
        storage.disconnect()
        return
    
    print("\n✓ Attacker data imported successfully")
    
    # Verify data in database
    print("\n" + "-" * 70)
    print("VERIFYING DATA IN DATABASE")
    print("-" * 70)
    
    victim_trades = storage.get_trades_as_dataframe({'user_id': '1445939'})
    attacker_trades = storage.get_trades_as_dataframe({'user_id': '4866868'})
    
    print(f"\nVictim (1445939): {len(victim_trades)} trades in database")
    if not victim_trades.empty:
        print(f"  Symbols: {victim_trades['symbol'].unique()}")
        print(f"  Date range: {victim_trades['timestamp'].min()} to {victim_trades['timestamp'].max()}")
    
    print(f"\nAttacker (4866868): {len(attacker_trades)} trades in database")
    if not attacker_trades.empty:
        print(f"  Symbols: {attacker_trades['symbol'].unique()}")
        print(f"  Date range: {attacker_trades['timestamp'].min()} to {attacker_trades['timestamp'].max()}")
    
    storage.disconnect()
    
    print("\n" + "=" * 70)
    print("✓ DATA IMPORT COMPLETE")
    print("=" * 70)
    print("\nNext step: Train models with this data")
    print("Run: python train_with_labeled_data.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
