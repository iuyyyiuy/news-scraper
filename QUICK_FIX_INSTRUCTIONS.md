# Quick Fix Instructions

## Problem Summary:
1. "全部" (All) tab shows too many logs (including filtered news)
2. Need to verify Jinse scraper works correctly
3. Confirm 50 articles means 50 per source (already correct)

## Solution:

### Fix 1: Update Logging Behavior

The issue is that ALL logs go to the "All" tab. We need to filter it so only important logs show there.

**Change in scrapers**: When logging filtered/skipped news, mark them as source-only logs.

### Fix 2: Test Jinse Scraper

Run this test to verify Jinse works:

```bash
cd /Users/kabellatsang/PycharmProjects/ai_code
python -c "
from datetime import date, timedelta
from scraper.core.config import Config
from scraper.core.storage import CSVDataStore
from scraper.core.jinse_scraper import JinseScraper

end_date = date.today()
start_date = end_date - timedelta(days=1)
keywords = ['BTC', 'Bitcoin', '比特币']

config = Config(
    target_url='https://www.jinse.cn/lives',
    max_articles=10,
    request_delay=1.0,
    output_path='jinse_test.csv'
)

store = CSVDataStore('jinse_test.csv')
scraper = JinseScraper(config, store, start_date, end_date, keywords)

print('Testing Jinse scraper...')
result = scraper.scrape()
print(f'Checked: {result.total_articles_found}')
print(f'Scraped: {result.articles_scraped}')
print(f'Failed: {result.articles_failed}')
"
```

## Quick Fix Files:

I'll create the fixed versions of the key files next.
