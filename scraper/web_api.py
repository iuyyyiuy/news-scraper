"""
Web API - Dashboard Integration
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

# Import database routes
from scraper.api.database_routes import router as database_router

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

# Serve static files
app.mount("/static", StaticFiles(directory="scraper/static"), name="static")

# Serve dashboard HTML
@app.get("/")
async def index():
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard")
async def dashboard():
    response = FileResponse("scraper/templates/dashboard.html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

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

@app.on_event("startup")
async def startup_event():
    """Start the scheduler when the app starts"""
    try:
        from scraper.core.scheduler import SchedulerService
        scheduler = SchedulerService()
        scheduler.start_scheduler()
        print("✅ Scheduler started successfully")
    except Exception as e:
        print(f"⚠️  Scheduler failed to start: {e}")
