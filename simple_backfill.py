#!/usr/bin/env python3
"""
Simple Backfill Script - Direct ID-based approach
Scrapes BlockBeats (from ID 323133) and Jinse (from ID 490206)
"""
import sys
import os
sys.path.insert(0, '/Users/kabellatsang/PycharmProjects/ai_code')

import requests
from datetime import datetime, date
from bs4 import BeautifulSoup
import time

# Add parent directory to path
from scraper.core.database_manager import DatabaseManager

# Starting IDs
BLOCKBEATS_START_ID = 323133
JINSE_START_ID = 490206

# Security keywords
KEYWORDS = [
    "安全问题", "黑客", "被盗", "漏洞", "攻击", "恶意软件", "盗窃",
    "CoinEx", "ViaBTC", "破产", "执法", "监管", "洗钱", "KYC",
    "合规", "牌照", "风控", "诈骗", "突发", "rug pull", "下架"
]

def scrape_blockbeats_article(article_id):
    """Scrape a single BlockBeats article by ID"""
    url = f"https://www.theblockbeats.info/flash/{article_id}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title_elem = soup.select_one('h1.article-title, .flash-title, h1')
        title = title_elem.get_text(strip=True) if title_elem else f"BlockBeats Article {article_id}"
        
        # Extract content
        content_elem = soup.select_one('.article-content, .flash-content, .content')
        content = content_elem.get_text(strip=True) if content_elem else title
        
        # Extract date
        date_elem = soup.select_one('.article-time, .flash-time, time')
        article_date = datetime.now()
        if date_elem:
            try:
                date_str = date_elem.get_text(strip=True)
                article_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            except:
                pass
        
        return {
            'id': article_id,
            'title': title,
            'content': content,
            'date': article_date,
            'url': url
        }
    except Exception as e:
        return None

def scrape_jinse_article(article_id):
    """Scrape a single Jinse article by ID"""
    url = f"https://www.jinse.cn/lives/{article_id}.html"
    
    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title_elem = soup.select_one('h1, .live-title, .title')
        title = title_elem.get_text(strip=True) if title_elem else f"Jinse Article {article_id}"
        
        # Extract content
        content_elem = soup.select_one('.live-content, .content, article')
        content = content_elem.get_text(strip=True) if content_elem else title
        
        # Extract date
        article_date = datetime.now()
        
        return {
            'id': article_id,
            'title': title,
            'content': content,
            'date': article_date,
            'url': url
        }
    except Exception as e:
        return None

def check_keywords(text):
    """Check which keywords match the text"""
    matched = []
    text_lower = text.lower()
    for keyword in KEYWORDS:
        if keyword.lower() in text_lower:
            matched.append(keyword)
    return matched

def backfill_by_id(source, start_id, max_articles=500):
    """Backfill articles by ID range"""
    print(f"📰 Scraping {source} from ID {start_id}...")
    print()
    
    db_manager = DatabaseManager()
    
    total_checked = 0
    total_stored = 0
    total_duplicate = 0
    total_no_match = 0
    total_errors = 0
    
    current_id = start_id
    consecutive_errors = 0
    
    while total_checked < max_articles and consecutive_errors < 10:
        try:
            # Scrape article
            if source == 'BlockBeats':
                article = scrape_blockbeats_article(current_id)
            else:  # Jinse
                article = scrape_jinse_article(current_id)
            
            if not article:
                consecutive_errors += 1
                total_errors += 1
                current_id += 1
                continue
            
            consecutive_errors = 0  # Reset on success
            total_checked += 1
            
            # Check keywords
            full_text = f"{article['title']} {article['content']}"
            matched_keywords = check_keywords(full_text)
            
            if not matched_keywords:
                total_no_match += 1
                current_id += 1
                continue
            
            # Check if exists
            if db_manager.check_article_exists(article['url']):
                total_duplicate += 1
                current_id += 1
                continue
            
            # Store article
            article_data = {
                'title': article['title'],
                'url': article['url'],
                'date': article['date'],
                'source': source,
                'content': article['content'],
                'matched_keywords': matched_keywords
            }
            
            if db_manager.insert_article(article_data):
                total_stored += 1
                print(f"  ✅ [{current_id}] {article['title'][:50]}... ({', '.join(matched_keywords[:2])})")
            
            current_id += 1
            time.sleep(1)  # Be nice to servers
            
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
            break
        except Exception as e:
            total_errors += 1
            consecutive_errors += 1
            current_id += 1
            continue
    
    print()
    print(f"  📊 {source} Summary:")
    print(f"     Checked: {total_checked}, Stored: {total_stored}, Duplicate: {total_duplicate}")
    print(f"     No match: {total_no_match}, Errors: {total_errors}")
    print()
    
    return total_stored

def backfill_all():
    """Backfill from both sources"""
    print("="*60)
    print("🔄 Historical Data Backfill (ID-based)")
    print("="*60)
    print(f"📰 BlockBeats: Starting from ID {BLOCKBEATS_START_ID}")
    print(f"📰 Jinse: Starting from ID {JINSE_START_ID}")
    print("="*60)
    print()
    
    # Initialize database
    db_manager = DatabaseManager()
    
    if not db_manager.supabase:
        print("❌ Failed to connect to database")
        return False
    
    print("✅ Connected to Supabase")
    print()
    
    total_stored = 0
    
    # Backfill BlockBeats
    print("1️⃣  BlockBeats")
    print("-" * 60)
    stored = backfill_by_id('BlockBeats', BLOCKBEATS_START_ID, max_articles=500)
    total_stored += stored
    
    # Backfill Jinse
    print("2️⃣  Jinse")
    print("-" * 60)
    stored = backfill_by_id('Jinse', JINSE_START_ID, max_articles=500)
    total_stored += stored
    
    print("="*60)
    print("📊 Total Backfill Summary")
    print("="*60)
    print(f"💾 Total articles stored: {total_stored}")
    print("="*60)
    print()
    
    if total_stored > 0:
        print(f"✅ Successfully backfilled {total_stored} articles!")
        print()
        print("🌐 View them at:")
        print("   https://crypto-news-scraper.onrender.com/dashboard")
    else:
        print("⚠️  No new articles were stored.")
    
    return total_stored > 0

if __name__ == "__main__":
    print()
    print("🚀 ID-Based Backfill Script")
    print()
    print(f"This will scrape:")
    print(f"  - BlockBeats from ID {BLOCKBEATS_START_ID}")
    print(f"  - Jinse from ID {JINSE_START_ID}")
    print()
    print("And store articles matching security keywords.")
    print()
    
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("❌ Cancelled")
        sys.exit(0)
    
    print()
    success = backfill_all()
    
    if success:
        print("🎉 Backfill complete!")
        sys.exit(0)
    else:
        print("❌ Backfill failed or no data stored")
        sys.exit(1)
