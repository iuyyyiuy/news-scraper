# News Database Feature Design

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Interface                         │
│  ┌──────────────┐  ┌─────────────────────────────────────┐ │
│  │   Sidebar    │  │         Main Content Area           │ │
│  │              │  │  ┌──────────────────────────────┐   │ │
│  │ 📰 Database  │  │  │   News Database Dashboard    │   │ │
│  │ 🔍 Scraper   │  │  │  - Filter by keyword         │   │ │
│  │              │  │  │  - Article list              │   │ │
│  └──────────────┘  │  │  - Article details           │   │ │
│                    │  └──────────────────────────────┘   │ │
│                    │  ┌──────────────────────────────┐   │ │
│                    │  │   Manual Scraper (existing)  │   │ │
│                    │  └──────────────────────────────┘   │ │
│                    └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Flask Backend (web_api.py)              │
│  ┌──────────────────┐  ┌──────────────────────────────┐    │
│  │  API Endpoints   │  │   Scheduler Service          │    │
│  │  - /api/articles │  │   - Daily scraper (8AM)      │    │
│  │  - /api/scrape   │  │   - Monthly cleanup (1st)    │    │
│  │  - /dashboard    │  │                              │    │
│  └──────────────────┘  └──────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer (Supabase)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  articles table                                      │   │
│  │  - id (uuid, primary key)                           │   │
│  │  - title (text)                                     │   │
│  │  - url (text, unique)                               │   │
│  │  - date (timestamp)                                 │   │
│  │  - source (text)                                    │   │
│  │  - content (text)                                   │   │
│  │  - matched_keywords (text[])                        │   │
│  │  - scraped_at (timestamp)                           │   │
│  │  - created_at (timestamp, default now())            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Design

### 1. Database Schema (Supabase)

**Table: articles**
```sql
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    date TIMESTAMP NOT NULL,
    source TEXT NOT NULL,
    content TEXT NOT NULL,
    matched_keywords TEXT[] NOT NULL,
    scraped_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_articles_date ON articles(date DESC);
CREATE INDEX idx_articles_source ON articles(source);
CREATE INDEX idx_articles_keywords ON articles USING GIN(matched_keywords);
```

### 2. Backend Components

#### 2.1 Database Manager (`scraper/core/database_manager.py`)
```python
class DatabaseManager:
    - connect_to_supabase()
    - insert_article(article_data)
    - get_all_articles(limit, offset)
    - get_articles_by_keyword(keyword)
    - delete_old_articles(before_date)
    - check_article_exists(url)
```

#### 2.2 Scheduled Scraper (`scraper/core/scheduled_scraper.py`)
```python
class ScheduledScraper:
    - KEYWORDS = [list of security keywords]
    - scrape_daily()
    - process_and_store_articles()
    - log_scraping_results()
```

#### 2.3 Scheduler Service (`scraper/core/scheduler.py`)
```python
class SchedulerService:
    - schedule_daily_scrape(time="08:00", timezone="Asia/Shanghai")
    - schedule_monthly_cleanup(day=1, time="00:00")
    - start_scheduler()
```

#### 2.4 API Endpoints (additions to `web_api.py`)
```python
# New endpoints
@app.route('/dashboard')
- Render dashboard page

@app.route('/api/articles')
- GET: Fetch articles (with pagination, filtering)
- Query params: keyword, limit, offset

@app.route('/api/articles/<id>')
- GET: Fetch single article details

@app.route('/api/keywords')
- GET: Fetch all keywords with article counts

@app.route('/api/scrape/status')
- GET: Get last scrape status and next scheduled time
```

### 3. Frontend Components

#### 3.1 Navigation Sidebar
```html
<div class="sidebar">
    <div class="nav-item" data-page="database">
        📰 News Database
    </div>
    <div class="nav-item active" data-page="scraper">
        🔍 Scrape News
    </div>
</div>
```

#### 3.2 Dashboard Page (`templates/dashboard.html`)
```html
<div id="dashboard-page">
    <!-- Header Section -->
    <div class="dashboard-header">
        <h2>📰 安全事件数据库</h2>
        <div class="header-stats">
            <span id="article-count">0 条新闻</span>
            <span id="last-update">最后更新: --</span>
        </div>
    </div>
    
    <!-- Filter Section -->
    <div class="filter-section">
        <div class="filter-group">
            <label>关键词筛选:</label>
            <select id="keyword-filter">
                <option value="">全部关键词</option>
                <!-- Populated dynamically -->
            </select>
        </div>
        <div class="filter-group">
            <label>来源:</label>
            <select id="source-filter">
                <option value="">全部来源</option>
                <option value="BlockBeats">BlockBeats</option>
                <option value="Jinse">Jinse</option>
            </select>
        </div>
        <button id="clear-filters" class="btn-secondary">清除筛选</button>
    </div>
    
    <!-- Article Table -->
    <div class="table-container">
        <table id="articles-table" class="articles-table">
            <thead>
                <tr>
                    <th width="10%">日期</th>
                    <th width="15%">来源</th>
                    <th width="50%">标题</th>
                    <th width="15%">关键词</th>
                    <th width="10%">操作</th>
                </tr>
            </thead>
            <tbody id="articles-tbody">
                <!-- Rows populated via JavaScript -->
                <tr class="loading-row">
                    <td colspan="5">加载中...</td>
                </tr>
            </tbody>
        </table>
    </div>
    
    <!-- Pagination -->
    <div class="pagination">
        <button id="prev-page" class="btn-page" disabled>上一页</button>
        <span id="page-info">第 1 页</span>
        <button id="next-page" class="btn-page">下一页</button>
    </div>
    
    <!-- Article Detail Modal -->
    <div id="article-modal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <div class="modal-header">
                <h3 id="modal-title"></h3>
                <div class="modal-meta">
                    <span id="modal-source"></span>
                    <span id="modal-date"></span>
                </div>
            </div>
            <div class="modal-body">
                <div id="modal-keywords" class="keywords-tags"></div>
                <div id="modal-content"></div>
                <a id="modal-link" href="#" target="_blank" class="btn-primary">查看原文</a>
            </div>
        </div>
    </div>
</div>
```

#### 3.3 JavaScript Dashboard Controller
```javascript
class DashboardController {
    - loadArticles(keyword=null, source=null, page=1)
    - renderTableRows(articles)
    - showArticleDetail(articleId)
    - filterByKeyword(keyword)
    - filterBySource(source)
    - clearFilters()
    - setupPagination()
    - formatDate(dateString)
    - truncateTitle(title, maxLength)
    - displayLastUpdateTime()
}
```

#### 3.4 CSS Design System
```css
/* Color Palette */
--primary-color: #2563eb (blue)
--secondary-color: #64748b (slate)
--success-color: #10b981 (green)
--danger-color: #ef4444 (red)
--warning-color: #f59e0b (amber)
--bg-primary: #ffffff
--bg-secondary: #f8fafc
--border-color: #e2e8f0
--text-primary: #1e293b
--text-secondary: #64748b

/* Table Styling */
- Alternating row colors for readability
- Hover effects on rows
- Sticky header on scroll
- Clean borders and spacing
- Responsive column widths

/* Keyword Tags */
- Simple gray tags with consistent styling
- Comma-separated display in table cells
- Badge style in modal view
```

## Data Flow

### Daily Scraping Flow
```
1. Scheduler triggers at 8:00 AM UTC+8
2. ScheduledScraper.scrape_daily() executes
3. For each keyword in KEYWORDS:
   - Scrape BlockBeats with keyword
   - Scrape Jinse with keyword
4. For each article found:
   - Check if URL exists in database
   - If new: insert with matched_keywords
   - If exists: update matched_keywords (append new keyword)
5. Log results to session manager
6. Send notification (optional)
```

### Monthly Cleanup Flow
```
1. Scheduler triggers on 1st at 00:00 UTC+8
2. Calculate cutoff date (first day of current month)
3. DatabaseManager.delete_old_articles(cutoff_date)
4. Log deletion count
```

### Dashboard Loading Flow
```
1. User clicks "📰 News Database"
2. Frontend loads dashboard.html
3. JavaScript calls /api/articles
4. Backend queries Supabase
5. Returns JSON array of articles
6. Frontend renders table rows
7. Display last scrape time (no auto-refresh needed since scraping is once daily)
8. User can manually refresh by clicking browser refresh or re-navigating
```

### Filtering Flow
```
1. User selects keyword from dropdown
2. JavaScript calls /api/articles?keyword=黑客
3. Backend filters by matched_keywords array
4. Returns filtered articles
5. Frontend updates article list and count
```

## Technology Stack

- **Database**: Supabase (PostgreSQL)
- **Backend**: Flask, APScheduler (for scheduling)
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Deployment**: Render (with persistent scheduler)
- **Python Libraries**: 
  - supabase-py (Supabase client)
  - apscheduler (task scheduling)
  - pytz (timezone handling)

## Security Considerations

1. Supabase credentials stored in environment variables
2. API endpoints use rate limiting
3. Input validation for all user inputs
4. SQL injection prevention via parameterized queries
5. CORS configuration for API endpoints

## Performance Optimization

1. Database indexes on frequently queried columns
2. Pagination for article lists (50 per page)
3. Lazy loading for article content
4. Caching for keyword list
5. Connection pooling for Supabase

## Error Handling

1. Failed scraping: Log error, continue with next keyword
2. Database connection failure: Retry with exponential backoff
3. Duplicate articles: Silently skip, log for monitoring
4. Scheduler failure: Alert admin, attempt restart
