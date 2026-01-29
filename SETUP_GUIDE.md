# FileStream Bot - Setup Guide

## 📋 Prerequisites

Before starting, you need:

1. **Telegram Bot Token**
   - Open [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot` and follow instructions
   - Copy the bot token (format: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
   - Send `/setinline` to enable inline mode
   - Send `/setinlinefeedback` and choose "Disabled"

2. **Telegram API Credentials**
   - Go to [my.telegram.org](https://my.telegram.org)
   - Login with your phone number
   - Click "API Development Tools"
   - Create a new application
   - Copy `api_id` (number) and `api_hash` (string)

3. **Your Telegram User ID**
   - Open [@userinfobot](https://t.me/userinfobot) on Telegram
   - Send any message
   - Copy your user ID (number)

4. **Telegram Channel**
   - Create a private channel on Telegram
   - Add your bot as admin with "Edit Messages" permission
   - Forward any message from the channel to [@userinfobot](https://t.me/userinfobot)
   - Copy the channel ID (must start with `-100`, e.g., `-1001234567890`)

5. **Generate Secret Key**
   ```bash
   openssl rand -hex 32
   ```
   Or use any strong random string (32+ characters)

## 🐳 Quick Start with Docker (Recommended)

### Step 1: Install Docker

**Ubuntu/Debian:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

**macOS:**
```bash
brew install --cask docker
```

**Windows:**
- Download [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Install and restart

### Step 2: Clone & Configure

```bash
# Clone repository (replace with your repo URL)
git clone <your-repo-url>
cd webapp

# Copy environment template
cp .env.example .env

# Edit configuration
nano .env  # or use your favorite editor
```

### Step 3: Configure Environment

Edit `.env` file and add your credentials:

```env
# Bot Configuration
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id_here
API_HASH=your_api_hash_here

# Bot Owner & Channel
BOT_OWNER=your_user_id_here
BOT_CHANNEL=your_channel_id_here
OWNER_USERNAME=your_telegram_username
BOT_NAME=FileStream Bot

# Security (generate with: openssl rand -hex 32)
SIA_SECRET=your_random_secret_key_here

# Access Control
PUBLIC_BOT=false  # Set to true for public access

# MongoDB Configuration
MONGO_URI=mongodb://mongodb:27017/
DATABASE_NAME=filestream

# Web Server Configuration
HOST=0.0.0.0
PORT=8080
BASE_URL=http://localhost:8080  # Change to your domain
```

### Step 4: Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### Step 5: Access

- **Web Interface**: http://localhost:8080
- **Bot**: https://t.me/<your_bot_username>
- **Health Check**: http://localhost:8080/health

### Step 6: Test

1. Open your bot on Telegram
2. Send `/start` command
3. Send any file (image, video, etc.)
4. Click on the stream page link
5. Watch your file streaming!

## 🔧 Manual Installation (Without Docker)

### Step 1: Install MongoDB

**Ubuntu/Debian:**
```bash
# Import MongoDB public GPG key
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

# Add MongoDB repository
echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Install MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify
sudo systemctl status mongod
```

**macOS:**
```bash
# Install with Homebrew
brew tap mongodb/brew
brew install mongodb-community@7.0

# Start MongoDB
brew services start mongodb-community@7.0

# Verify
brew services list
```

### Step 2: Install Python Dependencies

```bash
# Ensure Python 3.11+ is installed
python3 --version

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env
```

Add your credentials as shown in Docker setup.

### Step 4: Run Bot

```bash
# Make sure MongoDB is running
sudo systemctl status mongod  # Linux
brew services list            # macOS

# Start bot
python main.py
```

## 🌐 Deploy to Production

### Option 1: VPS Deployment

1. **Get a VPS** (DigitalOcean, AWS, etc.)

2. **Point domain to VPS**
   ```
   Type: A
   Name: @
   Value: your_vps_ip
   ```

3. **Install Docker on VPS**
   ```bash
   ssh user@your_vps_ip
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```

4. **Clone and configure**
   ```bash
   git clone <your-repo>
   cd webapp
   cp .env.example .env
   nano .env
   # Update BASE_URL to https://yourdomain.com
   ```

5. **Setup reverse proxy (Nginx)**
   ```bash
   sudo apt install nginx certbot python3-certbot-nginx
   
   # Create Nginx config
   sudo nano /etc/nginx/sites-available/filestream
   ```

   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://localhost:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           
           # For large file uploads
           client_max_body_size 4G;
       }
   }
   ```

   ```bash
   # Enable site
   sudo ln -s /etc/nginx/sites-available/filestream /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   
   # Get SSL certificate
   sudo certbot --nginx -d yourdomain.com
   ```

6. **Start services**
   ```bash
   docker-compose up -d
   ```

### Option 2: Heroku Deployment

1. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

2. **Add MongoDB addon**
   ```bash
   heroku addons:create mongolab:sandbox
   ```

3. **Set environment variables**
   ```bash
   heroku config:set BOT_TOKEN=your_token
   heroku config:set API_ID=your_id
   # ... set all variables
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

## 🔍 Troubleshooting

### Port 8080 already in use
```bash
# Find process using port
lsof -i :8080

# Kill process
kill -9 <PID>

# Or change port in .env
PORT=8081
```

### MongoDB connection failed
```bash
# Check MongoDB status
sudo systemctl status mongod

# Restart MongoDB
sudo systemctl restart mongod

# Check logs
sudo tail -f /var/log/mongodb/mongod.log
```

### Bot not responding
```bash
# Check bot token
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe

# Check logs
docker-compose logs bot
# or
tail -f logs/bot.log
```

### Files not streaming
1. Verify BASE_URL is correct
2. Check bot is admin in channel
3. Verify channel ID starts with `-100`
4. Check file exists: docker-compose logs bot

## 📊 Monitoring

### View logs
```bash
# All services
docker-compose logs -f

# Only bot
docker-compose logs -f bot

# Only MongoDB
docker-compose logs -f mongodb
```

### Check database
```bash
# Connect to MongoDB
docker exec -it filestream_mongodb mongosh

# Switch to database
use filestream

# View files
db.files.find().pretty()

# Count documents
db.files.countDocuments()
db.users.countDocuments()
```

### Health check
```bash
curl http://localhost:8080/health
```

## 🔄 Updates

```bash
# Pull latest changes
git pull

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🛠️ Maintenance

### Backup database
```bash
# Create backup
docker exec filestream_mongodb mongodump --out /data/backup

# Copy backup from container
docker cp filestream_mongodb:/data/backup ./backup
```

### Restore database
```bash
# Copy backup to container
docker cp ./backup filestream_mongodb:/data/backup

# Restore
docker exec filestream_mongodb mongorestore /data/backup
```

### Clean up
```bash
# Remove old images
docker image prune -a

# Remove stopped containers
docker container prune

# Remove unused volumes
docker volume prune
```

## 📞 Support

- Create issue on GitHub
- Contact: [@your_username](https://t.me/your_username)
- Documentation: Check PYTHON_README.md

## ✅ Checklist

Before going live:

- [ ] All environment variables set
- [ ] MongoDB running and accessible
- [ ] Bot token valid
- [ ] Bot is admin in channel
- [ ] Channel ID correct (starts with -100)
- [ ] BASE_URL points to your domain
- [ ] SSL certificate installed (for HTTPS)
- [ ] Firewall configured (allow ports 80, 443)
- [ ] Backup strategy in place
- [ ] Monitoring setup

---

Good luck! 🚀
