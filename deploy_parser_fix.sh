#!/bin/bash
# Deploy parser fix to Digital Ocean server

echo "🚀 Deploying Parser Fix to Digital Ocean Server"
echo "================================================"

# Server details
SERVER_IP="143.198.219.220"
SERVER_PATH="/opt/news-scraper"

echo "📤 Uploading fixed parser file..."
scp scraper/core/parser.py root@${SERVER_IP}:${SERVER_PATH}/scraper/core/

echo "📤 Uploading test scripts..."
scp test_parser_fix_simple.py root@${SERVER_IP}:${SERVER_PATH}/
scp test_date_parsing_fix.py root@${SERVER_IP}:${SERVER_PATH}/

echo "🔧 Testing parser title fix on server..."
ssh root@${SERVER_IP} "cd ${SERVER_PATH} && source venv/bin/activate && python test_parser_fix_simple.py"

if [ $? -eq 0 ]; then
    echo "✅ Parser title fix working!"
    
    echo "🔧 Testing date parsing fix on server..."
    ssh root@${SERVER_IP} "cd ${SERVER_PATH} && source venv/bin/activate && python test_date_parsing_fix.py"
    
    if [ $? -eq 0 ]; then
        echo "✅ Date parsing fix working!"
        echo "🔄 Restarting scheduler with all fixes..."
        ssh root@${SERVER_IP} "cd ${SERVER_PATH} && source venv/bin/activate && python automated_news_scheduler.py"
    else
        echo "❌ Date parsing fix test failed!"
        exit 1
    fi
else
    echo "❌ Parser title fix test failed!"
    exit 1
fi