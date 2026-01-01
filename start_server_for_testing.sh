#!/bin/bash
# Start the web server for testing the progress notification fix

echo "🚀 Starting Web Server for Testing"
echo "=================================="
echo ""
echo "📱 Dashboard will be available at:"
echo "   http://localhost:8000/dashboard"
echo ""
echo "🔧 API will be available at:"
echo "   http://localhost:8000/api/health"
echo ""
echo "💡 Press Ctrl+C to stop the server"
echo "=================================="
echo ""

# Start the server on port 8000 with host 0.0.0.0 to allow external access
python -m uvicorn scraper.web_api:app --host 0.0.0.0 --port 8000 --reload
