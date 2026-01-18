-- Cloudflare D1 Database Schema for FileStream Bot

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    username TEXT,
    registered_at INTEGER NOT NULL,
    total_files INTEGER DEFAULT 0,
    total_downloads INTEGER DEFAULT 0
);

-- Files table
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_hash TEXT UNIQUE NOT NULL,
    message_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    user_name TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_type TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    downloads INTEGER DEFAULT 0,
    revoke_token TEXT NOT NULL,
    revoked INTEGER DEFAULT 0,
    revoked_at INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_files_file_hash ON files(file_hash);
CREATE INDEX IF NOT EXISTS idx_files_user_id ON files(user_id);
CREATE INDEX IF NOT EXISTS idx_files_revoked ON files(revoked);
CREATE INDEX IF NOT EXISTS idx_files_message_id ON files(message_id);
