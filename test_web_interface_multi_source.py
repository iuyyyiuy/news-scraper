"""
Test the web interface with multi-source scraping.

Run this script and then open http://localhost:8000 in your browser.
"""
import uvicorn
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    print("=" * 60)
    print("Starting Multi-Source News Scraper Web Interface")
    print("=" * 60)
    print()
    print("🌐 Open your browser and go to: http://localhost:8000")
    print()
    print("Features:")
    print("  ✅ Multi-source scraping (BlockBeats, Jinse, PANews)")
    print("  ✅ Per-source log tabs")
    print("  ✅ Smart deduplication")
    print("  ✅ Real-time progress updates")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "scraper.web_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
