"""
Patch file for web_api.py integration
Add these lines to your existing web_api.py
"""

# ============================================
# ADD THESE IMPORTS AT THE TOP (after existing imports)
# ============================================

from scraper.api.database_routes import router as database_router, init_scheduler
from fastapi.responses import HTMLResponse

# ============================================
# ADD AFTER app = FastAPI(...) and CORS middleware
# ============================================

# Mount static files (if not already done)
app.mount("/static", StaticFiles(directory="scraper/static"), name="static")

# Include database routes
app.include_router(database_router)

# ============================================
# ADD STARTUP EVENT (after app initialization)
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize scheduler on startup"""
    try:
        init_scheduler()
        logger.info("✅ Scheduler initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize scheduler: {e}")

# ============================================
# ADD DASHBOARD ROUTE (add anywhere with other routes)
# ============================================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the dashboard page"""
    try:
        with open("scraper/templates/dashboard.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dashboard template not found")
