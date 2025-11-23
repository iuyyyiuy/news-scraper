"""
Import Futures Orders from Excel Files

This script imports your Excel files as futures orders into the new database.
Maps Chinese column names to English.
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


def import_futures_orders_from_excel(conn, file_path, user_id):
    """
    Import Excel file as futures orders
    
    Chinese columns → English mapping:
    - 开仓时间 → open_time
    - 平仓时间 → close_time
    - 合约 → symbol
    - 方向 → side
    - 类型 → order_type
    - 开仓均价 → avg_entry_price
    - 进入价格 → entry_price
    - 离开价格 → exit_price
    - 平仓类型 → close_type
    - 历史最高数量 → max_qty
    - 历史最高名义价值 → max_notional
    - 已实现盈亏 → realized_pnl
    - 手续费 → fees
    - 资金费用 → funding_fee
    """
    print(f"\nProcessing {user_id}...")
    
    try:
        # Read Excel
        df = pd.read_excel(file_path)
        
        # Column mapping - Chinese to English
        column_mapping = {
            '开仓时间': 'open_time',
            '平仓时间': 'close_time',
            '合约': 'symbol',
            '方向': 'side',
            '类型': 'order_type',
            '开仓均价': 'avg_entry_price',
            '进入价格': 'entry_price',
            '离开价格': 'exit_price',
            '平仓类型': 'close_type',
            '历史最高数量': 'max_qty',
            '历史最高名义价值': 'max_notional',
            '已实现盈亏': 'realized_pnl',
            '手续费': 'fees',
            '资金费用': 'funding_fee'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        cursor = conn.cursor()
        order_count = 0
        
        # Import each row as an order
        for idx, row in df.iterrows():
            order_id = f"{user_id}_order_{idx}"
            
            # Determine position side from order type (多仓 = LONG, 空仓 = SHORT)
            position_side = None
            if 'order_type' in row and pd.notna(row['order_type']):
                if '多仓' in str(row['order_type']) or '多' in str(row['order_type']):
                    position_side = 'LONG'
                elif '空仓' in str(row['order_type']) or '空' in str(row['order_type']):
                    position_side = 'SHORT'
            
            # Insert into futures_trades_orders
            cursor.execute('''
                INSERT OR REPLACE INTO futures_trades_orders (
                    order_id,
                    user_id,
                    symbol,
                    side,
                    order_type,
                    price,
                    quantity,
                    avg_price,
                    status,
                    order_time,
                    update_time,
                    position_side
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                order_id,
                user_id,
                row.get('symbol'),
                row.get('side'),
                row.get('order_type'),
                float(row['entry_price']) if pd.notna(row.get('entry_price')) else None,
                float(row['max_qty']) if pd.notna(row.get('max_qty')) else None,
                float(row['avg_entry_price']) if pd.notna(row.get('avg_entry_price')) else None,
                'FILLED',  # Assume all orders are filled since we have close data
                str(pd.to_datetime(row['open_time'])) if pd.notna(row.get('open_time')) else None,
                str(pd.to_datetime(row['close_time'])) if pd.notna(row.get('close_time')) else None,
                position_side
            ))
            order_count += 1
            
            # Also create opening trade
            open_trade_id = f"{user_id}_trade_open_{idx}"
            cursor.execute('''
                INSERT OR REPLACE INTO futures_trades_history (
                    trade_id,
                    user_id,
                    order_id,
                    symbol,
                    side,
                    price,
                    quantity,
                    trade_time,
                    position_side,
                    realized_pnl
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                open_trade_id,
                user_id,
                order_id,
                row.get('symbol'),
                'BUY' if position_side == 'LONG' else 'SELL',
                float(row['entry_price']) if pd.notna(row.get('entry_price')) else None,
                float(row['max_qty']) if pd.notna(row.get('max_qty')) else None,
                str(pd.to_datetime(row['open_time'])) if pd.notna(row.get('open_time')) else None,
                position_side,
                0  # Opening trade has no PnL
            ))
            
            # Create closing trade
            close_trade_id = f"{user_id}_trade_close_{idx}"
            cursor.execute('''
                INSERT OR REPLACE INTO futures_trades_history (
                    trade_id,
                    user_id,
                    order_id,
                    symbol,
                    side,
                    price,
                    quantity,
                    trade_time,
                    position_side,
                    realized_pnl,
                    commission
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                close_trade_id,
                user_id,
                order_id,
                row.get('symbol'),
                'SELL' if position_side == 'LONG' else 'BUY',
                float(row['exit_price']) if pd.notna(row.get('exit_price')) else None,
                float(row['max_qty']) if pd.notna(row.get('max_qty')) else None,
                str(pd.to_datetime(row['close_time'])) if pd.notna(row.get('close_time')) else None,
                position_side,
                float(row['realized_pnl']) if pd.notna(row.get('realized_pnl')) else None,
                float(row['fees']) if pd.notna(row.get('fees')) else None
            ))
        
        conn.commit()
        print(f"  ✓ Imported {order_count} orders and {order_count * 2} trades")
        return order_count
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
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
    
    # Try just "12345" format (filename is the UID)
    if filename.replace(' ', '').isdigit():
        return f"user_{filename.replace(' ', '')}"
    
    # Try to extract any number from filename
    import re
    numbers = re.findall(r'\d+', filename)
    if numbers:
        return f"user_{numbers[-1]}"  # Use last number found
    
    return None


def main():
    """Main import function"""
    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + "IMPORT FUTURES ORDERS FROM EXCEL".center(78) + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    
    # Connect to database
    conn = sqlite3.connect('trading_data.db')
    
    print("\n" + "=" * 80)
    print("FINDING EXCEL FILES")
    print("=" * 80)
    
    files = find_all_excel_files()
    print(f"\nFound {len(files)} Excel files")
    
    print("\n" + "=" * 80)
    print("IMPORTING DATA")
    print("=" * 80)
    
    total_orders = 0
    users_imported = 0
    
    for i, file_path in enumerate(files, 1):
        user_id = extract_user_id_from_filename(file_path)
        
        if not user_id:
            print(f"\n[{i}/{len(files)}] Skipping {file_path.name} - no UID found")
            continue
        
        print(f"\n[{i}/{len(files)}] {user_id} ({file_path.name})")
        
        # Import user first
        import_user(conn, user_id, notes=f"Imported from {file_path.name}")
        
        # Import orders
        order_count = import_futures_orders_from_excel(conn, file_path, user_id)
        
        if order_count > 0:
            total_orders += order_count
            users_imported += 1
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("IMPORT COMPLETE")
    print("=" * 80)
    print(f"Users imported: {users_imported}")
    print(f"Total orders imported: {total_orders:,}")
    print(f"Total trades imported: {total_orders * 2:,} (open + close)")
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
    
    cursor.execute("SELECT COUNT(*) FROM futures_trades_orders")
    order_count = cursor.fetchone()[0]
    print(f"Futures orders in database: {order_count:,}")
    
    cursor.execute("SELECT COUNT(*) FROM futures_trades_history")
    trade_count = cursor.fetchone()[0]
    print(f"Futures trades in database: {trade_count:,}")
    
    # Show sample
    print("\nTop 5 users by order count:")
    cursor.execute("""
        SELECT 
            u.user_id,
            COUNT(o.order_id) as order_count,
            COUNT(t.trade_id) as trade_count
        FROM users u
        LEFT JOIN futures_trades_orders o ON u.user_id = o.user_id
        LEFT JOIN futures_trades_history t ON u.user_id = t.user_id
        GROUP BY u.user_id
        ORDER BY order_count DESC
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} orders, {row[2]} trades")
    
    # Show sample data
    print("\nSample order:")
    cursor.execute("""
        SELECT order_id, user_id, symbol, side, position_side, quantity, price
        FROM futures_trades_orders
        LIMIT 1
    """)
    
    row = cursor.fetchone()
    if row:
        print(f"  Order ID: {row[0]}")
        print(f"  User: {row[1]}")
        print(f"  Symbol: {row[2]}")
        print(f"  Side: {row[3]}")
        print(f"  Position: {row[4]}")
        print(f"  Quantity: {row[5]}")
        print(f"  Price: {row[6]}")
    
    conn.close()
    
    print("\n✓ Import successful!")
    print("\nNext steps:")
    print("  1. Open trading_data.db in DB Browser to explore")
    print("  2. Run queries to analyze the data")
    print("  3. Add spot trades if you have them")


if __name__ == "__main__":
    main()
