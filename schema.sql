-- Cloudflare D1 Database Schema for FileStream Bot

-- Files table: stores all uploaded files information
CREATE TABLE IF NOT EXISTS files (
    file_id TEXT PRIMARY KEY,
    message_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    username TEXT,
    file_name TEXT,
    file_size INTEGER,
    file_type TEXT,
    secret_token TEXT NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    downloads INTEGER DEFAULT 0
);

-- Users table: stores user information and statistics
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    first_used DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_files INTEGER DEFAULT 0,
    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_files_user_id ON files(user_id);
CREATE INDEX IF NOT EXISTS idx_files_created ON files(created_at);
CREATE INDEX IF NOT EXISTS idx_files_secret_token ON files(secret_token);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
