"""
Scraper controller that orchestrates the scraping workflow.
"""
import logging
import time
from typing import List
from urllib.parse import urlparse

from .http_client import HTTPClient
from .parser import HTMLParser
from .storage import DataStore, JSONDataStore, CSVDataStore
from .models import Config, ScrapingResult, Article


logger = logging.getLogger(__name__)


class ScraperController:
    """
    Main controller that orchestrates the scraping workflow.
    
    Coordinates HTTP fetching, HTML parsing, and data storage while
    tracking progress and handling errors.
    """
    
    def __init__(self, config: Config, data_store: DataStore = None, days_filter: int = None, keywords_filter: List[str] = None, progress_callback=None):
        """
        Initialize the scraper controller.
        
        Args:
            config: Configuration object
            data_store: Data storage implementation (creates JSONDataStore if None)
            days_filter: Only scrape articles from last N days (optional)
            keywords_filter: Only save articles containing these keywords (optional)
            progress_callback: Optional callback function(articles_found, articles_scraped) for progress updates
        """
        self.config = config
        self.days_filter = days_filter
        self.keywords_filter = [kw.strip().lower() for kw in keywords_filter] if keywords_filter else None
        self.progress_callback = progress_callback
        
        # Initialize components
        self.http_client = HTTPClient(
            timeout=config.timeout,
            request_delay=config.request_delay,
            max_retries=config.max_retries
        )
        
        self.parser = HTMLParser(selectors=config.selectors)
        
        # Use provided data store or create based on output format
        if data_store is None:
            if config.output_format == 'csv':
                self.data_store = CSVDataStore(config.output_path)
            else:
                self.data_store = JSONDataStore(config.output_path)
        else:
            self.data_store = data_store
        
        # Extract source website from target URL
        parsed_url = urlparse(config.target_url)
        self.source_website = parsed_url.netloc
    
    def scrape(self) -> ScrapingResult:
        """
        Execute the full scraping workflow.
        
        This method:
        1. Fetches the listing page
        2. Extracts article URLs
        3. Fetches and parses each article
        4. Saves articles to storage
        5. Tracks progress and errors
        
        Returns:
            ScrapingResult with statistics about the scraping session
        """
        start_time = time.time()
        errors: List[str] = []
        articles_scraped = 0
        articles_failed = 0
        
        logger.info(f"Starting scraping session for {self.config.target_url}")
        logger.info(f"Max articles: {self.config.max_articles}")
        
        try:
            # Step 1: Fetch the listing page
            logger.info("Fetching article listing page...")
            response = self.http_client.fetch_with_retry(self.config.target_url)
            
            # Step 2: Extract article URLs
            logger.info("Extracting article URLs...")
            article_urls = self.parser.parse_article_list(
                response.text,
                self.config.target_url
            )
            
            total_articles_found = len(article_urls)
            logger.info(f"Found {total_articles_found} article URLs")
            
            # Notify progress callback
            if self.progress_callback:
                self.progress_callback(total_articles_found, 0)
            
            # Limit to max_articles
            article_urls = article_urls[:self.config.max_articles]
            logger.info(f"Processing {len(article_urls)} articles (limited by max_articles)")

            # Step 3: Process each article
            for index, article_url in enumerate(article_urls, 1):
                try:
                    # Check if article already exists
                    if self.data_store.article_exists(article_url):
                        logger.info(f"[{index}/{len(article_urls)}] Skipping duplicate: {article_url}")
                        continue
                    
                    logger.info(f"[{index}/{len(article_urls)}] Processing: {article_url}")
                    
                    # Fetch article page
                    article_response = self.http_client.fetch_with_retry(article_url)
                    
                    # Parse article
                    article = self.parser.parse_article(
                        article_response.text,
                        article_url,
                        self.source_website
                    )
                    
                    # Check if article passes filters
                    if not self._should_save_article(article):
                        logger.info(
                            f"[{index}/{len(article_urls)}] Skipping (filtered): {article.title}"
                        )
                        continue
                    
                    # Save article
                    if self.data_store.save_article(article):
                        articles_scraped += 1
                        logger.info(
                            f"[{index}/{len(article_urls)}] Successfully scraped: {article.title}"
                        )
                        
                        # Notify progress callback
                        if self.progress_callback:
                            self.progress_callback(total_articles_found, articles_scraped)
                    else:
                        logger.warning(
                            f"[{index}/{len(article_urls)}] Article already exists: {article_url}"
                        )
                    
                except Exception as e:
                    articles_failed += 1
                    error_msg = f"Failed to scrape {article_url}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(f"[{index}/{len(article_urls)}] {error_msg}")
                    # Continue processing other articles
                    continue
            
            # Calculate duration
            duration_seconds = time.time() - start_time
            
            # Create result summary
            result = ScrapingResult(
                total_articles_found=total_articles_found,
                articles_scraped=articles_scraped,
                articles_failed=articles_failed,
                duration_seconds=duration_seconds,
                errors=errors
            )
            
            # Log session summary
            self._log_session_summary(result)
            
            return result
            
        except Exception as e:
            # Handle fatal errors that prevent scraping
            duration_seconds = time.time() - start_time
            error_msg = f"Fatal error during scraping: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
            
            return ScrapingResult(
                total_articles_found=0,
                articles_scraped=articles_scraped,
                articles_failed=articles_failed,
                duration_seconds=duration_seconds,
                errors=errors
            )
        
        finally:
            # Clean up HTTP client
            self.http_client.close()
    
    def _check_keywords(self, article: Article) -> List[str]:
        """
        Check if article contains any of the configured keywords.
        
        Args:
            article: Article to check
            
        Returns:
            List of matched keywords, empty if no matches
        """
        matched = []
        # Combine title and body for searching
        content = f"{article.title} {article.body_text}".lower()
        
        for keyword in self.config.keywords:
            if keyword.lower() in content:
                matched.append(keyword)
        
        return matched
    
    def _should_save_article(self, article: Article) -> bool:
        """
        Check if article should be saved based on filters.
        Also populates matched_keywords field.
        
        Args:
            article: Article to check
            
        Returns:
            True if article passes all filters, False otherwise
        """
        from datetime import datetime, timedelta
        
        # Check date filter
        if self.days_filter is not None:
            if article.publication_date:
                cutoff_date = datetime.now() - timedelta(days=self.days_filter)
                if article.publication_date < cutoff_date:
                    logger.debug(f"Article filtered out by date: {article.title}")
                    return False
            else:
                # If no publication date and date filter is active, use scraped_at
                cutoff_date = datetime.now() - timedelta(days=self.days_filter)
                if article.scraped_at < cutoff_date:
                    logger.debug(f"Article filtered out by date (using scraped_at): {article.title}")
                    return False
        
        # Check keyword filter and populate matched_keywords
        if self.keywords_filter:
            article_text = f"{article.title} {article.body_text}".lower()
            matched = [keyword for keyword in self.keywords_filter if keyword in article_text]
            
            if not matched:
                logger.debug(f"Article filtered out by keywords: {article.title}")
                return False
            
            # Store the matched keywords in the article
            article.matched_keywords = matched
        
        return True
    
    def _log_session_summary(self, result: ScrapingResult) -> None:
        """
        Log a summary of the scraping session.
        
        Args:
            result: ScrapingResult object with session statistics
        """
        logger.info("=" * 60)
        logger.info("SCRAPING SESSION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total articles found: {result.total_articles_found}")
        logger.info(f"Articles successfully scraped: {result.articles_scraped}")
        logger.info(f"Articles failed: {result.articles_failed}")
        logger.info(f"Duration: {result.duration_seconds:.2f} seconds")
        
        if result.errors:
            logger.warning(f"Errors encountered: {len(result.errors)}")
            for error in result.errors[:5]:  # Show first 5 errors
                logger.warning(f"  - {error}")
            if len(result.errors) > 5:
                logger.warning(f"  ... and {len(result.errors) - 5} more errors")
        else:
            logger.info("No errors encountered")
        
        logger.info("=" * 60)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.http_client.close()
