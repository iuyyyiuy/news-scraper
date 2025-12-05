#!/bin/bash

echo "🚀 Starting Crypto News Server with Database Feature..."
echo ""

cd /Users/kabellatsang/PycharmProjects/ai_code

echo "📍 Current directory: $(pwd)"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Make sure Supabase credentials are configured"
    echo ""
fi

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
python3 -c "import supabase" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ supabase not installed. Installing..."
    pip install supabase==1.0.3
fi

python3 -c "import apscheduler" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ APScheduler not installed. Installing..."
    pip install APScheduler==3.10.4
fi

echo "✅ Dependencies OK"
echo ""

echo "🌐 Starting server..."
echo ""
echo "Access points:"
echo "  📰 News Database: http://localhost:8000/dashboard"
echo "  🔍 News Scraper:  http://localhost:8000/"
echo "  📚 API Docs:      http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 -m uvicorn scraper.web_api:app --reload --host 0.0.0.0 --port 8000
