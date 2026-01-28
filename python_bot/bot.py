"""
FileStream Bot - Main Pyrogram Bot
Handles all Telegram bot operations
"""
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from pyrogram.types import InlineQueryResultCachedDocument, InlineQueryResultCachedPhoto
from config import config
from database import db
from utils import Cryptic, escape_markdown, format_size
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Pyrogram Client
app = Client(
    "filestream_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    workers=config.WORKERS,
    sleep_threshold=config.SLEEP_THRESHOLD
)


# ========== Command Handlers ==========

@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    """Handle /start command"""
    # Check if it's a deep link with file hash
    if len(message.command) > 1:
        file_hash = message.command[1]
        try:
            message_id = Cryptic.dehash_message_id(file_hash)
            # Get the file from channel and send to user
            try:
                file_msg = await client.get_messages(config.BOT_CHANNEL, int(message_id))
                if file_msg:
                    await file_msg.copy(message.chat.id)
                else:
                    await message.reply_text("❌ File not found or deleted.")
            except Exception as e:
                logger.error(f"Error fetching file: {e}")
                await message.reply_text("❌ Error: File not found.")
        except ValueError:
            await message.reply_text("❌ Invalid file link.")
        return
    
    # Regular start command
    buttons = [[InlineKeyboardButton("👨‍💻 Source Code", url="https://t.me/FLiX_LY")]]
    start_text = (
        f"👋 **ʜᴇʟʟᴏ {message.from_user.first_name}**,\n\n"
        f"I am a **ᴘʀᴇᴍɪᴜᴍ ғɪʟᴇ sᴛʀᴇᴀᴍ ʙᴏᴛ**.\n\n"
        f"📂 **Send me any file** (Video, Audio, Document) and I will generate a direct download and streaming link for you.\n\n"
        f"**ᴄᴏᴍᴍᴀɴᴅs:**\n"
        f"/files - View all your files\n"
        f"/revoke <token> - Revoke a file\n"
        f"/stats - View statistics (Owner only)\n"
        f"/revokeall - Delete all files (Owner only)"
    )
    await message.reply_text(start_text, reply_markup=InlineKeyboardMarkup(buttons))


@app.on_message(filters.command("files") & filters.private)
async def files_command(client: Client, message: Message):
    """Handle /files command - show user's files"""
    user_id = str(message.from_user.id)
    user_files = await db.get_user_files(user_id)
    
    if not user_files:
        await message.reply_text(
            "📂 **ʏᴏᴜʀ ғɪʟᴇs**\n\n"
            "You don't have any files yet. Send me a file to get started!"
        )
        return
    
    # Create buttons for files
    buttons = []
    for file in user_files[:10]:  # Show max 10 files
        file_name = file['file_name']
        if len(file_name) > 30:
            file_name = file_name[:27] + '...'
        buttons.append([
            InlineKeyboardButton(
                f"📄 {file_name}",
                callback_data=f"view_{file['message_id']}"
            )
        ])
    
    message_text = f"📂 **ʏᴏᴜʀ ғɪʟᴇs** ({len(user_files)} total)\n\nClick on any file to view details and get links:"
    await message.reply_text(message_text, reply_markup=InlineKeyboardMarkup(buttons))


@app.on_message(filters.command("revoke") & filters.private)
async def revoke_command(client: Client, message: Message):
    """Handle /revoke command"""
    if len(message.command) < 2:
        await message.reply_text(
            "❌ **ɪɴᴠᴀʟɪᴅ ᴄᴏᴍᴍᴀɴᴅ**\n\n"
            "Usage: `/revoke <secret_token>`"
        )
        return
    
    token = message.command[1]
    file_data = await db.get_file_by_token(token)
    
    if not file_data:
        await message.reply_text(
            "❌ **ғɪʟᴇ ɴᴏᴛ ғᴏᴜɴᴅ**\n\n"
            "The file with this token doesn't exist or has already been deleted."
        )
        return
    
    # Check permissions
    if file_data['user_id'] != str(message.from_user.id) and message.from_user.id != config.BOT_OWNER:
        await message.reply_text(
            "❌ **ᴘᴇʀᴍɪssɪᴏɴ ᴅᴇɴɪᴇᴅ**\n\n"
            "You don't have permission to revoke this file."
        )
        return
    
    # Delete from channel and database
    try:
        await client.delete_messages(config.BOT_CHANNEL, int(file_data['message_id']))
    except:
        pass
    
    await db.delete_file(file_data['message_id'])
    
    await message.reply_text(
        f"🗑️ **ғɪʟᴇ ʀᴇᴠᴏᴋᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**\n\n"
        f"📂 **ғɪʟᴇ:** `{escape_markdown(file_data['file_name'])}`\n\n"
        f"All links have been deleted and the file is no longer accessible."
    )


@app.on_message(filters.command("revokeall") & filters.private)
async def revokeall_command(client: Client, message: Message):
    """Handle /revokeall command - owner only"""
    if message.from_user.id != config.BOT_OWNER:
        await message.reply_text(
            "❌ **ᴘᴇʀᴍɪssɪᴏɴ ᴅᴇɴɪᴇᴅ**\n\n"
            "This command is only available to the bot owner."
        )
        return
    
    # Get all files and delete from channel
    all_files = await db.get_user_files("0", limit=10000)  # Get all
    
    deleted_count = 0
    for file in all_files:
        try:
            await client.delete_messages(config.BOT_CHANNEL, int(file['message_id']))
            deleted_count += 1
        except:
            pass
    
    # Delete all from database
    total_deleted = await db.delete_all_files()
    
    await message.reply_text(
        f"🗑️ **ᴀʟʟ ғɪʟᴇs ᴅᴇʟᴇᴛᴇᴅ!**\n\n"
        f"Deleted {total_deleted} files from the database."
    )


@app.on_message(filters.command("stats") & filters.private)
async def stats_command(client: Client, message: Message):
    """Handle /stats command - owner only"""
    if message.from_user.id != config.BOT_OWNER:
        await message.reply_text(
            "❌ **ᴘᴇʀᴍɪssɪᴏɴ ᴅᴇɴɪᴇᴅ**\n\n"
            "This command is only available to the bot owner."
        )
        return
    
    stats = await db.get_stats()
    
    await message.reply_text(
        f"📊 **ʙᴏᴛ sᴛᴀᴛɪsᴛɪᴄs**\n\n"
        f"📂 **ᴛᴏᴛᴀʟ ғɪʟᴇs:** `{stats['total_files']}`\n"
        f"👥 **ᴛᴏᴛᴀʟ ᴜsᴇʀs:** `{stats['total_users']}`\n"
        f"📥 **ᴛᴏᴛᴀʟ ᴅᴏᴡɴʟᴏᴀᴅs:** `{stats['total_downloads']}`"
    )


# ========== File Handler ==========

@app.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def handle_file(client: Client, message: Message):
    """Handle file uploads"""
    # Access control
    if not config.PUBLIC_BOT and message.from_user.id != config.BOT_OWNER:
        buttons = [[InlineKeyboardButton("Source Code", url="https://t.me/FLiX_LY")]]
        await message.reply_text(
            "**❌ ᴀᴄᴄᴇss ғᴏʀʙɪᴅᴅᴇɴ.**\n"
            "📡 Deploy your own filestream bot.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
    
    # Extract file metadata
    if message.document:
        file_name = message.document.file_name or "Document"
        file_size = message.document.file_size
        file_type = message.document.mime_type.split('/')[0] if message.document.mime_type else "document"
    elif message.video:
        file_name = message.video.file_name or "Video File"
        file_size = message.video.file_size
        file_type = "video"
    elif message.audio:
        file_name = message.audio.file_name or "Audio File"
        file_size = message.audio.file_size
        file_type = "audio"
    elif message.photo:
        file_name = f"{message.photo.file_unique_id}.jpg"
        file_size = message.photo.file_size
        file_type = "image"
    else:
        return
    
    # Check file size
    if file_size > config.MAX_TELEGRAM_SIZE:
        await message.reply_text(
            f"❌ **ғɪʟᴇ ᴛᴏᴏ ʟᴀʀɢᴇ**\n\n"
            f"📊 **ғɪʟᴇ sɪᴢᴇ:** `{format_size(file_size)}`\n"
            f"⚠️ **ᴍᴀx ᴀʟʟᴏᴡᴇᴅ:** `4.00 GB`\n\n"
            f"Please send a smaller file."
        )
        return
    
    # Copy to channel (no caption to avoid parsing errors)
    try:
        forwarded = await message.copy(config.BOT_CHANNEL)
    except Exception as e:
        logger.error(f"Error copying to channel: {e}")
        await message.reply_text(f"❌ Error forwarding to channel: {str(e)}")
        return
    
    # Send reply message in channel with user info
    user_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    user_info_text = (
        f"RᴇQᴜᴇꜱᴛᴇᴅ ʙʏ : ٭千🅻丨乂٭\n"
        f"Uꜱᴇʀ ɪᴅ : {message.from_user.id}\n"
        f"Fɪʟᴇ ɴᴀᴍᴇ : {file_name}"
    )
    try:
        await client.send_message(
            config.BOT_CHANNEL,
            user_info_text,
            reply_to_message_id=forwarded.id
        )
    except Exception as e:
        logger.error(f"Error sending user info: {e}")
    
    # Generate hash and links
    file_hash = Cryptic.hash_message_id(str(forwarded.id))
    stream_page = f"{config.BASE_URL}/streampage?file={file_hash}"
    stream_link = f"{config.BASE_URL}/stream/{file_hash}"
    download_link = f"{config.BASE_URL}/dl/{file_hash}"
    telegram_link = f"https://t.me/{(await client.get_me()).username}?start={file_hash}"
    
    # Generate secret token
    secret_token = Cryptic.generate_secret_token()
    
    # Save to database
    await db.register_user({
        "user_id": message.from_user.id,
        "username": message.from_user.username or "",
        "first_name": message.from_user.first_name or "",
        "last_name": message.from_user.last_name or ""
    })
    
    await db.add_file({
        "file_id": file_hash,
        "message_id": forwarded.id,
        "user_id": message.from_user.id,
        "username": message.from_user.username or "",
        "file_name": file_name,
        "file_size": file_size,
        "file_type": file_type,
        "secret_token": secret_token
    })
    
    # Determine if streamable
    is_streamable = file_type in ['video', 'audio']
    
    # Create buttons
    buttons = []
    if is_streamable:
        buttons.append([
            InlineKeyboardButton("🌐 sᴛʀᴇᴀᴍ ᴘᴀɢᴇ", url=stream_page),
            InlineKeyboardButton("📥 ᴅᴏᴡɴʟᴏᴀᴅ", url=download_link)
        ])
    else:
        buttons.append([
            InlineKeyboardButton("📥 ᴅᴏᴡɴʟᴏᴀᴅ", url=download_link),
            InlineKeyboardButton("💬 ᴛᴇʟᴇɢʀᴀᴍ", url=telegram_link)
        ])
    
    buttons.extend([
        [
            InlineKeyboardButton("💬 ᴛᴇʟᴇɢʀᴀᴍ", url=telegram_link),
            InlineKeyboardButton("🔁 sʜᴀʀᴇ", switch_inline_query=file_hash)
        ],
        [InlineKeyboardButton("🗑️ ʀᴇᴠᴏᴋᴇ", callback_data=f"revoke_{secret_token}")],
        [InlineKeyboardButton(f"👑 ᴏᴡɴᴇʀ", url=f"https://t.me/{config.OWNER_USERNAME}")]
    ])
    
    # Send response
    safe_name = escape_markdown(file_name)
    formatted_size = format_size(file_size)
    
    final_text = (
        f"✅ **ғɪʟᴇ sᴜᴄᴄᴇssғᴜʟʟʏ ᴘʀᴏᴄᴇssᴇᴅ!**\n\n"
        f"📂 **ғɪʟᴇ ɴᴀᴍᴇ:** `{safe_name}`\n"
        f"💾 **ғɪʟᴇ sɪᴢᴇ:** `{formatted_size}`\n"
        f"📊 **ғɪʟᴇ ᴛʏᴘᴇ:** `{file_type}`\n"
        f"🔐 **sᴇᴄʀᴇᴛ ᴛᴏᴋᴇɴ:** `{secret_token}`\n"
    )
    
    if is_streamable:
        final_text += f"🎬 **sᴛʀᴇᴀᴍɪɴɢ:** `Available`\n\n"
        final_text += f"🔗 **sᴛʀᴇᴀᴍ ʟɪɴᴋ:**\n`{stream_link}`"
        if file_size > config.MAX_STREAM_SIZE:
            final_text += f"\n\n⚠️ **ɴᴏᴛᴇ:** Streaming works best for files under 2GB."
    else:
        final_text += f"\n🔗 **ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ:**\n`{download_link}`"
    
    await message.reply_text(final_text, reply_markup=InlineKeyboardMarkup(buttons))


# ========== Callback Query Handler ==========

@app.on_callback_query()
async def handle_callback(client: Client, callback: CallbackQuery):
    """Handle callback queries"""
    data = callback.data
    user_id = callback.from_user.id
    
    # Handle revoke button
    if data.startswith("revoke_"):
        token = data.replace("revoke_", "")
        file_data = await db.get_file_by_token(token)
        
        if not file_data:
            await callback.answer("❌ File not found or already deleted", show_alert=True)
            return
        
        # Check permissions
        if file_data['user_id'] != str(user_id) and user_id != config.BOT_OWNER:
            await callback.answer("❌ You don't have permission to revoke this file", show_alert=True)
            return
        
        # Delete from channel and database
        try:
            await client.delete_messages(config.BOT_CHANNEL, int(file_data['message_id']))
        except:
            pass
        
        await db.delete_file(file_data['message_id'])
        
        await callback.message.edit_text(
            "🗑️ **ғɪʟᴇ ʀᴇᴠᴏᴋᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**\n\n"
            "All links have been deleted and the file is no longer accessible."
        )
        await callback.answer("✅ File revoked successfully!", show_alert=False)
        return
    
    # Handle view file details
    if data.startswith("view_"):
        message_id = data.replace("view_", "")
        file_data = await db.get_file(message_id)
        
        if not file_data:
            await callback.answer("❌ File not found", show_alert=True)
            return
        
        # Generate links
        file_hash = Cryptic.hash_message_id(message_id)
        stream_page = f"{config.BASE_URL}/streampage?file={file_hash}"
        stream_link = f"{config.BASE_URL}/stream/{file_hash}"
        download_link = f"{config.BASE_URL}/dl/{file_hash}"
        telegram_link = f"https://t.me/{(await client.get_me()).username}?start={file_hash}"
        
        safe_name = escape_markdown(file_data['file_name'])
        formatted_size = format_size(file_data['file_size'])
        
        buttons = [
            [
                InlineKeyboardButton("🌐 sᴛʀᴇᴀᴍ ᴘᴀɢᴇ", url=stream_page),
                InlineKeyboardButton("📥 ᴅᴏᴡɴʟᴏᴀᴅ", url=download_link)
            ],
            [
                InlineKeyboardButton("💬 ᴛᴇʟᴇɢʀᴀᴍ", url=telegram_link),
                InlineKeyboardButton("🔁 sʜᴀʀᴇ", switch_inline_query=file_hash)
            ],
            [InlineKeyboardButton("🗑️ ʀᴇᴠᴏᴋᴇ ᴀᴄᴄᴇss", callback_data=f"revoke_{file_data['secret_token']}")],
            [InlineKeyboardButton("⬅️ ʙᴀᴄᴋ ᴛᴏ ʟɪsᴛ", callback_data="back_to_files")]
        ]
        
        message_text = (
            f"✅ **ғɪʟᴇ ᴅᴇᴛᴀɪʟs**\n\n"
            f"📂 **ғɪʟᴇ ɴᴀᴍᴇ:** `{safe_name}`\n"
            f"💾 **ғɪʟᴇ sɪᴢᴇ:** `{formatted_size}`\n"
            f"📊 **ғɪʟᴇ ᴛʏᴘᴇ:** `{file_data['file_type']}`\n"
            f"📥 **ᴅᴏᴡɴʟᴏᴀᴅs:** `{file_data.get('downloads', 0)}`\n"
            f"📅 **ᴜᴘʟᴏᴀᴅᴇᴅ:** `{file_data['created_at'].strftime('%Y-%m-%d')}`\n\n"
            f"🔗 **sᴛʀᴇᴀᴍ ʟɪɴᴋ:**\n`{stream_link}`"
        )
        
        await callback.message.edit_text(message_text, reply_markup=InlineKeyboardMarkup(buttons))
        await callback.answer("📂 File details loaded", show_alert=False)
        return
    
    # Handle back to files list
    if data == "back_to_files":
        user_files = await db.get_user_files(str(user_id))
        
        if not user_files:
            await callback.message.edit_text(
                "📂 **ʏᴏᴜʀ ғɪʟᴇs**\n\n"
                "You don't have any files yet. Send me a file to get started!"
            )
            await callback.answer("No files found", show_alert=False)
            return
        
        buttons = []
        for file in user_files[:10]:
            file_name = file['file_name']
            if len(file_name) > 30:
                file_name = file_name[:27] + '...'
            buttons.append([
                InlineKeyboardButton(f"📄 {file_name}", callback_data=f"view_{file['message_id']}")
            ])
        
        message_text = f"📂 **ʏᴏᴜʀ ғɪʟᴇs** ({len(user_files)} total)\n\nClick on any file to view details and get links:"
        await callback.message.edit_text(message_text, reply_markup=InlineKeyboardMarkup(buttons))
        await callback.answer("📂 Files list loaded", show_alert=False)


# ========== Inline Query Handler ==========

@app.on_inline_query()
async def handle_inline(client: Client, inline_query: InlineQuery):
    """Handle inline queries"""
    if not config.PUBLIC_BOT and inline_query.from_user.id != config.BOT_OWNER:
        results = [
            InlineQueryResultArticle(
                title="Access forbidden",
                description="Deploy your own filestream bot.",
                input_message_content=InputTextMessageContent(
                    "**❌ ᴀᴄᴄᴇss ғᴏʀʙɪᴅᴅᴇɴ.**\n📡 Deploy your own filestream bot."
                )
            )
        ]
        await inline_query.answer(results, cache_time=1)
        return
    
    query = inline_query.query
    
    try:
        message_id = Cryptic.dehash_message_id(query)
    except:
        results = [
            InlineQueryResultArticle(
                title="Error",
                description="Invalid file hash",
                input_message_content=InputTextMessageContent("❌ Invalid file hash")
            )
        ]
        await inline_query.answer(results, cache_time=1)
        return
    
    # Get file from channel
    try:
        file_msg = await client.get_messages(config.BOT_CHANNEL, int(message_id))
        
        if not file_msg:
            raise Exception("File not found")
        
        # Create inline result based on media type
        buttons = [[InlineKeyboardButton("Send Again", switch_inline_query_current_chat=query)]]
        
        if file_msg.photo:
            results = [
                InlineQueryResultCachedPhoto(
                    photo_file_id=file_msg.photo.file_id,
                    title="Photo",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            ]
        elif file_msg.document:
            results = [
                InlineQueryResultCachedDocument(
                    document_file_id=file_msg.document.file_id,
                    title=file_msg.document.file_name or "Document",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            ]
        elif file_msg.video:
            results = [
                InlineQueryResultCachedDocument(
                    document_file_id=file_msg.video.file_id,
                    title=file_msg.video.file_name or "Video",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            ]
        elif file_msg.audio:
            results = [
                InlineQueryResultCachedDocument(
                    document_file_id=file_msg.audio.file_id,
                    title=file_msg.audio.file_name or "Audio",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            ]
        else:
            raise Exception("Unsupported file type")
        
        await inline_query.answer(results, cache_time=1)
    
    except Exception as e:
        logger.error(f"Inline query error: {e}")
        results = [
            InlineQueryResultArticle(
                title="Error",
                description="File not found or deleted",
                input_message_content=InputTextMessageContent("❌ File not found or deleted")
            )
        ]
        await inline_query.answer(results, cache_time=1)


async def start_bot():
    """Start the bot"""
    await db.connect()
    await app.start()
    logger.info("✅ Bot started successfully!")
    me = await app.get_me()
    logger.info(f"🤖 Bot: @{me.username}")


async def stop_bot():
    """Stop the bot"""
    await app.stop()
    await db.close()
    logger.info("🛑 Bot stopped")


if __name__ == "__main__":
    import asyncio
    
    async def main():
        await start_bot()
        await asyncio.Event().wait()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received stop signal")
