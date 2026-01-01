"""
Session reporting functionality for tracking scraping performance and results.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class ScrapingAttempt:
    """Represents a single article scraping attempt."""
    url: str
    source: str
    success: bool
    error_message: Optional[str] = None
    title: Optional[str] = None
    content_length: Optional[int] = None
    processing_time: Optional[float] = None

@dataclass
class SourceStats:
    """Statistics for a specific news source."""
    source_name: str
    total_attempts: int = 0
    successful_extractions: int = 0
    failed_extractions: int = 0
    articles_stored: int = 0
    total_content_length: int = 0
    avg_processing_time: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_attempts == 0:
            return 0.0
        return (self.successful_extractions / self.total_attempts) * 100

@dataclass
class SessionReport:
    """Complete session report with all statistics."""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration: Optional[float] = None
    sources: Dict[str, SourceStats] = None
    attempts: List[ScrapingAttempt] = None
    summary: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = {}
        if self.attempts is None:
            self.attempts = []
        if self.summary is None:
            self.summary = {}

class SessionReporter:
    """
    Tracks and reports on scraping session performance.
    
    Provides detailed statistics on success rates, failure patterns,
    and performance metrics for debugging and optimization.
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize session reporter.
        
        Args:
            session_id: Unique identifier for this session
        """
        self.session_id = session_id or self._generate_session_id()
        self.report = SessionReport(
            session_id=self.session_id,
            start_time=datetime.now()
        )
        self.reports_dir = Path("session_reports")
        self.reports_dir.mkdir(exist_ok=True)
        
        logger.info(f"Started session reporting: {self.session_id}")
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}"
    
    def record_attempt(self, 
                      url: str, 
                      source: str, 
                      success: bool,
                      error_message: Optional[str] = None,
                      title: Optional[str] = None,
                      content_length: Optional[int] = None,
                      processing_time: Optional[float] = None):
        """
        Record a scraping attempt.
        
        Args:
            url: Article URL
            source: Source website name
            success: Whether extraction was successful
            error_message: Error message if failed
            title: Extracted title if successful
            content_length: Length of extracted content
            processing_time: Time taken to process in seconds
        """
        attempt = ScrapingAttempt(
            url=url,
            source=source,
            success=success,
            error_message=error_message,
            title=title,
            content_length=content_length,
            processing_time=processing_time
        )
        
        self.report.attempts.append(attempt)
        
        # Update source statistics
        if source not in self.report.sources:
            self.report.sources[source] = SourceStats(source_name=source)
        
        stats = self.report.sources[source]
        stats.total_attempts += 1
        
        if success:
            stats.successful_extractions += 1
            if content_length:
                stats.total_content_length += content_length
        else:
            stats.failed_extractions += 1
        
        if processing_time:
            # Update average processing time
            total_time = stats.avg_processing_time * (stats.total_attempts - 1) + processing_time
            stats.avg_processing_time = total_time / stats.total_attempts
        
        logger.debug(f"Recorded attempt: {url} - {'SUCCESS' if success else 'FAILED'}")
    
    def record_storage(self, source: str, count: int = 1):
        """
        Record successful article storage.
        
        Args:
            source: Source website name
            count: Number of articles stored
        """
        if source in self.report.sources:
            self.report.sources[source].articles_stored += count
        else:
            # Create source stats if not exists
            self.report.sources[source] = SourceStats(source_name=source)
            self.report.sources[source].articles_stored = count
    
    def finalize_session(self) -> SessionReport:
        """
        Finalize the session and generate complete report.
        
        Returns:
            Complete session report
        """
        self.report.end_time = datetime.now()
        self.report.total_duration = (
            self.report.end_time - self.report.start_time
        ).total_seconds()
        
        # Generate summary statistics
        self.report.summary = self._generate_summary()
        
        # Save report to file
        self._save_report()
        
        logger.info(f"Finalized session: {self.session_id}")
        return self.report
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics for the session."""
        total_attempts = len(self.report.attempts)
        successful_attempts = sum(1 for a in self.report.attempts if a.success)
        failed_attempts = total_attempts - successful_attempts
        
        total_stored = sum(stats.articles_stored for stats in self.report.sources.values())
        
        # Calculate average processing time
        processing_times = [a.processing_time for a in self.report.attempts if a.processing_time]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        # Error analysis
        error_types = {}
        for attempt in self.report.attempts:
            if not attempt.success and attempt.error_message:
                error_type = attempt.error_message.split(':')[0]  # Get error type
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            "total_attempts": total_attempts,
            "successful_extractions": successful_attempts,
            "failed_extractions": failed_attempts,
            "success_rate_percent": (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0,
            "articles_stored": total_stored,
            "storage_rate_percent": (total_stored / successful_attempts * 100) if successful_attempts > 0 else 0,
            "avg_processing_time_seconds": round(avg_processing_time, 3),
            "total_duration_seconds": self.report.total_duration,
            "sources_processed": len(self.report.sources),
            "error_types": error_types
        }
    
    def _save_report(self):
        """Save the session report to a JSON file."""
        try:
            filename = f"{self.session_id}_report.json"
            filepath = self.reports_dir / filename
            
            # Convert report to dictionary for JSON serialization
            report_dict = asdict(self.report)
            
            # Convert datetime objects to ISO format strings
            report_dict['start_time'] = self.report.start_time.isoformat()
            if self.report.end_time:
                report_dict['end_time'] = self.report.end_time.isoformat()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Session report saved: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save session report: {e}")
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current session statistics without finalizing."""
        return {
            "session_id": self.session_id,
            "duration_seconds": (datetime.now() - self.report.start_time).total_seconds(),
            "total_attempts": len(self.report.attempts),
            "sources": {name: {
                "attempts": stats.total_attempts,
                "success_rate": stats.success_rate,
                "stored": stats.articles_stored
            } for name, stats in self.report.sources.items()}
        }
    
    def print_summary(self):
        """Print a human-readable summary of the session."""
        if not self.report.summary:
            self.report.summary = self._generate_summary()
        
        print(f"\n📊 Session Report: {self.session_id}")
        print("=" * 50)
        print(f"⏱️  Duration: {self.report.summary['total_duration_seconds']:.1f} seconds")
        print(f"🎯 Success Rate: {self.report.summary['success_rate_percent']:.1f}%")
        print(f"📄 Articles Extracted: {self.report.summary['successful_extractions']}")
        print(f"💾 Articles Stored: {self.report.summary['articles_stored']}")
        print(f"⚡ Avg Processing Time: {self.report.summary['avg_processing_time_seconds']:.3f}s")
        
        print(f"\n📈 Source Breakdown:")
        for source_name, stats in self.report.sources.items():
            print(f"  {source_name}:")
            print(f"    Attempts: {stats.total_attempts}")
            print(f"    Success Rate: {stats.success_rate:.1f}%")
            print(f"    Stored: {stats.articles_stored}")
        
        if self.report.summary['error_types']:
            print(f"\n❌ Error Types:")
            for error_type, count in self.report.summary['error_types'].items():
                print(f"  {error_type}: {count}")
        
        print("=" * 50)