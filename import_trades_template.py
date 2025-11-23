"""
Template for Importing Trade Data

This shows you how to import your futures and spot trade data
into the new database structure.
"""

import sqlite3
import pandas as pd
from datetime import datetime


def import_user(conn, user_id, notes=None):
    """Import a single user"""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, notes)
        VALUES (?, ?)
    ''', (user_id, notes))
    conn.commit()
    print(f"✓ Imported user: {user_id}")


def import_futures_order(conn, order_data):
    """
    Import a futures order
    
    order_data should be a dict with keys:
        order_id, user_id, symbol, order_type, side, price, quantity, etc.
    """
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO futures_trades_orders (
            order_id, user_id, symbol, order_type, side, price, quantity,
            filled_quantity, status, order_time, update_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        order_data.get('order_id'),
        order_data.get('user_id'),
        order_data.get('symbol'),
        order_data.get('order_type'),
        order_data.get('side'),
        order_data.get('price'),
        order_data.get('quantity'),
        order_data.get('filled_quantity'),
        order_data.get('status'),
        order_data.get('order_time'),
        order_data.get('update_time')
    ))
    conn.commit()


def import_futures_trade(conn, trade_data):
    """
    Import a futures trade
    
    trade_data should be a dict with keys:
        trade_id, user_id, order_id, symbol, side, price, quantity, etc.
    """
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO futures_trades_history (
            trade_id, user_id, order_id, symbol, side, price, quantity,
            commission, commission_asset, trade_time, is_buyer, is_maker
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        trade_data.get('trade_id'),
        trade_data.get('user_id'),
        trade_data.get('order_id'),
        trade_data.get('symbol'),
        trade_data.get('side'),
        trade_data.get('price'),
        trade_data.get('quantity'),
        trade_data.get('commission'),
        trade_data.get('commission_asset'),
        trade_data.get('trade_time'),
        trade_data.get('is_buyer', 0),
        trade_data.get('is_maker', 0)
    ))
    conn.commit()


def import_spot_order(conn, order_data):
    """Import a spot order"""
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO spot_trades_orders (
            order_id, user_id, symbol, order_type, side, price, quantity,
            filled_quantity, status, order_time, update_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        order_data.get('order_id'),
        order_data.get('user_id'),
        order_data.get('symbol'),
        order_data.get('order_type'),
        order_data.get('side'),
        order_data.get('price'),
        order_data.get('quantity'),
        order_data.get('filled_quantity'),
        order_data.get('status'),
        order_data.get('order_time'),
        order_data.get('update_time')
    ))
    conn.commit()


def import_spot_trade(conn, trade_data):
    """Import a spot trade"""
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO spot_trades_history (
            trade_id, user_id, order_id, symbol, side, price, quantity,
            commission, commission_asset, trade_time, is_buyer, is_maker
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        trade_data.get('trade_id'),
        trade_data.get('user_id'),
        trade_data.get('order_id'),
        trade_data.get('symbol'),
        trade_data.get('side'),
        trade_data.get('price'),
        trade_data.get('quantity'),
        trade_data.get('commission'),
        trade_data.get('commission_asset'),
        trade_data.get('trade_time'),
        trade_data.get('is_buyer', 0),
        trade_data.get('is_maker', 0)
    ))
    conn.commit()


def example_import_from_excel():
    """Example: Import data from Excel file"""
    conn = sqlite3.connect('trading_data.db')
    
    # Example: Read Excel file
    df = pd.read_excel('your_file.xlsx')
    
    # Import user first
    user_id = 'user_12345'
    import_user(conn, user_id, notes='Imported from Excel')
    
    # Import each row as a trade
    for idx, row in df.iterrows():
        trade_data = {
            'trade_id': f"{user_id}_trade_{idx}",
            'user_id': user_id,
            'order_id': f"{user_id}_order_{idx}",
            'symbol': row['symbol'],
            'side': row['side'],
            'price': float(row['price']),
            'quantity': float(row['quantity']),
            'trade_time': pd.to_datetime(row['timestamp']),
            'commission': row.get('commission', 0),
            'commission_asset': row.get('commission_asset', 'USDT')
        }
        
        # Choose futures or spot based on your data
        import_futures_trade(conn, trade_data)
    
    conn.close()
    print(f"✓ Imported {len(df)} trades for {user_id}")


def example_bulk_import():
    """Example: Bulk import multiple users"""
    conn = sqlite3.connect('trading_data.db')
    
    users = ['user_001', 'user_002', 'user_003']
    
    for user_id in users:
        # Import user
        import_user(conn, user_id)
        
        # Import their trades
        # ... your logic here
    
    conn.close()


def query_examples():
    """Example queries for the new structure"""
    conn = sqlite3.connect('trading_data.db')
    
    # Get all futures trades for a user
    df = pd.read_sql_query('''
        SELECT * FROM futures_trades_history
        WHERE user_id = 'user_12345'
        ORDER BY trade_time DESC
    ''', conn)
    
    # Get all spot trades for a symbol
    df = pd.read_sql_query('''
        SELECT * FROM spot_trades_history
        WHERE symbol = 'BTCUSDT'
        ORDER BY trade_time DESC
    ''', conn)
    
    # Get combined view of all trades for a user
    df = pd.read_sql_query('''
        SELECT 'futures' as market, * FROM futures_trades_history WHERE user_id = 'user_12345'
        UNION ALL
        SELECT 'spot' as market, * FROM spot_trades_history WHERE user_id = 'user_12345'
        ORDER BY trade_time DESC
    ''', conn)
    
    # Get trading summary by user and market
    df = pd.read_sql_query('''
        SELECT 
            user_id,
            'futures' as market,
            COUNT(*) as trade_count,
            SUM(quantity) as total_volume,
            AVG(price) as avg_price
        FROM futures_trades_history
        GROUP BY user_id
        UNION ALL
        SELECT 
            user_id,
            'spot' as market,
            COUNT(*) as trade_count,
            SUM(quantity) as total_volume,
            AVG(price) as avg_price
        FROM spot_trades_history
        GROUP BY user_id
    ''', conn)
    
    conn.close()
    return df


if __name__ == "__main__":
    print("This is a template file. Copy the functions you need.")
    print("\nAvailable functions:")
    print("  - import_user()")
    print("  - import_futures_order()")
    print("  - import_futures_trade()")
    print("  - import_spot_order()")
    print("  - import_spot_trade()")
    print("\nSee the code for examples of how to use them.")
