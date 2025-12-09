-- Drop existing table if it exists
DROP TABLE IF EXISTS articles CASCADE;

-- Create articles table matching CSV structure exactly
CREATE TABLE articles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    publication_date TEXT NOT NULL,
    title TEXT NOT NULL,
    body_text TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    source TEXT NOT NULL,
    matched_keywords TEXT[] NOT NULL,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX idx_articles_publication_date ON articles(publication_date);
CREATE INDEX idx_articles_source ON articles(source);
CREATE INDEX idx_articles_matched_keywords ON articles USING GIN(matched_keywords);
CREATE INDEX idx_articles_url ON articles(url);

-- Enable Row Level Security (optional, but recommended)
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (adjust based on your security needs)
CREATE POLICY "Allow all operations on articles" ON articles
    FOR ALL
    USING (true)
    WITH CHECK (true);
