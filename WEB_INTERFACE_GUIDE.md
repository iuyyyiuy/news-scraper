# News Scraper Web Interface Guide

## Overview

The news scraper now includes a user-friendly web interface that allows non-technical team members to scrape news articles without using code or command line tools.

## Features Implemented

### ✅ Task 13: Session Management
- **Session class** with unique UUID identifiers
- **SessionManager** for thread-safe session handling
- Progress tracking and real-time updates
- Automatic cleanup of old sessions (24-hour retention)
- Support for concurrent scraping sessions

### ✅ Task 14: Web API Endpoints
- **POST /api/scrape** - Start a new scraping session
- **GET /api/status/{session_id}** - Get session status
- **GET /api/status/{session_id}/stream** - Real-time updates via Server-Sent Events
- **GET /api/download/{session_id}** - Download results as CSV
- **GET /api/sessions** - List all sessions
- **DELETE /api/sessions/cleanup** - Clean up old sessions
- **GET /health** - Health check endpoint

### ✅ Task 15: CSV Download Functionality
- UTF-8 encoding with BOM for Excel compatibility
- Proper escaping of quotes, commas, and newlines
- Descriptive filenames with timestamps
- Columns: Publication Date, Title, Body Text, URL, Matched Keywords

### ✅ Task 16: Web Interface HTML and Frontend
- Clean, modern, responsive design
- Date range picker (HTML5 date inputs)
- Keyword input field (comma-separated)
- Real-time progress tracking with spinner
- Article counter updates during scraping
- Download button when complete
- Mobile-responsive layout

## How to Use

### Starting the Web Server

1. Navigate to your project directory
2. Run the web server:
   ```bash
   uvicorn scraper.web_api:app --host 0.0.0.0 --port 5000
   ```

3. Open your browser and go to:
   ```
   http://localhost:5000
   ```

### Using the Web Interface

1. **Enter Date Range**
   - Select start date and end date
   - Default is last 7 days to today

2. **Enter Keywords**
   - Type keywords separated by commas
   - Example: `crypto, bitcoin, blockchain`

3. **Optional: Set Maximum Articles**
   - Leave empty for default (50 articles)
   - Or specify a custom number

4. **Optional: Enter Target URL**
   - Leave empty to use default news source
   - Or provide a specific news website URL

5. **Click "Start Scraping"**
   - Progress will be shown in real-time
   - Article count updates as scraping progresses

6. **Download Results**
   - When complete, click "Download CSV File"
   - File will be saved to your downloads folder
   - Filename format: `news_articles_YYYYMMDD_HHMMSS.csv`

## API Usage Examples

### Start a Scrape

```bash
curl -X POST "http://localhost:5000/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-11-01",
    "end_date": "2025-11-13",
    "keywords": ["crypto", "bitcoin"],
    "max_articles": 50
  }'
```

Response:
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "Scraping session started successfully",
  "status": "running"
}
```

### Check Session Status

```bash
curl "http://localhost:5000/api/status/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

Response:
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "articles_found": 25,
  "articles_scraped": 25,
  "start_time": "2025-11-13T10:30:00",
  "end_time": "2025-11-13T10:32:15",
  "error_message": null,
  "csv_ready": true,
  "duration_seconds": 135.5,
  "start_date": "2025-11-01T00:00:00",
  "end_date": "2025-11-13T23:59:59",
  "keywords": ["crypto", "bitcoin"]
}
```

### Download CSV

```bash
curl "http://localhost:5000/api/download/a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
  -o news_articles.csv
```

## CSV File Format

The downloaded CSV file includes the following columns:

| Column | Description | Format |
|--------|-------------|--------|
| publication_date | When the article was published | YYYY-MM-DD HH:MM:SS |
| title | Article title | Text |
| body_text | Full article content | Text |
| url | Article URL | URL |
| matched_keywords | Keywords found in article | Comma-separated |

## Architecture

```
┌─────────────┐
│  Browser    │
│  (User)     │
└──────┬──────┘
       │ HTTP/SSE
       ▼
┌─────────────┐
│  FastAPI    │
│  Web Server │
└──────┬──────┘
       │
       ├──────────────┬──────────────┐
       ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Session  │   │ Scraper  │   │   CSV    │
│ Manager  │   │Controller│   │Generator │
└──────────┘   └──────────┘   └──────────┘
```

## Security Considerations

- **Default Binding**: Server binds to localhost by default for security
- **Input Validation**: All user inputs are validated on both client and server
- **Session IDs**: Secure UUID v4 identifiers prevent session guessing
- **Rate Limiting**: Configurable delays between requests to avoid overloading servers
- **Error Handling**: Graceful error handling with user-friendly messages

## Configuration

### Default Settings

```python
DEFAULT_CONFIG = {
    "target_url": "https://example.com/news",
    "max_articles": 50,
    "request_delay": 2.0,
    "timeout": 30,
    "max_retries": 3,
    "selectors": {}
}
```

### Session Retention

Sessions are automatically cleaned up after 24 hours. To change this:

```python
session_manager = SessionManager(retention_hours=48)  # 48 hours
```

## Troubleshooting

### Server Won't Start

**Problem**: Port already in use
```
ERROR: [Errno 48] Address already in use
```

**Solution**: Use a different port
```bash
uvicorn scraper.web_api:app --port 8000
```

### No Articles Found

**Problem**: Scraping completes but no articles match criteria

**Solutions**:
- Broaden date range
- Use more general keywords
- Check if target website is accessible
- Verify CSS selectors in configuration

### Download Button Not Appearing

**Problem**: Scraping completes but download button doesn't show

**Possible Causes**:
- Session failed (check error message)
- No articles matched the criteria
- Browser JavaScript disabled

**Solution**: Check session status via API:
```bash
curl "http://localhost:5000/api/status/{session_id}"
```

### Real-Time Updates Not Working

**Problem**: Progress counter doesn't update during scraping

**Solution**: Browser may not support Server-Sent Events. The interface will fall back to polling automatically.

## Testing

Run the test suite to verify everything works:

```bash
python test_web_api.py
```

Expected output:
```
============================================================
Web API Test Suite
============================================================
Testing health check endpoint...
✓ Health check passed

Testing scrape request validation...
✓ Date range validation works
✓ Keywords validation works

...

============================================================
✓ All API tests passed!
============================================================
```

## Next Steps

To complete the web interface implementation, you can:

1. **Task 17**: Implement real-time progress updates (JavaScript EventSource)
2. **Task 18**: Integrate web interface with scraper controller
3. **Task 19**: Create web server startup script
4. **Task 20**: Update documentation

The core functionality is now complete and ready for your teammates to use!
