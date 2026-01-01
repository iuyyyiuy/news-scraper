"""
Manual Scraper - 手动更新功能
Manual news scraping with sequential source processing and AI filtering
"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from .database_manager import DatabaseManager
from .multi_source_scraper import MultiSourceScraper
from .alert_logger import AlertLogger
from .ai_content_analyzer import AIContentAnalyzer
from scraper.core import Config
from scraper.core.storage import CSVDataStore
import tempfile
import os
import time
import logging
import hashlib

logger = logging.getLogger(__name__)


class EnhancedDuplicateDetector:
    """Multi-layer duplicate detection system for real-time scraping"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
        # In-memory caches for this session
        self.seen_urls = set()
        self.seen_titles = set()
        self.seen_content_hashes = set()
        
        # Load existing data from database
        self._load_existing_data()
    
    def _load_existing_data(self):
        """Load existing URLs, titles, and content hashes from database"""
        try:
            # Get recent articles (last 30 days) to build cache
            result = self.db_manager.supabase.table('articles').select(
                'url, title, body_text'
            ).gte(
                'scraped_at', '2025-12-01T00:00:00'  # Last 30 days
            ).execute()
            
            for article in result.data:
                self.seen_urls.add(article['url'])
                self.seen_titles.add(article['title'].strip().lower())
                
                # Create content hash
                content = article.get('body_text', article['title'])
                content_hash = self._calculate_content_hash(content)
                self.seen_content_hashes.add(content_hash)
            
            logger.info(f"Enhanced duplicate detector loaded {len(self.seen_urls)} URLs, {len(self.seen_titles)} titles")
            
        except Exception as e:
            logger.warning(f"Error loading existing data for duplicate detection: {e}")
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate normalized content hash"""
        import re
        normalized = re.sub(r'[^\w\s]', '', content.lower())
        normalized = ''.join(normalized.split())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def is_duplicate(self, article_data: Dict) -> Dict[str, any]:
        """Check if article is duplicate using multiple methods"""
        url = article_data.get('url', '')
        title = article_data.get('title', '').strip().lower()
        content = article_data.get('content', article_data.get('title', ''))
        
        # Method 1: URL check (most reliable)
        if url in self.seen_urls:
            return {
                'is_duplicate': True,
                'method': 'url_match',
                'confidence': 100,
                'reason': f'URL already exists'
            }
        
        # Method 2: Exact title match
        if title in self.seen_titles:
            return {
                'is_duplicate': True,
                'method': 'title_match',
                'confidence': 95,
                'reason': f'Title already exists'
            }
        
        # Method 3: Content hash match
        content_hash = self._calculate_content_hash(content)
        if content_hash in self.seen_content_hashes:
            return {
                'is_duplicate': True,
                'method': 'content_hash_match',
                'confidence': 90,
                'reason': f'Content already exists'
            }
        
        # Method 4: Similar title check (fuzzy matching)
        similar_title = self._find_similar_title(title)
        if similar_title:
            return {
                'is_duplicate': True,
                'method': 'similar_title',
                'confidence': 80,
                'reason': f'Similar title exists'
            }
        
        return {
            'is_duplicate': False,
            'method': 'none',
            'confidence': 0,
            'reason': 'No duplicates found'
        }
    
    def _find_similar_title(self, title: str) -> str:
        """Find similar titles using simple similarity"""
        title_words = set(title.split())
        
        for existing_title in self.seen_titles:
            existing_words = set(existing_title.split())
            
            # Calculate Jaccard similarity
            intersection = len(title_words & existing_words)
            union = len(title_words | existing_words)
            
            if union > 0:
                similarity = intersection / union
                if similarity > 0.8:  # 80% similarity threshold
                    return existing_title
        
        return None
    
    def add_article(self, article_data: Dict):
        """Add article to seen cache"""
        url = article_data.get('url', '')
        title = article_data.get('title', '').strip().lower()
        content = article_data.get('content', article_data.get('title', ''))
        
        self.seen_urls.add(url)
        self.seen_titles.add(title)
        
        content_hash = self._calculate_content_hash(content)
        self.seen_content_hashes.add(content_hash)


class ManualScraper:
    """手动更新 - Manual news scraper with sequential processing and AI filtering"""
    
    # Security-related keywords for filtering (21 keywords as specified)
    KEYWORDS = [
        "安全问题", "黑客", "被盗", "漏洞", "攻击", "恶意软件", "盗窃",
        "CoinEx", "ViaBTC", "破产", "执法", "监管", "洗钱", "KYC",
        "合规", "牌照", "风控", "诈骗", "突发", "rug pull", "下架"
    ]
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.alert_logger = AlertLogger()
        
        # Initialize enhanced duplicate detector
        self.duplicate_detector = EnhancedDuplicateDetector(self.db_manager)
        
        # Initialize AI content analyzer
        try:
            self.ai_analyzer = AIContentAnalyzer()
            self.use_ai_analysis = True
            logger.info("AI Content Analyzer initialized successfully")
        except ValueError as e:
            self.ai_analyzer = None
            self.use_ai_analysis = False
            logger.warning(f"AI Content Analyzer not available: {e}")
        
        # Create temporary directory for CSV storage
        self.temp_dir = tempfile.mkdtemp()
    
    def 手动更新(self, max_articles: int = 2000, progress_callback: Optional[callable] = None) -> Dict[str, any]:
        """
        手动更新 - Manual news update function
        
        Process:
        1. First scrape BlockBeats (check latest news ID, scrape backward 2000 articles)
        2. Then scrape ForesightNews (check latest news ID, scrape backward 2000 articles)
        3. Use AI to filter duplicates/similar/unrelated news
        4. Real-time update to Supabase database
        5. Extract same content as CSV scraper results
        
        Args:
            max_articles: Maximum articles to scrape per source (default 2000)
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with comprehensive scraping results
        """
        start_time = datetime.now()
        logger.info(f"🚀 Starting 手动更新 at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if progress_callback:
            progress_callback("🚀 开始手动更新...", "info")
        
        # Start alert logging session
        session_id = self.alert_logger.start_scraping_session(['BlockBeats'])
        
        results = {
            'start_time': start_time,
            'session_id': session_id,
            'sources_processed': [],
            'total_articles_found': 0,
            'total_articles_saved': 0,
            'total_duplicates_skipped': 0,
            'ai_filtered_count': 0,
            'errors': [],
            'source_results': {}
        }
        
        # Sequential processing: BlockBeats only (Jinse completely disabled)
        sources = ['blockbeats']
        
        for source in sources:
            try:
                if progress_callback:
                    progress_callback(f"📰 正在处理 {source.upper()}...", "info")
                
                source_result = self._process_source_sequential(
                    source, max_articles, progress_callback
                )
                
                results['sources_processed'].append(source)
                results['source_results'][source] = source_result
                results['total_articles_found'] += source_result['articles_found']
                results['total_articles_saved'] += source_result['articles_saved']
                results['total_duplicates_skipped'] += source_result['duplicates_skipped']
                results['ai_filtered_count'] += source_result.get('ai_filtered', 0)
                
                if source_result['errors']:
                    results['errors'].extend(source_result['errors'])
                
                if progress_callback:
                    progress_callback(
                        f"✅ {source.upper()} 完成: 找到 {source_result['articles_found']} 篇，保存 {source_result['articles_saved']} 篇",
                        "success"
                    )
                
            except Exception as e:
                error_msg = f"Error processing {source}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                results['errors'].append(error_msg)
                
                if progress_callback:
                    progress_callback(f"❌ {source.upper()} 处理失败: {str(e)}", "error")
        
        # Complete the session
        results['end_time'] = datetime.now()
        results['duration'] = (results['end_time'] - results['start_time']).total_seconds()
        
        # End alert logging session
        completed_session = self.alert_logger.end_scraping_session()
        
        # Final summary
        self._log_final_summary(results)
        
        if progress_callback:
            progress_callback(
                f"🎉 手动更新完成! 总共保存 {results['total_articles_saved']} 篇新闻",
                "success"
            )
        
        return results
    
    def _process_source_sequential(self, source: str, max_articles: int, progress_callback: Optional[callable] = None) -> Dict:
        """
        Process a single source sequentially with real-time updates
        
        Args:
            source: Source name ('blockbeats' or 'jinse')
            max_articles: Maximum articles to scrape
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary with source processing results
        """
        logger.info(f"Processing {source} - checking latest news ID and scraping backward {max_articles} articles")
        
        source_start_time = time.time()
        
        try:
            # Create config for this source
            if source == 'blockbeats':
                config = Config(
                    target_url="https://www.theblockbeats.info/newsflash",
                    max_articles=max_articles,
                    request_delay=1.5,
                    timeout=30,
                    max_retries=3
                )
            elif source == 'foresightnews':
                config = Config(
                    target_url="https://foresightnews.pro/news",
                    max_articles=max_articles,
                    request_delay=2.0,  # Slower for Selenium
                    timeout=45,
                    max_retries=2
                )
            else:
                raise ValueError(f"Unknown source: {source}")
            
            # Create temporary data store
            temp_file = os.path.join(self.temp_dir, f"temp_{source}_{int(time.time())}.csv")
            data_store = CSVDataStore(temp_file)
            
            # Date range: last 14 days to ensure we get enough articles
            end_date = date.today()
            start_date = end_date - timedelta(days=14)
            
            if progress_callback:
                progress_callback(f"🔍 {source.upper()}: 检查最新新闻ID...", "info")
            
            # Create scraper for this source
            scraper = MultiSourceScraper(
                config=config,
                data_store=data_store,
                start_date=start_date,
                end_date=end_date,
                keywords_filter=self.KEYWORDS,
                sources=[source],
                enable_deduplication=True
            )
            
            # Run scraper
            if progress_callback:
                progress_callback(f"📥 {source.upper()}: 开始抓取文章...", "info")
            
            scraper.scrape()
            articles = data_store.get_all_articles()
            
            logger.info(f"{source}: Found {len(articles)} articles")
            
            if progress_callback:
                progress_callback(f"📊 {source.upper()}: 找到 {len(articles)} 篇文章", "info")
            
            # AI filtering if available
            if self.use_ai_analysis and articles:
                if progress_callback:
                    progress_callback(f"🤖 {source.upper()}: AI分析中...", "info")
                
                articles = self._process_articles_with_ai(articles, source, progress_callback)
                
                if progress_callback:
                    progress_callback(f"🤖 {source.upper()}: AI分析完成，剩余 {len(articles)} 篇", "info")
            
            # Real-time database updates
            articles_saved = 0
            duplicates_skipped = 0
            ai_filtered = 0
            errors = []
            
            if progress_callback:
                progress_callback(f"💾 {source.upper()}: 开始保存到数据库...", "info")
            
            for i, article in enumerate(articles):
                try:
                    # Enhanced duplicate check FIRST (before AI analysis)
                    article_data = {
                        'url': article.url,
                        'title': article.title,
                        'content': getattr(article, 'body_text', article.title)
                    }
                    
                    duplicate_result = self.duplicate_detector.is_duplicate(article_data)
                    
                    if duplicate_result['is_duplicate']:
                        duplicates_skipped += 1
                        if progress_callback and duplicates_skipped % 5 == 0:
                            progress_callback(
                                f"💾 {source.upper()}: 跳过重复文章 {duplicates_skipped} 篇 ({duplicate_result['method']})",
                                "info"
                            )
                        continue
                    
                    # Check AI relevance if available
                    should_save = True
                    if hasattr(article, 'ai_analysis') and article.ai_analysis:
                        relevance = article.ai_analysis.get('relevance', {})
                        # More lenient relevance threshold - only filter out clearly irrelevant content
                        if not relevance.get('is_relevant', True) and relevance.get('relevance_score', 100) < 20:
                            should_save = False
                            ai_filtered += 1
                    
                    if should_save:
                        # Find matched keywords
                        title_lower = article.title.lower()
                        body_lower = getattr(article, 'body_text', '').lower()
                        matched_keywords = [kw for kw in self.KEYWORDS if kw.lower() in title_lower or kw.lower() in body_lower]
                        
                        if matched_keywords:
                            if self._store_article_realtime(article, matched_keywords, source):
                                articles_saved += 1
                                
                                # Add to duplicate detector cache
                                self.duplicate_detector.add_article(article_data)
                                
                                # Progress update every 5 articles
                                if articles_saved % 5 == 0 and progress_callback:
                                    progress_callback(
                                        f"💾 {source.upper()}: 已保存 {articles_saved}/{len(articles)} 篇",
                                        "success"
                                    )
                            else:
                                duplicates_skipped += 1
                    
                except Exception as e:
                    error_msg = f"Error saving article from {source}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            # Calculate duration
            duration = time.time() - source_start_time
            
            # Log source completion
            self.alert_logger.log_scraping_operation(
                source=source.upper(),
                articles_found=len(articles),
                articles_stored=articles_saved,
                articles_duplicate=duplicates_skipped,
                duration_seconds=duration,
                errors=errors if errors else None
            )
            
            return {
                'source': source,
                'articles_found': len(articles),
                'articles_saved': articles_saved,
                'duplicates_skipped': duplicates_skipped,
                'ai_filtered': ai_filtered,
                'duration': duration,
                'errors': errors
            }
            
        except Exception as e:
            error_msg = f"Critical error processing {source}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                'source': source,
                'articles_found': 0,
                'articles_saved': 0,
                'duplicates_skipped': 0,
                'ai_filtered': 0,
                'duration': time.time() - source_start_time,
                'errors': [error_msg]
            }
    
    def _process_articles_with_ai(self, articles: List, source: str, progress_callback: Optional[callable] = None) -> List:
        """
        Process articles with AI analysis for relevance and duplicate detection
        
        Args:
            articles: List of article objects
            source: Source name for logging
            progress_callback: Optional progress callback
            
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
            
            # Process articles with enhanced duplicate detection + AI analysis
            analyzed_articles = []
            duplicates_filtered = 0
            
            for i, article_dict in enumerate(article_dicts):
                try:
                    # First: Enhanced duplicate check (fast)
                    enhanced_duplicate_check = self.duplicate_detector.is_duplicate({
                        'url': getattr(article_dict['original_article'], 'url', ''),
                        'title': article_dict['title'],
                        'content': article_dict['content']
                    })
                    
                    if enhanced_duplicate_check['is_duplicate']:
                        duplicates_filtered += 1
                        self.alert_logger.log_info(
                            component="EnhancedDuplicateDetector",
                            message=f"{source}: Duplicate detected by {enhanced_duplicate_check['method']}",
                            details={
                                "title": article_dict['title'][:100],
                                "method": enhanced_duplicate_check['method'],
                                "confidence": enhanced_duplicate_check['confidence']
                            }
                        )
                        continue
                    
                    # Second: AI relevance analysis (if not duplicate)
                    relevance = self.ai_analyzer.analyze_content_relevance(
                        article_dict['title'],
                        article_dict['content'],
                        article_dict.get('matched_keywords', [])
                    )
                    
                    # Third: AI duplicate check against database (slower but more thorough)
                    duplicate_check = self.ai_analyzer.detect_duplicate_content(
                        {'title': article_dict['title'], 'content': article_dict['content']},
                        recent_db_articles
                    )
                    
                    # Also check against previously processed articles in this session
                    if not duplicate_check['is_duplicate'] and analyzed_articles:
                        session_duplicate_check = self.ai_analyzer.detect_duplicate_content(
                            {'title': article_dict['title'], 'content': article_dict['content']},
                            [{'title': a['title'], 'content': a['content']} for a in analyzed_articles]
                        )
                        if session_duplicate_check['is_duplicate']:
                            duplicate_check = session_duplicate_check
                    
                    # Add analysis results to original article
                    original_article = article_dict['original_article']
                    original_article.ai_analysis = {
                        'relevance': relevance,
                        'duplicate_check': duplicate_check,
                        'enhanced_duplicate_check': enhanced_duplicate_check,
                        'analyzed_at': datetime.now().isoformat()
                    }
                    
                    # Only add to analyzed list if not a duplicate
                    if not duplicate_check['is_duplicate']:
                        analyzed_articles.append({
                            'title': article_dict['title'],
                            'content': article_dict['content'],
                            'original_article': original_article
                        })
                        
                        # Add to enhanced duplicate detector cache
                        self.duplicate_detector.add_article({
                            'url': getattr(original_article, 'url', ''),
                            'title': article_dict['title'],
                            'content': article_dict['content']
                        })
                    else:
                        duplicates_filtered += 1
                        self.alert_logger.log_info(
                            component="AIContentAnalyzer",
                            message=f"{source}: AI duplicate detected",
                            details={
                                "title": article_dict['title'][:100],
                                "similarity_score": duplicate_check['similarity_score'],
                                "duplicate_type": duplicate_check.get('duplicate_type', 'unknown')
                            }
                        )
                
                except Exception as e:
                    logger.error(f"Error analyzing article {i} from {source}: {e}")
                    # Keep article without analysis
                    original_article = article_dict['original_article']
                    analyzed_articles.append({
                        'title': article_dict['title'],
                        'content': article_dict['content'],
                        'original_article': original_article
                    })
            
            # Extract original articles from analyzed results
            filtered_articles = [item['original_article'] for item in analyzed_articles]
            
            # Log AI filtering results
            original_count = len(articles)
            filtered_count = len(filtered_articles)
            
            if duplicates_filtered > 0:
                self.alert_logger.log_info(
                    component="AIContentAnalyzer",
                    message=f"{source}: AI duplicate filtering completed",
                    details={
                        "source": source,
                        "original_count": original_count,
                        "filtered_count": filtered_count,
                        "duplicates_removed": duplicates_filtered,
                        "database_articles_checked": len(recent_db_articles)
                    }
                )
            
            return filtered_articles
            
        except Exception as e:
            logger.error(f"Error in AI article processing for {source}: {e}")
            self.alert_logger.log_error(
                component="AIContentAnalyzer",
                message=f"Error in AI article processing for {source}",
                details={"article_count": len(articles)},
                exception=e
            )
            return articles
    
    def _get_recent_database_articles(self, days: int = 7, limit: int = 50) -> List[Dict[str, str]]:
        """
        Get recent articles from database for duplicate comparison
        
        Args:
            days: Number of days to look back
            limit: Maximum number of articles to retrieve
            
        Returns:
            List of recent articles with title and content
        """
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
            
            logger.info(f"Retrieved {len(recent_articles)} recent articles for duplicate comparison")
            return recent_articles
            
        except Exception as e:
            logger.error(f"Error retrieving recent database articles: {e}")
            return []
    
    def _store_article_realtime(self, article, matched_keywords: List[str], source: str) -> bool:
        """
        Store article in database with real-time updates
        Same content extraction as CSV scraper results
        
        Args:
            article: Article object from scraper
            matched_keywords: List of keywords that matched this article
            source: Source name
            
        Returns:
            True if stored, False if duplicate
        """
        try:
            # Check if article already exists
            if self.db_manager.check_article_exists(article.url):
                return False
            
            # Prepare article data - match CSV structure exactly
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
            
            # Extract content same as CSV scraper
            article_data = {
                'publication_date': pub_date_str,
                'title': article.title,
                'body_text': getattr(article, 'body_text', article.title),
                'url': article.url,
                'source': self._normalize_source_name(source),
                'matched_keywords': matched_keywords
            }
            
            # Real-time insert into Supabase
            return self.db_manager.insert_article(article_data)
            
        except Exception as e:
            logger.error(f"Error storing article from {source}: {e}")
            return False
    
    def _normalize_source_name(self, source: str) -> str:
        """Normalize source name to match CSV format"""
        if source.lower() == 'blockbeats':
            return 'BlockBeats'
        elif source.lower() == 'foresightnews':
            return 'ForesightNews'
        elif source.lower() == 'jinse':
            return 'Jinse'
        else:
            return source.title()
    
    def _log_final_summary(self, results: Dict):
        """Log comprehensive final summary"""
        logger.info("=" * 60)
        logger.info("手动更新完成摘要")
        logger.info("=" * 60)
        
        for source in results['sources_processed']:
            if source in results['source_results']:
                src_result = results['source_results'][source]
                logger.info(
                    f"{source.upper()}: "
                    f"找到 {src_result['articles_found']} 篇, "
                    f"保存 {src_result['articles_saved']} 篇, "
                    f"重复 {src_result['duplicates_skipped']} 篇, "
                    f"AI过滤 {src_result.get('ai_filtered', 0)} 篇"
                )
        
        logger.info("-" * 60)
        logger.info(f"总计找到文章: {results['total_articles_found']}")
        logger.info(f"总计保存文章: {results['total_articles_saved']}")
        logger.info(f"总计重复跳过: {results['total_duplicates_skipped']}")
        logger.info(f"AI过滤文章: {results['ai_filtered_count']}")
        logger.info(f"处理耗时: {results['duration']:.2f} 秒")
        
        if results['errors']:
            logger.info(f"遇到错误: {len(results['errors'])}")
        else:
            logger.info("未遇到错误")
        
        logger.info("=" * 60)