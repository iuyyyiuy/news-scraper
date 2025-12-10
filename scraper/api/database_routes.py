"""
Database API Routes for News Database Feature
FastAPI routes for accessing stored articles
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict
from datetime import datetime

from scraper.core.database_manager import DatabaseManager
# from scraper.core.scheduler import SchedulerService  # Not needed for dashboard

# Create router
router = APIRouter(prefix="/api/database", tags=["database"])

# Initialize database manager
db_manager = DatabaseManager()

# Scheduler not used in dashboard
scheduler_service = None


def normalize_source_name(source: str) -> str:
    """Normalize source name to standard format"""
    if not source:
        return 'Unknown'
    
    source_lower = source.lower()
    if any(pattern in source_lower for pattern in ['blockbeat', 'theblockbeats']):
        return 'BlockBeats'
    elif any(pattern in source_lower for pattern in ['jinse']):
        return 'Jinse'
    else:
        return source  # Return as-is if not recognized


def init_scheduler():
    """Initialize and start the scheduler service"""
    global scheduler_service
    if scheduler_service is None:
        scheduler_service = SchedulerService()
        scheduler_service.start_scheduler()
    return scheduler_service


@router.get("/export/csv")
async def export_csv(
    keyword: Optional[str] = Query(None),
    source: Optional[str] = Query(None)
):
    """Export articles to CSV"""
    from fastapi.responses import StreamingResponse
    import io
    import csv
    from datetime import datetime
    
    articles = db_manager.get_all_articles(limit=1000, keyword=keyword, source=source)
    
    output = io.StringIO()
    output.write('\ufeff')  # BOM for Excel
    writer = csv.writer(output)
    
    writer.writerow(['日期', '来源', '标题', '内容', '关键词', 'URL'])
    
    for article in articles:
        writer.writerow([
            article.get('date', ''),
            article.get('source', ''),
            article.get('title', ''),
            article.get('body_text', ''),
            ', '.join(article.get('matched_keywords', [])),
            article.get('url', '')
        ])
    
    output.seek(0)
    filename = f"crypto_news_{datetime.now().strftime('%Y%m%d')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

def normalize_source_name(source: str) -> str:
    """Normalize source names for display"""
    if not source:
        return source
    source_lower = source.lower()
    if 'blockbeats' in source_lower:
        return 'BlockBeats'
    elif 'jinse' in source_lower:
        return 'Jinse'
    return source

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
        # Validate source parameter
        if source and source not in ['BlockBeats', 'Jinse']:
            raise HTTPException(status_code=400, detail="Invalid source. Must be 'BlockBeats' or 'Jinse'")
        
        articles = db_manager.get_all_articles(
            limit=limit,
            offset=offset,
            keyword=keyword,
            source=source
        )
        
        # Ensure articles is a list
        if not isinstance(articles, list):
            articles = []
        
        # Normalize source names for display and ensure data consistency
        for article in articles:
            if isinstance(article, dict):
                if 'source' in article:
                    article['source'] = normalize_source_name(article['source'])
                # Ensure required fields exist
                if 'title' not in article:
                    article['title'] = 'Untitled'
                if 'date' not in article:
                    article['date'] = datetime.now().isoformat()
                if 'matched_keywords' not in article:
                    article['matched_keywords'] = []
        
        total_count = db_manager.get_total_count(keyword=keyword, source=source)
        
        return {
            "success": True,
            "data": articles,
            "total": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"❌ Error in get_articles: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": "Failed to retrieve articles",
            "data": [],
            "total": 0,
            "limit": limit,
            "offset": offset
        }


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
        
        # Ensure keywords is a dict
        if not isinstance(keywords, dict):
            keywords = {}
        
        # Convert to list format for easier frontend consumption
        keyword_list = [
            {"keyword": k, "count": v}
            for k, v in keywords.items()
            if k and isinstance(v, (int, float))  # Validate data
        ]
        
        return {
            "success": True,
            "data": keyword_list
        }
        
    except Exception as e:
        print(f"❌ Error in get_keywords: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": "Failed to retrieve keywords",
            "data": []
        }


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
