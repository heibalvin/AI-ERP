-- 1. Create dedicated user and database
CREATE USER ai_erp_user WITH PASSWORD 'ai_erp_password';
CREATE DATABASE ai_erp_db OWNER ai_erp_user;

-- Connect to ai_erp_db before running the rest:
-- \c ai_erp_db

-- 2. Create dedicated schema
CREATE SCHEMA IF NOT EXISTS api AUTHORIZATION ai_erp_user;

-- 3. Create the ai_tasks table
CREATE TABLE IF NOT EXISTS api.ai_tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Grant privileges
GRANT ALL PRIVILEGES ON SCHEMA api TO ai_erp_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA api TO ai_erp_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA api TO ai_erp_user;