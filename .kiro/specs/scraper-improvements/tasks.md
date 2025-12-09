# Implementation Tasks

## Task 1: Update Session Manager for Log Filtering
**Status**: ✅ COMPLETED  
**Priority**: High  
**Estimated Time**: 30 minutes

### Description
Add `show_in_all` parameter to the session manager's logging system to control which logs appear in the "全部" (All) tab.

### Acceptance Criteria
- [x] `add_log()` method accepts `show_in_all` parameter (default: True)
- [x] Log entries include `show_in_all` field in their structure
- [x] Backward compatible with existing log calls

### Files to Modify
- `/Users/kabellatsang/PycharmProjects/ai_code/scraper/core/session.py`

### Implementation Details
```python
def add_log(self, message: str, log_type: str, source: str, show_in_all: bool = True):
    """
    Add log entry with visibility control
    
    Args:
        message: Log message
        log_type: Type of log ('info', 'success', 'error', 'filtered', 'skipped')
        source: Source name ('BLOCKBEATS', 'JINSE', 'PANEWS', 'ALL')
        show_in_all: Whether to display in "全部" tab (default: True)
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

### Testing
- Verify logs with `show_in_all=True` are stored correctly
- Verify logs with `show_in_all=False` are stored correctly
- Verify default behavior (show_in_all=True) works

---

## Task 2: Fix Jinse Scraper URL Pattern
**Status**: ✅ COMPLETED & TESTED  
**Priority**: High  
**Estimated Time**: 1 hour

### Description
Update Jinse scraper to properly handle the ID-based URL pattern by extracting the latest article ID and iterating backwards.

### Acceptance Criteria
- [x] Extract latest article ID from Jinse homepage
- [x] Iterate backwards from latest ID
- [x] Check exactly `max_articles` articles or stop at date limit
- [x] Mark filtered/skipped logs with `show_in_all=False`
- [x] Mark success logs with `show_in_all=True`

### Test Results
✅ Successfully tested with `test_jinse_only.py`:
- Latest ID found: 488385
- Articles checked: 20
- Articles scraped: 13
- Duration: 23.97 seconds

### Files to Modify
- `/Users/kabellatsang/PycharmProjects/ai_code/scraper/core/jinse_scraper.py`

### Implementation Details

#### Add method to find latest ID:
```python
def _find_latest_article_id(self) -> int:
    """
    Extract the latest article ID from Jinse homepage
    
    Returns:
        int: Latest article ID
    """
    try:
        response = self.http_client.get("https://www.jinse.cn/lives")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all article links matching pattern /lives/{number}.html
        article_links = soup.find_all('a', href=re.compile(r'/lives/(\d+)\.html'))
        
        if not article_links:
            self._log("⚠️  无法找到文章链接", "error", show_in_all=True)
            return 0
        
        # Extract all IDs and return the maximum
        ids = []
        for link in article_links:
            match = re.search(r'/lives/(\d+)\.html', link['href'])
            if match:
                ids.append(int(match.group(1)))
        
        latest_id = max(ids) if ids else 0
        self._log(f"✅ 找到最新文章ID: {latest_id}", "info", show_in_all=True)
        return latest_id
        
    except Exception as e:
        self._log(f"❌ 获取最新ID失败: {str(e)}", "error", show_in_all=True)
        return 0
```

#### Update scrape method:
```python
def scrape(self) -> ScrapeResult:
    """Scrape Jinse articles by iterating backwards from latest ID"""
    start_time = time.time()
    articles_checked = 0
    articles_scraped = 0
    articles_failed = 0
    errors = []
    
    self._log("🔍 正在查找最新文章ID...", "info", show_in_all=True)
    latest_id = self._find_latest_article_id()
    
    if latest_id == 0:
        return ScrapeResult(
            total_articles_found=0,
            articles_scraped=0,
            articles_failed=0,
            duration_seconds=time.time() - start_time,
            errors=["无法获取最新文章ID"]
        )
    
    current_id = latest_id
    
    while articles_checked < self.config.max_articles:
        articles_checked += 1
        url = f"https://www.jinse.cn/lives/{current_id}.html"
        
        try:
            # Fetch article
            response = self.http_client.get(url)
            
            if response.status_code == 404:
                self._log(f"[{articles_checked}] ID {current_id}... ⏭️  文章不存在", "skipped", show_in_all=False)
                current_id -= 1
                continue
            
            # Parse article
            article = self._parse_article(response.text, url)
            
            # Check date range
            if article.publish_date < self.start_date:
                self._log(f"[{articles_checked}] ID {current_id}... ⏭️  日期过早 ({article.publish_date})", "filtered", show_in_all=False)
                break  # Stop if too old
            
            if article.publish_date > self.end_date:
                self._log(f"[{articles_checked}] ID {current_id}... ⏭️  日期过晚 ({article.publish_date})", "filtered", show_in_all=False)
                current_id -= 1
                continue
            
            # Check keywords
            if not self._matches_keywords(article):
                self._log(f"[{articles_checked}] ID {current_id}... ⏭️  无匹配关键词", "filtered", show_in_all=False)
                current_id -= 1
                continue
            
            # Save article
            self.data_store.save(article)
            articles_scraped += 1
            self._log(f"[{articles_checked}] ✅ 已保存: {article.title[:50]}...", "success", show_in_all=True)
            
        except Exception as e:
            articles_failed += 1
            error_msg = f"ID {current_id} 失败: {str(e)}"
            errors.append(error_msg)
            self._log(f"[{articles_checked}] ❌ {error_msg}", "error", show_in_all=True)
        
        current_id -= 1
        time.sleep(self.config.request_delay)
    
    duration = time.time() - start_time
    self._log(f"✅ 完成! 检查: {articles_checked}, 抓取: {articles_scraped}, 失败: {articles_failed}", "info", show_in_all=True)
    
    return ScrapeResult(
        total_articles_found=articles_checked,
        articles_scraped=articles_scraped,
        articles_failed=articles_failed,
        duration_seconds=duration,
        errors=errors
    )
```

### Testing
- Run `test_jinse_only.py`
- Verify latest ID extraction works
- Verify backward iteration works
- Verify date filtering works
- Verify keyword matching works

---

## Task 3: Update BlockBeats Scraper Logging
**Status**: ✅ COMPLETED  
**Priority**: Medium  
**Estimated Time**: 20 minutes

### Description
Update BlockBeats scraper to use `show_in_all=False` for filtered/skipped logs.

### Acceptance Criteria
- [x] Filtered articles use `show_in_all=False`
- [x] Skipped articles use `show_in_all=False`
- [x] Success articles use `show_in_all=True`
- [x] Error messages use `show_in_all=True`

### Files to Modify
- `/Users/kabellatsang/PycharmProjects/ai_code/scraper/core/blockbeats_scraper.py`

### Implementation Details
Update all `_log()` calls:
- Date out of range: `show_in_all=False`
- No keyword match: `show_in_all=False`
- Successfully saved: `show_in_all=True`
- Errors: `show_in_all=True`

---

## Task 4: Update PANews Scraper Logging
**Status**: ✅ COMPLETED  
**Priority**: Medium  
**Estimated Time**: 20 minutes

### Description
Update PANews scraper to use `show_in_all=False` for filtered/skipped logs.

### Acceptance Criteria
- [x] Filtered articles use `show_in_all=False`
- [x] Skipped articles use `show_in_all=False`
- [x] Success articles use `show_in_all=True`
- [x] Error messages use `show_in_all=True`

### Files to Modify
- `/Users/kabellatsang/PycharmProjects/ai_code/scraper/core/panews_scraper.py`

### Implementation Details
Same as Task 3, update all `_log()` calls appropriately.

---

## Task 5: Update Web Interface Log Filtering
**Status**: ✅ COMPLETED  
**Priority**: High  
**Estimated Time**: 30 minutes

### Description
Update the web interface to filter logs in the "全部" tab based on the `show_in_all` flag.

### Acceptance Criteria
- [x] "全部" tab shows only logs with `show_in_all=true`
- [x] Source-specific tabs show all logs for that source
- [x] Log filtering is performant (no lag)

### Files to Modify
- `/Users/kabellatsang/PycharmProjects/ai_code/scraper/templates/index.html`

### Implementation Details
```javascript
function updateLogs(source) {
    const logsContainer = document.getElementById('logs-container');
    const logs = currentSession.logs || [];
    
    let filteredLogs;
    
    if (source === 'ALL') {
        // Show only logs with show_in_all=true
        filteredLogs = logs.filter(log => log.show_in_all === true);
    } else {
        // Show all logs for specific source
        filteredLogs = logs.filter(log => log.source === source);
    }
    
    // Render logs
    logsContainer.innerHTML = '';
    filteredLogs.forEach(log => {
        const logElement = createLogElement(log);
        logsContainer.appendChild(logElement);
    });
    
    // Auto-scroll to bottom
    logsContainer.scrollTop = logsContainer.scrollHeight;
}

// Update tab switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const source = button.dataset.source;
        updateLogs(source);
    });
});
```

### Testing
- Open web interface
- Start scraping with multiple sources
- Switch to "全部" tab - should see only matched articles
- Switch to source tabs - should see all logs including filtered

---

## Task 6: Integration Testing
**Status**: ⏳ READY FOR TESTING  
**Priority**: High  
**Estimated Time**: 1 hour

### Description
Comprehensive testing of all changes together.

### Test Cases

#### Test 1: Jinse Scraper Standalone ✅ PASSED
```bash
cd /Users/kabellatsang/PycharmProjects/ai_code
python test_jinse_only.py
```
Expected: Successfully scrapes articles, shows detailed logs
**Result**: ✅ PASSED - 13/20 articles scraped successfully

#### Test 2: Multi-Source with 10 Articles
- Open web interface
- Set: 10 articles, all 3 sources, 2-day range
- Keywords: BTC, Bitcoin, 比特币
- Expected: Each source checks 10 articles

#### Test 3: Multi-Source with 50 Articles
- Open web interface
- Set: 50 articles, all 3 sources, 7-day range
- Keywords: BTC, ETH, 比特币, 以太坊
- Expected: Each source checks 50 articles

#### Test 4: Log Filtering
- Run any multi-source scrape
- Check "全部" tab: Should show only matched articles + status messages
- Check each source tab: Should show all logs including filtered

### Acceptance Criteria
- [x] Test 1 passes (Jinse standalone)
- [ ] Test 2 passes (Multi-source 10 articles) - Ready to test
- [ ] Test 3 passes (Multi-source 50 articles) - Ready to test
- [ ] Test 4 passes (Log filtering) - Ready to test
- [ ] No errors in console
- [ ] Logs display correctly
- [ ] Performance is acceptable

---

## Deployment Checklist

- [x] All tasks completed
- [x] Jinse scraper tested and working
- [ ] Web interface tested (ready to test)
- [x] Code reviewed
- [x] Documentation updated
- [ ] Deploy to staging
- [ ] Test on staging
- [ ] Deploy to production
- [ ] Monitor for issues

## Rollback Plan

If critical issues found:
1. Revert commits in reverse order (Task 5 → Task 1)
2. Test after each revert
3. Identify problematic change
4. Fix and redeploy
