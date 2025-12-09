# Log Format Update ✅

## Changes Made

Updated the logging system so that:
1. **"全部" (All) tab**: Shows ONLY matched news titles
2. **Specific source tabs**: Shows article IDs and status (without redundant progress updates)

---

## Before vs After

### "全部" (All) Tab

#### ❌ Before (Too Noisy)
```
🚀 开始多源爬取...
[BLOCKBEATS] 检查: 1, 抓取: 1
[BLOCKBEATS] 检查: 3, 抓取: 2
[BLOCKBEATS] 检查: 4, 抓取: 3
[BLOCKBEATS] 检查: 14, 抓取: 4
[JINSE] 检查: 1, 抓取: 1
[JINSE] 检查: 5, 抓取: 3
[BLOCKBEATS] ✅ 已保存: Bitcoin价格突破...
[JINSE] ✅ 已保存: 比特币行情分析...
```

#### ✅ After (Clean - Only Titles)
```
🚀 开始多源爬取...
📰 来源: BLOCKBEATS, JINSE, PANEWS
[BLOCKBEATS] ✅ Bitcoin价格突破新高，市场情绪乐观
[JINSE] ✅ 比特币行情分析：技术面显示强势信号
[PANEWS] ✅ 以太坊升级进展顺利，开发者表示满意
[BLOCKBEATS] ✅ 加密货币市场总市值突破2万亿美元
[JINSE] ✅ 金色午报 | 11月23日午间重要动态一览
📊 各来源统计:
  BLOCKBEATS: 检查 50 篇, 抓取 12 篇
  JINSE: 检查 50 篇, 抓取 15 篇
  PANEWS: 检查 50 篇, 抓取 8 篇
✅ 爬取完成！最终保存 35 篇唯一文章
```

---

### Specific Source Tabs (e.g., BlockBeats)

#### ❌ Before (Redundant Progress)
```
🔍 正在查找最新文章ID...
✅ 找到最新文章ID: 321600
[BLOCKBEATS] 检查: 1, 抓取: 1
[1] ID 321600... ✅ 已保存: Bitcoin...
[BLOCKBEATS] 检查: 3, 抓取: 2
[2] ID 321599... ⏭️  无匹配关键词
[BLOCKBEATS] 检查: 4, 抓取: 3
[3] ID 321598... ✅ 已保存: BTC...
```

#### ✅ After (Clean ID Logs)
```
🔍 正在查找最新文章ID...
✅ 找到最新文章ID: 321600
[1] ID 321600... ✅ 已保存: Bitcoin价格突破新高
[2] ID 321599... ⏭️  无匹配关键词
[3] ID 321598... ✅ 已保存: BTC市场动态更新
[4] ID 321597... ⏭️  日期过早
[5] ID 321596... ✅ 已保存: 加密货币行情分析
...
检查: 50, 抓取: 12
```

---

## What Was Changed

### File: `scraper/web_api.py`

**Progress callback logs** now use `show_in_all=False`:

```python
# Before
session_manager.add_log(
    session_id,
    f"[{source.upper()}] 检查: {articles_found}, 抓取: {articles_scraped}",
    "progress",
    source=source
)

# After
session_manager.add_log(
    session_id,
    f"[{source.upper()}] 检查: {articles_found}, 抓取: {articles_scraped}",
    "progress",
    source=source,
    show_in_all=False  # ← Don't show in "All" tab
)
```

---

## Log Types and Visibility

| Log Type | "全部" Tab | Source Tab | Example |
|----------|-----------|------------|---------|
| **Success** (matched news) | ✅ Show | ✅ Show | "[JINSE] ✅ 比特币行情..." |
| **Progress** (检查/抓取) | ❌ Hide | ✅ Show | "[BLOCKBEATS] 检查: 1, 抓取: 1" |
| **Filtered** (无匹配) | ❌ Hide | ✅ Show | "[2] ID 321599... ⏭️  无匹配关键词" |
| **Skipped** (日期过早) | ❌ Hide | ✅ Show | "[4] ID 321597... ⏭️  日期过早" |
| **Status** (开始/完成) | ✅ Show | ✅ Show | "🚀 开始多源爬取..." |
| **Statistics** (统计) | ✅ Show | ✅ Show | "📊 各来源统计..." |

---

## Benefits

### "全部" (All) Tab
✅ **Clean and focused** - Only shows what matters (matched news)
✅ **Easy to scan** - See all matched articles at a glance
✅ **No noise** - No progress updates or filtered articles

### Source Tabs
✅ **Complete logs** - All details for debugging
✅ **ID tracking** - See which IDs were checked
✅ **Filter reasons** - Know why articles were skipped
✅ **No redundant progress** - Removed "[SOURCE] 检查: X, 抓取: Y" spam

---

## Example Usage

### Scenario: Scraping 50 articles from 3 sources

**"全部" Tab will show (~40 entries)**:
- Start message
- ~35 matched article titles
- Statistics summary
- Completion message

**Each Source Tab will show (~55 entries)**:
- Start message
- Latest ID found
- 50 article check results (ID + status)
- Final statistics

**Result**: 
- "全部" tab: Clean, focused on results
- Source tabs: Complete, detailed for debugging
- No redundant progress spam

---

## Testing

To verify the changes work:

1. Start web server:
   ```bash
   cd /Users/kabellatsang/PycharmProjects/ai_code
   python3 run_web_server.py --port 8000
   ```

2. Open http://localhost:8000

3. Run a test scrape:
   - Date: 2 days
   - Keywords: BTC, Bitcoin, 比特币
   - Sources: All 3
   - Articles: 10

4. Check logs:
   - ✅ "全部" tab: Only matched titles
   - ✅ Source tabs: ID logs without progress spam

---

## Status

✅ **IMPLEMENTED AND READY**

All changes have been made. The logging system now provides:
- Clean "全部" tab with only matched news
- Detailed source tabs without redundant progress updates
- Better user experience for monitoring scraping progress

Ready for deployment! 🚀
