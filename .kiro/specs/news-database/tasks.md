# News Database Feature - Implementation Tasks

## Phase 1: Database Setup

### Task 1.1: Supabase Project Setup
**Depends on**: None  
**Estimated effort**: 30 minutes

**Steps**:
1. Create Supabase account/project
2. Get API URL and anon key
3. Add credentials to environment variables
4. Test connection from Python

**Deliverables**:
- Supabase project created
- Environment variables configured
- Connection test script

### Task 1.2: Create Database Schema
**Depends on**: Task 1.1  
**Estimated effort**: 20 minutes

**Steps**:
1. Create `articles` table with schema from design.md
2. Add indexes for performance
3. Set up RLS (Row Level Security) policies if needed
4. Test table creation

**Deliverables**:
- `articles` table created
- Indexes applied
- Schema documentation

### Task 1.3: Implement Database Manager
**Depends on**: Task 1.2  
**Estimated effort**: 2 hours

**Steps**:
1. Create `scraper/core/database_manager.py`
2. Implement DatabaseManager class with methods:
   - `connect_to_supabase()`
   - `insert_article()`
   - `get_all_articles()`
   - `get_articles_by_keyword()`
   - `delete_old_articles()`
   - `check_article_exists()`
3. Add error handling and logging
4. Write unit tests

**Deliverables**:
- `database_manager.py` file
- All methods implemented
- Unit tests passing

## Phase 2: Scheduled Scraping

### Task 2.1: Create Scheduled Scraper
**Depends on**: Task 1.3  
**Estimated effort**: 2 hours

**Steps**:
1. Create `scraper/core/scheduled_scraper.py`
2. Define KEYWORDS constant
3. Implement `scrape_daily()` method
4. Implement `process_and_store_articles()` method
5. Add deduplication logic
6. Add logging integration

**Deliverables**:
- `scheduled_scraper.py` file
- Scraping logic implemented
- Integration with database_manager

### Task 2.2: Implement Scheduler Service
**Depends on**: Task 2.1  
**Estimated effort**: 1.5 hours

**Steps**:
1. Create `scraper/core/scheduler.py`
2. Install APScheduler library
3. Implement daily scrape scheduling (8:00 AM UTC+8)
4. Implement monthly cleanup scheduling (1st at 00:00)
5. Add scheduler start/stop methods
6. Handle timezone correctly (Asia/Shanghai)

**Deliverables**:
- `scheduler.py` file
- APScheduler configured
- Timezone handling correct

### Task 2.3: Integrate Scheduler with Flask App
**Depends on**: Task 2.2  
**Estimated effort**: 1 hour

**Steps**:
1. Update `web_api.py` to start scheduler on app startup
2. Add graceful shutdown handling
3. Add scheduler status endpoint
4. Test scheduler in development mode

**Deliverables**:
- Scheduler starts with Flask app
- Status endpoint working
- Development testing complete

## Phase 3: Backend API

### Task 3.1: Create Dashboard API Endpoints
**Depends on**: Task 1.3  
**Estimated effort**: 2 hours

**Steps**:
1. Add `/api/articles` endpoint (GET with pagination)
2. Add `/api/articles/<id>` endpoint (GET single article)
3. Add `/api/keywords` endpoint (GET keyword list with counts)
4. Add `/api/scrape/status` endpoint (GET scheduler status)
5. Add error handling and validation
6. Test all endpoints with Postman/curl

**Deliverables**:
- 4 new API endpoints
- Request/response validation
- API documentation

### Task 3.2: Create Dashboard Page Route
**Depends on**: Task 3.1  
**Estimated effort**: 30 minutes

**Steps**:
1. Add `/dashboard` route to `web_api.py`
2. Create template rendering
3. Pass initial data to template
4. Test route accessibility

**Deliverables**:
- `/dashboard` route working
- Template rendering functional

## Phase 4: Frontend Development

### Task 4.1: Create Dashboard HTML Template
**Depends on**: Task 3.2  
**Estimated effort**: 2 hours

**Steps**:
1. Create `templates/dashboard.html`
2. Add sidebar navigation structure
3. Add filter section
4. Add article list container
5. Add article detail modal
6. Add loading states and empty states

**Deliverables**:
- `dashboard.html` file
- Complete HTML structure
- Responsive layout

### Task 4.2: Implement Dashboard CSS
**Depends on**: Task 4.1  
**Estimated effort**: 1.5 hours

**Steps**:
1. Create/update `static/css/dashboard.css`
2. Style sidebar navigation
3. Style article cards
4. Style filter section
5. Style modal
6. Add responsive breakpoints
7. Match existing scraper page styling

**Deliverables**:
- Dashboard styling complete
- Responsive design working
- Consistent with existing UI

### Task 4.3: Implement Dashboard JavaScript
**Depends on**: Task 4.2  
**Estimated effort**: 3 hours

**Steps**:
1. Create `static/js/dashboard.js`
2. Implement DashboardController class
3. Implement article loading with pagination
4. Implement keyword filtering
5. Implement article detail modal
6. Add auto-refresh (60 seconds)
7. Add error handling and loading states

**Deliverables**:
- `dashboard.js` file
- All interactive features working
- Error handling implemented

### Task 4.4: Update Navigation
**Depends on**: Task 4.3  
**Estimated effort**: 1 hour

**Steps**:
1. Update `templates/index.html` to add sidebar
2. Add navigation JavaScript for page switching
3. Highlight active page
4. Test navigation between pages
5. Ensure existing scraper functionality unchanged

**Deliverables**:
- Sidebar navigation working
- Page switching functional
- Existing features intact

## Phase 5: Testing & Deployment

### Task 5.1: Integration Testing
**Depends on**: Task 4.4  
**Estimated effort**: 2 hours

**Steps**:
1. Test complete scraping flow
2. Test database storage and retrieval
3. Test filtering functionality
4. Test scheduler execution
5. Test monthly cleanup (manually trigger)
6. Test error scenarios

**Deliverables**:
- All features tested
- Bug list created
- Test documentation

### Task 5.2: Fix Bugs and Optimize
**Depends on**: Task 5.1  
**Estimated effort**: 2 hours

**Steps**:
1. Fix identified bugs
2. Optimize database queries
3. Optimize frontend performance
4. Add missing error handling
5. Retest all features

**Deliverables**:
- All bugs fixed
- Performance optimized
- Retesting complete

### Task 5.3: Deployment Configuration
**Depends on**: Task 5.2  
**Estimated effort**: 1 hour

**Steps**:
1. Update `requirements.txt` with new dependencies
2. Add Supabase credentials to Render environment
3. Configure scheduler for production
4. Update deployment scripts
5. Test on Render platform

**Deliverables**:
- Dependencies updated
- Environment configured
- Deployment scripts updated

### Task 5.4: Documentation
**Depends on**: Task 5.3  
**Estimated effort**: 1 hour

**Steps**:
1. Create user guide for dashboard
2. Document API endpoints
3. Document scheduler configuration
4. Update README.md
5. Create troubleshooting guide

**Deliverables**:
- Complete documentation
- User guide
- API documentation

## Phase 6: Monitoring & Maintenance

### Task 6.1: Add Monitoring
**Depends on**: Task 5.4  
**Estimated effort**: 1 hour

**Steps**:
1. Add logging for scheduler tasks
2. Add metrics for scraping success/failure
3. Add database health checks
4. Create monitoring dashboard (optional)

**Deliverables**:
- Logging implemented
- Metrics tracked
- Health checks working

## Summary

**Total Estimated Effort**: ~24 hours

**Critical Path**:
1. Database Setup (Phase 1)
2. Scheduled Scraping (Phase 2)
3. Backend API (Phase 3)
4. Frontend Development (Phase 4)
5. Testing & Deployment (Phase 5)

**Dependencies**:
- Supabase account
- APScheduler library
- Render deployment platform
- Existing scraper codebase
