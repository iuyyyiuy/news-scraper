#!/bin/bash

echo "🚀 Deploying News Database Feature to Render"
echo "=============================================="
echo ""

cd /Users/kabellatsang/PycharmProjects/ai_code

# Check if we're in the right directory
if [ ! -f "scraper/web_api.py" ]; then
    echo "❌ Error: Not in ai_code directory"
    exit 1
fi

echo "📦 Step 1: Updating requirements.txt..."
echo ""

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "⚠️  requirements.txt not found, creating new one..."
    cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
beautifulsoup4==4.12.2
requests==2.31.0
lxml==4.9.3
python-dateutil==2.8.2
supabase==1.0.3
APScheduler==3.10.4
pytz==2024.1
python-dotenv==1.0.0
EOF
else
    # Add new dependencies if not already present
    if ! grep -q "supabase" requirements.txt; then
        echo "supabase==1.0.3" >> requirements.txt
    fi
    if ! grep -q "APScheduler" requirements.txt; then
        echo "APScheduler==3.10.4" >> requirements.txt
    fi
    if ! grep -q "pytz" requirements.txt; then
        echo "pytz==2024.1" >> requirements.txt
    fi
    if ! grep -q "python-dotenv" requirements.txt; then
        echo "python-dotenv==1.0.0" >> requirements.txt
    fi
fi

echo "✅ requirements.txt updated"
echo ""

echo "📝 Step 2: Checking git status..."
echo ""
git status

echo ""
echo "➕ Step 3: Adding all changes..."
git add .

echo ""
echo "📋 Step 4: Committing changes..."
git commit -m "Add news database feature with dashboard, scheduler, and Supabase integration

Features added:
- Automated daily scraping at 8 AM UTC+8
- Supabase database integration
- Dashboard UI with filtering and pagination
- Scheduler for daily scraping and monthly cleanup
- API endpoints for database operations
- Sidebar navigation
- 21 security-related keywords monitoring"

echo ""
echo "🔄 Step 5: Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "=============================================="
    echo "✅ Successfully pushed to GitHub!"
    echo "=============================================="
    echo ""
    echo "📊 Next Steps:"
    echo ""
    echo "1. Render will automatically detect the changes"
    echo "2. Wait 5-10 minutes for deployment"
    echo "3. Check deployment status at:"
    echo "   https://dashboard.render.com"
    echo ""
    echo "4. Once deployed, visit:"
    echo "   📰 Dashboard: https://crypto-news-scraper.onrender.com/dashboard"
    echo "   🔍 Scraper:   https://crypto-news-scraper.onrender.com/"
    echo "   📚 API Docs:  https://crypto-news-scraper.onrender.com/docs"
    echo ""
    echo "5. Verify environment variables are set in Render:"
    echo "   - SUPABASE_URL"
    echo "   - SUPABASE_KEY"
    echo ""
    echo "🎉 Deployment initiated successfully!"
else
    echo ""
    echo "❌ Failed to push to GitHub"
    echo "Please check your git configuration and try again"
    exit 1
fi
