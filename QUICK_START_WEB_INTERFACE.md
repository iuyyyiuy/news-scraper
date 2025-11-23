# Quick Start: Multi-Source Web Interface

## 🚀 Start the Server

```bash
python test_web_interface_multi_source.py
```

Then open: **http://localhost:8000**

## 📝 Configure Your Search

### 1. Time Range
```
最近几天: 7
```
(Scrape last 7 days)

### 2. Keywords
```
BTC, Bitcoin, 比特币, 安全, 黑客
```
(Comma-separated keywords)

### 3. Select Sources
```
✓ BlockBeats (区块律动)
✓ Jinse (金色财经)
✓ PANews
```
(Check the sources you want)

### 4. Article Limit
```
每个来源检查文章数量上限: 50
```
(Check 50 articles per source)

### 5. Deduplication
```
✓ 启用智能去重
```
(Remove duplicate articles)

## 🎯 Start Scraping

Click **"开始爬取"** button

## 📊 Monitor Progress

### View All Logs
Click **"全部"** tab to see combined logs from all sources

### View Per-Source Logs
Click source tabs to see logs for specific sources:
- **BlockBeats** - BlockBeats logs only
- **Jinse** - Jinse logs only
- **PANews** - PANews logs only

### Log Colors
- 🔵 **Blue (Info)**: General information
- 🟢 **Green (Success)**: Successfully scraped articles
- 🟣 **Purple (Progress)**: Progress updates
- ⚪ **Gray (Filtered)**: Filtered out articles
- 🟠 **Orange (Warning)**: Warnings
- 🔴 **Red (Error)**: Errors

## 📥 Download Results

When complete, click **"📥 下载CSV文件"**

CSV includes:
- 发布日期 (Publication date)
- 标题 (Title)
- 正文内容 (Body text)
- 链接 (URL with source)
- 匹配关键词 (Matched keywords)

## 🔄 Start New Search

Click **"🔍 开始新搜索"** to start over

## 💡 Tips

### Fast Search (Testing)
```
Time: 1-2 days
Articles: 20 per source
Sources: 1-2 sources
```

### Normal Search (Production)
```
Time: 3-7 days
Articles: 50 per source
Sources: All 3 sources
Dedup: ✓ Enabled
```

### Deep Search (Comprehensive)
```
Time: 14-30 days
Articles: 100-200 per source
Sources: All 3 sources
Dedup: ✓ Enabled
```

## ⚠️ Common Issues

### No articles found
- Try broader keywords
- Increase time range
- Check different sources

### Too slow
- Reduce article limit
- Reduce time range
- Use fewer sources

### Source not working
- Check that source's log tab
- Look for error messages
- Try other sources

## 📚 More Info

- **User Guide**: `WEB_INTERFACE_MULTI_SOURCE_GUIDE.md`
- **Technical Details**: `MULTI_SOURCE_SCRAPING_GUIDE.md`
- **Implementation**: `WEB_INTERFACE_UPDATE_SUMMARY.md`
