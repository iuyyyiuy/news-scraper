# Web Interface Testing Guide

## Quick Start

### Step 1: Start the Web Server

```bash
./START_WEB_SERVER.sh
```

Or manually:
```bash
cd /Users/kabellatsang/PycharmProjects/ai_code
python run_web_server.py --port 8000
```

### Step 2: Open Browser

Navigate to: **http://localhost:8000**

---

## Test Plan

### Test 1: Quick Multi-Source Test (5 minutes)

**Purpose**: Verify basic functionality and log filtering

**Settings**:
- **Date Range**: Last 2 days
- **Keywords**: `BTC, Bitcoin, 比特币, ETH, 以太坊`
- **Sources**: ✓ BlockBeats, ✓ Jinse, ✓ PANews
- **Articles per source**: `10`

**Expected Results**:
- ✅ Each source checks exactly 10 articles
- ✅ "全部" tab shows only matched articles (clean view)
- ✅ Source tabs show all logs including filtered
- ✅ Jinse titles are correct (not "金色财经_区块链资讯_数字货币行情分析")
- ✅ Dates show as 2025-MM-DD format

**What to Check**:

1. **"全部" (All) Tab** - Should look like:
   ```
   🚀 开始多源爬取...
   📰 来源: BLOCKBEATS, JINSE, PANEWS
   [BLOCKBEATS] ✅ 已保存: Bitcoin价格...
   [JINSE] ✅ 已保存: 比特币行情...
   [PANEWS] ✅ 已保存: BTC市场...
   📊 各来源统计:
     BLOCKBEATS: 检查 10 篇, 抓取 X 篇
     JINSE: 检查 10 篇, 抓取 X 篇
     PANEWS: 检查 10 篇, 抓取 X 篇
   ✅ 爬取完成！
   ```
   
   ❌ Should NOT show:
   - "⏭️  无匹配关键词"
   - "⏭️  日期过早"
   - "⏭️  文章不存在"

2. **"JINSE" Tab** - Should show ALL logs:
   ```
   🔍 正在查找最新文章ID...
   ✅ 找到最新文章ID: 488385
   [1] ID 488385... ⏭️  无匹配关键词
   [2] ID 488384... ✅ 已保存: 某巨鲸...
   [3] ID 488383... ⏭️  日期过早
   [4] ID 488382... ✅ 已保存: 金色午报...
   ...
   检查: 10, 抓取: X
   ```

3. **"BLOCKBEATS" Tab** - Should show ALL logs
4. **"PANEWS" Tab** - Should show ALL logs

---

### Test 2: Jinse Title & Date Verification (2 minutes)

**Purpose**: Verify Jinse parser fixes

**Settings**:
- **Date Range**: Last 1 day
- **Keywords**: `Cardano, FBI, 比特币` (to match specific articles)
- **Sources**: ✓ Jinse only
- **Articles per source**: `20`

**Expected Results**:
- ✅ Titles are meaningful (e.g., "Cardano周五因旧代码漏洞发生短暂性链分裂...")
- ✅ NOT generic "金色财经_区块链资讯_数字货币行情分析"
- ✅ Dates show as 2025-11-23 (not 2025-11-23 00:00:00)

**How to Verify**:
1. Look at the matched articles in "全部" tab
2. Check the article titles are specific and relevant
3. Download CSV and check date format

---

### Test 3: Full Production Test (10 minutes)

**Purpose**: Test with production-like settings

**Settings**:
- **Date Range**: Last 7 days
- **Keywords**: `BTC, Bitcoin, 比特币, 以太坊, ETH, USDT, 加密货币`
- **Sources**: ✓ BlockBeats, ✓ Jinse, ✓ PANews
- **Articles per source**: `50`

**Expected Results**:
- ✅ Each source checks exactly 50 articles
- ✅ Total articles checked: 150 (50 × 3)
- ✅ Scraping completes in ~3-5 minutes
- ✅ "全部" tab remains clean (only matched articles)
- ✅ CSV file downloads successfully
- ✅ No errors in browser console

**Performance Benchmarks**:
- Jinse: ~60 seconds for 50 articles
- BlockBeats: ~60 seconds for 50 articles
- PANews: ~60 seconds for 50 articles
- Total: ~3 minutes (sources run sequentially)

---

### Test 4: Log Filtering Verification (3 minutes)

**Purpose**: Verify show_in_all flag works correctly

**Settings**:
- **Date Range**: Last 1 day
- **Keywords**: `XYZ123NOTFOUND` (keyword that won't match)
- **Sources**: ✓ Jinse only
- **Articles per source**: `10`

**Expected Results**:
- ✅ "全部" tab shows NO matched articles (only status messages)
- ✅ "JINSE" tab shows all 10 articles as "⏭️  无匹配关键词"
- ✅ Demonstrates filtering is working

---

## Troubleshooting

### Issue: Server won't start

**Solution**:
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>

# Or use a different port
python run_web_server.py --port 8080
```

### Issue: Import errors

**Solution**:
```bash
cd /Users/kabellatsang/PycharmProjects/ai_code
source .venv/bin/activate
pip install -r requirements.txt
```

### Issue: "全部" tab still shows filtered logs

**Check**:
1. Hard refresh browser (Cmd+Shift+R)
2. Check browser console for JavaScript errors
3. Verify `index.html.backup` wasn't accidentally restored

### Issue: Jinse titles still wrong

**Check**:
1. Verify `jinse_scraper.py` has the custom parser
2. Check if `jinse_scraper.py.backup` was restored
3. Restart the web server

---

## Browser Console Checks

Open browser console (F12 or Cmd+Option+I) and check for:

✅ **Good**:
- No red errors
- WebSocket/SSE connection established
- Logs updating in real-time

❌ **Bad**:
- JavaScript errors
- Failed to fetch errors
- CORS errors

---

## CSV Output Verification

After scraping completes:

1. Click "Download CSV" button
2. Open the CSV file
3. Verify columns:
   - `url`: Full article URL
   - `title`: Correct article title (not generic)
   - `publication_date`: 2025-MM-DD format
   - `author`: Source name
   - `body_text`: Full article content
   - `source_website`: Domain name
   - `matched_keywords`: Keywords that matched

---

## Success Criteria

### ✅ All Tests Pass If:

1. **Log Filtering**:
   - "全部" tab shows only matched articles
   - Source tabs show all logs including filtered

2. **Jinse Parser**:
   - Titles are correct and specific
   - Dates are in 2025-MM-DD format
   - Content is fully extracted

3. **Multi-Source**:
   - Each source checks specified number of articles
   - All sources complete successfully
   - No errors in logs

4. **Performance**:
   - 50 articles per source completes in ~3-5 minutes
   - No timeouts or crashes
   - Browser remains responsive

5. **Data Quality**:
   - CSV contains accurate data
   - No duplicate articles (if deduplication enabled)
   - All matched keywords are relevant

---

## Quick Test Commands

### Test 1: Quick (10 articles)
```
Date: 2 days
Keywords: BTC, Bitcoin, 比特币
Sources: All
Articles: 10
Expected time: ~1 minute
```

### Test 2: Medium (25 articles)
```
Date: 5 days
Keywords: BTC, ETH, 比特币, 以太坊
Sources: All
Articles: 25
Expected time: ~2 minutes
```

### Test 3: Full (50 articles)
```
Date: 7 days
Keywords: BTC, Bitcoin, 比特币, 以太坊, ETH, USDT
Sources: All
Articles: 50
Expected time: ~3-5 minutes
```

---

## After Testing

### If All Tests Pass ✅

1. Document any issues found
2. Proceed with deployment:
   ```bash
   cd /Users/kabellatsang/PycharmProjects/ai_code
   ./deploy_to_render.sh
   ```

### If Tests Fail ❌

1. Note which test failed
2. Check error messages in:
   - Browser console
   - Server logs
   - "全部" tab
3. Review backup files if needed
4. Report issues for fixing

---

## Test Results Template

Copy this and fill in your results:

```
## Test Results - [Date]

### Test 1: Quick Multi-Source (10 articles)
- [ ] "全部" tab shows only matched articles
- [ ] Source tabs show all logs
- [ ] Each source checked 10 articles
- [ ] No errors
- Notes: 

### Test 2: Jinse Verification
- [ ] Titles are correct
- [ ] Dates are 2025-MM-DD format
- [ ] Content extracted fully
- Notes:

### Test 3: Full Production (50 articles)
- [ ] Completed successfully
- [ ] Time taken: ___ minutes
- [ ] Total articles scraped: ___
- [ ] CSV downloaded successfully
- Notes:

### Test 4: Log Filtering
- [ ] "全部" tab clean when no matches
- [ ] Source tabs show filtered logs
- Notes:

### Overall Status: ✅ PASS / ❌ FAIL

Issues found:
1. 
2. 
3. 

Recommendations:
1. 
2. 
```

---

## Ready to Test!

Run `./START_WEB_SERVER.sh` and follow the test plan above.

Good luck! 🚀
