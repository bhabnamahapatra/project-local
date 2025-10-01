-- PostgreSQL setup script for AI Dashboard
-- Create database and user with appropriate permissions

-- Grant privileges to the ai_dashboard_user
GRANT ALL PRIVILEGES ON DATABASE ai_dashboard_db TO ai_dashboard_user;

-- Create tables for dashboard data
\c ai_dashboard_db;

-- Create system_metrics table
CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create logs table
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create openai_metrics table
CREATE TABLE IF NOT EXISTS openai_metrics (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    tokens_used INTEGER NOT NULL,
    cost_usd NUMERIC(10,6) NOT NULL,
    requests_count INTEGER NOT NULL,
    avg_response_time NUMERIC(10,3),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create copilot_metrics table
CREATE TABLE IF NOT EXISTS copilot_metrics (
    id SERIAL PRIMARY KEY,
    suggestions_count INTEGER NOT NULL,
    acceptances_count INTEGER NOT NULL,
    lines_suggested INTEGER NOT NULL,
    lines_accepted INTEGER NOT NULL,
    active_users INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert sample data
INSERT INTO system_metrics (metric_name, metric_value) VALUES 
    ('cpu_usage', 45.2),
    ('memory_usage', 68.5),
    ('disk_usage', 72.1);

INSERT INTO logs (level, message) VALUES 
    ('INFO', 'PostgreSQL database initialized successfully'),
    ('INFO', 'Dashboard API connected to PostgreSQL'),
    ('DEBUG', 'Sample log entry for testing');

INSERT INTO openai_metrics (model_name, tokens_used, cost_usd, requests_count, avg_response_time) VALUES 
    ('gpt-4', 15000, 0.45, 25, 1.2),
    ('gpt-3.5-turbo', 25000, 0.05, 50, 0.8),
    ('text-davinci-003', 8000, 0.16, 15, 2.1);

INSERT INTO copilot_metrics (suggestions_count, acceptances_count, lines_suggested, lines_accepted, active_users) VALUES 
    (1250, 980, 3750, 2940, 15),
    (890, 720, 2670, 2160, 12),
    (1560, 1240, 4680, 3720, 18);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level);
CREATE INDEX IF NOT EXISTS idx_openai_metrics_timestamp ON openai_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_openai_metrics_model ON openai_metrics(model_name);
CREATE INDEX IF NOT EXISTS idx_copilot_metrics_timestamp ON copilot_metrics(timestamp);