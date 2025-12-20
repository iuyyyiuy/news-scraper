"""
HTML parser for extracting article data from news websites.
"""
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin
import re
import os
import logging
from pathlib import Path
from dateutil import parser as date_parser

from scraper.core.models import Article

# Setup logging
logger = logging.getLogger(__name__)


class HTMLParser:
    """
    Parses HTML content to extract article data.
    
    Uses CSS selectors to extract article information with fallback logic
    when selectors don't match. Includes debugging capabilities and enhanced
    error handling for better resilience.
    """
    
    def __init__(self, selectors: Optional[dict] = None, debug_mode: bool = False):
        """
        Initialize the HTML parser.
        
        Args:
            selectors: Dictionary of CSS selectors for article elements.
                      Expected keys: 'article_links', 'title', 'date', 'author', 'body'
            debug_mode: Enable HTML capture for debugging failed parsing attempts
        """
        self.selectors = selectors or {}
        self.debug_mode = debug_mode
        self.debug_dir = Path("debug_html")
        
        # Create debug directory if needed
        if self.debug_mode:
            self.debug_dir.mkdir(exist_ok=True)
            self._cleanup_old_debug_files()
    
    def _cleanup_old_debug_files(self):
        """Remove debug HTML files older than 7 days."""
        try:
            import time
            current_time = time.time()
            seven_days_ago = current_time - (7 * 24 * 60 * 60)
            
            for file_path in self.debug_dir.glob("*.html"):
                if file_path.stat().st_mtime < seven_days_ago:
                    file_path.unlink()
                    logger.info(f"Cleaned up old debug file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup old debug files: {e}")
    
    def _save_debug_html(self, html: str, url: str, error_msg: str):
        """Save HTML content for debugging when parsing fails."""
        if not self.debug_mode:
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Clean URL for filename
            url_clean = re.sub(r'[^\w\-_.]', '_', url.split('/')[-1] or 'unknown')
            filename = f"{timestamp}_{url_clean}_error.html"
            filepath = self.debug_dir / filename
            
            # Create debug info header
            debug_info = f"""
<!-- DEBUG INFO -->
<!-- URL: {url} -->
<!-- Error: {error_msg} -->
<!-- Timestamp: {datetime.now().isoformat()} -->
<!-- End DEBUG INFO -->

"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(debug_info + html)
            
            logger.info(f"Saved debug HTML: {filepath}")
            
        except Exception as e:
            logger.warning(f"Failed to save debug HTML: {e}")
        
    def parse_article_list(self, html: str, base_url: str) -> List[str]:
        """
        Extract article URLs from a listing page.
        
        Args:
            html: HTML content of the listing page
            base_url: Base URL for resolving relative links
            
        Returns:
            List of absolute article URLs
        """
        soup = BeautifulSoup(html, 'lxml')
        article_urls = []
        
        # Try using configured selector first
        if 'article_links' in self.selectors:
            links = soup.select(self.selectors['article_links'])
            for link in links:
                href = link.get('href')
                if href:
                    absolute_url = urljoin(base_url, href)
                    article_urls.append(absolute_url)
        else:
            # Fallback: find all links that look like article links
            article_urls = self._extract_article_links_fallback(soup, base_url)
        
        return article_urls

    def _extract_date_from_body(self, body_text: str) -> Optional[datetime]:
        """
        Extract date from body text using comprehensive patterns.
        
        Args:
            body_text: Article body text
            
        Returns:
            Extracted datetime or None
        """
        import re
        from datetime import datetime
        
        # Pattern 1: "2025-12-09 05:56" (full datetime)
        pattern1 = r'(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{1,2})'
        match = re.search(pattern1, body_text)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            hour = int(match.group(4))
            minute = int(match.group(5))
            try:
                return datetime(year, month, day, hour, minute)
            except ValueError:
                pass
        
        # Pattern 2: "BlockBeats 消息，11 月 11 日，" or similar
        pattern2 = r'BlockBeats\s*消息\s*，\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日'
        match = re.search(pattern2, body_text)
        if match:
            month = int(match.group(1))
            day = int(match.group(2))
            year = datetime.now().year
            try:
                return datetime(year, month, day)
            except ValueError:
                pass
        
        # Pattern 3: "2025-11-11" or "2025/11/11" (date only)
        pattern3 = r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})'
        match = re.search(pattern3, body_text)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            try:
                return datetime(year, month, day)
            except ValueError:
                pass
        
        # Pattern 4: "11月11日" without BlockBeats prefix
        pattern4 = r'(\d{1,2})\s*月\s*(\d{1,2})\s*日'
        match = re.search(pattern4, body_text[:200])  # Check first 200 chars
        if match:
            month = int(match.group(1))
            day = int(match.group(2))
            year = datetime.now().year
            try:
                return datetime(year, month, day)
            except ValueError:
                pass
        
        return None
    
    def _extract_source_from_content(self, text: str) -> Optional[str]:
        """
        Extract source information from article content.
        
        Args:
            text: Article content
            
        Returns:
            Source name or None
        """
        # Pattern 1: "据 Trend News 监测" or similar
        pattern1 = r'据\s+([^监测]+?)\s*监测'
        match = re.search(pattern1, text)
        if match:
            return match.group(1).strip()
        
        # Pattern 2: "BlockBeats 消息" (default source)
        if 'BlockBeats' in text:
            return 'BlockBeats'
        
        # Pattern 3: Other common source patterns
        source_patterns = [
            r'来源[:：]\s*([^\n,，。]+)',
            r'消息来源[:：]\s*([^\n,，。]+)',
            r'据\s+([^报道]+?)\s*报道'
        ]
        
        for pattern in source_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
    
    def parse_article(self, html: str, url: str, source_website: str) -> Article:
        """
        Extract article data from an article page.
        
        Args:
            html: HTML content of the article page
            url: URL of the article
            source_website: Source website domain
            
        Returns:
            Article object with extracted data
            
        Raises:
            ValueError: If required fields (title, body) cannot be extracted
        """
        soup = BeautifulSoup(html, 'lxml')
        
        try:
            # Extract title with enhanced fallback
            title = self._extract_title_enhanced(soup)
            if not title:
                error_msg = "Could not extract article title"
                self._save_debug_html(html, url, error_msg)
                raise ValueError(error_msg)
            
            # Extract publication date with enhanced fallback
            publication_date = self._extract_date_enhanced(soup)
            
            # Extract author with enhanced fallback
            author = self._extract_author_enhanced(soup)
            
            # Extract body text with enhanced fallback
            body_text = self._extract_body_enhanced(soup, source_website)
            
            if not body_text:
                error_msg = "Could not extract article body"
                self._save_debug_html(html, url, error_msg)
                raise ValueError(error_msg)
            
            # Clean the extracted content
            body_text = self._extract_clean_content(body_text)
            
            # If no publication date found, try to extract from body text
            if not publication_date:
                publication_date = self._extract_date_from_body(body_text)
            
            # Try to extract source information from content if not already set
            extracted_source = self._extract_source_from_content(body_text)
            if extracted_source and extracted_source != source_website:
                # You could store this as additional metadata or use it to enhance the source_website
                pass
            
            logger.info(f"Successfully parsed article: {title[:50]}...")
            
            return Article(
                url=url,
                title=title,
                publication_date=publication_date,
                author=author,
                body_text=body_text,
                scraped_at=datetime.now(),
                source_website=source_website
            )
            
        except Exception as e:
            logger.error(f"Failed to parse article from {url}: {e}")
            self._save_debug_html(html, url, str(e))
            raise
    
    def _extract_title_enhanced(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Enhanced title extraction with comprehensive fallback strategies.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Extracted title or None
        """
        # Strategy 1: Try configured selector
        if 'title' in self.selectors:
            element = soup.select_one(self.selectors['title'])
            if element:
                title = self._clean_text(element.get_text())
                if title:
                    logger.debug(f"Title extracted using configured selector: {title[:50]}...")
                    return title
        
        # Strategy 2: Try common title selectors (expanded list)
        common_selectors = [
            'h1.article-title',
            'h1.entry-title', 
            'h1[itemprop="headline"]',
            'article h1',
            '.article-header h1',
            '.post-title h1',
            '.news-title h1',
            '.content-title h1',
            'h1.title',
            'h1.post-title',
            'h1.news-title',
            # Flash news specific selectors
            '.flash-top h3',
            '.flash-item h3',
            '.flash-content h3',
            'h3',  # Generic h3 for flash news
            'h2',  # Generic h2 as backup
            'h1'   # Generic h1 as last resort
        ]
        
        for selector in common_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    title = self._clean_text(element.get_text())
                    if title and len(title) > 5:  # Ensure meaningful title
                        logger.debug(f"Title extracted using selector '{selector}': {title[:50]}...")
                        return title
            except Exception as e:
                logger.debug(f"Selector '{selector}' failed: {e}")
                continue
        
        # Strategy 3: Try meta tags (enhanced)
        meta_selectors = [
            ('meta[property="og:title"]', 'content'),
            ('meta[name="twitter:title"]', 'content'),
            ('meta[property="twitter:title"]', 'content'),
            ('meta[name="title"]', 'content'),
            ('meta[property="article:title"]', 'content')
        ]
        
        for selector, attr in meta_selectors:
            try:
                meta_tag = soup.select_one(selector)
                if meta_tag and meta_tag.get(attr):
                    title = self._clean_text(meta_tag[attr])
                    if title and len(title) > 5:
                        logger.debug(f"Title extracted from meta tag '{selector}': {title[:50]}...")
                        return title
            except Exception as e:
                logger.debug(f"Meta selector '{selector}' failed: {e}")
                continue
        
        # Strategy 4: Use page title as last resort (cleaned)
        try:
            title_tag = soup.find('title')
            if title_tag:
                title = self._clean_text(title_tag.get_text())
                # Clean common title suffixes
                title = re.sub(r'\s*[-|–]\s*.*$', '', title)  # Remove " - Site Name" etc.
                if title and len(title) > 5:
                    logger.debug(f"Title extracted from page title: {title[:50]}...")
                    return title
        except Exception as e:
            logger.debug(f"Page title extraction failed: {e}")
        
        logger.warning("All title extraction strategies failed")
        return None

    def _extract_date_enhanced(self, soup: BeautifulSoup) -> Optional[datetime]:
        """
        Enhanced date extraction with comprehensive fallback strategies.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Extracted datetime or None
        """
        date_text = None
        
        # Strategy 1: Try configured selector
        if 'date' in self.selectors:
            try:
                element = soup.select_one(self.selectors['date'])
                if element:
                    # Check for datetime attribute first
                    date_text = element.get('datetime') or element.get_text()
                    if date_text:
                        logger.debug(f"Date found using configured selector: {date_text}")
            except Exception as e:
                logger.debug(f"Configured date selector failed: {e}")
        
        # Strategy 2: Try common date selectors (expanded)
        if not date_text:
            common_selectors = [
                'time[datetime]',
                '.article-date',
                '.entry-date',
                '[itemprop="datePublished"]',
                '[itemprop="publishDate"]',
                '.published-date',
                '.publish-date',
                '.post-date',
                '.news-date',
                'time',
                '.date',
                'span.date'
            ]
            
            for selector in common_selectors:
                try:
                    element = soup.select_one(selector)
                    if element:
                        date_text = element.get('datetime') or element.get_text()
                        if date_text:
                            logger.debug(f"Date found using selector '{selector}': {date_text}")
                            break
                except Exception as e:
                    logger.debug(f"Date selector '{selector}' failed: {e}")
                    continue
        
        # Strategy 3: Try meta tags (enhanced)
        if not date_text:
            meta_selectors = [
                ('meta[property="article:published_time"]', 'content'),
                ('meta[property="og:published_time"]', 'content'),
                ('meta[name="publishdate"]', 'content'),
                ('meta[name="publish_date"]', 'content'),
                ('meta[name="date"]', 'content'),
                ('meta[property="article:modified_time"]', 'content')
            ]
            
            for selector, attr in meta_selectors:
                try:
                    meta_tag = soup.select_one(selector)
                    if meta_tag and meta_tag.get(attr):
                        date_text = meta_tag[attr]
                        logger.debug(f"Date found in meta tag '{selector}': {date_text}")
                        break
                except Exception as e:
                    logger.debug(f"Meta date selector '{selector}' failed: {e}")
                    continue
        
        # Strategy 4: Parse the date text with multiple parsers
        if date_text:
            # Try dateutil parser first (handles most formats)
            try:
                parsed_date = date_parser.parse(self._clean_text(date_text))
                logger.debug(f"Successfully parsed date: {parsed_date}")
                return parsed_date
            except (ValueError, TypeError) as e:
                logger.debug(f"dateutil parser failed: {e}")
            
            # Try custom date patterns
            try:
                parsed_date = self._parse_custom_date_formats(date_text)
                if parsed_date:
                    logger.debug(f"Successfully parsed date with custom format: {parsed_date}")
                    return parsed_date
            except Exception as e:
                logger.debug(f"Custom date parser failed: {e}")
        
        logger.debug("All date extraction strategies failed")
        return None
    
    def _parse_custom_date_formats(self, date_text: str) -> Optional[datetime]:
        """
        Parse dates using custom format patterns.
        
        Args:
            date_text: Date string to parse
            
        Returns:
            Parsed datetime or None
        """
        # Chinese date formats
        patterns = [
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日', '%Y-%m-%d'),
            (r'(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{1,2})', '%Y-%m-%d %H:%M'),
            (r'(\d{4})/(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{1,2})', '%Y/%m/%d %H:%M'),
        ]
        
        for pattern, fmt in patterns:
            match = re.search(pattern, date_text)
            if match:
                try:
                    # Reconstruct date string for parsing
                    if '年' in pattern:
                        date_str = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
                        return datetime.strptime(date_str, '%Y-%m-%d')
                    else:
                        return datetime.strptime(match.group(0), fmt)
                except ValueError:
                    continue
        
        return None
    
    def _extract_author_enhanced(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Enhanced author extraction with comprehensive fallback strategies.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Extracted author name or None
        """
        # Strategy 1: Try configured selector
        if 'author' in self.selectors:
            try:
                element = soup.select_one(self.selectors['author'])
                if element:
                    author = self._clean_text(element.get_text())
                    if author:
                        logger.debug(f"Author extracted using configured selector: {author}")
                        return author
            except Exception as e:
                logger.debug(f"Configured author selector failed: {e}")
        
        # Strategy 2: Try common author selectors (expanded)
        common_selectors = [
            '.article-author',
            '.author-name',
            '[rel="author"]',
            '[itemprop="author"]',
            '[itemprop="author"] [itemprop="name"]',
            '.byline',
            '.by-author',
            '.post-author',
            '.news-author',
            'span.author',
            'a.author',
            '.author'
        ]
        
        for selector in common_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    author = self._clean_text(element.get_text())
                    if author and len(author) > 1:
                        logger.debug(f"Author extracted using selector '{selector}': {author}")
                        return author
            except Exception as e:
                logger.debug(f"Author selector '{selector}' failed: {e}")
                continue
        
        # Strategy 3: Try meta tags (enhanced)
        meta_selectors = [
            ('meta[name="author"]', 'content'),
            ('meta[property="article:author"]', 'content'),
            ('meta[property="og:article:author"]', 'content'),
            ('meta[name="twitter:creator"]', 'content')
        ]
        
        for selector, attr in meta_selectors:
            try:
                meta_tag = soup.select_one(selector)
                if meta_tag and meta_tag.get(attr):
                    author = self._clean_text(meta_tag[attr])
                    if author and len(author) > 1:
                        logger.debug(f"Author extracted from meta tag '{selector}': {author}")
                        return author
            except Exception as e:
                logger.debug(f"Meta author selector '{selector}' failed: {e}")
                continue
        
        logger.debug("All author extraction strategies failed")
        return None

    def _extract_body_enhanced(self, soup: BeautifulSoup, source_website: str) -> Optional[str]:
        """
        Enhanced body text extraction with comprehensive fallback strategies.
        
        Args:
            soup: BeautifulSoup object
            source_website: Source website domain for site-specific handling
            
        Returns:
            Extracted body text or None
        """
        # Strategy 1: Try configured selector
        if 'body' in self.selectors:
            try:
                element = soup.select_one(self.selectors['body'])
                if element:
                    text = self._extract_text(element)
                    if text and len(text) > 50:
                        logger.debug(f"Body extracted using configured selector: {len(text)} chars")
                        return self._extract_from_blockbeats_message(text)
            except Exception as e:
                logger.debug(f"Configured body selector failed: {e}")
        
        # Strategy 2: Try common article body selectors (expanded and prioritized)
        common_selectors = [
            # Flash/short-form news (high priority for news sites)
            '.flash-top',
            '.flash-top-border',
            '.flash-content',
            '.news-flash',
            
            # Standard article content
            'article .article-body',
            'article .entry-content',
            '.article-content',
            '[itemprop="articleBody"]',
            'article',
            '.post-content',
            '.content',
            '.news-content',
            '.detail-content',
            '.main-content',
            
            # Generic content containers
            '.content-body',
            '.text-content',
            'main .content',
            '#content',
            '.post-body'
        ]
        
        for selector in common_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    text = self._extract_text(element)
                    # Accept shorter content for flash news, longer for articles
                    min_length = 30 if 'flash' in selector else 50
                    if text and len(text) > min_length:
                        logger.debug(f"Body extracted using selector '{selector}': {len(text)} chars")
                        return self._extract_from_blockbeats_message(text)
            except Exception as e:
                logger.debug(f"Body selector '{selector}' failed: {e}")
                continue
        
        # Strategy 3: Site-specific meta tag fallbacks
        if 'blockbeats' in source_website.lower():
            meta_selectors = [
                ('meta[property="og:description"]', 'content'),
                ('meta[name="description"]', 'content'),
                ('meta[property="twitter:description"]', 'content')
            ]
            
            for selector, attr in meta_selectors:
                try:
                    meta_tag = soup.select_one(selector)
                    if meta_tag and meta_tag.get(attr):
                        text = meta_tag[attr]
                        if text and len(text) > 30:
                            logger.debug(f"Body extracted from meta tag '{selector}': {len(text)} chars")
                            return self._extract_from_blockbeats_message(text)
                except Exception as e:
                    logger.debug(f"Meta body selector '{selector}' failed: {e}")
                    continue
        
        # Strategy 4: Try to find substantial paragraphs
        try:
            paragraphs = soup.find_all('p')
            substantial_paragraphs = []
            
            for p in paragraphs:
                text = self._clean_text(p.get_text())
                if len(text) > 20:  # Lowered threshold for Chinese content
                    substantial_paragraphs.append(text)
            
            if substantial_paragraphs:
                combined_text = '\n'.join(substantial_paragraphs)
                logger.debug(f"Body extracted from paragraphs: {len(combined_text)} chars")
                return self._extract_from_blockbeats_message(combined_text)
        except Exception as e:
            logger.debug(f"Paragraph extraction failed: {e}")
        
        # Strategy 5: Try any div with substantial text content
        try:
            divs = soup.find_all('div')
            for div in divs:
                text = self._clean_text(div.get_text())
                if len(text) > 30 and 'BlockBeats' in text:
                    logger.debug(f"Body extracted from div: {len(text)} chars")
                    return self._extract_from_blockbeats_message(text)
        except Exception as e:
            logger.debug(f"Div extraction failed: {e}")
        
        # Strategy 6: Last resort - find the largest text block
        try:
            text = self._extract_largest_text_block(soup)
            if text and len(text) > 30:  # Lowered threshold
                logger.debug(f"Body extracted from largest text block: {len(text)} chars")
                return self._extract_from_blockbeats_message(text)
        except Exception as e:
            logger.debug(f"Largest text block extraction failed: {e}")
        
        logger.warning("All body extraction strategies failed")
        return None
    
    def _extract_clean_content(self, text: str) -> str:
        """
        Extract clean article content by removing unwanted footer elements and repetitive content.
        
        Args:
            text: Full text content
            
        Returns:
            Cleaned article content
        """
        if not text:
            return text
        
        # Define comprehensive footer markers to remove
        footer_markers = [
            'AI 解读',
            '展开',
            '原文链接', 
            '举报',
            '纠错/举报',
            '本平台现已全面集成',
            '热门文章',
            'farcaster评论',
            'The content is also unclear',
            'are unneeed information',
            '登录 后发表评论',
            '可以 登录 后发表评论'
        ]
        
        # Find the earliest footer marker and cut there
        earliest_pos = len(text)
        for marker in footer_markers:
            pos = text.find(marker)
            if pos != -1 and pos < earliest_pos:
                earliest_pos = pos
        
        # Cut at the earliest footer marker
        if earliest_pos < len(text):
            text = text[:earliest_pos]
        
        # Remove repetitive content patterns
        # Remove duplicate lines (common in scraped content)
        lines = text.split('\n')
        unique_lines = []
        seen_lines = set()
        
        for line in lines:
            line = line.strip()
            if line and line not in seen_lines:
                unique_lines.append(line)
                seen_lines.add(line)
        
        cleaned_text = '\n'.join(unique_lines)
        
        # Remove extra whitespace and normalize
        cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)  # Normalize paragraph breaks
        cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)  # Normalize spaces
        
        return cleaned_text.strip()
    
    def _extract_from_blockbeats_message(self, text: str) -> str:
        """
        Extract content starting from 'BlockBeats 消息' and clean it.
        
        Args:
            text: Full text content
            
        Returns:
            Text starting from 'BlockBeats 消息' or cleaned original text
        """
        if not text:
            return text
        
        # Find "BlockBeats 消息" and extract everything after it
        pattern = r'BlockBeats\s*消息'
        match = re.search(pattern, text)
        if match:
            # Get text starting from "BlockBeats 消息"
            extracted_text = text[match.start():]
            return self._extract_clean_content(extracted_text)
        
        # If BlockBeats pattern not found, still clean the content
        return self._extract_clean_content(text)
    
    def _extract_article_links_fallback(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Fallback method to extract article links using heuristics.
        
        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links
            
        Returns:
            List of absolute article URLs
        """
        article_urls = []
        
        # Look for links in common article listing containers
        containers = soup.select('article, .article-list, .post-list, main, .content')
        
        if not containers:
            # If no containers found, search all links
            containers = [soup]
        
        for container in containers:
            links = container.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                if href and self._looks_like_article_link(href):
                    absolute_url = urljoin(base_url, href)
                    if absolute_url not in article_urls:
                        article_urls.append(absolute_url)
        
        return article_urls
    
    def _looks_like_article_link(self, href: str) -> bool:
        """
        Heuristic to determine if a link looks like an article link.
        
        Args:
            href: Link href attribute
            
        Returns:
            True if link looks like an article link
        """
        # First, reject social media and share links completely
        reject_patterns = [
            r'^#',  # Anchor links
            r'^javascript:',  # JavaScript links
            r'mailto:',  # Email links
            r'\.(jpg|jpeg|png|gif|pdf|zip|css|js)$',  # File extensions
            r'facebook\.com',  # Social media share links
            r'twitter\.com',
            r'weibo\.com',
            r'share\.php',  # Share endpoints
        ]
        
        for pattern in reject_patterns:
            if re.search(pattern, href, re.IGNORECASE):
                return False
        
        # For theblockbeats.info, ONLY accept /flash/{number} URLs
        # Check if it's a theblockbeats URL (full or relative)
        is_theblockbeats = 'theblockbeats.info' in href or (href.startswith('/') and not href.startswith('//'))
        
        if is_theblockbeats:
            # Only accept /flash/ URLs with numbers
            if re.match(r'^/flash/\d+$', href) or re.search(r'theblockbeats\.info/flash/\d+$', href):
                return True
            else:
                return False
        
        # For other sites, use general patterns
        skip_patterns = [
            r'/(tag|category|author|search|login|register|about|contact|privacy|terms)/',  # Common non-article paths
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, href, re.IGNORECASE):
                return False
        
        # Accept links that look like articles
        article_patterns = [
            r'/article/\d+',  # Article with IDs
            r'/post/\d+',  # Posts with IDs
            r'/story/\d+',  # Stories with IDs
            r'/\d{4}/\d{2}/\d{2}/',  # Date-based URLs
        ]
        
        for pattern in article_patterns:
            if re.search(pattern, href, re.IGNORECASE):
                return True
        
        return False

    def _extract_text(self, element) -> str:
        """
        Extract and clean text from an HTML element.
        
        Removes scripts, styles, and other unwanted elements before extracting text.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Cleaned text content
        """
        # Remove unwanted elements
        for unwanted in element.select('script, style, nav, header, footer, aside, .advertisement, .ad, .social-share'):
            unwanted.decompose()
        
        # Get text and clean it
        text = element.get_text(separator=' ', strip=True)
        return self._clean_text(text)
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace and unwanted characters.
        
        Args:
            text: Raw text string
            
        Returns:
            Cleaned text string
        """
        if not text:
            return ""
        
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _extract_largest_text_block(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Find and extract the largest text block in the page.
        
        This is a last-resort fallback when other methods fail.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Largest text block or None
        """
        # Remove unwanted elements from a copy
        soup_copy = BeautifulSoup(str(soup), 'lxml')
        for unwanted in soup_copy.select('script, style, nav, header, footer, aside, .advertisement, .ad'):
            unwanted.decompose()
        
        # Find all paragraph-containing elements
        candidates = soup_copy.find_all(['article', 'div', 'section'])
        
        largest_text = ""
        largest_length = 0
        
        for candidate in candidates:
            paragraphs = candidate.find_all('p')
            # Accept single paragraph for short-form news, or multiple paragraphs for articles
            if len(paragraphs) >= 1:
                text = self._extract_text(candidate)
                if len(text) > largest_length:
                    largest_text = text
                    largest_length = len(text)
        
        return largest_text if largest_length > 50 else None
