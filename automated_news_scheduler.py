#!/usr/bin/env python3
"""
Automated News Scheduler for Digital Ocean
Runs every 4 hours to scrape 100 news articles, filter duplicates and irrelevant content,
and update the Supabase database for the news dashboard.
"""

import sys
import os
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import time
import tempfile

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.core.database_manager import DatabaseManager
from scraper.core.multi_source_scraper import MultiSourceScraper
from scraper.core.alert_logger import AlertLogger
from scraper.core.ai_content_analyzer import AIContentAnalyzer
from scraper.core import Config
from scraper.core.storage import CSVDataStore

# Configure logging for different environments
def setup_logging():
    """Setup logging configuration based on environment"""
    # Try production log directory first
    if os.path.exists('/var/log') and os.access('/var/log', os.W_OK):
        log_dir = '/var/log/news-scraper'
        try:
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, 'scheduler.log')
        except PermissionError:
            log_file = './scheduler.log'
    else:
        # Development environment
        log_file = './scheduler.log'
    
    # Create handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    
    # Add file handler
    try:
        handlers.append(logging.FileHandler(log_file))
    except PermissionError:
        pass  # Skip file logging if no permissions
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    return log_file

# Setup logging
log_file_path = setup_logging()
logger = logging.getLogger(__name__)


class AutomatedNewsScheduler:
    """
    Automated news scheduler for Digital Ocean deployment
    Scrapes 100 articles every 4 hours with enhanced duplicate detection and AI filtering
    """
    
    # Security-related keywords for filtering (21 keywords as specified)
    KEYWORDS = [
        "安全问题", "黑客", "被盗", "漏洞", "攻击", "恶意软件", "盗窃",
        "CoinEx", "ViaBTC", "破产", "执法", "监管", "洗钱", "KYC",
        "合规", "牌照", "风控", "诈骗", "突发", "rug pull", "下架"
    ]
    
    def __init__(self):
        """Initialize the automated scheduler"""
        logger.info("🤖 Initializing Automated News Scheduler")
        
        # Initialize core components
        self.db_manager = DatabaseManager()
        self.alert_logger = AlertLogger()
        
        # Initialize AI content analyzer
        try:
            self.ai_analyzer = AIContentAnalyzer()
            self.use_ai_analysis = True
            logger.info("✅ AI Content Analyzer initialized successfully")
        except ValueError as e:
            self.ai_analyzer = None
            self.use_ai_analysis = False
            logger.warning(f"⚠️ AI Content Analyzer not available: {e}")
        
        # Create temporary directory for CSV storage
        self.temp_dir = tempfile.mkdtemp()
        
        logger.info("✅ Automated News Scheduler initialized successfully")
    
    def run_scheduled_scrape(self, max_articles: int = 100) -> Dict[str, any]:
        """
        Execute scheduled news scraping
        
        Process:
        1. Scrape latest 100 articles from BlockBeats
        2. Filter by security keywords
        3. Apply enhanced duplicate detection (database-aware)
        4. Use AI to filter irrelevant content
        5. Store relevant articles in Supabase database
        6. Update news dashboard automatically
        
        Args:
            max_articles: Maximum articles to scrape (default 100)
            
        Returns:
            Dictionary with comprehensive scraping results
        """
        start_time = datetime.now()
        logger.info(f"🚀 Starting scheduled scrape at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"📊 Target: {max_articles} articles with {len(self.KEYWORDS)} security keywords")
        
        # Start alert logging session
        session_id = self.alert_logger.start_scraping_session(['BlockBeats'])
        
        results = {
            'start_time': start_time,
            'session_id': session_id,
            'max_articles': max_articles,
            'articles_found': 0,
            'articles_with_keywords': 0,
            'articles_after_ai_filter': 0,
            'articles_stored': 0,
            'duplicates_removed': 0,
            'ai_filtered': 0,
            'errors': [],
            'duplicate_methods': {}
        }
        
        try:
            # Create scraper configuration
            config = Config(
                target_url="https://www.theblockbeats.info/newsflash",
                max_articles=max_articles,
                request_delay=1.0,  # Faster for automated runs
                timeout=30,
                max_retries=3
            )
            
            # Create temporary data store
            temp_file = os.path.join(self.temp_dir, f"scheduled_{int(time.time())}.csv")
            data_store = CSVDataStore(temp_file)
            
            # Date range: last 24 hours (for scheduled runs)
            end_date = date.today()
            start_date = end_date - timedelta(days=1)
            
            logger.info(f"📅 Date range: {start_date} to {end_date}")
            logger.info(f"🔑 Keywords: {', '.join(self.KEYWORDS[:5])}{'...' if len(self.KEYWORDS) > 5 else ''}")
            
            # Create scraper with enhanced duplicate detection
            scraper = MultiSourceScraper(
                config=config,
                data_store=data_store,
                start_date=start_date,
                end_date=end_date,
                keywords_filter=self.KEYWORDS,
                sources=['blockbeats'],  # Only BlockBeats (Jinse disabled)
                enable_deduplication=True,  # Enhanced duplicate detection enabled
                progress_callback=self._progress_callback,
                log_callback=self._log_callback
            )
            
            logger.info("🔍 Starting news scraping with enhanced duplicate detection...")
            
            # Run scraper
            scrape_result = scraper.scrape(parallel=False)
            
            # Get articles from data store
            articles = data_store.get_all_articles()
            
            results['articles_found'] = scrape_result.total_articles_found
            results['articles_with_keywords'] = len(articles)
            
            logger.info(f"📊 Scraping completed:")
            logger.info(f"   - Total articles checked: {scrape_result.total_articles_found}")
            logger.info(f"   - Articles with keywords: {len(articles)}")
            logger.info(f"   - Scraping duration: {scrape_result.duration_seconds:.2f}s")
            
            # AI filtering if available
            if self.use_ai_analysis and articles:
                logger.info(f"🤖 Starting AI analysis on {len(articles)} articles...")
                articles = self._process_articles_with_ai(articles)
                results['articles_after_ai_filter'] = len(articles)
                results['ai_filtered'] = results['articles_with_keywords'] - len(articles)
                logger.info(f"🤖 AI analysis completed: {len(articles)} articles after filtering")
            else:
                results['articles_after_ai_filter'] = len(articles)
            
            # Store articles in database
            logger.info(f"💾 Storing {len(articles)} articles in database...")
            stored_count = 0
            duplicate_count = 0
            
            for article in articles:
                try:
                    # Find matched keywords
                    title_lower = article.title.lower()
                    body_lower = getattr(article, 'body_text', '').lower()
                    matched_keywords = [kw for kw in self.KEYWORDS if kw.lower() in title_lower or kw.lower() in body_lower]
                    
                    # Check AI relevance if available
                    should_store = True
                    if hasattr(article, 'ai_analysis') and article.ai_analysis:
                        relevance = article.ai_analysis.get('relevance', {})
                        if not relevance.get('is_relevant', True) and relevance.get('relevance_score', 100) < 30:
                            should_store = False
                    
                    if matched_keywords and should_store:
                        if self._store_article_realtime(article, matched_keywords):
                            stored_count += 1
                            if stored_count % 5 == 0:
                                logger.info(f"   💾 Stored {stored_count} articles...")
                        else:
                            duplicate_count += 1
                    
                except Exception as e:
                    error_msg = f"Error storing article: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            results['articles_stored'] = stored_count
            results['duplicates_removed'] = duplicate_count
            
            # Calculate final statistics
            results['end_time'] = datetime.now()
            results['duration'] = (results['end_time'] - results['start_time']).total_seconds()
            
            # Log scraping operation
            self.alert_logger.log_scraping_operation(
                source="BlockBeats",
                articles_found=results['articles_found'],
                articles_stored=results['articles_stored'],
                articles_duplicate=results['duplicates_removed'],
                duration_seconds=results['duration'],
                errors=results['errors'] if results['errors'] else None
            )
            
            # End alert logging session
            completed_session = self.alert_logger.end_scraping_session()
            
            # Log comprehensive summary
            self._log_final_summary(results)
            
            return results
            
        except Exception as e:
            error_msg = f"Critical error during scheduled scraping: {str(e)}"
            logger.error(error_msg, exc_info=True)
            results['errors'].append(error_msg)
            
            # Log critical error
            self.alert_logger.log_critical(
                component="AutomatedNewsScheduler",
                message="Critical error during scheduled scraping",
                details={"max_articles": max_articles},
                exception=e
            )
            
            results['end_time'] = datetime.now()
            results['duration'] = (results['end_time'] - results['start_time']).total_seconds()
            
            return results
    
    def _progress_callback(self, source: str, articles_found: int, articles_scraped: int):
        """Progress callback for scraper"""
        if articles_found % 10 == 0:  # Log every 10 articles
            logger.info(f"📊 {source.upper()}: Found {articles_found}, Processed {articles_scraped}")
    
    def _log_callback(self, message: str, log_type: str = 'info', source: str = None, show_in_all: bool = True):
        """Log callback for scraper"""
        # Only log important messages to avoid spam
        if any(keyword in message for keyword in ['完成', '开始', '去重', '错误', '失败']):
            if log_type == 'error':
                logger.error(f"❌ {message}")
            elif log_type == 'success':
                logger.info(f"✅ {message}")
            else:
                logger.info(f"ℹ️ {message}")
    
    def _process_articles_with_ai(self, articles: List) -> List:
        """
        Process articles with AI analysis for relevance filtering
        
        Args:
            articles: List of article objects
            
        Returns:
            Filtered list of articles after AI analysis
        """
        if not self.ai_analyzer:
            return articles
        
        try:
            # Get recent articles from database for duplicate comparison
            recent_db_articles = self._get_recent_database_articles(days=7, limit=50)
            
            # Convert articles to format expected by AI analyzer
            article_dicts = []
            for article in articles:
                # Get matched keywords
                title_lower = article.title.lower()
                body_lower = getattr(article, 'body_text', '').lower()
                matched_keywords = [kw for kw in self.KEYWORDS if kw.lower() in title_lower or kw.lower() in body_lower]
                
                article_dict = {
                    'title': article.title,
                    'content': getattr(article, 'body_text', article.title),
                    'matched_keywords': matched_keywords,
                    'original_article': article
                }
                article_dicts.append(article_dict)
            
            # Process articles with AI analysis
            analyzed_articles = []
            for i, article_dict in enumerate(article_dicts):
                try:
                    # AI relevance analysis
                    relevance = self.ai_analyzer.analyze_content_relevance(
                        article_dict['title'],
                        article_dict['content'],
                        article_dict.get('matched_keywords', [])
                    )
                    
                    # AI duplicate check against database
                    duplicate_check = self.ai_analyzer.detect_duplicate_content(
                        {'title': article_dict['title'], 'content': article_dict['content']},
                        recent_db_articles
                    )
                    
                    # Add analysis results to original article
                    original_article = article_dict['original_article']
                    original_article.ai_analysis = {
                        'relevance': relevance,
                        'duplicate_check': duplicate_check,
                        'analyzed_at': datetime.now().isoformat()
                    }
                    
                    # Only keep if not duplicate and relevant
                    if not duplicate_check['is_duplicate'] and relevance.get('is_relevant', True):
                        analyzed_articles.append(original_article)
                    else:
                        # Log filtering reason
                        if duplicate_check['is_duplicate']:
                            logger.info(f"   🤖 AI filtered duplicate: {article_dict['title'][:50]}...")
                        else:
                            logger.info(f"   🤖 AI filtered irrelevant: {article_dict['title'][:50]}...")
                
                except Exception as e:
                    logger.error(f"Error analyzing article {i}: {e}")
                    # Keep article without analysis if AI fails
                    analyzed_articles.append(article_dict['original_article'])
            
            # Log AI filtering results
            original_count = len(articles)
            filtered_count = len(analyzed_articles)
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
            
            return analyzed_articles
            
        except Exception as e:
            logger.error(f"Error in AI article processing: {e}")
            self.alert_logger.log_error(
                component="AIContentAnalyzer",
                message="Error in AI article processing",
                details={"article_count": len(articles)},
                exception=e
            )
            return articles
    
    def _get_recent_database_articles(self, days: int = 7, limit: int = 50) -> List[Dict[str, str]]:
        """Get recent articles from database for duplicate comparison"""
        try:
            # Calculate date range
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # Query recent articles
            result = self.db_manager.supabase.table('articles').select(
                'title, body_text'
            ).gte(
                'date', start_date.strftime('%Y/%m/%d')
            ).order(
                'scraped_at', desc=True
            ).limit(limit).execute()
            
            # Convert to format expected by AI analyzer
            recent_articles = []
            for article in result.data:
                recent_articles.append({
                    'title': article['title'],
                    'content': article.get('body_text', article['title'])
                })
            
            logger.info(f"📊 Retrieved {len(recent_articles)} recent articles for AI duplicate comparison")
            return recent_articles
            
        except Exception as e:
            logger.error(f"Error retrieving recent database articles: {e}")
            return []
    
    def _store_article_realtime(self, article, matched_keywords: List[str]) -> bool:
        """
        Store article in database with real-time updates
        
        Args:
            article: Article object from scraper
            matched_keywords: List of keywords that matched this article
            
        Returns:
            True if stored, False if duplicate
        """
        try:
            # Check if article already exists
            if self.db_manager.check_article_exists(article.url):
                return False
            
            # Prepare article data - match original format
            if hasattr(article, 'publication_date') and article.publication_date:
                pub_date = article.publication_date
            elif hasattr(article, 'date') and article.date:
                pub_date = article.date
            else:
                pub_date = date.today()
            
            if hasattr(pub_date, 'strftime'):
                pub_date_str = pub_date.strftime('%Y/%m/%d')
            else:
                pub_date_str = str(pub_date)
            
            # Extract content same as original format
            article_data = {
                'publication_date': pub_date_str,
                'title': article.title,
                'body_text': getattr(article, 'body_text', article.title),
                'url': article.url,
                'source': self._normalize_source_name(article),
                'matched_keywords': matched_keywords
            }
            
            # Insert into Supabase
            return self.db_manager.insert_article(article_data)
            
        except Exception as e:
            logger.error(f"Error storing article: {e}")
            return False
    
    def _normalize_source_name(self, article) -> str:
        """Normalize source name to match original format"""
        # Get source from article
        if hasattr(article, 'source_website'):
            source = article.source_website.lower()
        elif hasattr(article, 'source'):
            source = article.source.lower()
        else:
            return 'BlockBeats'
        
        # Normalize based on source patterns
        if any(pattern in source for pattern in ['blockbeat', 'theblockbeats']):
            return 'BlockBeats'
        elif any(pattern in source for pattern in ['jinse']):
            return 'Jinse'
        else:
            return 'BlockBeats'
    
    def _log_final_summary(self, results: Dict):
        """Log comprehensive final summary"""
        logger.info("=" * 80)
        logger.info("🎯 AUTOMATED SCRAPING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"⏱️  Start Time: {results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"⏱️  End Time: {results['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"⏱️  Duration: {results['duration']:.2f} seconds")
        logger.info(f"🎯 Target Articles: {results['max_articles']}")
        logger.info(f"📊 Articles Found: {results['articles_found']}")
        logger.info(f"🔑 With Keywords: {results['articles_with_keywords']}")
        
        if self.use_ai_analysis:
            logger.info(f"🤖 After AI Filter: {results['articles_after_ai_filter']}")
            logger.info(f"🤖 AI Filtered Out: {results['ai_filtered']}")
        
        logger.info(f"💾 Articles Stored: {results['articles_stored']}")
        logger.info(f"🔄 Duplicates Removed: {results['duplicates_removed']}")
        
        if results['errors']:
            logger.info(f"❌ Errors: {len(results['errors'])}")
            for error in results['errors'][:3]:  # Show first 3 errors
                logger.info(f"   - {error}")
        else:
            logger.info("✅ No Errors")
        
        # Calculate success rate
        if results['articles_found'] > 0:
            success_rate = (results['articles_stored'] / results['articles_found']) * 100
            logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        
        logger.info("=" * 80)
        
        # Log to alert system
        self.alert_logger.log_info(
            component="AutomatedNewsScheduler",
            message="Scheduled scraping completed successfully",
            details={
                "articles_found": results['articles_found'],
                "articles_stored": results['articles_stored'],
                "duplicates_removed": results['duplicates_removed'],
                "duration_seconds": results['duration'],
                "ai_analysis_enabled": self.use_ai_analysis
            }
        )


def main():
    """Main function for scheduled execution"""
    try:
        # Create scheduler instance
        scheduler = AutomatedNewsScheduler()
        
        # Run scheduled scrape
        results = scheduler.run_scheduled_scrape(max_articles=100)
        
        # Exit with appropriate code
        if results['errors']:
            logger.error(f"Scheduled scrape completed with {len(results['errors'])} errors")
            sys.exit(1)
        else:
            logger.info(f"✅ Scheduled scrape completed successfully: {results['articles_stored']} articles stored")
            sys.exit(0)
            
    except Exception as e:
        logger.critical(f"Critical error in automated scheduler: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()