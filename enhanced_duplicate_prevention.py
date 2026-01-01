#!/usr/bin/env python3
"""
Enhanced Duplicate Prevention System
Implement multiple layers of duplicate detection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.core.database_manager import DatabaseManager
import hashlib
from typing import Dict, List, Set

class EnhancedDuplicateDetector:
    """
    Multi-layer duplicate detection system
    """
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        
        # In-memory caches for this session
        self.seen_urls: Set[str] = set()
        self.seen_titles: Set[str] = set()
        self.seen_content_hashes: Set[str] = set()
        
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
            
            print(f"✅ Loaded {len(self.seen_urls)} URLs, {len(self.seen_titles)} titles, {len(self.seen_content_hashes)} content hashes")
            
        except Exception as e:
            print(f"⚠️  Error loading existing data: {e}")
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate normalized content hash"""
        # Normalize: remove whitespace, convert to lowercase, remove punctuation
        import re
        normalized = re.sub(r'[^\w\s]', '', content.lower())
        normalized = ''.join(normalized.split())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def is_duplicate(self, article_data: Dict) -> Dict[str, any]:
        """
        Check if article is duplicate using multiple methods
        
        Args:
            article_data: Dict with 'url', 'title', 'content' keys
            
        Returns:
            Dict with duplicate detection results
        """
        url = article_data.get('url', '')
        title = article_data.get('title', '').strip().lower()
        content = article_data.get('content', article_data.get('title', ''))
        
        # Method 1: URL check (most reliable)
        if url in self.seen_urls:
            return {
                'is_duplicate': True,
                'method': 'url_match',
                'confidence': 100,
                'reason': f'URL already exists: {url}'
            }
        
        # Method 2: Exact title match
        if title in self.seen_titles:
            return {
                'is_duplicate': True,
                'method': 'title_match',
                'confidence': 95,
                'reason': f'Title already exists: {title[:50]}...'
            }
        
        # Method 3: Content hash match
        content_hash = self._calculate_content_hash(content)
        if content_hash in self.seen_content_hashes:
            return {
                'is_duplicate': True,
                'method': 'content_hash_match',
                'confidence': 90,
                'reason': f'Content hash already exists: {content_hash}'
            }
        
        # Method 4: Similar title check (fuzzy matching)
        similar_title = self._find_similar_title(title)
        if similar_title:
            return {
                'is_duplicate': True,
                'method': 'similar_title',
                'confidence': 80,
                'reason': f'Similar title exists: {similar_title[:50]}...'
            }
        
        # Not a duplicate
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
    
    def get_stats(self) -> Dict:
        """Get duplicate detector statistics"""
        return {
            'urls_tracked': len(self.seen_urls),
            'titles_tracked': len(self.seen_titles),
            'content_hashes_tracked': len(self.seen_content_hashes)
        }

def test_enhanced_duplicate_detection():
    """Test the enhanced duplicate detection system"""
    
    print("🧪 Testing Enhanced Duplicate Detection")
    print("=" * 50)
    
    # Initialize detector
    detector = EnhancedDuplicateDetector()
    stats = detector.get_stats()
    print(f"📊 Loaded existing data: {stats}")
    
    # Test cases
    test_articles = [
        {
            'url': 'https://www.theblockbeats.info/flash/326520',
            'title': '老牌国产公链NEO两位创始人撕逼，财务不透明为核心原因',
            'content': '老牌国产公链NEO两位创始人撕逼，财务不透明为核心原因，项目方资金管理存在问题'
        },
        {
            'url': 'https://www.theblockbeats.info/flash/326521',
            'title': '老牌国产公链NEO两位创始人撕逼，财务不透明为核心原因',  # Same title
            'content': '老牌国产公链NEO两位创始人撕逼，财务不透明为核心原因，项目方资金管理存在问题'  # Same content
        },
        {
            'url': 'https://www.theblockbeats.info/flash/326522',
            'title': 'Bitcoin价格突破新高',
            'content': 'Bitcoin今日价格突破历史新高，市场情绪乐观'
        }
    ]
    
    print(f"\n🔍 Testing duplicate detection:")
    
    for i, article in enumerate(test_articles):
        print(f"\n[{i+1}] Testing: {article['title'][:50]}...")
        
        result = detector.is_duplicate(article)
        
        print(f"    Is Duplicate: {result['is_duplicate']}")
        print(f"    Method: {result['method']}")
        print(f"    Confidence: {result['confidence']}%")
        print(f"    Reason: {result['reason']}")
        
        if not result['is_duplicate']:
            # Add to cache for next test
            detector.add_article(article)
            print(f"    ✅ Added to cache")
        else:
            print(f"    ❌ Blocked as duplicate")
    
    print(f"\n📊 Final stats: {detector.get_stats()}")
    print("🎯 Enhanced Duplicate Detection Test Complete")

if __name__ == "__main__":
    test_enhanced_duplicate_detection()