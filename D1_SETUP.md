# Cloudflare D1 Database Setup Guide

This guide will help you set up a Cloudflare D1 database for the FileStream Bot to enable advanced features like file management, user tracking, and statistics.

## Prerequisites

- A Cloudflare account
- Wrangler CLI installed (`npm install -g wrangler`)
- Your bot already deployed as a Cloudflare Worker

## Step 1: Create D1 Database

```bash
# Login to Cloudflare
wrangler login

# Create a new D1 database
wrangler d1 create filestream-db
```

After running this command, you'll receive output like:

```
✅ Successfully created DB 'filestream-db'!

[[d1_databases]]
binding = "DB"
database_name = "filestream-db"
database_id = "xxxx-xxxx-xxxx-xxxx-xxxx"
```

## Step 2: Update wrangler.toml

Add the database binding to your `wrangler.toml` file:

```toml
name = "filestream-bot"
main = "worker.js"
compatibility_date = "2024-01-01"

[[d1_databases]]
binding = "DB"
database_name = "filestream-db"
database_id = "your-database-id-here"
```

Replace `your-database-id-here` with the actual database_id from Step 1.

## Step 3: Initialize Database Schema

Run the SQL schema to create tables:

```bash
# Execute the schema file
wrangler d1 execute filestream-db --file=./schema.sql
```

Or you can create tables manually:

```bash
wrangler d1 execute filestream-db --command="CREATE TABLE IF NOT EXISTS files (file_id TEXT PRIMARY KEY, message_id TEXT NOT NULL, user_id TEXT NOT NULL, username TEXT, file_name TEXT, file_size INTEGER, file_type TEXT, secret_token TEXT NOT NULL UNIQUE, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, downloads INTEGER DEFAULT 0);"

wrangler d1 execute filestream-db --command="CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, username TEXT, first_name TEXT, last_name TEXT, first_used DATETIME DEFAULT CURRENT_TIMESTAMP, total_files INTEGER DEFAULT 0, last_activity DATETIME DEFAULT CURRENT_TIMESTAMP);"
```

## Step 4: Deploy Your Worker

```bash
# Deploy the worker with D1 binding
wrangler deploy
```

## Step 5: Verify Setup

1. Visit your worker URL at `https://your-worker.workers.dev/getMe`
2. Send a file to your bot
3. Check if the database is working by running:

```bash
wrangler d1 execute filestream-db --command="SELECT * FROM files LIMIT 5;"
```

## Database Features

Once D1 is set up, your bot will have these features:

### For Users:
- **/files** - View all your uploaded files with inline buttons
- **/revoke <token>** - Delete a specific file using its secret token
- **Revoke Button** - Each file gets a revoke button for easy deletion
- **File Statistics** - Track download counts for each file

### For Owner:
- **/stats** - View bot statistics (total files, users, downloads)
- **/revokeall** - Delete all files from the database and channel
- **User Management** - Track all users who have used the bot

## Database Management

### View all files
```bash
wrangler d1 execute filestream-db --command="SELECT * FROM files;"
```

### View all users
```bash
wrangler d1 execute filestream-db --command="SELECT * FROM users;"
```

### Get statistics
```bash
wrangler d1 execute filestream-db --command="SELECT COUNT(*) as total_files FROM files;"
wrangler d1 execute filestream-db --command="SELECT COUNT(*) as total_users FROM users;"
```

### Delete old files (older than 30 days)
```bash
wrangler d1 execute filestream-db --command="DELETE FROM files WHERE created_at < datetime('now', '-30 days');"
```

### Backup database
```bash
wrangler d1 export filestream-db --output=./backup.sql
```

## Troubleshooting

### Database Not Found Error
Make sure your `wrangler.toml` has the correct `database_id` and the binding name is exactly "DB".

### Permission Errors
Ensure you're logged in with `wrangler login` and have the necessary permissions for your Cloudflare account.

### Tables Not Created
Run the schema.sql file again:
```bash
wrangler d1 execute filestream-db --file=./schema.sql
```

## Local Development

For local development with D1:

```bash
# Create local database
wrangler d1 execute filestream-db --local --file=./schema.sql

# Run worker locally with D1
wrangler dev --local --persist
```

## Cost Considerations

Cloudflare D1 has a generous free tier:
- **5 GB storage** (free)
- **5 million reads/day** (free)
- **100,000 writes/day** (free)

For most users, this is more than enough and the bot will run completely free!

## Support

If you encounter any issues, please check:
1. Your wrangler.toml configuration
2. Database binding name is "DB"
3. Schema is properly initialized
4. Worker is deployed after database setup

For more information, visit: https://developers.cloudflare.com/d1/
