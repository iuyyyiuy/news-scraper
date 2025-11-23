"""
Web API for the news scraper with web interface.
"""
import asyncio
import logging
from datetime import datetime, date
from typing import Optional, List
import threading
from queue import Queue

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import json

from scraper.core import (
    SessionManager, Session, SessionStatus,
    Config, ScraperController, ScrapeRequest, BlockBeatsScraper
)
from scraper.core.storage import CSVDataStore, JSONDataStore

# Set up logging
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="News Scraper API",
    description="Web API for scraping news articles with date range and keyword filtering",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global session manager
session_manager = SessionManager(retention_hours=24)

# Configuration for scraper
DEFAULT_CONFIG = {
    "target_url": "https://www.theblockbeats.info/newsflash",  # BlockBeats newsflash listing page
    "max_articles": 500,  # How many articles to check (not how many to save)
    "request_delay": 2.0,
    "timeout": 30,
    "max_retries": 3,
    "selectors": {}
}


# Pydantic models for API
class ScrapeRequestModel(BaseModel):
    """Request model for starting a scrape."""
    days_filter: int = Field(..., description="Number of days to look back (e.g., 7 for last 7 days)", ge=1, le=90)
    keywords: List[str] = Field(..., description="Keywords to filter articles")
    max_articles: Optional[int] = Field(None, description="Maximum number of articles to scrape per source")
    sources: List[str] = Field(default=['blockbeats'], description="News sources to scrape from")
    enable_deduplication: bool = Field(default=True, description="Enable deduplication across sources")
    target_url: Optional[str] = Field(None, description="Target URL to scrape (optional, for backward compatibility)")
    
    @validator('keywords')
    def validate_keywords(cls, v):
        """Validate keywords list."""
        if not v:
            raise ValueError('At least one keyword is required')
        # Clean and normalize keywords
        return [kw.strip() for kw in v if kw.strip()]
    
    @validator('max_articles')
    def validate_max_articles(cls, v):
        """Validate max_articles if provided."""
        if v is not None and v <= 0:
            raise ValueError('max_articles must be greater than 0')
        return v
    
    @validator('sources')
    def validate_sources(cls, v):
        """Validate sources list."""
        if not v:
            raise ValueError('At least one source is required')
        valid_sources = ['blockbeats', 'jinse', 'panews']
        for source in v:
            if source.lower() not in valid_sources:
                raise ValueError(f'Invalid source: {source}. Valid sources: {valid_sources}')
        return [s.lower() for s in v]


class ScrapeResponseModel(BaseModel):
    """Response model for scrape initiation."""
    session_id: str
    message: str
    status: str


class SessionStatusModel(BaseModel):
    """Response model for session status."""
    session_id: str
    status: str
    articles_found: int
    articles_scraped: int
    start_time: str
    end_time: Optional[str]
    error_message: Optional[str]
    csv_ready: bool
    duration_seconds: float
    start_date: Optional[str]
    end_date: Optional[str]
    keywords: List[str]
    keywords: List[str]


def run_scraper_task(
    session_id: str,
    days_filter: int,
    keywords: List[str],
    max_articles: Optional[int],
    sources: List[str],
    enable_deduplication: bool
):
    """
    Background task to run the multi-source scraper.
    
    Args:
        session_id: Session ID
        days_filter: Number of days to look back
        keywords: Keywords for filtering
        max_articles: Maximum articles to scrape per source
        sources: List of sources to scrape from
        enable_deduplication: Whether to enable deduplication
    """
    try:
        from scraper.core.multi_source_scraper import MultiSourceScraper
        from scraper.core.storage import CSVDataStore
        from datetime import timedelta
        
        logger.info(f"Starting multi-source scraper task for session {session_id}")
        logger.info(f"Days filter: Last {days_filter} days")
        logger.info(f"Keywords: {keywords}")
        logger.info(f"Sources: {sources}")
        logger.info(f"Deduplication: {enable_deduplication}")
        
        # Calculate date range
        end_date_obj = datetime.now().date()
        start_date_obj = end_date_obj - timedelta(days=days_filter)
        
        # Create config
        config = Config(
            target_url="",  # Not used for multi-source
            max_articles=max_articles or DEFAULT_CONFIG["max_articles"],
            request_delay=DEFAULT_CONFIG["request_delay"],
            output_format="csv",
            output_path=f"temp_session_{session_id}.csv",
            timeout=DEFAULT_CONFIG["timeout"],
            max_retries=DEFAULT_CONFIG["max_retries"],
            selectors=DEFAULT_CONFIG["selectors"]
        )
        
        # Create data store
        data_store = CSVDataStore(config.output_path)
        
        # Set up progress callback with source tracking
        def progress_callback(source: str, articles_found: int, articles_scraped: int):
            session_manager.update_progress(
                session_id,
                articles_found=articles_found,
                articles_scraped=articles_scraped
            )
            # Log with source prefix (don't show in "All" tab)
            session_manager.add_log(
                session_id,
                f"[{source.upper()}] 检查: {articles_found}, 抓取: {articles_scraped}",
                "progress",
                source=source,
                show_in_all=False
            )
        
        # Set up logging callback with source tracking
        def log_callback(message: str, log_type: str = 'info', source: str = None, show_in_all: bool = True):
            session_manager.add_log(session_id, message, log_type, source=source, show_in_all=show_in_all)
        
        # Log start
        log_callback("🚀 开始多源爬取...", "info")
        log_callback(f"📅 日期范围: {start_date_obj} 到 {end_date_obj}", "info")
        log_callback(f"🔑 关键词: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}", "info")
        log_callback(f"📰 来源: {', '.join([s.upper() for s in sources])}", "info")
        log_callback(f"🔄 去重: {'启用' if enable_deduplication else '禁用'}", "info")
        log_callback(f"📊 每个来源最多检查: {config.max_articles} 篇", "info")
        
        # Create multi-source scraper
        scraper = MultiSourceScraper(
            config=config,
            data_store=data_store,
            start_date=start_date_obj,
            end_date=end_date_obj,
            keywords_filter=keywords,
            sources=sources,
            enable_deduplication=enable_deduplication,
            progress_callback=progress_callback,
            log_callback=log_callback
        )
        
        # Run scraper
        result = scraper.scrape(parallel=True)
        
        # Get per-source results
        source_results = scraper.get_source_results()
        
        # Log per-source summary
        log_callback("=" * 60, "info")
        log_callback("📊 各来源统计:", "info")
        for source, src_result in source_results.items():
            log_callback(
                f"  {source.upper()}: 检查 {src_result.total_articles_found} 篇, "
                f"抓取 {src_result.articles_scraped} 篇",
                "info",
                source=source
            )
        
        # Log deduplication stats
        if enable_deduplication and scraper.deduplicator:
            dedup_stats = scraper.deduplicator.get_statistics()
            log_callback("=" * 60, "info")
            log_callback(f"🔍 去重统计: 移除 {dedup_stats['duplicates_found']} 篇重复文章", "info")
        
        log_callback("=" * 60, "info")
        log_callback(f"✅ 爬取完成！最终保存 {result.articles_scraped} 篇唯一文章", "success")
        
        # Get session and add all scraped articles
        session = session_manager.get_session(session_id)
        if session:
            for article in data_store.get_all_articles():
                session_manager.add_article(session_id, article)
        
        # Mark session as complete
        session_manager.complete_session(session_id, result)
        
        logger.info(f"Multi-source scraper task completed for session {session_id}")
        logger.info(f"Articles scraped: {result.articles_scraped}")
        
    except Exception as e:
        logger.error(f"Scraper task failed for session {session_id}: {str(e)}", exc_info=True)
        log_callback(f"❌ 错误: {str(e)}", "error")
        session_manager.fail_session(session_id, str(e))


@app.get("/")
async def root():
    """Serve the main web interface."""
    return FileResponse("scraper/templates/index.html")


@app.post("/api/scrape", response_model=ScrapeResponseModel)
async def start_scrape(
    request: ScrapeRequestModel,
    background_tasks: BackgroundTasks
):
    """
    Start a new scraping session.
    
    Args:
        request: Scrape request parameters
        background_tasks: FastAPI background tasks
        
    Returns:
        Session ID and status
    """
    try:
        # Calculate date range from days_filter
        from datetime import timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.days_filter)
        
        # Create session
        session_id = session_manager.create_session(
            start_date=start_date,
            end_date=end_date,
            keywords=request.keywords
        )
        
        logger.info(f"Created session {session_id}")
        logger.info(f"Days filter: Last {request.days_filter} days")
        logger.info(f"Date range: {start_date.date()} to {end_date.date()}")
        logger.info(f"Keywords: {request.keywords}")
        
        # Start scraper in background
        background_tasks.add_task(
            run_scraper_task,
            session_id,
            request.days_filter,
            request.keywords,
            request.max_articles,
            request.sources,
            request.enable_deduplication
        )
        
        return ScrapeResponseModel(
            session_id=session_id,
            message="Scraping session started successfully",
            status="running"
        )
        
    except Exception as e:
        logger.error(f"Failed to start scraping session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status/{session_id}", response_model=SessionStatusModel)
async def get_session_status(session_id: str):
    """
    Get the status of a scraping session.
    
    Args:
        session_id: Session ID
        
    Returns:
        Session status information
    """
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionStatusModel(**session.to_dict())


@app.get("/api/status/{session_id}/stream")
async def stream_session_status(session_id: str):
    """
    Stream real-time updates for a scraping session using Server-Sent Events.
    
    Args:
        session_id: Session ID
        
    Returns:
        SSE stream of session updates
    """
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    async def event_generator():
        """Generate SSE events for session updates."""
        try:
            # Send initial status
            session_data = session.to_dict()
            yield f"data: {json.dumps(session_data)}\n\n"
            
            # Keep streaming while session is running
            while session.status == SessionStatus.RUNNING:
                await asyncio.sleep(1)  # Update every second
                
                # Get latest session data
                current_session = session_manager.get_session(session_id)
                if current_session:
                    session_data = current_session.to_dict()
                    yield f"data: {json.dumps(session_data)}\n\n"
                else:
                    break
            
            # Send final status
            final_session = session_manager.get_session(session_id)
            if final_session:
                session_data = final_session.to_dict()
                yield f"data: {json.dumps(session_data)}\n\n"
            
        except Exception as e:
            logger.error(f"Error in SSE stream: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/api/download/{session_id}")
async def download_csv(session_id: str):
    """
    Download scraped articles as CSV file.
    
    Args:
        session_id: Session ID
        
    Returns:
        CSV file download
    """
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status != SessionStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Session is not completed yet"
        )
    
    if not session.csv_ready:
        raise HTTPException(
            status_code=400,
            detail="No articles available for download"
        )
    
    # Generate CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"news_articles_{timestamp}.csv"
    filepath = f"temp_{session_id}.csv"
    
    try:
        # Create CSV data store and save articles
        csv_store = CSVDataStore(filepath)
        for article in session.articles:
            csv_store.save_article(article)
        
        # Return file for download
        return FileResponse(
            filepath,
            media_type="text/csv",
            filename=filename,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to generate CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate CSV: {str(e)}")


@app.get("/api/sessions")
async def list_sessions():
    """
    List all scraping sessions.
    
    Returns:
        List of all sessions
    """
    sessions = session_manager.get_all_sessions()
    return {
        "sessions": [session.to_dict() for session in sessions],
        "total": len(sessions),
        "active": len([s for s in sessions if s.status == SessionStatus.RUNNING])
    }


@app.delete("/api/sessions/cleanup")
async def cleanup_sessions():
    """
    Clean up old completed sessions.
    
    Returns:
        Number of sessions removed
    """
    removed = session_manager.cleanup_old_sessions()
    return {
        "message": f"Cleaned up {removed} old session(s)",
        "removed_count": removed
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(session_manager.get_active_sessions())
    }


# Mount static files (for CSS, JS, etc.)
try:
    app.mount("/static", StaticFiles(directory="scraper/static"), name="static")
except RuntimeError:
    # Directory doesn't exist yet, will be created later
    pass
