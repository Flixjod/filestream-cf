# 🚀 FileStream Bot - Enhanced with D1 Database

Advanced Telegram File-to-Link Bot with Cloudflare Workers & D1 Database Integration.

## ✨ Features

### Core Features
- 📤 **File Upload**: Upload any file type (video, audio, document, photo) up to 4GB
- 🔗 **Multiple Link Types**: Download links, streaming links, and Telegram deep links
- 🎬 **Stream Player**: Built-in web player for videos and audio
- 📱 **Multi-Platform**: Support for VLC, MX Player, and browser streaming
- ⚡ **Lightning Fast**: Powered by Cloudflare's global CDN

### New Database Features
- 👤 **User Registration**: Automatic user registration and tracking
- 📊 **File Metadata**: Store comprehensive file information
- 📈 **Download Statistics**: Track download counts per file and user
- 🗂️ **File Management**: List and manage uploaded files
- 🔒 **Revoke Tokens**: Secure file deletion with unique tokens
- 🗑️ **File Revocation**: Delete files from channel and deactivate links

### Commands

| Command | Description | Access |
|---------|-------------|--------|
| `/start` | Start the bot and register | All Users |
| `/files` | View uploaded files with inline navigation | All Users |
| `/stats` | View personal statistics | All Users |
| `/revoke [hash] [token]` | Revoke a file with token | File Owner |
| `/revoke [hash]` | Revoke any file without token | Owner Only |
| `/revokeall` | Delete all files permanently | Owner Only |

### URL Formats

**New Clean URLs (Primary):**
- Download: `domain.com/dl/ABCD1234`
- Stream: `domain.com/stream/ABCD1234`
- Stream Page: `domain.com/stream?file=ABCD1234`

**Legacy URLs (Still Supported):**
- Download: `domain.com/?file=ABCD1234`
- Stream: `domain.com/?file=ABCD1234&mode=inline`

### Interactive Features

**File Generation Response:**
- 🌐 Stream Page - Opens streaming interface
- 📥 Download - Direct download link
- 🔗 Copy Link - Copy stream URL
- ▶️ VLC Player - Open in VLC
- 📱 MX Player - Open in MX Player
- 💬 Telegram - Share via Telegram
- 🔁 Share - Inline share button
- 🗑️ Revoke - One-click file deletion
- 👑 Owner - Contact owner

**File Browser (/files command):**
1. View list of uploaded files as inline buttons
2. Click file to see detailed information
3. Manage files (view stats, revoke, share)
4. Navigate back and forth with inline keyboard

## 📦 Database Schema

### Users Table
```sql
- user_id (PRIMARY KEY)
- first_name
- username
- registered_at
- total_files
- total_downloads
```

### Files Table
```sql
- id (AUTO INCREMENT)
- file_hash (UNIQUE)
- message_id
- user_id
- user_name
- file_name
- file_size
- file_type
- created_at
- downloads
- revoke_token
- revoked
- revoked_at
```

## 🛠️ Setup Instructions

### 1. Prerequisites
- Cloudflare account
- Telegram bot token from [@BotFather](https://t.me/botfather)
- Telegram channel with bot as admin

### 2. Create D1 Database

```bash
# Login to Cloudflare
npx wrangler login

# Create D1 database
npx wrangler d1 create filestream_db

# Note the database_id from the output
```

### 3. Initialize Database Schema

```bash
# Apply the schema to your D1 database
npx wrangler d1 execute filestream_db --file=schema.sql
```

### 4. Configure Variables

Edit `worker.js` and update these variables:

```javascript
const BOT_TOKEN = "YOUR_BOT_TOKEN"; // From @BotFather
const BOT_SECRET = "YOUR_SECRET_TEXT"; // Random secure string
const BOT_OWNER = 123456789; // Your Telegram user ID
const BOT_CHANNEL = -100123456789; // Your channel ID (must start with -100)
const SIA_SECRET = "YOUR_SIA_SECRET"; // Random secure string
const PUBLIC_BOT = false; // Set to true for public access
const OWNER_USERNAME = "YOUR_USERNAME"; // Your Telegram username
const BOT_NAME = "Your Bot Name"; // Display name
```

### 5. Update wrangler.toml

Update the `database_id` in `wrangler.toml` with your actual D1 database ID:

```toml
[[d1_databases]]
binding = "DB"
database_name = "filestream_db"
database_id = "your-actual-database-id-here"
```

### 6. Deploy to Cloudflare

```bash
# Deploy the worker
npx wrangler deploy

# Your worker will be available at: https://your-worker.workers.dev
```

### 7. Register Webhook

After deployment, visit:
```
https://your-worker.workers.dev/registerWebhook
```

### 8. Verify Bot

Check if bot is working:
```
https://your-worker.workers.dev/getMe
```

### 9. Bot Configuration

In [@BotFather](https://t.me/botfather):
1. Enable **Inline Mode** for your bot
2. Disable **Inline Feedback** for better performance
3. Set bot commands:
```
start - Start the bot
files - View your uploaded files
stats - View your statistics
revoke - Revoke a file with token
```

### 10. Channel Setup

1. Create a Telegram channel
2. Add your bot as administrator
3. Give bot **Edit** permissions
4. Forward a message from channel to [@userinfobot](https://t.me/userinfobot) to get channel ID
5. Channel ID must start with `-100`

## 🎯 Usage Examples

### Upload a File
1. Send any file to the bot
2. Receive links and revoke token
3. Save the revoke token for later deletion

### View Your Files
```
/files
```
- Browse uploaded files
- Click file to view details
- Manage (revoke, share, download)

### Check Statistics
```
/stats
```
- Total files uploaded
- Active files count
- Total downloads

### Revoke a File

**As File Owner:**
```
/revoke ABCD1234 TOKEN123456
```

**As Bot Owner:**
```
/revoke ABCD1234
```

**Via Button:**
- Click 🗑️ Revoke button on file message
- Instant deletion with confirmation

### Delete All Files (Owner Only)
```
/revokeall
```

## 📊 Features Details

### Enhanced Channel Messages

When a file is saved, the channel message includes:
```
ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ : 🍃⏤͟͟͞͞ User Name @username
ᴜsᴇʀ ɪᴅ : 123456789
ғɪʟᴇ ɪᴅ : 42
```

### Download Tracking

- Every file access increments download counter
- Per-file download statistics
- User total download tracking
- Revoked files cannot be downloaded

### Security Features

- Unique revoke token per file
- File owner validation
- Owner bypass for revoke operations
- Revoked file access blocking
- Secure hash generation

### File Browser Navigation

```
📂 Files List
   ↓
📄 File Details
   ↓
🗑️ Revoke / ← Back
```

## 🔧 Development

### Local Testing

```bash
# Install dependencies
npm install -g wrangler

# Run locally with D1
npx wrangler dev

# Test with local D1
npx wrangler d1 execute filestream_db --local --file=schema.sql
```

### Database Management

```bash
# Query database
npx wrangler d1 execute filestream_db --command="SELECT * FROM users LIMIT 10"

# Backup database
npx wrangler d1 export filestream_db --output=backup.sql

# View database info
npx wrangler d1 info filestream_db
```

## 📝 File Size Limitations

| Link Type | Size Limit | Notes |
|-----------|------------|-------|
| Telegram Link | < 4.00GB | Via bot deep link |
| Inline Link | < 4.00GB | Via inline query |
| Direct Download | < 100MB | Cloudflare Worker limit |
| Stream Link | < 100MB | Cloudflare Worker limit |

**Note:** Large files (>100MB) are best accessed via Telegram links.

## 🆕 What's New

### Version 2.0 - Database Integration

✅ MongoDB → Cloudflare D1 migration  
✅ User registration and tracking  
✅ File metadata storage  
✅ Download statistics  
✅ Revoke token system  
✅ `/files` command with inline navigation  
✅ `/stats` command for user statistics  
✅ `/revoke` and `/revokeall` commands  
✅ One-click revoke button  
✅ Enhanced channel messages  
✅ Clean URL routing (`/dl/` and `/stream/`)  
✅ Revoked file access blocking  
✅ Download count tracking  

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📄 License

This project is licensed under the MIT License.

## 🙏 Credits

- Original project: [filestream-cf](https://github.com/vauth/filestream-cf)
- Database integration: Enhanced version with D1
- Created by [@FLiX_LY](https://t.me/FLiX_LY)

## 🔗 Links

- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [Cloudflare D1 Docs](https://developers.cloudflare.com/d1/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

**⚡ Powered by Cloudflare Workers & D1 Database**
