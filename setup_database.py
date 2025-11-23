"""
Database Setup Script

This script creates a SQLite database and loads all user trade data from Excel files.
Run this once to set up your database.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
from trade_risk_analyzer.data_ingestion import TradeDataImporter, TradeDataValidator


def create_database(db_path='trade_data.db'):
    """Create database with proper schema"""
    print("=" * 80)
    print("CREATING DATABASE SCHEMA")
    print("=" * 80)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            first_seen TIMESTAMP,
            last_seen TIMESTAMP,
            total_trades INTEGER,
            data_source TEXT,
            notes TEXT
        )
    ''')
    
    # Create trades table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            trade_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            symbol TEXT NOT NULL,
            price REAL NOT NULL,
            volume REAL NOT NULL,
            trade_type TEXT NOT NULL,
            order_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Create indexes for faster queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_user_id ON trades(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_user_timestamp ON trades(user_id, timestamp)')
    
    # Create analysis results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            analysis_date TIMESTAMP NOT NULL,
            anomaly_score REAL,
            is_anomaly BOOLEAN,
            trades_per_day REAL,
            win_ratio REAL,
            risk_level TEXT,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    conn.commit()
    print("✓ Database schema created successfully")
    print(f"✓ Database location: {db_path}")
    
    return conn


def load_excel_files_to_db(conn, directories=['商務大使09.22', '商務大使09.28']):
    """Load all Excel files into the database"""
    print("\n" + "=" * 80)
    print("LOADING EXCEL FILES INTO DATABASE")
    print("=" * 80)
    
    cursor = conn.cursor()
    importer = TradeDataImporter()
    validator = TradeDataValidator()
    
    column_mapping = {
        '开仓时间': 'open_time',
        '平仓时间': 'close_time',
        '合约': 'symbol',
        '类型': 'position_type',
        '开仓均价': 'open_price',
        '进入价格': 'entry_price',
        '离开价格': 'exit_price',
        '历史最高数量': 'max_quantity'
    }
    
    # Find all Excel files
    all_files = []
    for directory in directories:
        if Path(directory).exists():
            files = list(Path(directory).rglob("*.xlsx"))
            all_files.extend(files)
    
    print(f"\nFound {len(all_files)} Excel files")
    
    total_trades_loaded = 0
    users_loaded = 0
    
    for i, file_path in enumerate(all_files, 1):
        filename = Path(file_path).stem
        if not filename.startswith("UID "):
            continue
        
        user_id = f"user_{filename.split()[1]}"
        print(f"\n[{i}/{len(all_files)}] Processing {user_id}...")
        
        try:
            # Load Excel file
            df = importer.import_excel(str(file_path))
            df = df.rename(columns=column_mapping)
            
            # Transform to trade format
            trades = []
            for idx, row in df.iterrows():
                # Opening trade
                trades.append({
                    'trade_id': f"{user_id}_open_{idx}",
                    'user_id': user_id,
                    'timestamp': pd.to_datetime(row['open_time']),
                    'symbol': row['symbol'],
                    'price': float(row['entry_price']),
                    'volume': float(row['max_quantity']),
                    'trade_type': 'BUY' if row['position_type'] == '多仓' else 'SELL',
                    'order_id': f"{user_id}_order_open_{idx}"
                })
                
                # Closing trade
                trades.append({
                    'trade_id': f"{user_id}_close_{idx}",
                    'user_id': user_id,
                    'timestamp': pd.to_datetime(row['close_time']),
                    'symbol': row['symbol'],
                    'price': float(row['exit_price']),
                    'volume': float(row['max_quantity']),
                    'trade_type': 'SELL' if row['position_type'] == '多仓' else 'BUY',
                    'order_id': f"{user_id}_order_close_{idx}"
                })
            
            trades_df = pd.DataFrame(trades)
            
            # Validate
            result = validator.validate(trades_df, strict=False)
            
            if result.valid_records > 0:
                valid_df = validator.get_valid_records(trades_df, result)
                
                # Insert user record
                first_seen = str(valid_df['timestamp'].min())
                last_seen = str(valid_df['timestamp'].max())
                total_trades = len(valid_df)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO users (user_id, first_seen, last_seen, total_trades, data_source)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, first_seen, last_seen, total_trades, str(file_path)))
                
                # Insert trades
                for _, trade in valid_df.iterrows():
                    cursor.execute('''
                        INSERT OR REPLACE INTO trades 
                        (trade_id, user_id, timestamp, symbol, price, volume, trade_type, order_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        trade['trade_id'],
                        trade['user_id'],
                        str(trade['timestamp']),
                        trade['symbol'],
                        float(trade['price']),
                        float(trade['volume']),
                        trade['trade_type'],
                        trade['order_id']
                    ))
                
                conn.commit()
                total_trades_loaded += total_trades
                users_loaded += 1
                
                time_span = (last_seen - first_seen).total_seconds() / 86400
                print(f"  ✓ Loaded {total_trades} trades ({time_span:.1f} days)")
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
    
    print(f"\n{'=' * 80}")
    print("DATABASE LOADING COMPLETE")
    print(f"{'=' * 80}")
    print(f"Users loaded: {users_loaded}")
    print(f"Total trades loaded: {total_trades_loaded:,}")
    
    return users_loaded, total_trades_loaded


def verify_database(conn):
    """Verify database contents"""
    print("\n" + "=" * 80)
    print("VERIFYING DATABASE")
    print("=" * 80)
    
    cursor = conn.cursor()
    
    # Count users
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"\nTotal users: {user_count}")
    
    # Count trades
    cursor.execute("SELECT COUNT(*) FROM trades")
    trade_count = cursor.fetchone()[0]
    print(f"Total trades: {trade_count:,}")
    
    # Date range
    cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM trades")
    min_date, max_date = cursor.fetchone()
    print(f"Date range: {min_date} to {max_date}")
    
    # Symbols
    cursor.execute("SELECT DISTINCT symbol FROM trades")
    symbols = [row[0] for row in cursor.fetchall()]
    print(f"Symbols: {', '.join(symbols)}")
    
    # Top 5 most active users
    print("\nTop 5 Most Active Users:")
    cursor.execute('''
        SELECT user_id, total_trades, 
               ROUND((julianday(last_seen) - julianday(first_seen)), 2) as days,
               ROUND(total_trades / (julianday(last_seen) - julianday(first_seen) + 0.01), 2) as trades_per_day
        FROM users
        ORDER BY trades_per_day DESC
        LIMIT 5
    ''')
    
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} trades, {row[2]} days, {row[3]} trades/day")
    
    print(f"\n{'=' * 80}")
    print("✓ Database verification complete")
    print(f"{'=' * 80}")


def main():
    """Main setup function"""
    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + "DATABASE SETUP".center(78) + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    
    # Create database
    conn = create_database('trade_data.db')
    
    # Load data
    users_loaded, trades_loaded = load_excel_files_to_db(conn)
    
    # Verify
    verify_database(conn)
    
    conn.close()
    
    print("\n✓ Setup complete! You can now use 'trade_data.db' for analysis.")
    print("\nNext steps:")
    print("  1. Run: python analyze_from_database.py")
    print("  2. Query the database using SQL or Python")


if __name__ == "__main__":
    main()
