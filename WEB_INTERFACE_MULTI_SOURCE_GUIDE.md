# Multi-Source Web Interface Guide

## Overview

The web interface now supports scraping from multiple news sources with per-source log tracking and intelligent deduplication.

## Features

### 1. **Multi-Source Selection**
Choose which news sources to scrape from:
- **BlockBeats** (区块律动) - theblockbeats.info
- **Jinse** (金色财经) - jinse.cn
- **PANews** - panewslab.com

You can select any combination of sources. The scraper will run them in parallel for faster results.

### 2. **Per-Source Log Tabs**
View logs organized by source:
- **全部 (All)** - Combined logs from all sources
- **BlockBeats** - Logs specific to BlockBeats scraping
- **Jinse** - Logs specific to Jinse scraping
- **PANews** - Logs specific to PANews scraping

This makes it easy to:
- Track progress for each source independently
- Debug issues with specific sources
- See which source is finding the most articles

### 3. **Smart Deduplication**
Enable/disable intelligent deduplication:
- **Enabled (default)**: Automatically removes duplicate articles across sources
- **Disabled**: Keeps all articles, including duplicates

The deduplication engine uses:
- Title similarity (85% threshold)
- Body text similarity (80% threshold)
- Combined scoring (75% threshold)

### 4. **Flexible Configuration**
- **Time Range**: Specify how many days back to search (1-90 days)
- **Keywords**: Filter articles by keywords (comma-separated)
- **Article Limit**: Set maximum articles to check per source
- **Sources**: Select which sources to scrape
- **Deduplication**: Toggle smart deduplication on/off

## Quick Start

### 1. Start the Web Server

```bash
python test_web_interface_multi_source.py
```

Or using the original script:

```bash
python run_web_server.py
```

### 2. Open Your Browser

Navigate to: http://localhost:8000

### 3. Configure Your Search

1. **Set Time Range**: Enter number of days (e.g., 7 for last 7 days)
2. **Enter Keywords**: Add keywords separated by commas
3. **Select Sources**: Check the boxes for sources you want to scrape
4. **Set Article Limit**: How many articles to check per source
5. **Enable/Disable Deduplication**: Toggle the checkbox

### 4. Start Scraping

Click "开始爬取" (Start Scraping) button.

### 5. Monitor Progress

- Watch real-time logs in the log viewer
- Switch between source tabs to see per-source progress
- See article count update in real-time

### 6. Download Results

When scraping completes:
- Click "📥 下载CSV文件" to download results
- CSV includes all unique articles from all sources
- Articles are marked with their source website

## Usage Examples

### Example 1: Scrape All Sources

```
Time Range: 7 days
Keywords: BTC, Bitcoin, 比特币
Sources: ✓ BlockBeats ✓ Jinse ✓ PANews
Article Limit: 50
Deduplication: ✓ Enabled
```

This will:
- Scrape last 7 days from all three sources
- Check up to 50 articles per source (150 total)
- Filter for Bitcoin-related news
- Remove duplicates across sources

### Example 2: Single Source, No Deduplication

```
Time Range: 3 days
Keywords: 安全, 黑客, 攻击
Sources: ✓ BlockBeats ☐ Jinse ☐ PANews
Article Limit: 100
Deduplication: ☐ Disabled
```

This will:
- Only scrape BlockBeats
- Check up to 100 articles
- Filter for security-related news
- Keep all articles (no deduplication)

### Example 3: Deep Search with Deduplication

```
Time Range: 30 days
Keywords: DeFi, 去中心化金融
Sources: ✓ BlockBeats ✓ Jinse ✓ PANews
Article Limit: 200
Deduplication: ✓ Enabled
```

This will:
- Scrape last 30 days from all sources
- Check up to 200 articles per source (600 total)
- Filter for DeFi-related news
- Remove duplicates (important for long time ranges)

## Log Tab Features

### Viewing Per-Source Logs

Click on any source tab to see logs specific to that source:

- **All Tab**: Shows combined logs from all sources with source prefixes
- **Source Tabs**: Show only logs from that specific source

### Log Types

Logs are color-coded by type:
- **Blue (Info)**: General information and status updates
- **Green (Success)**: Successfully scraped articles
- **Purple (Progress)**: Progress updates with counts
- **Gray (Filtered)**: Articles that were filtered out
- **Orange (Warning)**: Warnings and non-critical issues
- **Red (Error)**: Errors and failures

### Log Messages

Common log messages you'll see:

```
🚀 开始多源爬取...
📅 日期范围: 2025-11-16 到 2025-11-23
🔑 关键词: BTC, Bitcoin, 比特币
📰 来源: BLOCKBEATS, JINSE, PANEWS
🔄 去重: 启用
📊 每个来源最多检查: 50 篇

[BLOCKBEATS] 🔍 正在查找最新文章ID...
[BLOCKBEATS] ✅ 找到最新文章ID: 320000
[BLOCKBEATS] [1] ID 320000... ✅ 已保存: Bitcoin价格突破...

[JINSE] 🔍 正在查找金色财经最新文章ID...
[JINSE] ✅ 找到最新文章ID: 7000000
[JINSE] [1] ID 7000000... ✅ 已保存: 比特币行情分析...

📊 各来源统计:
  BLOCKBEATS: 检查 50 篇, 抓取 12 篇
  JINSE: 检查 50 篇, 抓取 15 篇
  PANEWS: 检查 50 篇, 抓取 8 篇

🔍 去重统计: 移除 5 篇重复文章
✅ 爬取完成！最终保存 30 篇唯一文章
```

## CSV Output Format

The downloaded CSV file includes:

| Column | Description |
|--------|-------------|
| 发布日期 | Publication date |
| 标题 | Article title |
| 正文内容 | Article body text |
| 链接 | Article URL (includes source domain) |
| 匹配关键词 | Matched keywords |

The source can be identified from the URL:
- `theblockbeats.info` = BlockBeats
- `jinse.cn` = Jinse
- `panewslab.com` = PANews

## Performance Tips

### 1. Optimize Article Limit

- **Small searches (1-3 days)**: 20-50 articles per source
- **Medium searches (4-7 days)**: 50-100 articles per source
- **Large searches (8-30 days)**: 100-200 articles per source

### 2. Use Parallel Scraping

The system automatically scrapes sources in parallel, which is much faster than sequential scraping.

Expected times:
- 1 source, 50 articles: ~1-2 minutes
- 3 sources, 50 articles each: ~2-3 minutes (parallel)
- 3 sources, 200 articles each: ~8-12 minutes (parallel)

### 3. Enable Deduplication

Always enable deduplication when:
- Scraping multiple sources
- Using long time ranges
- Searching for popular topics

Deduplication typically removes 10-30% of articles, depending on topic overlap.

### 4. Refine Keywords

Use specific keywords to reduce processing time:
- ✅ Good: "BTC", "Bitcoin", "比特币"
- ❌ Too broad: "crypto", "blockchain"

## Troubleshooting

### Problem: No articles found

**Solutions:**
1. Check if keywords are too specific
2. Expand the time range
3. Try different sources
4. Check the logs for errors

### Problem: Too many duplicates

**Solutions:**
1. Enable deduplication
2. Adjust deduplication thresholds (requires code change)
3. Use more specific keywords

### Problem: Scraping is slow

**Solutions:**
1. Reduce article limit per source
2. Reduce time range
3. Use fewer sources
4. Check network connection

### Problem: Source not working

**Solutions:**
1. Check the source-specific log tab
2. Look for error messages
3. The website structure may have changed
4. Try other sources

### Problem: Can't see per-source logs

**Solutions:**
1. Make sure you selected that source
2. Click on the source tab
3. Wait for scraping to start
4. Check browser console for errors

## API Endpoints

The web interface uses these API endpoints:

### POST /api/scrape
Start a new scraping session.

**Request:**
```json
{
  "days_filter": 7,
  "keywords": ["BTC", "Bitcoin"],
  "sources": ["blockbeats", "jinse", "panews"],
  "max_articles": 50,
  "enable_deduplication": true
}
```

**Response:**
```json
{
  "session_id": "uuid-here",
  "message": "Scraping session started successfully",
  "status": "running"
}
```

### GET /api/status/{session_id}/stream
Stream real-time updates via Server-Sent Events.

**Response (SSE):**
```
data: {"session_id": "...", "status": "running", "articles_scraped": 5, "log": "...", "log_source": "blockbeats"}
```

### GET /api/download/{session_id}
Download results as CSV file.

## Advanced Configuration

### Customize Deduplication Thresholds

Edit `scraper/core/multi_source_scraper.py`:

```python
self.deduplicator = DeduplicationEngine(
    title_threshold=0.90,      # More strict
    body_threshold=0.85,       # More strict
    combined_threshold=0.80    # More strict
)
```

### Add More Sources

1. Create a new scraper (e.g., `newsource_scraper.py`)
2. Add to `MultiSourceScraper.AVAILABLE_SOURCES`
3. Update web interface HTML to add checkbox
4. Test thoroughly

### Customize Request Delay

Edit `scraper/web_api.py`:

```python
DEFAULT_CONFIG = {
    "request_delay": 1.0,  # Faster (be careful!)
    # or
    "request_delay": 3.0,  # Slower (more polite)
}
```

## Best Practices

1. **Start Small**: Test with 1-2 days and 20-30 articles first
2. **Use Specific Keywords**: More specific = faster and more relevant
3. **Enable Deduplication**: Especially for multiple sources
4. **Monitor Logs**: Watch for errors or issues
5. **Be Respectful**: Don't set request delay too low
6. **Save Results**: Download CSV immediately after completion

## Next Steps

- Integrate with your analysis pipeline
- Set up scheduled scraping
- Add more news sources
- Customize deduplication thresholds
- Build dashboards with the data

## Support

For issues or questions:
1. Check the logs in the web interface
2. Review this guide
3. Check `MULTI_SOURCE_SCRAPING_GUIDE.md` for technical details
4. Review the code in `scraper/` directory
