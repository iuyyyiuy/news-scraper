"""
Scheduled Scraper for News Database Feature
Automatically scrapes news based on predefined keywords
"""
from datetime import datetime, date, timedelta
from typing import List, Dict
from .database_manager import DatabaseManager
from .multi_source_scraper import MultiSourceScraper
from scraper.core import Config
from scraper.core.storage import CSVDataStore
import tempfile
import os


class ScheduledScraper:
    """Handles automated daily scraping of security-related news"""
    
    # Fixed keywords for security-related news
    KEYWORDS = [
        "安全问题", "黑客", "被盗", "漏洞", "攻击", "恶意软件", "盗窃",
        "CoinEx", "ViaBTC", "破产", "执法", "监管", "洗钱", "KYC",
        "合规", "牌照", "风控", "诈骗", "突发", "rug pull", "下架"
    ]
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        # Create a temporary directory for CSV storage (we won't use it, but MultiSourceScraper needs it)
        self.temp_dir = tempfile.mkdtemp()
        
    def _create_scraper(self, keyword: str) -> MultiSourceScraper:
        """Create a MultiSourceScraper instance for a specific keyword"""
        # Create config
        config = Config(
            target_url="https://www.theblockbeats.info/newsflash",
            max_articles=50,
            request_delay=2.0,
            timeout=30,
            max_retries=3
        )
        
        # Create temporary data store
        temp_file = os.path.join(self.temp_dir, f"temp_{keyword}.csv")
        data_store = CSVDataStore(temp_file)
        
        # Date range: last 24 hours
        end_date = date.today()
        start_date = end_date - timedelta(days=1)
        
        # Create scraper - only BlockBeats for scheduled runs
        scraper = MultiSourceScraper(
            config=config,
            data_store=data_store,
            start_date=start_date,
            end_date=end_date,
            keywords_filter=[keyword],
            sources=['blockbeats'],  # Only BlockBeats to avoid Jinse 404 errors
            enable_deduplication=True
        )
        
        return scraper
    
    def scrape_daily(self) -> Dict[str, any]:
        """
        Execute daily scraping for all keywords
        Scrapes latest 500 articles once and filters by all keywords
        
        Returns:
            Dictionary with scraping results
        """
        print(f"\n{'='*60}")
        print(f"🤖 Starting scheduled scrape at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        results = {
            'start_time': datetime.now(),
            'keywords_processed': 0,
            'articles_found': 0,
            'articles_stored': 0,
            'articles_duplicate': 0,
            'errors': []
        }
        
        # Scrape once with all keywords (more efficient)
        try:
            print(f"\n🔍 Scraping latest 500 articles with {len(self.KEYWORDS)} keywords")
            
            # Create config for bulk scraping
            config = Config(
                target_url="https://www.theblockbeats.info/newsflash",
                max_articles=500,
                request_delay=2.0,
                timeout=30,
                max_retries=3
            )
            
            temp_file = os.path.join(self.temp_dir, "temp_daily.csv")
            data_store = CSVDataStore(temp_file)
            
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            # Create scraper with all keywords at once
            scraper = MultiSourceScraper(
                config=config,
                data_store=data_store,
                start_date=start_date,
                end_date=end_date,
                keywords_filter=self.KEYWORDS,  # All keywords at once
                sources=['blockbeats'],
                enable_deduplication=True
            )
            
            # Run scraper
            scraper.scrape()
            articles = data_store.get_all_articles()
            
            results['articles_found'] = len(articles)
            results['keywords_processed'] = len(self.KEYWORDS)
            
            # Store each article
            for article in articles:
                # Find which keywords matched
                matched_keywords = [kw for kw in self.KEYWORDS if kw in article.title or kw in article.content]
                
                if self._store_article(article, matched_keywords):
                    results['articles_stored'] += 1
                else:
                    results['articles_duplicate'] += 1
            
            print(f"  ✅ Found: {results['articles_found']}, Stored: {results['articles_stored']}, Duplicate: {results['articles_duplicate']}")
            
        except Exception as e:
            error_msg = f"Error during scraping: {e}"
            print(f"❌ {error_msg}")
            results['errors'].append(error_msg)
        
        results['end_time'] = datetime.now()
        results['duration'] = (results['end_time'] - results['start_time']).total_seconds()
        
        self._log_results(results)
        return results
    
    def _scrape_keyword(self, keyword: str) -> Dict[str, int]:
        """
        Scrape news for a single keyword
        
        Args:
            keyword: Keyword to search for
        
        Returns:
            Dictionary with counts
        """
        result = {
            'found': 0,
            'stored': 0,
            'duplicate': 0
        }
        
        try:
            # Create scraper for this keyword
            scraper = self._create_scraper(keyword)
            
            # Scrape from all sources
            scraper.scrape()
            
            # Get articles from the data store
            articles = scraper.data_store.get_all_articles()
            
            result['found'] = len(articles)
            
            # Store each article
            for article in articles:
                if self._store_article(article, [keyword]):
                    result['stored'] += 1
                else:
                    result['duplicate'] += 1
            
            print(f"  ✅ Found: {result['found']}, Stored: {result['stored']}, Duplicate: {result['duplicate']}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            raise
        
        return result
    
    def _store_article(self, article, matched_keywords: List[str]) -> bool:
        """
        Store article in database
        
        Args:
            article: Article data from scraper
            keyword: Keyword that matched this article
        
        Returns:
            True if stored, False if duplicate
        """
        try:
            # Check if article already exists
            if self.db_manager.check_article_exists(article['url']):
                # Article exists, could update keywords here if needed
                return False
            
            # Prepare article data - match CSV structure
            pub_date = article.date if hasattr(article, 'date') else article.publication_date
            if hasattr(pub_date, 'strftime'):
                pub_date_str = pub_date.strftime('%Y/%m/%d')
            else:
                pub_date_str = str(pub_date)
            
            article_data = {
                'publication_date': pub_date_str,
                'title': article.title,
                'body_text': article.content if hasattr(article, 'content') else article.title,
                'url': article.url,
                'source': article.source,
                'matched_keywords': matched_keywords
            }
            
            # Insert into database
            return self.db_manager.insert_article(article_data)
            
        except Exception as e:
            print(f"  ❌ Error storing article: {e}")
            return False
    
    def _log_results(self, results: Dict):
        """Log scraping results summary"""
        print(f"\n{'='*60}")
        print(f"📊 Scraping Summary")
        print(f"{'='*60}")
        print(f"⏱️  Duration: {results['duration']:.2f} seconds")
        print(f"🔑 Keywords processed: {results['keywords_processed']}/{len(self.KEYWORDS)}")
        print(f"📰 Articles found: {results['articles_found']}")
        print(f"💾 Articles stored: {results['articles_stored']}")
        print(f"🔄 Duplicates skipped: {results['articles_duplicate']}")
        
        if results['errors']:
            print(f"❌ Errors: {len(results['errors'])}")
            for error in results['errors']:
                print(f"   - {error}")
        else:
            print(f"✅ No errors")
        
        print(f"{'='*60}\n")


# Test when run directly
if __name__ == "__main__":
    scraper = ScheduledScraper()
    
    print("🧪 Testing scheduled scraper with one keyword...")
    
    # Test with just one keyword
    test_keyword = "黑客"
    print(f"\nTesting keyword: {test_keyword}")
    
    result = scraper._scrape_keyword(test_keyword)
    print(f"\nTest result: {result}")
    
    print("\n✅ Scheduled scraper test complete!")
