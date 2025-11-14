# 📰 Crypto News Scraper

A web-based news scraper for cryptocurrency news from multiple sources.

## Features

- 🌐 Web interface for easy scraping
- 📊 Multiple news sources support
- 💾 Export to CSV
- 🔄 Real-time scraping with progress updates
- 🎨 Clean, modern UI

## Supported News Sources

- BlockBeats
- More sources coming soon...

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the web server
python run_web_server.py

# Open browser
http://localhost:8000
```

### Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Fork this repository
2. Sign up at [Render.com](https://render.com)
3. Create a new Web Service
4. Connect your repository
5. Deploy!

## Tech Stack

- **Backend**: FastAPI + Uvicorn
- **Scraping**: BeautifulSoup4 + Requests
- **Frontend**: HTML + JavaScript (Vanilla)

## API Endpoints

- `GET /` - Web interface
- `GET /health` - Health check
- `POST /scrape` - Start scraping
- `GET /sessions/{session_id}` - Get scraping results

## License

MIT

## Author

Created with ❤️ for the crypto community
