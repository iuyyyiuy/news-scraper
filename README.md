# News Website Scraper

A Python-based web scraper for extracting articles from news websites with both a **user-friendly web interface** and command-line interface. Perfect for teams who need to collect news data without coding.

## 🌟 Features

### Web Interface (NEW!)
- 🖥️ **User-Friendly Web Interface**: No coding required - just open your browser!
- 📅 **Date Range Selection**: Pick start and end dates with visual date pickers
- 🔑 **Keyword Filtering**: Search for articles containing specific keywords
- 📊 **Real-Time Progress**: Watch articles being scraped in real-time
- 💾 **One-Click CSV Download**: Download results instantly in Excel-compatible format
- 📱 **Mobile Responsive**: Works on desktop, tablet, and mobile devices

### Core Features
- 🔍 **Intelligent Article Extraction**: Automatically detects and extracts article URLs from listing pages
- 📝 **Comprehensive Data Capture**: Extracts title, publication date, author, and body text
- 🎯 **CSS Selector Support**: Configure custom selectors for different website structures
- 🔄 **Retry Logic**: Exponential backoff retry mechanism for failed requests
- ⏱️ **Rate Limiting**: Configurable delays between requests to respect server resources
- 🚫 **Duplicate Detection**: Prevents scraping the same article multiple times
- 📊 **Multiple Export Formats**: Save results as JSON or CSV
- 📋 **Detailed Logging**: Comprehensive logging with configurable levels
- ⌨️ **CLI Interface**: Powerful command-line interface for advanced users

## Installation

### Requirements

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

### Option 1: Web Interface (Recommended for Non-Technical Users)

**Perfect for teammates who don't code!**

1. **Start the web server:**
   ```bash
   python run_web_server.py
   ```

2. **Open your browser:**
   ```
   http://localhost:5000
   ```

3. **Use the interface:**
   - Select date range (e.g., last 7 days)
   - Enter keywords (e.g., "crypto, bitcoin")
   - Click "Start Scraping"
   - Watch progress in real-time
   - Download CSV when complete

**That's it!** No coding required. Share the URL with your team.

---

## 🖥️ Web Interface Guide

### Starting the Server

```bash
# Default (localhost:5000)
python run_web_server.py

# Custom port
python run_web_server.py --port 8000

# Allow network access (for team use)
python run_web_server.py --host 0.0.0.0 --port 5000

# Development mode with auto-reload
python run_web_server.py --reload
```

### Server Options

| Option | Description | Default |
|--------|-------------|---------|
| `--host` | Host to bind to | 127.0.0.1 (localhost only) |
| `--port` | Port number | 5000 |
| `--reload` | Auto-reload on file changes | False |
| `--log-level` | Logging level | INFO |
| `--workers` | Number of worker processes | 1 |

### Using the Web Interface

1. **Date Range**
   - Click on start date field
   - Select your start date
   - Click on end date field
   - Select your end date
   - Default is last 7 days

2. **Keywords**
   - Enter keywords separated by commas
   - Example: `crypto, bitcoin, blockchain`
   - At least one keyword is required
   - Articles must contain at least one keyword

3. **Optional Settings**
   - **Target URL**: Leave empty for default, or enter specific news site
   - **Max Articles**: Leave empty for default (50), or set custom limit

4. **Start Scraping**
   - Click "Start Scraping" button
   - Progress section appears with spinner
   - Article count updates in real-time
   - Status messages show current state

5. **Download Results**
   - When complete, "Download CSV File" button appears
   - Click to download
   - File saved to your Downloads folder
   - Filename includes date and time

### CSV File Format

Downloaded CSV files include:

| Column | Description |
|--------|-------------|
| publication_date | When article was published (YYYY-MM-DD HH:MM:SS) |
| title | Article headline |
| body_text | Full article content |
| url | Article URL |
| matched_keywords | Keywords found in the article |

**Excel Compatible**: Files use UTF-8 with BOM encoding for perfect Excel compatibility.

### API Endpoints

The web server also provides a REST API:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/api/scrape` | POST | Start scraping session |
| `/api/status/{session_id}` | GET | Get session status |
| `/api/status/{session_id}/stream` | GET | Real-time updates (SSE) |
| `/api/download/{session_id}` | GET | Download CSV |
| `/api/sessions` | GET | List all sessions |
| `/health` | GET | Health check |
| `/docs` | GET | API documentation |

### Troubleshooting

**Port Already in Use**
```bash
# Use a different port
python run_web_server.py --port 8000
```

**Can't Access from Another Computer**
```bash
# Allow network access
python run_web_server.py --host 0.0.0.0
```

**No Articles Found**
- Broaden your date range
- Use more general keywords
- Check if website is accessible
- Verify target URL is correct

**Download Button Not Appearing**
- Check if scraping completed successfully
- Look for error messages in results
- Verify at least one article matched criteria

---

### Option 2: Command Line Interface (For Developers)

#### Basic Usage

Scrape articles from a news website:

```bash
python -m scraper.main --url https://example.com/news --max-articles 10
```

#### Using a Configuration File

Create a configuration file (see `example_config.json`) and run:

```bash
python -m scraper.main --config example_config.json
```

#### Export to CSV

```bash
python -m scraper.main --url https://example.com/news --output articles.csv --output-format csv
```

## Configuration

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--url` | Target URL to scrape | Required (unless using --config) |
| `--config` | Path to JSON configuration file | None |
| `--max-articles` | Maximum number of articles to scrape | 10 |
| `--output` | Output file path | scraped_articles.json |
| `--output-format` | Output format (json or csv) | json |
| `--delay` | Delay between requests in seconds | 2.0 |
| `--timeout` | Request timeout in seconds | 30 |
| `--retries` | Maximum number of retry attempts | 3 |
| `--log-level` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO |
| `--log-file` | Path to log file | None (console only) |
| `--quiet` | Suppress console output | False |

### Configuration File Format

Create a JSON file with the following structure:

```json
{
  "target_url": "https://example.com/news",
  "max_articles": 10,
  "request_delay": 2.0,
  "output_format": "json",
  "output_path": "scraped_articles.json",
  "timeout": 30,
  "max_retries": 3,
  "selectors": {
    "article_links": "a.article-link",
    "title": "h1.article-title",
    "date": "time.published-date",
    "author": ".author-name",
    "body": ".article-content"
  }
}
```

### CSS Selectors

The scraper uses CSS selectors to locate elements on the page. If selectors are not provided, the scraper will use intelligent fallback logic to detect common patterns.

#### Selector Configuration

- **article_links**: Selector for article links on listing pages
- **title**: Selector for article title
- **date**: Selector for publication date
- **author**: Selector for author name
- **body**: Selector for article body text

#### Example Selectors for Common Sites

**Standard Blog/News Site:**
```json
{
  "article_links": "article a, .post-link",
  "title": "h1, .entry-title",
  "date": "time, .published-date",
  "author": ".author, [rel='author']",
  "body": ".entry-content, .post-content"
}
```

**News Flash/Short-form Content:**
```json
{
  "article_links": "a[href*='/flash/']",
  "title": "h1",
  "date": "time",
  "author": ".author-name",
  "body": ".flash-content, .news-body"
}
```

### Environment Variables

You can also configure the scraper using environment variables:

```bash
export SCRAPER_TARGET_URL="https://example.com/news"
export SCRAPER_MAX_ARTICLES=20
export SCRAPER_REQUEST_DELAY=2.0
export SCRAPER_OUTPUT_FORMAT=json
export SCRAPER_OUTPUT_PATH=articles.json
export SCRAPER_TIMEOUT=30
export SCRAPER_MAX_RETRIES=3
```

## Usage Examples

### Example 1: Basic Scraping

```bash
python -m scraper.main --url https://example.com/news
```

### Example 2: Custom Settings

```bash
python -m scraper.main \
  --url https://example.com/news \
  --max-articles 20 \
  --output my_articles.json \
  --delay 3.0 \
  --timeout 60
```

### Example 3: CSV Export with Logging

```bash
python -m scraper.main \
  --url https://example.com/news \
  --output articles.csv \
  --output-format csv \
  --log-level DEBUG \
  --log-file scraper.log
```

### Example 4: Using Configuration File

```bash
python -m scraper.main --config example_config.json
```

### Example 5: Quiet Mode (No Console Output)

```bash
python -m scraper.main \
  --url https://example.com/news \
  --log-file scraper.log \
  --quiet
```

## Output Format

### JSON Output

```json
[
  {
    "url": "https://example.com/article1",
    "title": "Article Title",
    "publication_date": "2025-11-11T10:30:00",
    "author": "John Doe",
    "body_text": "Article content...",
    "scraped_at": "2025-11-11T12:00:00",
    "source_website": "example.com"
  }
]
```

### CSV Output

```csv
url,title,publication_date,author,body_text,scraped_at,source_website
"https://example.com/article1","Article Title","2025-11-11T10:30:00","John Doe","Article content...","2025-11-11T12:00:00","example.com"
```

## Project Structure

```
news-scraper/
├── scraper/
│   ├── __init__.py
│   ├── main.py              # CLI interface
│   └── core/
│       ├── __init__.py
│       ├── config.py        # Configuration management
│       ├── http_client.py   # HTTP client with retry logic
│       ├── logger.py        # Logging configuration
│       ├── models.py        # Data models
│       ├── parser.py        # HTML parsing
│       ├── scraper.py       # Main scraper controller
│       └── storage.py       # Data storage (JSON/CSV)
├── example_config.json      # Example configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## How It Works

1. **Fetch Listing Page**: The scraper fetches the target URL (listing page)
2. **Extract Article URLs**: Parses the page to find article links
3. **Fetch Articles**: Retrieves each article page with rate limiting
4. **Parse Content**: Extracts title, date, author, and body text
5. **Check Duplicates**: Skips articles that have already been scraped
6. **Save Data**: Stores articles in JSON or CSV format
7. **Report Results**: Displays summary of scraping session

## Error Handling

The scraper includes robust error handling:

- **Network Errors**: Automatic retry with exponential backoff
- **Parsing Errors**: Continues processing other articles
- **Duplicate Detection**: Skips already-scraped articles
- **Validation**: Validates configuration before starting
- **Graceful Shutdown**: Handles Ctrl+C interrupts cleanly

## Logging

The scraper provides detailed logging at multiple levels:

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about scraping progress
- **WARNING**: Warning messages for non-critical issues
- **ERROR**: Error messages for failed operations
- **CRITICAL**: Critical errors that stop execution

Example log output:

```
2025-11-11 10:30:00 - scraper.core.scraper - INFO - Starting scraping session
2025-11-11 10:30:01 - scraper.core.http_client - INFO - Fetching URL: https://example.com/news
2025-11-11 10:30:02 - scraper.core.scraper - INFO - Found 15 article URLs
2025-11-11 10:30:03 - scraper.core.scraper - INFO - [1/10] Successfully scraped: Article Title
```

## Best Practices

1. **Respect Rate Limits**: Use appropriate delays between requests (2-3 seconds recommended)
2. **Start Small**: Test with a small number of articles first
3. **Use Configuration Files**: Store selectors in config files for reusability
4. **Monitor Logs**: Check logs for errors and warnings
5. **Handle Failures**: The scraper continues on errors, but review failed articles
6. **Verify Selectors**: Test CSS selectors on the target website first

## Troubleshooting

### No Articles Found

- Check if the target URL is correct
- Verify CSS selectors match the website structure
- Try without custom selectors to use fallback logic

### Articles Fail to Parse

- Check if the website structure has changed
- Update CSS selectors in configuration
- Review logs for specific error messages

### Rate Limiting Issues

- Increase `--delay` parameter
- Reduce `--max-articles` to scrape fewer articles
- Check if the website has anti-scraping measures

### Timeout Errors

- Increase `--timeout` parameter
- Check your internet connection
- Verify the website is accessible

## Legal and Ethical Considerations

- **Respect robots.txt**: Check the website's robots.txt file
- **Terms of Service**: Review and comply with the website's terms of service
- **Rate Limiting**: Don't overload servers with too many requests
- **Copyright**: Respect copyright and intellectual property rights
- **Personal Data**: Handle any personal data in compliance with privacy laws

## License

This project is provided as-is for educational and personal use.

## Contributing

Contributions are welcome! Please ensure your code follows the existing style and includes appropriate tests.

## Support

For issues, questions, or suggestions, please open an issue on the project repository.
