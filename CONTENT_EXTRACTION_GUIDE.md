# Content Extraction Guide

## Overview
This guide shows the improved content extraction structure for your news scraper, based on your example content. The parser now extracts clean, structured content without unwanted footer elements.

## What to Extract

### 1. Title
- **Source**: HTML `<title>` tag, `<h1>`, or meta tags
- **Example**: "新币ELONREAPER：马斯克化身「监管死神」横扫官僚主义"
- **Method**: `_extract_title()` with fallback logic

### 2. Publication Date & Time
- **Source**: Content text, meta tags, or datetime attributes
- **Example**: "2025-12-09 05:56"
- **Patterns Supported**:
  - `2025-12-09 05:56` (full datetime)
  - `2025-12-09` (date only)
  - `BlockBeats 消息，11 月 11 日` (Chinese format)
  - `11月11日` (short Chinese format)
- **Method**: `_extract_date_from_body()` with comprehensive patterns

### 3. Source Information
- **Source**: Content text analysis
- **Example**: "Trend News" (extracted from "据 Trend News 监测")
- **Patterns Supported**:
  - `据 [SOURCE] 监测`
  - `来源：[SOURCE]`
  - `据 [SOURCE] 报道`
  - `BlockBeats 消息` (default to BlockBeats)
- **Method**: `_extract_source_from_content()`

### 4. Clean Main Content
- **Source**: Article body with footer removal
- **Example**: Core article text without "AI 解读", "展开", "原文链接", etc.
- **Method**: `_extract_clean_content()` with comprehensive footer filtering

## How Extraction Works

### Content Cleaning Process

1. **Footer Removal**: Automatically removes unwanted elements:
   ```python
   footer_markers = [
       'AI 解读',
       '展开', 
       '原文链接',
       '举报',
       '纠错/举报',
       '本平台现已全面集成',
       '热门文章',
       'farcaster评论',
       'The content is also unclear',
       'are unneeed information',
       '登录 后发表评论'
   ]
   ```

2. **Duplicate Line Removal**: Removes repetitive content common in scraped text

3. **Text Normalization**: 
   - Normalizes whitespace and paragraph breaks
   - Removes extra spaces and tabs
   - Cleans up formatting artifacts

### Date Extraction Process

The parser uses multiple patterns to extract dates:

```python
# Pattern 1: Full datetime
r'(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{1,2})'

# Pattern 2: BlockBeats format
r'BlockBeats\s*消息\s*，\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日'

# Pattern 3: Standard date
r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})'

# Pattern 4: Chinese short format
r'(\d{1,2})\s*月\s*(\d{1,2})\s*日'
```

### Source Extraction Process

Identifies source information from content:

```python
# Primary pattern: "据 SOURCE 监测"
r'据\s+([^监测]+?)\s*监测'

# Fallback patterns
r'来源[:：]\s*([^\n,，。]+)'
r'消息来源[:：]\s*([^\n,，。]+)'
r'据\s+([^报道]+?)\s*报道'
```

## Example Results

### Before (Raw Content)
```
新币ELONREAPER：马斯克化身「监管死神」横扫官僚主义 2025-12-09 05:56 据 Trend News 监测，知名加密 kol @cb_doge 近期发布一张爆火 meme... AI 解读 首先，这本质上是一个典型的meme币叙事驱动案例... 展开 原文链接 举报 纠错/举报 本平台现已全面集成Farcaster协议...
```

### After (Clean Extraction)
```
Title: 新币ELONREAPER：马斯克化身「监管死神」横扫官僚主义
Date: 2025-12-09 05:56:00
Source: Trend News
Content: 据 Trend News 监测，知名加密 kol @cb_doge 近期发布一张爆火 meme，Elon Musk 被塑造成手持镰刀、笑容诡异的死神形象...以监管死神为核心的代币 $ELONREAPER 也在链上响应，15 个同名代币在 1 小时内成交额达 230k。
```

## Usage in Your Scraper

The improved parser is already integrated into your existing scraper structure:

1. **Article Parsing**: `parse_article()` method uses all extraction functions
2. **Content Cleaning**: Automatically applied to all extracted content
3. **Metadata Extraction**: Date and source information extracted from content
4. **Fallback Logic**: Multiple extraction strategies for robustness

## Testing

Run the test script to verify extraction:

```bash
python test_improved_parser.py
```

This will show:
- Clean content extraction results
- Date extraction accuracy
- Source identification
- Content structure analysis
- Before/after comparison

## Key Improvements

1. **Cleaner Content**: Removes all footer noise and repetitive elements
2. **Better Date Parsing**: Supports multiple date formats including Chinese
3. **Source Detection**: Automatically identifies news sources from content
4. **Robust Extraction**: Multiple fallback strategies for each data type
5. **Structured Output**: Consistent, clean data structure for all articles

The parser now extracts exactly the type of clean, structured content you need for your news database.