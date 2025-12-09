# 🔄 Restart Server Guide

## Updated Scraper Logic

The scraper now uses the same approach as your Colab notebook:

1. ✅ Fetches the listing page: `https://www.theblockbeats.info/newsflash`
2. ✅ Extracts all `/flash/{number}` article URLs from the page
3. ✅ Scrapes each article
4. ✅ Filters by date range and keywords
5. ✅ Much faster than iterating through IDs!

## How to Restart

### Step 1: Stop the Current Server
In your terminal where the server is running, press:
```
Ctrl + C
```

### Step 2: Start the Server Again
```bash
.venv/bin/uvicorn scraper.web_api:app --host 127.0.0.1 --port 8000
```

### Step 3: Refresh Your Browser
1. Go to `http://127.0.0.1:8000`
2. Press `Cmd + Shift + R` (Mac) or `Ctrl + Shift + R` (Windows) to hard refresh
3. The form should still show:
   - Start Date: 2025-11-01
   - End Date: 2025-11-13
   - Keywords: (your security keywords)

### Step 4: Run a New Scrape
1. Click "开始爬取" (Start Scraping)
2. Watch the progress - it should be much faster now!
3. The scraper will:
   - Find all articles on the newsflash listing page
   - Process each one
   - Filter by your date range (Nov 1-13)
   - Filter by your keywords
   - Show you the results

### Expected Results

For Nov 1-13, 2025 with security keywords, you should see:
- **Much faster scraping** (processes listing page articles only)
- **More articles found** (the listing page shows many recent articles)
- **Accurate date filtering** (only articles within your date range)

## Configuration

Current settings in `web_api.py`:
- **Target URL**: `https://www.theblockbeats.info/newsflash` (listing page)
- **Max Articles**: 1000 (will process up to 1000 articles from listing)
- **Request Delay**: 2.0 seconds (polite to the server)

## Troubleshooting

### If you still get few results:
1. Check the browser console (F12) for any errors
2. Try increasing `max_articles` in the web interface
3. Check that your date range is correct
4. Verify keywords are matching (try fewer keywords for testing)

### If it's too slow:
- The listing page approach should be fast
- Each article still needs to be fetched individually
- With 2 second delay, 50 articles = ~100 seconds

## Next Steps

After restarting, try a test scrape and let me know:
1. How many articles were found
2. How many matched your filters
3. The total time taken

This will help verify the new approach is working correctly!
