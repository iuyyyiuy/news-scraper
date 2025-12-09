# News Database Feature Requirements

## Overview
Automated news monitoring system that scrapes security-related crypto news daily and stores them in a database with a dashboard interface for viewing and filtering.

## User Stories

### US-1: Automated Daily Scraping
**As a** user  
**I want** the system to automatically scrape news based on predefined keywords every day  
**So that** I can stay updated on security incidents without manual searches

**Acceptance Criteria:**
- AC-1.1: System scrapes BlockBeats and Jinse at 8:00 AM UTC+8 daily
- AC-1.2: Scraping uses the fixed keywords list for security-related news
- AC-1.3: Scraping runs automatically without user intervention
- AC-1.4: System logs scraping status and results

### US-2: News Storage
**As a** system  
**I want** to store scraped articles in Supabase database  
**So that** articles persist and can be queried efficiently

**Acceptance Criteria:**
- AC-2.1: Articles stored with same structure as CSV export (title, URL, date, source, content)
- AC-2.2: Full article content is stored, not just metadata
- AC-2.3: Duplicate articles are not stored (based on URL)
- AC-2.4: Each article records which keyword(s) matched
- AC-2.5: Articles include timestamp of when they were scraped

### US-3: Monthly Cleanup
**As a** system administrator  
**I want** old articles automatically deleted on the 1st of each month  
**So that** only current month's articles are retained

**Acceptance Criteria:**
- AC-3.1: On 1st of each month at 00:00 UTC+8, delete all articles from previous months
- AC-3.2: Cleanup process logs success/failure
- AC-3.3: Current month's articles are preserved

### US-4: Dashboard Interface
**As a** user  
**I want** a dashboard to view stored articles  
**So that** I can review security incidents that occurred

**Acceptance Criteria:**
- AC-4.1: Dashboard displays all stored articles in reverse chronological order
- AC-4.2: Each article shows: title, source, date, matched keywords
- AC-4.3: Articles are clickable to view full content
- AC-4.4: Dashboard shows total count of articles
- AC-4.5: Dashboard shows last scrape time (no auto-refresh since scraping is once daily)

### US-5: Keyword Filtering
**As a** user  
**I want** to filter articles by keyword  
**So that** I can focus on specific types of security incidents

**Acceptance Criteria:**
- AC-5.1: Filter dropdown shows all keywords that have matched articles
- AC-5.2: Selecting a keyword filters the article list
- AC-5.3: Filter can be cleared to show all articles
- AC-5.4: Filtered count is displayed

### US-6: Navigation Structure
**As a** user  
**I want** separate navigation for database and manual scraping  
**So that** I can easily switch between viewing stored news and searching new keywords

**Acceptance Criteria:**
- AC-6.1: Left sidebar shows two options: "📰 News Database" and "🔍 Scrape News"
- AC-6.2: Clicking "News Database" shows the dashboard page
- AC-6.3: Clicking "Scrape News" shows the existing scraper interface
- AC-6.4: Current page is visually highlighted in navigation

## Fixed Keywords List
```
安全问题, 黑客, 被盗, 漏洞, 攻击, 恶意软件, 盗窃, CoinEx, ViaBTC, 破产, 
执法, 监管, 洗钱, KYC, 合规, 牌照, 风控, 诈骗, 突发, rug pull, 下架
```

## Technical Constraints
- TC-1: Use Supabase for database storage
- TC-2: Maintain compatibility with existing scraper code
- TC-3: Schedule tasks must work on Render deployment platform
- TC-4: Database schema must support CSV export format

## Non-Functional Requirements
- NFR-1: Dashboard should load within 2 seconds
- NFR-2: Automated scraping should complete within 10 minutes
- NFR-3: System should handle at least 1000 articles per month
- NFR-4: Failed scraping attempts should not crash the system
