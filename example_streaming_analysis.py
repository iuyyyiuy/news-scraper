"""
Example: Real-time Streaming Analysis

Demonstrates how to use the StreamingProcessor for real-time trade analysis.
"""

import pandas as pd
from datetime import datetime, timedelta
import time

from trade_risk_analyzer.detection.engine import DetectionEngine, DetectionConfig
from trade_risk_analyzer.detection.streaming_processor import (
    StreamingProcessor,
    StreamingConfig
)
from trade_risk_analyzer.core.base import Trade, TradeType, Alert
from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage


def create_sample_trade(trade_id: str, user_id: str, 
                       symbol: str = "BTC/USDT",
                       price: float = 50000.0,
                       volume: float = 1.0,
                       trade_type: str = "BUY") -> Trade:
    """Create a sample trade"""
    return Trade(
        trade_id=trade_id,
        user_id=user_id,
        timestamp=datetime.now(),
        symbol=symbol,
        price=price,
        volume=volume,
        trade_type=TradeType.BUY if trade_type == "BUY" else TradeType.SELL,
        order_id=f"order_{trade_id}"
    )


def alert_callback(alert: Alert):
    """Callback function for real-time alerts"""
    print(f"\n🚨 ALERT GENERATED:")
    print(f"   Pattern: {alert.pattern_type.value}")
    print(f"   User: {alert.user_id}")
    print(f"   Risk Level: {alert.risk_level.value}")
    print(f"   Score: {alert.anomaly_score:.1f}")
    print(f"   Explanation: {alert.explanation}")


def example_basic_streaming():
    """Example 1: Basic streaming analysis"""
    print("=" * 60)
    print("Example 1: Basic Streaming Analysis")
    print("=" * 60)
    
    # Create detection engine
    detection_config = DetectionConfig(
        use_ml_models=False,  # Disable ML for faster processing
        use_rule_based=True
    )
    engine = DetectionEngine(config=detection_config)
    
    # Create streaming processor
    streaming_config = StreamingConfig(
        window_size_minutes=1,
        slide_interval_seconds=5,
        min_trades_for_analysis=5,
        enable_redis=False
    )
    
    processor = StreamingProcessor(
        detection_engine=engine,
        config=streaming_config
    )
    
    # Add alert callback
    processor.add_alert_callback(alert_callback)
    
    print("\nSimulating real-time trade stream...")
    print("Adding trades one by one...\n")
    
    # Simulate incoming trades
    for i in range(20):
        trade = create_sample_trade(
            f"trade_{i}",
            "user_suspicious",
            price=50000.0 + (i % 2) * 100,  # Alternating prices
            volume=1.0,
            trade_type="BUY" if i % 2 == 0 else "SELL"
        )
        
        # Process trade
        alerts = processor.process_trade(trade)
        
        print(f"Processed trade {i+1}/20", end="\r")
        time.sleep(0.1)  # Simulate time between trades
    
    print("\n\nForcing final window analysis...")
    result = processor.analyze_current_window(force=True)
    
    # Get statistics
    stats = processor.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"   Trades processed: {stats.trades_processed}")
    print(f"   Windows analyzed: {stats.windows_analyzed}")
    print(f"   Alerts generated: {stats.alerts_generated}")
    print(f"   Current window size: {stats.current_window_size}")
    print(f"   Avg analysis time: {stats.average_analysis_time_ms:.1f}ms")


def example_batch_streaming():
    """Example 2: Batch streaming analysis"""
    print("\n" + "=" * 60)
    print("Example 2: Batch Streaming Analysis")
    print("=" * 60)
    
    # Create detection engine
    detection_config = DetectionConfig(
        use_ml_models=False,
        use_rule_based=True
    )
    engine = DetectionEngine(config=detection_config)
    
    # Create streaming processor
    streaming_config = StreamingConfig(
        window_size_minutes=2,
        batch_size=50,
        min_trades_for_analysis=10,
        enable_redis=False
    )
    
    processor = StreamingProcessor(
        detection_engine=engine,
        config=streaming_config
    )
    
    print("\nProcessing trades in batches...")
    
    # Create batch of trades
    trades = []
    for i in range(100):
        trade = create_sample_trade(
            f"batch_trade_{i}",
            f"user_{i % 5}",  # 5 different users
            price=50000.0 + (i % 10) * 50,
            volume=1.0 + (i % 3) * 0.5
        )
        trades.append(trade)
    
    # Process batch
    result = processor.process_trades_batch(trades)
    
    if result:
        print(f"\n✅ Batch processed successfully")
        print(f"   Total alerts: {len(result.alerts)}")
        
        # Show alerts by risk level
        high_risk = sum(1 for a in result.alerts if a.risk_level.value == "HIGH")
        medium_risk = sum(1 for a in result.alerts if a.risk_level.value == "MEDIUM")
        low_risk = sum(1 for a in result.alerts if a.risk_level.value == "LOW")
        
        print(f"   High risk: {high_risk}")
        print(f"   Medium risk: {medium_risk}")
        print(f"   Low risk: {low_risk}")
    
    # Get statistics
    stats = processor.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"   Trades processed: {stats.trades_processed}")
    print(f"   Windows analyzed: {stats.windows_analyzed}")
    print(f"   Current window size: {stats.current_window_size}")


def example_sliding_window():
    """Example 3: Sliding window behavior"""
    print("\n" + "=" * 60)
    print("Example 3: Sliding Window Behavior")
    print("=" * 60)
    
    from trade_risk_analyzer.detection.streaming_processor import SlidingWindow
    
    # Create sliding window
    window = SlidingWindow(window_size_minutes=1, max_size=100)
    
    print("\nAdding trades over time...")
    
    base_time = datetime.now()
    
    # Add trades at different times
    for i in range(10):
        trade = Trade(
            trade_id=f"window_trade_{i}",
            user_id=f"user_{i % 3}",
            timestamp=base_time + timedelta(seconds=i * 10),
            symbol="BTC/USDT",
            price=50000.0,
            volume=1.0,
            trade_type=TradeType.BUY,
            order_id=f"order_{i}"
        )
        window.add_trade(trade)
    
    print(f"Total trades in window: {window.size()}")
    
    # Get current window
    current_trades = window.get_window_trades()
    print(f"Trades in current window (1 min): {len(current_trades)}")
    
    # Get window at specific time
    past_time = base_time + timedelta(seconds=30)
    past_trades = window.get_window_trades(past_time)
    print(f"Trades in window at 30s mark: {len(past_trades)}")
    
    # Get as DataFrame
    df = window.get_trades_dataframe()
    print(f"\nDataFrame shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    if not df.empty:
        print(f"\nSample data:")
        print(df[['trade_id', 'user_id', 'timestamp', 'price']].head())


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("STREAMING ANALYSIS EXAMPLES")
    print("=" * 60)
    
    try:
        example_basic_streaming()
        example_batch_streaming()
        example_sliding_window()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
