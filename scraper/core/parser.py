"""
HTML parser for extracting article data from news websites.
"""
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin
import re
from dateutil import parser as date_parser

from scraper.core.models import Article


class HTMLParser:
    """
    Parses HTML content to extract article data.
    
    Uses CSS selectors to extract article information with fallback logic
    when selectors don't match.
    """
    
    def __init__(self, selectors: Optional[dict] = None):
        """
        Initialize the HTML parser.
        
        Args:
            selectors: Dictionary of CSS selectors for article elements.
                      Expected keys: 'article_links', 'title', 'date', 'author', 'body'
        """
        self.selectors = selectors or {}
        
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
        Extract date from body text using common patterns.
        
        Args:
            body_text: Article body text
            
        Returns:
            Extracted datetime or None
        """
        import re
        from datetime import datetime
        
        # Pattern 1: "BlockBeats 消息，11 月 11 日，" or similar
        pattern1 = r'BlockBeats\s*消息\s*，\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日'
        match = re.search(pattern1, body_text)
        if match:
            month = int(match.group(1))
            day = int(match.group(2))
            # Use current year
            year = datetime.now().year
            try:
                return datetime(year, month, day)
            except ValueError:
                pass
        
        # Pattern 2: "2025-11-11" or "2025/11/11"
        pattern2 = r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})'
        match = re.search(pattern2, body_text)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            try:
                return datetime(year, month, day)
            except ValueError:
                pass
        
        # Pattern 3: "11月11日" without BlockBeats prefix
        pattern3 = r'(\d{1,2})\s*月\s*(\d{1,2})\s*日'
        match = re.search(pattern3, body_text[:200])  # Check first 200 chars
        if match:
            month = int(match.group(1))
            day = int(match.group(2))
            year = datetime.now().year
            try:
                return datetime(year, month, day)
            except ValueError:
                pass
        
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
        
        # Extract title
        title = self._extract_title(soup)
        if not title:
            raise ValueError("Could not extract article title")
        
        # Extract publication date
        publication_date = self._extract_date(soup)
        
        # Extract author
        author = self._extract_author(soup)
        
        # Extract body text
        body_text = self._extract_body(soup)
        if not body_text:
            raise ValueError("Could not extract article body")
        
        # If no publication date found, try to extract from body text
        if not publication_date:
            publication_date = self._extract_date_from_body(body_text)
        
        return Article(
            url=url,
            title=title,
            publication_date=publication_date,
            author=author,
            body_text=body_text,
            scraped_at=datetime.now(),
            source_website=source_website
        )
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract article title using selectors or fallback logic.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Extracted title or None
        """
        # Try configured selector
        if 'title' in self.selectors:
            element = soup.select_one(self.selectors['title'])
            if element:
                return self._clean_text(element.get_text())
        
        # Fallback strategies
        # 1. Try common title selectors
        common_selectors = [
            'h1.article-title',
            'h1.entry-title',
            'h1[itemprop="headline"]',
            'article h1',
            '.article-header h1',
            'h1'
        ]
        
        for selector in common_selectors:
            element = soup.select_one(selector)
            if element:
                return self._clean_text(element.get_text())
        
        # 2. Try meta tags
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get('content'):
            return self._clean_text(meta_title['content'])
        
        # 3. Use page title as last resort
        title_tag = soup.find('title')
        if title_tag:
            return self._clean_text(title_tag.get_text())
        
        return None

    def _extract_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """
        Extract publication date using selectors or fallback logic.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Extracted datetime or None
        """
        date_text = None
        
        # Try configured selector
        if 'date' in self.selectors:
            element = soup.select_one(self.selectors['date'])
            if element:
                # Check for datetime attribute first
                date_text = element.get('datetime') or element.get_text()
        
        # Fallback strategies
        if not date_text:
            # 1. Try common date selectors
            common_selectors = [
                'time[datetime]',
                '.article-date',
                '.entry-date',
                '[itemprop="datePublished"]',
                '.published-date',
                'time'
            ]
            
            for selector in common_selectors:
                element = soup.select_one(selector)
                if element:
                    date_text = element.get('datetime') or element.get_text()
                    if date_text:
                        break
        
        # 2. Try meta tags
        if not date_text:
            meta_date = soup.find('meta', property='article:published_time')
            if not meta_date:
                meta_date = soup.find('meta', property='og:published_time')
            if meta_date and meta_date.get('content'):
                date_text = meta_date['content']
        
        # Parse the date text
        if date_text:
            try:
                return date_parser.parse(self._clean_text(date_text))
            except (ValueError, TypeError):
                pass
        
        return None
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract article author using selectors or fallback logic.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Extracted author name or None
        """
        # Try configured selector
        if 'author' in self.selectors:
            element = soup.select_one(self.selectors['author'])
            if element:
                return self._clean_text(element.get_text())
        
        # Fallback strategies
        # 1. Try common author selectors
        common_selectors = [
            '.article-author',
            '.author-name',
            '[rel="author"]',
            '[itemprop="author"]',
            '.byline',
            '.by-author'
        ]
        
        for selector in common_selectors:
            element = soup.select_one(selector)
            if element:
                return self._clean_text(element.get_text())
        
        # 2. Try meta tags
        meta_author = soup.find('meta', attrs={'name': 'author'})
        if not meta_author:
            meta_author = soup.find('meta', property='article:author')
        if meta_author and meta_author.get('content'):
            return self._clean_text(meta_author['content'])
        
        return None

    def _extract_body(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract article body text using selectors or fallback logic.
        Only extracts content starting from "BlockBeats 消息".
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Extracted body text or None
        """
        # Try configured selector
        if 'body' in self.selectors:
            element = soup.select_one(self.selectors['body'])
            if element:
                text = self._extract_text(element)
                return self._extract_from_blockbeats_message(text)
        
        # Fallback strategies
        # 1. Try common article body selectors (including flash/short-form news)
        common_selectors = [
            '.flash-top',  # Flash news items
            '.flash-top-border',  # Flash news items
            'article .article-body',
            'article .entry-content',
            '.article-content',
            '[itemprop="articleBody"]',
            'article',
            '.post-content',
            '.content',
            '.news-content',
            '.detail-content'
        ]
        
        for selector in common_selectors:
            element = soup.select_one(selector)
            if element:
                text = self._extract_text(element)
                # Accept if we got text (lowered threshold for short-form news)
                if text and len(text) > 50:
                    return self._extract_from_blockbeats_message(text)
        
        # 2. Try to find single paragraph with substantial content (for flash news)
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = self._clean_text(p.get_text())
            if len(text) > 50:  # Accept shorter content for news flashes
                return self._extract_from_blockbeats_message(text)
        
        # 3. Last resort: find the largest text block
        text = self._extract_largest_text_block(soup)
        return self._extract_from_blockbeats_message(text) if text else None
    
    def _extract_from_blockbeats_message(self, text: str) -> str:
        """
        Extract content starting from 'BlockBeats 消息' and ending before footer content.
        
        Args:
            text: Full text content
            
        Returns:
            Text starting from 'BlockBeats 消息' or original text if pattern not found
        """
        if not text:
            return text
        
        # Find "BlockBeats 消息" and extract everything after it
        pattern = r'BlockBeats\s*消息'
        match = re.search(pattern, text)
        if match:
            # Get text starting from "BlockBeats 消息"
            extracted_text = text[match.start():]
            
            # Find the first occurrence of footer markers and cut there
            footer_markers = [
                'AI 解读',
                '展开',
                '原文链接',
                '举报',
                '纠错/举报',
                '本平台现已全面集成',
                '热门文章'
            ]
            
            # Find the earliest footer marker
            earliest_pos = len(extracted_text)
            for marker in footer_markers:
                pos = extracted_text.find(marker)
                if pos != -1 and pos < earliest_pos:
                    earliest_pos = pos
            
            # Cut at the earliest footer marker
            if earliest_pos < len(extracted_text):
                extracted_text = extracted_text[:earliest_pos]
            
            return extracted_text.strip()
        
        # If pattern not found, return original text
        return text
    
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
