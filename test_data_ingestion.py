"""
Simple test script to verify data ingestion module implementation
"""

import pandas as pd
from datetime import datetime
import tempfile
import os

from trade_risk_analyzer.data_ingestion import TradeDataImporter, TradeDataValidator, DatabaseStorage


def test_csv_import():
    """Test CSV import functionality"""
    print("Testing CSV import...")
    
    # Create sample CSV data
    csv_data = """user_id,timestamp,symbol,price,volume,trade_type,order_id
user_001,2024-01-01 10:00:00,BTC/USDT,45000.50,1.5,BUY,order_001
user_002,2024-01-01 10:05:00,ETH/USDT,3000.25,5.0,SELL,order_002
user_003,2024-01-01 10:10:00,BTC/USDT,45100.00,2.0,BUY,order_003
"""
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_data)
        temp_file = f.name
    
    try:
        # Import CSV
        importer = TradeDataImporter()
        df = importer.import_csv(temp_file)
        
        print(f"✓ Successfully imported {len(df)} records from CSV")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Sample data:\n{df.head()}")
        
        return df
    finally:
        os.unlink(temp_file)


def test_json_import():
    """Test JSON import functionality"""
    print("\nTesting JSON import...")
    
    # Create sample JSON data
    json_data = """{
    "trades": [
        {
            "user_id": "user_001",
            "timestamp": "2024-01-01T10:00:00",
            "symbol": "BTC/USDT",
            "price": 45000.50,
            "volume": 1.5,
            "trade_type": "BUY",
            "order_id": "order_001"
        },
        {
            "user_id": "user_002",
            "timestamp": "2024-01-01T10:05:00",
            "symbol": "ETH/USDT",
            "price": 3000.25,
            "volume": 5.0,
            "trade_type": "SELL",
            "order_id": "order_002"
        }
    ]
}"""
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(json_data)
        temp_file = f.name
    
    try:
        # Import JSON
        importer = TradeDataImporter()
        df = importer.import_json(temp_file)
        
        print(f"✓ Successfully imported {len(df)} records from JSON")
        print(f"  Columns: {list(df.columns)}")
        
        return df
    finally:
        os.unlink(temp_file)


def test_validation():
    """Test data validation functionality"""
    print("\nTesting data validation...")
    
    # Create sample data with some invalid records
    data = {
        'user_id': ['user_001', 'user_002', '', 'user_004'],
        'timestamp': [datetime(2024, 1, 1, 10, 0), datetime(2024, 1, 1, 10, 5), 
                     datetime(2024, 1, 1, 10, 10), None],
        'symbol': ['BTC/USDT', 'ETH/USDT', 'BTC/USDT', 'ETH/USDT'],
        'price': [45000.50, 3000.25, -100.0, 2500.0],
        'volume': [1.5, 5.0, 2.0, 0.0],
        'trade_type': ['BUY', 'SELL', 'BUY', 'INVALID']
    }
    df = pd.DataFrame(data)
    
    # Validate
    validator = TradeDataValidator()
    result = validator.validate(df, strict=False)
    
    print(f"✓ Validation complete:")
    print(f"  Valid records: {result.valid_records}")
    print(f"  Invalid records: {result.invalid_records}")
    print(f"  Total errors: {len(result.errors)}")
    print(f"  Total warnings: {len(result.warnings)}")
    
    if result.errors:
        print(f"\n  Sample errors:")
        for error in result.errors[:3]:
            print(f"    - {error.field}: {error.message}")
    
    # Get valid records
    valid_df = validator.get_valid_records(df, result)
    print(f"\n  Valid records extracted: {len(valid_df)}")
    
    return valid_df


def test_database_storage():
    """Test database storage functionality"""
    print("\nTesting database storage...")
    
    # Create in-memory SQLite database
    storage = DatabaseStorage("sqlite:///:memory:")
    storage.connect()
    
    print("✓ Database connected successfully")
    
    # Create sample data
    data = {
        'trade_id': ['trade_001', 'trade_002', 'trade_003'],
        'user_id': ['user_001', 'user_002', 'user_003'],
        'timestamp': [datetime(2024, 1, 1, 10, 0), datetime(2024, 1, 1, 10, 5), 
                     datetime(2024, 1, 1, 10, 10)],
        'symbol': ['BTC/USDT', 'ETH/USDT', 'BTC/USDT'],
        'price': [45000.50, 3000.25, 45100.0],
        'volume': [1.5, 5.0, 2.0],
        'trade_type': ['BUY', 'SELL', 'BUY'],
        'order_id': ['order_001', 'order_002', 'order_003']
    }
    df = pd.DataFrame(data)
    
    # Save to database
    success = storage.save_trades_from_dataframe(df)
    print(f"✓ Saved {len(df)} trades to database: {success}")
    
    # Retrieve trades
    trades = storage.get_trades()
    print(f"✓ Retrieved {len(trades)} trades from database")
    
    # Retrieve as DataFrame
    retrieved_df = storage.get_trades_as_dataframe()
    print(f"✓ Retrieved {len(retrieved_df)} trades as DataFrame")
    
    # Get count
    count = storage.get_trade_count()
    print(f"✓ Total trade count: {count}")
    
    # Filter by user
    user_trades = storage.get_trades({'user_id': 'user_001'})
    print(f"✓ Retrieved {len(user_trades)} trades for user_001")
    
    storage.disconnect()
    print("✓ Database disconnected")
    
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Data Ingestion Module Test Suite")
    print("=" * 60)
    
    try:
        # Test CSV import
        csv_df = test_csv_import()
        
        # Test JSON import
        json_df = test_json_import()
        
        # Test validation
        valid_df = test_validation()
        
        # Test database storage
        test_database_storage()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
