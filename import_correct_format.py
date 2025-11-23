"""
Import extraction attack data with CORRECT column mapping
Based on actual Excel structure
"""

import pandas as pd
import sqlite3
import os


def restructure_table(db_path):
    """Restructure table with correct columns"""
    print("Restructuring spot_trades_history table...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Delete all data
    cursor.execute("DELETE FROM spot_trades_history")
    print(f"✓ Deleted {cursor.rowcount} records")
    
    # Drop and recreate table
    cursor.execute("DROP TABLE IF EXISTS spot_trades_history")
    
    cursor.execute("""
        CREATE TABLE spot_trades_history (
            user_id TEXT NOT NULL,
            order_id TEXT,
            order_time TIMESTAMP,
            symbol TEXT,
            order_type TEXT,
            side TEXT,
            order_price REAL,
            order_qty REAL,
            filled_qty REAL,
            avg_fill_price REAL,
            notional REAL,
            status TEXT,
            placed_by TEXT,
            advanced_settings TEXT
        )
    """)
    
    print("✓ Table recreated with columns:")
    print("  user_id, order_id, order_time, symbol, order_type,")
    print("  side, order_price, order_qty, filled_qty, avg_fill_price, notional,")
    print("  status, placed_by, advanced_settings")
    
    conn.commit()
    conn.close()


def import_excel(db_path, excel_file, user_id):
    """Import Excel with correct column mapping"""
    print(f"\nImporting: {excel_file}")
    print(f"User ID: {user_id}")
    
    if not os.path.exists(excel_file):
        print(f"✗ File not found")
        return False
    
    try:
        # Read Excel
        df = pd.read_excel(excel_file)
        print(f"✓ Read {len(df)} records")
        
        # Handle Chinese column names
        df = df.rename(columns={'订单ID': 'order_id'})
        
        # Filter out rows with NULL symbols
        original_count = len(df)
        df = df[df['symbol'].notna()].copy()
        if len(df) < original_count:
            print(f"  Filtered out {original_count - len(df)} rows with NULL symbols")
        
        # Add user_id to dataframe
        df.insert(0, 'user_id', user_id)
        
        # Now the Excel already has the correct column names, just select them (excluding client_id)
        mapped_df = df[[
            'user_id', 'order_id', 'order_time', 'symbol',
            'order_type', 'side', 'order_price', 'order_qty', 'filled_qty',
            'avg_fill_price', 'notional', 'status', 'placed_by', 'advanced_settings'
        ]].copy()
        
        print(f"✓ Columns already match database schema")
        
        # Import to database
        conn = sqlite3.connect(db_path)
        mapped_df.to_sql('spot_trades_history', conn, if_exists='append', index=False)
        
        print(f"✓ Imported {len(mapped_df)} records")
        
        # Verify
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM spot_trades_history WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        print(f"✓ Total for user {user_id}: {count}")
        
        # Show sample
        cursor.execute("""
            SELECT symbol, side, order_price, order_qty, filled_qty, avg_fill_price 
            FROM spot_trades_history 
            WHERE user_id = ? 
            LIMIT 3
        """, (user_id,))
        
        print("\n  Sample records:")
        for row in cursor.fetchall():
            print(f"    {row[0]} {row[1]} order_price={row[2]} order_qty={row[3]} filled_qty={row[4]} avg_price={row[5]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 70)
    print("IMPORT WITH CORRECT FORMAT")
    print("=" * 70)
    
    db_path = "trading_data.db"
    
    if not os.path.exists(db_path):
        print(f"✗ Database not found: {db_path}")
        return
    
    print(f"\nDatabase: {db_path}\n")
    
    # Restructure table
    restructure_table(db_path)
    
    # Import user 1445939
    print("\n" + "=" * 70)
    print("USER 1445939")
    print("=" * 70)
    success1 = import_excel(db_path, "Extraction_Attack_case1/1445939.xlsx", "1445939")
    
    # Import user 4866868
    print("\n" + "=" * 70)
    print("USER 4866868")
    print("=" * 70)
    success2 = import_excel(db_path, "Extraction_Attack_case1/4866868.xlsx", "4866868")
    
    # Summary
    print("\n" + "=" * 70)
    if success1 and success2:
        print("✓ IMPORT COMPLETE")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM spot_trades_history")
        total = cursor.fetchone()[0]
        print(f"\nTotal records: {total}")
        
        cursor.execute("SELECT user_id, COUNT(*) FROM spot_trades_history GROUP BY user_id")
        for row in cursor.fetchall():
            print(f"  User {row[0]}: {row[1]} trades")
        
        conn.close()
    else:
        print("✗ IMPORT FAILED")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
