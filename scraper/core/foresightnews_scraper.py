"""
ForesightNews (foresightnews.pro) specific scraper using Selenium for anti-bot bypass.
"""
import logging
import time
import random
from typing import List, Optional
from datetime import datetime, date
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup

from .storage import DataStore
from .models import Config, ScrapingResult, Article

logger = logging.getLogger(__name__)


class ForesightNewsScraper:
    """
    Specialized scraper for ForesightNews (foresightnews.pro).
    
    Uses Selenium WebDriver to bypass anti-bot protection.
    Article URLs follow the pattern:
    https://foresightnews.pro/news/detail/{id}
    
    This scraper:
    1. Uses browser automation to bypass JavaScript challenges
    2. Finds the latest article IDs from the main page
    3. Iterates backwards through IDs
    4. Stops when reaching the start_date or max_articles limit
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
        Initialize the ForesightNews scraper.
        
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
        
        self.driver = None
        self.base_url = "https://foresightnews.pro/news/detail/"
        
    def _log(self, message: str, log_type: str = 'info', show_in_all: bool = None):
        """Helper to log messages if callback is available."""
        if show_in_all is None:
            show_in_all = log_type not in ['filtered', 'skipped']
        
        if self.log_callback:
            self.log_callback(message, log_type, 'foresightnews', show_in_all)
        logger.info(message)
    
    def _setup_driver(self):
        """Setup Selenium WebDriver with anti-detection measures"""
        try:
            chrome_options = Options()
            
            # Anti-detection measures
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')  # Faster loading
            chrome_options.add_argument('--disable-javascript-harmony-shipping')
            chrome_options.add_argument('--disable-background-timer-throttling')
            chrome_options.add_argument('--disable-backgrounding-occluded-windows')
            chrome_options.add_argument('--disable-renderer-backgrounding')
            
            # User agent rotation
            user_agents = [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
            
            # Exclude automation flags
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Create driver
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Execute script to hide webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            self._log("✅ WebDriver initialized successfully", "info")
            return True
            
        except Exception as e:
            self._log(f"❌ Failed to setup WebDriver: {str(e)}", "error")
            return False
    
    def _human_delay(self, min_seconds=1, max_seconds=3):
        """Add human-like random delays"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def find_latest_article_ids(self) -> List[int]:
        """
        Find the latest article IDs by scraping the main news page.
        
        Returns:
            List of article IDs sorted in descending order
        """
        try:
            self._log("🔍 查找最新文章ID...", "info")
            
            # Load main news page
            self.driver.get("https://foresightnews.pro/news")
            self._human_delay(3, 5)  # Wait for page to load
            
            # Wait for articles to load
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/news/detail/"]'))
                )
            except TimeoutException:
                self._log("⚠️  等待文章加载超时", "error")
                return []
            
            # Get page source and parse
            page_source = self.driver.page_source
            
            # Extract article IDs
            pattern = r'/news/detail/(\d+)'
            matches = re.findall(pattern, page_source)
            
            if matches:
                # Convert to integers and remove duplicates
                article_ids = list(set([int(match) for match in matches]))
                article_ids.sort(reverse=True)  # Sort descending
                
                self._log(f"✅ 找到 {len(article_ids)} 个文章ID，最新ID: {article_ids[0]}", "info")
                return article_ids[:100]  # Return top 100 IDs for more coverage
            else:
                self._log("❌ 未找到任何文章ID", "error")
                return []
                
        except Exception as e:
            self._log(f"❌ 查找文章ID失败: {str(e)}", "error")
            return []
    
    def _parse_foresightnews_article(self, article_id: int) -> Optional[Article]:
        """
        Parse a ForesightNews article using Selenium.
        
        Args:
            article_id: Article ID to scrape
            
        Returns:
            Article object or None if failed
        """
        try:
            article_url = f"{self.base_url}{article_id}"
            
            # Load article page
            self.driver.get(article_url)
            self._human_delay(2, 4)
            
            # Wait for content to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'h1'))
                )
            except TimeoutException:
                # Article might not exist or be blocked
                return None
            
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract title
            title_selectors = ['h1', '.title', '[class*="title"]']
            title = None
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) > 5 and 'ForesightNews' not in title:
                        break
            
            if not title:
                return None
            
            # Extract content
            content_selectors = [
                '.content', '.article-content', '[class*="content"]', 
                'article', 'main', '[class*="body"]'
            ]
            body_text = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    body_text = content_elem.get_text(strip=True)
                    if len(body_text) > 50:
                        break
            
            # Extract date - try multiple methods
            publication_date = None
            year = datetime.now().year
            
            # Method 1: Look for date elements
            date_selectors = ['.date', '.time', '[class*="date"]', '[class*="time"]', 'time']
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    # Try to parse various date formats
                    date_patterns = [
                        r'(\d{4})-(\d{1,2})-(\d{1,2})',  # 2024-12-29
                        r'(\d{1,2})月(\d{1,2})日',        # 12月29日
                        r'(\d{1,2})/(\d{1,2})/(\d{4})'   # 12/29/2024
                    ]
                    
                    for pattern in date_patterns:
                        match = re.search(pattern, date_text)
                        if match:
                            try:
                                if pattern.endswith(r'(\d{4})'):  # Full year format
                                    if '月' in pattern:
                                        month, day = int(match.group(1)), int(match.group(2))
                                        publication_date = datetime(year, month, day)
                                    else:
                                        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                                        publication_date = datetime(year, month, day)
                                else:
                                    month, day = int(match.group(1)), int(match.group(2))
                                    publication_date = datetime(year, month, day)
                                break
                            except ValueError:
                                continue
                    if publication_date:
                        break
            
            # Fallback: use current date
            if not publication_date:
                publication_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Create article
            article = Article(
                url=article_url,
                title=title,
                publication_date=publication_date,
                author="ForesightNews",
                body_text=body_text,
                scraped_at=datetime.now(),
                source_website="foresightnews.pro"
            )
            
            return article
            
        except Exception as e:
            logger.error(f"Error parsing ForesightNews article {article_id}: {e}")
            return None
    
    def scrape(self) -> ScrapingResult:
        """
        Execute the scraping workflow.
        
        Returns:
            ScrapingResult with statistics
        """
        start_time = time.time()
        errors: List[str] = []
        articles_scraped = 0
        articles_failed = 0
        articles_checked = 0
        
        logger.info(f"Starting ForesightNews scraping session")
        logger.info(f"Date range: {self.start_date.date()} to {self.end_date.date()}")
        logger.info(f"Keywords: {self.keywords_filter}")
        logger.info(f"Max articles: {self.config.max_articles}")
        
        try:
            # Setup WebDriver
            if not self._setup_driver():
                raise Exception("Failed to setup WebDriver")
            
            # Find latest article IDs
            article_ids = self.find_latest_article_ids()
            if not article_ids:
                raise Exception("No article IDs found")
            
            # Process articles
            consecutive_failures = 0
            max_consecutive_failures = 30  # Increased for more coverage
            articles_before_start_date = 0
            max_articles_before_start_date = 10  # Increased tolerance
            
            for article_id in article_ids:
                if articles_checked >= self.config.max_articles:
                    break
                
                if consecutive_failures >= max_consecutive_failures:
                    self._log(f"⏹️  停止: {max_consecutive_failures} 个连续失败", "info")
                    break
                
                if articles_before_start_date >= max_articles_before_start_date:
                    self._log(f"⏹️  停止: 找到 {max_articles_before_start_date} 个连续的过早文章", "info")
                    break
                
                articles_checked += 1
                
                try:
                    # Parse article
                    article = self._parse_foresightnews_article(article_id)
                    
                    if not article:
                        consecutive_failures += 1
                        self._log(f"[{articles_checked}] ID {article_id}... ⏭️  文章不存在或无法访问", "filtered", show_in_all=False)
                        continue
                    
                    # Reset consecutive failures
                    consecutive_failures = 0
                    
                    # Check date range
                    if article.publication_date:
                        if article.publication_date < self.start_date:
                            articles_before_start_date += 1
                            self._log(f"[{articles_checked}] ID {article_id}... ⏭️  日期过早 ({article.publication_date.date()})", "filtered", show_in_all=False)
                            continue
                        elif article.publication_date > self.end_date:
                            self._log(f"[{articles_checked}] ID {article_id}... ⏭️  日期太新 ({article.publication_date.date()})", "filtered", show_in_all=False)
                            continue
                        else:
                            articles_before_start_date = 0  # Reset counter
                    
                    # Check keywords
                    if self.keywords_filter:
                        article_text = f"{article.title} {article.body_text}".lower()
                        matched = [kw for kw in self.keywords_filter if kw in article_text]
                        
                        if not matched:
                            self._log(f"[{articles_checked}] ID {article_id}... ⏭️  无匹配关键词", "filtered", show_in_all=False)
                            continue
                        
                        article.matched_keywords = matched
                    
                    # Save article
                    if self.data_store.save_article(article):
                        articles_scraped += 1
                        self._log(
                            f"[{articles_scraped}] ID {article_id}... ✅ 已保存: {article.title[:30]}...",
                            "success"
                        )
                        
                        # Notify progress
                        if self.progress_callback:
                            self.progress_callback(articles_checked, articles_scraped)
                    
                    # Human-like delay between articles
                    self._human_delay(1, 2)
                    
                except Exception as e:
                    articles_failed += 1
                    error_msg = f"ID {article_id} 处理失败: {str(e)}"
                    errors.append(error_msg)
                    self._log(f"⚠️  {error_msg}", "filtered", show_in_all=False)
            
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
            # Clean up WebDriver
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
    
    def _log_session_summary(self, result: ScrapingResult) -> None:
        """Log a summary of the scraping session."""
        logger.info("=" * 60)
        logger.info("FORESIGHTNEWS SCRAPING SESSION SUMMARY")
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