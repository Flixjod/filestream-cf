"""
Configuration file for FileStream Bot
"""
import os
from typing import Optional

class Config:
    # Bot Configuration
    BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "BOT_TOKEN")
    API_ID: int = int(os.environ.get("API_ID", "12345"))
    API_HASH: str = os.environ.get("API_HASH", "API_HASH")
    
    # Bot Settings
    BOT_OWNER: int = int(os.environ.get("BOT_OWNER", "1008848605"))
    BOT_CHANNEL: int = int(os.environ.get("BOT_CHANNEL", "-1002199235178"))
    OWNER_USERNAME: str = os.environ.get("OWNER_USERNAME", "FLiX_LY")
    BOT_NAME: str = os.environ.get("BOT_NAME", "FileStream Bot")
    PUBLIC_BOT: bool = os.environ.get("PUBLIC_BOT", "False").lower() == "true"
    
    # MongoDB Configuration
    MONGODB_URI: str = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
    DB_NAME: str = os.environ.get("DB_NAME", "filestream_bot")
    
    # Server Configuration
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", "8080"))
    BASE_URL: str = os.environ.get("BASE_URL", "http://localhost:8080")
    
    # Security
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "your-secret-key-here")
    
    # File Size Limits (in bytes)
    MAX_TELEGRAM_SIZE: int = 4 * 1024 * 1024 * 1024  # 4GB for Telegram
    MAX_STREAM_SIZE: int = 2 * 1024 * 1024 * 1024  # 2GB for streaming
    
    # Cache Settings
    CACHE_DURATION: int = 3600  # 1 hour
    
    # Pyrogram Settings
    WORKERS: int = 4
    SLEEP_THRESHOLD: int = 10

# Singleton instance
config = Config()
