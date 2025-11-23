"""
PANews (panewslab.com) specific scraper.
"""
import logging
import time
from typing import List, Optional
from datetime import datetime, date
import requests
import re

from .http_client import HTTPClient
from .parser import HTMLParser
from .storage import DataStore
from .models import Config, ScrapingResult, Article


logger = logging.getLogger(__name__)


class PANewsScraper:
    """
    Specialized scraper for PANews (panewslab.com).
    
    PANews uses article IDs in the format:
    https://www.panewslab.com/zh/articledetails/{id}.html
    
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
        Initialize the PANews scraper.
        
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
        
        # PANews-specific selectors
        panews_selectors = {
            'title': 'h1, .article-title, .detail-title',
            'date': 'time, .time, .date, .publish-time, .article-time',
            'body': '.article-content, .detail-content, .content, .article-body'
        }
        
        self.parser = HTMLParser(selectors=panews_selectors)
        self.base_url = "https://www.panewslab.com/zh/articledetails/"
    
    def _log(self, message: str, log_type: str = 'info', show_in_all: bool = None):
        """Helper to log messages if callback is available."""
        # Smart defaults: filtered/skipped logs don't show in "All" tab
        if show_in_all is None:
            show_in_all = log_type not in ['filtered', 'skipped']
        
        if self.log_callback:
            self.log_callback(message, log_type, 'panews', show_in_all)
        logger.info(message)
    
    def find_latest_article_id(self) -> Optional[int]:
        """
        Find the latest article ID by checking the main page.
        
        Returns:
            Latest article ID or None if not found
        """
        try:
            self._log("🔍 正在查找PANews最新文章ID...", "info")
            response = self.http_client.fetch_with_retry("https://www.panewslab.com/zh/index.html")
            
            # Look for article links in the format /zh/articledetails/{id}.html
            pattern = r'/zh/articledetails/(\w+)\.html'
            matches = re.findall(pattern, response.text)
            
            if matches:
                # PANews uses alphanumeric IDs, try to find the highest numeric one
                numeric_ids = []
                for id_str in matches:
                    # Try to extract numeric part or convert if fully numeric
                    if id_str.isdigit():
                        numeric_ids.append(int(id_str))
                    else:
                        # Extract numeric parts
                        nums = re.findall(r'\d+', id_str)
                        if nums:
                            numeric_ids.append(int(nums[0]))
                
                if numeric_ids:
                    latest_id = max(numeric_ids)
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
        
        logger.info(f"Starting PANews scraping session")
        logger.info(f"Date range: {self.start_date.date()} to {self.end_date.date()}")
        logger.info(f"Keywords: {self.keywords_filter}")
        logger.info(f"Max articles: {self.config.max_articles}")
        
        try:
            # Find the latest article ID
            latest_id = self.find_latest_article_id()
            if not latest_id:
                # Fallback to a reasonable starting point
                latest_id = 800000  # Adjust based on current PANews article count
                self._log(f"⚠️  使用默认起始ID: {latest_id}", "info")
            
            # Iterate backwards through article IDs
            current_id = latest_id
            consecutive_failures = 0
            max_consecutive_failures = 20
            articles_before_start_date = 0
            max_articles_before_start_date = 5
            
            while articles_checked < self.config.max_articles:
                # Check if we've hit too many consecutive failures
                if consecutive_failures >= max_consecutive_failures:
                    self._log(f"⏹️  停止: {max_consecutive_failures} 个连续失败", "info")
                    break
                
                # Check if we've gone too far back in time
                if articles_before_start_date >= max_articles_before_start_date:
                    self._log(f"⏹️  停止: 找到 {max_articles_before_start_date} 个连续的过早文章", "info")
                    break
                
                # PANews uses alphanumeric IDs, try both formats
                article_url = f"{self.base_url}{current_id}.html"
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
                        "panewslab.com"
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
                        consecutive_failures += 1
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
                
                # Safety check
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
        logger.info("PANEWS SCRAPING SESSION SUMMARY")
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
