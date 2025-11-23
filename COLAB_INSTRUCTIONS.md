# 📓 Google Colab Instructions

## How to Use the News Scraper in Google Colab

### Step 1: Upload to Google Colab

1. Go to [Google Colab](https://colab.research.google.com/)
2. Click **File** → **Upload notebook**
3. Upload the `news_scraper_colab.ipynb` file
4. Or use this direct link: **File** → **Open notebook** → **GitHub** → Paste your repository URL

### Step 2: Run the Notebook

1. **Run all cells in order** by clicking **Runtime** → **Run all**
2. Or run each cell individually by clicking the ▶️ play button

### Step 3: Configure Your Settings

In **Step 9: Configuration**, modify these settings:

```python
# Maximum number of articles to scrape
MAX_ARTICLES = 20

# Keywords to filter (Chinese & English supported)
KEYWORDS = ["BTC", "ETH", "Bitcoin", "Uniswap", "黑客", "监管"]

# Date filter: only scrape articles from last N days
DAYS_FILTER = 7  # Last 7 days

# Output filename
OUTPUT_FILE = "crypto_news.csv"
```

### Step 4: Run the Scraper

Run **Step 10** to start scraping. You'll see real-time progress:

```
📰 NEWS SCRAPER
======================================================================
Target URL:      https://www.theblockbeats.info/newsflash
Max Articles:    20
Keywords:        BTC, ETH, Bitcoin, Uniswap, 黑客, 监管
Date Filter:     Last 7 days
Output File:     crypto_news.csv
======================================================================

📡 Fetching article listing page...
🔍 Extracting article URLs...
✅ Found 21 article URLs
📝 Processing 20 articles

[1/20] Processing: https://www.theblockbeats.info/flash/319969
   ✅ Scraped: CryptoQuant CEO：若费用开关启动，每年将销毁价值5亿美元UNI...
...
```

### Step 5: Download Results

1. Run **Step 11** to preview results
2. Click the **📁 folder icon** on the left sidebar
3. Find your `crypto_news.csv` file
4. **Right-click** → **Download**

## 📊 Output Format

The CSV file contains these columns:

| Column | Description |
|--------|-------------|
| url | Article URL |
| title | Article title |
| publication_date | Date in YYYY-MM-DD format |
| author | Author name |
| body_text | Full article text |
| scraped_at | When it was scraped |
| source_website | Source domain |
| matched_keywords | Which keywords were found |

## 🎯 Features

✅ **Keyword Filtering**: Only saves articles containing your keywords  
✅ **Date Filtering**: Only scrapes articles from last N days  
✅ **Chinese Support**: Works with Chinese keywords (黑客, 监管, etc.)  
✅ **Auto Date Extraction**: Extracts dates from article text  
✅ **Rate Limiting**: Respects server with 2-second delays  
✅ **Error Handling**: Continues even if some articles fail  

## 💡 Tips

1. **Start Small**: Test with `MAX_ARTICLES = 5` first
2. **Be Respectful**: Don't set `REQUEST_DELAY` below 2 seconds
3. **Multiple Keywords**: Add more keywords to catch more articles
4. **Date Range**: Adjust `DAYS_FILTER` to scrape older/newer articles
5. **Re-run Anytime**: Just modify settings and run Step 10 again

## 🔧 Troubleshooting

**Problem**: "No articles matched your filters"  
**Solution**: Try broader keywords or increase `DAYS_FILTER`

**Problem**: "Failed to scrape" errors  
**Solution**: Normal! Some articles may fail. The scraper continues with others.

**Problem**: Slow scraping  
**Solution**: This is intentional (rate limiting). Don't reduce `REQUEST_DELAY`!

## 📤 Sharing with Teammates

### Option 1: Share the Notebook File
1. Send them the `news_scraper_colab.ipynb` file
2. They upload it to their Google Colab
3. They run it with their own settings

### Option 2: Share via Google Drive
1. Upload notebook to Google Drive
2. Right-click → **Open with** → **Google Colaboratory**
3. Click **Share** button (top right)
4. Share the link with teammates

### Option 3: Share via GitHub
1. Upload `news_scraper_colab.ipynb` to GitHub
2. Share the GitHub URL
3. Teammates can open directly in Colab:
   - Go to [colab.research.google.com](https://colab.research.google.com/)
   - Click **GitHub** tab
   - Paste your repository URL

## 🚀 Quick Start for Teammates

Tell your teammates:

1. Open the notebook in Google Colab
2. Click **Runtime** → **Run all**
3. Wait for Step 9 (Configuration)
4. Modify the keywords and settings
5. Continue running (or re-run Step 10)
6. Download the CSV file from the files panel

That's it! No installation needed! 🎉
