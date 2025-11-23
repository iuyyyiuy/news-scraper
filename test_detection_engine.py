"""
Test script for DetectionEngine
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from trade_risk_analyzer.detection import DetectionEngine, DetectionConfig
from trade_risk_analyzer.detection import RuleBasedThresholds
from trade_risk_analyzer.core.base import RiskLevel


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


def test_detection_engine():
    """Test the DetectionEngine"""
    print("=" * 80)
    print("Testing DetectionEngine")
    print("=" * 80)
    
    # Create test data
    print("\n1. Creating test trade data...")
    trades_df = create_test_trades()
    print(f"   Created {len(trades_df)} test trades")
    print(f"   Unique users: {trades_df['user_id'].nunique()}")
    print(f"   Symbols: {trades_df['symbol'].unique()}")
    
    # Test 1: Rule-based detection only
    print("\n2. Testing rule-based detection only...")
    config_rule_only = DetectionConfig(
        use_feature_extraction=False,
        use_ml_models=False,
        use_rule_based=True
    )
    engine_rule = DetectionEngine(config=config_rule_only)
    result_rule = engine_rule.detect(trades_df)
    
    print(f"   Alerts generated: {len(result_rule.alerts)}")
    print(f"   Risk flags: {len(result_rule.risk_flags)}")
    
    # Show alert breakdown
    pattern_counts = {}
    for alert in result_rule.alerts:
        pattern = alert.pattern_type.value
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
    print(f"   Alerts by pattern: {pattern_counts}")
    
    # Test 2: Feature extraction only (no ML models loaded)
    print("\n3. Testing feature extraction...")
    config_features = DetectionConfig(
        use_feature_extraction=True,
        use_ml_models=False,
        use_rule_based=False
    )
    engine_features = DetectionEngine(config=config_features)
    result_features = engine_features.detect(trades_df)
    
    print(f"   Alerts generated: {len(result_features.alerts)}")
    print(f"   ✓ Feature extraction completed without errors")
    
    # Test 3: Combined detection (rule-based + features, no ML)
    print("\n4. Testing combined detection (rule-based + features)...")
    config_combined = DetectionConfig(
        use_feature_extraction=True,
        use_ml_models=False,
        use_rule_based=True,
        ml_weight=0.5,
        rule_weight=0.5
    )
    engine_combined = DetectionEngine(config=config_combined)
    result_combined = engine_combined.detect(trades_df)
    
    print(f"   Alerts generated: {len(result_combined.alerts)}")
    print(f"   Anomaly scores calculated: {len(result_combined.anomaly_scores)}")
    print(f"   Risk flags assigned: {len(result_combined.risk_flags)}")
    
    # Test 4: Get detection statistics
    print("\n5. Testing detection statistics...")
    stats = engine_combined.get_detection_stats(result_combined)
    print(f"   Total alerts: {stats['total_alerts']}")
    print(f"   Alerts by pattern: {stats['alerts_by_pattern']}")
    print(f"   Alerts by risk level: {stats['alerts_by_risk_level']}")
    if stats['anomaly_score_stats']:
        print(f"   Score stats: mean={stats['anomaly_score_stats']['mean']:.2f}, "
              f"max={stats['anomaly_score_stats']['max']:.2f}")
    
    # Test 5: Update configuration
    print("\n6. Testing configuration update...")
    new_config = DetectionConfig(
        use_rule_based=True,
        rule_based_thresholds=RuleBasedThresholds(
            hft_trade_frequency_threshold=50,
            wash_trading_min_trades=2
        )
    )
    engine_combined.update_config(new_config)
    print("   ✓ Configuration updated")
    
    # Re-run detection with new config
    result_new = engine_combined.detect(trades_df)
    print(f"   Alerts with new config: {len(result_new.alerts)}")
    
    # Test 6: Get current configuration
    print("\n7. Testing get_config()...")
    current_config = engine_combined.get_config()
    print(f"   Use feature extraction: {current_config.use_feature_extraction}")
    print(f"   Use ML models: {current_config.use_ml_models}")
    print(f"   Use rule-based: {current_config.use_rule_based}")
    print(f"   ML weight: {current_config.ml_weight}")
    print(f"   Rule weight: {current_config.rule_weight}")
    
    # Test 7: Display sample alerts
    print("\n8. Sample alerts from combined detection:")
    for i, alert in enumerate(result_combined.alerts[:3], 1):
        print(f"\n   Alert {i}:")
        print(f"   - ID: {alert.alert_id}")
        print(f"   - User: {alert.user_id}")
        print(f"   - Pattern: {alert.pattern_type.value}")
        print(f"   - Risk: {alert.risk_level.value}")
        print(f"   - Score: {alert.anomaly_score:.2f}")
        print(f"   - Explanation: {alert.explanation[:100]}...")
        print(f"   - Trades involved: {len(alert.trade_ids)}")
    
    # Test 8: Test with empty trades
    print("\n9. Testing with empty DataFrame...")
    empty_df = pd.DataFrame()
    result_empty = engine_combined.detect(empty_df)
    print(f"   Alerts: {len(result_empty.alerts)}")
    print(f"   ✓ Handled empty data gracefully")
    
    # Test 9: Test different grouping
    print("\n10. Testing detection grouped by symbol...")
    result_by_symbol = engine_combined.detect(trades_df, group_by='symbol')
    print(f"   Alerts generated: {len(result_by_symbol.alerts)}")
    print(f"   ✓ Symbol-based grouping works")
    
    print("\n" + "=" * 80)
    print("✓ All DetectionEngine tests completed successfully!")
    print("=" * 80)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total trades analyzed: {len(trades_df)}")
    print(f"Unique users: {trades_df['user_id'].nunique()}")
    print(f"Unique symbols: {trades_df['symbol'].nunique()}")
    print(f"\nRule-based only: {len(result_rule.alerts)} alerts")
    print(f"Combined detection: {len(result_combined.alerts)} alerts")
    print(f"\nHigh risk alerts: {sum(1 for a in result_combined.alerts if a.risk_level == RiskLevel.HIGH)}")
    print(f"Medium risk alerts: {sum(1 for a in result_combined.alerts if a.risk_level == RiskLevel.MEDIUM)}")
    print(f"Low risk alerts: {sum(1 for a in result_combined.alerts if a.risk_level == RiskLevel.LOW)}")
    print("=" * 80)


if __name__ == "__main__":
    test_detection_engine()
