"""
Import extraction attack data to spot_trades_history table
Maps Excel columns to database schema properly
"""

import pandas as pd
import sqlite3
import os
from datetime import datetime


def import_excel_to_database(db_path, excel_file, user_id):
    """
    Import ALL trades from Excel file to spot_trades_history table
    Maps columns properly to match database schema
    
    Args:
        db_path: Path to SQLite database
        excel_file: Path to Excel file
        user_id: User ID
    """
    print(f"\nImporting: {excel_file}")
    print(f"User ID: {user_id}")
    
    # Check if file exists
    if not os.path.exists(excel_file):
        print(f"✗ File not found: {excel_file}")
        return False
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_file)
        print(f"✓ Read {len(df)} records from Excel")
        print(f"  Excel columns: {list(df.columns)}")
        
        # Normalize column names (handle Chinese columns)
        column_mapping = {
            '订单ID': 'order_id',
            'order_id': 'order_id',
            'client_id': 'client_id',
            'order_time': 'order_time',
            'symbol': 'symbol',
            'order_type': 'order_type',
            'side': 'side',
            'order_qty': 'order_qty',
            'filled_qty': 'filled_qty',
            'avg_fill_price': 'avg_fill_price',
            'notional': 'notional',
            'status': 'status'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        print(f"✓ Normalized column names")
        
        # Filter out rows with NULL symbols
        original_count = len(df)
        df = df[df['symbol'].notna()]
        if len(df) < original_count:
            print(f"  Filtered out {original_count - len(df)} rows with NULL symbols")
        
        # Map Excel columns to database columns
        # Excel: order_id, client_id, order_time, symbol, order_type, side, order_qty, filled_qty, avg_fill_price, notional, status
        # DB: trade_id, user_id, order_id, symbol, side, price, quantity, quote_quantity, trade_time
        
        mapped_df = pd.DataFrame()
        
        # Generate trade_id (use order_id + row number for uniqueness)
        mapped_df['trade_id'] = df['order_id'].astype(str) + '_' + df.index.astype(str)
        
        # Add user_id
        mapped_df['user_id'] = user_id
        
        # Map order_id
        mapped_df['order_id'] = df['order_id']
        
        # Map symbol
        mapped_df['symbol'] = df['symbol']
        
        # Map side (BUY/SELL)
        mapped_df['side'] = df['side']
        
        # Map price (avg_fill_price)
        mapped_df['price'] = df['avg_fill_price']
        
        # Map quantity (filled_qty)
        mapped_df['quantity'] = df['filled_qty']
        
        # Map quote_quantity (notional)
        mapped_df['quote_quantity'] = df['notional'] if 'notional' in df.columns else None
        
        # Map commission (if exists)
        mapped_df['commission'] = None
        mapped_df['commission_asset'] = None
        
        # Map trade_time (order_time)
        mapped_df['trade_time'] = pd.to_datetime(df['order_time'])
        
        # Map is_buyer (True if side is BUY)
        mapped_df['is_buyer'] = (df['side'] == 'BUY').astype(int)
        
        # Set defaults for other fields
        mapped_df['is_maker'] = 0
        mapped_df['is_best_match'] = 0
        
        print(f"✓ Mapped to database schema")
        print(f"  Database columns: {list(mapped_df.columns)}")
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        
        # Import to spot_trades_history table
        mapped_df.to_sql('spot_trades_history', conn, if_exists='append', index=False)
        
        print(f"✓ Imported {len(mapped_df)} records to spot_trades_history table")
        
        # Verify import
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM spot_trades_history WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        print(f"✓ Total records for user {user_id}: {count}")
        
        # Show sample of imported data
        cursor.execute("""
            SELECT trade_id, symbol, side, price, quantity, trade_time 
            FROM spot_trades_history 
            WHERE user_id = ? 
            LIMIT 3
        """, (user_id,))
        
        print(f"\n  Sample records:")
        for row in cursor.fetchall():
            print(f"    {row[1]} {row[2]} {row[4]}@{row[3]} at {row[5]}")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 70)
    print("IMPORT EXTRACTION ATTACK DATA TO DATABASE")
    print("=" * 70)
    print("\nImporting ALL trades from both users to spot_trades_history table")
    
    # Database path
    db_path = "trading_data.db"
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"\n✗ Database not found: {db_path}")
        print("Please specify the correct database path.")
        return
    
    print(f"\nUsing database: {db_path}")
    
    # Import user 1445939
    print("\n" + "-" * 70)
    print("USER 1445939")
    print("-" * 70)
    success1 = import_excel_to_database(
        db_path=db_path,
        excel_file="Extraction_Attack_case1/1445939.xlsx",
        user_id="1445939"
    )
    
    # Import user 4866868
    print("\n" + "-" * 70)
    print("USER 4866868")
    print("-" * 70)
    success2 = import_excel_to_database(
        db_path=db_path,
        excel_file="Extraction_Attack_case1/4866868.xlsx",
        user_id="4866868"
    )
    
    # Summary
    print("\n" + "=" * 70)
    if success1 and success2:
        print("✓ IMPORT COMPLETE")
    else:
        print("✗ IMPORT FAILED")
    print("=" * 70)
    
    if success1 and success2:
        # Show summary
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\nImported Data Summary:")
        
        # User 1445939
        cursor.execute("SELECT COUNT(*) FROM spot_trades_history WHERE user_id = '1445939'")
        count1 = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT symbol) FROM spot_trades_history WHERE user_id = '1445939'")
        symbols1 = cursor.fetchone()[0]
        print(f"  User 1445939: {count1} trades across {symbols1} symbols")
        
        # User 4866868
        cursor.execute("SELECT COUNT(*) FROM spot_trades_history WHERE user_id = '4866868'")
        count2 = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT symbol) FROM spot_trades_history WHERE user_id = '4866868'")
        symbols2 = cursor.fetchone()[0]
        print(f"  User 4866868: {count2} trades across {symbols2} symbols")
        
        print(f"\n  Total: {count1 + count2} trades")
        
        # Show symbols traded
        print("\n  Symbols traded:")
        cursor.execute("""
            SELECT DISTINCT symbol, COUNT(*) as trade_count 
            FROM spot_trades_history 
            WHERE user_id IN ('1445939', '4866868')
            GROUP BY symbol
            ORDER BY trade_count DESC
        """)
        for row in cursor.fetchall():
            print(f"    {row[0]}: {row[1]} trades")
        
        conn.close()
    
    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
