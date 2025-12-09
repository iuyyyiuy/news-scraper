-- First, completely drop everything
DROP TABLE IF EXISTS articles CASCADE;

-- Create the table with exact CSV structure
CREATE TABLE articles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    publication_date TEXT NOT NULL,
    title TEXT NOT NULL,
    body_text TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    source TEXT NOT NULL,
    matched_keywords TEXT[] NOT NULL,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add a simple index
CREATE INDEX idx_articles_url ON articles(url);

-- Disable RLS for now to test
ALTER TABLE articles DISABLE ROW LEVEL SECURITY;
