# News Dashboard Redesign - Design Document

## Overview

This design document outlines a complete redesign of the news scraping and dashboard system to eliminate existing bugs, standardize data formats, and create a robust, maintainable system. The new architecture focuses on reliability, consistency, and proper error handling.

## Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Scheduler     │    │  News Scraper   │    │   Dashboard     │
│   (Cron Job)    │───▶│   (Core Logic)  │───▶│  (Web Interface)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Supabase Database│    │   Alert Log     │
                       │  (Articles)     │    │  (Monitoring)   │
                       └─────────────────┘    └─────────────────┘
```

### Data Flow

1. **Scheduler** triggers daily at 2:30 PM UTC+8
2. **News Scraper** queries database for latest article IDs
3. **News Scraper** scrapes 300 articles from each source (BlockBeats, Jinse)
4. **Content Processor** cleans and standardizes article content
5. **Database Manager** stores articles with consistent formatting
6. **Alert Logger** records all operations and errors
7. **Dashboard** displays articles with real-time updates

## Components and Interfaces

### 1. Enhanced Scheduler (`scheduler.py`)

**Purpose**: Reliable daily scheduling with timezone handling

**Key Features**:
- UTC+8 timezone support
- Robust error handling
- Execution logging
- Manual trigger capability

**Interface**:
```python
class EnhancedScheduler:
    def schedule_daily_scraping(self, hour: int, minute: int, timezone: str)
    def trigger_manual_scraping(self) -> Dict[str, Any]
    def get_next_execution_time(self) -> datetime
    def is_running(self) -> bool
```

### 2. Unified News Scraper (`unified_scraper.py`)

**Purpose**: Single, reliable scraper for all news sources

**Key Features**:
- Source-agnostic scraping logic
- Intelligent starting point detection
- Standardized content extraction
- Comprehensive error handling

**Interface**:
```python
class UnifiedNewsScraper:
    def scrape_source(self, source: str, max_articles: int = 300) -> ScrapingResult
    def get_latest_article_id(self, source: str) -> Optional[str]
    def extract_article_content(self, html: str, source: str) -> Article
    def normalize_source_name(self, raw_source: str) -> str
```

### 3. Content Processor (`content_processor.py`)

**Purpose**: Consistent content cleaning and standardization

**Key Features**:
- Footer removal (AI 解读, 展开, etc.)
- Date format normalization
- Source name standardization
- Content validation

**Interface**:
```python
class ContentProcessor:
    def clean_article_content(self, content: str) -> str
    def normalize_date(self, date_str: str) -> str
    def extract_source_info(self, content: str) -> Optional[str]
    def validate_article_data(self, article: Dict) -> bool
```

### 4. Enhanced Database Manager (`enhanced_db_manager.py`)

**Purpose**: Reliable database operations with proper error handling

**Key Features**:
- Connection pooling
- Retry logic
- Batch operations
- Data validation

**Interface**:
```python
class EnhancedDatabaseManager:
    def insert_article_batch(self, articles: List[Dict]) -> BatchResult
    def get_latest_article_id(self, source: str) -> Optional[str]
    def normalize_existing_sources(self) -> int
    def get_articles_paginated(self, page: int, per_page: int, filters: Dict) -> PaginatedResult
```

### 5. Alert Logger (`alert_logger.py`)

**Purpose**: Comprehensive system monitoring and logging

**Key Features**:
- Structured logging
- Performance metrics
- Error tracking
- Web interface for logs

**Interface**:
```python
class AlertLogger:
    def log_scraping_session(self, session_data: Dict) -> None
    def log_error(self, error: Exception, context: Dict) -> None
    def get_recent_logs(self, limit: int = 100) -> List[Dict]
    def get_system_health(self) -> Dict[str, Any]
```

### 6. Redesigned Dashboard (`dashboard_v2.py`)

**Purpose**: Clean, professional web interface

**Key Features**:
- Responsive design
- Real-time updates
- Advanced filtering
- Performance optimization

**Interface**:
```python
class DashboardV2:
    def render_articles_page(self, filters: Dict) -> str
    def get_article_stats(self) -> Dict[str, int]
    def render_alert_log_page(self) -> str
    def handle_real_time_updates(self) -> None
```

## Data Models

### Enhanced Article Model

```python
@dataclass
class EnhancedArticle:
    id: str
    title: str
    content: str
    publication_date: datetime
    source: Literal["BlockBeats", "Jinse"]  # Standardized names only
    url: str
    scraped_at: datetime
    content_hash: str  # For duplicate detection
    metadata: Dict[str, Any]  # Additional source-specific data
```

### Alert Log Entry Model

```python
@dataclass
class AlertLogEntry:
    id: str
    timestamp: datetime
    level: Literal["INFO", "WARNING", "ERROR", "CRITICAL"]
    component: str
    message: str
    details: Dict[str, Any]
    session_id: Optional[str]
```

### Scraping Session Model

```python
@dataclass
class ScrapingSession:
    id: str
    start_time: datetime
    end_time: Optional[datetime]
    sources_processed: List[str]
    articles_found: int
    articles_stored: int
    errors_encountered: int
    performance_metrics: Dict[str, float]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Scheduled Execution Consistency
*For any* valid date and time configuration, when the scheduler reaches 2:30 PM UTC+8, it should trigger scraping from both BlockBeats and Jinse sources
**Validates: Requirements 1.1**

### Property 2: Latest ID Query Behavior
*For any* scraping session, the scraper should query the database for the most recent article ID before beginning to scrape
**Validates: Requirements 1.2, 2.1**

### Property 3: Article Count Consistency
*For any* valid starting point, the scraper should attempt to collect exactly 300 articles from each source
**Validates: Requirements 1.3, 2.2**

### Property 4: Immediate Database Insertion
*For any* successfully parsed article, the scraper should immediately insert it into the database
**Validates: Requirements 3.1**

### Property 5: Source Name Standardization
*For any* article being stored, the source name should be exactly "BlockBeats" or "Jinse" regardless of the original source URL format
**Validates: Requirements 3.2, 5.1, 5.2**

### Property 6: Content Cleaning Consistency
*For any* article content containing footer elements like "AI 解读", "展开", "原文链接", these elements should be completely removed from the final stored content
**Validates: Requirements 4.1**

### Property 7: Date Format Normalization
*For any* date string in supported formats ("YYYY-MM-DD HH:MM", "MM月DD日", ISO datetime), the parser should successfully convert it to a consistent format
**Validates: Requirements 4.2, 9.2**

### Property 8: Dashboard Metadata Display
*For any* article displayed in the dashboard, it should show standardized source name, publication date, and article title
**Validates: Requirements 6.2**

### Property 9: Alert Logging Completeness
*For any* scraping operation, the alert log should record timestamp, source, articles found, articles stored, and any errors encountered
**Validates: Requirements 7.1**

### Property 10: Session Summary Generation
*For any* completed daily scraping session, the alert log should display a summary with total articles processed, success rate, and execution time
**Validates: Requirements 7.2**

### Property 11: Network Retry Behavior
*For any* network timeout during scraping, the system should retry the request up to 3 times with exponential backoff
**Validates: Requirements 8.1**

### Property 12: Parsing Error Recovery
*For any* article that fails to parse, the scraper should log the failure and continue processing the next article
**Validates: Requirements 8.2**

### Property 13: Required Field Validation
*For any* article being stored, the system should validate that title, URL, and source fields are not empty
**Validates: Requirements 9.1**

### Property 14: Dashboard Performance
*For any* normal system load, the dashboard should display the first page of articles within 2 seconds
**Validates: Requirements 10.1**

### Property 15: Scraping Performance
*For any* scraping session, the system should process at least 10 articles per minute to efficiently handle 300 articles
**Validates: Requirements 10.2**

## Error Handling

### Error Categories and Responses

1. **Network Errors**
   - Timeout: Retry with exponential backoff (1s, 2s, 4s)
   - Connection refused: Log error, continue with next source
   - DNS resolution: Log error, skip source for this session

2. **Parsing Errors**
   - Malformed HTML: Log error, continue with next article
   - Missing required fields: Log validation error, skip article
   - Invalid date format: Use current date, log warning

3. **Database Errors**
   - Connection lost: Attempt reconnection, queue operations
   - Constraint violation: Log duplicate, continue processing
   - Transaction timeout: Retry operation, reduce batch size

4. **System Errors**
   - Memory exhaustion: Reduce batch size, log critical error
   - Disk space low: Log critical error, continue with reduced logging
   - Permission denied: Log critical error, attempt fallback operations

## Testing Strategy

### Unit Testing Approach

Unit tests will focus on individual component functionality:
- Content cleaning and normalization functions
- Date parsing with various input formats
- Source name standardization logic
- Database connection and retry mechanisms
- Error handling for specific failure scenarios

### Property-Based Testing Approach

Property-based tests will verify universal behaviors using **Hypothesis** for Python:
- Generate random article content and verify cleaning consistency
- Test date parsing with various valid date formats
- Verify source name normalization across different URL patterns
- Test retry logic with simulated network failures
- Validate database operations with various article data structures

**Configuration**: Each property-based test will run a minimum of 100 iterations to ensure comprehensive coverage of the input space.

**Test Tagging**: Each property-based test will include a comment with the format:
`# Feature: news-dashboard-redesign, Property X: [property description]`

### Integration Testing

Integration tests will verify component interactions:
- End-to-end scraping workflow from trigger to database storage
- Dashboard data retrieval and display accuracy
- Alert logging across multiple system components
- Error propagation and recovery across component boundaries

### Performance Testing

Performance tests will validate system efficiency:
- Dashboard page load times under various data volumes
- Scraping throughput with different network conditions
- Database query performance with large article datasets
- Memory usage during batch processing operations

## Implementation Priority

### Phase 1: Core Infrastructure (Week 1)
1. Enhanced Database Manager with proper error handling
2. Content Processor with standardized cleaning
3. Alert Logger with structured logging
4. Basic unit tests for core functions

### Phase 2: Scraping Engine (Week 2)
1. Unified News Scraper with source abstraction
2. Enhanced Scheduler with timezone support
3. Integration tests for scraping workflow
4. Property-based tests for content processing

### Phase 3: Dashboard Redesign (Week 3)
1. Clean dashboard interface with consistent formatting
2. Real-time updates and filtering
3. Alert log viewing interface
4. Performance optimization and caching

### Phase 4: Monitoring and Optimization (Week 4)
1. Comprehensive error monitoring
2. Performance metrics collection
3. System health dashboard
4. Final integration testing and deployment

## Security Considerations

- **Input Validation**: All scraped content will be sanitized before storage
- **SQL Injection Prevention**: Use parameterized queries for all database operations
- **Rate Limiting**: Implement respectful scraping delays to avoid overwhelming source sites
- **Error Information**: Ensure error logs don't expose sensitive system information
- **Access Control**: Secure dashboard and alert interfaces with proper authentication

## Deployment Strategy

- **Database Migration**: Script to normalize existing source names in current data
- **Gradual Rollout**: Deploy components incrementally with fallback to current system
- **Monitoring**: Enhanced logging during initial deployment to catch issues early
- **Rollback Plan**: Maintain current system as backup during transition period