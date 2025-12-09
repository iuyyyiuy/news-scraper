#!/usr/bin/env python3
"""
Upload CSV to Database
Takes a CSV file from the scraper and uploads it to Supabase
"""
import sys
import os
sys.path.insert(0, '/Users/kabellatsang/PycharmProjects/ai_code')

import csv
from datetime import datetime
from scraper.core.database_manager import DatabaseManager

# Security keywords to match
KEYWORDS = [
    "安全问题", "黑客", "被盗", "漏洞", "攻击", "恶意软件", "盗窃",
    "CoinEx", "ViaBTC", "破产", "执法", "监管", "洗钱", "KYC",
    "合规", "牌照", "风控", "诈骗", "突发", "rug pull", "下架"
]

def check_keywords(text):
    """Check which keywords match the text"""
    matched = []
    text_lower = text.lower()
    for keyword in KEYWORDS:
        if keyword.lower() in text_lower:
            matched.append(keyword)
    return matched

def upload_csv(csv_file):
    """Upload CSV file to database"""
    
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
    total_no_match = 0
    
    # Read CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            total_rows += 1
            
            try:
                # Get data from CSV - try multiple column name variations
                title = row.get('title', row.get('Title', ''))
                url = row.get('url', row.get('URL', ''))
                date_str = row.get('publication_date', row.get('date', row.get('Date', '')))
                source = row.get('source', row.get('Source', 'Unknown'))
                content = row.get('content', row.get('Content', title))
                
                if not title or not url:
                    print(f"  ⚠️  Skipping row {total_rows}: Missing title or URL")
                    continue
                
                # Parse date - handle multiple formats
                try:
                    # Try with time first
                    article_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                except:
                    try:
                        # Try date only
                        article_date = datetime.strptime(date_str, '%Y-%m-%d')
                    except:
                        try:
                            # Try with Chinese format
                            article_date = datetime.strptime(date_str, '%Y年%m月%d日')
                        except:
                            # Default to now
                            article_date = datetime.now()
                
                # Format date as YYYY-MM-DD for storage
                article_date = article_date.replace(hour=0, minute=0, second=0, microsecond=0)
                
                # Check keywords
                full_text = f"{title} {content}"
                matched_keywords = check_keywords(full_text)
                
                if not matched_keywords:
                    total_no_match += 1
                    continue
                
                # Check if exists
                if db_manager.check_article_exists(url):
                    total_duplicate += 1
                    continue
                
                # Store article
                article_data = {
                    'title': title,
                    'url': url,
                    'date': article_date,
                    'source': source,
                    'content': content,
                    'matched_keywords': matched_keywords
                }
                
                if db_manager.insert_article(article_data):
                    total_stored += 1
                    print(f"  ✅ [{total_stored}] {title[:60]}... ({', '.join(matched_keywords[:2])})")
                
            except Exception as e:
                print(f"  ❌ Error processing row {total_rows}: {e}")
                continue
    
    print()
    print("="*60)
    print("📊 Upload Summary")
    print("="*60)
    print(f"📄 Total rows: {total_rows}")
    print(f"💾 Articles stored: {total_stored}")
    print(f"🔄 Duplicates skipped: {total_duplicate}")
    print(f"⚪ No keyword match: {total_no_match}")
    print("="*60)
    print()
    
    if total_stored > 0:
        print(f"✅ Successfully uploaded {total_stored} articles!")
        print()
        print("🌐 View at: https://crypto-news-scraper.onrender.com/dashboard")
    else:
        print("⚠️  No articles were stored.")
    
    return total_stored > 0

if __name__ == "__main__":
    print()
    print("🚀 CSV to Database Uploader")
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python upload_csv_to_database.py <csv_file>")
        print()
        print("Example:")
        print("  python upload_csv_to_database.py crypto_news.csv")
        print()
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    print(f"📁 CSV File: {csv_file}")
    print()
    
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("❌ Cancelled")
        sys.exit(0)
    
    print()
    success = upload_csv(csv_file)
    
    if success:
        print("🎉 Upload complete!")
        sys.exit(0)
    else:
        print("❌ Upload failed")
        sys.exit(1)
