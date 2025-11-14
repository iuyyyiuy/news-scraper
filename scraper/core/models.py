"""
Data models for the news scraper.
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, List


@dataclass
class Article:
    """Represents a scraped news article."""
    url: str
    title: str
    publication_date: Optional[datetime]
    author: Optional[str]
    body_text: str
    scraped_at: datetime
    source_website: str
    matched_keywords: Optional[List[str]] = None


@dataclass
class ScrapingResult:
    """Represents the outcome of a scraping session."""
    total_articles_found: int
    articles_scraped: int
    articles_failed: int
    duration_seconds: float
    errors: List[str]


@dataclass
class Config:
    """Represents scraper configuration."""
    target_url: str
    max_articles: int = 10
    request_delay: float = 2.0
    output_format: str = "json"
    output_path: str = "scraped_articles.json"
    timeout: int = 30
    max_retries: int = 3
    selectors: Dict[str, str] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    
    def validate(self) -> None:
        """
        Validate configuration parameters.
        
        Raises:
            ValueError: If any configuration parameter is invalid
        """
        if not self.target_url:
            raise ValueError("target_url cannot be empty")
        
        if not self.target_url.startswith(('http://', 'https://')):
            raise ValueError("target_url must start with http:// or https://")
        
        if self.max_articles <= 0:
            raise ValueError("max_articles must be greater than 0")
        
        if self.request_delay < 0:
            raise ValueError("request_delay cannot be negative")
        
        if self.output_format not in ['json', 'csv']:
            raise ValueError("output_format must be 'json' or 'csv'")
        
        if not self.output_path:
            raise ValueError("output_path cannot be empty")
        
        if self.timeout <= 0:
            raise ValueError("timeout must be greater than 0")
        
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative")


@dataclass
class ScrapeRequest:
    """Represents a scraping request from the web interface."""
    start_date: date
    end_date: date
    keywords: List[str]
    max_articles: Optional[int] = None
    
    def validate(self) -> None:
        """
        Validate the scrape request parameters.
        
        Raises:
            ValueError: If any parameter is invalid
        """
        if self.start_date > self.end_date:
            raise ValueError("start_date cannot be after end_date")
        
        if self.max_articles is not None and self.max_articles <= 0:
            raise ValueError("max_articles must be greater than 0")
