# Web Interface Quick Start Guide

## For Non-Technical Team Members

This guide will help you use the News Scraper web interface to collect news articles without any coding.

## Step 1: Start the Server

Ask your developer to run this command:

```bash
python run_web_server.py
```

They will give you a URL like: `http://localhost:5000`

## Step 2: Open the Web Interface

1. Open your web browser (Chrome, Firefox, Safari, or Edge)
2. Type or paste the URL in the address bar
3. Press Enter

You should see a purple page with "📰 News Scraper" at the top.

## Step 3: Fill Out the Form

### Date Range

1. **Start Date**: Click the first date field
   - A calendar will appear
   - Select the earliest date you want articles from
   - Example: November 1, 2025

2. **End Date**: Click the second date field
   - Select the latest date you want articles from
   - Example: November 13, 2025

**Tip**: The dates are pre-filled with the last 7 days by default.

### Keywords

1. Click in the "Keywords" field
2. Type words you want to search for
3. Separate multiple words with commas
4. Example: `crypto, bitcoin, blockchain`

**Important**: You must enter at least one keyword!

### Optional Settings

You can usually skip these:

- **Target Website URL**: Leave empty to use the default news source
- **Maximum Articles**: Leave empty to get up to 50 articles

## Step 4: Start Scraping

1. Click the big purple "Start Scraping" button
2. The form will disappear
3. You'll see a spinning circle
4. A number will show how many articles have been found
5. This usually takes 1-5 minutes depending on how many articles match

**What's happening**: The system is searching news websites for articles that:
- Were published between your start and end dates
- Contain at least one of your keywords

## Step 5: Download Your Results

When scraping is complete:

1. You'll see a green checkmark ✅
2. Statistics will show:
   - How many articles were found
   - How long it took
3. A green "📥 Download CSV File" button will appear
4. Click the button
5. The file will download to your Downloads folder

## Step 6: Open the CSV File

1. Go to your Downloads folder
2. Find the file named like: `news_articles_20251113_143022.csv`
3. Double-click to open in Excel or Google Sheets

### What's in the CSV File?

| Column | What It Contains |
|--------|------------------|
| publication_date | When the article was published |
| title | The article headline |
| body_text | The full article text |
| url | Link to the original article |
| matched_keywords | Which keywords were found |

## Step 7: Start a New Search

1. Click the "🔍 Start New Search" button
2. The form will reappear
3. Enter new dates and keywords
4. Repeat the process

## Common Questions

### Q: How do I know if it's working?

**A**: You'll see the article counter increasing. If it stays at 0 for more than a minute, the search might not be finding matches.

### Q: What if no articles are found?

**A**: Try:
- Making your date range longer (more days)
- Using more general keywords
- Using fewer keywords (just 1 or 2)

### Q: Can I search for multiple topics at once?

**A**: Yes! Just separate them with commas. Example: `crypto, stocks, economy`

### Q: How many articles can I get?

**A**: By default, up to 50 articles. Your developer can increase this limit if needed.

### Q: Can I use this on my phone?

**A**: Yes! The interface works on phones and tablets too.

### Q: What if I get an error?

**A**: 
1. Check that your start date is before your end date
2. Make sure you entered at least one keyword
3. Try clicking "Start New Search" and try again
4. If it still doesn't work, contact your developer

### Q: Can multiple people use this at the same time?

**A**: Yes! Multiple team members can use it simultaneously.

### Q: Where is the data stored?

**A**: The CSV file is downloaded to your computer. The server keeps a temporary copy for 24 hours, then automatically deletes it.

## Tips for Best Results

1. **Be Specific with Keywords**
   - Good: `bitcoin price, cryptocurrency market`
   - Too broad: `news, article`

2. **Use Reasonable Date Ranges**
   - Good: Last 7-30 days
   - May be slow: Last 365 days

3. **Check Your Downloads**
   - Files are named with date and time
   - Keep them organized in folders by topic or date

4. **Combine Keywords Smartly**
   - Use related terms: `AI, artificial intelligence, machine learning`
   - Avoid unrelated terms in one search

## Example Searches

### Example 1: Cryptocurrency News (Last Week)
- **Start Date**: 7 days ago
- **End Date**: Today
- **Keywords**: `crypto, bitcoin, ethereum`
- **Expected Results**: 10-50 articles about cryptocurrency

### Example 2: Tech Industry News (Last Month)
- **Start Date**: 30 days ago
- **End Date**: Today
- **Keywords**: `technology, startup, innovation`
- **Expected Results**: 20-50 articles about tech industry

### Example 3: Specific Company News
- **Start Date**: 14 days ago
- **End Date**: Today
- **Keywords**: `Apple, iPhone, iOS`
- **Expected Results**: 5-30 articles about Apple

## Need Help?

If you're stuck or something isn't working:

1. Take a screenshot of what you see
2. Note what you were trying to do
3. Contact your developer or IT support
4. They can check the server logs to see what happened

## Security Note

- The web interface is usually only accessible from your computer
- If your developer set it up for team access, only use it on your work network
- Don't share the URL outside your organization
- The CSV files contain public news articles, but handle them according to your company's data policies

---

**Happy Scraping!** 🎉

If you have suggestions for improving this guide, let your developer know!
