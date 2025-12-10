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

-- Add comments for documentation
COMMENT ON TABLE alert_logs IS 'System alerts and monitoring logs for news scraping operations';
COMMENT ON TABLE scraping_sessions IS 'Statistics and metadata for news scraping sessions';

COMMENT ON COLUMN alert_logs.level IS 'Alert severity: INFO, WARNING, ERROR, CRITICAL';
COMMENT ON COLUMN alert_logs.component IS 'System component that generated the alert';
COMMENT ON COLUMN alert_logs.details IS 'Additional structured data about the alert';
COMMENT ON COLUMN alert_logs.session_id IS 'Associated scraping session ID if applicable';

COMMENT ON COLUMN scraping_sessions.session_id IS 'Unique identifier for the scraping session';
COMMENT ON COLUMN scraping_sessions.sources_processed IS 'List of news sources processed in this session';
COMMENT ON COLUMN scraping_sessions.performance_metrics IS 'JSON object containing performance data';