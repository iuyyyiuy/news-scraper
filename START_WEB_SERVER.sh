#!/bin/bash

# Script to start the web interface for testing
# Run this to test the multi-source scraper improvements

echo "============================================================"
echo "Starting Multi-Source Scraper Web Interface"
echo "============================================================"
echo ""

cd /Users/kabellatsang/PycharmProjects/ai_code

echo "📍 Working directory: $(pwd)"
echo ""

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "✅ Activating virtual environment..."
    source .venv/bin/activate
else
    echo "⚠️  No virtual environment found, using system Python"
fi

echo ""
echo "🚀 Starting web server on http://localhost:8000"
echo ""
echo "============================================================"
echo "TESTING CHECKLIST:"
echo "============================================================"
echo ""
echo "1. Open http://localhost:8000 in your browser"
echo ""
echo "2. Test Settings:"
echo "   - Date range: Last 2 days"
echo "   - Keywords: BTC, Bitcoin, 比特币, ETH, 以太坊"
echo "   - Sources: All 3 (BlockBeats, Jinse, PANews)"
echo "   - Articles per source: 10 (for quick test)"
echo ""
echo "3. Verify:"
echo "   ✓ Click '全部' tab - should show ONLY matched articles"
echo "   ✓ Click 'JINSE' tab - should show ALL logs (including filtered)"
echo "   ✓ Click 'BLOCKBEATS' tab - should show ALL logs"
echo "   ✓ Click 'PANEWS' tab - should show ALL logs"
echo "   ✓ Check article titles are correct (not generic)"
echo "   ✓ Check dates are in 2025-MM-DD format"
echo ""
echo "4. Full Test (optional):"
echo "   - Change articles per source to 50"
echo "   - Verify each source checks exactly 50 articles"
echo ""
echo "============================================================"
echo ""
echo "💡 Press Ctrl+C to stop the server when done testing"
echo ""
echo "============================================================"
echo ""

# Start the server
python3 run_web_server.py --port 8000
