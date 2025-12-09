"""
Create New Database Schema

This script creates a new database structure with:
- users table
- futures_trades_orders and futures_trades_history
- spot_trades_orders and spot_trades_history
"""

import sqlite3
from datetime import datetime


def create_new_database(db_path='trading_data.db'):
    """Create new database with improved schema"""
    print("=" * 80)
    print("CREATING NEW DATABASE SCHEMA")
    print("=" * 80)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ========================================================================
    # USERS TABLE - Central user registry
    # ========================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        )
    ''')
    print("✓ Created table: users")
    
    # ========================================================================
    # FUTURES TRADES - ORDER HISTORY
    # ========================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS futures_trades_orders (
            order_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            order_type TEXT,
            side TEXT,
            price REAL,
            quantity REAL,
            filled_quantity REAL,
            status TEXT,
            order_time TIMESTAMP,
            update_time TIMESTAMP,
            time_in_force TEXT,
            reduce_only INTEGER,
            close_position INTEGER,
            stop_price REAL,
            working_type TEXT,
            price_protect INTEGER,
            original_type TEXT,
            position_side TEXT,
            activation_price REAL,
            price_rate REAL,
            avg_price REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    print("✓ Created table: futures_trades_orders")
    
    # ========================================================================
    # FUTURES TRADES - TRADE HISTORY
    # ========================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS futures_trades_history (
            trade_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            order_id TEXT,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            price REAL NOT NULL,
            quantity REAL NOT NULL,
            quote_quantity REAL,
            commission REAL,
            commission_asset TEXT,
            trade_time TIMESTAMP NOT NULL,
            is_buyer INTEGER,
            is_maker INTEGER,
            is_isolated INTEGER,
            position_side TEXT,
            realized_pnl REAL,
            margin_asset TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (order_id) REFERENCES futures_trades_orders(order_id)
        )
    ''')
    print("✓ Created table: futures_trades_history")
    
    # ========================================================================
    # SPOT TRADES - ORDER HISTORY
    # ========================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spot_trades_orders (
            order_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            order_type TEXT,
            side TEXT,
            price REAL,
            quantity REAL,
            filled_quantity REAL,
            status TEXT,
            order_time TIMESTAMP,
            update_time TIMESTAMP,
            time_in_force TEXT,
            stop_price REAL,
            iceberg_quantity REAL,
            is_working INTEGER,
            orig_quote_order_quantity REAL,
            self_trade_prevention_mode TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    print("✓ Created table: spot_trades_orders")
    
    # ========================================================================
    # SPOT TRADES - TRADE HISTORY
    # ========================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spot_trades_history (
            trade_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            order_id TEXT,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            price REAL NOT NULL,
            quantity REAL NOT NULL,
            quote_quantity REAL,
            commission REAL,
            commission_asset TEXT,
            trade_time TIMESTAMP NOT NULL,
            is_buyer INTEGER,
            is_maker INTEGER,
            is_best_match INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (order_id) REFERENCES spot_trades_orders(order_id)
        )
    ''')
    print("✓ Created table: spot_trades_history")
    
    # ========================================================================
    # INDEXES for Performance
    # ========================================================================
    print("\nCreating indexes...")
    
    # Futures indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_futures_orders_user ON futures_trades_orders(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_futures_orders_symbol ON futures_trades_orders(symbol)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_futures_orders_time ON futures_trades_orders(order_time)')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_futures_trades_user ON futures_trades_history(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_futures_trades_symbol ON futures_trades_history(symbol)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_futures_trades_time ON futures_trades_history(trade_time)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_futures_trades_order ON futures_trades_history(order_id)')
    
    # Spot indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_spot_orders_user ON spot_trades_orders(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_spot_orders_symbol ON spot_trades_orders(symbol)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_spot_orders_time ON spot_trades_orders(order_time)')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_spot_trades_user ON spot_trades_history(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_spot_trades_symbol ON spot_trades_history(symbol)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_spot_trades_time ON spot_trades_history(trade_time)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_spot_trades_order ON spot_trades_history(order_id)')
    
    print("✓ Created all indexes")
    
    conn.commit()
    
    print("\n" + "=" * 80)
    print("DATABASE SCHEMA CREATED SUCCESSFULLY")
    print("=" * 80)
    print(f"Database: {db_path}")
    print("\nTables created:")
    print("  1. users")
    print("  2. futures_trades_orders")
    print("  3. futures_trades_history")
    print("  4. spot_trades_orders")
    print("  5. spot_trades_history")
    
    return conn


def verify_schema(conn):
    """Verify the schema was created correctly"""
    print("\n" + "=" * 80)
    print("VERIFYING SCHEMA")
    print("=" * 80)
    
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"\nTables in database: {len(tables)}")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"\n{table_name}:")
        print(f"  Columns: {len(columns)}")
        for col in columns[:5]:  # Show first 5 columns
            print(f"    - {col[1]} ({col[2]})")
        if len(columns) > 5:
            print(f"    ... and {len(columns) - 5} more columns")
    
    # Get all indexes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' ORDER BY name")
    indexes = cursor.fetchall()
    print(f"\nIndexes created: {len(indexes)}")
    
    print("\n✓ Schema verification complete")


def main():
    """Main function"""
    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + "NEW DATABASE SCHEMA CREATION".center(78) + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    
    # Create new database
    conn = create_new_database('trading_data.db')
    
    # Verify schema
    verify_schema(conn)
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. Open 'trading_data.db' in DB Browser to see the structure")
    print("2. Run migration script to move data from old database (if needed)")
    print("3. Start importing your futures and spot trade data")
    print("\nDatabase is ready to use!")


if __name__ == "__main__":
    main()
