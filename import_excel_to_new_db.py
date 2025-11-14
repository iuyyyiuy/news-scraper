"""
Import Excel Files to New Database

This script imports your existing Excel files into the new trading_data.db structure.
It will treat all your current data as FUTURES trades.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime


def import_user(conn, user_id, notes=None):
    """Import or update a user"""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, notes, updated_at)
        VALUES (?, ?, ?)
    ''', (user_id, notes, datetime.now()))
    conn.commit()


def import_excel_file_as_futures(conn, file_path, user_id):
    """
    Import an Excel file as futures trades
    
    Assumes Excel has columns:
    - 开仓时间 (open time)
    - 平仓时间 (close time)
    - 合约 (symbol)
    - 类型 (position type: 多仓/空仓)
    - 进入价格 (entry price)
    - 离开价格 (exit price)
    - 历史最高数量 (quantity)
    """
    print(f"\nProcessing {user_id}...")
    
    try:
        # Read Excel
        df = pd.read_excel(file_path)
        
        # Column mapping
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
        
        df = df.rename(columns=column_mapping)
        
        cursor = conn.cursor()
        trade_count = 0
        
        # Process each row (each row is a position with open and close)
        for idx, row in df.iterrows():
            # Determine side based on position type
            is_long = row['position_type'] == '多仓'
            
            # Opening trade (BUY for long, SELL for short)
            open_trade_id = f"{user_id}_open_{idx}"
            open_side = 'BUY' if is_long else 'SELL'
            
            cursor.execute('''
                INSERT OR REPLACE INTO futures_trades_history (
                    trade_id, user_id, symbol, side, price, quantity, 
                    trade_time, position_side
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                open_trade_id,
                user_id,
                row['symbol'],
                open_side,
                float(row['entry_price']),
                float(row['max_quantity']),
                str(pd.to_datetime(row['open_time'])),
                'LONG' if is_long else 'SHORT'
            ))
            trade_count += 1
            
            # Closing trade (SELL for long, BUY for short)
            close_trade_id = f"{user_id}_close_{idx}"
            close_side = 'SELL' if is_long else 'BUY'
            
            cursor.execute('''
                INSERT OR REPLACE INTO futures_trades_history (
                    trade_id, user_id, symbol, side, price, quantity, 
                    trade_time, position_side
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                close_trade_id,
                user_id,
                row['symbol'],
                close_side,
                float(row['exit_price']),
                float(row['max_quantity']),
                str(pd.to_datetime(row['close_time'])),
                'LONG' if is_long else 'SHORT'
            ))
            trade_count += 1
        
        conn.commit()
        print(f"  ✓ Imported {trade_count} trades from {len(df)} positions")
        return trade_count
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return 0


def find_all_excel_files(directories=['商務大使09.22', '商務大使09.28']):
    """Find all Excel files in directories"""
    all_files = []
    
    for directory in directories:
        if Path(directory).exists():
            files = list(Path(directory).rglob("*.xlsx"))
            all_files.extend(files)
    
    return all_files


def extract_user_id_from_filename(filepath):
    """Extract UID from filename"""
    filename = Path(filepath).stem
    
    # Try "UID 12345" format
    if filename.startswith("UID "):
        return f"user_{filename.split()[1]}"
    
    # Try just "12345.xlsx" format
    if filename.isdigit():
        return f"user_{filename}"
    
    return None


def main():
    """Main import function"""
    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + "IMPORT EXCEL FILES TO NEW DATABASE".center(78) + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    
    # Connect to new database
    conn = sqlite3.connect('trading_data.db')
    
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
    
    for i, file_path in enumerate(files, 1):
        user_id = extract_user_id_from_filename(file_path)
        
        if not user_id:
            print(f"\n[{i}/{len(files)}] Skipping {file_path.name} - no UID found")
            continue
        
        print(f"\n[{i}/{len(files)}] {user_id}")
        
        # Import user first
        import_user(conn, user_id, notes=f"Imported from {file_path.name}")
        
        # Import trades
        trade_count = import_excel_file_as_futures(conn, file_path, user_id)
        
        if trade_count > 0:
            total_trades += trade_count
            users_imported += 1
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("IMPORT COMPLETE")
    print("=" * 80)
    print(f"Users imported: {users_imported}")
    print(f"Total trades imported: {total_trades:,}")
    print(f"\nDatabase: trading_data.db")
    
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    # Verify import
    conn = sqlite3.connect('trading_data.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"Users in database: {user_count}")
    
    cursor.execute("SELECT COUNT(*) FROM futures_trades_history")
    trade_count = cursor.fetchone()[0]
    print(f"Futures trades in database: {trade_count:,}")
    
    cursor.execute("SELECT COUNT(*) FROM spot_trades_history")
    spot_count = cursor.fetchone()[0]
    print(f"Spot trades in database: {spot_count:,}")
    
    # Show sample
    print("\nSample users:")
    cursor.execute("""
        SELECT 
            u.user_id,
            COUNT(t.trade_id) as trade_count
        FROM users u
        LEFT JOIN futures_trades_history t ON u.user_id = t.user_id
        GROUP BY u.user_id
        ORDER BY trade_count DESC
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} trades")
    
    conn.close()
    
    print("\n✓ Import successful! Open trading_data.db in DB Browser to explore.")


if __name__ == "__main__":
    main()
