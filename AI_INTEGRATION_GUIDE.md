# AI Content Analysis Integration Guide

## Overview

The news scraper now includes AI-powered content analysis using DeepSeek API to solve two key problems:

1. **Inaccurate Keyword Matching**: Articles like the Bitcoin price example that don't truly relate to "合规" (compliance)
2. **Duplicate Content Detection**: Identifying articles with 90%+ similar content

## Setup Instructions

### 1. Get DeepSeek API Key
- Visit: https://platform.deepseek.com/
- Sign up and get your API key
- The API is cost-effective for content analysis tasks

### 2. Configure API Key
Choose one of these methods:

**Option A: Add to .env file (Recommended)**
```bash
echo 'DEEPSEEK_API_KEY=your-actual-api-key-here' >> .env
```

**Option B: Environment variable**
```bash
export DEEPSEEK_API_KEY='your-actual-api-key-here'
```

**Option C: Shell profile**
```bash
echo 'export DEEPSEEK_API_KEY="your-actual-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Test the Integration
```bash
python test_ai_analyzer.py
```

## How It Works

### 1. **Intelligent Keyword Relevance Analysis**

The AI analyzes each article to determine if it's truly relevant to the matched keywords:

```python
# Example: Bitcoin price article matched "合规" keyword
title = "Coinbase比特币溢价指数已连续8日处于正溢价"
content = "据 Coinglass 数据，Coinbase 比特币溢价指数..."
keywords = ["合规"]

# AI Analysis Result:
{
    "is_relevant": false,
    "relevance_score": 15,  # Low score = not relevant
    "explanation": "Article discusses Bitcoin price metrics, not compliance issues"
}
```

### 2. **Duplicate Content Detection**

The AI identifies articles that are substantially similar (>90% content overlap):

```python
# Example: Two articles about the same USDT regulatory news
new_article = "USDT获阿布扎比监管认定为「法币参考代币」"
existing_article = "USDT在阿布扎比获得监管认可"

# AI Analysis Result:
{
    "is_duplicate": true,
    "similarity_score": 95,
    "explanation": "Both articles report the same USDT regulatory approval in Abu Dhabi"
}
```

### 3. **Integration with Scraper**

The AI analysis is automatically integrated into the scraping workflow:

1. **Articles are scraped** using existing keyword matching
2. **AI analyzes relevance** for each matched article
3. **AI detects duplicates** against recently processed articles
4. **Only relevant, non-duplicate articles** are stored in the database

## Error Detection & Monitoring

### 1. **Execution Error Detection**

Run this command to check for recent errors:
```bash
python check_system_status.py
```

This will show:
- ❌ Recent errors and critical issues
- 📊 Latest session statistics
- ⚠️ Low success rate warnings
- ✅ System health status

### 2. **Monitoring Dashboard**

Access the monitoring page at: `http://localhost:8000/monitoring`

Features:
- Real-time system health indicators
- Alert log filtering by severity
- Session history with performance metrics
- Error tracking and analysis

### 3. **Alert Logging**

The system now logs all operations with detailed context:

```json
{
    "timestamp": "2025-12-10T06:23:49.433176+00:00",
    "level": "ERROR",
    "component": "ScrapingOperation", 
    "message": "Poor success rate scraping BlockBeats",
    "details": {
        "source": "BlockBeats",
        "articles_found": 24,
        "articles_stored": 1,
        "success_rate_percent": 4.2
    }
}
```

## Benefits

### ✅ **Improved Accuracy**
- Filters out irrelevant articles that only match keywords superficially
- Example: Bitcoin price articles won't be stored as "compliance" news

### ✅ **Duplicate Prevention**
- Detects semantic similarity, not just exact matches
- Prevents storing multiple versions of the same story

### ✅ **Better Monitoring**
- Comprehensive error detection and alerting
- Real-time system health monitoring
- Detailed performance metrics

### ✅ **Fallback Protection**
- If AI API is unavailable, falls back to basic keyword matching
- System continues to function even without AI analysis

## Performance Impact

- **AI Analysis**: ~1-2 seconds per article
- **Batch Processing**: Analyzes multiple articles efficiently
- **Cost**: Very low cost per API call with DeepSeek
- **Fallback**: Zero impact if AI is disabled

## Testing the System

### 1. Test AI Analysis
```bash
python test_ai_analyzer.py
```

### 2. Test Full Scraper with AI
```bash
python test_scraper_now.py
```

### 3. Check System Status
```bash
python check_system_status.py
```

### 4. View Monitoring Dashboard
```bash
# Start web server
python -c "import uvicorn; from scraper.web_api import app; uvicorn.run(app, host='0.0.0.0', port=8000)"

# Visit: http://localhost:8000/monitoring
```

## Configuration Options

The AI analyzer can be configured in `scraper/core/ai_content_analyzer.py`:

- **Relevance Threshold**: Minimum score for article relevance (default: 40/100)
- **Duplicate Threshold**: Minimum similarity for duplicate detection (default: 90%)
- **API Timeout**: Request timeout for DeepSeek API (default: 30 seconds)
- **Batch Size**: Number of articles to compare for duplicates (default: 5)

## Troubleshooting

### Common Issues:

1. **API Key Not Working**
   - Check key format and permissions
   - Verify account has API access
   - Test with `python test_ai_analyzer.py`

2. **High API Costs**
   - Monitor usage in DeepSeek dashboard
   - Adjust batch sizes if needed
   - Consider rate limiting for high-volume scraping

3. **AI Analysis Errors**
   - Check alert logs for detailed error messages
   - System will fall back to basic matching
   - Verify network connectivity to DeepSeek API

The system is designed to be robust and will continue functioning even if AI analysis fails, ensuring your news scraping remains reliable.