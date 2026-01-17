# Streamfile Worker - Ultimate Premium Edition
File To Link Telegram Bot Using Cloudflare Workers.

## ✨ Premium Features

### 🚀 Core Features
- **Smart Streaming**: Automatic detection of video/audio files for streaming
- **Rate Limiting**: Built-in protection against abuse (30 requests/minute per user)
- **File Validation**: Automatic file size and type validation
- **Enhanced Security**: Multiple layers of security and error handling
- **Statistics Tracking**: Built-in analytics for monitoring usage
- **Clean UI**: Modern, responsive interface with glassmorphism design

### 🎯 File Type Support
- **Streamable**: MP4, MKV, WebM, AVI, MOV, FLV, MP3, AAC, FLAC, OGG, OPUS
- **All Files**: Support for documents, images, and other file types
- **Smart Buttons**: Context-aware button display based on file type

### 🔒 Security Features
- Rate limiting per user
- File size validation (up to 4GB)
- Secure hash-based link generation
- Bot secret token validation
- Channel authorization checks

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
const OWNER_USERNAME = "FLiX_LY"; // Your telegram username.
const BOT_NAME = "FileStream Bot"; // Your bot display name.
const ENABLE_STATS = true; // Enable statistics tracking.
const RATE_LIMIT_REQUESTS = 30; // Max requests per minute.
const MAX_FILE_SIZE = 4294967296; // 4GB in bytes.
const MONGODB_URI = "MONGODB_URI"; // MongoDB connection string with API key.
const MONGODB_DATABASE = "filestream"; // MongoDB database name.
const MONGODB_COLLECTION = "files"; // MongoDB collection name.
```

### MongoDB Setup:
1. Create a free [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) account
2. Create a new cluster (free M0 tier is sufficient)
3. Go to "Data API" section in your cluster
4. Enable Data API and create an API key
5. Copy the API key and use it in `MONGODB_URI`
6. Format: `your-api-key-here` (just the API key, not the full connection string)
7. The bot will automatically use MongoDB Data API endpoints

**Why MongoDB?**
- **Reliable**: No more editMessage issues with Telegram API
- **Fast**: Quick lookups for file metadata
- **Scalable**: Can handle millions of files
- **Persistent**: File metadata stored permanently
- **Fallback**: Falls back to editMessage if MongoDB is unavailable

### Setup:
- Get `BOT_TOKEN` from [@botfather](https://t.me/botfather).
    - Turn on `inline mode` in bot settings.
    - Disable `inline feedback` for better results.
- Change `BOT_WEBHOOK` with your preferred webhook.
- Change `BOT_SECRET` with a powerful secret text (only `[A-Z, a-z, 0-9, _, -]` are allowed).
- Change `SIA_SECRET` with a powerful secret text using [password-generator](https://1password.com/password-generator).
- Change `PUBLIC_BOT` to make your bot public (only `[true, false]` are allowed).
- Get `BOT_OWNER` from [@idbot](https://t.me/username_to_id_bot).
- Get `BOT_CHANNEL` id by forwarding a message from channel to [@idbot](https://t.me/username_to_id_bot).
  - Channel **ID** must start with `-100`.
  - Bot must be **admin** in channel with **edit rights**.

<br>

## ⚙️Deploy
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

[![Deploy to Cloudflare Workers](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=https://github.com/vauth/filestream-cf)

### Setup:
- Once you deployed the bot on Cloudflare.
- Check `XXX.XXXX.workers.dev/getMe` to verify your bot authorization.
- Open `XXX.XXXX.workers.dev/registerWebhook` to register your bot webhook.
- Then you can start using your bot.

<br>

## 📚 Response

### For Video/Audio Files:
```python
Stream Page: XX.XX.workers.dev/stream?file=GRJUYMDDJRFGK
Download Link: XX.XX.workers.dev/?file=GRJUYMDDJRFGK
Stream Link: XX.XX.workers.dev/?file=GRJUYMDDJRFGK&mode=inline
VLC Link: vlc://XX.XX.workers.dev/?file=GRJUYMDDJRFGK&mode=inline
Telegram Link: t.me/usernamebot/?start=GRJUYMDDJRFGK
```

### For Other Files:
```python
Download Link: XX.XX.workers.dev/?file=GRJUYMDDJRFGK
Telegram Link: t.me/usernamebot/?start=GRJUYMDDJRFGK
```

### Button Layout:
- **Video/Audio**: Stream | Download | VLC Player | Copy Download Link
- **Other Files**: Download | Copy Download Link | Telegram

### Limitations:
- Telegram Link: `<4.00GB`
- Inline Link: `<4.00GB`
- Download Link: `<20.00MB`
- Stream Link: `<20.00MB`
- Rate Limit: `30 requests/minute per user`

<br>

## 🎯 Key Improvements

### 1. MongoDB Integration ✨ NEW!
- **Fixed editMessage issues**: No more Telegram API rate limits or errors
- File metadata stored in MongoDB for instant retrieval
- Fallback to editMessage for backward compatibility
- Faster file access and streaming
- Persistent storage of file information
- Automatic storage when files are uploaded

### 2. Fixed Link Generation Issue
- Bot now properly responds with links after file is forwarded to channel
- Added comprehensive error handling for channel forwarding
- Better validation of message IDs from channel

### 3. Smart Streaming
- Stream option only available for video/audio files
- Automatic MIME type detection
- Support for 18+ video/audio formats

### 4. Simplified Button Layout
- Video/Audio: 4 focused buttons (Stream, Download, VLC, Copy Link)
- Other Files: 3 essential buttons (Download, Copy Link, Telegram)
- Clean, intuitive user experience

### 5. Enhanced Security
- Rate limiting (30 requests/minute per user)
- File size validation (max 4GB)
- Better error messages
- Request validation

### 6. Better User Experience
- Modern, responsive UI
- Clear error messages
- File type indicators
- Formatted file sizes
- Loading states

<br>

## 📷 Screenshot

<a href="#Screenshot"><img src="https://github.com/user-attachments/assets/09101285-c68c-44a1-aaa1-e2d5c4c0cf90" width="300px"></a>

<br>

## 🛠️ Advanced Features

### Statistics Endpoint
Access statistics at: `XXX.XXXX.workers.dev/stats?d=YOUR_BOT_SECRET`

### Supported Streaming Formats
**Video**: MP4, MKV, WebM, QuickTime, AVI, MPEG, 3GP, FLV, WMV  
**Audio**: MP3, MP4, WAV, OGG, WebM, FLAC, AAC, M4A, OPUS

### Rate Limiting
- Default: 30 requests per minute per user
- Customizable via `RATE_LIMIT_REQUESTS` variable
- Automatic reset every 60 seconds

<br>

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!

## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Credits
- Original Project: [vauth/filestream-cf](https://github.com/vauth/filestream-cf)
- Enhanced by: AI Development Team
- Powered by: Cloudflare Workers

<br>

---

<div align="center">
  <b>Made with ❤️ by developers, for developers</b>
</div>
