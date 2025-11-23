# News Sources Configuration Guide

This guide helps you configure the scraper for different news websites.

## Quick Setup

Edit `scraper/web_api.py` and change the `target_url` in `DEFAULT_CONFIG`:

```python
DEFAULT_CONFIG = {
    "target_url": "https://your-news-site.com/",  # Change this
    "max_articles": 50,
    "request_delay": 2.0,
    "timeout": 30,
    "max_retries": 3,
    "selectors": {}
}
```

## Recommended News Sources

### 1. CoinDesk (Cryptocurrency)

**URL**: `https://www.coindesk.com/`

**Best for**: Cryptocurrency, blockchain, bitcoin, ethereum, DeFi

**Example Keywords**:
- `bitcoin, BTC, cryptocurrency`
- `ethereum, ETH, smart contracts`
- `blockchain, DeFi, NFT`

**Configuration**:
```python
"target_url": "https://www.coindesk.com/"
```

---

### 2. TechCrunch (Technology & Startups)

**URL**: `https://techcrunch.com/`

**Best for**: Startups, technology, venture capital, AI

**Example Keywords**:
- `startup, funding, venture capital`
- `artificial intelligence, AI, machine learning`
- `technology, innovation, product launch`

**Configuration**:
```python
"target_url": "https://techcrunch.com/"
```

---

### 3. Reuters (General News)

**URL**: `https://www.reuters.com/`

**Best for**: Business, politics, world news, markets

**Example Keywords**:
- `business, economy, markets`
- `politics, government, policy`
- `world news, international`

**Configuration**:
```python
"target_url": "https://www.reuters.com/"
```

---

### 4. The Verge (Tech & Science)

**URL**: `https://www.theverge.com/`

**Best for**: Technology, gadgets, science, culture

**Example Keywords**:
- `smartphone, gadget, device`
- `science, research, space`
- `gaming, entertainment, streaming`

**Configuration**:
```python
"target_url": "https://www.theverge.com/"
```

---

### 5. Hacker News (Tech Community)

**URL**: `https://news.ycombinator.com/`

**Best for**: Programming, startups, tech discussions

**Example Keywords**:
- `programming, coding, development`
- `startup, YC, founder`
- `open source, GitHub, software`

**Configuration**:
```python
"target_url": "https://news.ycombinator.com/"
```

---

### 6. Cointelegraph (Crypto News)

**URL**: `https://cointelegraph.com/`

**Best for**: Cryptocurrency news and analysis

**Example Keywords**:
- `crypto, cryptocurrency, digital currency`
- `bitcoin, altcoin, token`
- `blockchain, Web3, metaverse`

**Configuration**:
```python
"target_url": "https://cointelegraph.com/"
```

---

### 7. Ars Technica (Technology)

**URL**: `https://arstechnica.com/`

**Best for**: In-depth technology coverage

**Example Keywords**:
- `technology, computing, hardware`
- `security, privacy, encryption`
- `science, space, research`

**Configuration**:
```python
"target_url": "https://arstechnica.com/"
```

---

### 8. BBC News (World News)

**URL**: `https://www.bbc.com/news`

**Best for**: International news, politics, business

**Example Keywords**:
- `world news, international, global`
- `politics, government, election`
- `business, economy, finance`

**Configuration**:
```python
"target_url": "https://www.bbc.com/news"
```

---

## Testing a News Source

Before using with your team, test the configuration:

1. **Update the URL** in `scraper/web_api.py`

2. **Start the server**:
   ```bash
   python run_web_server.py
   ```

3. **Open browser**: `http://localhost:5000`

4. **Test search**:
   - Date Range: Last 7 days
   - Keywords: Common terms for that site
   - Max Articles: 10 (for quick test)

5. **Check results**:
   - Did it find articles?
   - Are titles extracted correctly?
   - Is the body text complete?
   - Are dates parsed correctly?

## Custom CSS Selectors (Advanced)

If the default scraper doesn't work well, you can add custom CSS selectors:

```python
DEFAULT_CONFIG = {
    "target_url": "https://your-site.com/",
    "max_articles": 50,
    "request_delay": 2.0,
    "timeout": 30,
    "max_retries": 3,
    "selectors": {
        "article_links": "a.article-link",      # Links to articles
        "title": "h1.article-title",            # Article title
        "date": "time.published-date",          # Publication date
        "author": ".author-name",               # Author name
        "body": ".article-content"              # Article body
    }
}
```

### How to Find Selectors

1. **Open the news website** in Chrome/Firefox
2. **Right-click** on an article title → "Inspect"
3. **Look at the HTML** to find the CSS class or tag
4. **Test the selector** in browser console:
   ```javascript
   document.querySelector('h1.article-title')
   ```
5. **Add to configuration** if it works

## Multiple News Sources

If you want to scrape from multiple sources, you can:

### Option 1: Change URL in Web Interface

Users can enter different URLs in the "Target Website URL" field.

### Option 2: Create Multiple Configurations

Create separate config files:

**config_coindesk.json**:
```json
{
  "target_url": "https://www.coindesk.com/",
  "max_articles": 50,
  "request_delay": 2.0
}
```

**config_techcrunch.json**:
```json
{
  "target_url": "https://techcrunch.com/",
  "max_articles": 50,
  "request_delay": 2.0
}
```

Use with CLI:
```bash
python -m scraper.main --config config_coindesk.json --keywords "bitcoin"
python -m scraper.main --config config_techcrunch.json --keywords "startup"
```

## Best Practices

### 1. Respect Rate Limits

- Use `request_delay` of 2-3 seconds
- Don't scrape too frequently
- Be a good internet citizen

### 2. Check robots.txt

Before scraping, check if the site allows it:
```
https://www.example.com/robots.txt
```

Look for:
```
User-agent: *
Disallow: /admin/
Allow: /news/
```

### 3. Monitor for Changes

Websites update their HTML structure. If scraping stops working:
- Check if the site changed its layout
- Update CSS selectors
- Test with a small sample first

### 4. Legal Considerations

- Only scrape publicly available content
- Respect copyright and terms of service
- Don't scrape personal data
- Use data responsibly

## Troubleshooting

### No Articles Found

**Problem**: Scraper runs but finds 0 articles

**Solutions**:
1. Check if URL is correct
2. Try accessing the URL in your browser
3. Check if site requires JavaScript (scraper doesn't support JS)
4. Add custom CSS selectors
5. Check if site blocks scrapers (User-Agent)

### Wrong Content Extracted

**Problem**: Titles or body text are incorrect

**Solutions**:
1. Inspect the HTML structure
2. Add custom CSS selectors
3. Check if site uses dynamic content (JavaScript)

### Rate Limited

**Problem**: Getting 429 or 403 errors

**Solutions**:
1. Increase `request_delay` to 3-5 seconds
2. Reduce `max_articles`
3. Wait before trying again
4. Check if site requires authentication

## Recommended Starting Configuration

For most users, start with **CoinDesk** as it's:
- ✅ Well-structured HTML
- ✅ No JavaScript required
- ✅ Allows scraping (check robots.txt)
- ✅ Good for testing with crypto keywords

```python
DEFAULT_CONFIG = {
    "target_url": "https://www.coindesk.com/",
    "max_articles": 50,
    "request_delay": 2.0,
    "timeout": 30,
    "max_retries": 3,
    "selectors": {}
}
```

## Need Help?

If you're having trouble with a specific news source:

1. Check the site's HTML structure
2. Try with a small sample (max_articles: 5)
3. Check browser console for errors
4. Review the scraper logs
5. Consider if the site requires JavaScript rendering

---

**Happy Scraping!** Remember to always respect website terms of service and rate limits.
