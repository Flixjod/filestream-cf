"""
Main entry point for FileStream Bot
Runs both Pyrogram bot and FastAPI server concurrently
"""
import asyncio
import uvicorn
from bot import app as bot_app, start_bot, stop_bot
from server import app as server_app
from config import config
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_bot():
    """Run the Pyrogram bot"""
    await start_bot()
    logger.info("🤖 Bot is running...")
    await asyncio.Event().wait()


async def run_server():
    """Run the FastAPI server"""
    config_uvicorn = uvicorn.Config(
        server_app,
        host=config.HOST,
        port=config.PORT,
        log_level="info"
    )
    server = uvicorn.Server(config_uvicorn)
    await server.serve()


async def main():
    """Run both bot and server concurrently"""
    logger.info("🚀 Starting FileStream Bot...")
    logger.info(f"📡 Server URL: {config.BASE_URL}")
    
    # Run both tasks concurrently
    await asyncio.gather(
        run_bot(),
        run_server()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️  Received stop signal")
        asyncio.run(stop_bot())
        logger.info("👋 Goodbye!")
