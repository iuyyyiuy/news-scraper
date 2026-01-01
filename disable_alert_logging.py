#!/usr/bin/env python3
"""
Disable alert logging to eliminate 404 errors
This is a quick fix that keeps the main system working without alert table errors
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_minimal_alert_logger():
    """Create a minimal alert logger that doesn't use database"""
    
    alert_logger_code = '''"""
Minimal Alert Logger - File-only version to avoid 404 errors
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict


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


class AlertLogger:
    """
    Minimal alert logging system - file-only to avoid database 404 errors
    """
    
    def __init__(self):
        self.current_session_id: Optional[str] = None
        print("📁 Alert logging: Using file-only mode (no database)")
        
    def start_scraping_session(self, sources: List[str]) -> str:
        """Start a new scraping session and return session ID"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_session_id = session_id
        
        self.log_info(
            component="SessionManager",
            message=f"Started scraping session: {session_id}",
            details={"sources_to_process": sources}
        )
        
        return session_id
    
    def end_scraping_session(self):
        """End the current scraping session"""
        if self.current_session_id:
            self.log_info(
                component="SessionManager",
                message=f"Completed scraping session: {self.current_session_id}",
                details={}
            )
        
        self.current_session_id = None
        return None
    
    def update_session_stats(self, **kwargs):
        """Update session statistics - minimal implementation"""
        pass
    
    def log_info(self, component: str, message: str, details: Dict[str, Any] = None):
        """Log an info-level message"""
        self._log_entry(AlertLevel.INFO, component, message, details or {})
    
    def log_warning(self, component: str, message: str, details: Dict[str, Any] = None):
        """Log a warning-level message"""
        self._log_entry(AlertLevel.WARNING, component, message, details or {})
    
    def log_error(self, component: str, message: str, details: Dict[str, Any] = None, exception: Exception = None):
        """Log an error-level message"""
        error_details = details or {}
        if exception:
            error_details.update({
                'exception_type': type(exception).__name__,
                'exception_message': str(exception)
            })
        
        self._log_entry(AlertLevel.ERROR, component, message, error_details)
    
    def log_critical(self, component: str, message: str, details: Dict[str, Any] = None, exception: Exception = None):
        """Log a critical-level message"""
        error_details = details or {}
        if exception:
            error_details.update({
                'exception_type': type(exception).__name__,
                'exception_message': str(exception)
            })
        
        self._log_entry(AlertLevel.CRITICAL, component, message, error_details)
    
    def log_scraping_operation(self, source: str, articles_found: int, articles_stored: int, 
                             articles_duplicate: int, duration_seconds: float, errors: List[str] = None):
        """Log a complete scraping operation for a source"""
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
        
        # Store in file
        self._store_log_entry(entry)
    
    def _store_log_entry(self, entry: AlertLogEntry):
        """Store log entry in file"""
        try:
            log_file = f"alert_logs_{datetime.now().strftime('%Y%m%d')}.json"
            with open(log_file, 'a') as f:
                f.write(json.dumps(entry.to_dict(), default=str) + '\\n')
        except Exception as e:
            print(f"❌ Failed to write log: {e}")


# Global logger instance
alert_logger = AlertLogger()
'''
    
    return alert_logger_code

def main():
    """Create minimal alert logger to replace the database version"""
    
    print("🔧 Creating minimal alert logger (file-only, no database)")
    print("=" * 60)
    
    # Create the minimal alert logger
    minimal_code = create_minimal_alert_logger()
    
    # Write to file
    with open('scraper/core/alert_logger_minimal.py', 'w') as f:
        f.write(minimal_code)
    
    print("✅ Created scraper/core/alert_logger_minimal.py")
    
    # Create backup of original
    import shutil
    try:
        shutil.copy('scraper/core/alert_logger.py', 'scraper/core/alert_logger_original.py')
        print("📁 Backed up original to alert_logger_original.py")
    except Exception as e:
        print(f"⚠️ Could not backup original: {e}")
    
    # Replace the original with minimal version
    with open('scraper/core/alert_logger.py', 'w') as f:
        f.write(minimal_code)
    
    print("✅ Replaced alert_logger.py with minimal version")
    print("\n" + "=" * 60)
    print("🎉 SUCCESS: Alert logging now uses file-only mode")
    print("📁 Logs will be saved to alert_logs_YYYYMMDD.json files")
    print("🚫 No more 404 database errors!")
    print("=" * 60)

if __name__ == "__main__":
    main()