"""
CSV Export Service - Export articles to CSV format with filtering
Implements RFC 4180 compliant CSV formatting
"""

import csv
import io
import os
import uuid
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import logging

from .database_manager import DatabaseManager

logger = logging.getLogger(__name__)


@dataclass
class CSVExportConfig:
    """Configuration for CSV export"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    sources: List[str] = None
    keywords: List[str] = None
    include_content: bool = True
    max_records: Optional[int] = None
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = []
        if self.keywords is None:
            self.keywords = []


class CSVExportService:
    """Service for exporting articles to CSV format with filtering capabilities"""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize CSV export service
        
        Args:
            db_manager: Database manager instance (creates new if not provided)
        """
        self.db_manager = db_manager or DatabaseManager()
        self.export_dir = os.path.join(os.getcwd(), 'exports')
        
        # Create exports directory if it doesn't exist
        os.makedirs(self.export_dir, exist_ok=True)
        
        logger.info("CSV Export Service initialized")
    
    def export_articles(
        self,
        config: Optional[CSVExportConfig] = None,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export articles to CSV file with optional filtering
        
        Args:
            config: Export configuration with filters
            output_file: Optional output file path (generates if not provided)
            
        Returns:
            Dictionary with export results including file path and statistics
        """
        start_time = datetime.now()
        config = config or CSVExportConfig()
        
        logger.info(f"Starting CSV export with config: {config}")
        
        try:
            # Step 1: Filter articles from database
            articles = self.filter_articles(config)
            
            if not articles:
                logger.warning("No articles found matching filters")
                return {
                    'success': False,
                    'message': 'No articles found matching filters',
                    'articles_count': 0,
                    'file_path': None
                }
            
            # Step 2: Format articles as CSV
            csv_content = self.format_csv(articles, config.include_content)
            
            # Step 3: Write to file
            if not output_file:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_id = str(uuid.uuid4())[:8]
                output_file = os.path.join(
                    self.export_dir,
                    f'articles_export_{timestamp}_{file_id}.csv'
                )
            
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                f.write(csv_content)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            result = {
                'success': True,
                'message': 'Export completed successfully',
                'file_path': output_file,
                'file_id': os.path.basename(output_file),
                'articles_count': len(articles),
                'duration_seconds': duration,
                'filters_applied': {
                    'start_date': config.start_date.isoformat() if config.start_date else None,
                    'end_date': config.end_date.isoformat() if config.end_date else None,
                    'sources': config.sources,
                    'keywords': config.keywords,
                    'max_records': config.max_records
                }
            }
            
            logger.info(f"CSV export completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"CSV export failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f'Export failed: {str(e)}',
                'articles_count': 0,
                'file_path': None
            }
    
    def filter_articles(self, config: CSVExportConfig) -> List[Dict[str, Any]]:
        """
        Filter articles from database based on configuration
        
        Args:
            config: Export configuration with filter criteria
            
        Returns:
            List of filtered articles
        """
        try:
            # Start with base query
            query = self.db_manager.supabase.table('articles').select('*')
            
            # Apply date range filter
            if config.start_date:
                # Convert date to string format matching database
                start_date_str = config.start_date.strftime('%Y/%m/%d')
                query = query.gte('date', start_date_str)
                logger.info(f"Filtering articles from: {start_date_str}")
            
            if config.end_date:
                # Convert date to string format matching database
                end_date_str = config.end_date.strftime('%Y/%m/%d')
                query = query.lte('date', end_date_str)
                logger.info(f"Filtering articles until: {end_date_str}")
            
            # Apply source filter
            if config.sources:
                # Use ilike for case-insensitive matching
                source_conditions = []
                for source in config.sources:
                    source_conditions.append(('source', 'ilike', f'%{source}%'))
                
                # For multiple sources, we need to use OR logic
                if len(config.sources) == 1:
                    query = query.ilike('source', f'%{config.sources[0]}%')
                else:
                    # For multiple sources, use in_ with exact matches
                    query = query.in_('source', config.sources)
                
                logger.info(f"Filtering by sources: {config.sources}")
            
            # Apply max records limit
            if config.max_records:
                query = query.limit(config.max_records)
            
            # Order by date descending
            query = query.order('scraped_at', desc=True)
            
            # Execute query
            result = query.execute()
            articles = result.data
            
            # Apply keyword filter (post-query since it requires text search)
            if config.keywords:
                articles = self._filter_by_keywords(articles, config.keywords)
                logger.info(f"Filtered by keywords: {len(articles)} articles remaining")
            
            logger.info(f"Filtered {len(articles)} articles from database")
            return articles
            
        except Exception as e:
            logger.error(f"Error filtering articles: {str(e)}", exc_info=True)
            return []
    
    def _filter_by_keywords(
        self,
        articles: List[Dict[str, Any]],
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Filter articles by keywords in title or content
        
        Args:
            articles: List of articles to filter
            keywords: List of keywords to search for
            
        Returns:
            Filtered list of articles containing at least one keyword
        """
        if not keywords:
            return articles
        
        filtered = []
        keywords_lower = [k.lower() for k in keywords]
        
        for article in articles:
            title = (article.get('title') or '').lower()
            content = (article.get('body_text') or '').lower()
            matched_keywords = article.get('matched_keywords') or []
            
            # Check if any keyword matches
            has_match = False
            
            # Check in matched_keywords field
            if matched_keywords:
                matched_lower = [k.lower() for k in matched_keywords]
                if any(k in matched_lower for k in keywords_lower):
                    has_match = True
            
            # Check in title and content
            if not has_match:
                for keyword in keywords_lower:
                    if keyword in title or keyword in content:
                        has_match = True
                        break
            
            if has_match:
                filtered.append(article)
        
        return filtered
    
    def format_csv(
        self,
        articles: List[Dict[str, Any]],
        include_content: bool = True
    ) -> str:
        """
        Format articles as RFC 4180 compliant CSV
        
        Args:
            articles: List of articles to format
            include_content: Whether to include full article content
            
        Returns:
            CSV formatted string
        """
        output = io.StringIO()
        
        # Define CSV columns
        if include_content:
            fieldnames = [
                'date',
                'title',
                'content',
                'source',
                'keywords',
                'url',
                'scraped_at'
            ]
        else:
            fieldnames = [
                'date',
                'title',
                'source',
                'keywords',
                'url',
                'scraped_at'
            ]
        
        # Create CSV writer with RFC 4180 compliance
        writer = csv.DictWriter(
            output,
            fieldnames=fieldnames,
            quoting=csv.QUOTE_MINIMAL,
            lineterminator='\n'
        )
        
        # Write header
        writer.writeheader()
        
        # Write article rows
        for article in articles:
            row = {
                'date': article.get('date', ''),
                'title': article.get('title', ''),
                'source': article.get('source', ''),
                'keywords': ', '.join(article.get('matched_keywords', [])),
                'url': article.get('url', ''),
                'scraped_at': article.get('scraped_at', '')
            }
            
            if include_content:
                # Properly handle multi-line content
                content = article.get('body_text', '')
                row['content'] = content
            
            writer.writerow(row)
        
        csv_content = output.getvalue()
        output.close()
        
        logger.info(f"Formatted {len(articles)} articles as CSV")
        return csv_content
    
    def get_export_file(self, file_id: str) -> Optional[str]:
        """
        Get full path for an export file by ID
        
        Args:
            file_id: File ID or filename
            
        Returns:
            Full file path if exists, None otherwise
        """
        file_path = os.path.join(self.export_dir, file_id)
        
        if os.path.exists(file_path):
            return file_path
        
        return None
    
    def cleanup_old_exports(self, days: int = 1):
        """
        Clean up export files older than specified days
        
        Args:
            days: Number of days to keep files
        """
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            
            for filename in os.listdir(self.export_dir):
                file_path = os.path.join(self.export_dir, filename)
                
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        logger.info(f"Cleaned up old export: {filename}")
            
        except Exception as e:
            logger.error(f"Error cleaning up exports: {str(e)}")
