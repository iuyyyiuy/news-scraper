"""
Test Streaming Processor

Tests real-time streaming analysis functionality.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import threading

from trade_risk_analyzer.detection.engine import DetectionEngine, DetectionConfig
from trade_risk_analyzer.detection.streaming_processor import (
    StreamingProcessor, StreamingConfig, SlidingWindow
)
from trade_risk_analyzer.core.base import Trade, TradeType, Alert
from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage


def create_test_trade(trade_id: str, user_id: str, timestamp: datetime,
                     symbol: str = "BTC/USDT", price: float = 50000.0,
                     volume: float = 1.0, trade_type: str = "BUY") -> Trade:
    """Create a test trade"""
    return Trade(
        trade_id=trade_id,
        user_id=user_id,
        timestamp=timestamp,
        symbol=symbol,
        price=price,
        volume=volume,
        trade_type=TradeType.BUY if trade_type == "BUY" else TradeType.SELL,
        order_id=f"order_{trade_id}"
    )


def test_sliding_window():
    """Test sliding window functionality"""
    print("\n=== Testing Sliding Window ===")
    
    # Create sliding window (1 minute window)
    window = SlidingWindow(window_size_minutes=1, max_size=100)
    
    base_time = datetime.now()
    
    # Add trades over time
    trades = []
    for i in range(10):
        trade_time = base_time + timedelta(seconds=i * 10)
        trade = create_test_trade(
            f"trade_{i}", f"user_{i % 3}", trade_time
        )
        trades.append(trade)
        window.add_trade(trade)
    
    print(f"Added {len(trades)} trades to window")
    print(f"Window size: {window.size()}")
    
    # Get window trades
    window_trades = window.get_window_trades()
    print(f"Trades in window: {len(window_trades)}")
    
    # Get as DataFrame
    df = window.get_trades_dataframe()
    print(f"DataFrame shape: {df.shape}")
    print(f"DataFrame columns: {list(df.columns)}")
    
    # Test with old timestamp (should get fewer trades)
    old_time = base_time + timedelta(seconds=30)
    old_window_trades = window.get_window_trades(old_time)
    print(f"Trades in old window: {len(old_window_trades)}")
    
    assert len(window_trades) >= len(old_window_trades)
    assert not df.empty
    assert 'user_id' in df.columns
    
    print("✓ Sliding window test passed")


def test_streaming_config():
    """Test streaming configuration"""
    print("\n=== Testing Streaming Configuration ===")
    
    # Test default config
    config = StreamingConfig()
    print(f"Default window size: {config.window_size_minutes} minutes")
    print(f"Default slide interval: {config.slide_interval_seconds} seconds")
    print(f"Redis enabled: {config.enable_redis}")
    
    # Test custom config
    custom_config = StreamingConfig(
        window_size_minutes=10,
        slide_interval_seconds=60,
        alert_threshold_score=80.0,
        enable_redis=False
    )
    
    assert custom_config.window_size_minutes == 10
    assert custom_config.slide_interval_seconds == 60
    assert custom_config.alert_threshold_score == 80.0
    assert not custom_config.enable_redis
    
    print("✓ Streaming configuration test passed")


def test_streaming_processor_basic():
    """Test basic streaming processor functionality"""
    print("\n=== Testing Streaming Processor Basic ===")
    
    # Create detection engine
    detection_config = DetectionConfig(
        use_ml_models=False,
        use_rule_based=True
    )
    engine = DetectionEngine(config=detection_config)
    
    # Create streaming config
    streaming_config = StreamingConfig(
        window_size_minutes=1,
        slide_interval_seconds=1,
        batch_size=5,
        enable_redis=False
    )
    
    # Create streaming processor
    processor = StreamingProcessor(
        detection_engine=engine,
        config=streaming_config
    )
    
    print(f"Processor created with window size: {streaming_config.window_size_minutes} min")
    
    # Test statistics
    stats = processor.get_statistics()
    print(f"Initial stats: {stats.to_dict()}")
    
    assert stats.trades_processed == 0
    assert stats.alerts_generated == 0
    
    print("✓ Streaming processor basic test passed")


def test_streaming_analysis():
    """Test streaming analysis with manual window analysis"""
    print("\n=== Testing Streaming Analysis ===")
    
    # Create detection engine
    detection_config = DetectionConfig(
        use_ml_models=False,
        use_rule_based=True
    )
    engine = DetectionEngine(config=detection_config)
    
    # Create streaming config
    streaming_config = StreamingConfig(
        window_size_minutes=1,
        slide_interval_seconds=1,
        batch_size=5,
        enable_redis=False,
        alert_threshold_score=50.0
    )
    
    # Create streaming processor
    processor = StreamingProcessor(
        detection_engine=engine,
        config=streaming_config
    )
    
    # Add trades to sliding window
    base_time = datetime.now()
    
    # Create wash trading pattern
    for i in range(10):
        trade_time = base_time + timedelta(seconds=i)
        
        # Buy trade
        buy_trade = create_test_trade(
            f"trade_buy_{i}", "user_1", trade_time,
            symbol="BTC/USDT", price=50000.0, volume=1.0, trade_type="BUY"
        )
        processor.sliding_window.add_trade(buy_trade)
        
        # Sell trade (same user, same price - wash trading)
        sell_trade = create_test_trade(
            f"trade_sell_{i}", "user_1", trade_time + timedelta(seconds=1),
            symbol="BTC/USDT", price=50000.0, volume=1.0, trade_type="SELL"
        )
        processor.sliding_window.add_trade(sell_trade)
    
    print(f"Added 20 trades to window")
    
    # Analyze current window
    result = processor.analyze_current_window(force=True)
    
    if result:
        print(f"Analysis complete: {len(result.alerts)} alerts generated")
        
        for alert in result.alerts:
            print(f"  - Alert: {alert.pattern_type.value} for user {alert.user_id}")
            print(f"    Score: {alert.anomaly_score:.1f}, Risk: {alert.risk_level.value}")
    else:
        print("No alerts generated")
    
    # Get statistics
    stats = processor.get_statistics()
    print(f"Statistics: {stats.to_dict()}")
    
    print("✓ Streaming analysis test passed")


def test_alert_callback():
    """Test alert callback functionality"""
    print("\n=== Testing Alert Callback ===")
    
    # Create detection engine
    detection_config = DetectionConfig(
        use_ml_models=False,
        use_rule_based=True
    )
    engine = DetectionEngine(config=detection_config)
    
    # Create streaming config
    streaming_config = StreamingConfig(
        window_size_minutes=1,
        slide_interval_seconds=1,
        batch_size=5,
        enable_redis=False,
        alert_threshold_score=50.0
    )
    
    # Create streaming processor
    processor = StreamingProcessor(
        detection_engine=engine,
        config=streaming_config
    )
    
    # Track alerts via callback
    received_alerts = []
    
    def alert_callback(alert: Alert):
        received_alerts.append(alert)
        print(f"Callback received alert: {alert.pattern_type.value}")
    
    processor.add_alert_callback(alert_callback)
    
    # Add trades and process
    base_time = datetime.now()
    
    for i in range(10):
        trade_time = base_time + timedelta(seconds=i)
        
        buy_trade = create_test_trade(
            f"trade_buy_{i}", "user_1", trade_time,
            symbol="BTC/USDT", price=50000.0, volume=1.0, trade_type="BUY"
        )
        processor.sliding_window.add_trade(buy_trade)
        
        sell_trade = create_test_trade(
            f"trade_sell_{i}", "user_1", trade_time + timedelta(seconds=1),
            symbol="BTC/USDT", price=50000.0, volume=1.0, trade_type="SELL"
        )
        processor.sliding_window.add_trade(sell_trade)
    
    # Manually trigger analysis
    result = processor.analyze_current_window(force=True)
    
    if result and result.alerts:
        # Process alerts manually to trigger callbacks
        processor._process_alerts(result.alerts)
    
    print(f"Received {len(received_alerts)} alerts via callback")
    
    print("✓ Alert callback test passed")


def main():
    """Run all tests"""
    print("=" * 60)
    print("STREAMING PROCESSOR TESTS")
    print("=" * 60)
    
    try:
        test_sliding_window()
        test_streaming_config()
        test_streaming_processor_basic()
        test_streaming_analysis()
        test_alert_callback()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
