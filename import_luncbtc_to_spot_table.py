"""
Import LUNCBTC Extraction Attack Data to spot_trade_history table

Simple script to import victim and attacker data directly to the database.
"""

import pandas as pd
import sqlite3
from datetime import datetime
import os


def import_excel_to_spot_table(db_path, excel_file, user_id, label):
    """
    Import Excel file directly to spot_trade_history table
    
    Args:
        db_path: Path to SQLite database
        excel_file: Path to Excel file
        user_id: User ID
        label: 'victim' or 'attacker'
    """
    print(f"\nImporting {label} data: {excel_file}")
    print(f"User ID: {user_id}")
    
    # Check if file exists
    if not os.path.exists(excel_file):
        print(f"✗ File not found: {excel_file}")
        return False
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_file)
        print(f"✓ Read {len(df)} records from Excel")
        
        # Display columns
        print(f"Columns: {list(df.columns)}")
        
        # Add user_id if not present
        if 'user_id' not in df.columns:
            df['user_id'] = user_id
        
        # Add label column
        df['label'] = label
        df['attack_type'] = 'extraction_attack'
        df['symbol'] = 'LUNCBTC'
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        
        # Import to spot_trade_history table
        df.to_sql('spot_trade_history', conn, if_exists='append', index=False)
        
        print(f"✓ Imported {len(df)} records to spot_trade_history table")
        
        # Verify import
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM spot_trade_history WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        print(f"✓ Verified: {count} total records for user {user_id} in database")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Error importing data: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 70)
    print("IMPORT LUNCBTC EXTRACTION ATTACK DATA")
    print("=" * 70)
    print("\nThis will import data to spot_trade_history table:")
    print("  Victim:   User 1445939 (Extraction_Attack_case1/1445939.xlsx)")
    print("  Attacker: User 4866868 (Extraction_Attack_case1/4866868.xlsx)")
    print("  Symbol:   LUNCBTC")
    print()
    
    # Database path
    db_path = "trading_analysis.db"
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"✗ Database not found: {db_path}")
        print("Please specify the correct database path.")
        return
    
    print(f"Using database: {db_path}\n")
    
    # Import victim data
    print("-" * 70)
    print("IMPORTING VICTIM DATA")
    print("-" * 70)
    
    victim_success = import_excel_to_spot_table(
        db_path=db_path,
        excel_file="Extraction_Attack_case1/1445939.xlsx",
        user_id="1445939",
        label="victim"
    )
    
    if not victim_success:
        print("\n✗ Failed to import victim data")
        return
    
    # Import attacker data
    print("\n" + "-" * 70)
    print("IMPORTING ATTACKER DATA")
    print("-" * 70)
    
    attacker_success = import_excel_to_spot_table(
        db_path=db_path,
        excel_file="Extraction_Attack_case1/4866868.xlsx",
        user_id="4866868",
        label="attacker"
    )
    
    if not attacker_success:
        print("\n✗ Failed to import attacker data")
        return
    
    # Summary
    print("\n" + "=" * 70)
    print("✓ IMPORT COMPLETE")
    print("=" * 70)
    
    # Show summary
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\nData Summary:")
    
    # Count for victim
    cursor.execute("SELECT COUNT(*) FROM spot_trade_history WHERE user_id = '1445939'")
    victim_count = cursor.fetchone()[0]
    print(f"  Victim (1445939):   {victim_count} trades")
    
    # Count for attacker
    cursor.execute("SELECT COUNT(*) FROM spot_trade_history WHERE user_id = '4866868'")
    attacker_count = cursor.fetchone()[0]
    print(f"  Attacker (4866868): {attacker_count} trades")
    
    # Total labeled records
    cursor.execute("SELECT COUNT(*) FROM spot_trade_history WHERE label IN ('victim', 'attacker')")
    total_labeled = cursor.fetchone()[0]
    print(f"  Total labeled:      {total_labeled} trades")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)
    print("\nThe data has been imported to the spot_trade_history table.")
    print("You can now use this labeled data for training models.")


if __name__ == "__main__":
    main()
