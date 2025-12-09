#!/usr/bin/env python3
"""Upload CSV using direct SQL instead of REST API"""
import sys
import os
sys.path.insert(0, '/Users/kabellatsang/PycharmProjects/ai_code')

import csv
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse

load_dotenv()

print("="*60)
print("📤 Upload CSV via Direct SQL Connection")
print("="*60)
print()
print("⚠️  You need the database connection string from Supabase.")
print()
print("To get it:")
print("1. Go to Supabase Dashboard → Settings → Database")
print("2. Find 'Connection string' section")
print("3. Copy the 'URI' connection string")
print("4. Replace [YOUR-PASSWORD] with your actual password")
print()
print("Example:")
print("postgresql://postgres.xxx:[PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres")
print()

db_url = input("Paste your connection string here: ").strip()

if not db_url:
    print("❌ Connection string required")
    sys.exit(1)

csv_file = "/Users/kabellatsang/PycharmProjects/ai_code/crypto_news_20251205_072237.csv"

try:
    print("\n🔌 Connecting to database...")
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    print("✅ Connected!")
    print()
    
    total_rows = 0
    total_inserted = 0
    total_skipped = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            total_rows += 1
            
            try:
                # Parse keywords
                keywords = [k.strip() for k in row['matched_keywords'].split(',') if k.strip()]
                
                # Check if exists
                cursor.execute("SELECT id FROM articles WHERE url = %s", (row['url'],))
                if cursor.fetchone():
                    total_skipped += 1
                    continue
                
                # Insert
                cursor.execute("""
                    INSERT INTO articles (publication_date, title, body_text, url, source, matched_keywords)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    row['publication_date'],
                    row['title'],
                    row['body_text'],
                    row['url'],
                    row['source'],
                    keywords
                ))
                
                total_inserted += 1
                print(f"  ✅ [{total_inserted}] {row['title'][:60]}...")
                
            except Exception as e:
                print(f"  ❌ Error on row {total_rows}: {e}")
                continue
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print()
    print("="*60)
    print("📊 Upload Summary")
    print("="*60)
    print(f"📄 Total rows: {total_rows}")
    print(f"💾 Articles inserted: {total_inserted}")
    print(f"🔄 Duplicates skipped: {total_skipped}")
    print("="*60)
    print()
    print("✅ Upload complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
