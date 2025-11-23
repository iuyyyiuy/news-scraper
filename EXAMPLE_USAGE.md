# Example Usage Guide

This guide shows real-world examples of using the News Scraper for different scenarios.

## Scenario 1: Marketing Team Needs Competitor News

**Goal**: Track competitor mentions in tech news over the past month.

### Using Web Interface

1. Start the server:
   ```bash
   python run_web_server.py
   ```

2. Open browser to `http://localhost:5000`

3. Fill in the form:
   - **Start Date**: 2025-10-13 (30 days ago)
   - **End Date**: 2025-11-13 (today)
   - **Keywords**: `CompanyX, CompanyY, CompanyZ`
   - **Max Articles**: 100

4. Click "Start Scraping"

5. Wait 2-3 minutes

6. Download CSV file

7. Open in Excel and filter by company name

**Result**: CSV file with all news articles mentioning your competitors.

---

## Scenario 2: Research Team Needs Academic News

**Goal**: Collect articles about AI research published this week.

### Using Web Interface

1. Start server (if not already running)

2. Open `http://localhost:5000`

3. Fill in:
   - **Start Date**: 2025-11-06 (7 days ago)
   - **End Date**: 2025-11-13 (today)
   - **Keywords**: `artificial intelligence, machine learning, deep learning, neural networks`
   - **Max Articles**: 50

4. Start scraping

5. Download results

**Result**: Recent AI research news articles.

---

## Scenario 3: Investment Team Needs Market News

**Goal**: Daily cryptocurrency market news for morning briefing.

### Using Command Line (for automation)

Create a script `daily_crypto_news.sh`:

```bash
#!/bin/bash

# Get today's date and 7 days ago
END_DATE=$(date +%Y-%m-%d)
START_DATE=$(date -d '7 days ago' +%Y-%m-%d)

# Run scraper
python -m scraper.main \
  --url https://cryptonews.com \
  --keywords "bitcoin" "ethereum" "crypto market" \
  --days 7 \
  --output "crypto_news_${END_DATE}.csv" \
  --output-format csv \
  --max-articles 30

echo "Crypto news saved to crypto_news_${END_DATE}.csv"
```

Run daily:
```bash
chmod +x daily_crypto_news.sh
./daily_crypto_news.sh
```

**Result**: Automated daily crypto news collection.

---

## Scenario 4: PR Team Monitors Brand Mentions

**Goal**: Track brand mentions across multiple news sources.

### Using Web Interface with Multiple Searches

**Search 1: Direct Brand Mentions**
- Keywords: `OurBrand, OurProduct`
- Date Range: Last 7 days
- Download as: `brand_direct_mentions.csv`

**Search 2: Industry Category**
- Keywords: `fintech, financial technology, digital banking`
- Date Range: Last 7 days
- Download as: `industry_news.csv`

**Search 3: Executive Mentions**
- Keywords: `CEO Name, CTO Name, Company Spokesperson`
- Date Range: Last 7 days
- Download as: `executive_mentions.csv`

**Result**: Three CSV files covering different aspects of brand presence.

---

## Scenario 5: Content Team Needs Topic Research

**Goal**: Research content ideas for blog posts.

### Using Web Interface

**Topic 1: Blockchain Technology**
```
Start Date: 2025-10-01
End Date: 2025-11-13
Keywords: blockchain, distributed ledger, smart contracts
Max Articles: 50
```

**Topic 2: Cybersecurity**
```
Start Date: 2025-10-01
End Date: 2025-11-13
Keywords: cybersecurity, data breach, ransomware, hacking
Max Articles: 50
```

**Topic 3: Cloud Computing**
```
Start Date: 2025-10-01
End Date: 2025-11-13
Keywords: cloud computing, AWS, Azure, serverless
Max Articles: 50
```

**Result**: Three CSV files with articles on different topics for content inspiration.

---

## Scenario 6: Analyst Needs Historical Data

**Goal**: Analyze news trends over the past quarter.

### Using Command Line for Large Dataset

```bash
# Q4 2025 news about electric vehicles
python -m scraper.main \
  --url https://technews.com \
  --keywords "electric vehicle" "EV" "Tesla" "battery technology" \
  --days 90 \
  --output ev_news_q4_2025.csv \
  --output-format csv \
  --max-articles 500 \
  --delay 3.0
```

**Note**: Increased delay to 3 seconds to be respectful to the server.

**Result**: Large dataset for trend analysis.

---

## Scenario 7: Multiple Team Members Using Simultaneously

**Setup for Team Use**

1. **Developer starts server with network access:**
   ```bash
   python run_web_server.py --host 0.0.0.0 --port 5000
   ```

2. **Find your computer's IP address:**
   ```bash
   # On Mac/Linux
   ifconfig | grep "inet "
   
   # On Windows
   ipconfig
   ```
   Example IP: `192.168.1.100`

3. **Share URL with team:**
   ```
   http://192.168.1.100:5000
   ```

4. **Team members access from their computers:**
   - Marketing: Searches for competitor news
   - PR: Searches for brand mentions
   - Research: Searches for industry trends
   - All simultaneously!

**Result**: Multiple team members can use the tool at the same time.

---

## Scenario 8: API Integration

**Goal**: Integrate scraper into existing workflow automation.

### Using the REST API

```python
import requests
import time

# Start a scraping session
response = requests.post('http://localhost:5000/api/scrape', json={
    'start_date': '2025-11-01',
    'end_date': '2025-11-13',
    'keywords': ['technology', 'innovation'],
    'max_articles': 50
})

session_id = response.json()['session_id']
print(f"Session started: {session_id}")

# Poll for completion
while True:
    status = requests.get(f'http://localhost:5000/api/status/{session_id}')
    data = status.json()
    
    print(f"Status: {data['status']}, Articles: {data['articles_scraped']}")
    
    if data['status'] in ['completed', 'failed']:
        break
    
    time.sleep(5)

# Download results
if data['status'] == 'completed':
    csv_response = requests.get(f'http://localhost:5000/api/download/{session_id}')
    with open('results.csv', 'wb') as f:
        f.write(csv_response.content)
    print("Results downloaded!")
```

**Result**: Automated scraping integrated into your Python workflow.

---

## Scenario 9: Scheduled Weekly Reports

**Goal**: Automatically generate weekly news reports.

### Using Cron (Linux/Mac)

1. Create script `weekly_report.sh`:
   ```bash
   #!/bin/bash
   
   WEEK=$(date +%Y-W%V)
   START_DATE=$(date -d 'monday last week' +%Y-%m-%d)
   END_DATE=$(date -d 'sunday last week' +%Y-%m-%d)
   
   python -m scraper.main \
     --url https://industrynews.com \
     --keywords "industry trends" "market analysis" \
     --days 7 \
     --output "weekly_report_${WEEK}.csv" \
     --output-format csv \
     --max-articles 100
   
   # Email the report (requires mail setup)
   echo "Weekly news report attached" | mail -s "Weekly Report ${WEEK}" \
     -a "weekly_report_${WEEK}.csv" team@company.com
   ```

2. Add to crontab:
   ```bash
   # Run every Monday at 9 AM
   0 9 * * 1 /path/to/weekly_report.sh
   ```

**Result**: Automated weekly reports delivered to your team.

---

## Scenario 10: Emergency News Monitoring

**Goal**: Quickly check for breaking news about a specific event.

### Using Web Interface (Fastest)

1. Open `http://localhost:5000`

2. Quick search:
   - **Start Date**: Today
   - **End Date**: Today
   - **Keywords**: `breaking news, urgent, alert, [specific event]`
   - **Max Articles**: 20

3. Start scraping (should complete in under 1 minute)

4. Download and review immediately

**Result**: Fast access to breaking news articles.

---

## Best Practices

### For Web Interface Users

1. **Start Broad, Then Narrow**
   - First search: General keywords, longer date range
   - Second search: Specific keywords, shorter date range

2. **Use Descriptive Keywords**
   - Good: `electric vehicle charging infrastructure`
   - Bad: `car stuff`

3. **Organize Your Downloads**
   - Create folders by date or topic
   - Rename files with descriptive names
   - Keep a log of what you searched for

### For Command Line Users

1. **Use Configuration Files**
   - Save common searches as JSON configs
   - Version control your configs
   - Share configs with team

2. **Respect Rate Limits**
   - Use `--delay 2.0` or higher
   - Don't scrape the same site too frequently
   - Consider the website's resources

3. **Log Everything**
   - Use `--log-file scraper.log`
   - Review logs for errors
   - Monitor for changes in website structure

### For Developers

1. **Monitor Server Resources**
   - Check CPU and memory usage
   - Limit concurrent sessions if needed
   - Set up alerts for failures

2. **Backup Data**
   - Regularly backup scraped data
   - Keep logs for troubleshooting
   - Document any custom selectors

3. **Update Selectors**
   - Websites change their HTML structure
   - Test scraper regularly
   - Update selectors as needed

---

## Troubleshooting Examples

### Problem: No Articles Found

**Scenario**: Searched for "quantum computing" but got 0 results.

**Solutions**:
1. Try broader keywords: `quantum, computing, qubits`
2. Extend date range: Last 30 days instead of 7
3. Check if target website has articles on this topic
4. Try alternative keywords: `quantum technology, quantum research`

### Problem: Too Many Articles

**Scenario**: Got 500 articles but only need recent ones.

**Solutions**:
1. Shorten date range: Last 7 days instead of 30
2. Use more specific keywords: `quantum computing breakthrough` instead of just `quantum`
3. Lower max articles: Set to 50 instead of 500
4. Filter CSV in Excel after download

### Problem: Slow Scraping

**Scenario**: Scraping is taking too long.

**Solutions**:
1. Reduce max articles
2. Shorten date range
3. Check your internet connection
4. Increase request delay (paradoxically, this can help avoid rate limiting)

---

## Tips for Different Industries

### Finance/Investment
- Keywords: Company tickers, financial terms, market indicators
- Date Range: Recent (last 7-14 days)
- Frequency: Daily or weekly

### Marketing/PR
- Keywords: Brand names, product names, competitor names
- Date Range: Ongoing monitoring (last 7 days)
- Frequency: Daily

### Research/Academic
- Keywords: Technical terms, research topics, author names
- Date Range: Longer periods (30-90 days)
- Frequency: Weekly or monthly

### Legal/Compliance
- Keywords: Regulatory terms, company names, legal issues
- Date Range: As needed for cases
- Frequency: Ad-hoc

---

**Need more examples?** Check the [Web Interface Guide](WEB_INTERFACE_GUIDE.md) for technical details.
