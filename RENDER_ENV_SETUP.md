# Render Environment Variables Setup

## Problem
The dashboard shows "暂无数据" (no data) on the deployed site because environment variables are not configured.

## Solution
You need to add environment variables to your Render service:

### Steps:

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Select your service (crypto-news-scraper)

2. **Add Environment Variables**
   - Go to "Environment" tab
   - Click "Add Environment Variable"
   - Add these two variables:

   ```
   SUPABASE_URL=https://vckulcbgaqyujucbbeno.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZja3VsY2JnYXF5dWp1Y2JiZW5vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3Mjc1NDcsImV4cCI6MjA4MDMwMzU0N30.k713c5eTsM-fEFAxp8ST5IIh_AhJZtHVBrb4-oViHZU
   ```

3. **Save and Redeploy**
   - Click "Save Changes"
   - Render will automatically redeploy

### Verify
After deployment completes, visit:
- Health check: https://crypto-news-scraper.onrender.com/api/health
- Dashboard: https://crypto-news-scraper.onrender.com/dashboard

The health check should show:
```json
{
  "status": "ok",
  "env_vars": {
    "SUPABASE_URL": "set",
    "SUPABASE_KEY": "set"
  },
  "database": "connected (71 articles)"
}
```

## Alternative: Use Render.yaml
Create a `render.yaml` file in your repo root (but don't commit secrets):
```yaml
services:
  - type: web
    name: crypto-news-scraper
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python start_dashboard.py
    envVars:
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
```
