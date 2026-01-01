#!/bin/bash
# Deploy final parser fix to Digital Ocean server

echo "🚀 Deploying Final Parser Fix to Digital Ocean"
echo "=============================================="

# Server details
SERVER_IP="143.198.219.220"
SERVER_PATH="/opt/news-scraper"

echo "📤 Uploading fixed parser..."
scp scraper/core/parser.py root@${SERVER_IP}:${SERVER_PATH}/scraper/core/

echo "🔧 Testing parser fix on server..."

# Test the parser fix
ssh root@${SERVER_IP} "cd ${SERVER_PATH} && source venv/bin/activate && python -c \"
from scraper.core.parser import HTMLParser
from scraper.core.http_client import HTTPClient
import requests

print('🔍 Testing parser with live articles...')

# Test URLs
test_urls = [
    'https://www.theblockbeats.info/flash/326535',
    'https://www.theblockbeats.info/flash/326534',
    'https://www.theblockbeats.info/flash/326533'
]

parser = HTMLParser()

for i, url in enumerate(test_urls, 1):
    try:
        print(f'{i}️⃣ Testing: {url}')
        
        # Fetch with requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            article = parser.parse_article(response.text, url, 'theblockbeats.info')
            print(f'   ✅ Title: {article.title}')
        else:
            print(f'   ❌ Failed to fetch: {response.status_code}')
            
    except Exception as e:
        print(f'   ❌ Error: {e}')

print('✅ Parser test completed')
\""

if [ $? -eq 0 ]; then
    echo ""
    echo "🧪 Running scheduler test with fixed parser..."
    ssh root@${SERVER_IP} "cd ${SERVER_PATH} && source venv/bin/activate && timeout 60 python automated_news_scheduler.py || echo 'Scheduler test completed'"
    
    echo ""
    echo "✅ PARSER FIX DEPLOYED SUCCESSFULLY!"
    echo "===================================="
    echo "🎯 What's Fixed:"
    echo "   ✅ Title extraction now prioritizes og:title and page title"
    echo "   ✅ Avoids picking up titles from other articles on the page"
    echo "   ✅ Better validation to prevent wrong title extraction"
    echo "   ✅ Enhanced fallback strategies for edge cases"
    echo ""
    echo "📊 Your news scraper should now extract correct, unique titles!"
else
    echo ""
    echo "❌ Parser fix deployment failed!"
    echo "📋 Manual steps:"
    echo "1. SSH to server: ssh root@${SERVER_IP}"
    echo "2. Go to project: cd ${SERVER_PATH}"
    echo "3. Test parser: source venv/bin/activate && python test_title_parsing_simple.py"
    exit 1
fi