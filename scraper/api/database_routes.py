"""
Database API Routes for News Database Feature
FastAPI routes for accessing stored articles
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict
from datetime import datetime

from scraper.core.database_manager import DatabaseManager
from scraper.core.scheduler import SchedulerService

# Create router
router = APIRouter(prefix="/api/database", tags=["database"])

# Initialize database manager
db_manager = DatabaseManager()

# Initialize scheduler (will be started by main app)
scheduler_service = None


def init_scheduler():
    """Initialize and start the scheduler service"""
    global scheduler_service
    if scheduler_service is None:
        scheduler_service = SchedulerService()
        scheduler_service.start_scheduler()
    return scheduler_service


@router.get("/articles")
async def get_articles(
    limit: int = Query(50, ge=1, le=100, description="Number of articles to return"),
    offset: int = Query(0, ge=0, description="Number of articles to skip"),
    keyword: Optional[str] = Query(None, description="Filter by keyword"),
    source: Optional[str] = Query(None, description="Filter by source (BlockBeats or Jinse)")
):
    """
    Get articles from database with optional filtering
    """
    try:
        articles = db_manager.get_all_articles(
            limit=limit,
            offset=offset,
            keyword=keyword,
            source=source
        )
        
        total_count = db_manager.get_total_count(keyword=keyword, source=source)
        
        return {
            "success": True,
            "data": articles,
            "total": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/articles/{article_id}")
async def get_article(article_id: str):
    """
    Get a single article by ID
    """
    try:
        article = db_manager.get_article_by_id(article_id)
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return {
            "success": True,
            "data": article
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keywords")
async def get_keywords():
    """
    Get all keywords with article counts
    """
    try:
        keywords = db_manager.get_all_keywords_with_counts()
        
        # Convert to list format for easier frontend consumption
        keyword_list = [
            {"keyword": k, "count": v}
            for k, v in keywords.items()
        ]
        
        return {
            "success": True,
            "data": keyword_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats():
    """
    Get database statistics
    """
    try:
        total_count = db_manager.get_total_count()
        last_scrape = db_manager.get_last_scrape_time()
        keywords = db_manager.get_all_keywords_with_counts()
        
        return {
            "success": True,
            "data": {
                "total_articles": total_count,
                "last_scrape": last_scrape.isoformat() if last_scrape else None,
                "unique_keywords": len(keywords),
                "sources": ["BlockBeats", "Jinse"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scheduler/status")
async def get_scheduler_status():
    """
    Get scheduler status and next run times
    """
    try:
        if scheduler_service is None:
            return {
                "success": True,
                "data": {
                    "running": False,
                    "message": "Scheduler not initialized"
                }
            }
        
        status = scheduler_service.get_scheduler_status()
        
        return {
            "success": True,
            "data": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduler/trigger")
async def trigger_scrape():
    """
    Manually trigger a scrape (for testing)
    """
    try:
        if scheduler_service is None:
            raise HTTPException(status_code=503, detail="Scheduler not initialized")
        
        # Trigger scrape in background
        import threading
        thread = threading.Thread(target=scheduler_service.trigger_scrape_now)
        thread.start()
        
        return {
            "success": True,
            "message": "Scrape triggered successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
