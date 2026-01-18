# 🚀 Deployment Guide

Complete step-by-step guide to deploy FileStream Bot with D1 database.

## Prerequisites

Before starting, make sure you have:
- ✅ Cloudflare account (free tier works)
- ✅ Node.js installed (v16 or higher)
- ✅ Telegram account
- ✅ Basic knowledge of terminal/command line

---

## Part 1: Telegram Setup

### Step 1: Create Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the prompts:
   - Enter bot name (e.g., "My FileStream Bot")
   - Enter bot username (e.g., "myfilestream_bot")
4. **Save the bot token** - you'll need it later
   ```
   Example: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

### Step 2: Configure Bot Settings

In @BotFather, configure your bot:

```
/mybots → Select your bot → Bot Settings
```

**Enable Inline Mode:**
```
/mybots → Select your bot → Inline Mode → Turn On
```

**Disable Inline Feedback:**
```
/mybots → Select your bot → Inline Feedback → Turn Off
```

**Set Commands:**
```
/mybots → Select your bot → Edit Commands
```

Paste this:
```
start - Start the bot
files - View your uploaded files
stats - View your statistics
revoke - Revoke a file with token
```

### Step 3: Get Your User ID

1. Search for [@userinfobot](https://t.me/userinfobot) on Telegram
2. Start the bot
3. **Save your user ID** (e.g., 123456789)

### Step 4: Create a Channel

1. Create a new Telegram channel (public or private)
2. Add your bot as administrator
3. Give bot **Edit Messages** permission
4. Forward any message from your channel to [@userinfobot](https://t.me/userinfobot)
5. **Save the channel ID** - it should start with `-100` (e.g., -1001234567890)

---

## Part 2: Cloudflare Setup

### Step 1: Install Wrangler CLI

Open terminal and run:

```bash
npm install -g wrangler
```

Verify installation:
```bash
wrangler --version
```

### Step 2: Login to Cloudflare

```bash
wrangler login
```

This will open a browser window. Log in and authorize Wrangler.

### Step 3: Create D1 Database

```bash
wrangler d1 create filestream_db
```

**Important:** Save the output! You'll need the `database_id`.

Example output:
```
✅ Successfully created DB 'filestream_db'

[[d1_databases]]
binding = "DB"
database_name = "filestream_db"
database_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

**Copy the `database_id`** value!

### Step 4: Initialize Database

Navigate to your project folder:
```bash
cd /path/to/your/project
```

Apply the schema:
```bash
wrangler d1 execute filestream_db --file=schema.sql
```

Verify the tables were created:
```bash
wrangler d1 execute filestream_db --command="SELECT name FROM sqlite_master WHERE type='table'"
```

You should see: `users` and `files` tables.

---

## Part 3: Configuration

### Step 1: Update worker.js

Open `worker.js` and find these lines at the top:

```javascript
const BOT_TOKEN = "BOT_TOKEN";
const BOT_SECRET = "BOT_SECRET";
const BOT_OWNER = 123456789;
const BOT_CHANNEL = -100123456789;
const SIA_SECRET = "SIA_SECRET";
const PUBLIC_BOT = false;
const OWNER_USERNAME = "FLiX_LY";
const BOT_NAME = "FileStream Bot";
```

Replace with your values:

```javascript
const BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"; // From @BotFather
const BOT_SECRET = "MySecureSecret123!@#"; // Any random secure string
const BOT_OWNER = 123456789; // Your Telegram user ID
const BOT_CHANNEL = -1001234567890; // Your channel ID (starts with -100)
const SIA_SECRET = "AnotherSecureString456$%^"; // Another random string
const PUBLIC_BOT = false; // Set to true if you want anyone to use it
const OWNER_USERNAME = "your_username"; // Your Telegram username (without @)
const BOT_NAME = "My FileStream Bot"; // Your bot display name
```

**Security Tips:**
- Use strong random strings for `BOT_SECRET` and `SIA_SECRET`
- You can generate them at: https://1password.com/password-generator
- Never share these values publicly

### Step 2: Update wrangler.toml

Open `wrangler.toml` and find:

```toml
[[d1_databases]]
binding = "DB"
database_name = "filestream_db"
database_id = "your-database-id-here"
```

Replace `your-database-id-here` with your actual database ID from Step 3 of Part 2.

Example:
```toml
[[d1_databases]]
binding = "DB"
database_name = "filestream_db"
database_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

---

## Part 4: Deployment

### Step 1: Deploy to Cloudflare

From your project directory:

```bash
wrangler deploy
```

Wait for deployment to complete. You'll see output like:
```
✨ Success! Uploaded 1 file (X seconds)
✨ Deployment complete!

https://streamfile-cf.your-subdomain.workers.dev
```

**Save this URL!** This is your bot's URL.

### Step 2: Register Webhook

Open your browser and visit:
```
https://your-worker-url.workers.dev/registerWebhook
```

You should see a JSON response:
```json
{
  "ok": true,
  "result": true,
  "description": "Webhook was set"
}
```

### Step 3: Verify Bot Authorization

Visit:
```
https://your-worker-url.workers.dev/getMe
```

You should see your bot information:
```json
{
  "id": 1234567890,
  "is_bot": true,
  "first_name": "My FileStream Bot",
  "username": "myfilestream_bot",
  ...
}
```

---

## Part 5: Testing

### Test 1: Start Bot

1. Open Telegram
2. Search for your bot (@your_bot_username)
3. Send `/start`
4. You should receive a welcome message

### Test 2: Upload File

1. Send any file (image, video, document) to your bot
2. You should receive:
   - Stream and download links
   - Revoke token
   - Inline buttons

### Test 3: Check Files

1. Send `/files` to your bot
2. You should see a list of uploaded files
3. Click on a file to view details

### Test 4: Check Stats

1. Send `/stats` to your bot
2. You should see your statistics:
   - Total files
   - Active files
   - Total downloads

### Test 5: Stream File

1. Click "🌐 Stream Page" button on any file
2. Browser should open with a player
3. Try playing the video/audio

---

## Part 6: Troubleshooting

### Bot doesn't respond

**Check webhook:**
```bash
curl https://your-worker-url.workers.dev/getMe
```

If this fails, re-register webhook:
```
https://your-worker-url.workers.dev/registerWebhook
```

### Database errors

**Verify database:**
```bash
wrangler d1 execute filestream_db --command="SELECT COUNT(*) FROM users"
```

**Re-apply schema if needed:**
```bash
wrangler d1 execute filestream_db --file=schema.sql
```

### Channel forwarding fails

**Verify:**
1. Bot is admin in channel
2. Bot has "Edit Messages" permission
3. Channel ID starts with `-100`

### Files not downloading

**Check file size:**
- Files over 100MB may not stream via worker
- Use Telegram link instead for large files

---

## Part 7: Maintenance

### View Logs

```bash
wrangler tail
```

This shows real-time logs from your worker.

### Update Bot

After making changes to `worker.js`:

```bash
wrangler deploy
```

### Backup Database

```bash
wrangler d1 export filestream_db --output=backup.sql
```

### Query Database

View all users:
```bash
wrangler d1 execute filestream_db --command="SELECT * FROM users"
```

View all files:
```bash
wrangler d1 execute filestream_db --command="SELECT file_name, downloads FROM files LIMIT 10"
```

---

## Part 8: Making Bot Public

To allow anyone to use your bot:

1. Open `worker.js`
2. Find: `const PUBLIC_BOT = false;`
3. Change to: `const PUBLIC_BOT = true;`
4. Deploy: `wrangler deploy`

---

## Part 9: Custom Domain (Optional)

### Add Custom Domain

1. Go to Cloudflare Dashboard
2. Navigate to Workers & Pages → Your Worker
3. Click "Triggers" tab
4. Click "Add Custom Domain"
5. Enter your domain (e.g., `bot.yourdomain.com`)
6. Wait for DNS propagation

### Update Webhook

After adding custom domain:
```
https://bot.yourdomain.com/registerWebhook
```

---

## 🎉 Congratulations!

Your FileStream Bot is now live! 

### What's Next?

- Share bot link with friends
- Monitor usage with `/stats`
- Check logs with `wrangler tail`
- Customize bot messages in `worker.js`

### Need Help?

- Check the [README.md](README.md) for detailed features
- Review Cloudflare Workers docs
- Check Telegram Bot API documentation

---

## 📊 Quick Reference

### Important URLs

- Bot: `https://t.me/your_bot_username`
- Worker: `https://your-worker.workers.dev`
- Register Webhook: `https://your-worker.workers.dev/registerWebhook`
- Get Bot Info: `https://your-worker.workers.dev/getMe`

### Important Commands

```bash
# Deploy
wrangler deploy

# View logs
wrangler tail

# Database query
wrangler d1 execute filestream_db --command="YOUR_SQL"

# Database backup
wrangler d1 export filestream_db --output=backup.sql
```

### Bot Commands

```
/start - Start bot
/files - View files
/stats - View statistics
/revoke [hash] [token] - Revoke file
/revokeall - Delete all files (owner only)
```

---

**Happy Streaming! 🚀**
