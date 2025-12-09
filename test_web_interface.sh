#!/bin/bash

# Test script for multi-source scraper web interface
# This script helps you test the improvements

echo "============================================================"
echo "Multi-Source Scraper - Web Interface Test"
echo "============================================================"
echo ""

# Check if we're in the right directory
if [ ! -d "/Users/kabellatsang/PycharmProjects/ai_code" ]; then
    echo "❌ Error: ai_code directory not found"
    exit 1
fi

cd /Users/kabellatsang/PycharmProjects/ai_code

echo "📁 Working directory: $(pwd)"
echo ""

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Error: Python not found"
    exit 1
fi

echo "🐍 Python version: $(python --version)"
echo ""

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "✅ Virtual environment found"
    echo "💡 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "⚠️  No virtual environment found"
    echo "💡 Using system Python"
fi

echo ""
echo "============================================================"
echo "Test Options:"
echo "============================================================"
echo ""
echo "1. Test Jinse scraper only (quick test)"
echo "2. Start web interface server"
echo "3. Run full multi-source test"
echo ""
read -p "Choose option (1-3): " option

case $option in
    1)
        echo ""
        echo "🧪 Testing Jinse scraper..."
        echo "------------------------------------------------------------"
        python test_jinse_only.py
        ;;
    2)
        echo ""
        echo "🌐 Starting web interface server..."
        echo "------------------------------------------------------------"
        echo "💡 Open http://localhost:8000 in your browser"
        echo "💡 Press Ctrl+C to stop the server"
        echo ""
        
        if [ -f "run_web_server.py" ]; then
            python run_web_server.py
        elif [ -f "test_web_interface_multi_source.py" ]; then
            python test_web_interface_multi_source.py
        else
            echo "❌ Error: Web server script not found"
            exit 1
        fi
        ;;
    3)
        echo ""
        echo "🧪 Running full multi-source test..."
        echo "------------------------------------------------------------"
        
        # Create a test script
        cat > /tmp/test_multi_source.py << 'EOF'
from datetime import date, timedelta
from scraper.core.config import Config
from scraper.core.storage import CSVDataStore
from scraper.core.multi_source_scraper import MultiSourceScraper

print("=" * 60)
print("Testing Multi-Source Scraper")
print("=" * 60)
print()

# Setup
end_date = date.today()
start_date = end_date - timedelta(days=2)
keywords = ['BTC', 'Bitcoin', '比特币', '以太坊', 'ETH']

print(f"Date range: {start_date} to {end_date}")
print(f"Keywords: {keywords}")
print(f"Will check: 10 articles per source")
print()

# Create config
config = Config(
    target_url="https://www.theblockbeats.info",
    max_articles=10,
    request_delay=1.0,
    output_format="csv",
    output_path="multi_source_test_output.csv"
)

# Create data store
data_store = CSVDataStore("multi_source_test_output.csv")

# Create scraper with detailed logging
def log_callback(message, log_type='info', source=None, show_in_all=True):
    prefix = f"[{source}]" if source else "[ALL]"
    visibility = "📢" if show_in_all else "🔇"
    print(f"{visibility} {prefix} [{log_type.upper()}] {message}")

scraper = MultiSourceScraper(
    config=config,
    data_store=data_store,
    start_date=start_date,
    end_date=end_date,
    keywords_filter=keywords,
    sources=['blockbeats', 'jinse', 'panews'],
    log_callback=log_callback
)

# Run scraper
print("Starting scrape...")
print("-" * 60)
result = scraper.scrape()

# Print results
print()
print("=" * 60)
print("Results:")
print("=" * 60)
print(f"✅ Total articles checked: {result.total_articles_found}")
print(f"✅ Total articles scraped: {result.articles_scraped}")
print(f"❌ Total articles failed: {result.articles_failed}")
print(f"⏱️  Duration: {result.duration_seconds:.2f} seconds")
print()

if result.articles_scraped > 0:
    print(f"✅ SUCCESS! Multi-source scraper is working!")
    print(f"📄 Output saved to: multi_source_test_output.csv")
else:
    print("⚠️  No articles found.")

print("=" * 60)
EOF
        
        python /tmp/test_multi_source.py
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "============================================================"
echo "Test complete!"
echo "============================================================"
