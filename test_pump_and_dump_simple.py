"""
Simple test for Pump-and-Dump Detector
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from trade_risk_analyzer.detection.pump_and_dump import PumpAndDumpDetector


def create_pump_and_dump_pattern():
    """Create synthetic trade data with pump-and-dump pattern"""
    trades = []
    base_time = datetime.now() - timedelta(days=10)
    
    # Normal trading for first 5 days
    for day in range(5):
        for hour in range(24):
            timestamp = base_time + timedelta(days=day, hours=hour)
            for i in range(5):  # 5 trades per hour
                trades.append({
                    'trade_id': f'trade_{len(trades)}',
                    'user_id': f'user_{i % 3}',
                    'timestamp': timestamp + timedelta(minutes=i*10),
                    'symbol': 'BTC/USDT',
                    'price': 50000 + np.random.normal(0, 100),
                    'volume': 1.0 + np.random.normal(0, 0.1),
                    'trade_type': 'BUY' if i % 2 == 0 else 'SELL'
                })
    
    # PUMP PHASE - Day 6: Coordinated buying with volume spike
    pump_day = 5
    base_price = 50000
    for hour in range(12):  # 12-hour pump
        timestamp = base_time + timedelta(days=pump_day, hours=hour)
        # Increased volume and coordinated buying
        for i in range(20):  # 20 trades per hour (4x normal)
            price_increase = (hour / 12) * 0.6  # 60% increase over 12 hours
            trades.append({
                'trade_id': f'trade_{len(trades)}',
                'user_id': f'user_{i % 5}',  # More users involved
                'timestamp': timestamp + timedelta(minutes=i*3),
                'symbol': 'BTC/USDT',
                'price': base_price * (1 + price_increase) + np.random.normal(0, 50),
                'volume': 3.0 + np.random.normal(0, 0.2),  # 3x volume
                'trade_type': 'BUY'  # Mostly buys
            })
    
    # DUMP PHASE - Day 7-8: Rapid price decline
    peak_price = base_price * 1.6
    for day in range(2):
        for hour in range(24):
            timestamp = base_time + timedelta(days=pump_day + 1 + day, hours=hour)
            price_decline = ((day * 24 + hour) / 48) * 0.4  # 40% decline over 2 days
            for i in range(10):
                trades.append({
                    'trade_id': f'trade_{len(trades)}',
                    'user_id': f'user_{i % 4}',
                    'timestamp': timestamp + timedelta(minutes=i*6),
                    'symbol': 'BTC/USDT',
                    'price': peak_price * (1 - price_decline) + np.random.normal(0, 100),
                    'volume': 2.0 + np.random.normal(0, 0.2),
                    'trade_type': 'SELL'  # Mostly sells
                })
    
    # Back to normal - Days 9-10
    for day in range(2):
        for hour in range(24):
            timestamp = base_time + timedelta(days=pump_day + 3 + day, hours=hour)
            for i in range(5):
                trades.append({
                    'trade_id': f'trade_{len(trades)}',
                    'user_id': f'user_{i % 3}',
                    'timestamp': timestamp + timedelta(minutes=i*10),
                    'symbol': 'BTC/USDT',
                    'price': 48000 + np.random.normal(0, 100),
                    'volume': 1.0 + np.random.normal(0, 0.1),
                    'trade_type': 'BUY' if i % 2 == 0 else 'SELL'
                })
    
    return pd.DataFrame(trades)


def main():
    print("=" * 70)
    print("PUMP-AND-DUMP DETECTOR TEST")
    print("=" * 70)
    
    # Create test data
    print("\n1. Creating synthetic pump-and-dump pattern...")
    trades_df = create_pump_and_dump_pattern()
    print(f"   ✓ Created {len(trades_df)} trades")
    print(f"   ✓ Symbols: {trades_df['symbol'].unique()}")
    print(f"   ✓ Users: {trades_df['user_id'].nunique()}")
    print(f"   ✓ Date range: {trades_df['timestamp'].min()} to {trades_df['timestamp'].max()}")
    
    # Initialize detector
    print("\n2. Initializing pump-and-dump detector...")
    detector = PumpAndDumpDetector(
        volume_spike_threshold=3.0,
        price_increase_threshold=0.5,
        price_decline_threshold=0.3,
        lookback_days=7,
        pump_window_hours=24,
        dump_window_hours=48,
        coordinated_accounts_threshold=3,
        coordinated_time_window_minutes=30
    )
    print("   ✓ Detector initialized")
    
    # Run detection
    print("\n3. Running pump-and-dump detection...")
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
            print(f"  User(s): {alert.user_id[:100]}...")  # Truncate if too long
            print(f"  Trades Involved: {len(alert.trade_ids)}")
            print(f"  Explanation: {alert.explanation}")
            print(f"  Recommended Action: {alert.recommended_action}")
    else:
        print("\n4. No pump-and-dump patterns detected")
    
    # Calculate probability scores
    print("\n5. Pump-and-Dump Probability Scores:")
    print("-" * 70)
    for symbol in trades_df['symbol'].unique():
        prob = detector.calculate_pump_and_dump_probability(trades_df, symbol)
        print(f"  {symbol}: {prob:.4f} ({prob*100:.1f}%)")
    
    print("\n" + "=" * 70)
    print("✓ TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
