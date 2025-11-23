"""
Test script for RuleBasedDetector orchestrator
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from trade_risk_analyzer.detection import (
    RuleBasedDetector,
    RuleBasedThresholds,
    DetectionStats
)
from trade_risk_analyzer.core.base import PatternType, RiskLevel


def create_test_trades():
    """Create test trade data with various patterns"""
    trades = []
    base_time = datetime.now() - timedelta(days=7)
    
    # Create wash trading pattern (user 1)
    for i in range(5):
        # Buy
        trades.append({
            'trade_id': f'wash_buy_{i}',
            'user_id': 'user_wash_1',
            'timestamp': base_time + timedelta(minutes=i*10),
            'symbol': 'BTC/USDT',
            'price': 50000.0,
            'volume': 1.0,
            'trade_type': 'BUY',
            'order_id': f'order_buy_{i}'
        })
        # Sell at same price shortly after
        trades.append({
            'trade_id': f'wash_sell_{i}',
            'user_id': 'user_wash_1',
            'timestamp': base_time + timedelta(minutes=i*10+2),
            'symbol': 'BTC/USDT',
            'price': 50000.0,
            'volume': 1.0,
            'trade_type': 'SELL',
            'order_id': f'order_sell_{i}'
        })
    
    # Create HFT pattern (user 2) - excessive frequency
    for i in range(150):
        trades.append({
            'trade_id': f'hft_{i}',
            'user_id': 'user_hft_2',
            'timestamp': base_time + timedelta(seconds=i*20),
            'symbol': 'ETH/USDT',
            'price': 3000.0 + np.random.randn() * 10,
            'volume': 0.5,
            'trade_type': 'BUY' if i % 2 == 0 else 'SELL',
            'order_id': f'order_hft_{i}'
        })
    
    # Create pump and dump pattern (multiple users)
    pump_time = base_time + timedelta(days=3)
    
    # Normal volume baseline
    for i in range(20):
        trades.append({
            'trade_id': f'baseline_{i}',
            'user_id': f'user_normal_{i % 5}',
            'timestamp': base_time + timedelta(hours=i),
            'symbol': 'DOGE/USDT',
            'price': 0.10,
            'volume': 100.0,
            'trade_type': 'BUY' if i % 2 == 0 else 'SELL',
            'order_id': f'order_baseline_{i}'
        })
    
    # Pump phase - coordinated buying with volume spike
    for i in range(30):
        trades.append({
            'trade_id': f'pump_{i}',
            'user_id': f'user_pump_{i % 5}',
            'timestamp': pump_time + timedelta(minutes=i*2),
            'symbol': 'DOGE/USDT',
            'price': 0.10 + (i * 0.01),  # Price increases
            'volume': 500.0,  # 5x normal volume
            'trade_type': 'BUY',
            'order_id': f'order_pump_{i}'
        })
    
    # Dump phase - price declines
    dump_time = pump_time + timedelta(hours=12)
    for i in range(20):
        trades.append({
            'trade_id': f'dump_{i}',
            'user_id': f'user_pump_{i % 5}',
            'timestamp': dump_time + timedelta(minutes=i*3),
            'symbol': 'DOGE/USDT',
            'price': 0.40 - (i * 0.015),  # Price declines
            'volume': 400.0,
            'trade_type': 'SELL',
            'order_id': f'order_dump_{i}'
        })
    
    # Add some normal trades
    for i in range(50):
        trades.append({
            'trade_id': f'normal_{i}',
            'user_id': f'user_normal_{i % 10}',
            'timestamp': base_time + timedelta(hours=i, minutes=i*5),
            'symbol': 'BTC/USDT',
            'price': 50000.0 + np.random.randn() * 500,
            'volume': np.random.uniform(0.1, 2.0),
            'trade_type': 'BUY' if np.random.rand() > 0.5 else 'SELL',
            'order_id': f'order_normal_{i}'
        })
    
    return pd.DataFrame(trades)


def test_rule_based_detector():
    """Test the RuleBasedDetector orchestrator"""
    print("=" * 80)
    print("Testing RuleBasedDetector Orchestrator")
    print("=" * 80)
    
    # Create test data
    print("\n1. Creating test trade data...")
    trades_df = create_test_trades()
    print(f"   Created {len(trades_df)} test trades")
    print(f"   Unique users: {trades_df['user_id'].nunique()}")
    print(f"   Symbols: {trades_df['symbol'].unique()}")
    print(f"   Date range: {trades_df['timestamp'].min()} to {trades_df['timestamp'].max()}")
    
    # Initialize detector with default thresholds
    print("\n2. Initializing RuleBasedDetector with default thresholds...")
    detector = RuleBasedDetector()
    print("   ✓ Detector initialized")
    
    # Test detect_all_patterns
    print("\n3. Running detect_all_patterns()...")
    all_alerts = detector.detect_all_patterns(trades_df)
    print(f"   ✓ Generated {len(all_alerts)} total alerts")
    
    # Display alerts by pattern type
    print("\n4. Alerts by pattern type:")
    pattern_counts = {}
    for alert in all_alerts:
        pattern = alert.pattern_type.value
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
    
    for pattern, count in pattern_counts.items():
        print(f"   - {pattern}: {count} alerts")
    
    # Display alerts by risk level
    print("\n5. Alerts by risk level:")
    risk_counts = {}
    for alert in all_alerts:
        risk = alert.risk_level.value
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
    
    for risk, count in risk_counts.items():
        print(f"   - {risk}: {count} alerts")
    
    # Test detection stats
    print("\n6. Getting detection statistics...")
    stats = detector.get_detection_stats(all_alerts, len(trades_df))
    print(f"   Total trades analyzed: {stats.total_trades_analyzed}")
    print(f"   Total alerts generated: {stats.total_alerts_generated}")
    print(f"   Alerts by pattern: {stats.alerts_by_pattern}")
    print(f"   Alerts by risk level: {stats.alerts_by_risk_level}")
    
    # Test detect_by_pattern
    print("\n7. Testing detect_by_pattern()...")
    wash_alerts = detector.detect_by_pattern(trades_df, PatternType.WASH_TRADING)
    print(f"   Wash trading alerts: {len(wash_alerts)}")
    
    hft_alerts = detector.detect_by_pattern(trades_df, PatternType.HFT_MANIPULATION)
    print(f"   HFT manipulation alerts: {len(hft_alerts)}")
    
    pump_alerts = detector.detect_by_pattern(trades_df, PatternType.PUMP_AND_DUMP)
    print(f"   Pump and dump alerts: {len(pump_alerts)}")
    
    # Test unified alert format
    print("\n8. Testing create_unified_alert_format()...")
    unified_alerts = detector.create_unified_alert_format(all_alerts[:3])
    print(f"   ✓ Converted {len(unified_alerts)} alerts to unified format")
    if unified_alerts:
        print(f"   Sample alert keys: {list(unified_alerts[0].keys())}")
    
    # Test alert filtering
    print("\n9. Testing filter_alerts()...")
    high_risk_alerts = detector.filter_alerts(
        all_alerts, 
        min_risk_level=RiskLevel.HIGH
    )
    print(f"   High risk alerts: {len(high_risk_alerts)}")
    
    wash_only = detector.filter_alerts(
        all_alerts,
        pattern_types=[PatternType.WASH_TRADING]
    )
    print(f"   Wash trading only: {len(wash_only)}")
    
    high_score_alerts = detector.filter_alerts(
        all_alerts,
        min_score=70.0
    )
    print(f"   Alerts with score >= 70: {len(high_score_alerts)}")
    
    # Test threshold updates
    print("\n10. Testing update_thresholds()...")
    new_thresholds = RuleBasedThresholds(
        hft_trade_frequency_threshold=50,  # Lower threshold
        wash_trading_min_trades=2
    )
    detector.update_thresholds(new_thresholds)
    print("   ✓ Thresholds updated")
    
    # Re-run detection with new thresholds
    new_alerts = detector.detect_all_patterns(trades_df)
    print(f"   Alerts with new thresholds: {len(new_alerts)}")
    
    # Test get_thresholds
    print("\n11. Testing get_thresholds()...")
    current_thresholds = detector.get_thresholds()
    print(f"   HFT frequency threshold: {current_thresholds.hft_trade_frequency_threshold}")
    print(f"   Wash trading min trades: {current_thresholds.wash_trading_min_trades}")
    
    # Display sample alerts
    print("\n12. Sample alerts:")
    for i, alert in enumerate(all_alerts[:3], 1):
        print(f"\n   Alert {i}:")
        print(f"   - ID: {alert.alert_id}")
        print(f"   - User: {alert.user_id}")
        print(f"   - Pattern: {alert.pattern_type.value}")
        print(f"   - Risk: {alert.risk_level.value}")
        print(f"   - Score: {alert.anomaly_score:.2f}")
        print(f"   - Explanation: {alert.explanation[:100]}...")
        print(f"   - Trades involved: {len(alert.trade_ids)}")
    
    print("\n" + "=" * 80)
    print("✓ All tests completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    test_rule_based_detector()
