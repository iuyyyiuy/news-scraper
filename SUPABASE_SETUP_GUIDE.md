# Supabase Setup Guide for News Database

## Step 1: Create Supabase Account

1. Go to https://supabase.com
2. Click "Start your project" or "Sign In"
3. Sign up with GitHub, Google, or email
4. Verify your email if needed

## Step 2: Create New Project

1. After logging in, click "New Project"
2. Fill in the project details:
   - **Name**: `crypto-news-db` (or any name you prefer)
   - **Database Password**: Create a strong password (SAVE THIS!)
   - **Region**: Choose closest to you (e.g., `Northeast Asia (Tokyo)` for better performance)
   - **Pricing Plan**: Select "Free" (sufficient for this project)
3. Click "Create new project"
4. Wait 2-3 minutes for project to be provisioned

## Step 3: Get API Credentials

Once your project is ready:

1. In the left sidebar, click on **"Settings"** (gear icon at bottom)
2. Click on **"API"** in the settings menu
3. You'll see two important values:

   **Project URL**:
   ```
   https://xxxxxxxxxxxxx.supabase.co
   ```
   
   **anon/public key** (under "Project API keys"):
   ```
   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh4eHh4...
   ```

4. **COPY BOTH VALUES** - you'll need them in Step 5

## Step 4: Create Database Table

1. In the left sidebar, click on **"SQL Editor"**
2. Click **"New query"**
3. Copy and paste this SQL code:

```sql
-- Create articles table
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    date TIMESTAMP NOT NULL,
    source TEXT NOT NULL,
    content TEXT NOT NULL,
    matched_keywords TEXT[] NOT NULL,
    scraped_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_articles_date ON articles(date DESC);
CREATE INDEX idx_articles_source ON articles(source);
CREATE INDEX idx_articles_keywords ON articles USING GIN(matched_keywords);

-- Add comment to table
COMMENT ON TABLE articles IS 'Stores scraped crypto security news articles';
```

4. Click **"Run"** (or press Ctrl+Enter / Cmd+Enter)
5. You should see "Success. No rows returned"

## Step 5: Verify Table Creation

1. In the left sidebar, click on **"Table Editor"**
2. You should see the `articles` table listed
3. Click on it to see the columns (it will be empty for now)

## Step 6: Configure Environment Variables

Now add your credentials to the project:

### For Local Development:

Create a `.env` file in your project root:

```bash
# Supabase Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh4eHh4...
```

Replace with your actual values from Step 3.

### For Render Deployment:

You'll add these as environment variables in Render dashboard later:
- `SUPABASE_URL`
- `SUPABASE_KEY`

## Step 7: Test Connection (Optional)

You can test the connection with this simple Python script:

```python
from supabase import create_client, Client

url = "YOUR_SUPABASE_URL"
key = "YOUR_SUPABASE_KEY"

supabase: Client = create_client(url, key)

# Test query
response = supabase.table('articles').select("*").execute()
print(f"Connection successful! Found {len(response.data)} articles")
```

## What You Need to Provide Me

Once you complete the setup, please share:

1. ✅ Supabase Project URL
2. ✅ Supabase Anon Key

**Note**: The anon key is safe to share with me as it's designed for client-side use. However, never share your `service_role` key!

## Troubleshooting

### Issue: "relation 'articles' does not exist"
- Solution: Make sure you ran the SQL in Step 4 successfully

### Issue: "Invalid API key"
- Solution: Double-check you copied the `anon` key, not the `service_role` key

### Issue: Project creation stuck
- Solution: Wait a few more minutes, or try refreshing the page

### Issue: Can't see SQL Editor
- Solution: Make sure your project is fully provisioned (green status indicator)

## Next Steps

After setup is complete:
1. Share your credentials with me
2. I'll create the database manager code
3. We'll test the connection
4. Then proceed with the full implementation

---

**Ready?** Once you have your Supabase URL and Key, paste them here and we'll continue!
