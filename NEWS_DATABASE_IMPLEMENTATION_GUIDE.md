# News Database Implementation Guide

## Files Created

### Core Backend Files
1. `scraper/core/database_manager.py` - Database operations
2. `scraper/core/scheduled_scraper.py` - Automated scraping logic
3. `scraper/core/scheduler.py` - Task scheduling service
4. `.env` - Environment variables (Supabase credentials)
5. `requirements_news_database.txt` - New dependencies

### Test Files
6. `test_database_connection.py` - Database connection test

## Step 1: Copy Files to ai_code Project

Copy these files from `pythonProject3` to your `ai_code` project:

```bash
# Navigate to ai_code project
cd /Users/kabellatsang/PycharmProjects/ai_code/

# Copy the core files
cp ../pythonProject3/scraper/core/database_manager.py scraper/core/
cp ../pythonProject3/scraper/core/scheduled_scraper.py scraper/core/
cp ../pythonProject3/scraper/core/scheduler.py scraper/core/

# Copy environment file
cp ../pythonProject3/.env .

# Copy test file
cp ../pythonProject3/test_database_connection.py .
```

## Step 2: Install Dependencies

```bash
# Install new dependencies
pip install supabase==2.3.4
pip install APScheduler==3.10.4
pip install pytz==2024.1
pip install python-dotenv==1.0.0

# Or install from requirements file
pip install -r ../pythonProject3/requirements_news_database.txt
```

## Step 3: Test Database Connection

```bash
# Run the test script
python test_database_connection.py
```

You should see:
- ✅ Connection successful
- ✅ Sample article inserted
- ✅ Articles retrieved
- ✅ Keyword filtering works
- ✅ Statistics retrieved

## Step 4: Test Individual Components

### Test Database Manager
```bash
python -m scraper.core.database_manager
```

### Test Scheduled Scraper (with one keyword)
```bash
python -m scraper.core.scheduled_scraper
```

### Test Scheduler Service
```bash
python -m scraper.core.scheduler
```

## Step 5: Verify Supabase

1. Go to your Supabase dashboard
2. Click on "Table Editor"
3. Select the `articles` table
4. You should see the test article inserted

## Next Steps

After successful testing:

1. ✅ **Phase 1 Complete** - Database setup done!

2. **Phase 2** - Integrate with Flask app:
   - Update `web_api.py` to add new API endpoints
   - Start scheduler when Flask app starts

3. **Phase 3** - Create dashboard frontend:
   - Create `templates/dashboard.html`
   - Create `static/css/dashboard.css`
   - Create `static/js/dashboard.js`

4. **Phase 4** - Add navigation:
   - Update `templates/index.html` with sidebar

## Troubleshooting

### Error: "No module named 'supabase'"
```bash
pip install supabase
```

### Error: "SUPABASE_URL not found"
- Make sure `.env` file is in the project root
- Check that `.env` contains correct credentials

### Error: "relation 'articles' does not exist"
- Go to Supabase SQL Editor
- Run the CREATE TABLE script from SUPABASE_SETUP_GUIDE.md

### Error: "Invalid API key"
- Double-check the SUPABASE_KEY in `.env`
- Make sure you copied the `anon` key, not `service_role`

## Current Status

✅ **Completed:**
- Database schema created in Supabase
- Database manager implemented
- Scheduled scraper implemented
- Scheduler service implemented
- Environment configuration done
- Test scripts created

⏳ **Next:**
- Integrate with Flask web_api.py
- Create dashboard UI
- Add navigation
- Deploy to Render

## Testing Checklist

- [ ] Database connection works
- [ ] Can insert articles
- [ ] Can retrieve articles
- [ ] Can filter by keyword
- [ ] Can get statistics
- [ ] Scheduled scraper works with one keyword
- [ ] Scheduler service starts successfully

Once all tests pass, you're ready to proceed with Flask integration!
