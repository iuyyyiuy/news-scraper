"""
Remove created_at column from all tables in trading_data.db
"""

import sqlite3


def remove_created_at_column(db_path, table_name):
    """Remove created_at column from a table"""
    print(f"\nProcessing table: {table_name}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get current table structure
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # Check if created_at exists
        has_created_at = any(col[1] == 'created_at' for col in columns)
        
        if not has_created_at:
            print(f"  ✓ No created_at column found")
            conn.close()
            return
        
        # Get column names excluding created_at
        column_names = [col[1] for col in columns if col[1] != 'created_at']
        columns_str = ', '.join(column_names)
        
        print(f"  Found created_at column, removing...")
        
        # Create new table without created_at
        cursor.execute(f"CREATE TABLE {table_name}_new AS SELECT {columns_str} FROM {table_name}")
        
        # Drop old table
        cursor.execute(f"DROP TABLE {table_name}")
        
        # Rename new table
        cursor.execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name}")
        
        conn.commit()
        print(f"  ✓ Removed created_at column")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        conn.rollback()
    finally:
        conn.close()


def main():
    print("=" * 70)
    print("REMOVE created_at COLUMN FROM ALL TABLES")
    print("=" * 70)
    
    db_path = "trading_data.db"
    
    # List of tables to process
    tables = [
        'futures_trades_history',
        'futures_trades_orders',
        'spot_trades_orders',
        'users'
    ]
    
    for table in tables:
        remove_created_at_column(db_path, table)
    
    # Verify
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        has_created_at = any(col[1] == 'created_at' for col in columns)
        
        if has_created_at:
            print(f"  ✗ {table}: still has created_at")
        else:
            print(f"  ✓ {table}: created_at removed")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
