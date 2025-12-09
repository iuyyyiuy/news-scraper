#!/usr/bin/env python3
"""
Cleanup Database Script
1. Delete test articles
2. Update date format to DATE type (YYYY-MM-DD only, no timestamp)
"""
import sys
sys.path.insert(0, '/Users/kabellatsang/PycharmProjects/ai_code')

from scraper.core.database_manager import DatabaseManager

print("="*60)
print("🧹 Database Cleanup")
print("="*60)
print()

# Initialize
db_manager = DatabaseManager()

if not db_manager.supabase:
    print("❌ Failed to connect to Supabase")
    sys.exit(1)

print("✅ Connected to Supabase")
print()

# Step 1: Delete test article
print("1️⃣  Deleting test article...")
try:
    # Delete the test article (source = 'Test')
    response = db_manager.supabase.table('articles').delete().eq('source', 'Test').execute()
    print(f"   ✅ Deleted test articles")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Step 2: Update date column type in Supabase
print("2️⃣  Date format information:")
print("   The 'date' column is currently TIMESTAMP type")
print("   To change it to DATE type (YYYY-MM-DD only):")
print()
print("   Go to Supabase Dashboard:")
print("   1. Open https://supabase.com/dashboard")
print("   2. Select your project")
print("   3. Go to 'SQL Editor'")
print("   4. Run this SQL:")
print()
print("   " + "-"*50)
print("   ALTER TABLE articles")
print("   ALTER COLUMN date TYPE DATE;")
print("   " + "-"*50)
print()
print("   This will convert all timestamps to dates (YYYY-MM-DD)")
print()

print("="*60)
print("✅ Cleanup Complete!")
print("="*60)
print()
print("Next: Run the SQL command above in Supabase to change date format")
