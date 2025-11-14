"""
Simple test for HFT Manipulation Detector
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from trade_risk_analyzer.detection.hft_manipulation import HFTManipulationDetector


def create_hft_manipulation_pattern():
    """Create synthetic trade data with HFT manipulation patterns"""
    trades = []
    base_time = datetime.now() - timedelta(hours=5)
    
    # Normal user trading
    for hour in range(3):
        timestamp = base_time + timedelta(hours=hour)
        for i in range(10):  # 10 trades per hour (normal)
            trades.append({
                'trade_id': f'normal_trade_{len(trades)}',
                'user_id': 'normal_user',
                'timestamp': timestamp + timedelta(minutes=i*6),
                'symbol': 'BTC/USDT',
                'price': 50000 + np.random.normal(0, 100),
                'volume': 1.0 + np.random.normal(0, 0.1),
                'trade_type': 'BUY' if i % 2 == 0 else 'SELL'
            })
    
    # HFT USER 1: Excessive frequency (150 trades in 1 hour)
    hft_time = base_time + timedelta(hours=3)
    for i in range(150):
        trades.append({
            'trade_id': f'hft_freq_{i}',
            'user_id': 'hft_user_1',
            'timestamp': hft_time + timedelta(seconds=i*24),  # Every 24 seconds
            'symbol': 'ETH/USDT',
            'price': 3000 + np.random.normal(0, 10),
            'volume': 0.5 + np.random.normal(0, 0.05),
            'trade_type': 'BUY' if i % 2 == 0 else 'SELL'
        })
    
    # HFT USER 2: Quote stuffing (60 orders in 1 minute)
    quote_time = base_time + timedelta(hours=3, minutes=30)
    for i in range(60):
        trades.append({
            'trade_id': f'quote_stuff_{i}',
            'user_id': 'hft_user_2',
            'timestamp': quote_time + timedelta(seconds=i),  # Every second
            'symbol': 'BTC/USDT',
            'price': 50000 + i * 10,  # Incrementing prices
            'volume': 0.1,
            'trade_type': 'BUY'
        })
    
    # Repeat quote stuffing pattern 3 more times
    for repeat in range(1, 4):
        quote_time_repeat = quote_time + timedelta(minutes=repeat * 5)
        for i in range(60):
            trades.append({
                'trade_id': f'quote_stuff_{repeat}_{i}',
                'user_id': 'hft_user_2',
                'timestamp': quote_time_repeat + timedelta(seconds=i),
                'symbol': 'BTC/USDT',
                'price': 50000 + i * 10,
                'volume': 0.1,
                'trade_type': 'BUY'
            })
    
    # HFT USER 3: Layering (multiple price levels followed by reversals)
    layer_time = base_time + timedelta(hours=4)
    for pattern in range(5):  # 5 layering patterns
        pattern_time = layer_time + timedelta(minutes=pattern * 3)
        
        # Place orders at 5 different price levels
        for level in range(5):
            trades.append({
                'trade_id': f'layer_{pattern}_{level}',
                'user_id': 'hft_user_3',
                'timestamp': pattern_time + timedelta(seconds=level * 10),
                'symbol': 'BTC/USDT',
                'price': 50000 + level * 50,  # Different price levels
                'volume': 1.0,
                'trade_type': 'BUY'
            })
        
        # Then reverse with sells
        reverse_time = pattern_time + timedelta(seconds=60)
        for level in range(3):
            trades.append({
                'trade_id': f'layer_reverse_{pattern}_{level}',
                'user_id': 'hft_user_3',
                'timestamp': reverse_time + timedelta(seconds=level * 5),
                'symbol': 'BTC/USDT',
                'price': 50000 + level * 50,
                'volume': 0.5,
                'trade_type': 'SELL'
            })
    
    # HFT USER 4: Spoofing (rapid placement and cancellation)
    spoof_time = base_time + timedelta(hours=4, minutes=30)
    for pattern in range(10):  # 10 spoofing patterns
        pattern_time = spoof_time + timedelta(seconds=pattern * 30)
        
        # Place buy order
        trades.append({
            'trade_id': f'spoof_buy_{pattern}',
            'user_id': 'hft_user_4',
            'timestamp': pattern_time,
            'symbol': 'ETH/USDT',
            'price': 3000,
            'volume': 5.0,  # Large volume
            'trade_type': 'BUY'
        })
        
        # Cancel (reverse) within 3 seconds
        trades.append({
            'trade_id': f'spoof_cancel_{pattern}',
            'user_id': 'hft_user_4',
            'timestamp': pattern_time + timedelta(seconds=3),
            'symbol': 'ETH/USDT',
            'price': 3000,
            'volume': 5.0,
            'trade_type': 'SELL'
        })
    
    return pd.DataFrame(trades)


def main():
    print("=" * 70)
    print("HFT MANIPULATION DETECTOR TEST")
    print("=" * 70)
    
    # Create test data
    print("\n1. Creating synthetic HFT manipulation patterns...")
    trades_df = create_hft_manipulation_pattern()
    print(f"   ✓ Created {len(trades_df)} trades")
    print(f"   ✓ Symbols: {trades_df['symbol'].unique()}")
    print(f"   ✓ Users: {trades_df['user_id'].nunique()}")
    print(f"   ✓ Date range: {trades_df['timestamp'].min()} to {trades_df['timestamp'].max()}")
    
    # Show user trade counts
    print("\n   User Trade Counts:")
    for user_id in trades_df['user_id'].unique():
        count = len(trades_df[trades_df['user_id'] == user_id])
        print(f"     {user_id}: {count} trades")
    
    # Initialize detector
    print("\n2. Initializing HFT manipulation detector...")
    detector = HFTManipulationDetector(
        trade_frequency_threshold=100,
        frequency_window_hours=1,
        cancellation_ratio_threshold=0.8,
        quote_stuffing_threshold=50,
        quote_stuffing_window_minutes=1,
        layering_price_levels=3,
        layering_time_window_seconds=60,
        spoofing_cancel_time_seconds=5,
        min_pattern_occurrences=3
    )
    print("   ✓ Detector initialized")
    
    # Run detection
    print("\n3. Running HFT manipulation detection...")
    alerts = detector.detect(trades_df)
    print(f"   ✓ Detection complete: {len(alerts)} alerts generated")
    
    # Display results
    if alerts:
        print("\n4. Detection Results:")
        print("-" * 70)
        for i, alert in enumerate(alerts, 1):
            print(f"\nAlert {i}:")
            print(f"  Alert ID: {alert.alert_id}")
            print(f"  Pattern Type: {alert.pattern_type.value}")
            print(f"  Risk Level: {alert.risk_level.value}")
            print(f"  Anomaly Score: {alert.anomaly_score:.2f}")
            print(f"  User: {alert.user_id}")
            print(f"  Trades Involved: {len(alert.trade_ids)}")
            print(f"  Explanation: {alert.explanation}")
            print(f"  Recommended Action: {alert.recommended_action}")
    else:
        print("\n4. No HFT manipulation patterns detected")
    
    # Calculate manipulation scores
    print("\n5. HFT Manipulation Scores by User:")
    print("-" * 70)
    for user_id in trades_df['user_id'].unique():
        score = detector.calculate_hft_manipulation_score(trades_df, user_id)
        print(f"  {user_id}: {score:.4f} ({score*100:.1f}%)")
    
    print("\n" + "=" * 70)
    print("✓ TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
