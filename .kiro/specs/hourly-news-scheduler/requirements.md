# Hourly News Scheduler Dashboard Requirements

## Introduction

Enhance the news scraper dashboard to support and monitor hourly automated scraping that checks BlockBeats and Jinse every hour, with real-time status updates and comprehensive monitoring capabilities.

## Glossary

- **Dashboard_Interface**: The web-based monitoring interface for the news scraper system
- **Scheduler_Status**: Real-time information about the automated scraping schedule and current state
- **Hourly_Cycle**: A single automated scraping operation that processes both BlockBeats and Jinse
- **Source_Processing_Order**: The sequential order in which news sources are processed (BlockBeats first, then Jinse)
- **Real_Time_Updates**: Live updates to the dashboard showing current scraping progress and results

## Requirements

### Requirement 1

**User Story:** As a dashboard user, I want to see the hourly scheduler status and controls, so that I can monitor and manage the automated scraping process.

#### Acceptance Criteria

1. WHEN I access the dashboard THEN the Dashboard_Interface SHALL display the current scheduler status (running/stopped)
2. WHEN the scheduler is running THEN the Dashboard_Interface SHALL show the next scheduled run time
3. WHEN I want to start hourly scheduling THEN the Dashboard_Interface SHALL provide a button to enable hourly scraping
4. WHEN I want to stop hourly scheduling THEN the Dashboard_Interface SHALL provide a button to disable hourly scraping
5. WHEN the scheduler status changes THEN the Dashboard_Interface SHALL update the display in real-time

### Requirement 2

**User Story:** As a dashboard user, I want to see the sequential processing order and progress, so that I can monitor which source is currently being processed.

#### Acceptance Criteria

1. WHEN an Hourly_Cycle starts THEN the Dashboard_Interface SHALL display "Processing BlockBeats" status first
2. WHEN BlockBeats processing completes THEN the Dashboard_Interface SHALL display "Processing Jinse" status
3. WHEN both sources complete THEN the Dashboard_Interface SHALL display "Cycle Complete" status
4. WHEN a source is being processed THEN the Dashboard_Interface SHALL show progress indicators for that source
5. WHEN an error occurs THEN the Dashboard_Interface SHALL display error status while continuing to next source

### Requirement 3

**User Story:** As a dashboard user, I want to see the scraping progress and article counts, so that I can monitor how many articles are being processed from each source.

#### Acceptance Criteria

1. WHEN BlockBeats processing starts THEN the Dashboard_Interface SHALL display the latest news ID found
2. WHEN Jinse processing starts THEN the Dashboard_Interface SHALL display the latest news ID found
3. WHEN articles are being checked THEN the Dashboard_Interface SHALL show progress counter (e.g., "50/200 articles checked")
4. WHEN articles are found and saved THEN the Dashboard_Interface SHALL increment the "articles saved" counter
5. WHEN 200 articles have been checked THEN the Dashboard_Interface SHALL show "Complete" status for that source

### Requirement 4

**User Story:** As a dashboard user, I want to see AI filtering results and duplicate detection statistics, so that I can understand the quality of articles being processed.

#### Acceptance Criteria

1. WHEN articles are being processed THEN the Dashboard_Interface SHALL display duplicate detection counts
2. WHEN AI analysis is running THEN the Dashboard_Interface SHALL show "AI Analysis" status indicator
3. WHEN AI filters out articles THEN the Dashboard_Interface SHALL increment the "filtered by AI" counter
4. WHEN AI analysis completes THEN the Dashboard_Interface SHALL show relevance scores and filtering statistics
5. WHEN AI analysis fails THEN the Dashboard_Interface SHALL display "Using keyword filtering" fallback status

### Requirement 5

**User Story:** As a dashboard user, I want to see real-time database updates and connection status, so that I can monitor the health of the data storage process.

#### Acceptance Criteria

1. WHEN articles are saved to database THEN the Dashboard_Interface SHALL show Real_Time_Updates of saved article counts
2. WHEN database operations succeed THEN the Dashboard_Interface SHALL display green status indicators
3. WHEN database operations fail THEN the Dashboard_Interface SHALL display red error indicators with retry status
4. WHEN database connection is lost THEN the Dashboard_Interface SHALL show connection error warnings
5. WHEN all processing completes THEN the Dashboard_Interface SHALL display the updated last scrape timestamp

### Requirement 6

**User Story:** As a dashboard user, I want to see comprehensive logs and performance metrics, so that I can track the hourly scraping performance and troubleshoot any issues.

#### Acceptance Criteria

1. WHEN each Hourly_Cycle starts THEN the Dashboard_Interface SHALL display the cycle start time and sources being processed
2. WHEN each source completes THEN the Dashboard_Interface SHALL show summary statistics (found, stored, filtered counts)
3. WHEN errors occur THEN the Dashboard_Interface SHALL display error messages with timestamps in a dedicated error log section
4. WHEN a cycle completes THEN the Dashboard_Interface SHALL show total cycle duration and performance metrics
5. WHEN I request historical data THEN the Dashboard_Interface SHALL provide access to previous cycle logs and statistics