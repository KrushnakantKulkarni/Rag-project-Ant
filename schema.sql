-- SQLite database schema initialization script
-- Establishes observability database indexes and cascades deletion configurations

CREATE TABLE IF NOT EXISTS traces (
    trace_id TEXT PRIMARY KEY,
    document_name TEXT NOT NULL,
    status TEXT NOT NULL,          -- SUCCESS or FAILED
    error_message TEXT,
    overall_latency_ms REAL,
    overall_token_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS spans (
    span_id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    step_name TEXT NOT NULL,
    status TEXT NOT NULL,
    confidence_score INTEGER,      -- 1 to 5, NULL for non-LLM steps
    latency_ms REAL,
    token_count INTEGER,
    error TEXT,
    FOREIGN KEY(trace_id) REFERENCES traces(trace_id) ON DELETE CASCADE
);
