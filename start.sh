#!/bin/bash

# FileStream Bot - Quick Start Script

echo "=================================="
echo "🚀 FileStream Bot - Quick Start"
echo "=================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please edit .env file with your credentials before running the bot"
    echo ""
    echo "Required variables:"
    echo "  - BOT_TOKEN (from @BotFather)"
    echo "  - API_ID (from my.telegram.org)"
    echo "  - API_HASH (from my.telegram.org)"
    echo "  - BOT_OWNER (your user ID)"
    echo "  - BOT_CHANNEL (channel ID starting with -100)"
    echo "  - SIA_SECRET (random secret key)"
    echo ""
    echo "Run: nano .env"
    exit 1
fi

# Check if Docker is installed
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "🐳 Docker detected!"
    echo ""
    echo "Starting services with Docker Compose..."
    docker-compose up -d
    echo ""
    echo "✅ Services started!"
    echo ""
    echo "📊 View logs: docker-compose logs -f"
    echo "🔍 Check status: docker-compose ps"
    echo "🛑 Stop services: docker-compose down"
    echo ""
    echo "🌐 Web Interface: http://localhost:8080"
    echo "🤖 Bot: https://t.me/<your_bot_username>"
else
    echo "⚠️  Docker not found. Using manual installation..."
    echo ""
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is not installed!"
        echo "Please install Python 3.11 or higher"
        exit 1
    fi
    
    echo "🐍 Python detected: $(python3 --version)"
    echo ""
    
    # Check if MongoDB is running
    if ! pgrep -x "mongod" > /dev/null; then
        echo "⚠️  MongoDB is not running!"
        echo "Please start MongoDB: sudo systemctl start mongod"
        exit 1
    fi
    
    echo "🍃 MongoDB is running"
    echo ""
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    echo "📚 Installing dependencies..."
    pip install -r requirements.txt
    echo ""
    
    # Run the bot
    echo "🚀 Starting bot..."
    python3 main.py
fi
