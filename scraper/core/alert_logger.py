"""
Alert Logger for News Scraping System
Provides comprehensive monitoring and logging capabilities
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict
from scraper.core.database_manager import DatabaseManager


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class AlertLogEntry:
    """Represents a single alert log entry"""
    timestamp: datetime
    level: AlertLevel
    component: str
    message: str
    details: Dict[str, Any]
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.value,
            'component': self.component,
            'message': self.message,
            'details': self.details,
            'session_id': self.session_id
        }


@dataclass
class ScrapingSessionStats:
    """Statistics for a scraping session"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    sources_processed: List[str]
    articles_found: int
    articles_stored: int
    articles_duplicate: int
    errors_encountered: int
    performance_metrics: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'sources_processed': self.sources_processed,
            'articles_found': self.articles_found,
            'articles_stored': self.articles_stored,
            'articles_duplicate': self.articles_duplicate,
            'errors_encountered': self.errors_encountered,
            'performance_metrics': self.performance_metrics
        }


class AlertLogger:
    """
    Comprehensive alert logging system for monitoring news scraping operations
    """
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.current_session_id: Optional[str] = None
        self.session_stats: Optional[ScrapingSessionStats] = None
        
    def start_scraping_session(self, sources: List[str]) -> str:
        """
        Start a new scraping session and return session ID
        
        Args:
            sources: List of sources to be processed
            
        Returns:
            Session ID for tracking
        """
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_session_id = session_id
        
        self.session_stats = ScrapingSessionStats(
            session_id=session_id,
            start_time=datetime.now(timezone.utc),
            end_time=None,
            sources_processed=[],
            articles_found=0,
            articles_stored=0,
            articles_duplicate=0,
            errors_encountered=0,
            performance_metrics={}
        )
        
        self.log_info(
            component="SessionManager",
            message=f"Started scraping session: {session_id}",
            details={
                "sources_to_process": sources,
                "start_time": self.session_stats.start_time.isoformat()
            }
        )
        
        return session_id
    
    def end_scraping_session(self) -> Optional[ScrapingSessionStats]:
        """
        End the current scraping session and log summary
        
        Returns:
            Session statistics if session was active
        """
        if not self.session_stats:
            self.log_warning(
                component="SessionManager",
                message="Attempted to end session but no active session found",
                details={}
            )
            return None
        
        self.session_stats.end_time = datetime.now(timezone.utc)
        duration = (self.session_stats.end_time - self.session_stats.start_time).total_seconds()
        self.session_stats.performance_metrics['total_duration_seconds'] = duration
        
        # Calculate success rate
        total_processed = self.session_stats.articles_found
        success_rate = (self.session_stats.articles_stored / total_processed * 100) if total_processed > 0 else 0
        self.session_stats.performance_metrics['success_rate_percent'] = success_rate
        
        # Log session summary
        self.log_info(
            component="SessionManager",
            message=f"Completed scraping session: {self.session_stats.session_id}",
            details={
                "duration_seconds": duration,
                "articles_found": self.session_stats.articles_found,
                "articles_stored": self.session_stats.articles_stored,
                "articles_duplicate": self.session_stats.articles_duplicate,
                "success_rate_percent": success_rate,
                "errors_encountered": self.session_stats.errors_encountered
            }
        )
        
        # Store session stats in database
        self._store_session_stats()
        
        # Reset current session
        completed_session = self.session_stats
        self.session_stats = None
        self.current_session_id = None
        
        return completed_session
    
    def update_session_stats(self, **kwargs):
        """Update current session statistics"""
        if not self.session_stats:
            return
        
        for key, value in kwargs.items():
            if hasattr(self.session_stats, key):
                if key == 'sources_processed' and isinstance(value, str):
                    # Add source to list if not already present
                    if value not in self.session_stats.sources_processed:
                        self.session_stats.sources_processed.append(value)
                else:
                    setattr(self.session_stats, key, value)
    
    def log_info(self, component: str, message: str, details: Dict[str, Any] = None):
        """Log an info-level message"""
        self._log_entry(AlertLevel.INFO, component, message, details or {})
    
    def log_warning(self, component: str, message: str, details: Dict[str, Any] = None):
        """Log a warning-level message"""
        self._log_entry(AlertLevel.WARNING, component, message, details or {})
        if self.session_stats:
            self.session_stats.errors_encountered += 1
    
    def log_error(self, component: str, message: str, details: Dict[str, Any] = None, exception: Exception = None):
        """Log an error-level message"""
        error_details = details or {}
        if exception:
            error_details.update({
                'exception_type': type(exception).__name__,
                'exception_message': str(exception)
            })
        
        self._log_entry(AlertLevel.ERROR, component, message, error_details)
        if self.session_stats:
            self.session_stats.errors_encountered += 1
    
    def log_critical(self, component: str, message: str, details: Dict[str, Any] = None, exception: Exception = None):
        """Log a critical-level message"""
        error_details = details or {}
        if exception:
            error_details.update({
                'exception_type': type(exception).__name__,
                'exception_message': str(exception)
            })
        
        self._log_entry(AlertLevel.CRITICAL, component, message, error_details)
        if self.session_stats:
            self.session_stats.errors_encountered += 1
    
    def log_scraping_operation(self, source: str, articles_found: int, articles_stored: int, 
                             articles_duplicate: int, duration_seconds: float, errors: List[str] = None):
        """
        Log a complete scraping operation for a source
        
        Args:
            source: Source name (BlockBeats, Jinse)
            articles_found: Number of articles found
            articles_stored: Number of articles successfully stored
            articles_duplicate: Number of duplicate articles skipped
            duration_seconds: Time taken for the operation
            errors: List of error messages encountered
        """
        details = {
            'source': source,
            'articles_found': articles_found,
            'articles_stored': articles_stored,
            'articles_duplicate': articles_duplicate,
            'duration_seconds': duration_seconds,
            'success_rate_percent': (articles_stored / articles_found * 100) if articles_found > 0 else 0
        }
        
        if errors:
            details['errors'] = errors
        
        # Update session stats
        if self.session_stats:
            self.session_stats.articles_found += articles_found
            self.session_stats.articles_stored += articles_stored
            self.session_stats.articles_duplicate += articles_duplicate
            self.update_session_stats(sources_processed=source)
        
        # Determine log level based on success rate
        success_rate = details['success_rate_percent']
        if success_rate >= 80:
            self.log_info("ScrapingOperation", f"Successfully scraped {source}", details)
        elif success_rate >= 50:
            self.log_warning("ScrapingOperation", f"Partial success scraping {source}", details)
        else:
            self.log_error("ScrapingOperation", f"Poor success rate scraping {source}", details)
    
    def log_database_operation(self, operation: str, success: bool, details: Dict[str, Any] = None):
        """Log database operations for monitoring"""
        operation_details = details or {}
        operation_details['operation'] = operation
        operation_details['success'] = success
        
        if success:
            self.log_info("DatabaseOperation", f"Database {operation} successful", operation_details)
        else:
            self.log_error("DatabaseOperation", f"Database {operation} failed", operation_details)
    
    def get_recent_logs(self, limit: int = 100, level: Optional[AlertLevel] = None) -> List[Dict[str, Any]]:
        """
        Get recent log entries
        
        Args:
            limit: Maximum number of entries to return
            level: Filter by alert level (optional)
            
        Returns:
            List of log entries
        """
        try:
            query = self.db_manager.supabase.table('alert_logs').select('*')
            
            if level:
                query = query.eq('level', level.value)
            
            response = query.order('timestamp', desc=True).limit(limit).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"❌ Error retrieving logs: {e}")
            return []
    
    def get_session_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent scraping session history"""
        try:
            response = self.db_manager.supabase.table('scraping_sessions').select('*').order('start_time', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"❌ Error retrieving session history: {e}")
            return []
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        try:
            # Get recent session stats
            recent_sessions = self.get_session_history(limit=5)
            
            # Calculate health metrics
            if recent_sessions:
                avg_success_rate = sum(s.get('performance_metrics', {}).get('success_rate_percent', 0) for s in recent_sessions) / len(recent_sessions)
                avg_duration = sum(s.get('performance_metrics', {}).get('total_duration_seconds', 0) for s in recent_sessions) / len(recent_sessions)
                total_errors = sum(s.get('errors_encountered', 0) for s in recent_sessions)
            else:
                avg_success_rate = 0
                avg_duration = 0
                total_errors = 0
            
            # Get recent error count
            recent_errors = self.get_recent_logs(limit=50, level=AlertLevel.ERROR)
            recent_criticals = self.get_recent_logs(limit=50, level=AlertLevel.CRITICAL)
            
            # Determine overall health status
            if avg_success_rate >= 90 and len(recent_criticals) == 0:
                health_status = "HEALTHY"
            elif avg_success_rate >= 70 and len(recent_criticals) <= 1:
                health_status = "WARNING"
            else:
                health_status = "CRITICAL"
            
            return {
                'health_status': health_status,
                'avg_success_rate_percent': avg_success_rate,
                'avg_session_duration_seconds': avg_duration,
                'recent_errors_count': len(recent_errors),
                'recent_criticals_count': len(recent_criticals),
                'total_recent_errors': total_errors,
                'last_session_time': recent_sessions[0].get('start_time') if recent_sessions else None
            }
            
        except Exception as e:
            return {
                'health_status': 'UNKNOWN',
                'error': str(e)
            }
    
    def _log_entry(self, level: AlertLevel, component: str, message: str, details: Dict[str, Any]):
        """Internal method to create and store log entry"""
        entry = AlertLogEntry(
            timestamp=datetime.now(timezone.utc),
            level=level,
            component=component,
            message=message,
            details=details,
            session_id=self.current_session_id
        )
        
        # Print to console for immediate visibility
        timestamp_str = entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        level_emoji = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.ERROR: "❌",
            AlertLevel.CRITICAL: "🚨"
        }
        
        print(f"{level_emoji.get(level, '📝')} [{timestamp_str}] {component}: {message}")
        if details:
            print(f"   Details: {json.dumps(details, indent=2, default=str)}")
        
        # Store in database
        self._store_log_entry(entry)
    
    def _store_log_entry(self, entry: AlertLogEntry):
        """Store log entry in database with fallback to file"""
        try:
            data = entry.to_dict()
            self.db_manager.supabase.table('alert_logs').insert(data).execute()
        except Exception as e:
            # Fallback to file logging if database fails (tables don't exist yet)
            self._fallback_file_log(entry)
    
    def _store_session_stats(self):
        """Store session statistics in database with fallback to file"""
        if not self.session_stats:
            return
        
        try:
            data = self.session_stats.to_dict()
            self.db_manager.supabase.table('scraping_sessions').insert(data).execute()
        except Exception as e:
            # Fallback to file logging
            try:
                session_file = f"session_stats_{datetime.now().strftime('%Y%m%d')}.json"
                with open(session_file, 'a') as f:
                    f.write(json.dumps(self.session_stats.to_dict(), default=str) + '\n')
            except Exception as file_error:
                print(f"❌ Failed to write session stats to file: {file_error}")
    
    def _fallback_file_log(self, entry: AlertLogEntry):
        """Fallback file logging when database is unavailable"""
        try:
            log_file = f"alert_logs_{datetime.now().strftime('%Y%m%d')}.json"
            with open(log_file, 'a') as f:
                f.write(json.dumps(entry.to_dict(), default=str) + '\n')
        except Exception as e:
            print(f"❌ Failed to write fallback log: {e}")


# Global logger instance
alert_logger = AlertLogger()