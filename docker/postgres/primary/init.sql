-- Create monitoring user
CREATE USER monitoring_user WITH PASSWORD 'monitor123';
GRANT SELECT ON pg_stat_database TO monitoring_user;
GRANT SELECT ON pg_stat_activity TO monitoring_user;
GRANT SELECT ON pg_stat_replication TO monitoring_user;

-- Create replication user
CREATE USER replicator REPLICATION LOGIN CONNECTION LIMIT 3 ENCRYPTED PASSWORD 'repl123';

-- Create test tables for monitoring
CREATE TABLE IF NOT EXISTS test_data (
    id SERIAL PRIMARY KEY,
    data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert some test data
INSERT INTO test_data (data) VALUES ('Test data 1'), ('Test data 2'), ('Test data 3');

-- Create monitoring metrics table
CREATE TABLE IF NOT EXISTS monitoring_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100),
    metric_value DECIMAL(10,2),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create recovery log table
CREATE TABLE IF NOT EXISTS recovery_log (
    id SERIAL PRIMARY KEY,
    action_type VARCHAR(50),
    status VARCHAR(20),
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Grant permissions on monitoring tables
GRANT SELECT, INSERT, UPDATE ON monitoring_metrics TO monitoring_user;
GRANT SELECT, INSERT ON recovery_log TO monitoring_user;
GRANT USAGE, SELECT ON SEQUENCE monitoring_metrics_id_seq TO monitoring_user;
GRANT USAGE, SELECT ON SEQUENCE recovery_log_id_seq TO monitoring_user;
