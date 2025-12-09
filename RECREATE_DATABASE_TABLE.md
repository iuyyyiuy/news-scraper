# Recreate Database Table to Match CSV Structure

## Problem
The current Supabase `articles` table doesn't match the CSV structure. The CSV has these columns:
- publication_date
- title
- body_text
- url
- source
- matched_keywords

## Solution

### Step 1: Run SQL in Supabase

1. Go to your Supabase dashboard: https://supabase.com/dashboard
2. Select your project
3. Click on "SQL Editor" in the left sidebar
4. Copy and paste the contents of `create_articles_table.sql`
5. Click "Run" to execute the SQL

This will:
- Drop the existing `articles` table
- Create a new table with the exact CSV structure
- Add indexes for better performance
- Set up Row Level Security

### Step 2: Upload CSV Data

After the table is created, run:

```bash
python3 upload_csv_exact.py
```

This will upload all 60 articles from `crypto_news_20251205_072237.csv` to Supabase.

## CSV Structure

The table now matches this exact structure:

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Auto-generated primary key |
| publication_date | TEXT | Date in YYYY/MM/DD format |
| title | TEXT | Article title |
| body_text | TEXT | Full article content |
| url | TEXT | Article URL (unique) |
| source | TEXT | Source name (e.g., "blockbeat") |
| matched_keywords | TEXT[] | Array of matched keywords |
| scraped_at | TIMESTAMP | When article was added to database |
| created_at | TIMESTAMP | Record creation time |

## Quick Commands

```bash
# After running SQL in Supabase, upload the data:
python3 upload_csv_exact.py

# Check the data:
python3 test_database_connection.py
```
