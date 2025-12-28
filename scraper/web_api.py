"""
Web API - Dashboard Integration
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, timedelta
import asyncio
import json
import logging

# Import database routes
from scraper.api.database_routes import router as database_router
from scraper.api.monitoring_routes import router as monitoring_router
from scraper.api.csv_routes import router as csv_router
# Temporarily disable AI trading to avoid SQLite errors
# from scraper.api.trading_strategy_routes import router as trading_strategy_router
# from scraper.api.ai_trading_routes import router as ai_trading_router

# Import ML integration routes
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml_orderbook_analyzer'))
    from ml_orderbook_analyzer.ml_integration_api import router as ml_analysis_router
    ML_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  ML integration not available: {e}")
    ML_AVAILABLE = False

# Import scraper components
from scraper.core import SessionManager, Session, SessionStatus, Config
from scraper.core.storage import CSVDataStore

# Set up logging
logger = logging.getLogger(__name__)

# Global session manager
session_manager = SessionManager(retention_hours=24)

# Configuration for scraper
DEFAULT_CONFIG = {
    "target_url": "https://www.theblockbeats.info/newsflash",
    "max_articles": 500,
    "request_delay": 2.0,
    "timeout": 30,
    "max_retries": 3,
    "selectors": {}
}

# Pydantic models for API
class ScrapeRequestModel(BaseModel):
    """Request model for starting a scrape."""
    days_filter: int = Field(..., description="Number of days to look back", ge=1, le=90)
    keywords: List[str] = Field(..., description="Keywords to filter articles")
    max_articles: Optional[int] = Field(None, description="Maximum number of articles to scrape per source")
    sources: List[str] = Field(default=['blockbeats'], description="News sources to scrape from")
    enable_deduplication: bool = Field(default=True, description="Enable deduplication across sources")
    
    @validator('keywords')
    def validate_keywords(cls, v):
        if not v:
            raise ValueError('At least one keyword is required')
        return [kw.strip() for kw in v if kw.strip()]
    
    @validator('sources')
    def validate_sources(cls, v):
        if not v:
            raise ValueError('At least one source is required')
        valid_sources = ['blockbeats', 'jinse']
        for source in v:
            if source.lower() not in valid_sources:
                raise ValueError(f'Invalid source: {source}')
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

# Create FastAPI app
app = FastAPI(title="News Database Dashboard")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include database API routes
app.include_router(database_router)

# Include monitoring API routes
app.include_router(monitoring_router)

# Include CSV export API routes
app.include_router(csv_router)

# Temporarily disable AI trading routes to avoid SQLite errors
# Include trading strategy analysis API routes
# app.include_router(trading_strategy_router)

# Include AI trading system API routes
# app.include_router(ai_trading_router)

# Include ML analysis API routes (if available)
if ML_AVAILABLE:
    app.include_router(ml_analysis_router)

# Serve static files
app.mount("/static", StaticFiles(directory="scraper/static"), name="static")

# Background task for scraping
def run_scraper_task(
    session_id: str,
    days_filter: int,
    keywords: List[str],
    max_articles: Optional[int],
    sources: List[str],
    enable_deduplication: bool
):
    """Background task to run the multi-source scraper."""
    try:
        from scraper.core.multi_source_scraper import MultiSourceScraper
        
        logger.info(f"Starting multi-source scraper task for session {session_id}")
        
        # Calculate date range
        end_date_obj = datetime.now().date()
        start_date_obj = end_date_obj - timedelta(days=days_filter)
        
        # Create config
        config = Config(
            target_url="",
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
        
        # Progress callback
        def progress_callback(source: str, articles_found: int, articles_scraped: int):
            session_manager.update_progress(
                session_id,
                articles_found=articles_found,
                articles_scraped=articles_scraped
            )
        
        # Log callback
        global_counter = {'count': 0}
        
        def log_callback(message: str, log_type: str = 'info', source: str = None, show_in_all: bool = True):
            if '✅ 已保存:' in message or '✅ ID' in message:
                global_counter['count'] += 1
                if show_in_all:
                    import re
                    message = re.sub(r'\[\d+\]\s*ID \d+\.\.\.\s*', '', message)
            session_manager.add_log(session_id, message, log_type, source=source, show_in_all=show_in_all)
        
        # Log start
        log_callback("🚀 开始多源爬取...", "info")
        log_callback(f"📅 日期范围: {start_date_obj} 到 {end_date_obj}", "info")
        log_callback(f"🔑 关键词: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}", "info")
        
        # Create scraper
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
        
        # Add articles to session
        session = session_manager.get_session(session_id)
        if session:
            for article in data_store.get_all_articles():
                session_manager.add_article(session_id, article)
        
        # Complete session
        session_manager.complete_session(session_id, result)
        
        logger.info(f"Scraper task completed for session {session_id}")
        
    except Exception as e:
        logger.error(f"Scraper task failed for session {session_id}: {str(e)}", exc_info=True)
        session_manager.fail_session(session_id, str(e))

# Serve dashboard HTML
@app.get("/")
async def index():
    """Serve the news scraper interface"""
    response = FileResponse("scraper/templates/index.html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/dashboard")
async def dashboard():
    response = FileResponse("scraper/templates/dashboard.html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/monitoring")
async def monitoring():
    response = FileResponse("scraper/templates/monitoring.html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/ml-analysis")
async def ml_analysis():
    """Serve the ML analysis interface"""
    if not ML_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML analysis not available")
    
    response = FileResponse("scraper/templates/ml_analysis.html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/trading-strategy")
async def trading_strategy():
    """Serve the trading strategy analysis interface - DISABLED"""
    raise HTTPException(status_code=503, detail="Trading strategy analysis temporarily disabled")

@app.get("/ai-trading")
async def ai_trading():
    """Serve the AI trading system interface - DISABLED"""
    raise HTTPException(status_code=503, detail="AI trading system temporarily disabled")

@app.post("/api/scrape", response_model=ScrapeResponseModel)
async def start_scrape(
    request: ScrapeRequestModel,
    background_tasks: BackgroundTasks
):
    """Start a new scraping session."""
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.days_filter)
        
        # Create session
        session_id = session_manager.create_session(
            start_date=start_date,
            end_date=end_date,
            keywords=request.keywords
        )
        
        logger.info(f"Created session {session_id}")
        
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
    """Get the status of a scraping session."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionStatusModel(**session.to_dict())

@app.get("/api/status/{session_id}/stream")
async def stream_session_status(session_id: str):
    """Stream real-time updates for a scraping session using Server-Sent Events."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    async def event_generator():
        try:
            # Send initial status
            session_data = session.to_dict()
            yield f"data: {json.dumps(session_data)}\n\n"
            
            # Keep streaming while session is running
            while session.status == SessionStatus.RUNNING:
                await asyncio.sleep(1)
                
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
    """Download scraped articles as CSV file."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status != SessionStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Session is not completed yet")
    
    if not session.csv_ready:
        raise HTTPException(status_code=400, detail="No articles available for download")
    
    # Generate CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"news_articles_{timestamp}.csv"
    filepath = f"temp_session_{session_id}.csv"
    
    try:
        csv_store = CSVDataStore(filepath)
        for article in session.articles:
            csv_store.save_article(article)
        
        return FileResponse(
            filepath,
            media_type="text/csv",
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Failed to generate CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate CSV: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    import os
    from scraper.core.database_manager import DatabaseManager
    
    health_status = {
        "status": "ok",
        "env_vars": {
            "SUPABASE_URL": "set" if os.getenv('SUPABASE_URL') else "missing",
            "SUPABASE_KEY": "set" if os.getenv('SUPABASE_KEY') else "missing"
        },
        "database": "unknown"
    }
    
    try:
        db = DatabaseManager()
        if db.supabase:
            count = db.get_total_count()
            health_status["database"] = f"connected ({count} articles)"
        else:
            health_status["database"] = "connection failed"
            health_status["status"] = "error"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "error"
    
    return health_status

@app.post("/api/trigger-scrape")
async def trigger_scrape_now(background_tasks: BackgroundTasks):
    """Manually trigger the scheduled scraper (for testing)"""
    try:
        from scraper.core.scheduled_scraper import ScheduledScraper
        
        def run_scrape():
            scraper = ScheduledScraper()
            result = scraper.scrape_daily()
            logger.info(f"Manual scrape completed: {result}")
        
        background_tasks.add_task(run_scrape)
        
        return {
            "success": True,
            "message": "Scrape triggered successfully. Check logs for progress."
        }
    except Exception as e:
        logger.error(f"Failed to trigger scrape: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trigger-scrape")
async def trigger_manual_scrape():
    """Manually trigger the scheduled scraper (for testing)"""
    try:
        from scraper.core.scheduled_scraper import ScheduledScraper
        import threading
        
        def run_scrape():
            scraper = ScheduledScraper()
            scraper.scrape_daily()
        
        # Run in background thread
        thread = threading.Thread(target=run_scrape)
        thread.start()
        
        return {"success": True, "message": "Scrape triggered successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/trigger-scrape")
async def trigger_manual_scrape(background_tasks: BackgroundTasks):
    """Manually trigger the scheduled scraper (for testing)"""
    try:
        from scraper.core.scheduled_scraper import ScheduledScraper
        
        def run_scrape():
            scraper = ScheduledScraper()
            result = scraper.scrape_daily()
            logger.info(f"Manual scrape completed: {result}")
        
        background_tasks.add_task(run_scrape)
        
        return {
            "success": True,
            "message": "Scrape triggered successfully. Check logs for progress."
        }
    except Exception as e:
        logger.error(f"Failed to trigger scrape: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/manual-update")
async def 手动更新(background_tasks: BackgroundTasks, request: dict = None):
    """
    手动更新 - Manual news update with configurable parameters
    
    Parameters:
    - max_articles: Number of articles to scrape per source (default: 1000)
    
    Process:
    1. First scrape BlockBeats (check latest news ID, scrape backward N articles)
    2. Then scrape Jinse (check latest news ID, scrape backward N articles)  
    3. Use AI to filter duplicates/similar/unrelated news
    4. Real-time update to Supabase database
    5. Extract same content as CSV scraper results
    """
    try:
        from scraper.core.manual_scraper import ManualScraper
        from fastapi import Request, Body
        
        # Get max_articles from request body, default to 1000
        max_articles = 1000  # Default value
        if request:
            max_articles = request.get('max_articles', 1000)
        
        def run_manual_update():
            scraper = ManualScraper()
            result = scraper.手动更新(max_articles=max_articles)
            logger.info(f"手动更新 completed: {result}")
        
        background_tasks.add_task(run_manual_update)
        
        return {
            "success": True,
            "message": f"手动更新已启动 - 每个源抓取{max_articles}篇文章",
            "parameters": {
                "date_range": "最近7天",
                "keywords_count": 21,
                "max_articles_per_source": max_articles,
                "sources": ["BlockBeats", "Jinse"]
            },
            "process": [
                f"1. 抓取 BlockBeats (检查最新新闻ID，向后抓取{max_articles}篇文章)",
                f"2. 抓取 Jinse (检查最新新闻ID，向后抓取{max_articles}篇文章)", 
                "3. 使用21个安全相关关键词过滤",
                "4. AI过滤重复/相似/无关新闻",
                "5. 实时更新到 Supabase 数据库"
            ]
        }
    except Exception as e:
        logger.error(f"Failed to start 手动更新: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/manual-update/status")
async def get_manual_update_status():
    """Get status of manual update process"""
    return {
        "status": "ready",
        "message": "手动更新功能已就绪 - 固定参数配置",
        "parameters": {
            "date_range": "最近1天",
            "keywords_count": 21,
            "max_articles_per_source": 100,
            "sources": ["BlockBeats", "Jinse"]
        },
        "keywords": [
            "安全问题", "黑客", "被盗", "漏洞", "攻击", "恶意软件", "盗窃",
            "CoinEx", "ViaBTC", "破产", "执法", "监管", "洗钱", "KYC",
            "合规", "牌照", "风控", "诈骗", "突发", "rug pull", "下架"
        ],
        "features": [
            "顺序处理 BlockBeats 和 Jinse",
            "使用21个安全相关关键词", 
            "AI智能过滤重复和无关新闻", 
            "实时更新到 Supabase 数据库",
            "提取与CSV相同的新闻内容"
        ]
    }
