# FileStream Bot - Python Version

A powerful Telegram bot for streaming and downloading files with a beautiful web interface. Built with Pyrogram and FastAPI.

## ✨ Features

- 🚀 **Fast Streaming**: Direct file streaming from Telegram's CDN
- 📱 **Responsive Design**: Works perfectly on all devices
- 🔐 **Secure**: HMAC-SHA256 hash verification for file links
- 💾 **MongoDB Database**: Persistent storage for files and users
- 🎬 **Video/Audio Player**: Built-in player with controls
- 📊 **Statistics**: Track downloads and usage
- 🗑️ **File Management**: Revoke access anytime
- 🔗 **Multiple Link Types**: Telegram, Stream, Download

## 🛠️ Requirements

- Python 3.8+
- MongoDB
- Telegram Bot Token
- Telegram API ID & Hash

## 📦 Installation

1. **Clone the repository**:
```bash
git clone https://github.com/Flixjod/filestream-cf.git
cd filestream-cf/python_bot
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
# Create .env file or export variables
export BOT_TOKEN="your_bot_token"
export API_ID="your_api_id"
export API_HASH="your_api_hash"
export BOT_OWNER="your_user_id"
export BOT_CHANNEL="-100your_channel_id"
export MONGODB_URI="mongodb://localhost:27017"
export BASE_URL="https://your-domain.com"
export SECRET_KEY="your-secret-key"
```

4. **Run the bot**:
```bash
python main.py
```

## ⚙️ Configuration

Edit `config.py` or set environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Telegram bot token from @BotFather | Yes |
| `API_ID` | Telegram API ID from my.telegram.org | Yes |
| `API_HASH` | Telegram API Hash from my.telegram.org | Yes |
| `BOT_OWNER` | Your Telegram user ID | Yes |
| `BOT_CHANNEL` | Channel ID for storing files | Yes |
| `MONGODB_URI` | MongoDB connection URI | Yes |
| `BASE_URL` | Your public URL (domain or IP) | Yes |
| `SECRET_KEY` | Secret key for hashing | Yes |
| `BOT_NAME` | Bot display name | No |
| `OWNER_USERNAME` | Your Telegram username | No |
| `PUBLIC_BOT` | Make bot public (true/false) | No |
| `HOST` | Server host (default: 0.0.0.0) | No |
| `PORT` | Server port (default: 8080) | No |

## 🎯 Bot Setup

1. **Create a bot** with @BotFather
2. **Enable inline mode** in bot settings
3. **Disable inline feedback** for better performance
4. **Create a channel** and add bot as admin with edit rights
5. **Get API credentials** from https://my.telegram.org

## 🚀 Deployment

### Using PM2 (Production)

```bash
# Install PM2
npm install -g pm2

# Start bot
pm2 start main.py --name filestream-bot --interpreter python3

# View logs
pm2 logs filestream-bot

# Restart bot
pm2 restart filestream-bot

# Stop bot
pm2 stop filestream-bot
```

### Using Docker

```bash
# Build image
docker build -t filestream-bot .

# Run container
docker run -d \
  --name filestream-bot \
  -e BOT_TOKEN="your_token" \
  -e API_ID="your_id" \
  -e API_HASH="your_hash" \
  -e BOT_OWNER="your_user_id" \
  -e BOT_CHANNEL="-100channel_id" \
  -e MONGODB_URI="mongodb://mongo:27017" \
  -e BASE_URL="https://your-domain.com" \
  -p 8080:8080 \
  filestream-bot
```

### Using Systemd

```bash
# Create service file
sudo nano /etc/systemd/system/filestream-bot.service

# Add service configuration
[Unit]
Description=FileStream Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/python_bot
Environment="BOT_TOKEN=your_token"
Environment="API_ID=your_id"
Environment="API_HASH=your_hash"
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start service
sudo systemctl enable filestream-bot
sudo systemctl start filestream-bot
```

## 📝 Commands

- `/start` - Start the bot
- `/files` - View your uploaded files
- `/revoke <token>` - Revoke file access
- `/stats` - View bot statistics (owner only)
- `/revokeall` - Delete all files (owner only)

## 🔗 URL Structure

- **Stream Page**: `https://your-domain.com/streampage?file=HASH`
- **Direct Stream**: `https://your-domain.com/stream/HASH`
- **Download**: `https://your-domain.com/dl/HASH`
- **Telegram**: `https://t.me/bot_username?start=HASH`

## 🎨 Features Comparison

| Feature | JavaScript (Cloudflare) | Python (This Version) |
|---------|------------------------|----------------------|
| File Size Limit | 2GB (Workers limit) | 4GB (Telegram limit) |
| Database | D1 (SQLite) | MongoDB |
| Bot Framework | Manual HTTP API | Pyrogram |
| Server | Cloudflare Workers | FastAPI + Uvicorn |
| Inline Mode | ✅ | ✅ |
| File Streaming | ✅ | ✅ |
| Range Requests | ✅ | ✅ |
| Download Stats | ✅ | ✅ |
| User Management | ✅ | ✅ |
| Deployment | Cloudflare | Any server/VPS |

## 🔧 Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Telegram  │◄────►│  Pyrogram    │◄────►│  MongoDB    │
│   API       │      │  Bot         │      │  Database   │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐      ┌─────────────┐
                     │   FastAPI    │◄────►│   HTML      │
                     │   Server     │      │  Templates  │
                     └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   Users      │
                     │   (Web/App)  │
                     └──────────────┘
```

## 🔒 Security

- HMAC-SHA256 for file hash verification
- Secret token for file revocation
- MongoDB authentication support
- Environment variable configuration
- No file content stored (only metadata)

## 📊 Performance

- **Async/Await**: Fully asynchronous for better performance
- **Streaming**: Direct streaming without loading into memory
- **MongoDB**: Fast document-based database
- **Pyrogram**: Optimized Telegram client with 20MB file API limit
- **FastAPI**: High-performance async web framework

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

Created by [@FLiX_LY](https://t.me/FLiX_LY)

## 🙏 Credits

- [Pyrogram](https://github.com/pyrogram/pyrogram) - Telegram MTProto API Client
- [FastAPI](https://github.com/tiangolo/fastapi) - Modern web framework
- [MongoDB](https://www.mongodb.com/) - NoSQL database
- Original JavaScript version: [filestream-cf](https://github.com/vauth/filestream-cf)

## ⚠️ Disclaimer

This bot is for educational purposes only. Use at your own risk. Respect Telegram's Terms of Service and local laws.
