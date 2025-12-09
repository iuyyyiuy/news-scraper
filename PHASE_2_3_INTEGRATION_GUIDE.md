# Phase 2 & 3: Flask Integration and Dashboard UI

## Files Created

### Backend API
1. `scraper/api/database_routes.py` - FastAPI routes for database operations

### Frontend
2. `scraper/templates/dashboard.html` - Dashboard page
3. `scraper/static/js/dashboard.js` - Dashboard JavaScript controller

## Integration Steps

### Step 1: Copy Files to ai_code Project

```bash
cd /Users/kabellatsang/PycharmProjects/pythonProject3

# Copy API routes
cp scraper/api/database_routes.py /Users/kabellatsang/PycharmProjects/ai_code/scraper/api/

# Copy dashboard template
cp scraper/templates/dashboard.html /Users/kabellatsang/PycharmProjects/ai_code/scraper/templates/

# Create static/js directory if it doesn't exist
mkdir -p /Users/kabellatsang/PycharmProjects/ai_code/scraper/static/js

# Copy dashboard JavaScript
cp scraper/static/js/dashboard.js /Users/kabellatsang/PycharmProjects/ai_code/scraper/static/js/
```

### Step 2: Update web_api.py

Add these imports at the top of `web_api.py`:

```python
from scraper.api.database_routes import router as database_router, init_scheduler
```

Add this line after creating the FastAPI app (after `app = FastAPI(...)`):

```python
# Include database routes
app.include_router(database_router)

# Initialize scheduler on startup
@app.on_event("startup")
async def startup_event():
    init_scheduler()
```

Add a new route for the dashboard page:

```python
@app.get("/dashboard")
async def dashboard():
    """Serve the dashboard page"""
    from fastapi.responses import HTMLResponse
    with open("scraper/templates/dashboard.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)
```

### Step 3: Update index.html (Add Sidebar Navigation)

Open `scraper/templates/index.html` and add the sidebar. Replace the `<body>` section with:

```html
<body>
    <div class="container">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="sidebar-title">📊 Crypto News</div>
            <div class="nav-item" onclick="window.location.href='/dashboard'">
                📰 安全事件数据库
            </div>
            <div class="nav-item active" onclick="window.location.href='/'">
                🔍 新闻搜索
            </div>
        </div>

        <!-- Main Content (existing content) -->
        <div class="main-content">
            <!-- Your existing scraper interface goes here -->
        </div>
    </div>
</body>
```

Add these styles to the `<style>` section:

```css
.container {
    display: flex;
    min-height: 100vh;
}

.sidebar {
    width: 250px;
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
    padding: 20px;
}

.sidebar-title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 30px;
    color: #2563eb;
}

.nav-item {
    padding: 12px 16px;
    margin-bottom: 8px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 10px;
}

.nav-item:hover {
    background: #f1f5f9;
}

.nav-item.active {
    background: #eff6ff;
    color: #2563eb;
    font-weight: 500;
}

.main-content {
    flex: 1;
    padding: 30px;
    overflow-y: auto;
}
```

### Step 4: Test the Integration

1. Start the web server:
```bash
cd /Users/kabellatsang/PycharmProjects/ai_code
python -m uvicorn scraper.web_api:app --reload --host 0.0.0.0 --port 8000
```

2. Open your browser and test:
   - Dashboard: http://localhost:8000/dashboard
   - Scraper: http://localhost:8000/
   - API: http://localhost:8000/api/database/articles

### Step 5: Test API Endpoints

Test the API endpoints:

```bash
# Get articles
curl http://localhost:8000/api/database/articles

# Get keywords
curl http://localhost:8000/api/database/keywords

# Get stats
curl http://localhost:8000/api/database/stats

# Get scheduler status
curl http://localhost:8000/api/database/scheduler/status

# Trigger manual scrape (for testing)
curl -X POST http://localhost:8000/api/database/scheduler/trigger
```

## Features Implemented

### Dashboard Features
✅ View all stored articles in table format
✅ Filter by keyword
✅ Filter by source (BlockBeats/Jinse)
✅ Pagination (50 articles per page)
✅ Click to view full article details
✅ Modal popup for article content
✅ Last scrape time display
✅ Article count display
✅ Clean, modern UI

### API Endpoints
✅ `GET /api/database/articles` - Get articles with filtering
✅ `GET /api/database/articles/{id}` - Get single article
✅ `GET /api/database/keywords` - Get all keywords with counts
✅ `GET /api/database/stats` - Get database statistics
✅ `GET /api/database/scheduler/status` - Get scheduler status
✅ `POST /api/database/scheduler/trigger` - Manually trigger scrape

### Scheduler
✅ Daily scraping at 8:00 AM UTC+8
✅ Monthly cleanup on 1st at 00:00
✅ Automatic startup with Flask app
✅ Status monitoring

## Troubleshooting

### Issue: "Module 'scraper.api' has no attribute 'database_routes'"
Solution: Make sure you created the `scraper/api/` directory and added `__init__.py`:
```bash
mkdir -p scraper/api
touch scraper/api/__init__.py
```

### Issue: Dashboard shows "加载中..." forever
Solution: Check browser console for errors. Make sure:
1. API endpoints are accessible
2. Database connection is working
3. Static files are being served correctly

### Issue: Scheduler not starting
Solution: Check logs for errors. Make sure:
1. `.env` file is in the correct location
2. Supabase credentials are correct
3. APScheduler is installed

### Issue: "Cannot find module 'dashboard.js'"
Solution: Make sure static files are mounted in web_api.py:
```python
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="scraper/static"), name="static")
```

## Next Steps

After successful integration:

1. ✅ Test dashboard in browser
2. ✅ Test all filters and pagination
3. ✅ Test article detail modal
4. ✅ Verify scheduler is running
5. ✅ Test manual scrape trigger
6. 🚀 Deploy to Render

## Deployment Notes

For Render deployment, make sure to:
1. Add all environment variables (SUPABASE_URL, SUPABASE_KEY)
2. Update requirements.txt with new dependencies
3. Scheduler will start automatically with the app
4. First scrape will run at 8:00 AM UTC+8

## Current Status

✅ **Phase 1 Complete** - Database setup and testing
✅ **Phase 2 Complete** - API endpoints created
✅ **Phase 3 Complete** - Dashboard UI created

⏳ **Next**: Integration testing and deployment
