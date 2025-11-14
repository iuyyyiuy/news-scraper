#!/usr/bin/env python3
"""
Simple News Scraper for BlockBeats
A standalone script version that can be run anywhere.

Usage:
    python simple_scraper.py

Then follow the prompts to configure your scraping session.
"""

import requests
import csv
import time
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Article:
    """Represents a scraped news article."""
    url: str
    title: str
    publication_date: Optional[datetime]
    author: Optional[str]
    body_text: str
    scraped_at: datetime
    source_website: str
    matched_keywords: Optional[List[str]] = None


def fetch_url(url: str, timeout: int = 30, max_retries: int = 3) -> str:
    """Fetch URL with retry logic."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; NewsScraperBot/1.0)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise e


def extract_article_urls(html: str, base_url: str) -> List[str]:
    """Extract article URLs from listing page."""
    from urllib.parse import urljoin
    soup = BeautifulSoup(html, 'lxml')
    article_urls = []
    
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        if re.match(r'^/flash/\d+$', href):
            absolute_url = urljoin(base_url, href)
            if absolute_url not in article_urls:
                article_urls.append(absolute_url)
    
    return article_urls


def extract_date_from_body(body_text: str) -> Optional[datetime]:
    """Extract date from body text patterns."""
    pattern = r'BlockBeats\s*消息\s*，\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日'
    match = re.search(pattern, body_text)
    if match:
        month = int(match.group(1))
        day = int(match.group(2))
        year = datetime.now().year
        try:
            return datetime(year, month, day)
        except ValueError:
            pass
    return None


def parse_article(html: str, url: str) -> Article:
    """Parse article from HTML."""
    soup = BeautifulSoup(html, 'lxml')
    
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else "No Title"
    
    author = "@BlockBeats"
    
    body_element = soup.select_one('.flash-top, .flash-top-border')
    if body_element:
        for unwanted in body_element.select('script, style, nav, header, footer'):
            unwanted.decompose()
        body_text = body_element.get_text(separator=' ', strip=True)
    else:
        body_text = ""
    
    if not body_text or len(body_text) < 50:
        raise ValueError("Could not extract article body")
    
    # Extract content starting from "BlockBeats 消息" and remove footer
    # Use simple string find for better reliability
    blockbeats_marker = 'BlockBeats 消息'
    blockbeats_pos = body_text.find(blockbeats_marker)
    
    if blockbeats_pos != -1:
        # Start from BlockBeats 消息
        body_text = body_text[blockbeats_pos:]
        
        # Remove footer content - find the earliest footer marker
        footer_markers = [
            'AI 解读',
            '展开',
            '原文链接',
            '举报',
            '纠错/举报',
            '本平台现已全面集成',
            '热门文章'
        ]
        
        earliest_pos = len(body_text)
        for marker in footer_markers:
            pos = body_text.find(marker)
            if pos != -1 and pos < earliest_pos:
                earliest_pos = pos
        
        # Cut at the earliest footer marker
        if earliest_pos < len(body_text):
            body_text = body_text[:earliest_pos]
    
    body_text = body_text.strip()
    
    publication_date = extract_date_from_body(body_text)
    
    return Article(
        url=url,
        title=title,
        publication_date=publication_date,
        author=author,
        body_text=body_text,
        scraped_at=datetime.now(),
        source_website="www.theblockbeats.info"
    )


def should_save_article(article: Article, days_filter: Optional[int], keywords_filter: Optional[List[str]]) -> bool:
    """Check if article passes filters."""
    if days_filter is not None and article.publication_date:
        cutoff_date = datetime.now() - timedelta(days=days_filter)
        if article.publication_date < cutoff_date:
            return False
    
    if keywords_filter:
        article_text = f"{article.title} {article.body_text}".lower()
        matched = [kw for kw in keywords_filter if kw.lower() in article_text]
        
        if not matched:
            return False
        
        article.matched_keywords = matched
    
    return True


def save_to_csv(articles: List[Article], filename: str):
    """Save articles to CSV file."""
    fieldnames = ['publication_date', 'title', 'body_text', 'url', 'matched_keywords']
    
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        
        for article in articles:
            row = {
                'publication_date': article.publication_date.strftime('%Y-%m-%d') if article.publication_date else '',
                'title': article.title,
                'body_text': article.body_text,
                'url': article.url,
                'matched_keywords': ', '.join(article.matched_keywords) if article.matched_keywords else ''
            }
            writer.writerow(row)


def main():
    """Main function with interactive prompts."""
    print("\n" + "="*70)
    print("📰 NEWS SCRAPER FOR BLOCKBEATS")
    print("="*70 + "\n")
    
    # Get configuration from user
    target_url = "https://www.theblockbeats.info/newsflash"
    
    max_articles = input("How many articles to scrape? (default: 20): ").strip()
    max_articles = int(max_articles) if max_articles else 20
    
    keywords_input = input("Enter keywords (comma-separated, e.g., BTC,ETH,监管): ").strip()
    keywords = [k.strip() for k in keywords_input.split(',')] if keywords_input else []
    
    days_input = input("Filter by last N days? (press Enter to skip): ").strip()
    days_filter = int(days_input) if days_input else None
    
    # Generate default filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"crypto_news_{timestamp}.csv"
    
    output_file = input(f"Output filename (default: {default_filename}): ").strip()
    output_file = output_file if output_file else default_filename
    
    print(f"\n{'='*70}")
    print("CONFIGURATION")
    print(f"{'='*70}")
    print(f"Target URL:      {target_url}")
    print(f"Max Articles:    {max_articles}")
    print(f"Keywords:        {', '.join(keywords) if keywords else 'None (all articles)'}")
    print(f"Date Filter:     Last {days_filter} days" if days_filter else "Date Filter:     Disabled")
    print(f"Output File:     {output_file}")
    print(f"{'='*70}\n")
    
    input("Press Enter to start scraping...")
    
    start_time = time.time()
    articles_scraped = []
    articles_failed = 0
    
    try:
        print("\n📡 Fetching article listing page...")
        html = fetch_url(target_url)
        
        print("🔍 Extracting article URLs...")
        article_urls = extract_article_urls(html, target_url)
        print(f"✅ Found {len(article_urls)} article URLs")
        
        article_urls = article_urls[:max_articles]
        print(f"📝 Processing {len(article_urls)} articles\n")
        
        for index, article_url in enumerate(article_urls, 1):
            try:
                print(f"[{index}/{len(article_urls)}] {article_url}")
                
                article_html = fetch_url(article_url)
                article = parse_article(article_html, article_url)
                
                if should_save_article(article, days_filter, keywords):
                    articles_scraped.append(article)
                    print(f"   ✅ {article.title[:60]}...")
                else:
                    print(f"   ⏭️  Filtered out")
                
                if index < len(article_urls):
                    time.sleep(2.0)
                    
            except Exception as e:
                articles_failed += 1
                print(f"   ❌ Error: {str(e)}")
        
        if articles_scraped:
            print(f"\n💾 Saving {len(articles_scraped)} articles to {output_file}...")
            save_to_csv(articles_scraped, output_file)
        
        duration = time.time() - start_time
        print(f"\n{'='*70}")
        print("📊 SUMMARY")
        print(f"{'='*70}")
        print(f"Articles Found:    {len(article_urls)}")
        print(f"Articles Scraped:  {len(articles_scraped)}")
        print(f"Articles Failed:   {articles_failed}")
        print(f"Duration:          {duration:.2f} seconds")
        print(f"{'='*70}\n")
        
        if articles_scraped:
            print(f"✅ Successfully scraped {len(articles_scraped)} article(s)!")
            print(f"📄 Results saved to: {output_file}\n")
        else:
            print("⚠️  No articles matched your filters\n")
            
    except Exception as e:
        print(f"\n❌ Fatal error: {e}\n")
        raise


if __name__ == "__main__":
    main()
