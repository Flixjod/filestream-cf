#!/usr/bin/env python3
"""
FileStream Bot - Main Entry Point
A Python-based Telegram bot for file streaming with web interface
"""

import asyncio
import os
import sys
from threading import Thread
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config import Config
from bot.bot import FileStreamBot
from bot.web_server import run_web_server

def start_web_server():
    """Start Flask web server in separate thread"""
    run_web_server()

def main():
    """Main entry point"""
    # Display configuration
    Config.display()
    
    # Validate configuration
    if not Config.validate():
        print("\n❌ Configuration validation failed!")
        print("Please set all required environment variables in .env file")
        sys.exit(1)
    
    print("\n🚀 Starting FileStream Bot...")
    
    # Start web server in background thread
    web_thread = Thread(target=start_web_server, daemon=True)
    web_thread.start()
    
    # Start Telegram bot
    bot = FileStreamBot()
    
    try:
        print("✅ All services started successfully!")
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
