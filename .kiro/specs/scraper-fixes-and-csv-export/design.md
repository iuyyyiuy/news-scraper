# Design Document

## Overview

This design addresses critical failures in the news scraping system where manual updates return 0 articles from both BlockBeats and Jinse sources, and implements a comprehensive CSV export feature. The solution focuses on improving parser robustness, enhancing error handling, and providing flexible data export capabilities.

## Architecture

The system follows a modular architecture with enhanced error handling and debugging capabilities:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   Manual Update │    │   CSV Export    │
│                 │    │   Controller    │    │   Module        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────────┐
         │            Enhanced Scraper Core                    │
         └─────────────────────────────────────────────────────┘
                                 │
    ┌────────────────┬───────────┼───────────┬────────────────┐
    │                │           │           │                │
┌───▼───┐    ┌──────▼──┐    ┌───▼───┐   ┌──▼──┐    ┌───────▼───┐
│Parser │    │HTTP     │    │Debug  │   │AI   │    │Database   │
│Engine │    │Client   │    │Logger │   │Filter│   │Manager    │
└───────┘    └─────────┘    └───────┘   └─────┘    └───────────┘
```

## Components and Interfaces

### Enhanced Parser Engine
- **Multi-Strategy Parser**: Implements cascading parsing strategies with fallback mechanisms
- **Content Extractor**: Specialized extractors for different content types (meta tags, structured data, text blocks)
- **Selector Manager**: Dynamic selector management with automatic fallback chains

### Improved HTTP Client
- **Adaptive Request Handler**: Implements intelligent retry logic with exponential backoff
- **Anti-Scraping Countermeasures**: User-agent rotation, request delays, header management
- **Response Analyzer**: Analyzes response patterns to detect blocking or structure changes

### Debug Logger
- **Structured Logging**: Comprehensive logging with contextual information
- **HTML Capture**: Stores raw HTML for failed parsing attempts
- **Performance Metrics**: Tracks parsing success rates and performance indicators

### CSV Export Module
- **Flexible Query Engine**: Supports date range, source, and keyword filtering
- **Format Handler**: Proper CSV escaping and multi-line content handling
- **File Manager**: Secure file generation and download management

## Data Models

### Enhanced Article Model
```python
@dataclass
class Article:
    url: str
    title: str
    publication_date: Optional[datetime]
    author: Optional[str]
    body_text: str
    scraped_at: datetime
    source_website: str
    matched_keywords: List[str] = field(default_factory=list)
    parsing_metadata: Dict[str, Any] = field(default_factory=dict)
    raw_html: Optional[str] = None  # For debugging failed parses
```

### CSV Export Configuration
```python
@dataclass
class CSVExportConfig:
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    sources: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    include_content: bool = True
    max_records: Optional[int] = None
```

### Debug Session
```python
@dataclass
class DebugSession:
    session_id: str
    start_time: datetime
    source: str
    articles_attempted: int
    articles_successful: int
    parsing_failures: List[Dict[str, Any]]
    http_errors: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After reviewing all identified properties, several can be consolidated:
- Properties 1.2 and 1.3 (parsing for different sources) can be combined into a single comprehensive parsing property
- Properties 3.1, 3.2, 3.3, 3.4 can be consolidated into a comprehensive logging property
- Properties 4.1 and 4.2 (parsing strategies and fallbacks) can be combined into a resilience property

### Core Parsing Properties

**Property 1: Successful Article Discovery**
*For any* manual update operation, the scraper should find at least one article when the source websites are accessible and contain recent content
**Validates: Requirements 1.1**

**Property 2: Complete Article Extraction**
*For any* accessible article URL from supported sources, the parser should successfully extract title, content, and URL, with optional date and author fields
**Validates: Requirements 1.2, 1.3**

**Property 3: Reliable Data Storage**
*For any* successfully parsed article, the database manager should store it with all extracted metadata and return a success confirmation
**Validates: Requirements 1.4**

**Property 4: Graceful Error Handling**
*For any* parsing error encountered during scraping, the system should log detailed error information and continue processing remaining articles
**Validates: Requirements 1.5**

### CSV Export Properties

**Property 5: Complete CSV Generation**
*For any* CSV export request, the generated file should contain all requested articles with publication_date, title, content, source, and keywords columns
**Validates: Requirements 2.1**

**Property 6: Proper CSV Formatting**
*For any* article content containing special characters or multi-line text, the CSV export should properly escape and format the content according to RFC 4180
**Validates: Requirements 2.2**

**Property 7: Accurate Date Filtering**
*For any* CSV export request with date filters, only articles with publication dates within the specified range should be included in the output
**Validates: Requirements 2.3**

**Property 8: Correct Source Filtering**
*For any* CSV export request with source filters, only articles from the specified sources should be included in the output
**Validates: Requirements 2.4**

**Property 9: Export Completion Notification**
*For any* completed CSV export operation, the system should provide the user with a valid file path or download link to access the generated CSV
**Validates: Requirements 2.5**

### Debugging and Resilience Properties

**Property 10: Comprehensive Error Logging**
*For any* failed operation (parsing, HTTP, filtering), the system should log sufficient detail including context, parameters, and error specifics to enable debugging
**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

**Property 11: Session Reporting**
*For any* completed scraping session, the system should generate a comprehensive report including success rates, failure analysis, and performance metrics
**Validates: Requirements 3.5**

**Property 12: Parser Resilience**
*For any* article with non-standard HTML structure, the parser should attempt multiple extraction strategies before failing, using fallback selectors and methods
**Validates: Requirements 4.1, 4.2**

**Property 13: URL Pattern Adaptation**
*For any* article URL that doesn't match expected patterns, the system should attempt to extract content using flexible URL handling and pattern detection
**Validates: Requirements 4.3**

**Property 14: Anti-Scraping Compliance**
*For any* scraping operation, the system should implement appropriate delays, headers, and request patterns to minimize the risk of being blocked
**Validates: Requirements 4.4**

**Property 15: Failure Recovery**
*For any* complete parsing failure, the system should store the raw HTML for analysis and continue processing other articles without terminating the session
**Validates: Requirements 4.5**

## Error Handling

### Parsing Error Recovery
- **Multi-Level Fallbacks**: Primary selectors → Common selectors → Meta tags → Text analysis
- **Content Validation**: Verify extracted content meets minimum quality thresholds
- **Raw HTML Preservation**: Store failed parsing attempts for manual analysis

### HTTP Error Management
- **Intelligent Retries**: Exponential backoff with jitter for temporary failures
- **Status Code Handling**: Specific handling for 404, 403, 429, and 5xx errors
- **Circuit Breaker**: Temporary suspension of requests when consistent failures occur

### Data Integrity
- **Duplicate Detection**: Enhanced duplicate checking using content similarity
- **Validation Pipeline**: Multi-stage validation of extracted article data
- **Rollback Capability**: Ability to rollback failed batch operations

## Testing Strategy

### Unit Testing
- Parser component testing with various HTML structures
- CSV export functionality with edge cases (special characters, large datasets)
- Error handling scenarios with simulated failures
- Database operations with transaction testing

### Property-Based Testing
The system will use **Hypothesis** for Python property-based testing with a minimum of 100 iterations per property test.

Each property-based test will be tagged with comments referencing the design document:
- Format: `# Feature: scraper-fixes-and-csv-export, Property X: [property description]`

**Property Test Examples:**
- Generate random article HTML structures and verify parsing resilience
- Generate random CSV export configurations and verify output correctness
- Generate random error scenarios and verify logging completeness
- Generate random article datasets and verify filtering accuracy

### Integration Testing
- End-to-end manual update workflows
- CSV export with real database data
- Error recovery scenarios with actual website responses
- Performance testing with large article datasets

### Debugging and Monitoring
- Real-time parsing success rate monitoring
- Automated alerts for parsing failure spikes
- HTML structure change detection
- Performance regression detection