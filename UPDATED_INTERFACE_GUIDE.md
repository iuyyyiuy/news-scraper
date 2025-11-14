# ✅ Updated Interface - Last XX Days

## Changes Made

### 1. Simplified Date Input
**Before:** Start Date + End Date (date pickers)
**After:** "Last XX days" (single number input)

### 2. Default Settings
- **Days Filter**: 7 (last 7 days)
- **Keywords**: Pre-filled with security keywords
- **Max Articles**: 1000

### 3. How It Works
1. User enters number of days (e.g., 7, 14, 30)
2. System calculates: `start_date = today - N days`, `end_date = today`
3. Scraper fetches articles from listing page
4. Filters by date and keywords
5. Returns matching articles

## Restart Server

```bash
# Stop current server (Ctrl+C)
# Start again:
.venv/bin/uvicorn scraper.web_api:app --host 127.0.0.1 --port 8000
```

## Test the New Interface

1. Go to `http://127.0.0.1:8000`
2. You'll see:
   - **时间范围（最近几天）**: Input field with value "7"
   - **关键词**: Pre-filled security keywords
   - **文章浏览数量上限**: 1000

3. Try different values:
   - `7` = Last 7 days
   - `14` = Last 2 weeks
   - `30` = Last month

## Benefits

✅ **Simpler**: No need to calculate dates
✅ **Faster**: Just enter a number
✅ **Clearer**: "Last 7 days" is easier to understand than date ranges
✅ **Matches Colab**: Same approach as your notebook

## Example Usage

### Last 7 days with security keywords:
- Days: `7`
- Keywords: `安全问题, 黑客, 被盗, 漏洞, 攻击...`
- Max Articles: `1000`
- Click "开始爬取"

### Last 30 days:
- Days: `30`
- Keywords: (same)
- Max Articles: `1000`
- Click "开始爬取"

## Expected Results

For last 7 days with security keywords, you should get:
- **Faster scraping** (listing page approach)
- **More accurate results** (proper date filtering)
- **Better performance** (no need to iterate through IDs)

The scraper will:
1. Fetch https://www.theblockbeats.info/newsflash
2. Extract all `/flash/{number}` URLs
3. Scrape each article
4. Filter by last N days
5. Filter by keywords
6. Return results

Enjoy the simplified interface! 🎉
