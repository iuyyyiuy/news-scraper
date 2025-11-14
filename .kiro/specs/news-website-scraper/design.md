# News Website Scraper - Design Document

## Overview

The News Website Scraper is a Python-based system that extracts article data from news websites. It uses HTTP requests to retrieve web pages, parses HTML content to extract structured data, and stores the results in a persistent format. The system is designed to be configurable, resilient to errors, and respectful of website resources through rate limiting.

## Architecture

The system follows a modular architecture with clear separation of concerns:

```
┌─────────────┐         ┌─────────────┐
│   CLI/Main  │         │  Web Server │
└──────┬──────┘         └──────┬──────┘
       │                       │
       │                       ▼
       │                ┌─────────────┐
       │                │  Web API    │
       │                │  Endpoints  │
       │                └──────┬──────┘
       │                       │
       └───────────┬───────────┘
                   ▼
            ┌─────────────┐
            │   Scraper   │
            │  Controller │
            └──────┬──────┘
                   │
       ├───────────┼──────────────┬──────────────┐
       ▼           ▼              ▼              ▼
┌──────────┐ ┌──────────┐   ┌──────────┐   ┌──────────┐
│  HTTP    │ │  HTML    │   │  Data    │   │  Config  │
│  Client  │ │  Parser  │   │  Store   │   │  Manager │
└──────────┘ └──────────┘   └──────────┘   └──────────┘
```

### Design Principles

- **Modularity**: Each component has a single responsibility
- **Configurability**: Key parameters are externalized
- **Resilience**: Graceful error handling and retry logic
- **Respectful scraping**: Rate limiting and user-agent headers
- **Extensibility**: Easy to add support for different news sites

## Components and Interfaces

### 1. Scraper Controller

The main orchestrator that coordinates the scraping process.

**Responsibilities:**
- Initialize and configure components
- Manage scraping workflow
- Track progress and report status
- Handle high-level error recovery

**Key Methods:**
- `scrape(url: str, max_articles: int) -> ScrapingResult`
- `get_progress() -> ProgressInfo`

### 2. HTTP Client

Handles all network communication with target websites.

**Responsibilities:**
- Make HTTP GET requests
- Handle timeouts and retries
- Respect rate limiting
- Set appropriate headers (User-Agent, etc.)

**Key Methods:**
- `fetch(url: str) -> Response`
- `fetch_with_retry(url: str, max_retries: int) -> Response`

**Configuration:**
- Request timeout: 30 seconds
- Max retries: 3
- Delay between requests: configurable (default 2 seconds)
- User-Agent: identifies the scraper appropriately

### 3. HTML Parser

Extracts structured data from HTML content.

**Responsibilities:**
- Parse HTML using BeautifulSoup4
- Extract article metadata (title, date, author)
- Extract article body text
- Handle different HTML structures

**Key Methods:**
- `parse_article_list(html: str) -> List[str]` - Extract article URLs from listing page
- `parse_article(html: str) -> Article` - Extract article data from article page
- `extract_text(element) -> str` - Clean and extract text content

**Extraction Strategy:**
- Use CSS selectors for common article elements
- Support configurable selectors for different sites
- Fall back to heuristics when selectors fail
- Clean extracted text (remove extra whitespace, scripts, etc.)

### 4. Data Store

Persists scraped article data.

**Responsibilities:**
- Save articles to storage
- Check for duplicate articles
- Provide data retrieval interface
- Support multiple output formats

**Key Methods:**
- `save_article(article: Article) -> bool`
- `article_exists(url: str) -> bool`
- `get_all_articles() -> List[Article]`
- `export(format: str, path: str) -> None`

**Storage Options:**
- JSON file (default)
- CSV file
- SQLite database (for larger datasets)

### 5. Config Manager

Manages configuration and settings.

**Responsibilities:**
- Load configuration from file or environment
- Provide default values
- Validate configuration parameters

**Configuration Parameters:**
- `target_url`: The news website URL to scrape
- `max_articles`: Maximum number of articles to scrape
- `request_delay`: Delay between requests in seconds
- `output_format`: Format for saved data (json, csv, sqlite)
- `output_path`: Path to save scraped data
- `selectors`: CSS selectors for article elements

### 6. Web Server

Provides a web-based user interface for non-technical users.

**Responsibilities:**
- Serve HTML/CSS/JavaScript files for the web interface
- Handle HTTP requests from the browser
- Provide REST API endpoints for scraping operations
- Manage scraping sessions initiated from the web interface
- Stream progress updates to the browser in real-time

**Key Endpoints:**
- `GET /` - Serve the main web interface HTML page
- `POST /api/scrape` - Start a new scraping session with parameters
- `GET /api/status/{session_id}` - Get current status of a scraping session
- `GET /api/download/{session_id}` - Download results as CSV file
- `GET /api/sessions` - List recent scraping sessions

**Technology Stack:**
- Flask or FastAPI for the web framework
- Server-Sent Events (SSE) or WebSockets for real-time progress updates
- Static file serving for HTML/CSS/JavaScript

### 7. Web API Layer

Handles API requests from the web interface and coordinates with the scraper controller.

**Responsibilities:**
- Validate incoming request parameters
- Create and manage scraping sessions
- Track session state (running, completed, failed)
- Generate CSV files from scraped data
- Provide session results and metadata

**Key Methods:**
- `start_scraping(start_date, end_date, keywords) -> session_id`
- `get_session_status(session_id) -> SessionStatus`
- `generate_csv(session_id) -> file_path`
- `cleanup_old_sessions()` - Remove old session data

**Session Management:**
- Each scraping session gets a unique ID
- Session data stored temporarily (configurable retention period)
- Support for concurrent sessions from multiple users

## Data Models

### Article

Represents a scraped news article.

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
```

### ScrapingResult

Represents the outcome of a scraping session.

```python
@dataclass
class ScrapingResult:
    total_articles_found: int
    articles_scraped: int
    articles_failed: int
    duration_seconds: float
    errors: List[str]
```

### Config

Represents scraper configuration.

```python
@dataclass
class Config:
    target_url: str
    max_articles: int = 10
    request_delay: float = 2.0
    output_format: str = "json"
    output_path: str = "scraped_articles.json"
    timeout: int = 30
    max_retries: int = 3
    selectors: Dict[str, str] = field(default_factory=dict)
```

### ScrapeRequest

Represents a scraping request from the web interface.

```python
@dataclass
class ScrapeRequest:
    start_date: date
    end_date: date
    keywords: List[str]
    max_articles: Optional[int] = None
```

### SessionStatus

Represents the current status of a scraping session.

```python
@dataclass
class SessionStatus:
    session_id: str
    status: str  # "running", "completed", "failed"
    articles_found: int
    articles_scraped: int
    start_time: datetime
    end_time: Optional[datetime]
    error_message: Optional[str]
    csv_ready: bool
```

## Error Handling

### Error Categories

1. **Network Errors**
   - Connection failures
   - Timeouts
   - HTTP errors (404, 500, etc.)
   - **Handling**: Retry with exponential backoff, log error, skip article if retries exhausted

2. **Parsing Errors**
   - Invalid HTML
   - Missing expected elements
   - Malformed data
   - **Handling**: Log error with context, skip article, continue processing

3. **Storage Errors**
   - File write failures
   - Database connection issues
   - **Handling**: Log error, attempt to save to fallback location, fail gracefully

4. **Configuration Errors**
   - Invalid parameters
   - Missing required config
   - **Handling**: Validate at startup, provide clear error messages, use defaults where appropriate

### Logging Strategy

- Use Python's logging module
- Log levels:
  - INFO: Progress updates, successful operations
  - WARNING: Recoverable errors, fallback actions
  - ERROR: Failed operations, skipped articles
  - DEBUG: Detailed execution information
- Log format: timestamp, level, component, message
- Output to both console and file

## Testing Strategy

### Unit Tests

- Test each component in isolation
- Mock external dependencies (HTTP requests, file I/O)
- Focus on:
  - HTML parsing with various structures
  - Error handling logic
  - Data validation
  - Configuration loading

### Integration Tests

- Test component interactions
- Use test fixtures with sample HTML
- Verify end-to-end data flow
- Test with mock HTTP server

### Manual Testing

- Test against real news websites
- Verify data quality
- Check rate limiting behavior
- Monitor resource usage

## Implementation Considerations

### Rate Limiting

- Implement configurable delay between requests
- Consider using exponential backoff for retries
- Respect robots.txt (optional enhancement)

### Scalability

- Initial implementation: single-threaded, sequential processing
- Future enhancement: concurrent requests with thread pool
- Consider memory usage for large scraping sessions

### Maintainability

- Use type hints throughout
- Document CSS selectors and their purpose
- Provide example configurations for common news sites
- Include clear error messages with troubleshooting hints

### Legal and Ethical Considerations

- Include User-Agent header identifying the scraper
- Respect rate limits to avoid overloading servers
- Document that users should check website terms of service
- Consider adding robots.txt checking

## Web Interface Design

### User Interface Layout

The web interface will be a single-page application with a clean, intuitive design:

**Main Form Section:**
- Date range picker with start and end date inputs (HTML5 date inputs)
- Text input for keywords (comma-separated or space-separated)
- Submit button to start scraping
- Clear visual feedback for validation errors

**Progress Section:**
- Initially hidden, shown when scraping starts
- Progress spinner or animated indicator
- Real-time counter showing articles found
- Status messages (e.g., "Scraping in progress...", "Completed!")

**Results Section:**
- Shown after scraping completes
- Summary statistics (total articles, time taken)
- Download button for CSV file
- Option to start a new search

**Styling:**
- Clean, modern design with good contrast
- Mobile-responsive layout
- Clear visual hierarchy
- Accessible form labels and ARIA attributes

### Real-Time Updates

Use Server-Sent Events (SSE) for pushing progress updates from server to browser:

1. Client initiates scraping via POST request
2. Server returns session_id
3. Client opens SSE connection to `/api/status/{session_id}/stream`
4. Server pushes updates as JSON events
5. Client updates UI in real-time
6. Connection closes when scraping completes

### CSV Generation

When user clicks download:
1. Browser sends GET request to `/api/download/{session_id}`
2. Server generates CSV with proper headers
3. Response includes `Content-Disposition: attachment` header
4. Browser automatically downloads file with name like `news_articles_2025-11-13_143022.csv`

CSV Format:
- Columns: Title, Publication Date, URL, Author, Body Text, Scraped At
- UTF-8 encoding with BOM for Excel compatibility
- Proper escaping of quotes and commas
- Date format: YYYY-MM-DD HH:MM:SS

## Dependencies

- **requests**: HTTP client library
- **beautifulsoup4**: HTML parsing
- **lxml**: Fast HTML parser for BeautifulSoup
- **python-dateutil**: Date parsing
- **typing**: Type hints (built-in for Python 3.5+)
- **flask** or **fastapi**: Web framework for the API and web interface
- **uvicorn**: ASGI server (if using FastAPI)
- **jinja2**: Template engine for HTML rendering

## Security Considerations

### Web Interface Security

- **Input Validation**: Validate all user inputs (dates, keywords) on both client and server side
- **Rate Limiting**: Limit number of scraping sessions per IP address to prevent abuse
- **Session Management**: Use secure session IDs (UUID v4) that are hard to guess
- **File Access**: Ensure users can only download their own session results
- **CORS**: Configure appropriate CORS headers if needed
- **XSS Prevention**: Sanitize any user input displayed in the UI

### Deployment Considerations

- Run on localhost by default for security
- Provide option to bind to specific network interface
- Consider adding basic authentication for team deployment
- Use HTTPS in production environments

## Future Enhancements

- Support for JavaScript-rendered content (Selenium/Playwright)
- Multi-site scraping with site-specific adapters
- Article deduplication using content similarity
- Automatic selector discovery
- Distributed scraping with task queue
- User authentication and multi-user support
- Saved search templates
- Email notifications when scraping completes
- Scheduled/recurring scrapes
