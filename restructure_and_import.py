"""
Restructure spot_trades_history table and import extraction attack data
Matches Excel column structure exactly
"""

import pandas as pd
import sqlite3
import os


def restructure_table(db_path):
    """
    Delete all data and restructure spot_trades_history table
    """
    print("=" * 70)
    print("RESTRUCTURING spot_trades_history TABLE")
    print("=" * 70)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Delete all existing data
    print("\n1. Deleting all existing data...")
    cursor.execute("DELETE FROM spot_trades_history")
    deleted_count = cursor.rowcount
    print(f"   ✓ Deleted {deleted_count} records")
    
    # Drop the old table
    print("\n2. Dropping old table structure...")
    cursor.execute("DROP TABLE IF EXISTS spot_trades_history")
    print("   ✓ Table dropped")
    
    # Create new table with Excel column structure
    print("\n3. Creating new table structure...")
    cursor.execute("""
        CREATE TABLE spot_trades_history (
            user_id TEXT NOT NULL,
            order_id TEXT,
            client_id TEXT,
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
            advanced_settings TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("   ✓ New table created with columns:")
    print("      user_id, order_id, client_id, order_time, symbol,")
    print("      order_type, side, order_price, order_qty, filled_qty,")
    print("      avg_fill_price, notional, status, placed_by, advanced_settings")
    
    conn.commit()
    conn.close()
    
    print("\n✓ Table restructured successfully")


def import_excel_to_database(db_path, excel_file, user_id):
    """
    Import Excel file directly to spot_trades_history table
    Keeps all original columns
    """
    print(f"\nImporting: {excel_file}")
    print(f"User ID: {user_id}")
    
    if not os.path.exists(excel_file):
        print(f"✗ File not found: {excel_file}")
        return False
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_file)
        print(f"✓ Read {len(df)} records from Excel")
        
        # Normalize column names (handle Chinese columns)
        column_mapping = {
            '订单ID': 'order_id',
            'order_id': 'order_id'
        }
        df = df.rename(columns=column_mapping)
        
        # Add user_id column
        df.insert(0, 'user_id', user_id)
        
        # Rename columns to match database structure:
        # Excel order_qty → DB order_price
        # Excel filled_qty (first) → DB order_qty
        # Excel filled_qty.1 (second) → DB filled_qty
        df = df.rename(columns={
            'order_qty': 'order_price',
            'filled_qty': 'order_qty'
        })
        
        if 'filled_qty.1' in df.columns:
            df = df.rename(columns={'filled_qty.1': 'filled_qty'})
        
        # Select only the columns we want
        columns_to_keep = [
            'user_id', 'order_id', 'client_id', 'order_time', 'symbol',
            'order_type', 'side', 'order_price', 'order_qty', 'filled_qty',
            'avg_fill_price', 'notional', 'status', 'placed_by', 'advanced_settings'
        ]
        
        # Keep only columns that exist
        existing_columns = [col for col in columns_to_keep if col in df.columns]
        df_to_import = df[existing_columns]
        
        print(f"✓ Prepared {len(df_to_import)} records for import")
        print(f"  Columns: {list(df_to_import.columns)}")
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        
        # Import to spot_trades_history table
        df_to_import.to_sql('spot_trades_history', conn, if_exists='append', index=False)
        
        print(f"✓ Imported {len(df_to_import)} records")
        
        # Verify import
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM spot_trades_history WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        print(f"✓ Total records for user {user_id}: {count}")
        
        # Show sample
        cursor.execute("""
            SELECT user_id, symbol, side, filled_qty, avg_fill_price, order_time 
            FROM spot_trades_history 
            WHERE user_id = ? 
            LIMIT 3
        """, (user_id,))
        
        print(f"\n  Sample records:")
        for row in cursor.fetchall():
            print(f"    User {row[0]}: {row[1]} {row[2]} {row[3]}@{row[4]} at {row[5]}")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 70)
    print("RESTRUCTURE AND IMPORT EXTRACTION ATTACK DATA")
    print("=" * 70)
    
    db_path = "trading_data.db"
    
    if not os.path.exists(db_path):
        print(f"\n✗ Database not found: {db_path}")
        return
    
    print(f"\nUsing database: {db_path}\n")
    
    # Step 1: Restructure table
    restructure_table(db_path)
    
    # Step 2: Import user 1445939
    print("\n" + "=" * 70)
    print("IMPORTING USER 1445939")
    print("=" * 70)
    success1 = import_excel_to_database(
        db_path=db_path,
        excel_file="Extraction_Attack_case1/1445939.xlsx",
        user_id="1445939"
    )
    
    # Step 3: Import user 4866868
    print("\n" + "=" * 70)
    print("IMPORTING USER 4866868")
    print("=" * 70)
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
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\nFinal Summary:")
        
        # Total records
        cursor.execute("SELECT COUNT(*) FROM spot_trades_history")
        total = cursor.fetchone()[0]
        print(f"  Total records: {total}")
        
        # By user
        cursor.execute("SELECT user_id, COUNT(*) FROM spot_trades_history GROUP BY user_id")
        for row in cursor.fetchall():
            print(f"    User {row[0]}: {row[1]} trades")
        
        # By symbol
        print("\n  Top symbols:")
        cursor.execute("""
            SELECT symbol, COUNT(*) as count 
            FROM spot_trades_history 
            GROUP BY symbol 
            ORDER BY count DESC 
            LIMIT 10
        """)
        for row in cursor.fetchall():
            print(f"    {row[0]}: {row[1]} trades")
        
        conn.close()
    
    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
