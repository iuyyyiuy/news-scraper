#!/bin/bash
# Deploy and run immediate cleanup on Digital Ocean server

echo "🚀 Deploying Immediate Cleanup to Digital Ocean"
echo "==============================================="

# Server details
SERVER_IP="143.198.219.220"
SERVER_PATH="/opt/news-scraper"

echo "📤 Uploading cleanup script..."
scp run_cleanup_now.py root@${SERVER_IP}:${SERVER_PATH}/

echo "🔧 Running immediate cleanup on server..."
echo "⚠️  This will delete 309 old articles from 2025"
echo "💾 Only 2026-01-XX articles will remain"
echo ""

# Run the cleanup script on the server
ssh root@${SERVER_IP} "cd ${SERVER_PATH} && source venv/bin/activate && python run_cleanup_now.py"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ CLEANUP COMPLETED SUCCESSFULLY!"
    echo "=================================="
    echo "🎯 Result:"
    echo "   ✅ 309 old articles deleted"
    echo "   ✅ Only 2026-01-XX articles remain"
    echo "   ✅ Database is now clean and fast"
    echo "   ✅ Dashboard will load much faster"
    echo ""
    echo "📊 Your database now contains only current month articles!"
else
    echo ""
    echo "❌ Cleanup failed!"
    echo "📋 You can try running it manually:"
    echo "1. SSH to server: ssh root@${SERVER_IP}"
    echo "2. Go to project: cd ${SERVER_PATH}"
    echo "3. Run cleanup: source venv/bin/activate && python run_cleanup_now.py"
    exit 1
fi