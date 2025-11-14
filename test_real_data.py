"""
Test feature engineering with real Excel data from 4 users
"""

import pandas as pd
import numpy as np
from datetime import datetime

from trade_risk_analyzer.data_ingestion import TradeDataImporter, TradeDataValidator
from trade_risk_analyzer.feature_engineering import FeatureExtractor


# File paths for the 4 users
FILE_PATHS = [
    "商務大使09.22/商務大使8286819-上級8241081/UID 8347040.xlsx",
    "商務大使09.22/商務大使8286819-上級8241081/UID 8350885.xlsx",
    "商務大使09.22/商務大使8347984-上級6302548/UID 8354838.xlsx",
    "商務大使09.22/商務大使8347984-上級6302548/UID 8363457.xlsx"
]

USER_IDS = ['user_8347040', 'user_8350885', 'user_8354838', 'user_8363457']

# Column mapping from Chinese to English
COLUMN_MAPPING = {
    '开仓时间': 'open_time',
    '平仓时间': 'close_time',
    '合约': 'symbol',
    '类型': 'position_type',
    '开仓均价': 'open_price',
    '进入价格': 'entry_price',
    '离开价格': 'exit_price',
    '平仓类型': 'close_type',
    '历史最高数量': 'max_quantity',
    '历史最高价值': 'max_value',
    '已实现盈亏': 'realized_pnl',
    '手续费': 'fee',
    '资金费用': 'funding_fee'
}


def transform_to_trade_format(df, user_id):
    """Transform Chinese format data to standard trade format"""
    
    # Rename columns
    df = df.rename(columns=COLUMN_MAPPING)
    
    # Create two trades per position: one for open, one for close
    trades = []
    
    for idx, row in df.iterrows():
        # Opening trade (BUY for long, SELL for short)
        open_trade = {
            'trade_id': f"{user_id}_open_{idx}",
            'user_id': user_id,
            'timestamp': pd.to_datetime(row['open_time']),
            'symbol': row['symbol'],
            'price': float(row['entry_price']),
            'volume': float(row['max_quantity']),
            'trade_type': 'BUY' if row['position_type'] == '多仓' else 'SELL',
            'order_id': f"{user_id}_order_open_{idx}"
        }
        trades.append(open_trade)
        
        # Closing trade (opposite of opening)
        close_trade = {
            'trade_id': f"{user_id}_close_{idx}",
            'user_id': user_id,
            'timestamp': pd.to_datetime(row['close_time']),
            'symbol': row['symbol'],
            'price': float(row['exit_price']),
            'volume': float(row['max_quantity']),
            'trade_type': 'SELL' if row['position_type'] == '多仓' else 'BUY',
            'order_id': f"{user_id}_order_close_{idx}"
        }
        trades.append(close_trade)
    
    return pd.DataFrame(trades)


def load_and_combine_data():
    """Load all Excel files and combine into single DataFrame"""
    print("=" * 60)
    print("Loading Real Trade Data")
    print("=" * 60)
    
    importer = TradeDataImporter()
    validator = TradeDataValidator()
    
    all_trades = []
    
    for file_path, user_id in zip(FILE_PATHS, USER_IDS):
        print(f"\nLoading {file_path}...")
        
        try:
            # Import Excel file
            df = importer.import_excel(file_path)
            
            print(f"  ✓ Loaded {len(df)} position records")
            
            # Transform to trade format
            trades_df = transform_to_trade_format(df, user_id)
            print(f"  ✓ Transformed to {len(trades_df)} trades (open + close)")
            
            # Validate data
            validation_result = validator.validate(trades_df, strict=False)
            print(f"  Validation: {validation_result.valid_records} valid, {validation_result.invalid_records} invalid")
            
            if validation_result.errors:
                print(f"  Sample errors: {[f'{e.field}: {e.message}' for e in validation_result.errors[:3]]}")
            
            # Get valid records only
            if validation_result.valid_records > 0:
                valid_df = validator.get_valid_records(trades_df, validation_result)
                all_trades.append(valid_df)
                print(f"  ✓ Added {len(valid_df)} valid trades for {user_id}")
            
        except Exception as e:
            print(f"  ✗ Error loading {file_path}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    if not all_trades:
        print("\n✗ No valid trades loaded!")
        return None
    
    # Combine all trades
    combined_df = pd.concat(all_trades, ignore_index=True)
    
    print(f"\n{'=' * 60}")
    print(f"Combined Data Summary")
    print(f"{'=' * 60}")
    print(f"Total trades: {len(combined_df)}")
    print(f"Users: {combined_df['user_id'].nunique()}")
    print(f"Symbols: {list(combined_df['symbol'].unique()[:10])}")  # Show first 10
    print(f"Date range: {combined_df['timestamp'].min()} to {combined_df['timestamp'].max()}")
    print(f"Trade types: {combined_df['trade_type'].value_counts().to_dict()}")
    
    return combined_df


def test_feature_extraction(trades_df):
    """Test feature extraction on real data"""
    print(f"\n{'=' * 60}")
    print("Feature Extraction Test")
    print(f"{'=' * 60}")
    
    # Initialize feature extractor
    print("\n1. Initializing feature extractor...")
    extractor = FeatureExtractor(
        time_windows=['1H', '24H', '7D'],
        scaler_type='standard'
    )
    print("   ✓ Initialized")
    
    # Extract features
    print("\n2. Extracting features...")
    try:
        features_df = extractor.extract_features(
            trades_df,
            group_by='user_id',
            include_frequency=True,
            include_volume=True,
            include_temporal=True,
            include_price=True,
            include_behavioral=True
        )
        
        print(f"   ✓ Extracted {len(features_df.columns) - 1} features for {len(features_df)} users")
        
        # Display features
        print(f"\n3. Feature Summary:")
        print(f"   Total features: {len(features_df.columns) - 1}")
        print(f"   Users analyzed: {len(features_df)}")
        
        # Show sample features for each user
        print(f"\n4. Sample Features by User:")
        for idx, row in features_df.iterrows():
            user_id = row['user_id']
            print(f"\n   {user_id}:")
            print(f"     - Total trades: {row.get('total_trades', 0):.0f}")
            print(f"     - Avg trades/day: {row.get('avg_trades_per_day', 0):.2f}")
            print(f"     - Volume mean: {row.get('volume_mean', 0):.4f}")
            print(f"     - Volume std: {row.get('volume_std', 0):.4f}")
            print(f"     - Unique symbols: {row.get('unique_symbols', 0):.0f}")
            print(f"     - Win ratio: {row.get('win_ratio', 0):.2%}")
            print(f"     - Peak hour: {row.get('peak_trading_hour', 0):.0f}")
            print(f"     - Business hours ratio: {row.get('business_hours_ratio', 0):.2%}")
            print(f"     - Quote stuffing detected: {bool(row.get('quote_stuffing_detected', 0))}")
            print(f"     - Trades per hour (1H): {row.get('trades_per_hour_1H', 0):.2f}")
        
        # Normalize and build feature vectors
        print(f"\n5. Building feature vectors...")
        features_df_norm = extractor.normalize_features(features_df, exclude_columns=['user_id'])
        feature_array = extractor.build_feature_vector(features_df_norm, exclude_columns=['user_id'])
        
        print(f"   ✓ Feature array shape: {feature_array.shape}")
        print(f"   ✓ Features per user: {feature_array.shape[1]}")
        
        # Show feature statistics
        print(f"\n6. Feature Statistics (first 5 features):")
        print(f"   Mean: {np.mean(feature_array, axis=0)[:5]}")
        print(f"   Std: {np.std(feature_array, axis=0)[:5]}")
        print(f"   Min: {np.min(feature_array, axis=0)[:5]}")
        print(f"   Max: {np.max(feature_array, axis=0)[:5]}")
        
        return features_df, feature_array
        
    except Exception as e:
        print(f"   ✗ Error during feature extraction: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None


def analyze_user_patterns(trades_df):
    """Analyze specific patterns in the data"""
    print(f"\n{'=' * 60}")
    print("User Pattern Analysis")
    print(f"{'=' * 60}")
    
    for user_id in sorted(trades_df['user_id'].unique()):
        user_trades = trades_df[trades_df['user_id'] == user_id]
        
        print(f"\n{user_id}:")
        print(f"  Total trades: {len(user_trades)}")
        print(f"  Symbols traded: {user_trades['symbol'].nunique()}")
        print(f"  Top 3 symbols: {user_trades['symbol'].value_counts().head(3).to_dict()}")
        print(f"  Buy/Sell ratio: {len(user_trades[user_trades['trade_type']=='BUY'])}/{len(user_trades[user_trades['trade_type']=='SELL'])}")
        print(f"  Avg volume: {user_trades['volume'].mean():.4f}")
        print(f"  Avg price: {user_trades['price'].mean():.2f}")
        
        # Time analysis
        user_trades_sorted = user_trades.sort_values('timestamp')
        time_span = (user_trades_sorted['timestamp'].max() - user_trades_sorted['timestamp'].min()).total_seconds() / 86400
        print(f"  Trading period: {time_span:.1f} days")
        if time_span > 0:
            print(f"  Trades per day: {len(user_trades) / time_span:.2f}")


def main():
    """Main test function"""
    try:
        # Load data
        trades_df = load_and_combine_data()
        
        if trades_df is None or len(trades_df) == 0:
            print("\n✗ No data to process")
            return
        
        # Analyze patterns
        analyze_user_patterns(trades_df)
        
        # Extract features
        features_df, feature_array = test_feature_extraction(trades_df)
        
        if features_df is not None:
            print(f"\n{'=' * 60}")
            print("✓ All tests completed successfully!")
            print(f"{'=' * 60}")
            
            # Save results
            print("\nSaving results...")
            features_df.to_csv('extracted_features.csv', index=False)
            print("  ✓ Saved features to extracted_features.csv")
            
            trades_df.to_csv('combined_trades.csv', index=False)
            print("  ✓ Saved trades to combined_trades.csv")
        
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
