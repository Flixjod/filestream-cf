"""
FileStream Server - FastAPI streaming server
Handles HTTP requests for file streaming and downloads
"""
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
from pathlib import Path
from config import config
from database import db
from utils import Cryptic, format_size, escape_markdown
from pyrogram import Client
import logging
import os

logger = logging.getLogger(__name__)

app = FastAPI(title="FileStream Server")

# Templates
templates = Jinja2Templates(directory="templates")

# Telegram client for file access
telegram_client = None


async def get_telegram_client():
    """Get or create Telegram client"""
    global telegram_client
    if telegram_client is None:
        telegram_client = Client(
            "streaming_client",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN
        )
        await telegram_client.start()
    return telegram_client


async def get_file_info(message_id: int):
    """Get file information using getMessage"""
    try:
        client = await get_telegram_client()
        message = await client.get_messages(config.BOT_CHANNEL, message_id)
        
        if not message:
            return None
        
        file_info = {"size": 0, "type": ""}
        
        if message.document:
            file_info["size"] = message.document.file_size
            file_info["type"] = message.document.mime_type or "application/octet-stream"
        elif message.video:
            file_info["size"] = message.video.file_size
            file_info["type"] = message.video.mime_type or "video/mp4"
        elif message.audio:
            file_info["size"] = message.audio.file_size
            file_info["type"] = message.audio.mime_type or "audio/mpeg"
        elif message.photo:
            file_info["size"] = message.photo.file_size
            file_info["type"] = "image/jpeg"
        else:
            return None
        
        return file_info
    except Exception as e:
        logger.error(f"Error getting file info: {e}")
        return None


async def get_file_url(message_id: int):
    """Get Telegram file URL for streaming"""
    try:
        client = await get_telegram_client()
        message = await client.get_messages(config.BOT_CHANNEL, message_id)
        
        if not message:
            return None, None, None, None
        
        file_id = None
        file_name = None
        file_size = None
        mime_type = None
        
        if message.document:
            file_id = message.document.file_id
            file_name = message.document.file_name or "Document"
            file_size = message.document.file_size
            mime_type = message.document.mime_type or "application/octet-stream"
        elif message.video:
            file_id = message.video.file_id
            file_name = message.video.file_name or "Video"
            file_size = message.video.file_size
            mime_type = message.video.mime_type or "video/mp4"
        elif message.audio:
            file_id = message.audio.file_id
            file_name = message.audio.file_name or "Audio"
            file_size = message.audio.file_size
            mime_type = message.audio.mime_type or "audio/mpeg"
        elif message.photo:
            file_id = message.photo.file_id
            file_name = f"{message.photo.file_unique_id}.jpg"
            file_size = message.photo.file_size
            mime_type = "image/jpeg"
        
        if not file_id:
            return None, None, None, None
        
        # Get file path from Telegram
        file = await client.download_media(file_id, in_memory=True)
        
        # Get bot info for file URL
        me = await client.get_me()
        
        # For streaming, we need the file path from Telegram API
        # Using pyrogram's get_file method
        file_data = await client.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{config.BOT_TOKEN}/{file_data.file_path}"
        
        return file_url, file_name, file_size, mime_type
    
    except Exception as e:
        logger.error(f"Error getting file URL: {e}")
        return None, None, None, None


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    await db.connect()
    await get_telegram_client()
    logger.info("✅ Streaming server started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await db.close()
    if telegram_client:
        await telegram_client.stop()
    logger.info("🛑 Streaming server stopped")


@app.get("/")
async def home(request: Request):
    """Home page"""
    client = await get_telegram_client()
    me = await client.get_me()
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "bot_name": config.BOT_NAME,
        "bot_username": me.username,
        "owner_username": config.OWNER_USERNAME
    })


@app.get("/stream/{file_hash}")
@app.get("/dl/{file_hash}")
async def stream_file(file_hash: str, request: Request):
    """Stream or download file"""
    try:
        # Decode hash to get message_id
        message_id = int(Cryptic.dehash_message_id(file_hash))
    except:
        raise HTTPException(status_code=404, detail="Invalid file hash")
    
    # Check if file exists in database
    file_data = await db.get_file(str(message_id))
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found or deleted")
    
    # Increment downloads
    await db.increment_downloads(str(message_id))
    
    # Get file URL and info
    file_url, file_name, file_size, mime_type = await get_file_url(message_id)
    
    if not file_url:
        raise HTTPException(status_code=404, detail="File not accessible")
    
    # Check size limits for streaming
    if file_size > config.MAX_STREAM_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds streaming limit (2GB max)")
    
    # Determine content disposition
    is_download = request.url.path.startswith("/dl/")
    disposition = "attachment" if is_download else "inline"
    
    # Stream from Telegram
    async def stream_from_telegram():
        async with httpx.AsyncClient() as client:
            # Handle range requests
            headers = {}
            range_header = request.headers.get("range")
            if range_header:
                headers["Range"] = range_header
            
            async with client.stream("GET", file_url, headers=headers) as response:
                async for chunk in response.aiter_bytes(chunk_size=1024 * 1024):  # 1MB chunks
                    yield chunk
    
    # Get range info for proper status code
    status_code = 200
    response_headers = {
        "Content-Type": mime_type,
        "Content-Disposition": f'{disposition}; filename="{file_name}"',
        "Accept-Ranges": "bytes",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "public, max-age=3600"
    }
    
    # Handle range requests
    if request.headers.get("range"):
        status_code = 206
        # Add Content-Range header (simplified, Telegram API handles it)
        response_headers["Content-Range"] = f"bytes */{file_size}"
    else:
        response_headers["Content-Length"] = str(file_size)
    
    return StreamingResponse(
        stream_from_telegram(),
        status_code=status_code,
        headers=response_headers,
        media_type=mime_type
    )


@app.get("/streampage")
async def stream_page(request: Request, file: str):
    """Streaming page with player"""
    try:
        message_id = int(Cryptic.dehash_message_id(file))
    except:
        raise HTTPException(status_code=404, detail="Invalid file hash")
    
    # Get file data
    file_data = await db.get_file(str(message_id))
    
    if file_data:
        file_name = file_data['file_name']
        file_size = file_data['file_size']
        file_type = file_data['file_type']
        downloads = file_data.get('downloads', 0)
    else:
        # Fallback to Telegram API
        file_info = await get_file_info(message_id)
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_name = "Media File"
        file_size = file_info['size']
        file_type = "video" if "video" in file_info['type'] else "audio" if "audio" in file_info['type'] else "document"
        downloads = 0
    
    # Get bot info
    client = await get_telegram_client()
    me = await client.get_me()
    
    # Generate URLs
    stream_url = f"{config.BASE_URL}/stream/{file}"
    download_url = f"{config.BASE_URL}/dl/{file}"
    telegram_url = f"https://t.me/{me.username}?start={file}"
    
    # Truncate filename for title
    truncated_filename = file_name[:50] + '...' if len(file_name) > 50 else file_name
    page_title = f"Watch {truncated_filename} | {config.BOT_NAME}"
    
    return templates.TemplateResponse("stream.html", {
        "request": request,
        "page_title": page_title,
        "bot_name": config.BOT_NAME,
        "owner_username": config.OWNER_USERNAME,
        "file_name": file_name,
        "file_size": file_size,
        "file_type": file_type,
        "downloads": downloads,
        "stream_url": stream_url,
        "download_url": download_url,
        "telegram_url": telegram_url,
        "format_size": format_size
    })


@app.head("/stream/{file_hash}")
@app.head("/dl/{file_hash}")
async def head_file(file_hash: str):
    """Handle HEAD requests for file info"""
    try:
        message_id = int(Cryptic.dehash_message_id(file_hash))
    except:
        raise HTTPException(status_code=404, detail="Invalid file hash")
    
    file_info = await get_file_info(message_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    return Response(
        headers={
            "Content-Type": file_info['type'],
            "Content-Length": str(file_info['size']),
            "Accept-Ranges": "bytes"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
