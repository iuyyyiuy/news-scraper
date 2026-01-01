"""
Jinse (jinse.com.cn) specific scraper.
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


class JinseScraper:
    """
    Specialized scraper for Jinse (jinse.com.cn).
    
    Jinse uses article IDs in the format:
    https://www.jinse.com.cn/lives/{id}.html
    
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
        Initialize the Jinse scraper.
        
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
        
        # Jinse-specific selectors
        jinse_selectors = {
            'title': 'h1, .live-title, .article-title',
            'date': 'time, .time, .date, .publish-time',
            'body': '.live-content, .article-content, .content'
        }
        
        self.parser = HTMLParser(selectors=jinse_selectors)
        self.base_url = "https://www.jinse.com.cn/lives/"
    
    
    def _parse_jinse_article(self, html: str, url: str) -> Article:
        """
        Custom parser for Jinse articles.
        
        Args:
            html: HTML content
            url: Article URL
            
        Returns:
            Article object
        """
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title from <span class="title">
        title_elem = soup.select_one('span.title')
        title = title_elem.get_text(strip=True) if title_elem else "金色财经_区块链资讯_数字货币行情分析"
        
        # Extract content from <p class="content">
        content_elem = soup.select_one('p.content')
        body_text = content_elem.get_text(strip=True) if content_elem else ""
        
        # Extract date - try multiple sources
        publication_date = None
        year = datetime.now().year
        
        # Method 1: Extract from <span class="js-liveDetail__date">
        date_elem = soup.select_one('span.js-liveDetail__date')
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            # Pattern: "11月23日，星期日" or "11月23日"
            date_match = re.search(r'(\d{1,2})月(\d{1,2})日', date_text)
            if date_match:
                month = int(date_match.group(1))
                day = int(date_match.group(2))
                try:
                    publication_date = datetime(year, month, day, 0, 0, 0)
                except ValueError:
                    pass
        
        # Method 2: Extract from content text - pattern: "11月23日消息"
        if not publication_date and body_text:
            date_match = re.search(r'(\d{1,2})月(\d{1,2})日', body_text[:100])
            if date_match:
                month = int(date_match.group(1))
                day = int(date_match.group(2))
                try:
                    publication_date = datetime(year, month, day, 0, 0, 0)
                except ValueError:
                    pass
        
        # Fallback: use current date
        if not publication_date:
            publication_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Create article
        article = Article(
            url=url,
            title=title,
            publication_date=publication_date,
            author="金色财经",
            body_text=body_text,
            scraped_at=datetime.now(),
            source_website="jinse.com.cn"
        )
        
        return article

    def _log(self, message: str, log_type: str = 'info', show_in_all: bool = None):
        """Helper to log messages if callback is available."""
        # Smart defaults: filtered/skipped logs don't show in "All" tab
        if show_in_all is None:
            show_in_all = log_type not in ['filtered', 'skipped']
        
        if self.log_callback:
            self.log_callback(message, log_type, 'jinse', show_in_all)
        logger.info(message)
    
    def find_latest_article_id(self) -> Optional[int]:
        """
        Find the latest article ID by checking the main lives page.
        
        Returns:
            Latest article ID or None if not found
        """
        try:
            response = self.http_client.fetch_with_retry("https://www.jinse.com.cn/lives")
            
            # Look for lives article links in the format /lives/{id}.html
            pattern = r'/lives/(\d+)\.html'
            matches = re.findall(pattern, response.text)
            
            if matches:
                # Get the highest ID
                latest_id = max(int(id_str) for id_str in matches)
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
        
        logger.info(f"Starting Jinse scraping session")
        logger.info(f"Date range: {self.start_date.date()} to {self.end_date.date()}")
        logger.info(f"Keywords: {self.keywords_filter}")
        logger.info(f"Max articles: {self.config.max_articles}")
        
        try:
            # Find the latest article ID
            latest_id = self.find_latest_article_id()
            if not latest_id:
                # Jinse is temporarily unavailable due to domain issues
                self._log(f"⚠️  Jinse 暫時不可用", "info")
                
                # Return a proper ScrapingResult indicating Jinse is unavailable
                duration_seconds = time.time() - start_time
                return ScrapingResult(
                    total_articles_found=0,
                    articles_scraped=0,
                    articles_failed=0,
                    duration_seconds=duration_seconds,
                    errors=["Jinse 暫時不可用 - 域名访问问题"]
                )
            
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
                
                article_url = f"{self.base_url}{current_id}.html"
                articles_checked += 1
                
                try:
                    # Fetch article
                    response = self.http_client.fetch_with_retry(article_url)
                    
                    # Reset consecutive failures counter
                    consecutive_failures = 0
                    
                    # Parse article using custom Jinse parser
                    article = self._parse_jinse_article(response.text, article_url)
                    
                    # Check if article is within date range
                    if article.publication_date:
                        if article.publication_date < self.start_date:
                            articles_before_start_date += 1
                            self._log(f"[{articles_checked}] ID {current_id}... ⏭️  日期过早 ({article.publication_date.date()})", "filtered", show_in_all=False)
                            current_id -= 1
                            continue
                        elif article.publication_date > self.end_date:
                            self._log(f"[{articles_checked}] ID {current_id}... ⏭️  日期太新 ({article.publication_date.date()})", "filtered", show_in_all=False)
                            current_id -= 1
                            continue
                        else:
                            # Reset the counter since we found an article in range
                            articles_before_start_date = 0
                    
                    # Filter out summary titles (晨讯, 午报, etc.)
                    if re.search(r'(金色晨讯|金色午报|重要动态一览)', article.title):
                        self._log(f"[{articles_checked}] ID {current_id}... ⏭️  过滤摘要类标题", "filtered", show_in_all=False)
                        current_id -= 1
                        continue
                    
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
        logger.info("JINSE SCRAPING SESSION SUMMARY")
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
