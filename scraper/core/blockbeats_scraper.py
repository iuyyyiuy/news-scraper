"""
BlockBeats-specific scraper that iterates through article IDs.
"""
import logging
import time
from typing import List, Optional
from datetime import datetime, date
import requests

from .http_client import HTTPClient
from .parser import HTMLParser
from .storage import DataStore
from .models import Config, ScrapingResult, Article


logger = logging.getLogger(__name__)


class BlockBeatsScraper:
    """
    Specialized scraper for BlockBeats that iterates through article IDs.
    
    BlockBeats uses sequential article IDs in the format:
    https://www.theblockbeats.info/flash/{id}
    
    This scraper:
    1. Finds the latest article ID
    2. Iterates backwards through IDs
    3. Stops when reaching the start_date or max_articles limit
    """
    
    def __init__(
        self,
        config: Config,
        data_store: DataStore,
        start_date: date,
        end_date: date,
        keywords_filter: List[str],
        progress_callback=None,
        log_callback=None
    ):
        """
        Initialize the BlockBeats scraper.
        
        Args:
            config: Configuration object
            data_store: Data storage implementation
            start_date: Start date for filtering articles
            end_date: End date for filtering articles
            keywords_filter: Keywords to filter articles
            progress_callback: Optional callback function(articles_found, articles_scraped)
            log_callback: Optional callback function(message, log_type) for logging
        """
        self.config = config
        self.data_store = data_store
        self.start_date = datetime.combine(start_date, datetime.min.time())
        self.end_date = datetime.combine(end_date, datetime.max.time())
        self.keywords_filter = [kw.strip().lower() for kw in keywords_filter] if keywords_filter else []
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        
        self.http_client = HTTPClient(
            timeout=config.timeout,
            request_delay=config.request_delay,
            max_retries=config.max_retries
        )
        
        self.parser = HTMLParser(selectors=config.selectors)
        self.base_url = "https://www.theblockbeats.info/flash/"
    
    def _log(self, message: str, log_type: str = 'info', show_in_all: bool = None):
        """Helper to log messages if callback is available."""
        # Smart defaults: filtered/skipped logs don't show in "All" tab
        if show_in_all is None:
            show_in_all = log_type not in ['filtered', 'skipped']
        
        if self.log_callback:
            self.log_callback(message, log_type, show_in_all)
        logger.info(message)
    
    def find_latest_article_id(self) -> Optional[int]:
        """
        Find the latest article ID by checking the main page.
        
        Returns:
            Latest article ID or None if not found
        """
        try:
            self._log("🔍 正在查找最新文章ID...", "info")
            response = self.http_client.fetch_with_retry("https://www.theblockbeats.info/")
            
            # Look for flash article links in the format /flash/{id}
            import re
            pattern = r'/flash/(\d+)'
            matches = re.findall(pattern, response.text)
            
            if matches:
                # Get the highest ID
                latest_id = max(int(id_str) for id_str in matches)
                self._log(f"✅ 找到最新文章ID: {latest_id}", "success")
                return latest_id
            
            self._log("⚠️  未找到任何文章ID", "error")
            return None
            
        except Exception as e:
            self._log(f"❌ 查找最新文章ID失败: {str(e)}", "error")
            return None
    
    def scrape(self) -> ScrapingResult:
        """
        Execute the scraping workflow by iterating through article IDs.
        
        Returns:
            ScrapingResult with statistics
        """
        start_time = time.time()
        errors: List[str] = []
        articles_scraped = 0
        articles_failed = 0
        articles_checked = 0
        
        logger.info(f"Starting BlockBeats scraping session")
        logger.info(f"Date range: {self.start_date.date()} to {self.end_date.date()}")
        logger.info(f"Keywords: {self.keywords_filter}")
        logger.info(f"Max articles: {self.config.max_articles}")
        
        try:
            # Find the latest article ID
            latest_id = self.find_latest_article_id()
            if not latest_id:
                # Fallback to a reasonable starting point
                latest_id = 320000  # Adjust this based on current BlockBeats article count
                self._log(f"⚠️  使用默认起始ID: {latest_id}", "info")
            
            # Iterate backwards through article IDs
            current_id = latest_id
            consecutive_failures = 0
            max_consecutive_failures = 20  # Stop if we hit 20 consecutive 404s
            articles_before_start_date = 0
            max_articles_before_start_date = 5  # Stop if we find 5 consecutive articles before start_date
            
            # max_articles now means "how many to check", not "how many to save"
            while articles_checked < self.config.max_articles:
                # Check if we've hit too many consecutive failures
                if consecutive_failures >= max_consecutive_failures:
                    self._log(f"⏹️  停止: {max_consecutive_failures} 个连续失败", "info")
                    break
                
                # Check if we've gone too far back in time
                if articles_before_start_date >= max_articles_before_start_date:
                    self._log(f"⏹️  停止: 找到 {max_articles_before_start_date} 个连续的过早文章", "info")
                    break
                
                article_url = f"{self.base_url}{current_id}"
                articles_checked += 1
                
                try:
                    # Fetch article
                    response = self.http_client.fetch_with_retry(article_url)
                    
                    # Reset consecutive failures counter
                    consecutive_failures = 0
                    
                    # Parse article
                    article = self.parser.parse_article(
                        response.text,
                        article_url,
                        "theblockbeats.info"
                    )
                    
                    # Check if article is within date range
                    if article.publication_date:
                        if article.publication_date < self.start_date:
                            articles_before_start_date += 1
                            self._log(f"[{articles_checked}] ID {current_id}... ⏭️  日期过早 ({article.publication_date.date()})", "filtered")
                            current_id -= 1
                            continue
                        elif article.publication_date > self.end_date:
                            self._log(f"[{articles_checked}] ID {current_id}... ⏭️  日期太新 ({article.publication_date.date()})", "filtered")
                            current_id -= 1
                            continue
                        else:
                            # Reset the counter since we found an article in range
                            articles_before_start_date = 0
                    
                    # Check keywords
                    if self.keywords_filter:
                        article_text = f"{article.title} {article.body_text}".lower()
                        matched = [kw for kw in self.keywords_filter if kw in article_text]
                        
                        if not matched:
                            self._log(f"[{articles_checked}] ID {current_id}... ⏭️  无匹配关键词", "filtered", show_in_all=False)
                            current_id -= 1
                            continue
                        
                        article.matched_keywords = matched
                    
                    # Save article
                    if self.data_store.save_article(article):
                        articles_scraped += 1
                        self._log(
                            f"[{articles_scraped}] ID {current_id}... ✅ 已保存: {article.title[:30]}...",
                            "success"
                        )
                        
                        # Notify progress
                        if self.progress_callback:
                            self.progress_callback(articles_checked, articles_scraped)
                    
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 404:
                        # Article doesn't exist, continue to next ID
                        consecutive_failures += 1
                        # Don't log every 404, only every 10th
                        if consecutive_failures % 10 == 0:
                            self._log(f"⏭️  连续 {consecutive_failures} 个文章不存在", "filtered", show_in_all=False)
                    else:
                        articles_failed += 1
                        error_msg = f"HTTP错误 ID {current_id}: {str(e)}"
                        errors.append(error_msg)
                        self._log(f"⚠️  {error_msg}", "filtered", show_in_all=False)
                
                except Exception as e:
                    articles_failed += 1
                    error_msg = f"ID {current_id} 跳过: {str(e)}"
                    errors.append(error_msg)
                    self._log(f"⚠️  {error_msg}", "filtered", show_in_all=False)
                
                # Move to next article ID
                current_id -= 1
                
                # Safety check: don't go below a reasonable minimum
                if current_id < 1:
                    logger.info("Reached minimum article ID")
                    break
            
            # Calculate duration
            duration_seconds = time.time() - start_time
            
            # Create result
            result = ScrapingResult(
                total_articles_found=articles_checked,
                articles_scraped=articles_scraped,
                articles_failed=articles_failed,
                duration_seconds=duration_seconds,
                errors=errors
            )
            
            # Log summary
            self._log_session_summary(result)
            
            return result
            
        except Exception as e:
            duration_seconds = time.time() - start_time
            error_msg = f"Fatal error during scraping: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
            
            return ScrapingResult(
                total_articles_found=articles_checked,
                articles_scraped=articles_scraped,
                articles_failed=articles_failed,
                duration_seconds=duration_seconds,
                errors=errors
            )
        
        finally:
            self.http_client.close()
    
    def _log_session_summary(self, result: ScrapingResult) -> None:
        """Log a summary of the scraping session."""
        logger.info("=" * 60)
        logger.info("BLOCKBEATS SCRAPING SESSION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total articles checked: {result.total_articles_found}")
        logger.info(f"Articles successfully scraped: {result.articles_scraped}")
        logger.info(f"Articles failed: {result.articles_failed}")
        logger.info(f"Duration: {result.duration_seconds:.2f} seconds")
        
        if result.errors:
            logger.warning(f"Errors encountered: {len(result.errors)}")
            for error in result.errors[:5]:
                logger.warning(f"  - {error}")
            if len(result.errors) > 5:
                logger.warning(f"  ... and {len(result.errors) - 5} more errors")
        else:
            logger.info("No errors encountered")
        
        logger.info("=" * 60)
