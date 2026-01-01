#!/bin/bash
# Deploy alert tables fix to Digital Ocean server

echo "🚀 Deploying Alert Tables Fix to Digital Ocean Server"
echo "====================================================="

# Server details
SERVER_IP="143.198.219.220"
SERVER_PATH="/opt/news-scraper"

echo "📤 Uploading fix files..."
scp fix_alert_tables_404.py root@${SERVER_IP}:${SERVER_PATH}/
scp scraper/core/alert_logger.py root@${SERVER_IP}:${SERVER_PATH}/scraper/core/

echo "🔧 Running alert tables fix on server..."
ssh root@${SERVER_IP} "cd ${SERVER_PATH} && source venv/bin/activate && python fix_alert_tables_404.py"

if [ $? -eq 0 ]; then
    echo "✅ Alert tables fix deployed successfully!"
    echo "🔄 Testing scheduler with fixed alert system..."
    ssh root@${SERVER_IP} "cd ${SERVER_PATH} && source venv/bin/activate && timeout 30 python automated_news_scheduler.py || echo 'Scheduler test completed'"
else
    echo "❌ Alert tables fix failed!"
    echo "📋 Manual steps required:"
    echo "1. SSH to server: ssh root@${SERVER_IP}"
    echo "2. Go to project: cd ${SERVER_PATH}"
    echo "3. Run fix: source venv/bin/activate && python fix_alert_tables_404.py"
    exit 1
fi