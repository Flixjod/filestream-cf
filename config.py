import os
from typing import Optional

class Config:
    """Configuration class for the bot with environment variable support"""
    
    # Bot Configuration
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    API_ID: int = int(os.getenv("API_ID", "0"))
    API_HASH: str = os.getenv("API_HASH", "")
    
    # Bot Owner & Channel
    BOT_OWNER: int = int(os.getenv("BOT_OWNER", "0"))
    BOT_CHANNEL: int = int(os.getenv("BOT_CHANNEL", "0"))
    OWNER_USERNAME: str = os.getenv("OWNER_USERNAME", "")
    BOT_NAME: str = os.getenv("BOT_NAME", "FileStream Bot")
    
    # Security
    SIA_SECRET: str = os.getenv("SIA_SECRET", "")
    
    # Access Control
    PUBLIC_BOT: bool = os.getenv("PUBLIC_BOT", "false").lower() == "true"
    
    # Database Configuration
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "filestream")
    
    # Web Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8080")
    
    # File Size Limits (in bytes)
    MAX_TELEGRAM_SIZE: int = 4 * 1024 * 1024 * 1024  # 4GB
    MAX_STREAM_SIZE: int = 2 * 1024 * 1024 * 1024  # 2GB
    
    # Cache Configuration
    CACHE_DURATION: int = 3600  # 1 hour
    
    # Session Configuration
    SESSION_NAME: str = "filestream_bot"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required_fields = [
            ("BOT_TOKEN", cls.BOT_TOKEN),
            ("API_ID", cls.API_ID),
            ("API_HASH", cls.API_HASH),
            ("BOT_OWNER", cls.BOT_OWNER),
            ("BOT_CHANNEL", cls.BOT_CHANNEL),
            ("SIA_SECRET", cls.SIA_SECRET),
            ("MONGO_URI", cls.MONGO_URI),
        ]
        
        missing_fields = [field for field, value in required_fields if not value]
        
        if missing_fields:
            print(f"❌ Missing required configuration: {', '.join(missing_fields)}")
            return False
        
        return True
    
    @classmethod
    def display(cls):
        """Display current configuration (hiding sensitive data)"""
        print("=" * 50)
        print("🤖 FileStream Bot Configuration")
        print("=" * 50)
        print(f"Bot Name: {cls.BOT_NAME}")
        print(f"Bot Owner: {cls.BOT_OWNER}")
        print(f"Channel ID: {cls.BOT_CHANNEL}")
        print(f"Public Bot: {cls.PUBLIC_BOT}")
        print(f"Web Server: {cls.HOST}:{cls.PORT}")
        print(f"Base URL: {cls.BASE_URL}")
        print(f"Database: {cls.DATABASE_NAME}")
        print(f"Bot Token: {'*' * 20 if cls.BOT_TOKEN else 'NOT SET'}")
        print(f"API ID: {'SET' if cls.API_ID else 'NOT SET'}")
        print(f"API Hash: {'*' * 20 if cls.API_HASH else 'NOT SET'}")
        print(f"Secret: {'*' * 20 if cls.SIA_SECRET else 'NOT SET'}")
        print("=" * 50)
