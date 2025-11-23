"""
Multi-source scraper that coordinates scraping from multiple news sources.
"""
import logging
from typing import List, Dict, Optional
from datetime import date
from concurrent.futures import ThreadPoolExecutor, as_completed

from .models import Config, ScrapingResult, Article
from .storage import DataStore
from .blockbeats_scraper import BlockBeatsScraper
from .jinse_scraper import JinseScraper
from .panews_scraper import PANewsScraper
from .deduplicator import DeduplicationEngine


logger = logging.getLogger(__name__)


class MultiSourceScraper:
    """
    Coordinates scraping from multiple news sources and deduplicates results.
    
    Supports:
    - BlockBeats (theblockbeats.info)
    - Jinse (jinse.cn)
    - PANews (panewslab.com)
    """
    
    AVAILABLE_SOURCES = {
        'blockbeats': BlockBeatsScraper,
        'jinse': JinseScraper,
        'panews': PANewsScraper
    }
    
    def __init__(
        self,
        config: Config,
        data_store: DataStore,
        start_date: date,
        end_date: date,
        keywords_filter: List[str],
        sources: List[str] = None,
        enable_deduplication: bool = True,
        progress_callback=None,
        log_callback=None
    ):
        """
        Initialize the multi-source scraper.
        
        Args:
            config: Configuration object
            data_store: Data storage implementation
            start_date: Start date for filtering articles
            end_date: End date for filtering articles
            keywords_filter: Keywords to filter articles
            sources: List of source names to scrape (default: all)
            enable_deduplication: Whether to deduplicate results
            progress_callback: Optional callback function(source, articles_found, articles_scraped)
            log_callback: Optional callback function(message, log_type) for logging
        """
        self.config = config
        self.data_store = data_store
        self.start_date = start_date
        self.end_date = end_date
        self.keywords_filter = keywords_filter
        self.enable_deduplication = enable_deduplication
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        
        # Validate and set sources
        if sources is None:
            self.sources = list(self.AVAILABLE_SOURCES.keys())
        else:
            self.sources = []
            for source in sources:
                if source.lower() in self.AVAILABLE_SOURCES:
                    self.sources.append(source.lower())
                else:
                    logger.warning(f"Unknown source: {source}, skipping")
        
        if not self.sources:
            raise ValueError("No valid sources specified")
        
        # Initialize deduplicator
        self.deduplicator = DeduplicationEngine() if enable_deduplication else None
        
        # Track per-source results
        self.source_results: Dict[str, ScrapingResult] = {}
        self.source_articles: Dict[str, List[Article]] = {}
    
    def _log(self, message: str, log_type: str = 'info', show_in_all: bool = True):
        """Helper to log messages if callback is available."""
        if self.log_callback:
            self.log_callback(message, log_type, show_in_all)
        logger.info(message)
    
    def _create_scraper(self, source: str):
        """
        Create a scraper instance for the given source.
        
        Args:
            source: Source name
            
        Returns:
            Scraper instance
        """
        scraper_class = self.AVAILABLE_SOURCES[source]
        
        # Create a temporary data store for this source
        from .storage import InMemoryDataStore
        temp_store = InMemoryDataStore()
        
        # Create progress callback that includes source name
        def source_progress_callback(articles_found, articles_scraped):
            if self.progress_callback:
                self.progress_callback(source, articles_found, articles_scraped)
        
        return scraper_class(
            config=self.config,
            data_store=temp_store,
            start_date=self.start_date,
            end_date=self.end_date,
            keywords_filter=self.keywords_filter,
            progress_callback=source_progress_callback,
            log_callback=self.log_callback
        )
    
    def scrape_source(self, source: str) -> tuple:
        """
        Scrape a single source.
        
        Args:
            source: Source name
            
        Returns:
            Tuple of (source_name, scraping_result, articles_list)
        """
        # Start message removed
        
        try:
            scraper = self._create_scraper(source)
            result = scraper.scrape()
            
            # Get articles from the temporary store
            articles = scraper.data_store.get_all_articles()
            
            self._log(
                f"✅ {source.upper()} 完成: {result.articles_scraped} 篇文章",
                "success"
            )
            
            return (source, result, articles)
            
        except Exception as e:
            error_msg = f"❌ {source.upper()} 失败: {str(e)}"
            self._log(error_msg, "error")
            logger.error(error_msg, exc_info=True)
            
            # Return empty result
            from .models import ScrapingResult
            return (source, ScrapingResult(0, 0, 0, 0.0, [str(e)]), [])
    
    def scrape(self, parallel: bool = True) -> ScrapingResult:
        """
        Execute scraping from all configured sources.
        
        Args:
            parallel: Whether to scrape sources in parallel (default: True)
            
        Returns:
            Combined ScrapingResult with statistics
        """
        import time
        start_time = time.time()
        
        self._log("=" * 60, "info")
        self._log("开始多源新闻抓取", "info")
        self._log(f"来源: {', '.join([s.upper() for s in self.sources])}", "info")
        self._log(f"日期范围: {self.start_date} 到 {self.end_date}", "info")
        self._log(f"关键词: {self.keywords_filter if self.keywords_filter else '无'}", "info")
        self._log(f"去重: {'启用' if self.enable_deduplication else '禁用'}", "info")
        self._log("=" * 60, "info")
        
        all_articles = []
        total_checked = 0
        total_scraped = 0
        total_failed = 0
        all_errors = []
        
        if parallel and len(self.sources) > 1:
            # Scrape sources in parallel
            with ThreadPoolExecutor(max_workers=len(self.sources)) as executor:
                futures = {
                    executor.submit(self.scrape_source, source): source
                    for source in self.sources
                }
                
                for future in as_completed(futures):
                    source, result, articles = future.result()
                    
                    # Store results
                    self.source_results[source] = result
                    self.source_articles[source] = articles
                    
                    # Aggregate statistics
                    total_checked += result.total_articles_found
                    total_scraped += result.articles_scraped
                    total_failed += result.articles_failed
                    all_errors.extend(result.errors)
                    all_articles.extend(articles)
        else:
            # Scrape sources sequentially
            for source in self.sources:
                source, result, articles = self.scrape_source(source)
                
                # Store results
                self.source_results[source] = result
                self.source_articles[source] = articles
                
                # Aggregate statistics
                total_checked += result.total_articles_found
                total_scraped += result.articles_scraped
                total_failed += result.articles_failed
                all_errors.extend(result.errors)
                all_articles.extend(articles)
        
        # Deduplicate if enabled
        articles_before_dedup = len(all_articles)
        duplicates_removed = 0
        
        if self.enable_deduplication and self.deduplicator and len(all_articles) > 1:
            self._log("🔍 开始去重处理...", "info")
            all_articles = self.deduplicator.deduplicate(all_articles)
            duplicates_removed = articles_before_dedup - len(all_articles)
            self._log(f"✅ 去重完成: 移除 {duplicates_removed} 篇重复文章", "success")
        
        # Save all unique articles to the main data store
        saved_count = 0
        for article in all_articles:
            if self.data_store.save_article(article):
                saved_count += 1
        
        # Calculate duration
        duration_seconds = time.time() - start_time
        
        # Create combined result
        result = ScrapingResult(
            total_articles_found=total_checked,
            articles_scraped=saved_count,
            articles_failed=total_failed,
            duration_seconds=duration_seconds,
            errors=all_errors
        )
        
        # Log summary
        self._log_session_summary(result, duplicates_removed)
        
        return result
    
    def _log_session_summary(self, result: ScrapingResult, duplicates_removed: int) -> None:
        """Log a summary of the multi-source scraping session."""
        self._log("=" * 60, "info")
        self._log("多源抓取会话摘要", "info")
        self._log("=" * 60, "info")
        
        # Per-source statistics
        for source in self.sources:
            if source in self.source_results:
                src_result = self.source_results[source]
                self._log(
                    f"{source.upper()}: "
                    f"检查 {src_result.total_articles_found} 篇, "
                    f"抓取 {src_result.articles_scraped} 篇, "
                    f"失败 {src_result.articles_failed} 篇",
                    "info"
                )
        
        self._log("-" * 60, "info")
        self._log(f"总计检查文章: {result.total_articles_found}", "info")
        self._log(f"总计抓取文章: {result.articles_scraped + duplicates_removed}", "info")
        
        if self.enable_deduplication:
            self._log(f"移除重复文章: {duplicates_removed}", "info")
            self._log(f"最终唯一文章: {result.articles_scraped}", "info")
        
        self._log(f"失败文章: {result.articles_failed}", "info")
        self._log(f"耗时: {result.duration_seconds:.2f} 秒", "info")
        
        if result.errors:
            self._log(f"遇到错误: {len(result.errors)}", "info")
        else:
            self._log("未遇到错误", "info")
        
        self._log("=" * 60, "info")
    
    def get_source_results(self) -> Dict[str, ScrapingResult]:
        """
        Get per-source scraping results.
        
        Returns:
            Dictionary mapping source names to their ScrapingResult
        """
        return self.source_results
    
    def get_source_articles(self) -> Dict[str, List[Article]]:
        """
        Get per-source article lists.
        
        Returns:
            Dictionary mapping source names to their article lists
        """
        return self.source_articles
