"""
Enhanced scraper that continues scraping until reaching a date cutoff.
Scrapes articles by sequential IDs going backwards in time.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional
import csv
import time
import re


@dataclass
class Article:
    url: str
    title: str
    publication_date: Optional[datetime]
    author: Optional[str]
    body_text: str
    scraped_at: datetime
    source_website: str
    matched_keywords: List[str] = None


def fetch_article(url: str, session: requests.Session) -> str:
    """Fetch article HTML."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = session.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def extract_date_from_body(body_text: str) -> Optional[datetime]:
    """Extract date from body text."""
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
    
    # Extract title
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else "No Title"
    
    # Extract body text
    body_element = soup.select_one('.flash-top, .flash-top-border')
    if body_element:
        for unwanted in body_element.select('script, style, nav, header, footer'):
            unwanted.decompose()
        body_text = body_element.get_text(separator=' ', strip=True)
    else:
        body_text = ""
    
    if not body_text or len(body_text) < 50:
        raise ValueError("Could not extract article body")
    
    # Extract content starting from "BlockBeats 消息"
    blockbeats_marker = 'BlockBeats 消息'
    blockbeats_pos = body_text.find(blockbeats_marker)
    
    if blockbeats_pos != -1:
        body_text = body_text[blockbeats_pos:]
        
        # Remove footer content
        footer_markers = ['AI 解读', '展开', '原文链接', '举报', '纠错/举报', '本平台现已全面集成', '热门文章']
        earliest_pos = len(body_text)
        for marker in footer_markers:
            pos = body_text.find(marker)
            if pos != -1 and pos < earliest_pos:
                earliest_pos = pos
        
        if earliest_pos < len(body_text):
            body_text = body_text[:earliest_pos]
    
    body_text = body_text.strip()
    publication_date = extract_date_from_body(body_text)
    
    return Article(
        url=url,
        title=title,
        publication_date=publication_date,
        author="@BlockBeats",
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


def scrape_by_date_range(start_id: int, days_back: int, keywords: List[str], output_file: str, max_articles: int = 1000):
    """
    Scrape articles going backwards from start_id until reaching the date cutoff.
    
    Args:
        start_id: Starting article ID (e.g., 320007 for latest)
        days_back: How many days back to scrape
        keywords: List of keywords to filter
        output_file: Output CSV filename
        max_articles: Maximum articles to attempt (safety limit)
    """
    session = requests.Session()
    articles = []
    current_id = start_id
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    consecutive_failures = 0
    max_consecutive_failures = 10
    articles_outside_range = 0
    max_outside_range = 20  # Stop if we see 20 articles in a row outside date range
    
    print(f"\n{'='*70}")
    print(f"📰 SCRAPING ARTICLES BY DATE RANGE")
    print(f"{'='*70}")
    print(f"Starting ID:     {start_id}")
    print(f"Date cutoff:     {cutoff_date.strftime('%Y-%m-%d')} ({days_back} days back)")
    print(f"Keywords:        {', '.join(keywords) if keywords else 'None'}")
    print(f"Output file:     {output_file}")
    print(f"{'='*70}\n")
    
    for attempt in range(max_articles):
        url = f"https://www.theblockbeats.info/flash/{current_id}"
        
        try:
            print(f"[{attempt + 1}] Checking ID {current_id}...", end=" ")
            html = fetch_article(url, session)
            article = parse_article(html, url)
            
            # Check if article is within date range
            if article.publication_date and article.publication_date < cutoff_date:
                articles_outside_range += 1
                print(f"⏭️  Too old ({article.publication_date.strftime('%Y-%m-%d')})")
                
                if articles_outside_range >= max_outside_range:
                    print(f"\n✋ Reached {max_outside_range} consecutive articles outside date range. Stopping.")
                    break
            else:
                articles_outside_range = 0  # Reset counter
                
                # Check if article matches filters
                if should_save_article(article, days_back, keywords):
                    articles.append(article)
                    keywords_str = f" [{', '.join(article.matched_keywords)}]" if article.matched_keywords else ""
                    print(f"✅ {article.title[:50]}...{keywords_str}")
                else:
                    print(f"⏭️  Filtered out")
            
            consecutive_failures = 0
            time.sleep(2)  # Be respectful to the server
            
        except Exception as e:
            consecutive_failures += 1
            print(f"❌ Error: {str(e)[:50]}")
            
            if consecutive_failures >= max_consecutive_failures:
                print(f"\n✋ Too many consecutive failures ({max_consecutive_failures}). Stopping.")
                break
        
        current_id -= 1
    
    # Save results
    if articles:
        print(f"\n💾 Saving {len(articles)} articles to {output_file}...")
        save_to_csv(articles, output_file)
        print(f"✅ Done! Scraped {len(articles)} articles.")
    else:
        print("\n⚠️  No articles matched the criteria.")
    
    print(f"\n{'='*70}")
    print(f"📊 SUMMARY")
    print(f"{'='*70}")
    print(f"Articles scraped:  {len(articles)}")
    print(f"IDs checked:       {start_id - current_id}")
    print(f"{'='*70}\n")


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
    """Main function."""
    print("\n" + "="*70)
    print("📰 NEWS SCRAPER - DATE RANGE MODE")
    print("="*70 + "\n")
    
    # Get latest article ID (you can check the website for the current latest ID)
    start_id_input = input("Starting article ID (default: 320007): ").strip()
    start_id = int(start_id_input) if start_id_input else 320007
    
    days_input = input("How many days back to scrape? (default: 30): ").strip()
    days_back = int(days_input) if days_input else 30
    
    keywords_input = input("Enter keywords (comma-separated, e.g., BTC,ETH,监管): ").strip()
    keywords = [k.strip() for k in keywords_input.split(',')] if keywords_input else []
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"crypto_news_{timestamp}.csv"
    output_file = input(f"Output filename (default: {default_filename}): ").strip()
    output_file = output_file if output_file else default_filename
    
    max_articles_input = input("Maximum articles to check (default: 1000): ").strip()
    max_articles = int(max_articles_input) if max_articles_input else 1000
    
    input("\nPress Enter to start scraping...")
    
    scrape_by_date_range(start_id, days_back, keywords, output_file, max_articles)


if __name__ == "__main__":
    main()
