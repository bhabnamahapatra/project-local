CREATE TABLE IF NOT EXISTS openai_metrics (
    id SERIAL PRIMARY KEY,
    application_id VARCHAR(50) DEFAULT 'openai',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    response_time NUMERIC(10, 2),
    request_count INTEGER,
    error_rate NUMERIC(5, 2),
    success_rate NUMERIC(5, 2),
    average_tokens NUMERIC(10, 2),
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    cost NUMERIC(10, 2),
    uptime NUMERIC(5, 2),
    model VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS copilot_metrics (
    id SERIAL PRIMARY KEY,
    application_id VARCHAR(50) DEFAULT 'copilot',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    total_suggestions INTEGER,
    accepted_suggestions INTEGER,
    total_users INTEGER,
    lines_suggested INTEGER,
    lines_accepted INTEGER,
    meta JSONB,
    request_count INTEGER,
    error_rate NUMERIC(5, 2),
    success_rate NUMERIC(5, 2),
    average_tokens NUMERIC(10, 2),
    total_tokens INTEGER,
    cost NUMERIC(10, 2),
    uptime NUMERIC(5, 2)
);

CREATE TABLE IF NOT EXISTS claude_metrics (
    id SERIAL PRIMARY KEY,
    application_id VARCHAR(50) DEFAULT 'claude',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    response_time NUMERIC(10, 2),
    request_count INTEGER,
    error_rate NUMERIC(5, 2),
    success_rate NUMERIC(5, 2),
    average_tokens NUMERIC(10, 2),
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    cost NUMERIC(10, 2),
    uptime NUMERIC(5, 2),
    model VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS cursor_metrics (
    id SERIAL PRIMARY KEY,
    application_id VARCHAR(50) DEFAULT 'cursor',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    total_seats INTEGER,
    active_users INTEGER,
    utilization_rate NUMERIC(5, 2),
    monthly_active_users INTEGER,
    weekly_active_users INTEGER,
    daily_active_users INTEGER,
    total_interactions INTEGER,
    accepted_suggestions INTEGER,
    total_tokens BIGINT,
    total_cost NUMERIC(10, 2),
    token_breakdown JSONB,
    event_breakdown JSONB,
    model_breakdown JSONB,
    meta JSONB,
    request_count INTEGER,
    error_rate NUMERIC(5, 2),
    success_rate NUMERIC(5, 2),
    average_tokens NUMERIC(10, 2),
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    uptime NUMERIC(5, 2)
);

-- Create indices for better performance
CREATE INDEX idx_openai_timestamp ON openai_metrics(timestamp);
CREATE INDEX idx_copilot_timestamp ON copilot_metrics(timestamp);
CREATE INDEX idx_claude_timestamp ON claude_metrics(timestamp);
CREATE INDEX idx_cursor_timestamp ON cursor_metrics(timestamp);

-- Keep unified view for reporting
CREATE OR REPLACE VIEW unified_metrics AS
SELECT
  'openai' AS source,
  timestamp,
  request_count,
  success_rate,
  average_tokens,
  total_tokens AS tokens,
  cost,
  uptime,
  model
FROM openai_metrics
UNION ALL
SELECT
  'copilot' AS source,
  timestamp,
  total_suggestions AS request_count,
  CASE
    WHEN total_suggestions > 0 THEN (accepted_suggestions::float / total_suggestions * 100)
    ELSE NULL
  END AS success_rate,
  NULL AS average_tokens,
  NULL AS tokens,
  NULL AS cost,
  NULL AS uptime,
  NULL AS model
FROM copilot_metrics
UNION ALL
SELECT
  'cursor' AS source,
  timestamp,
  total_interactions AS request_count,
  CASE
    WHEN total_interactions > 0 THEN (accepted_suggestions::float / total_interactions * 100)
    ELSE NULL
  END AS success_rate,
  (total_tokens::float / NULLIF(total_interactions, 0)) AS average_tokens,
  total_tokens AS tokens,
  total_cost AS cost,
  utilization_rate AS uptime,
  NULL AS model
FROM cursor_metrics;
