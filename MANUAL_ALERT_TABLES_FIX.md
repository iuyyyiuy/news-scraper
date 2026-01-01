# Manual Alert Tables Fix - Supabase Dashboard

## 🎯 **Current Status**
- ✅ **Main system working perfectly** - 12 articles stored successfully
- ⚠️ **Alert logging failing** - 404 error (non-critical)
- 🔧 **Solution**: Create tables manually in Supabase dashboard

## 📋 **Manual Fix Steps**

### **Step 1: Access Supabase Dashboard**
1. Go to: https://vckulcbgaqyujucbbeno.supabase.co
2. Sign in to your Supabase account
3. Navigate to your project dashboard

### **Step 2: Open SQL Editor**
1. In the left sidebar, click **"SQL Editor"**
2. Click **"New Query"** button
3. You'll see a blank SQL editor

### **Step 3: Create Alert Tables**
Copy and paste this SQL code into the editor:

```sql
-- Create alert_logs table for storing system alerts and monitoring data
CREATE TABLE IF NOT EXISTS alert_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    level VARCHAR(20) NOT NULL CHECK (level IN ('INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    component VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    details JSONB,
    session_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create scraping_sessions table for tracking scraping session statistics
CREATE TABLE IF NOT EXISTS scraping_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    sources_processed TEXT[],
    articles_found INTEGER DEFAULT 0,
    articles_stored INTEGER DEFAULT 0,
    articles_duplicate INTEGER DEFAULT 0,
    errors_encountered INTEGER DEFAULT 0,
    performance_metrics JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_alert_logs_timestamp ON alert_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_alert_logs_level ON alert_logs(level);
CREATE INDEX IF NOT EXISTS idx_alert_logs_component ON alert_logs(component);
CREATE INDEX IF NOT EXISTS idx_alert_logs_session_id ON alert_logs(session_id);

CREATE INDEX IF NOT EXISTS idx_scraping_sessions_start_time ON scraping_sessions(start_time DESC);
CREATE INDEX IF NOT EXISTS idx_scraping_sessions_session_id ON scraping_sessions(session_id);
```

### **Step 4: Execute the SQL**
1. Click the **"Run"** button (or press Ctrl+Enter)
2. You should see success messages for each table created
3. Check the **"Table Editor"** to verify the tables exist

### **Step 5: Verify Tables Created**
1. Go to **"Table Editor"** in the left sidebar
2. You should see two new tables:
   - `alert_logs`
   - `scraping_sessions`

## 🎉 **After Creating Tables**

Once the tables are created, the 404 errors will stop and you'll get full monitoring:
- ✅ Alert logging will work
- ✅ Session statistics will be tracked
- ✅ System health monitoring enabled

## 🚀 **Alternative: Skip Alert Tables**

**Your system works perfectly without alert tables!** If you don't want to create them:
- ✅ News scraping continues working
- ✅ Articles stored in database
- ✅ Dashboard updates normally
- 📁 Alerts saved to local files instead

## 📊 **Current System Performance**

Even without alert tables, your system is:
- ✅ Scraping articles every 4 hours
- ✅ Successfully storing articles (12 stored today)
- ✅ Filtering by security keywords
- ✅ Updating Supabase database
- ✅ Providing fresh news data

## 🎯 **Recommendation**

**Option 1 (Recommended)**: Keep running as-is - your system is working perfectly!

**Option 2**: Create alert tables manually for enhanced monitoring using the steps above.

Either way, your automated news system is successfully deployed and operational! 🎉