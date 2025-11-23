"""
Deduplication engine for detecting and filtering duplicate news articles.
"""
import logging
import re
from typing import List, Tuple, Optional
from difflib import SequenceMatcher
from collections import defaultdict

from .models import Article


logger = logging.getLogger(__name__)


class DeduplicationEngine:
    """
    Detects and filters duplicate articles based on content similarity.
    
    Uses multiple signals:
    - Title similarity (primary)
    - Body text similarity (secondary)
    - Combined scoring
    
    Keeps the earliest published version when duplicates are detected.
    """
    
    def __init__(
        self,
        title_threshold: float = 0.85,
        body_threshold: float = 0.80,
        combined_threshold: float = 0.75
    ):
        """
        Initialize the deduplication engine.
        
        Args:
            title_threshold: Minimum similarity score for title matching (0-1)
            body_threshold: Minimum similarity score for body matching (0-1)
            combined_threshold: Minimum combined score for duplicate detection (0-1)
        """
        self.title_threshold = title_threshold
        self.body_threshold = body_threshold
        self.combined_threshold = combined_threshold
        
        self.duplicates_found = 0
        self.comparisons_made = 0
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison.
        
        Args:
            text: Raw text string
            
        Returns:
            Normalized text (lowercase, no punctuation, trimmed)
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common punctuation
        text = re.sub(r'[，。！？、；：""''（）《》【】\[\]{}(),.!?;:\'"<>]', '', text)
        
        # Trim
        text = text.strip()
        
        return text
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings using SequenceMatcher.
        
        Args:
            text1: First text string
            text2: Second text string
            
        Returns:
            Similarity score between 0 and 1
        """
        if not text1 or not text2:
            return 0.0
        
        # Normalize both texts
        norm1 = self.normalize_text(text1)
        norm2 = self.normalize_text(text2)
        
        if not norm1 or not norm2:
            return 0.0
        
        # Use SequenceMatcher for similarity
        matcher = SequenceMatcher(None, norm1, norm2)
        return matcher.ratio()
    
    def calculate_title_similarity(self, article1: Article, article2: Article) -> float:
        """
        Calculate title similarity between two articles.
        
        Args:
            article1: First article
            article2: Second article
            
        Returns:
            Title similarity score between 0 and 1
        """
        return self.calculate_similarity(article1.title, article2.title)
    
    def calculate_body_similarity(self, article1: Article, article2: Article) -> float:
        """
        Calculate body text similarity between two articles.
        
        Uses first 500 characters for efficiency.
        
        Args:
            article1: First article
            article2: Second article
            
        Returns:
            Body similarity score between 0 and 1
        """
        # Use first 500 chars for efficiency
        body1 = article1.body_text[:500] if article1.body_text else ""
        body2 = article2.body_text[:500] if article2.body_text else ""
        
        return self.calculate_similarity(body1, body2)
    
    def is_duplicate(self, article1: Article, article2: Article) -> Tuple[bool, float, dict]:
        """
        Determine if two articles are duplicates.
        
        Args:
            article1: First article
            article2: Second article
            
        Returns:
            Tuple of (is_duplicate, combined_score, details_dict)
        """
        self.comparisons_made += 1
        
        # Calculate individual similarities
        title_sim = self.calculate_title_similarity(article1, article2)
        body_sim = self.calculate_body_similarity(article1, article2)
        
        # Combined score (weighted: title 60%, body 40%)
        combined_score = (title_sim * 0.6) + (body_sim * 0.4)
        
        details = {
            'title_similarity': title_sim,
            'body_similarity': body_sim,
            'combined_score': combined_score
        }
        
        # Check if duplicate based on thresholds
        is_dup = False
        
        # High title similarity alone can indicate duplicate
        if title_sim >= self.title_threshold:
            is_dup = True
        # Or high body similarity with decent title similarity
        elif body_sim >= self.body_threshold and title_sim >= 0.6:
            is_dup = True
        # Or high combined score
        elif combined_score >= self.combined_threshold:
            is_dup = True
        
        if is_dup:
            logger.debug(
                f"Duplicate detected: '{article1.title[:40]}...' vs '{article2.title[:40]}...' "
                f"(title: {title_sim:.2f}, body: {body_sim:.2f}, combined: {combined_score:.2f})"
            )
        
        return is_dup, combined_score, details
    
    def deduplicate(self, articles: List[Article]) -> List[Article]:
        """
        Remove duplicate articles from a list, keeping the earliest published version.
        
        Args:
            articles: List of articles to deduplicate
            
        Returns:
            List of unique articles
        """
        if not articles:
            return []
        
        logger.info(f"Starting deduplication of {len(articles)} articles")
        
        # Reset counters
        self.duplicates_found = 0
        self.comparisons_made = 0
        
        # Sort by publication date (earliest first)
        # Articles without dates go to the end
        sorted_articles = sorted(
            articles,
            key=lambda a: a.publication_date if a.publication_date else datetime.max
        )
        
        unique_articles = []
        duplicate_groups = defaultdict(list)  # For logging
        
        for i, article in enumerate(sorted_articles):
            is_duplicate = False
            
            # Compare with all unique articles found so far
            for j, unique_article in enumerate(unique_articles):
                is_dup, score, details = self.is_duplicate(article, unique_article)
                
                if is_dup:
                    is_duplicate = True
                    self.duplicates_found += 1
                    
                    # Log the duplicate
                    logger.info(
                        f"Duplicate #{self.duplicates_found}: '{article.title[:40]}...' "
                        f"({article.source_website}) is duplicate of "
                        f"'{unique_article.title[:40]}...' ({unique_article.source_website}) "
                        f"[score: {score:.2f}]"
                    )
                    
                    # Track duplicate groups
                    duplicate_groups[j].append(i)
                    break
            
            if not is_duplicate:
                unique_articles.append(article)
        
        logger.info("=" * 60)
        logger.info("DEDUPLICATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total articles processed: {len(articles)}")
        logger.info(f"Unique articles: {len(unique_articles)}")
        logger.info(f"Duplicates removed: {self.duplicates_found}")
        logger.info(f"Comparisons made: {self.comparisons_made}")
        logger.info(f"Deduplication rate: {(self.duplicates_found / len(articles) * 100):.1f}%")
        logger.info("=" * 60)
        
        return unique_articles
    
    def get_statistics(self) -> dict:
        """
        Get deduplication statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'duplicates_found': self.duplicates_found,
            'comparisons_made': self.comparisons_made,
            'title_threshold': self.title_threshold,
            'body_threshold': self.body_threshold,
            'combined_threshold': self.combined_threshold
        }


# Import datetime for sorting
from datetime import datetime
