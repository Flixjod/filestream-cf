# 🌟 Premium FileStream Bot - Cloudflare Workers

A powerful Telegram bot that converts files into instant streaming links with a beautiful UI, database integration, and advanced file management features.

## ✨ Features

### 🎨 Premium UI
- **Stunning Home Page** - Animated background, modern design with gradient effects
- **Beautiful Streaming Page** - Embedded video/audio player with multiple playback options
- **Responsive Design** - Works perfectly on all devices

### 💾 Database Integration (Cloudflare D1)
- **File Tracking** - Store file metadata, download stats, and user information
- **User Management** - Track all users and their uploaded files
- **Statistics** - View bot statistics (total files, users, downloads)

### 🔐 Security & Management
- **Secret Tokens** - Each file gets a unique secret token for revocation
- **/revoke** - Users can delete their files using secret tokens
- **/revokeall** - Owner can delete all files at once
- **Revoke Button** - Each file message includes a revoke button

### 📂 File Management
- **/files** - View all your files with inline buttons
- **File Details** - View file info, links, and download stats
- **Easy Navigation** - Inline buttons for quick access

### 🌐 Modern URL Structure
- Stream: `domain/stream/FileID`
- Download: `domain/dl/FileID`
- Stream Page: `domain/streampage?file=FileID`

### 📢 Custom Channel Format
When files are copied to channel, they show:
```
RᴇQᴜᴇꜱᴛᴇᴅ ʙʏ : 🍃⏤͟͟͞͞ Username
Uꜱᴇʀ ɪᴅ : 123456789
Fɪʟᴇ ɴᴀᴍᴇ : example.mp4
```

<br>

## 🗂 Variables
```javascript
const BOT_TOKEN = "BOT_TOKEN"; // Insert your bot token.
const BOT_WEBHOOK = "/endpoint"; // Let it be as it is.
const BOT_SECRET = "BOT_SECRET"; // Insert a powerful secret text.
const BOT_OWNER = 123456789; // Insert your telegram account id.
const BOT_CHANNEL = -100123456789; // Insert telegram channel id.
const SIA_SECRET = "SIA_SECRET"; // Insert a powerful secret text.
const PUBLIC_BOT = false; // Make your bot public.
const OWNER_USERNAME = "your_username"; // Your Telegram username.
const BOT_NAME = "FileStream Bot"; // Your bot name.
```

### Setup:
- Get `BOT_TOKEN` from [@botfather](https://t.me/botfather).
    - Turn on `inline mode` in bot settings.
    - Disable `inline feedback` for better results.
- Change `BOT_WEBHOOK` with your preferred webhook.
- Change `BOT_SECRET` with a powerful secret text (only `[A-Z, a-z, 0-9, _, -]` are allowed).
- Change `SIA_SECRET` with a powerful secret text using [password-generator](https://1password.com/password-generator).
- Change `PUBLIC_BOT` to make your bot public (only `[true, false]` are allowed).
- Change `OWNER_USERNAME` to your Telegram username (without @).
- Change `BOT_NAME` to your preferred bot name.
- Get `BOT_OWNER` from [@idbot](https://t.me/username_to_id_bot).
- Get `BOT_CHANNEL` id by forwarding a message from channel to [@idbot](https://t.me/username_to_id_bot).
  - Channel **ID** must start with `-100`.
  - Bot must be **admin** in channel with **edit rights**.

<br>

## ⚙️ Deploy

### Step 1: Deploy Worker
- Create a [Cloudflare](https://www.cloudflare.com/) **account**.
- Navigate to `Workers & Pages > Create > Create Worker`.
- Deploy the worker by clicking **Deploy**.
- Edit the code by clicking **Edit Code**.
- **Manually:**
    - Upload `worker.js` into **Cloudflare**.
    - Modify the [variables](#-variables).
- **Dynamic:**
    - Generate the code using [code generator](https://vauth.github.io/filestream-cf/).
    - Copy paste the generated code to cloudflare workers.
- Finally, **Deploy**.

### Step 2: Setup D1 Database (Optional but Recommended)
To enable all advanced features like /files, /revoke, statistics, etc:

1. **Create D1 Database:**
```bash
wrangler d1 create filestream-db
```

2. **Update wrangler.toml** with the database binding from Step 1

3. **Initialize Database:**
```bash
wrangler d1 execute filestream-db --file=./schema.sql
```

4. **Deploy with Database:**
```bash
wrangler deploy
```

📚 **Full D1 Setup Guide:** See [D1_SETUP.md](./D1_SETUP.md) for detailed instructions.

[![Deploy to Cloudflare Workers](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=https://github.com/vauth/filestream-cf)

### Step 3: Register Webhook
- Once you deployed the bot on Cloudflare.
- Check `XXX.XXXX.workers.dev/getMe` to verify your bot authorization.
- Open `XXX.XXXX.workers.dev/registerWebhook` to register your bot webhook.
- Then you can start using your bot!

<br>

## 📚 Bot Commands

### User Commands:
- **/start** - Start the bot and get welcome message
- **/files** - View all your uploaded files with inline buttons
- **/revoke <token>** - Revoke/delete a file using its secret token

### Owner Commands:
- **/stats** - View bot statistics (total files, users, downloads)
- **/revokeall** - Delete all files from database and channel

## 🔗 Link Types

### New URL Structure:
```
Stream Link: domain/stream/FileID
Download Link: domain/dl/FileID
Stream Page: domain/streampage?file=FileID
Telegram Link: t.me/botusername/?start=FileID
Inline Query: @botusername FileID
```

### File Size Limitations:
- **Telegram/Inline:** Up to 4GB
- **Direct Stream/Download:** Up to 2GB (for best performance)
- Files larger than 2GB can still be accessed via Telegram

<br>

## 📷 Screenshots

### Premium Home Page
- Animated gradient background
- Modern card-based design
- Feature highlights
- How it works section
- Statistics display

### Beautiful Streaming Page
- Embedded video/audio player
- Multiple download options
- VLC & MX Player integration
- Copy link functionality
- Share options
- Responsive design

### File Management
- List all your files
- View file details
- Download statistics
- Easy revoke access
- Inline button navigation

<br>

## 🎯 Key Features Implemented

✅ Premium animated home page  
✅ Beautiful streaming page with player  
✅ Cloudflare D1 database integration  
✅ File tracking and statistics  
✅ User management system  
✅ Secret token generation  
✅ /revoke command with token  
✅ /revokeall command for owner  
✅ Revoke button on file messages  
✅ /files command with inline buttons  
✅ Custom channel message format  
✅ Modern URL structure (/stream/ID, /dl/ID)  
✅ Download counter  
✅ File details view  
✅ User statistics  

<br>

## 🔧 Advanced Configuration

### Enable D1 Database
Edit `wrangler.toml` and add:
```toml
[[d1_databases]]
binding = "DB"
database_name = "filestream-db"
database_id = "your-database-id-here"
```

### Database Tables
- **files** - Stores file metadata, tokens, and download stats
- **users** - Stores user information and activity

### Security Features
- Unique secret tokens for each file
- User-specific file access
- Owner-only admin commands
- Secure token validation

<br>

## 💡 Tips

1. **Database is Optional** - The bot works without D1, but you'll miss out on:
   - /files command
   - /revoke command
   - Statistics tracking
   - Download counting

2. **For Best Experience** - Set up D1 database following [D1_SETUP.md](./D1_SETUP.md)

3. **Free Tier Friendly** - Both Cloudflare Workers and D1 have generous free tiers

4. **Channel Setup** - Make sure bot is admin in channel with edit rights

5. **Inline Mode** - Enable inline mode in BotFather for sharing functionality

<br>

## 🛠️ Development

### Local Testing
```bash
# Install dependencies
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Test locally
wrangler dev --local
```

### Deploy
```bash
# Deploy to production
wrangler deploy
```

<br>

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<br>

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

<br>

## ⭐ Support

If you like this project, please give it a ⭐ star on GitHub!

<br>

## 📞 Contact

- Telegram: [@FLiX_LY](https://t.me/FLiX_LY)
- GitHub: [@vauth](https://github.com/vauth)

---

<div align="center">
Made with ❤️ by vauth
</div>
