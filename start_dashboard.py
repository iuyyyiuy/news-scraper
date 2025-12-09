#!/usr/bin/env python3
"""
Start Dashboard Web Server
Simple server to view the news database dashboard
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

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

# Serve static files with cache control
from fastapi import Response
from starlette.staticfiles import StaticFiles as StarletteStaticFiles

class NoCacheStaticFiles(StarletteStaticFiles):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def __call__(self, scope, receive, send):
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                headers[b"cache-control"] = b"no-cache, no-store, must-revalidate"
                headers[b"pragma"] = b"no-cache"
                headers[b"expires"] = b"0"
                message["headers"] = [(k, v) for k, v in headers.items()]
            await send(message)
        
        await super().__call__(scope, receive, send_wrapper)

app.mount("/static", NoCacheStaticFiles(directory="scraper/static"), name="static")

# Serve dashboard HTML
@app.get("/")
async def index():
    # Redirect to the deployed scraper interface
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="https://crypto-news-scraper.onrender.com/")

@app.get("/dashboard")
async def dashboard():
    from fastapi.responses import FileResponse
    response = FileResponse("scraper/templates/dashboard.html")
    # Prevent caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/test-api")
async def test_api():
    from fastapi.responses import FileResponse
    return FileResponse("scraper/templates/test_api.html")

@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify environment and database connection"""
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

if __name__ == "__main__":
    print("="*60)
    print("🚀 Starting News Database Dashboard")
    print("="*60)
    print()
    print("📊 Dashboard: http://localhost:8080/dashboard")
    print("🔌 API: http://localhost:8080/api/database/articles")
    print()
    print("Press Ctrl+C to stop")
    print("="*60)
    print()
    
    uvicorn.run(app, host="127.0.0.1", port=8080)
