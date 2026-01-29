from flask import Flask, render_template, request, Response, redirect, url_for, stream_with_context, jsonify
from config import Config
from bot.database import Database
from bot.utils import Cryptic, format_size, escape_markdown
from pyrogram import Client
from pyrogram.errors import RPCError
import aiohttp
import asyncio
from datetime import datetime
import re

app = Flask(__name__)

# Initialize database
db = Database()

# Initialize Pyrogram client for file retrieval
bot_client = None

async def init_bot_client():
    """Initialize bot client for file operations"""
    global bot_client
    bot_client = Client(
        "web_client",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN
    )
    await bot_client.start()
    print("✅ Web client initialized")

async def get_file_info(message_id: int):
    """Get file information from Telegram"""
    try:
        message = await bot_client.get_messages(Config.BOT_CHANNEL, message_id)
        
        if message.document:
            return {
                "file_id": message.document.file_id,
                "file_name": message.document.file_name or "Document",
                "file_size": message.document.file_size,
                "file_type": "video" if message.document.mime_type and "video" in message.document.mime_type else "document",
                "mime_type": message.document.mime_type or "application/octet-stream"
            }
        elif message.video:
            return {
                "file_id": message.video.file_id,
                "file_name": message.video.file_name or "Video File",
                "file_size": message.video.file_size,
                "file_type": "video",
                "mime_type": message.video.mime_type or "video/mp4"
            }
        elif message.audio:
            return {
                "file_id": message.audio.file_id,
                "file_name": message.audio.file_name or "Audio File",
                "file_size": message.audio.file_size,
                "file_type": "audio",
                "mime_type": message.audio.mime_type or "audio/mpeg"
            }
        elif message.photo:
            return {
                "file_id": message.photo.file_id,
                "file_name": f"{message.photo.file_unique_id}.jpg",
                "file_size": message.photo.file_size,
                "file_type": "image",
                "mime_type": "image/jpeg"
            }
        else:
            return None
    except Exception as e:
        print(f"Error getting file info: {e}")
        return None

async def stream_file(file_id: str, range_header=None):
    """Stream file from Telegram"""
    try:
        # Get file path
        file = await bot_client.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{Config.BOT_TOKEN}/{file.file_path}"
        
        # Setup headers for range request
        headers = {}
        if range_header:
            headers['Range'] = range_header
        
        # Stream from Telegram
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url, headers=headers) as response:
                async def generate():
                    async for chunk in response.content.iter_chunked(1024 * 1024):  # 1MB chunks
                        yield chunk
                
                return response, generate()
        
    except Exception as e:
        print(f"Error streaming file: {e}")
        return None, None

@app.route('/')
def home():
    """Home page"""
    return render_template('home.html', config=Config)

@app.route('/streampage')
def stream_page():
    """Premium streaming page"""
    file_hash = request.args.get('file')
    if not file_hash:
        return "Missing file parameter", 404
    
    try:
        message_id = Cryptic.dehash(file_hash)
    except Exception:
        return "Invalid file hash", 404
    
    # Run async function in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Get file data from database
        file_data = loop.run_until_complete(db.get_file(message_id))
        
        if not file_data:
            # Try to get from Telegram
            file_info = loop.run_until_complete(get_file_info(int(message_id)))
            if not file_info:
                return "File not found", 404
            
            file_name = file_info["file_name"]
            file_size = file_info["file_size"]
            file_type = file_info["file_type"]
            downloads = 0
        else:
            file_name = file_data["file_name"]
            file_size = file_data["file_size"]
            file_type = file_data["file_type"]
            downloads = file_data.get("downloads", 0)
        
        # Generate links
        stream_url = f"{Config.BASE_URL}/stream/{file_hash}"
        download_url = f"{Config.BASE_URL}/dl/{file_hash}"
        
        return render_template(
            'stream.html',
            file_name=file_name,
            file_size=format_size(file_size),
            file_type=file_type,
            file_url=stream_url,
            stream_url=stream_url,
            download_url=download_url,
            downloads=downloads,
            config=Config
        )
    finally:
        loop.close()

@app.route('/stream/<file_hash>')
@app.route('/dl/<file_hash>')
def serve_file(file_hash):
    """Serve file with streaming support"""
    # Determine mode based on path
    mode = "inline" if "/stream/" in request.path else "attachment"
    
    try:
        message_id = Cryptic.dehash(file_hash)
    except Exception:
        return jsonify({"error": "Invalid file hash"}), 404
    
    # Run async function in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Get file info
        file_info = loop.run_until_complete(get_file_info(int(message_id)))
        if not file_info:
            return jsonify({"error": "File not found"}), 404
        
        # Check file size limit
        if file_info["file_size"] > Config.MAX_STREAM_SIZE:
            return jsonify({"error": "File size exceeds streaming limit (2GB max)"}), 413
        
        # Increment download counter asynchronously
        loop.run_until_complete(db.increment_downloads(message_id))
        
        # Get range header
        range_header = request.headers.get('Range')
        
        # Stream file
        telegram_response, file_generator = loop.run_until_complete(
            stream_file(file_info["file_id"], range_header)
        )
        
        if not telegram_response:
            return jsonify({"error": "Error streaming file"}), 500
        
        # Create response
        def generate():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                gen = file_generator
                while True:
                    try:
                        chunk = loop.run_until_complete(gen.__anext__())
                        yield chunk
                    except StopAsyncIteration:
                        break
            finally:
                loop.close()
        
        # Setup response headers
        headers = {
            'Content-Type': file_info["mime_type"],
            'Content-Disposition': f'{mode}; filename="{file_info["file_name"]}"',
            'Accept-Ranges': 'bytes',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
            'Cache-Control': 'public, max-age=3600'
        }
        
        # Add content length and range headers
        if range_header and telegram_response.status == 206:
            headers['Content-Range'] = telegram_response.headers.get('Content-Range', '')
            headers['Content-Length'] = telegram_response.headers.get('Content-Length', '')
            status_code = 206
        else:
            headers['Content-Length'] = str(file_info["file_size"])
            status_code = 200
        
        return Response(
            stream_with_context(generate()),
            status=status_code,
            headers=headers
        )
        
    except Exception as e:
        print(f"Error serving file: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "bot": Config.BOT_NAME}), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

def run_web_server():
    """Run Flask web server"""
    # Initialize bot client
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(init_bot_client())
    
    print(f"🌐 Web server starting on {Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=False)

if __name__ == '__main__':
    run_web_server()
