# Requirements Document

## Introduction

This specification addresses critical issues with the news scraping system where manual updates are failing to find articles from both BlockBeats and Jinse sources, and adds CSV export functionality to allow users to export scraped news data for analysis and backup purposes.

## Glossary

- **News_Scraper_System**: The automated news collection system that gathers articles from multiple cryptocurrency news sources
- **Manual_Update_Function**: The 手动更新 feature that allows users to manually trigger news collection
- **BlockBeats_Source**: The theblockbeats.info news website source
- **Jinse_Source**: The jinse.cn news website source  
- **CSV_Export_Module**: The component responsible for exporting news data to CSV format
- **Article_Parser**: The component that extracts article content from HTML pages
- **Database_Manager**: The component that handles storing and retrieving articles from Supabase

## Requirements

### Requirement 1

**User Story:** As a system administrator, I want the manual update function to successfully scrape articles from news sources, so that I can collect current news data when needed.

#### Acceptance Criteria

1. WHEN the manual update function is triggered THEN the News_Scraper_System SHALL successfully find and parse articles from BlockBeats_Source
2. WHEN the manual update function processes BlockBeats_Source THEN the Article_Parser SHALL correctly extract article titles, content, dates, and URLs
3. WHEN the manual update function processes Jinse_Source THEN the Article_Parser SHALL correctly extract article titles, content, dates, and URLs
4. WHEN articles are found by the scrapers THEN the Database_Manager SHALL store them in the database with proper metadata
5. WHEN the scraping process encounters parsing errors THEN the News_Scraper_System SHALL log detailed error information and continue processing

### Requirement 2

**User Story:** As a data analyst, I want to export scraped news articles to CSV format, so that I can analyze the data in external tools and create backups.

#### Acceptance Criteria

1. WHEN a user requests CSV export THEN the CSV_Export_Module SHALL generate a file containing all articles with publication date, title, content, source, and keywords
2. WHEN generating CSV export THEN the CSV_Export_Module SHALL properly escape special characters and handle multi-line content
3. WHEN CSV export is requested with date filters THEN the CSV_Export_Module SHALL only include articles within the specified date range
4. WHEN CSV export is requested with source filters THEN the CSV_Export_Module SHALL only include articles from the specified sources
5. WHEN CSV export completes THEN the News_Scraper_System SHALL provide a download link or file path to the user

### Requirement 3

**User Story:** As a system administrator, I want detailed debugging information when scraping fails, so that I can identify and fix the root causes of scraping issues.

#### Acceptance Criteria

1. WHEN article parsing fails THEN the Article_Parser SHALL log the HTML content structure and parsing selectors used
2. WHEN HTTP requests fail THEN the News_Scraper_System SHALL log response status codes, headers, and error details
3. WHEN no articles are found THEN the News_Scraper_System SHALL log the search parameters, date ranges, and website response status
4. WHEN keyword filtering removes articles THEN the News_Scraper_System SHALL log which keywords were tested and why articles were filtered
5. WHEN scraping sessions complete THEN the News_Scraper_System SHALL generate comprehensive session reports with success rates and failure analysis

### Requirement 4

**User Story:** As a system user, I want the scraping system to handle website changes gracefully, so that news collection continues working even when source websites update their structure.

#### Acceptance Criteria

1. WHEN website HTML structure changes THEN the Article_Parser SHALL attempt multiple parsing strategies before failing
2. WHEN primary parsing selectors fail THEN the Article_Parser SHALL use fallback selectors to extract content
3. WHEN article URLs change format THEN the News_Scraper_System SHALL detect and adapt to new URL patterns
4. WHEN websites implement anti-scraping measures THEN the News_Scraper_System SHALL use appropriate delays and headers to avoid blocking
5. WHEN parsing completely fails THEN the News_Scraper_System SHALL store raw HTML for manual analysis and continue with other articles