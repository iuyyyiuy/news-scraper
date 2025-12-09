# Multi-Source Scraper Improvements

## Overview
Improve the multi-source news scraper to ensure reliable scraping from all sources (BlockBeats, Jinse, PANews) with better logging and URL handling.

## Background
- BlockBeats is working fine, no changes needed
- Jinse (金色财经) needs URL pattern fixes
- Logging system needs refinement for better visibility

## Acceptance Criteria

### AC1: Jinse URL Pattern Handling
**Given** the Jinse website uses URL pattern `https://www.jinse.cn/lives/{number}.html`
**When** scraping Jinse news
**Then** the scraper should:
- Extract the latest article ID number from the website
- Backtrack from the latest ID to check older articles
- Check each article for matching keywords
- Stop when reaching the date range limit or article count limit

### AC2: Per-Website Article Count
**Given** user specifies to check 50 news articles
**When** scraping multiple sources
**Then** each website should check 50 articles independently
- BlockBeats: checks 50 articles
- Jinse: checks 50 articles  
- PANews: checks 50 articles

### AC3: "全部" (All) Tab Logging
**Given** user views the "全部" (All) tab in the web interface
**When** scraping is in progress or completed
**Then** the log should only show:
- Successfully matched/scraped news articles
- Important status messages (start, completion, statistics)
- Should NOT show filtered/skipped articles

### AC4: Per-Source Tab Logging
**Given** user views a specific source tab (BlockBeats, Jinse, or PANews)
**When** scraping is in progress or completed
**Then** the log should show ALL logs including:
- Successfully matched articles
- Filtered articles (no keyword match)
- Skipped articles (date out of range)
- All progress and status messages

### AC5: Jinse Scraper Verification
**Given** the Jinse scraper implementation
**When** running the test script `test_jinse_only.py`
**Then** it should:
- Successfully connect to Jinse website
- Extract article IDs correctly
- Match articles with keywords
- Save results to CSV
- Show detailed logs of the process

## Non-Functional Requirements

### NFR1: Performance
- Each source should scrape independently without blocking others
- Request delays should be configurable per source
- Total scraping time should be reasonable (< 5 minutes for 50 articles per source)

### NFR2: Reliability
- Handle network errors gracefully
- Retry failed requests with exponential backoff
- Continue scraping other sources if one fails

### NFR3: Logging Clarity
- Logs should be clear and easy to understand
- Use consistent formatting across all sources
- Include progress indicators (e.g., [1/50], [2/50])

## Out of Scope
- Changes to BlockBeats scraper (already working)
- Changes to PANews scraper (unless similar issues found)
- UI/UX changes beyond logging improvements
- New data sources beyond the existing three

## Success Metrics
- Jinse scraper successfully extracts and processes articles
- "全部" tab shows only matched articles (cleaner view)
- Per-source tabs show complete logs for debugging
- Each source independently checks the specified number of articles
