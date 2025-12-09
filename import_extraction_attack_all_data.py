"""
Import ALL Extraction Attack Data to spot_trade_history table

Imports all trades from victim and attacker (not just LUNCBTC).
"""

import pandas as pd
import sqlite3
from datetime import datetime
import os


def import_excel_to_spot_table(db_path, excel_file, user_id, label, attack_type="extraction_attack"):
    """
    Import ALL data from Excel file directly to spot_trade_history table
    
    Args:
        db_path: Path to SQLite database
        excel_file: Path to Excel file
        user_id: User ID
        label: 'victim' or 'attacker'
        attack_type: Type of attack
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
        
        # Display original columns
        print(f"Original columns: {list(df.columns)}")
        
        # Standardize column names (handle Chinese column names)
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
            'filled_qty.1': 'filled_qty.1',
            'avg_fill_price': 'avg_fill_price',
            'notional': 'notional',
            'status': 'status',
            'placed_by': 'placed_by',
            'advanced_settings': 'advanced_settings'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        print(f"✓ Standardized column names")
        
        # Show unique symbols
        if 'symbol' in df.columns:
            symbols = df['symbol'].unique()
            print(f"Symbols: {', '.join(map(str, symbols))}")
        
        # Add user_id if not present
        if 'user_id' not in df.columns:
            df['user_id'] = user_id
        
        # Add label and attack_type columns
        df['label'] = label
        df['attack_type'] = attack_type
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        
        # Import ALL data to spot_trade_history table
        df.to_sql('spot_trade_history', conn, if_exists='append', index=False)
        
        print(f"✓ Imported {len(df)} records to spot_trade_history table")
        
        # Verify import
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM spot_trade_history WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        print(f"✓ Verified: {count} total records for user {user_id} in database")
        
        # Show breakdown by symbol
        cursor.execute("""
            SELECT symbol, COUNT(*) as count 
            FROM spot_trade_history 
            WHERE user_id = ? 
            GROUP BY symbol 
            ORDER BY count DESC
        """, (user_id,))
        
        symbol_counts = cursor.fetchall()
        if symbol_counts:
            print(f"  Breakdown by symbol:")
            for symbol, count in symbol_counts:
                print(f"    {symbol}: {count} trades")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Error importing data: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 70)
    print("IMPORT EXTRACTION ATTACK DATA - ALL SYMBOLS")
    print("=" * 70)
    print("\nThis will import ALL trade data to spot_trade_history table:")
    print("  Victim:   User 1445939 (Extraction_Attack_case1/1445939.xlsx)")
    print("  Attacker: User 4866868 (Extraction_Attack_case1/4866868.xlsx)")
    print("  Note: Importing ALL symbols, not just LUNCBTC")
    print()
    
    # Database path
    db_path = "trading_analysis.db"
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"✗ Database not found: {db_path}")
        print("\nTrying alternative database names...")
        
        # Try other common names
        alternatives = ["trade_risk_analyzer.db", "trades.db", "trading.db"]
        for alt_db in alternatives:
            if os.path.exists(alt_db):
                db_path = alt_db
                print(f"✓ Found database: {db_path}")
                break
        else:
            print("✗ No database found. Please specify the correct database path.")
            return
    
    print(f"Using database: {db_path}\n")
    
    # Import victim data
    print("-" * 70)
    print("IMPORTING VICTIM DATA (ALL SYMBOLS)")
    print("-" * 70)
    
    victim_success = import_excel_to_spot_table(
        db_path=db_path,
        excel_file="Extraction_Attack_case1/1445939.xlsx",
        user_id="1445939",
        label="victim",
        attack_type="extraction_attack"
    )
    
    if not victim_success:
        print("\n✗ Failed to import victim data")
        return
    
    # Import attacker data
    print("\n" + "-" * 70)
    print("IMPORTING ATTACKER DATA (ALL SYMBOLS)")
    print("-" * 70)
    
    attacker_success = import_excel_to_spot_table(
        db_path=db_path,
        excel_file="Extraction_Attack_case1/4866868.xlsx",
        user_id="4866868",
        label="attacker",
        attack_type="extraction_attack"
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
    
    # Show all symbols involved
    print("\nAll Symbols in Labeled Data:")
    cursor.execute("""
        SELECT symbol, COUNT(*) as count 
        FROM spot_trade_history 
        WHERE user_id IN ('1445939', '4866868')
        GROUP BY symbol 
        ORDER BY count DESC
    """)
    
    all_symbols = cursor.fetchall()
    for symbol, count in all_symbols:
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN user_id = '1445939' THEN 1 ELSE 0 END) as victim_count,
                SUM(CASE WHEN user_id = '4866868' THEN 1 ELSE 0 END) as attacker_count
            FROM spot_trade_history 
            WHERE symbol = ?
        """, (symbol,))
        victim_cnt, attacker_cnt = cursor.fetchone()
        print(f"  {symbol}: {count} trades (victim: {victim_cnt}, attacker: {attacker_cnt})")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)
    print("\nAll data has been imported to the spot_trade_history table.")
    print("The data includes all symbols traded by both users.")
    print("You can now use this labeled data for training models.")


if __name__ == "__main__":
    main()
