#!/usr/bin/env python3
"""
Daily News Scraper - Runs automatically to scrape latest news
Scrapes BlockBeats and Jinse, saves directly to Supabase
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
from datetime import datetime
from bs4 import BeautifulSoup
import time
from scraper.core.database_manager import DatabaseManager

# Security keywords
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

def scrape_blockbeats_latest(num_articles=50):
    """Scrape latest BlockBeats articles"""
    articles = []
    start_id = 323133  # Starting point
    
    print(f"🔍 Scraping BlockBeats (latest {num_articles} articles)...")
    
    for i in range(num_articles):
        article_id = start_id + i
        url = f"https://www.theblockbeats.info/flash/{article_id}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title_elem = soup.select_one('h1')
            title = title_elem.get_text(strip=True) if title_elem else f"Article {article_id}"
            
            content_elem = soup.select_one('.content, .article-content')
            content = content_elem.get_text(strip=True) if content_elem else title
            
            # Check keywords
            full_text = f"{title} {content}"
            matched_keywords = check_keywords(full_text)
            
            if matched_keywords:
                articles.append({
                    'date': datetime.now().strftime('%Y/%m/%d'),
                    'title': title,
                    'body_text': content,
                    'url': url,
                    'source': 'blockbeat',
                    'matched_keywords': matched_keywords
                })
                print(f"  ✅ Found: {title[:50]}... ({', '.join(matched_keywords[:2])})")
            
            time.sleep(0.5)  # Be nice to the server
            
        except Exception as e:
            continue
    
    return articles

def scrape_jinse_latest(num_articles=50):
    """Scrape latest Jinse articles"""
    articles = []
    start_id = 490206  # Starting point
    
    print(f"🔍 Scraping Jinse (latest {num_articles} articles)...")
    
    for i in range(num_articles):
        article_id = start_id + i
        url = f"https://www.jinse.cn/lives/{article_id}.html"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title_elem = soup.select_one('h1, .title')
            title = title_elem.get_text(strip=True) if title_elem else f"Jinse {article_id}"
            
            content_elem = soup.select_one('.content, .article-content')
            content = content_elem.get_text(strip=True) if content_elem else title
            
            # Check keywords
            full_text = f"{title} {content}"
            matched_keywords = check_keywords(full_text)
            
            if matched_keywords:
                articles.append({
                    'date': datetime.now().strftime('%Y/%m/%d'),
                    'title': title,
                    'body_text': content,
                    'url': url,
                    'source': 'jinse',
                    'matched_keywords': matched_keywords
                })
                print(f"  ✅ Found: {title[:50]}... ({', '.join(matched_keywords[:2])})")
            
            time.sleep(0.5)
            
        except Exception as e:
            continue
    
    return articles

def run_daily_scrape():
    """Run the daily scraping job"""
    print("="*60)
    print(f"🤖 Daily News Scraper - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print()
    
    # Initialize database
    db = DatabaseManager()
    if not db.supabase:
        print("❌ Failed to connect to database")
        return
    
    print("✅ Connected to database")
    print()
    
    # Scrape from both sources
    all_articles = []
    all_articles.extend(scrape_blockbeats_latest(50))
    all_articles.extend(scrape_jinse_latest(50))
    
    print()
    print(f"📰 Total articles found: {len(all_articles)}")
    print()
    
    # Save to database
    saved = 0
    duplicates = 0
    
    for article in all_articles:
        if db.insert_article(article):
            saved += 1
        else:
            duplicates += 1
    
    print()
    print("="*60)
    print("📊 Summary")
    print("="*60)
    print(f"📰 Articles found: {len(all_articles)}")
    print(f"💾 Saved to database: {saved}")
    print(f"🔄 Duplicates skipped: {duplicates}")
    print("="*60)
    print()
    
    if saved > 0:
        print("✅ Daily scrape complete!")
    else:
        print("⚠️  No new articles saved")

if __name__ == "__main__":
    run_daily_scrape()
