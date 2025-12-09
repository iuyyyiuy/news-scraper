# Multi-Source Scraper Improvements - Design

## Architecture Overview

The scraper system consists of:
- Individual scrapers (BlockBeats, Jinse, PANews)
- Multi-source coordinator
- Session manager for logging
- Web interface for monitoring

## Design Decisions

### 1. Jinse URL Pattern Handling (AC1)

**Current Issue**: Jinse uses sequential ID-based URLs (`/lives/{number}.html`)

**Solution**: 
- Extract latest article ID from the main page
- Iterate backwards from latest ID
- Check each article until limits reached

**Implementation**:
```python
# In jinse_scraper.py
def _find_latest_article_id(self) -> int:
    """Extract the latest article ID from Jinse homepage"""
    # Parse https://www.jinse.cn/lives
    # Find highest article ID in the page
    # Return that ID
    
def scrape(self):
    latest_id = self._find_latest_article_id()
    current_id = latest_id
    articles_checked = 0
    
    while articles_checked < self.config.max_articles:
        url = f"https://www.jinse.cn/lives/{current_id}.html"
        # Check article
        # If date too old, break
        # If keywords match, save
        current_id -= 1
        articles_checked += 1
```

**Property**: For any valid latest ID `n`, checking articles from `n` to `n-50` will process exactly 50 articles or stop when date limit reached.

### 2. Logging System Redesign (AC3, AC4)

**Current Issue**: All logs appear in "全部" tab, making it noisy

**Solution**: Add `show_in_all` flag to control log visibility

**Implementation**:

#### Session Manager (`session.py`)
```python
class ScraperSession:
    def add_log(self, message: str, log_type: str, source: str, show_in_all: bool = True):
        """
        Add log entry with visibility control
        
        Args:
            message: Log message
            log_type: 'info', 'success', 'error', 'filtered', 'skipped'
            source: 'BLOCKBEATS', 'JINSE', 'PANEWS', or 'ALL'
            show_in_all: Whether to show in "全部" tab (default True)
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'type': log_type,
            'source': source,
            'show_in_all': show_in_all
        }
        self.logs.append(log_entry)
```

#### Scraper Base Class
```python
class BaseScraper:
    def _log(self, message: str, log_type: str = 'info', show_in_all: bool = None):
        """
        Log with smart defaults:
        - success: show_in_all=True
        - error: show_in_all=True  
        - filtered: show_in_all=False
        - skipped: show_in_all=False
        - info: show_in_all=True (for important status)
        """
        if show_in_all is None:
            show_in_all = log_type not in ['filtered', 'skipped']
        
        if self.log_callback:
            self.log_callback(message, log_type, self.source_name, show_in_all)
```

#### Web Interface (`index.html`)
```javascript
function updateLogs(source) {
    const logs = session.logs;
    
    if (source === 'ALL') {
        // Filter to only show logs with show_in_all=true
        const filteredLogs = logs.filter(log => log.show_in_all === true);
        displayLogs(filteredLogs);
    } else {
        // Show all logs for specific source
        const sourceLogs = logs.filter(log => log.source === source);
        displayLogs(sourceLogs);
    }
}
```

**Property**: "全部" tab displays only logs where `show_in_all=true`, while source-specific tabs display all logs for that source.

### 3. Per-Source Article Count (AC2)

**Current Status**: Already implemented correctly

**Verification**: Each scraper has its own `max_articles` config

**Property**: For `n` sources with limit `m`, total articles checked = `n × m`

## Data Flow

```
User Request (50 articles, 3 sources)
    ↓
MultiSourceScraper
    ↓
    ├─→ BlockBeats (checks 50) ─→ Logs (all → source tab, success → all tab)
    ├─→ Jinse (checks 50)      ─→ Logs (all → source tab, success → all tab)
    └─→ PANews (checks 50)     ─→ Logs (all → source tab, success → all tab)
    ↓
Session Manager (aggregates logs)
    ↓
Web Interface (filters by show_in_all flag)
```

## Testing Strategy

### Unit Tests
1. Test Jinse ID extraction
2. Test Jinse backward iteration
3. Test log filtering logic
4. Test show_in_all flag propagation

### Integration Tests
1. Run `test_jinse_only.py` to verify Jinse works
2. Test multi-source with 10 articles per source
3. Verify "全部" tab shows only matched articles
4. Verify source tabs show all logs

### Manual Testing
1. Open web interface
2. Set 50 articles, all sources, 2-day range
3. Check "全部" tab - should see only matched articles
4. Check each source tab - should see all logs including filtered

## Implementation Tasks

### Task 1: Update Session Manager
- File: `scraper/core/session.py`
- Add `show_in_all` parameter to `add_log` method
- Update log entry structure to include flag

### Task 2: Update Jinse Scraper
- File: `scraper/core/jinse_scraper.py`
- Implement `_find_latest_article_id()` method
- Update `scrape()` to iterate backwards from latest ID
- Mark filtered/skipped logs with `show_in_all=False`

### Task 3: Update Other Scrapers
- Files: `blockbeats_scraper.py`, `panews_scraper.py`
- Mark filtered/skipped logs with `show_in_all=False`
- Keep success/error logs with `show_in_all=True`

### Task 4: Update Web Interface
- File: `scraper/templates/index.html`
- Filter logs in "全部" tab by `show_in_all` flag
- Show all logs in source-specific tabs

### Task 5: Testing
- Run `test_jinse_only.py`
- Test web interface with multiple sources
- Verify log filtering works correctly

## Rollback Plan

If issues occur:
1. Revert session.py changes
2. Revert scraper changes
3. Keep old logging behavior (all logs in all tabs)
4. Debug and retry

## Performance Considerations

- No performance impact expected
- Log filtering happens client-side (JavaScript)
- Backward iteration in Jinse is same complexity as forward

## Security Considerations

- No security changes
- Same rate limiting and request delays
- No new external dependencies
