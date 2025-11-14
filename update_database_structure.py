"""
Update Database Structure to Match Excel Format

This script:
1. Backs up existing data
2. Drops old futures_trades_history table
3. Creates new table matching Excel columns exactly
4. Re-imports data with correct mapping
"""

import sqlite3
import shutil
from datetime import datetime


def backup_database(db_path='trading_data.db'):
    """Create a backup of the database"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'trading_data_backup_{timestamp}.db'
    shutil.copy2(db_path, backup_path)
    print(f"✓ Backup created: {backup_path}")
    return backup_path


def update_futures_trades_history_structure(conn):
    """Update futures_trades_history table to match Excel format"""
    print("\n" + "=" * 80)
    print("UPDATING TABLE STRUCTURE")
    print("=" * 80)
    
    cursor = conn.cursor()
    
    # Drop old table
    cursor.execute("DROP TABLE IF EXISTS futures_trades_history")
    print("✓ Dropped old futures_trades_history table")
    
    # Create new table matching Excel format
    cursor.execute('''
        CREATE TABLE futures_trades_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            open_time TIMESTAMP NOT NULL,
            close_time TIMESTAMP NOT NULL,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            avg_entry_price REAL,
            entry_price REAL NOT NULL,
            exit_price REAL NOT NULL,
            close_type TEXT,
            max_qty REAL NOT NULL,
            max_notional REAL,
            realized_pnl REAL,
            fees REAL,
            funding_fee REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    print("✓ Created new futures_trades_history table")
    
    # Create indexes
    cursor.execute('CREATE INDEX idx_futures_history_user ON futures_trades_history(user_id)')
    cursor.execute('CREATE INDEX idx_futures_history_symbol ON futures_trades_history(symbol)')
    cursor.execute('CREATE INDEX idx_futures_history_open_time ON futures_trades_history(open_time)')
    cursor.execute('CREATE INDEX idx_futures_history_close_time ON futures_trades_history(close_time)')
    print("✓ Created indexes")
    
    conn.commit()
    print("\n✓ Table structure updated successfully")


def main():
    """Main function"""
    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + "UPDATE DATABASE STRUCTURE".center(78) + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    
    db_path = 'trading_data.db'
    
    # Backup database
    print("\n" + "=" * 80)
    print("BACKING UP DATABASE")
    print("=" * 80)
    backup_path = backup_database(db_path)
    
    # Connect and update
    conn = sqlite3.connect(db_path)
    
    # Update structure
    update_futures_trades_history_structure(conn)
    
    # Show new structure
    print("\n" + "=" * 80)
    print("NEW TABLE STRUCTURE")
    print("=" * 80)
    
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(futures_trades_history)")
    columns = cursor.fetchall()
    
    print("\nfutures_trades_history columns:")
    for col in columns:
        print(f"  {col[1]:20s} {col[2]:10s} {'NOT NULL' if col[3] else ''}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("UPDATE COMPLETE")
    print("=" * 80)
    print("\nNext step: Run import_futures_data.py to load data with new structure")
    print(f"Backup saved at: {backup_path}")


if __name__ == "__main__":
    main()
