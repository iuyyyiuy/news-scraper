# News Dashboard Redesign Requirements

## Introduction

This specification defines a complete redesign of the news scraping and dashboard system to eliminate bugs, standardize data formats, and create a reliable automated news collection system with proper monitoring.

## Glossary

- **News_Scraper**: Automated system that collects articles from news sources
- **Dashboard**: Web interface displaying scraped news articles
- **Alert_Log**: System monitoring and execution tracking interface
- **Supabase_Database**: Cloud database storing all news articles
- **BlockBeats**: Primary news source (theblockbeats.info)
- **Jinse**: Secondary news source (jinse.cn)

## Requirements

### Requirement 1: Automated Daily News Scraping

**User Story:** As a system administrator, I want automated daily news scraping at a specific time, so that fresh news content is collected consistently without manual intervention.

#### Acceptance Criteria

1. WHEN the system clock reaches 2:30 PM UTC+8 daily, THE News_Scraper SHALL automatically initiate scraping from both BlockBeats and Jinse sources
2. WHEN scraping begins, THE News_Scraper SHALL first check the latest news ID from each source to determine the starting point
3. WHEN the starting point is determined, THE News_Scraper SHALL scrape backward for exactly 300 articles from each source
4. WHEN scraping is active, THE News_Scraper SHALL process BlockBeats first, then Jinse in sequence
5. WHEN any scraping error occurs, THE News_Scraper SHALL log the error and continue with the next source

### Requirement 2: Intelligent Article Collection Strategy

**User Story:** As a content curator, I want the scraper to collect articles efficiently without duplicates, so that the database contains only new, relevant content.

#### Acceptance Criteria

1. WHEN starting a scraping session, THE News_Scraper SHALL query the database for the most recent article ID from each source
2. WHEN the latest ID is found, THE News_Scraper SHALL begin scraping from that point backward for 300 articles
3. WHEN an article already exists in the database, THE News_Scraper SHALL skip it and continue to the next article
4. WHEN 300 new articles are collected OR no more new articles are found, THE News_Scraper SHALL complete the session for that source
5. WHEN all sources are processed, THE News_Scraper SHALL update the Alert_Log with session statistics

### Requirement 3: Real-time Database Updates

**User Story:** As a news consumer, I want scraped articles to appear immediately in the database, so that I can access the latest news without delay.

#### Acceptance Criteria

1. WHEN an article is successfully parsed, THE News_Scraper SHALL immediately insert it into the Supabase_Database
2. WHEN inserting articles, THE News_Scraper SHALL use standardized source names: "BlockBeats" and "Jinse" only
3. WHEN database insertion fails, THE News_Scraper SHALL retry up to 3 times before logging the failure
4. WHEN an article is stored, THE News_Scraper SHALL ensure all required fields are populated: title, content, date, source, URL
5. WHEN the database is updated, THE News_Scraper SHALL maintain referential integrity and prevent duplicate URLs

### Requirement 4: Consistent Content Extraction

**User Story:** As a data analyst, I want all scraped content to follow the same extraction format, so that data analysis and display are consistent across all sources.

#### Acceptance Criteria

1. WHEN extracting article content, THE News_Scraper SHALL remove all footer elements including "AI 解读", "展开", "原文链接", "举报"
2. WHEN parsing dates, THE News_Scraper SHALL support multiple formats: "YYYY-MM-DD HH:MM", "MM月DD日", and ISO datetime
3. WHEN extracting source information, THE News_Scraper SHALL identify original sources from content patterns like "据 [SOURCE] 监测"
4. WHEN cleaning content, THE News_Scraper SHALL remove duplicate lines and normalize whitespace
5. WHEN content extraction fails, THE News_Scraper SHALL use meta tag fallbacks for title and description

### Requirement 5: Standardized Source Naming

**User Story:** As a dashboard user, I want consistent source names displayed, so that I can easily filter and identify news sources without confusion.

#### Acceptance Criteria

1. WHEN storing articles from theblockbeats.info, THE News_Scraper SHALL always use "BlockBeats" as the source name
2. WHEN storing articles from jinse.cn, THE News_Scraper SHALL always use "Jinse" as the source name
3. WHEN displaying articles in the dashboard, THE Dashboard SHALL show only "BlockBeats" or "Jinse" as source options
4. WHEN filtering by source, THE Dashboard SHALL use exact matches for "BlockBeats" and "Jinse"
5. WHEN existing data contains inconsistent source names, THE News_Scraper SHALL normalize them during the next update

### Requirement 6: Professional Dashboard Interface

**User Story:** As a news reader, I want a clean, professional dashboard interface, so that I can easily browse and read news articles.

#### Acceptance Criteria

1. WHEN loading the dashboard, THE Dashboard SHALL display articles in a clean, card-based layout with consistent formatting
2. WHEN showing article metadata, THE Dashboard SHALL display: standardized source name, publication date, and article title
3. WHEN articles are listed, THE Dashboard SHALL provide pagination with 20 articles per page
4. WHEN filtering options are available, THE Dashboard SHALL include: source filter (BlockBeats/Jinse), date range, and keyword search
5. WHEN displaying content, THE Dashboard SHALL show clean article previews without footer elements or formatting artifacts

### Requirement 7: Comprehensive Alert and Monitoring System

**User Story:** As a system administrator, I want detailed monitoring and alerting, so that I can track system health and quickly identify issues.

#### Acceptance Criteria

1. WHEN any scraping operation occurs, THE Alert_Log SHALL record: timestamp, source, articles found, articles stored, errors encountered
2. WHEN the daily scraping completes, THE Alert_Log SHALL display a summary: total articles processed, success rate, execution time
3. WHEN errors occur, THE Alert_Log SHALL log: error type, affected source, error message, and timestamp
4. WHEN database operations happen, THE Alert_Log SHALL track: connection status, query performance, storage statistics
5. WHEN accessing the alert page, THE Alert_Log SHALL show the last 100 log entries with filtering options by date and severity

### Requirement 8: Robust Error Handling and Recovery

**User Story:** As a system operator, I want the system to handle errors gracefully and continue operating, so that temporary issues don't break the entire news collection process.

#### Acceptance Criteria

1. WHEN network timeouts occur, THE News_Scraper SHALL retry the request up to 3 times with exponential backoff
2. WHEN parsing fails for an article, THE News_Scraper SHALL log the failure and continue with the next article
3. WHEN database connection is lost, THE News_Scraper SHALL attempt to reconnect and queue failed operations for retry
4. WHEN a source is completely unavailable, THE News_Scraper SHALL continue with other sources and log the unavailability
5. WHEN critical errors occur, THE News_Scraper SHALL send notifications to the Alert_Log and continue with remaining operations

### Requirement 9: Data Consistency and Validation

**User Story:** As a data consumer, I want all stored data to be consistent and validated, so that I can rely on the information quality.

#### Acceptance Criteria

1. WHEN storing articles, THE News_Scraper SHALL validate that required fields (title, URL, source) are not empty
2. WHEN processing dates, THE News_Scraper SHALL ensure all dates are stored in consistent YYYY-MM-DD format
3. WHEN handling URLs, THE News_Scraper SHALL ensure all URLs are absolute and properly formatted
4. WHEN storing content, THE News_Scraper SHALL limit article content to reasonable lengths (max 10,000 characters)
5. WHEN duplicate detection runs, THE News_Scraper SHALL use URL as the primary unique identifier

### Requirement 10: Performance and Scalability

**User Story:** As a system user, I want fast loading times and responsive interfaces, so that I can efficiently access news content.

#### Acceptance Criteria

1. WHEN loading the dashboard, THE Dashboard SHALL display the first page of articles within 2 seconds
2. WHEN scraping articles, THE News_Scraper SHALL process at least 10 articles per minute to complete 300 articles efficiently
3. WHEN querying the database, THE Dashboard SHALL use proper indexing to ensure fast search and filter operations
4. WHEN storing large batches of articles, THE News_Scraper SHALL use batch operations to optimize database performance
5. WHEN the system scales, THE News_Scraper SHALL handle up to 1000 articles per day without performance degradation