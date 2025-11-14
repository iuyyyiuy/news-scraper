"""
Test Batch Processor

Tests batch processing functionality with progress tracking and memory optimization.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from trade_risk_analyzer.detection.engine import DetectionEngine, DetectionConfig
from trade_risk_analyzer.detection.batch_processor import BatchProcessor, BatchProgress
from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage
from trade_risk_analyzer.core.base import TradeType


def generate_test_trades(num_trades: int = 1000, num_users: int = 10) -> pd.DataFrame:
    """Generate test trade data"""
    np.random.seed(42)
    
    trades = []
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(num_trades):
        trade = {
            'trade_id': f'trade_{i}',
            'user_id': f'user_{i % num_users}',
            'timestamp': base_time + timedelta(minutes=i),
            'symbol': np.random.choice(['BTC/USDT', 'ETH/USDT', 'BNB/USDT']),
            'price': np.random.uniform(100, 1000),
            'volume': np.random.uniform(0.1, 10),
            'trade_type': np.random.choice(['BUY', 'SELL']),
            'order_id': f'order_{i}'
        }
        trades.append(trade)
    
    return pd.DataFrame(trades)


def test_batch_processing_sequential():
    """Test sequential batch processing"""
    print("\n=== Testing Sequential Batch Processing ===")
    
    # Generate test data
    trades_df = generate_test_trades(num_trades=500, num_users=5)
    print(f"Generated {len(trades_df)} test trades")
    
    # Create detection engine
    config = DetectionConfig(
        use_ml_models=False,  # Disable ML for faster testing
        use_rule_based=True
    )
    engine = DetectionEngine(config=config)
    
    # Create batch processor
    processor = BatchProcessor(
        detection_engine=engine,
        batch_size=100,
        use_parallel=False
    )
    
    # Track progress updates
    progress_updates = []
    
    def progress_callback(progress: BatchProgress):
        progress_updates.append(progress.to_dict())
        print(f"  Progress: {progress.progress_percentage:.1f}% "
              f"({progress.completed_batches}/{progress.total_batches} batches)")
    
    processor.add_progress_callback(progress_callback)
    
    # Process trades
    results = processor.process_dataframe(
        trades_df,
        group_by='user_id',
        save_alerts=False
    )
    
    print(f"\nResults:")
    print(f"  Total trades: {results['total_trades']}")
    print(f"  Total batches: {results['total_batches']}")
    print(f"  Total alerts: {results['total_alerts']}")
    print(f"  Processing time: {results['processing_time_seconds']:.2f}s")
    print(f"  Trades per second: {results['trades_per_second']:.1f}")
    print(f"  Errors: {results['errors']}")
    
    # Verify results
    assert results['total_trades'] == 500
    assert results['total_batches'] == 5  # 500 / 100
    assert results['errors'] == 0
    assert len(progress_updates) > 0
    
    print("✓ Sequential batch processing test passed")


def test_batch_processing_with_storage():
    """Test batch processing with database storage"""
    print("\n=== Testing Batch Processing with Storage ===")
    
    # Create in-memory database
    db_path = "sqlite:///:memory:"
    storage = DatabaseStorage(db_path)
    storage.connect()
    
    # Generate and save test data
    trades_df = generate_test_trades(num_trades=300, num_users=3)
    storage.save_trades_from_dataframe(trades_df)
    print(f"Saved {len(trades_df)} trades to database")
    
    # Create detection engine with storage
    config = DetectionConfig(
        use_ml_models=False,
        use_rule_based=True
    )
    engine = DetectionEngine(config=config, storage=storage)
    
    # Create batch processor
    processor = BatchProcessor(
        detection_engine=engine,
        storage=storage,
        batch_size=100,
        use_parallel=False
    )
    
    # Process from database
    results = processor.process_from_database(
        group_by='user_id',
        save_alerts=True,
        check_duplicates=True
    )
    
    print(f"\nResults:")
    print(f"  Total trades: {results['total_trades']}")
    print(f"  Total alerts: {results['total_alerts']}")
    print(f"  Alerts saved: {results['alerts_saved']}")
    print(f"  Alerts duplicates: {results['alerts_duplicates']}")
    print(f"  Processing time: {results['processing_time_seconds']:.2f}s")
    
    # Verify alerts were saved
    saved_alerts = storage.get_alerts()
    print(f"  Alerts in database: {len(saved_alerts)}")
    
    assert results['total_trades'] == 300
    assert results['alerts_saved'] > 0
    assert len(saved_alerts) == results['alerts_saved']
    
    print("✓ Batch processing with storage test passed")


def test_batch_processing_date_range():
    """Test batch processing for date range"""
    print("\n=== Testing Batch Processing for Date Range ===")
    
    # Create in-memory database
    db_path = "sqlite:///:memory:"
    storage = DatabaseStorage(db_path)
    storage.connect()
    
    # Generate trades over 10 days
    base_time = datetime.now() - timedelta(days=10)
    trades = []
    
    for day in range(10):
        for i in range(50):
            trade = {
                'trade_id': f'trade_{day}_{i}',
                'user_id': f'user_{i % 5}',
                'timestamp': base_time + timedelta(days=day, hours=i),
                'symbol': 'BTC/USDT',
                'price': 50000 + np.random.uniform(-1000, 1000),
                'volume': np.random.uniform(0.1, 5),
                'trade_type': np.random.choice(['BUY', 'SELL']),
                'order_id': f'order_{day}_{i}'
            }
            trades.append(trade)
    
    trades_df = pd.DataFrame(trades)
    storage.save_trades_from_dataframe(trades_df)
    print(f"Saved {len(trades_df)} trades over 10 days")
    
    # Create detection engine
    config = DetectionConfig(
        use_ml_models=False,
        use_rule_based=True
    )
    engine = DetectionEngine(config=config, storage=storage)
    
    # Create batch processor
    processor = BatchProcessor(
        detection_engine=engine,
        storage=storage,
        batch_size=100
    )
    
    # Process last 5 days only
    start_date = base_time + timedelta(days=5)
    end_date = base_time + timedelta(days=10)
    
    results = processor.process_date_range(
        start_date=start_date,
        end_date=end_date,
        save_alerts=False
    )
    
    print(f"\nResults for date range:")
    print(f"  Total trades: {results['total_trades']}")
    print(f"  Total alerts: {results['total_alerts']}")
    print(f"  Processing time: {results['processing_time_seconds']:.2f}s")
    
    # Should process approximately 250 trades (5 days * 50 trades/day)
    assert 200 <= results['total_trades'] <= 300
    
    print("✓ Batch processing date range test passed")


def test_progress_tracking():
    """Test progress tracking functionality"""
    print("\n=== Testing Progress Tracking ===")
    
    # Generate test data
    trades_df = generate_test_trades(num_trades=400, num_users=4)
    
    # Create detection engine
    config = DetectionConfig(
        use_ml_models=False,
        use_rule_based=True
    )
    engine = DetectionEngine(config=config)
    
    # Create batch processor
    processor = BatchProcessor(
        detection_engine=engine,
        batch_size=100
    )
    
    # Track progress
    progress_snapshots = []
    
    def capture_progress(progress: BatchProgress):
        snapshot = {
            'completed': progress.completed_batches,
            'total': progress.total_batches,
            'percentage': progress.progress_percentage,
            'processed_trades': progress.processed_trades,
            'rate': progress.processing_rate
        }
        progress_snapshots.append(snapshot)
    
    processor.add_progress_callback(capture_progress)
    
    # Process
    results = processor.process_dataframe(trades_df, save_alerts=False)
    
    print(f"\nProgress snapshots captured: {len(progress_snapshots)}")
    
    # Verify progress tracking
    assert len(progress_snapshots) > 0
    assert progress_snapshots[-1]['completed'] == progress_snapshots[-1]['total']
    assert progress_snapshots[-1]['percentage'] == 100.0
    assert progress_snapshots[-1]['processed_trades'] == 400
    
    # Print progress evolution
    print("\nProgress evolution:")
    for i, snapshot in enumerate(progress_snapshots):
        print(f"  Update {i+1}: {snapshot['percentage']:.1f}% "
              f"({snapshot['completed']}/{snapshot['total']} batches, "
              f"{snapshot['processed_trades']} trades, "
              f"{snapshot['rate']:.1f} trades/s)")
    
    print("✓ Progress tracking test passed")


def test_memory_optimization():
    """Test memory optimization with large dataset"""
    print("\n=== Testing Memory Optimization ===")
    
    # Generate larger dataset
    trades_df = generate_test_trades(num_trades=2000, num_users=20)
    print(f"Generated {len(trades_df)} trades")
    
    # Create detection engine
    config = DetectionConfig(
        use_ml_models=False,
        use_rule_based=True
    )
    engine = DetectionEngine(config=config)
    
    # Create batch processor with smaller batch size
    processor = BatchProcessor(
        detection_engine=engine,
        batch_size=200  # Process in smaller chunks
    )
    
    # Process
    results = processor.process_dataframe(trades_df, save_alerts=False)
    
    print(f"\nResults:")
    print(f"  Total trades: {results['total_trades']}")
    print(f"  Total batches: {results['total_batches']}")
    print(f"  Total alerts: {results['total_alerts']}")
    print(f"  Processing time: {results['processing_time_seconds']:.2f}s")
    print(f"  Trades per second: {results['trades_per_second']:.1f}")
    
    # Verify all trades were processed
    assert results['total_trades'] == 2000
    assert results['total_batches'] == 10  # 2000 / 200
    assert results['errors'] == 0
    
    print("✓ Memory optimization test passed")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Batch Processor Test Suite")
    print("=" * 60)
    
    try:
        test_batch_processing_sequential()
        test_batch_processing_with_storage()
        test_batch_processing_date_range()
        test_progress_tracking()
        test_memory_optimization()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {str(e)}")
        raise
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
