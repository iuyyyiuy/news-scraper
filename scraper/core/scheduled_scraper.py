"""
Scheduled Scraper for News Database Feature
Automatically scrapes news based on predefined keywords
"""
from datetime import datetime, date, timedelta
from typing import List, Dict
from .database_manager import DatabaseManager
from .multi_source_scraper import MultiSourceScraper
from .alert_logger import AlertLogger
from .ai_content_analyzer import AIContentAnalyzer
from scraper.core import Config
from scraper.core.storage import CSVDataStore
import tempfile
import os
import time


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
        self.alert_logger = AlertLogger()
        # Initialize AI content analyzer if API key is available
        try:
            self.ai_analyzer = AIContentAnalyzer()
            self.use_ai_analysis = True
            self.alert_logger.log_info(
                component="ScheduledScraper",
                message="AI Content Analyzer initialized successfully",
                details={"deepseek_api": "enabled"}
            )
        except ValueError as e:
            self.ai_analyzer = None
            self.use_ai_analysis = False
            self.alert_logger.log_warning(
                component="ScheduledScraper",
                message="AI Content Analyzer not available - using basic keyword matching",
                details={"reason": str(e)}
            )
        
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
    
    def scrape_daily(self, max_articles: int = 200) -> Dict[str, any]:
        """
        Execute daily scraping for all keywords
        Gets latest news ID and scrapes backward specified number of articles
        
        Args:
            max_articles: Maximum number of articles to scrape (default 200)
        
        Returns:
            Dictionary with scraping results
        """
        print(f"\n{'='*60}")
        print(f"🤖 Starting scheduled scrape at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # Start alert logging session
        session_id = self.alert_logger.start_scraping_session(['BlockBeats'])
        
        results = {
            'start_time': datetime.now(),
            'session_id': session_id,
            'keywords_processed': 0,
            'articles_found': 0,
            'articles_stored': 0,
            'articles_duplicate': 0,
            'errors': []
        }
        
        # Scrape latest articles from BlockBeats (no date filter)
        scrape_start_time = time.time()
        try:
            print(f"\n🔍 Scraping latest {max_articles} articles from BlockBeats")
            print(f"   Keywords: {len(self.KEYWORDS)} security-related terms")
            
            self.alert_logger.log_info(
                component="ScheduledScraper",
                message=f"Starting scrape of {max_articles} articles from BlockBeats",
                details={"max_articles": max_articles, "keywords_count": len(self.KEYWORDS)}
            )
            
            # Create config - scrape latest articles
            config = Config(
                target_url="https://www.theblockbeats.info/newsflash",
                max_articles=max_articles,  # Use parameter value
                request_delay=1.0,  # Faster for scheduled runs
                timeout=30,
                max_retries=3
            )
            
            temp_file = os.path.join(self.temp_dir, "temp_daily.csv")
            data_store = CSVDataStore(temp_file)
            
            # No date filtering - just get latest articles
            end_date = date.today()
            start_date = end_date - timedelta(days=7)  # Look back 7 days max
            
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
            print("   Fetching articles...")
            scraper.scrape()
            articles = data_store.get_all_articles()
            
            results['articles_found'] = len(articles)
            results['keywords_processed'] = len(self.KEYWORDS)
            
            print(f"   Found {len(articles)} matching articles")
            
            # Process articles with AI analysis if available
            if self.use_ai_analysis and articles:
                print(f"   🤖 Running AI analysis on {len(articles)} articles...")
                articles = self._process_articles_with_ai(articles)
                print(f"   🤖 AI analysis complete: {len(articles)} articles after filtering")
            
            # Store each article - keywords already filtered by MultiSourceScraper
            for article in articles:
                try:
                    # Get matched keywords from article or find them
                    if hasattr(article, 'matched_keywords') and article.matched_keywords:
                        matched_keywords = article.matched_keywords
                    else:
                        # Find which keywords matched
                        title_lower = article.title.lower()
                        body_lower = article.body_text.lower() if hasattr(article, 'body_text') else ''
                        matched_keywords = [kw for kw in self.KEYWORDS if kw.lower() in title_lower or kw.lower() in body_lower]
                    
                    # Check AI relevance if available
                    should_store = True
                    if hasattr(article, 'ai_analysis') and article.ai_analysis:
                        relevance = article.ai_analysis.get('relevance', {})
                        if not relevance.get('is_relevant', True) or relevance.get('relevance_score', 100) < 40:
                            should_store = False
                            self.alert_logger.log_info(
                                component="AIFilter",
                                message="Article filtered out by AI relevance analysis",
                                details={
                                    "title": article.title[:100],
                                    "relevance_score": relevance.get('relevance_score', 0),
                                    "explanation": relevance.get('explanation', '')
                                }
                            )
                    
                    if matched_keywords and should_store:  # Only store if keywords matched and AI approves
                        if self._store_article(article, matched_keywords):
                            results['articles_stored'] += 1
                            print(f"   ✅ Stored: {article.title[:50]}...")
                        else:
                            results['articles_duplicate'] += 1
                    elif not should_store:
                        # Count as filtered by AI
                        results['articles_duplicate'] += 1
                        
                except Exception as e:
                    self.alert_logger.log_error(
                        component="ArticleStorage",
                        message=f"Failed to store article: {getattr(article, 'title', 'Unknown')}",
                        details={"error": str(e)},
                        exception=e
                    )
                    results['errors'].append(f"Storage error: {e}")
            
            # Calculate scraping performance
            scrape_duration = time.time() - scrape_start_time
            
            # Log scraping operation results
            self.alert_logger.log_scraping_operation(
                source="BlockBeats",
                articles_found=results['articles_found'],
                articles_stored=results['articles_stored'],
                articles_duplicate=results['articles_duplicate'],
                duration_seconds=scrape_duration,
                errors=results['errors'] if results['errors'] else None
            )
            
            print(f"\n  📊 Summary: Found {results['articles_found']}, Stored {results['articles_stored']}, Duplicate {results['articles_duplicate']}")
            
        except Exception as e:
            error_msg = f"Error during scraping: {e}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            results['errors'].append(error_msg)
            
            # Log critical error
            self.alert_logger.log_critical(
                component="ScheduledScraper",
                message="Critical error during scraping operation",
                details={"error_message": error_msg, "max_articles": max_articles},
                exception=e
            )
        
        results['end_time'] = datetime.now()
        results['duration'] = (results['end_time'] - results['start_time']).total_seconds()
        
        # End alert logging session
        completed_session = self.alert_logger.end_scraping_session()
        
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
            article: Article object from scraper
            matched_keywords: List of keywords that matched this article
        
        Returns:
            True if stored, False if duplicate
        """
        try:
            # Check if article already exists
            if self.db_manager.check_article_exists(article.url):
                # Article exists, could update keywords here if needed
                return False
            
            # Prepare article data - match CSV structure
            # Handle both date and publication_date attributes
            if hasattr(article, 'publication_date') and article.publication_date:
                pub_date = article.publication_date
            elif hasattr(article, 'date') and article.date:
                pub_date = article.date
            else:
                from datetime import date
                pub_date = date.today()
            
            if hasattr(pub_date, 'strftime'):
                pub_date_str = pub_date.strftime('%Y/%m/%d')
            else:
                pub_date_str = str(pub_date)
            
            # Get body text
            body_text = article.body_text if hasattr(article, 'body_text') else article.title
            
            # Normalize source name using standardized function
            source = self._normalize_source_name(article)
            
            article_data = {
                'publication_date': pub_date_str,
                'title': article.title,
                'body_text': body_text,
                'url': article.url,
                'source': source,
                'matched_keywords': matched_keywords
            }
            
            # Insert into database
            return self.db_manager.insert_article(article_data)
            
        except Exception as e:
            print(f"  ❌ Error storing article: {e}")
            import traceback
            traceback.print_exc()
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
    
    def _normalize_source_name(self, article) -> str:
        """
        Normalize source name to standardized format.
        
        Args:
            article: Article object with source information
            
        Returns:
            Standardized source name: "BlockBeats" or "Jinse"
        """
        # Get source from article
        if hasattr(article, 'source_website'):
            source = article.source_website.lower()
        elif hasattr(article, 'source'):
            source = article.source.lower()
        else:
            # Default to BlockBeats if no source info
            return 'BlockBeats'
        
        # Normalize based on source patterns
        if any(pattern in source for pattern in ['blockbeat', 'theblockbeats']):
            return 'BlockBeats'
        elif any(pattern in source for pattern in ['jinse']):
            return 'Jinse'
        else:
            # Default to BlockBeats for unknown sources
            return 'BlockBeats'
    
    def _process_articles_with_ai(self, articles: List) -> List:
        """
        Process articles with AI analysis for relevance and duplicate detection.
        
        Args:
            articles: List of article objects
            
        Returns:
            Filtered list of articles after AI analysis
        """
        if not self.ai_analyzer:
            return articles
        
        try:
            # Convert articles to format expected by AI analyzer
            article_dicts = []
            for article in articles:
                # Get matched keywords
                if hasattr(article, 'matched_keywords') and article.matched_keywords:
                    matched_keywords = article.matched_keywords
                else:
                    # Find which keywords matched
                    title_lower = article.title.lower()
                    body_lower = article.body_text.lower() if hasattr(article, 'body_text') else ''
                    matched_keywords = [kw for kw in self.KEYWORDS if kw.lower() in title_lower or kw.lower() in body_lower]
                
                article_dict = {
                    'title': article.title,
                    'content': article.body_text if hasattr(article, 'body_text') else article.title,
                    'matched_keywords': matched_keywords,
                    'original_article': article  # Keep reference to original
                }
                article_dicts.append(article_dict)
            
            # Run AI analysis
            analyzed_articles = self.ai_analyzer.analyze_article_batch(article_dicts)
            
            # Convert back to original article objects with AI analysis attached
            filtered_articles = []
            for analyzed in analyzed_articles:
                original_article = analyzed['original_article']
                # Attach AI analysis results
                original_article.ai_analysis = analyzed.get('ai_analysis', {})
                filtered_articles.append(original_article)
            
            # Log AI filtering results
            original_count = len(articles)
            filtered_count = len(filtered_articles)
            filtered_out = original_count - filtered_count
            
            if filtered_out > 0:
                self.alert_logger.log_info(
                    component="AIContentAnalyzer",
                    message=f"AI filtering completed: {filtered_out} articles filtered out",
                    details={
                        "original_count": original_count,
                        "filtered_count": filtered_count,
                        "filter_rate": f"{(filtered_out/original_count)*100:.1f}%"
                    }
                )
            
            return filtered_articles
            
        except Exception as e:
            self.alert_logger.log_error(
                component="AIContentAnalyzer",
                message="Error in AI article processing",
                details={"article_count": len(articles)},
                exception=e
            )
            # Return original articles if AI processing fails
            return articles


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
