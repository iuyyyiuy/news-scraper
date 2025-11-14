"""
Import Futures Trade Data from Standardized Excel Files

This script:
1. Clears existing data from futures_trades_orders and futures_trades_history
2. Imports users
3. Imports futures trade history from Excel files
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime


def clear_futures_data(conn):
    """Clear all data from futures tables"""
    print("\n" + "=" * 80)
    print("CLEARING EXISTING FUTURES DATA")
    print("=" * 80)
    
    cursor = conn.cursor()
    
    # Clear futures_trades_history first (has foreign key to orders)
    cursor.execute("DELETE FROM futures_trades_history")
    deleted_trades = cursor.rowcount
    print(f"✓ Cleared {deleted_trades} records from futures_trades_history")
    
    # Clear futures_trades_orders
    cursor.execute("DELETE FROM futures_trades_orders")
    deleted_orders = cursor.rowcount
    print(f"✓ Cleared {deleted_orders} records from futures_trades_orders")
    
    # Clear users (will be re-imported)
    cursor.execute("DELETE FROM users")
    deleted_users = cursor.rowcount
    print(f"✓ Cleared {deleted_users} records from users")
    
    conn.commit()
    print("\n✓ All futures data cleared")


def import_user(conn, user_id):
    """Import or update a user"""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, updated_at)
        VALUES (?, ?)
    ''', (user_id, datetime.now()))


def import_futures_trades_from_excel(conn, file_path, user_id):
    """
    Import futures trades from Excel file
    
    Excel columns (standardized):
    - open_time, close_time, symbol, side
    - avg_entry_price, entry_price, exit_price, close_type
    - max_qty, max_notional, realized_pnl, fees, funding_fee
    
    Each row in Excel = one complete position (open + close)
    """
    try:
        # Read Excel
        df = pd.read_excel(file_path)
        
        cursor = conn.cursor()
        
        # Import each row as one position record
        for idx, row in df.iterrows():
            cursor.execute('''
                INSERT INTO futures_trades_history (
                    user_id, open_time, close_time, symbol, side,
                    avg_entry_price, entry_price, exit_price, close_type,
                    max_qty, max_notional, realized_pnl, fees, funding_fee
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                str(pd.to_datetime(row['open_time'])),
                str(pd.to_datetime(row['close_time'])),
                row['symbol'],
                row['side'],  # 'long' or 'short'
                float(row['avg_entry_price']) if pd.notna(row['avg_entry_price']) else None,
                float(row['entry_price']),
                float(row['exit_price']),
                row['close_type'] if pd.notna(row['close_type']) else None,  # 'limit' or 'market'
                float(row['max_qty']),
                float(row['max_notional']) if pd.notna(row['max_notional']) else None,
                float(row['realized_pnl']) if pd.notna(row['realized_pnl']) else None,
                float(row['fees']) if pd.notna(row['fees']) else None,
                float(row['funding_fee']) if pd.notna(row['funding_fee']) else None
            ))
        
        conn.commit()
        return len(df), None
        
    except Exception as e:
        return 0, str(e)


def find_all_excel_files(directories=['商務大使09.22', '商務大使09.28']):
    """Find all Excel files"""
    all_files = []
    
    for directory in directories:
        if Path(directory).exists():
            files = list(Path(directory).rglob("*.xlsx"))
            all_files.extend(files)
    
    return all_files


def extract_user_id_from_filename(filepath):
    """Extract UID from filename"""
    filename = Path(filepath).stem
    
    # Check if filename starts with "UID " (e.g., "UID 8347040")
    if filename.startswith("UID "):
        return filename.split()[1]  # Just the number
    
    # Check if filename is just a number (e.g., "8347040")
    if filename.isdigit():
        return filename  # Just the number
    
    return None


def main():
    """Main import function"""
    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + "IMPORT FUTURES TRADE DATA".center(78) + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    
    # Connect to database
    conn = sqlite3.connect('trading_data.db')
    
    # Clear existing data
    clear_futures_data(conn)
    
    print("\n" + "=" * 80)
    print("FINDING EXCEL FILES")
    print("=" * 80)
    
    files = find_all_excel_files()
    print(f"\nFound {len(files)} Excel files")
    
    print("\n" + "=" * 80)
    print("IMPORTING DATA")
    print("=" * 80)
    
    total_trades = 0
    users_imported = 0
    errors = []
    
    for i, file_path in enumerate(files, 1):
        user_id = extract_user_id_from_filename(file_path)
        
        if not user_id:
            print(f"\n[{i}/{len(files)}] Skipping {file_path.name} - no UID found")
            continue
        
        print(f"\n[{i}/{len(files)}] {user_id} ({file_path.name})")
        
        # Import user first
        import_user(conn, user_id)
        
        # Import trades
        trade_count, error = import_futures_trades_from_excel(conn, file_path, user_id)
        
        if error:
            print(f"  ✗ Error: {error}")
            errors.append((user_id, error))
        else:
            print(f"  ✓ Imported {trade_count} trades")
            total_trades += trade_count
            users_imported += 1
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("IMPORT COMPLETE")
    print("=" * 80)
    print(f"Users imported: {users_imported}")
    print(f"Total trades imported: {total_trades:,}")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print("\nErrors encountered:")
        for user_id, error in errors:
            print(f"  {user_id}: {error}")
    
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    # Verify import
    conn = sqlite3.connect('trading_data.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"\nUsers in database: {user_count}")
    
    cursor.execute("SELECT COUNT(*) FROM futures_trades_history")
    trade_count = cursor.fetchone()[0]
    print(f"Futures trades in database: {trade_count:,}")
    
    cursor.execute("SELECT COUNT(*) FROM futures_trades_orders")
    order_count = cursor.fetchone()[0]
    print(f"Futures orders in database: {order_count:,}")
    
    # Show sample data
    print("\nTop 5 users by position count:")
    cursor.execute("""
        SELECT 
            u.user_id,
            COUNT(t.id) as position_count,
            MIN(t.open_time) as first_trade,
            MAX(t.close_time) as last_trade
        FROM users u
        LEFT JOIN futures_trades_history t ON u.user_id = t.user_id
        GROUP BY u.user_id
        ORDER BY position_count DESC
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} positions ({row[2]} to {row[3]})")
    
    # Show sample positions
    print("\nSample positions:")
    cursor.execute("""
        SELECT id, user_id, symbol, side, entry_price, exit_price, max_qty, realized_pnl
        FROM futures_trades_history
        ORDER BY close_time DESC
        LIMIT 3
    """)
    
    for row in cursor.fetchall():
        print(f"  Position {row[0]}: {row[1]} {row[2]} {row[3]} | Entry: {row[4]} Exit: {row[5]} | Qty: {row[6]} | PnL: {row[7]}")
    
    conn.close()
    
    print("\n✓ Import successful!")
    print("\nNext steps:")
    print("  1. Open trading_data.db in DB Browser to explore")
    print("  2. Run queries to analyze the data")
    print("  3. Build reports and dashboards")


if __name__ == "__main__":
    main()
