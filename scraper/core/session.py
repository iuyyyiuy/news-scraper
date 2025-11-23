"""
Session management for web interface scraping operations.
"""
import uuid
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from enum import Enum

from .models import Article, ScrapingResult


class SessionStatus(Enum):
    """Status of a scraping session."""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Session:
    """Represents a single scraping session."""
    session_id: str
    status: SessionStatus
    articles_found: int = 0
    articles_scraped: int = 0
    total_articles: int = 0  # Total before deduplication
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    articles: List[Article] = field(default_factory=list)
    scraping_result: Optional[ScrapingResult] = None
    
    # Search parameters
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    keywords: List[str] = field(default_factory=list)
    
    # Logs (organized by source)
    logs: List[dict] = field(default_factory=list)
    source_logs: Dict[str, List[dict]] = field(default_factory=dict)  # Per-source logs
    _last_log_index: int = -1  # Track which log was last sent
    
    @property
    def csv_ready(self) -> bool:
        """Check if CSV is ready for download."""
        return self.status == SessionStatus.COMPLETED
    
    @property
    def duration_seconds(self) -> float:
        """Calculate session duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()
    
    def add_log(self, message: str, log_type: str = 'info', source: str = None, show_in_all: bool = True):
        """
        Add a log entry to the session.
        
        Args:
            message: Log message
            log_type: Type of log (info, success, error, etc.)
            source: Optional source name (blockbeats, jinse, panews)
            show_in_all: Whether to show in "全部" (All) tab (default: True)
        """
        log_entry = {
            'message': message,
            'type': log_type,
            'timestamp': datetime.now().isoformat(),
            'source': source,
            'show_in_all': show_in_all
        }
        
        # Add to general logs
        self.logs.append(log_entry)
        
        # Add to source-specific logs if source is specified
        if source:
            if source not in self.source_logs:
                self.source_logs[source] = []
            self.source_logs[source].append(log_entry)
    
    def to_dict(self) -> dict:
        """Convert session to dictionary for API responses."""
        # Get new log if available
        new_log = None
        new_log_type = None
        new_log_source = None
        new_show_in_all = True
        if self.logs and len(self.logs) > self._last_log_index + 1:
            self._last_log_index = len(self.logs) - 1
            new_log = self.logs[-1].get('message')
            new_log_type = self.logs[-1].get('type')
            new_log_source = self.logs[-1].get('source')
            new_show_in_all = self.logs[-1].get('show_in_all', True)
        
        return {
            "session_id": self.session_id,
            "status": self.status.value,
            "articles_found": self.articles_found,
            "articles_scraped": self.articles_scraped,
            "total_articles": self.total_articles,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "error_message": self.error_message,
            "csv_ready": self.csv_ready,
            "duration_seconds": self.duration_seconds,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "keywords": self.keywords,
            "log": new_log,  # Only send new log
            "log_type": new_log_type,
            "log_source": new_log_source,  # Source of the log
            "show_in_all": new_show_in_all,  # Whether to show in "All" tab
            "source_logs": {source: logs for source, logs in self.source_logs.items()}  # All source logs
        }


class SessionManager:
    """Manages scraping sessions for the web interface."""
    
    def __init__(self, retention_hours: int = 24):
        """
        Initialize the session manager.
        
        Args:
            retention_hours: Number of hours to retain completed sessions
        """
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.Lock()
        self._retention_hours = retention_hours
        self._progress_callbacks: Dict[str, List[Callable]] = {}
    
    def create_session(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        keywords: Optional[List[str]] = None
    ) -> str:
        """
        Create a new scraping session.
        
        Args:
            start_date: Start date for article filtering
            end_date: End date for article filtering
            keywords: Keywords for article filtering
            
        Returns:
            Unique session ID (UUID v4)
        """
        session_id = str(uuid.uuid4())
        
        with self._lock:
            session = Session(
                session_id=session_id,
                status=SessionStatus.RUNNING,
                start_date=start_date,
                end_date=end_date,
                keywords=keywords or []
            )
            self._sessions[session_id] = session
            self._progress_callbacks[session_id] = []
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID.
        
        Args:
            session_id: The session ID
            
        Returns:
            Session object or None if not found
        """
        with self._lock:
            return self._sessions.get(session_id)
    
    def add_log(self, session_id: str, message: str, log_type: str = 'info', source: str = None, show_in_all: bool = True) -> None:
        """
        Add a log entry to a session.
        
        Args:
            session_id: The session ID
            message: Log message
            log_type: Type of log (info, success, filtered, error)
            source: Optional source name (blockbeats, jinse, panews)
            show_in_all: Whether to show in "全部" (All) tab (default: True)
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.add_log(message, log_type, source, show_in_all)
    
    def update_progress(
        self,
        session_id: str,
        articles_found: Optional[int] = None,
        articles_scraped: Optional[int] = None
    ) -> None:
        """
        Update session progress.
        
        Args:
            session_id: The session ID
            articles_found: Number of articles found
            articles_scraped: Number of articles scraped
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return
            
            if articles_found is not None:
                session.articles_found = articles_found
            if articles_scraped is not None:
                session.articles_scraped = articles_scraped
            
            # Trigger progress callbacks
            callbacks = self._progress_callbacks.get(session_id, [])
        
        # Execute callbacks outside the lock to avoid deadlocks
        for callback in callbacks:
            try:
                callback(session)
            except Exception:
                pass  # Ignore callback errors
    
    def add_article(self, session_id: str, article: Article) -> None:
        """
        Add an article to the session.
        
        Args:
            session_id: The session ID
            article: Article to add
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.articles.append(article)
                session.articles_scraped = len(session.articles)
    
    def complete_session(
        self,
        session_id: str,
        scraping_result: ScrapingResult
    ) -> None:
        """
        Mark a session as completed.
        
        Args:
            session_id: The session ID
            scraping_result: Final scraping result
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.status = SessionStatus.COMPLETED
                session.end_time = datetime.now()
                session.scraping_result = scraping_result
    
    def fail_session(self, session_id: str, error_message: str) -> None:
        """
        Mark a session as failed.
        
        Args:
            session_id: The session ID
            error_message: Error message describing the failure
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.status = SessionStatus.FAILED
                session.end_time = datetime.now()
                session.error_message = error_message
    
    def register_progress_callback(
        self,
        session_id: str,
        callback: Callable[[Session], None]
    ) -> None:
        """
        Register a callback for progress updates.
        
        Args:
            session_id: The session ID
            callback: Callback function that receives the session
        """
        with self._lock:
            if session_id in self._progress_callbacks:
                self._progress_callbacks[session_id].append(callback)
    
    def unregister_progress_callback(
        self,
        session_id: str,
        callback: Callable[[Session], None]
    ) -> None:
        """
        Unregister a progress callback.
        
        Args:
            session_id: The session ID
            callback: Callback function to remove
        """
        with self._lock:
            if session_id in self._progress_callbacks:
                try:
                    self._progress_callbacks[session_id].remove(callback)
                except ValueError:
                    pass
    
    def cleanup_old_sessions(self) -> int:
        """
        Remove sessions older than the retention period.
        
        Returns:
            Number of sessions removed
        """
        cutoff_time = datetime.now() - timedelta(hours=self._retention_hours)
        removed_count = 0
        
        with self._lock:
            sessions_to_remove = []
            
            for session_id, session in self._sessions.items():
                # Only cleanup completed or failed sessions
                if session.status in (SessionStatus.COMPLETED, SessionStatus.FAILED):
                    if session.end_time and session.end_time < cutoff_time:
                        sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                del self._sessions[session_id]
                if session_id in self._progress_callbacks:
                    del self._progress_callbacks[session_id]
                removed_count += 1
        
        return removed_count
    
    def get_all_sessions(self) -> List[Session]:
        """
        Get all sessions.
        
        Returns:
            List of all sessions
        """
        with self._lock:
            return list(self._sessions.values())
    
    def get_active_sessions(self) -> List[Session]:
        """
        Get all active (running) sessions.
        
        Returns:
            List of active sessions
        """
        with self._lock:
            return [
                session for session in self._sessions.values()
                if session.status == SessionStatus.RUNNING
            ]
    
    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists.
        
        Args:
            session_id: The session ID
            
        Returns:
            True if session exists, False otherwise
        """
        with self._lock:
            return session_id in self._sessions
