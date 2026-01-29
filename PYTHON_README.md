# FileStream Bot - Python Edition

A powerful Telegram bot for file streaming and downloading, built with Pyrogram, Flask, MongoDB, and Docker. Convert your Telegram files into direct streaming links with a premium web interface.

## ✨ Features

- 🚀 **Lightning Fast Streaming** - Direct file streaming from Telegram servers
- 🔐 **Secure & Private** - HMAC-SHA256 encrypted file hashes with revocation support
- 📱 **Multi-Platform** - Works on web browsers, VLC, MX Player, and more
- 💾 **MongoDB Database** - Store file metadata, user data, and download statistics
- 🎨 **Premium UI** - Beautiful, responsive streaming pages with video/audio players
- 🐳 **Docker Support** - Easy deployment with Docker Compose
- 📊 **Statistics** - Track total files, users, and downloads
- 🔄 **File Management** - View, share, and revoke files anytime
- ⚡ **Range Requests** - Support for seeking in videos and resumable downloads
- 🌐 **RESTful API** - Clean web interface for file streaming

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Telegram Bot   │◄────►│  Flask Web App   │◄────►│    MongoDB      │
│   (Pyrogram)    │      │   (Streaming)    │      │   (Database)    │
└─────────────────┘      └──────────────────┘      └─────────────────┘
         │                         │
         │                         │
         ▼                         ▼
  ┌─────────────┐          ┌──────────────┐
  │   Users     │          │   Browsers   │
  │  (Upload)   │          │  (Stream)    │
  └─────────────┘          └──────────────┘
```

## 📋 Requirements

- Python 3.11+
- MongoDB 7.0+
- Docker & Docker Compose (optional)
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Telegram API ID & Hash (from [my.telegram.org](https://my.telegram.org))

## 🚀 Installation

### Method 1: Docker Compose (Recommended)

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd webapp
```

2. **Configure environment variables**
```bash
cp .env.example .env
nano .env  # Edit with your values
```

3. **Start services**
```bash
docker-compose up -d
```

4. **View logs**
```bash
docker-compose logs -f
```

5. **Access the application**
- Bot: `https://t.me/<your_bot_username>`
- Web: `http://localhost:8080`

### Method 2: Manual Installation

1. **Install MongoDB**
```bash
# Ubuntu/Debian
sudo apt-get install mongodb

# macOS
brew install mongodb-community

# Start MongoDB
sudo systemctl start mongod  # Linux
brew services start mongodb-community  # macOS
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
nano .env  # Edit with your values
```

4. **Run the bot**
```bash
python main.py
```

## ⚙️ Configuration

Edit `.env` file with your credentials:

```env
# Bot Configuration
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
API_ID=12345678
API_HASH=0123456789abcdef0123456789abcdef

# Bot Owner & Channel
BOT_OWNER=123456789
BOT_CHANNEL=-1001234567890
OWNER_USERNAME=your_username
BOT_NAME=FileStream Bot

# Security Secret (use strong random string)
SIA_SECRET=your_strong_secret_key_here

# Access Control
PUBLIC_BOT=false

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/
DATABASE_NAME=filestream

# Web Server Configuration
HOST=0.0.0.0
PORT=8080
BASE_URL=http://localhost:8080
```

### How to Get Credentials

1. **BOT_TOKEN**: Create a bot via [@BotFather](https://t.me/botfather)
   - Send `/newbot` to create a new bot
   - Enable inline mode: `/setinline`
   - Disable inline feedback: `/setinlinefeedback`

2. **API_ID & API_HASH**: Get from [my.telegram.org](https://my.telegram.org)
   - Login with your phone number
   - Go to "API Development Tools"
   - Create a new application

3. **BOT_OWNER**: Your Telegram user ID
   - Get from [@userinfobot](https://t.me/userinfobot)

4. **BOT_CHANNEL**: Create a private channel
   - Add your bot as admin with edit rights
   - Forward a message from channel to [@userinfobot](https://t.me/userinfobot)
   - ID should start with `-100`

5. **SIA_SECRET**: Generate strong random string
   - Use: `openssl rand -hex 32`

## 📚 Usage

### Bot Commands

- `/start` - Start the bot and get welcome message
- `/files` - View all your uploaded files
- `/revoke <token>` - Revoke a specific file
- `/stats` - View bot statistics (owner only)
- `/revokeall` - Delete all files (owner only)

### Uploading Files

1. Send any file (video, audio, document, image) to the bot
2. Bot uploads to channel and generates links
3. You get:
   - 🌐 Stream Page (premium player)
   - 📥 Download Link
   - 💬 Telegram Link
   - 🔁 Inline Share
   - 🗑️ Revoke Button

### Streaming Files

**URL Formats:**
```
Stream: http://your-domain/stream/<file_hash>
Download: http://your-domain/dl/<file_hash>
Stream Page: http://your-domain/streampage?file=<file_hash>
```

**Features:**
- Video/Audio player with controls
- Range requests (seeking support)
- Download button
- Copy link button
- VLC/MX Player integration
- File statistics

### Inline Mode

Share files via inline mode:
```
@your_bot_username <file_hash>
```

## 🎨 Premium Web Interface

### Home Page (`/`)
- Animated background
- Feature showcase
- How it works section
- Statistics display
- Mobile responsive

### Stream Page (`/streampage`)
- HTML5 video/audio player
- File information card
- Download statistics
- Multiple download options
- Social sharing
- Copy link functionality
- VLC/MX Player support

## 🔧 Development

### Project Structure

```
webapp/
├── bot/
│   ├── __init__.py
│   ├── bot.py           # Telegram bot handlers
│   ├── database.py      # MongoDB operations
│   ├── utils.py         # Utility functions
│   └── web_server.py    # Flask web application
├── templates/
│   ├── home.html        # Landing page
│   └── stream.html      # Premium streaming page
├── static/
│   ├── css/
│   └── js/
├── config.py            # Configuration management
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker container config
├── docker-compose.yml   # Docker Compose config
├── .env.example         # Environment template
└── README.md            # This file
```

### Key Components

**bot.py** - Telegram Bot
- Message handlers
- Command processing
- Inline query handling
- Callback query handling
- File upload management

**database.py** - MongoDB Operations
- File CRUD operations
- User management
- Statistics tracking
- Async operations with Motor

**web_server.py** - Flask Web Server
- File streaming endpoint
- Range request support
- Template rendering
- Health check endpoint

**utils.py** - Utilities
- Cryptographic functions (HMAC-SHA256)
- File size formatting
- Markdown escaping
- Token generation

## 🔐 Security Features

- **HMAC-SHA256 Hash**: Secure file ID encryption
- **Secret Tokens**: Unique revocation tokens per file
- **Access Control**: Public/private bot modes
- **Owner Verification**: Admin commands restricted to owner
- **Database Validation**: Input sanitization
- **Secure Sessions**: Pyrogram session management

## 📊 Database Schema

### Files Collection
```javascript
{
  _id: ObjectId,
  file_id: String,        // Telegram file ID
  message_id: String,     // Channel message ID
  user_id: String,        // Uploader user ID
  username: String,       // Uploader username
  file_name: String,      // Original filename
  file_size: Number,      // File size in bytes
  file_type: String,      // video/audio/document/image
  secret_token: String,   // Revocation token
  created_at: DateTime,   // Upload timestamp
  downloads: Number       // Download count
}
```

### Users Collection
```javascript
{
  _id: ObjectId,
  user_id: String,        // Telegram user ID
  username: String,       // Username
  first_name: String,     // First name
  last_name: String,      // Last name
  first_used: DateTime,   // First interaction
  total_files: Number,    // Total files uploaded
  last_activity: DateTime // Last activity
}
```

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Rebuild images
docker-compose build --no-cache

# Remove volumes
docker-compose down -v
```

## 🔍 Troubleshooting

### Bot not starting
- Check if all required environment variables are set
- Verify BOT_TOKEN is correct
- Ensure MongoDB is running
- Check logs: `docker-compose logs bot`

### Files not streaming
- Verify BASE_URL is correct
- Check if bot has admin rights in channel
- Ensure file exists in channel
- Check file size limits

### Database connection failed
- Verify MONGO_URI is correct
- Ensure MongoDB is running
- Check network connectivity
- Review MongoDB logs

### Port already in use
- Change PORT in .env file
- Stop conflicting service
- Use different port mapping in docker-compose.yml

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Credits

- Original concept from [filestream-cf](https://github.com/vauth/filestream-cf)
- Built with [Pyrogram](https://pyrogram.org/)
- Database: [MongoDB](https://www.mongodb.com/)
- Web Framework: [Flask](https://flask.palletsprojects.com/)

## 📞 Support

- Create an issue on GitHub
- Contact: [@your_username](https://t.me/your_username)
- Documentation: [GitHub Wiki](https://github.com/your-repo/wiki)

## 🚀 Roadmap

- [ ] Add authentication system
- [ ] Implement file expiration
- [ ] Add thumbnail generation
- [ ] Support for batch uploads
- [ ] Admin dashboard
- [ ] API rate limiting
- [ ] Multiple language support
- [ ] Cloud storage integration

## ⚠️ Disclaimer

This bot is for educational purposes. Ensure you comply with:
- Telegram's Terms of Service
- Copyright laws in your jurisdiction
- Privacy regulations (GDPR, etc.)

Do not use this bot for:
- Distributing copyrighted content
- Illegal file sharing
- Violating Telegram's policies

---

Made with ❤️ by [@your_username](https://t.me/your_username)
