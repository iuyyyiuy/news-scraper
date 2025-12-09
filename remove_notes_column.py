"""
Remove Notes Column from Users Table

This script removes the 'notes' column from the users table in both databases.
SQLite doesn't support DROP COLUMN directly, so we need to recreate the table.
"""

import sqlite3
import shutil
from pathlib import Path
from datetime import datetime


def backup_database(db_path):
    """Create a backup of the database before modification"""
    if not Path(db_path).exists():
        print(f"⚠ Database {db_path} does not exist, skipping...")
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{db_path}.backup_{timestamp}"
    shutil.copy2(db_path, backup_path)
    print(f"✓ Created backup: {backup_path}")
    return backup_path


def remove_notes_from_users(db_path):
    """Remove notes column from users table"""
    if not Path(db_path).exists():
        print(f"⚠ Database {db_path} does not exist, skipping...")
        return False
    
    print(f"\nProcessing: {db_path}")
    print("-" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("⚠ Users table does not exist in this database")
            conn.close()
            return False
        
        # Check current schema
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Current columns: {', '.join(column_names)}")
        
        if 'notes' not in column_names:
            print("✓ Notes column does not exist, nothing to remove")
            conn.close()
            return True
        
        # Get all data from users table
        cursor.execute("SELECT * FROM users")
        users_data = cursor.fetchall()
        print(f"Found {len(users_data)} users")
        
        # Determine which columns to keep (all except notes)
        columns_to_keep = [col for col in columns if col[1] != 'notes']
        column_definitions = []
        
        for col in columns_to_keep:
            col_name = col[1]
            col_type = col[2]
            col_notnull = col[3]
            col_default = col[4]
            col_pk = col[5]
            
            definition = f"{col_name} {col_type}"
            if col_pk:
                definition += " PRIMARY KEY"
            if col_notnull and not col_pk:
                definition += " NOT NULL"
            if col_default is not None:
                definition += f" DEFAULT {col_default}"
            
            column_definitions.append(definition)
        
        # Create new table without notes column
        new_columns = ', '.join(column_definitions)
        cursor.execute(f"CREATE TABLE users_new ({new_columns})")
        print("✓ Created new users table without notes column")
        
        # Copy data (excluding notes column)
        old_column_names = [col[1] for col in columns]
        notes_index = old_column_names.index('notes')
        columns_without_notes = [name for name in old_column_names if name != 'notes']
        
        for row in users_data:
            # Remove notes value from row
            row_without_notes = list(row[:notes_index]) + list(row[notes_index + 1:])
            placeholders = ', '.join(['?' for _ in row_without_notes])
            columns_str = ', '.join(columns_without_notes)
            cursor.execute(f"INSERT INTO users_new ({columns_str}) VALUES ({placeholders})", row_without_notes)
        
        print(f"✓ Copied {len(users_data)} users to new table")
        
        # Drop old table and rename new one
        cursor.execute("DROP TABLE users")
        cursor.execute("ALTER TABLE users_new RENAME TO users")
        print("✓ Replaced old users table with new one")
        
        # Verify the change
        cursor.execute("PRAGMA table_info(users)")
        new_columns = cursor.fetchall()
        new_column_names = [col[1] for col in new_columns]
        print(f"New columns: {', '.join(new_column_names)}")
        
        conn.commit()
        print("✓ Changes committed successfully")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        conn.rollback()
        conn.close()
        return False


def main():
    """Main function"""
    print("\n" + "=" * 80)
    print("REMOVE NOTES COLUMN FROM USERS TABLE")
    print("=" * 80)
    
    databases = ['trade_data.db', 'trading_data.db']
    
    print("\nThis script will:")
    print("1. Create backups of your databases")
    print("2. Remove the 'notes' column from the users table")
    print("3. Preserve all other data")
    
    # Create backups
    print("\n" + "=" * 80)
    print("CREATING BACKUPS")
    print("=" * 80)
    
    for db in databases:
        backup_database(db)
    
    # Remove notes column from each database
    print("\n" + "=" * 80)
    print("REMOVING NOTES COLUMN")
    print("=" * 80)
    
    success_count = 0
    for db in databases:
        if remove_notes_from_users(db):
            success_count += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Databases processed: {success_count}/{len(databases)}")
    print("\n✓ Operation complete!")
    print("\nBackup files have been created in case you need to restore.")


if __name__ == "__main__":
    main()
"""
Remove notes column from users table

SQLite doesn't support DROP COLUMN directly (before version 3.35.0),
so we need to recreate the table without the notes column.
"""

import sqlite3
import os


def remove_notes_column(db_path):
    """Remove notes column from users table"""
    
    if not os.path.exists(db_path):
        print(f"✗ Database not found: {db_path}")
        return False
    
    print(f"\nProcessing: {db_path}")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("✗ Users table not found in this database")
            conn.close()
            return False
        
        # Get current table structure
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print(f"Current columns: {len(columns)}")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Check if notes column exists
        has_notes = any(col[1] == 'notes' for col in columns)
        
        if not has_notes:
            print("\n✓ Notes column doesn't exist - nothing to do")
            conn.close()
            return True
        
        # Get columns without notes
        columns_without_notes = [col for col in columns if col[1] != 'notes']
        column_names = [col[1] for col in columns_without_notes]
        column_defs = [f"{col[1]} {col[2]}" + (" PRIMARY KEY" if col[5] else "") for col in columns_without_notes]
        
        print(f"\nRemoving 'notes' column...")
        
        # Create new table without notes column
        create_sql = f"CREATE TABLE users_new ({', '.join(column_defs)})"
        cursor.execute(create_sql)
        
        # Copy data from old table to new table
        copy_sql = f"INSERT INTO users_new ({', '.join(column_names)}) SELECT {', '.join(column_names)} FROM users"
        cursor.execute(copy_sql)
        
        # Drop old table
        cursor.execute("DROP TABLE users")
        
        # Rename new table to users
        cursor.execute("ALTER TABLE users_new RENAME TO users")
        
        conn.commit()
        
        # Verify the change
        cursor.execute("PRAGMA table_info(users)")
        new_columns = cursor.fetchall()
        
        print(f"\n✓ Successfully removed 'notes' column")
        print(f"New columns: {len(new_columns)}")
        for col in new_columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        conn.rollback()
        conn.close()
        return False


def main():
    """Main function"""
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + "REMOVE NOTES COLUMN FROM USERS TABLE".center(58) + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)
    
    databases = ['trading_data.db', 'trade_data.db']
    
    success_count = 0
    for db_path in databases:
        if remove_notes_column(db_path):
            success_count += 1
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Processed: {success_count}/{len(databases)} databases")
    print("\n✓ Done!")


if __name__ == "__main__":
    main()
