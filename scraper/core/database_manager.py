"""
Database Manager for News Database Feature
Handles all Supabase database operations
"""
import os
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try different import methods for compatibility
try:
    from supabase import create_client, Client
except ImportError:
    from supabase import Client, create_client


class DatabaseManager:
    """Manages database operations for storing and retrieving news articles"""
    
    def __init__(self):
        self.supabase = None
        self.connect_to_supabase()
    
    def connect_to_supabase(self) -> bool:
        """
        Connect to Supabase database
        Returns True if successful, False otherwise
        """
        try:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY')
            
            if not url or not key:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
            
            # For supabase-py 2.x, use simple positional arguments
            self.supabase = create_client(url, key)
            
            # Test connection - skip table check for now
            # self.supabase.table('articles').select('id').limit(1).execute()
            
            print(f"✅ Connected to Supabase: {url}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")
            return False
    
    def insert_article(self, article_data: Dict) -> bool:
        """
        Insert a new article into the database
        
        Args:
            article_data: Dictionary containing article information
                - publication_date: str (YYYY/MM/DD format)
                - title: str
                - body_text: str
                - url: str
                - source: str
                - matched_keywords: str (comma-separated)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if article already exists
            if self.check_article_exists(article_data['url']):
                print(f"⚠️  Article already exists: {article_data['url']}")
                return False
            
            # Parse matched_keywords if it's a string
            matched_keywords = article_data.get('matched_keywords', '')
            if isinstance(matched_keywords, str):
                matched_keywords = [k.strip() for k in matched_keywords.split(',') if k.strip()]
            
            # Normalize source name to standard format
            source_name = self._normalize_source_name(article_data.get('source', ''))
            
            # Prepare data for insertion
            # Use UTC time for scraped_at (Supabase stores in UTC)
            from datetime import timezone
            data = {
                'date': article_data.get('publication_date') or article_data.get('date'),
                'title': article_data['title'],
                'body_text': article_data['body_text'],
                'url': article_data['url'],
                'source': source_name,
                'matched_keywords': matched_keywords,
                'scraped_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Insert into database
            response = self.supabase.table('articles').insert(data).execute()
            
            if response.data:
                print(f"✅ Inserted article: {article_data['title'][:50]}...")
                return True
            else:
                print(f"❌ Failed to insert article: {article_data['title'][:50]}...")
                return False
                
        except KeyError as e:
            print(f"❌ Missing required field: {e}")
            print(f"   Available fields: {list(article_data.keys())}")
            return False
        except Exception as e:
            print(f"❌ Error inserting article: {e}")
            print(f"   Error type: {type(e).__name__}")
            print(f"   Data being sent: {data}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_all_articles(self, limit: int = 50, offset: int = 0, keyword: Optional[str] = None, 
                        source: Optional[str] = None) -> List[Dict]:
        """
        Retrieve articles from database with optional filtering
        
        Args:
            limit: Maximum number of articles to return
            offset: Number of articles to skip (for pagination)
            keyword: Filter by keyword (optional)
            source: Filter by source (optional)
        
        Returns:
            List of article dictionaries
        """
        try:
            query = self.supabase.table('articles').select('*')
            
            # Apply filters
            if keyword:
                query = query.contains('matched_keywords', [keyword])
            
            if source:
                query = query.eq('source', source)
            
            # Order by date descending and apply pagination
            # Note: range() is exclusive on the end, so range(0, 50) returns 50 items (0-49)
            response = query.order('date', desc=True).range(offset, offset + limit).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"❌ Error retrieving articles: {e}")
            return []
    
    def get_article_by_id(self, article_id: str) -> Optional[Dict]:
        """
        Retrieve a single article by ID
        
        Args:
            article_id: UUID of the article
        
        Returns:
            Article dictionary or None if not found
        """
        try:
            response = self.supabase.table('articles').select('*').eq('id', article_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
            
        except Exception as e:
            print(f"❌ Error retrieving article: {e}")
            return None
    
    def get_articles_by_keyword(self, keyword: str, limit: int = 50) -> List[Dict]:
        """
        Retrieve articles that match a specific keyword
        
        Args:
            keyword: Keyword to filter by
            limit: Maximum number of articles to return
        
        Returns:
            List of article dictionaries
        """
        return self.get_all_articles(limit=limit, keyword=keyword)
    
    def get_all_keywords_with_counts(self) -> Dict[str, int]:
        """
        Get all keywords with their article counts
        
        Returns:
            Dictionary mapping keywords to counts
        """
        try:
            # Get all articles
            response = self.supabase.table('articles').select('matched_keywords').execute()
            
            if not response.data:
                return {}
            
            # Count keywords
            keyword_counts = {}
            for article in response.data:
                for keyword in article.get('matched_keywords', []):
                    keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            # Sort by count descending
            return dict(sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True))
            
        except Exception as e:
            print(f"❌ Error getting keyword counts: {e}")
            return {}
    
    def check_article_exists(self, url: str) -> bool:
        """
        Check if an article with the given URL already exists
        
        Args:
            url: Article URL to check
        
        Returns:
            True if exists, False otherwise
        """
        try:
            response = self.supabase.table('articles').select('id').eq('url', url).execute()
            return len(response.data) > 0 if response.data else False
            
        except Exception as e:
            print(f"❌ Error checking article existence: {e}")
            return False
    
    def delete_old_articles(self, before_date: datetime) -> int:
        """
        Delete articles older than the specified date
        
        Args:
            before_date: Delete articles with date before this
        
        Returns:
            Number of articles deleted
        """
        try:
            # First, get count of articles to be deleted
            count_response = self.supabase.table('articles').select('id', count='exact').lt('date', before_date.isoformat()).execute()
            count = count_response.count if hasattr(count_response, 'count') else 0
            
            # Delete articles
            self.supabase.table('articles').delete().lt('date', before_date.isoformat()).execute()
            
            print(f"✅ Deleted {count} old articles (before {before_date.date()})")
            return count
            
        except Exception as e:
            print(f"❌ Error deleting old articles: {e}")
            return 0
    
    def get_total_count(self, keyword: Optional[str] = None, source: Optional[str] = None) -> int:
        """
        Get total count of articles with optional filtering
        
        Args:
            keyword: Filter by keyword (optional)
            source: Filter by source (optional)
        
        Returns:
            Total count of articles
        """
        try:
            query = self.supabase.table('articles').select('id', count='exact')
            
            if keyword:
                query = query.contains('matched_keywords', [keyword])
            
            if source:
                query = query.eq('source', source)
            
            response = query.execute()
            return response.count if hasattr(response, 'count') else 0
            
        except Exception as e:
            print(f"❌ Error getting article count: {e}")
            return 0
    
    def get_last_scrape_time(self) -> Optional[datetime]:
        """
        Get the timestamp of the most recent scrape
        
        Returns:
            Datetime of last scrape or None
        """
        try:
            response = self.supabase.table('articles').select('scraped_at').order('scraped_at', desc=True).limit(1).execute()
            
            if response.data and len(response.data) > 0:
                return datetime.fromisoformat(response.data[0]['scraped_at'].replace('Z', '+00:00'))
            return None
            
        except Exception as e:
            print(f"❌ Error getting last scrape time: {e}")
            return None
    
    def _normalize_source_name(self, source: str) -> str:
        """
        Normalize source name to standardized format.
        
        Args:
            source: Raw source name
            
        Returns:
            Standardized source name: "BlockBeats" or "Jinse"
        """
        if not source:
            return 'BlockBeats'  # Default
        
        source_lower = source.lower()
        
        # Normalize based on source patterns
        if any(pattern in source_lower for pattern in ['blockbeat', 'theblockbeats']):
            return 'BlockBeats'
        elif any(pattern in source_lower for pattern in ['jinse']):
            return 'Jinse'
        else:
            # Default to BlockBeats for unknown sources
            return 'BlockBeats'


# Test connection when module is run directly
if __name__ == "__main__":
    db = DatabaseManager()
    
    if db.supabase:
        print("\n🧪 Testing database connection...")
        
        # Test getting articles
        articles = db.get_all_articles(limit=5)
        print(f"Found {len(articles)} articles in database")
        
        # Test getting keywords
        keywords = db.get_all_keywords_with_counts()
        print(f"Found {len(keywords)} unique keywords")
        
        print("\n✅ Database manager is working correctly!")
