"""
Test script for feature engineering module
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from trade_risk_analyzer.feature_engineering import FeatureExtractor


def create_sample_trades(num_users=3, trades_per_user=50):
    """Create sample trade data for testing"""
    trades = []
    
    base_time = datetime(2024, 1, 1, 10, 0, 0)
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
    
    for user_idx in range(num_users):
        user_id = f'user_{user_idx:03d}'
        
        for trade_idx in range(trades_per_user):
            # Generate realistic trade data
            timestamp = base_time + timedelta(
                hours=trade_idx * 0.5,
                minutes=np.random.randint(0, 60)
            )
            
            symbol = np.random.choice(symbols, p=[0.5, 0.3, 0.2])
            
            # Price varies by symbol
            if symbol == 'BTC/USDT':
                price = 45000 + np.random.normal(0, 1000)
            elif symbol == 'ETH/USDT':
                price = 3000 + np.random.normal(0, 100)
            else:
                price = 100 + np.random.normal(0, 10)
            
            volume = np.random.lognormal(0, 1)
            trade_type = np.random.choice(['BUY', 'SELL'])
            
            trades.append({
                'trade_id': f'trade_{user_idx}_{trade_idx}',
                'user_id': user_id,
                'timestamp': timestamp,
                'symbol': symbol,
                'price': max(0.01, price),
                'volume': max(0.01, volume),
                'trade_type': trade_type,
                'order_id': f'order_{user_idx}_{trade_idx}'
            })
    
    return pd.DataFrame(trades)


def test_feature_extractor():
    """Test the main feature extractor"""
    print("=" * 60)
    print("Feature Engineering Module Test")
    print("=" * 60)
    
    # Create sample data
    print("\n1. Creating sample trade data...")
    trades_df = create_sample_trades(num_users=3, trades_per_user=50)
    print(f"   Created {len(trades_df)} trades for {trades_df['user_id'].nunique()} users")
    print(f"   Symbols: {trades_df['symbol'].unique().tolist()}")
    print(f"   Time range: {trades_df['timestamp'].min()} to {trades_df['timestamp'].max()}")
    
    # Initialize feature extractor
    print("\n2. Initializing feature extractor...")
    extractor = FeatureExtractor(
        time_windows=['1H', '24H'],
        scaler_type='standard'
    )
    print("   ✓ Feature extractor initialized")
    
    # Extract features
    print("\n3. Extracting features...")
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
    print(f"   Feature columns: {len(features_df.columns)}")
    
    # Display sample features
    print("\n4. Sample features:")
    print(features_df.head())
    
    # Test normalization
    print("\n5. Testing feature normalization...")
    normalized_df = extractor.normalize_features(features_df, exclude_columns=['user_id'])
    print(f"   ✓ Normalized features")
    print(f"   Sample normalized values:\n{normalized_df[['volume_mean', 'trades_count_1H', 'peak_trading_hour']].head()}")
    
    # Build feature vectors
    print("\n6. Building feature vectors...")
    feature_array = extractor.build_feature_vector(normalized_df, exclude_columns=['user_id'])
    print(f"   ✓ Built feature array with shape: {feature_array.shape}")
    print(f"   Sample vector:\n{feature_array[0][:10]}")
    
    # Test extract_and_build
    print("\n7. Testing extract_and_build...")
    features_df2, feature_array2 = extractor.extract_and_build(
        trades_df,
        group_by='user_id',
        normalize=True
    )
    print(f"   ✓ Extracted and built in one call")
    print(f"   Features shape: {features_df2.shape}")
    print(f"   Array shape: {feature_array2.shape}")
    
    # Test individual calculators
    print("\n8. Testing individual calculators...")
    
    # Frequency metrics
    freq_metrics = extractor.frequency_calculator.calculate_trades_per_window(trades_df)
    print(f"   ✓ Frequency metrics: {len(freq_metrics)} users")
    
    # Volume statistics
    vol_stats = extractor.volume_calculator.calculate_basic_statistics(trades_df)
    print(f"   ✓ Volume statistics: {len(vol_stats)} users")
    
    # Temporal patterns
    temporal = extractor.temporal_analyzer.extract_hour_of_day_distribution(trades_df)
    print(f"   ✓ Temporal patterns: {len(temporal)} users")
    
    # Price impact
    price_impact = extractor.price_calculator.calculate_price_deviation(trades_df)
    print(f"   ✓ Price impact: {len(price_impact)} users")
    
    # Behavioral metrics
    behavioral = extractor.behavioral_calculator.calculate_trading_style_indicators(trades_df)
    print(f"   ✓ Behavioral metrics: {len(behavioral)} users")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed successfully!")
    print("=" * 60)
    
    return features_df, feature_array


def test_specific_features():
    """Test specific feature calculations"""
    print("\n" + "=" * 60)
    print("Testing Specific Feature Calculations")
    print("=" * 60)
    
    trades_df = create_sample_trades(num_users=2, trades_per_user=100)
    extractor = FeatureExtractor()
    
    # Test quote stuffing detection
    print("\n1. Quote stuffing detection...")
    quote_stuffing = extractor.frequency_calculator.detect_quote_stuffing(
        trades_df,
        threshold_per_minute=10
    )
    print(f"   Detected quote stuffing: {quote_stuffing['quote_stuffing_detected'].sum()} users")
    print(f"   Max orders per minute: {quote_stuffing['max_orders_per_minute'].max()}")
    
    # Test volume spikes
    print("\n2. Volume spike detection...")
    spikes = extractor.volume_calculator.detect_volume_spikes(
        trades_df,
        spike_threshold=3.0
    )
    print(f"   Total spikes detected: {spikes['spike_count'].sum()}")
    print(f"   Max spike multiplier: {spikes['max_spike_multiplier'].max():.2f}x")
    
    # Test temporal clustering
    print("\n3. Temporal clustering...")
    clustering = extractor.temporal_analyzer.identify_temporal_clustering(
        trades_df,
        cluster_threshold=5
    )
    print(f"   Clusters found: {clustering['num_clusters'].sum()}")
    print(f"   Max cluster size: {clustering['max_cluster_size'].max()}")
    
    # Test win/loss ratio
    print("\n4. Win/loss ratio...")
    win_loss = extractor.behavioral_calculator.calculate_win_loss_ratio(trades_df)
    print(f"   Average win ratio: {win_loss['win_ratio'].mean():.2%}")
    print(f"   Average profit factor: {win_loss['profit_factor'].mean():.2f}")
    
    print("\n✓ Specific feature tests completed")


if __name__ == "__main__":
    try:
        # Run main test
        features_df, feature_array = test_feature_extractor()
        
        # Run specific feature tests
        test_specific_features()
        
        print("\n" + "=" * 60)
        print("All feature engineering tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
