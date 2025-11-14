"""
Data storage components for the news scraper.
"""
import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import List, Set
from .models import Article


class DataStore(ABC):
    """Base class for data storage implementations."""
    
    def __init__(self, output_path: str):
        """
        Initialize the data store.
        
        Args:
            output_path: Path where data will be stored
        """
        self.output_path = output_path
        self._scraped_urls: Set[str] = set()
    
    @abstractmethod
    def save_article(self, article: Article) -> bool:
        """
        Save an article to storage.
        
        Args:
            article: The article to save
            
        Returns:
            True if article was saved, False if it already exists
        """
        pass
    
    @abstractmethod
    def article_exists(self, url: str) -> bool:
        """
        Check if an article with the given URL already exists.
        
        Args:
            url: The article URL to check
            
        Returns:
            True if article exists, False otherwise
        """
        pass
    
    @abstractmethod
    def get_all_articles(self) -> List[Article]:
        """
        Retrieve all stored articles.
        
        Returns:
            List of all articles in storage
        """
        pass
    
    @abstractmethod
    def export(self, path: str) -> None:
        """
        Export articles to a file.
        
        Args:
            path: Path where data will be exported
        """
        pass


class JSONDataStore(DataStore):
    """JSON file-based data storage implementation."""
    
    def __init__(self, output_path: str):
        """
        Initialize the JSON data store.
        
        Args:
            output_path: Path to the JSON file
        """
        super().__init__(output_path)
        self._articles: List[Article] = []
        self._load_existing_data()
    
    def _load_existing_data(self) -> None:
        """Load existing articles from the JSON file if it exists."""
        path = Path(self.output_path)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        # Parse datetime fields
                        pub_date = None
                        if item.get('publication_date'):
                            pub_date = datetime.fromisoformat(item['publication_date'])
                        
                        scraped_at = datetime.fromisoformat(item['scraped_at'])
                        
                        article = Article(
                            url=item['url'],
                            title=item['title'],
                            publication_date=pub_date,
                            author=item.get('author'),
                            body_text=item['body_text'],
                            scraped_at=scraped_at,
                            source_website=item['source_website'],
                            matched_keywords=item.get('matched_keywords')
                        )
                        self._articles.append(article)
                        self._scraped_urls.add(article.url)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # If file is corrupted or invalid, start fresh
                self._articles = []
                self._scraped_urls = set()

    def save_article(self, article: Article) -> bool:
        """
        Save an article to storage with duplicate checking.
        
        Args:
            article: The article to save
            
        Returns:
            True if article was saved, False if it already exists
        """
        # Check for duplicates based on URL
        if self.article_exists(article.url):
            return False
        
        # Add article to in-memory list and URL set
        self._articles.append(article)
        self._scraped_urls.add(article.url)
        
        # Persist to file
        self._save_to_file()
        
        return True
    
    def article_exists(self, url: str) -> bool:
        """
        Check if an article with the given URL already exists.
        
        Args:
            url: The article URL to check
            
        Returns:
            True if article exists, False otherwise
        """
        return url in self._scraped_urls
    
    def get_all_articles(self) -> List[Article]:
        """
        Retrieve all stored articles.
        
        Returns:
            List of all articles in storage
        """
        return self._articles.copy()
    
    def export(self, path: str) -> None:
        """
        Export articles to a JSON file.
        
        Args:
            path: Path where data will be exported
        """
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = []
        for article in self._articles:
            article_dict = {
                'url': article.url,
                'title': article.title,
                'publication_date': article.publication_date.isoformat() if article.publication_date else None,
                'author': article.author,
                'body_text': article.body_text,
                'scraped_at': article.scraped_at.isoformat(),
                'source_website': article.source_website,
                'matched_keywords': article.matched_keywords if article.matched_keywords else []
            }
            data.append(article_dict)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_to_file(self) -> None:
        """Save all articles to the JSON file."""
        # Ensure parent directory exists
        path = Path(self.output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = []
        for article in self._articles:
            article_dict = {
                'url': article.url,
                'title': article.title,
                'publication_date': article.publication_date.isoformat() if article.publication_date else None,
                'author': article.author,
                'body_text': article.body_text,
                'scraped_at': article.scraped_at.isoformat(),
                'source_website': article.source_website,
                'matched_keywords': article.matched_keywords if article.matched_keywords else []
            }
            data.append(article_dict)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)



class CSVDataStore(DataStore):
    """CSV file-based data storage implementation."""
    
    def __init__(self, output_path: str):
        """
        Initialize the CSV data store.
        
        Args:
            output_path: Path to the CSV file
        """
        super().__init__(output_path)
        self._articles: List[Article] = []
        self._load_existing_data()
    
    def _load_existing_data(self) -> None:
        """Load existing articles from the CSV file if it exists."""
        import csv
        
        path = Path(self.output_path)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8', newline='') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Parse datetime fields
                        pub_date = None
                        if row.get('publication_date'):
                            pub_date = datetime.fromisoformat(row['publication_date'])
                        
                        scraped_at = datetime.fromisoformat(row['scraped_at'])
                        
                        # Parse matched_keywords if present
                        matched_keywords = None
                        if row.get('matched_keywords'):
                            matched_keywords = row['matched_keywords'].split(',') if row['matched_keywords'] else None
                        
                        article = Article(
                            url=row['url'],
                            title=row['title'],
                            publication_date=pub_date,
                            author=row.get('author') if row.get('author') else None,
                            body_text=row['body_text'],
                            scraped_at=scraped_at,
                            source_website=row['source_website'],
                            matched_keywords=matched_keywords
                        )
                        self._articles.append(article)
                        self._scraped_urls.add(article.url)
            except (csv.Error, KeyError, ValueError) as e:
                # If file is corrupted or invalid, start fresh
                self._articles = []
                self._scraped_urls = set()
    
    def save_article(self, article: Article) -> bool:
        """
        Save an article to CSV storage with duplicate checking.
        
        Args:
            article: The article to save
            
        Returns:
            True if article was saved, False if it already exists
        """
        # Check for duplicates based on URL
        if self.article_exists(article.url):
            return False
        
        # Add article to in-memory list and URL set
        self._articles.append(article)
        self._scraped_urls.add(article.url)
        
        # Persist to file
        self._save_to_file()
        
        return True
    
    def article_exists(self, url: str) -> bool:
        """
        Check if an article with the given URL already exists.
        
        Args:
            url: The article URL to check
            
        Returns:
            True if article exists, False otherwise
        """
        return url in self._scraped_urls
    
    def get_all_articles(self) -> List[Article]:
        """
        Retrieve all stored articles.
        
        Returns:
            List of all articles in storage
        """
        return self._articles.copy()
    
    def export(self, path: str) -> None:
        """
        Export articles to a CSV file.
        
        Args:
            path: Path where data will be exported
        """
        import csv
        
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Define CSV columns in Chinese
        fieldnames = [
            '发布日期',
            '标题',
            '正文内容',
            '链接',
            '匹配关键词'
        ]
        
        # Write with UTF-8 BOM for Excel compatibility
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            
            for article in self._articles:
                row = {
                    '发布日期': article.publication_date.strftime('%Y-%m-%d') if article.publication_date else '',
                    '标题': article.title,
                    '正文内容': article.body_text,
                    '链接': article.url,
                    '匹配关键词': ', '.join(article.matched_keywords) if article.matched_keywords else ''
                }
                writer.writerow(row)
    
    def _save_to_file(self) -> None:
        """Save all articles to the CSV file."""
        import csv
        
        # Ensure parent directory exists
        path = Path(self.output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Define CSV columns in Chinese
        fieldnames = [
            '发布日期',
            '标题',
            '正文内容',
            '链接',
            '匹配关键词'
        ]
        
        # Write with UTF-8 BOM for Excel compatibility
        with open(path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            
            for article in self._articles:
                row = {
                    '发布日期': article.publication_date.strftime('%Y-%m-%d') if article.publication_date else '',
                    '标题': article.title,
                    '正文内容': article.body_text,
                    '链接': article.url,
                    '匹配关键词': ', '.join(article.matched_keywords) if article.matched_keywords else ''
                }
                writer.writerow(row)
