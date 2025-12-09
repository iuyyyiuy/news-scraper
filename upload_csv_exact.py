#!/usr/bin/env python3
"""
Upload CSV to Database - Exact CSV Structure Match
Uploads crypto_news CSV with exact column structure to Supabase
"""
import sys
import os
sys.path.insert(0, '/Users/kabellatsang/PycharmProjects/ai_code')

import csv
from datetime import datetime
from scraper.core.database_manager import DatabaseManager

def upload_csv(csv_file):
    """Upload CSV file to database with exact structure match"""
    
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return False
    
    print("="*60)
    print("📤 Uploading CSV to Database")
    print("="*60)
    print(f"📁 File: {csv_file}")
    print()
    
    # Initialize database
    db_manager = DatabaseManager()
    
    if not db_manager.supabase:
        print("❌ Failed to connect to database")
        return False
    
    print("✅ Connected to Supabase")
    print()
    
    total_rows = 0
    total_stored = 0
    total_duplicate = 0
    total_errors = 0
    
    # Read CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            total_rows += 1
            
            try:
                # Get data from CSV - exact column names
                article_data = {
                    'publication_date': row['publication_date'],
                    'title': row['title'],
                    'body_text': row['body_text'],
                    'url': row['url'],
                    'source': row['source'],
                    'matched_keywords': row['matched_keywords']
                }
                
                # Check if exists
                if db_manager.check_article_exists(article_data['url']):
                    total_duplicate += 1
                    continue
                
                # Store article
                if db_manager.insert_article(article_data):
                    total_stored += 1
                    keywords_preview = article_data['matched_keywords'][:30] if article_data['matched_keywords'] else ''
                    print(f"  ✅ [{total_stored}] {article_data['title'][:60]}... ({keywords_preview})")
                else:
                    total_errors += 1
                
            except Exception as e:
                print(f"  ❌ Error processing row {total_rows}: {e}")
                total_errors += 1
                continue
    
    print()
    print("="*60)
    print("📊 Upload Summary")
    print("="*60)
    print(f"📄 Total rows: {total_rows}")
    print(f"💾 Articles stored: {total_stored}")
    print(f"🔄 Duplicates skipped: {total_duplicate}")
    print(f"❌ Errors: {total_errors}")
    print("="*60)
    print()
    
    if total_stored > 0:
        print(f"✅ Successfully uploaded {total_stored} articles!")
    else:
        print("⚠️  No new articles were stored.")
    
    return total_stored > 0

if __name__ == "__main__":
    csv_file = "/Users/kabellatsang/PycharmProjects/ai_code/crypto_news_20251205_072237.csv"
    
    print()
    print("🚀 CSV to Database Uploader")
    print(f"📁 CSV File: {csv_file}")
    print()
    
    success = upload_csv(csv_file)
    
    if success:
        print("🎉 Upload complete!")
        sys.exit(0)
    else:
        print("❌ Upload failed or no new data")
        sys.exit(1)
