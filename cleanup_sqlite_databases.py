#!/usr/bin/env python3
"""
Clean up SQLite databases that are causing locks
The news scraper should ONLY use Supabase
"""
import os
import glob
import shutil
from datetime import datetime

def cleanup_sqlite_databases():
    """Remove SQLite databases that shouldn't be used by news scraper"""
    print("🧹 Cleaning up SQLite databases...")
    print("=" * 50)
    
    # List of SQLite databases that might be causing locks
    sqlite_patterns = [
        "*.db",
        "*.sqlite",
        "*.sqlite3",
        "**/*.db",
        "**/*.sqlite",
        "**/*.sqlite3"
    ]
    
    # Databases that are definitely not needed for news scraper
    unwanted_dbs = [
        "trading_analysis.db",
        "trade_risk_analyzer.db",
        "trading_data.db",
        "trades.db",
        "btc_orderbook.db",
        "news.db"  # Should use Supabase instead
    ]
    
    found_databases = []
    
    # Find all SQLite databases
    for pattern in sqlite_patterns:
        for db_file in glob.glob(pattern, recursive=True):
            if os.path.isfile(db_file):
                found_databases.append(db_file)
    
    if not found_databases:
        print("✅ No SQLite databases found")
        return
    
    print(f"📊 Found {len(found_databases)} SQLite database(s):")
    for db in found_databases:
        size = os.path.getsize(db) / 1024 / 1024  # MB
        print(f"   📁 {db} ({size:.2f} MB)")
    
    print()
    
    # Create backup directory
    backup_dir = f"sqlite_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Move unwanted databases to backup
    moved_count = 0
    for db_file in found_databases:
        db_name = os.path.basename(db_file)
        
        # Check if this database should be removed
        should_remove = any(unwanted in db_name.lower() for unwanted in unwanted_dbs)
        
        if should_remove:
            try:
                backup_path = os.path.join(backup_dir, db_name)
                shutil.move(db_file, backup_path)
                print(f"📦 Moved {db_file} → {backup_path}")
                moved_count += 1
            except Exception as e:
                print(f"❌ Failed to move {db_file}: {e}")
        else:
            print(f"⏭️  Keeping {db_file} (might be needed)")
    
    print()
    print(f"✅ Moved {moved_count} SQLite database(s) to backup")
    
    if moved_count > 0:
        print(f"📦 Backup location: {backup_dir}")
        print("💡 You can delete the backup folder if everything works correctly")
    
    print()
    print("🔍 Remaining databases:")
    remaining = [db for db in found_databases if os.path.exists(db)]
    if remaining:
        for db in remaining:
            print(f"   📁 {db}")
    else:
        print("   ✅ No SQLite databases remaining")
    
    print()
    print("🎯 News scraper should now use ONLY Supabase database")

def check_processes():
    """Check for any running processes that might be using SQLite"""
    print("\n🔍 Checking for processes that might use SQLite...")
    
    import subprocess
    try:
        # Check for Python processes
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        python_processes = [line for line in lines if 'python' in line.lower() and 'grep' not in line]
        
        if python_processes:
            print(f"📊 Found {len(python_processes)} Python process(es):")
            for proc in python_processes[:5]:  # Show first 5
                print(f"   🐍 {proc[:100]}...")
        else:
            print("✅ No Python processes found")
            
    except Exception as e:
        print(f"⚠️  Could not check processes: {e}")

if __name__ == "__main__":
    cleanup_sqlite_databases()
    check_processes()
    
    print("\n" + "=" * 50)
    print("🚀 Next steps:")
    print("1. Start the news scraper: python3 start_news_scraper_only.py")
    print("2. Test manual update: https://crypto-news-scraper.onrender.com/dashboard")
    print("3. Verify no more 'database is locked' errors")
    print("=" * 50)