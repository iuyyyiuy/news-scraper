"""
Simple import of ALL trades data to spot_trades_history table
Imports all trades from both users (not limited to LUNCBTC)
"""

import pandas as pd
import sqlite3
import os


def import_excel_to_database(db_path, excel_file, user_id):
    """
    Import ALL trades from Excel file to spot_trades_history table
    
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
        
        # Add user_id if not present
        if 'user_id' not in df.columns:
            df['user_id'] = user_id
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        
        # Import to spot_trades_history table
        df.to_sql('spot_trades_history', conn, if_exists='append', index=False)
        
        print(f"✓ Imported {len(df)} records to spot_trades_history table")
        
        # Verify import
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM spot_trades_history WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        print(f"✓ Total records for user {user_id}: {count}")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 70)
    print("IMPORT ALL TRADES DATA TO DATABASE")
    print("=" * 70)
    
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
    success1 = import_excel_to_database(
        db_path=db_path,
        excel_file="Extraction_Attack_case1/1445939.xlsx",
        user_id="1445939"
    )
    
    # Import user 4866868
    print("\n" + "-" * 70)
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
        
        print("\nImported Data:")
        cursor.execute("SELECT COUNT(*) FROM spot_trades_history WHERE user_id = '1445939'")
        count1 = cursor.fetchone()[0]
        print(f"  User 1445939: {count1} trades")
        
        cursor.execute("SELECT COUNT(*) FROM spot_trades_history WHERE user_id = '4866868'")
        count2 = cursor.fetchone()[0]
        print(f"  User 4866868: {count2} trades")
        
        print(f"  Total: {count1 + count2} trades")
        
        conn.close()


if __name__ == "__main__":
    main()
