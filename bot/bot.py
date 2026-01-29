from pyrogram import Client, filters
from pyrogram.types import (
    Message, InlineQuery, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    InlineQueryResultArticle, InputTextMessageContent,
    InlineQueryResultCachedDocument, InlineQueryResultCachedPhoto
)
from config import Config
from bot.database import Database
from bot.utils import Cryptic, format_size, escape_markdown, generate_secret_token
import asyncio

class FileStreamBot:
    """Main bot class handling all Telegram interactions"""
    
    def __init__(self):
        self.app = Client(
            Config.SESSION_NAME,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN
        )
        self.db = Database()
        
        # Register handlers
        self.register_handlers()
    
    def register_handlers(self):
        """Register all command and message handlers"""
        
        @self.app.on_message(filters.command("start"))
        async def start_command(client, message: Message):
            await self.handle_start(message)
        
        @self.app.on_message(filters.command("files"))
        async def files_command(client, message: Message):
            await self.handle_files(message)
        
        @self.app.on_message(filters.command("revoke"))
        async def revoke_command(client, message: Message):
            await self.handle_revoke(message)
        
        @self.app.on_message(filters.command("revokeall") & filters.user(Config.BOT_OWNER))
        async def revokeall_command(client, message: Message):
            await self.handle_revokeall(message)
        
        @self.app.on_message(filters.command("stats") & filters.user(Config.BOT_OWNER))
        async def stats_command(client, message: Message):
            await self.handle_stats(message)
        
        @self.app.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
        async def handle_media(client, message: Message):
            await self.handle_file(message)
        
        @self.app.on_inline_query()
        async def inline_query(client, query: InlineQuery):
            await self.handle_inline(query)
        
        @self.app.on_callback_query()
        async def callback_query(client, query: CallbackQuery):
            await self.handle_callback(query)
    
    async def handle_start(self, message: Message):
        """Handle /start command"""
        # Check for deep linking
        if len(message.command) > 1:
            file_hash = message.command[1]
            try:
                message_id = Cryptic.dehash(file_hash)
                await self.send_file_from_channel(message, int(message_id))
                return
            except Exception as e:
                await message.reply_text("❌ Invalid link or file not found.")
                return
        
        # Regular start message
        buttons = [[InlineKeyboardButton("👨‍💻 Source Code", url=f"https://t.me/{Config.OWNER_USERNAME}")]]
        
        start_text = (
            f"👋 **ʜᴇʟʟᴏ {message.from_user.first_name}**,\n\n"
            f"I am a **ᴘʀᴇᴍɪᴜᴍ ғɪʟᴇ sᴛʀᴇᴀᴍ ʙᴏᴛ**.\n\n"
            f"📂 **Send me any file** (Video, Audio, Document) and I will generate "
            f"a direct download and streaming link for you.\n\n"
            f"**ᴄᴏᴍᴍᴀɴᴅs:**\n"
            f"/files - View all your files\n"
            f"/revoke <token> - Revoke a file\n"
            f"/stats - View statistics (Owner only)\n"
            f"/revokeall - Delete all files (Owner only)"
        )
        
        await message.reply_text(start_text, reply_markup=InlineKeyboardMarkup(buttons))
    
    async def handle_file(self, message: Message):
        """Handle file uploads"""
        # Access control
        if not Config.PUBLIC_BOT and message.from_user.id != Config.BOT_OWNER:
            buttons = [[InlineKeyboardButton("Source Code", url=f"https://t.me/{Config.OWNER_USERNAME}")]]
            await message.reply_text(
                "**❌ ᴀᴄᴄᴇss ғᴏʀʙɪᴅᴅᴇɴ.**\n"
                "📡 Deploy your own filestream bot.",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return
        
        # Extract file information
        file_info = self.get_file_info(message)
        if not file_info:
            await message.reply_text("❌ Unsupported file type.")
            return
        
        file_id, file_name, file_size, file_type = file_info
        
        # Send file to channel
        try:
            sent_message = await self.app.copy_message(
                chat_id=Config.BOT_CHANNEL,
                from_chat_id=message.chat.id,
                message_id=message.id
            )
            
            message_id = str(sent_message.id)
            
            # Generate secret token
            secret_token = generate_secret_token()
            
            # Save to database
            file_data = {
                "file_id": file_id,
                "message_id": message_id,
                "user_id": message.from_user.id,
                "username": message.from_user.username or "",
                "file_name": file_name,
                "file_size": file_size,
                "file_type": file_type,
                "secret_token": secret_token
            }
            
            await self.db.add_file(file_data)
            
            # Register user
            user_data = {
                "user_id": message.from_user.id,
                "username": message.from_user.username or "",
                "first_name": message.from_user.first_name or "",
                "last_name": message.from_user.last_name or ""
            }
            await self.db.register_user(user_data)
            
            # Generate links
            final_hash = Cryptic.hash(message_id)
            stream_page = f"{Config.BASE_URL}/streampage?file={final_hash}"
            stream_link = f"{Config.BASE_URL}/stream/{final_hash}"
            download_link = f"{Config.BASE_URL}/dl/{final_hash}"
            telegram_link = f"https://t.me/{(await self.app.get_me()).username}?start={final_hash}"
            
            # Create buttons
            buttons = [
                [
                    InlineKeyboardButton("🌐 sᴛʀᴇᴀᴍ ᴘᴀɢᴇ", url=stream_page),
                    InlineKeyboardButton("📥 ᴅᴏᴡɴʟᴏᴀᴅ", url=download_link)
                ],
                [
                    InlineKeyboardButton("💬 ᴛᴇʟᴇɢʀᴀᴍ", url=telegram_link),
                    InlineKeyboardButton("🔁 sʜᴀʀᴇ", switch_inline_query=final_hash)
                ],
                [
                    InlineKeyboardButton("🗑️ ʀᴇᴠᴏᴋᴇ ᴀᴄᴄᴇss", callback_data=f"revoke_{secret_token}")
                ]
            ]
            
            safe_name = escape_markdown(file_name)
            formatted_size = format_size(file_size)
            
            response_text = (
                f"✅ **ғɪʟᴇ ᴜᴘʟᴏᴀᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**\n\n"
                f"📂 **ғɪʟᴇ ɴᴀᴍᴇ:** `{safe_name}`\n"
                f"💾 **ғɪʟᴇ sɪᴢᴇ:** `{formatted_size}`\n"
                f"📊 **ғɪʟᴇ ᴛʏᴘᴇ:** `{file_type}`\n\n"
                f"🔗 **sᴛʀᴇᴀᴍ ʟɪɴᴋ:**\n`{stream_link}`\n\n"
                f"📥 **ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ:**\n`{download_link}`"
            )
            
            await message.reply_text(response_text, reply_markup=InlineKeyboardMarkup(buttons))
            
        except Exception as e:
            print(f"Error handling file: {e}")
            await message.reply_text(f"❌ Error uploading file: {str(e)}")
    
    def get_file_info(self, message: Message):
        """Extract file information from message"""
        if message.document:
            return (
                message.document.file_id,
                message.document.file_name or "Document",
                message.document.file_size,
                message.document.mime_type or "document"
            )
        elif message.video:
            return (
                message.video.file_id,
                message.video.file_name or "Video File",
                message.video.file_size,
                "video"
            )
        elif message.audio:
            return (
                message.audio.file_id,
                message.audio.file_name or "Audio File",
                message.audio.file_size,
                "audio"
            )
        elif message.photo:
            return (
                message.photo.file_id,
                f"{message.photo.file_unique_id}.jpg",
                message.photo.file_size,
                "image"
            )
        return None
    
    async def send_file_from_channel(self, message: Message, message_id: int):
        """Send file from channel to user"""
        try:
            await self.app.copy_message(
                chat_id=message.chat.id,
                from_chat_id=Config.BOT_CHANNEL,
                message_id=message_id
            )
        except Exception as e:
            await message.reply_text("❌ File not found or has been deleted.")
    
    async def handle_files(self, message: Message):
        """Handle /files command"""
        user_id = str(message.from_user.id)
        user_files = await self.db.get_user_files(user_id)
        
        if not user_files:
            await message.reply_text(
                "📂 **ʏᴏᴜʀ ғɪʟᴇs**\n\n"
                "You don't have any files yet. Send me a file to get started!"
            )
            return
        
        buttons = []
        for file in user_files[:10]:
            file_name = file["file_name"]
            if len(file_name) > 30:
                file_name = file_name[:27] + '...'
            buttons.append([InlineKeyboardButton(f"📄 {file_name}", callback_data=f"view_{file['message_id']}")])
        
        message_text = f"📂 **ʏᴏᴜʀ ғɪʟᴇs** ({len(user_files)} total)\n\nClick on any file to view details and get links:"
        
        await message.reply_text(message_text, reply_markup=InlineKeyboardMarkup(buttons))
    
    async def handle_revoke(self, message: Message):
        """Handle /revoke command"""
        if len(message.command) < 2:
            await message.reply_text(
                "❌ **ɪɴᴠᴀʟɪᴅ ᴄᴏᴍᴍᴀɴᴅ**\n\n"
                "Usage: `/revoke <secret_token>`"
            )
            return
        
        token = message.command[1]
        file_data = await self.db.get_file_by_token(token)
        
        if not file_data:
            await message.reply_text(
                "❌ **ғɪʟᴇ ɴᴏᴛ ғᴏᴜɴᴅ**\n\n"
                "The file with this token doesn't exist or has already been deleted."
            )
            return
        
        # Check permission
        if int(file_data["user_id"]) != message.from_user.id and message.from_user.id != Config.BOT_OWNER:
            await message.reply_text(
                "❌ **ᴘᴇʀᴍɪssɪᴏɴ ᴅᴇɴɪᴇᴅ**\n\n"
                "You don't have permission to revoke this file."
            )
            return
        
        # Delete from channel and database
        try:
            await self.app.delete_messages(Config.BOT_CHANNEL, int(file_data["message_id"]))
            await self.db.delete_file(file_data["message_id"])
            
            await message.reply_text(
                f"🗑️ **ғɪʟᴇ ʀᴇᴠᴏᴋᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**\n\n"
                f"📂 **ғɪʟᴇ:** `{escape_markdown(file_data['file_name'])}`\n\n"
                f"All links have been deleted and the file is no longer accessible."
            )
        except Exception as e:
            await message.reply_text(f"❌ Error revoking file: {str(e)}")
    
    async def handle_revokeall(self, message: Message):
        """Handle /revokeall command (owner only)"""
        # Get all files
        all_files = await self.db.get_user_files("", limit=10000)
        
        if not all_files:
            await message.reply_text("📂 No files to delete.")
            return
        
        # Delete all files from channel
        deleted_count = 0
        for file in all_files:
            try:
                await self.app.delete_messages(Config.BOT_CHANNEL, int(file["message_id"]))
                deleted_count += 1
            except Exception as e:
                print(f"Failed to delete message {file['message_id']}: {e}")
        
        # Delete all from database
        await self.db.delete_all_files()
        
        await message.reply_text(
            f"🗑️ **ᴀʟʟ ғɪʟᴇs ᴅᴇʟᴇᴛᴇᴅ!**\n\n"
            f"Deleted {deleted_count} files from the database and channel."
        )
    
    async def handle_stats(self, message: Message):
        """Handle /stats command (owner only)"""
        stats = await self.db.get_stats()
        
        await message.reply_text(
            f"📊 **ʙᴏᴛ sᴛᴀᴛɪsᴛɪᴄs**\n\n"
            f"📂 **ᴛᴏᴛᴀʟ ғɪʟᴇs:** `{stats['total_files']}`\n"
            f"👥 **ᴛᴏᴛᴀʟ ᴜsᴇʀs:** `{stats['total_users']}`\n"
            f"📥 **ᴛᴏᴛᴀʟ ᴅᴏᴡɴʟᴏᴀᴅs:** `{stats['total_downloads']}`"
        )
    
    async def handle_inline(self, query: InlineQuery):
        """Handle inline queries"""
        # Access control
        if not Config.PUBLIC_BOT and query.from_user.id != Config.BOT_OWNER:
            results = [
                InlineQueryResultArticle(
                    title="Access forbidden",
                    input_message_content=InputTextMessageContent(
                        "**❌ ᴀᴄᴄᴇss ғᴏʀʙɪᴅᴅᴇɴ.**\n"
                        "📡 Deploy your own filestream bot."
                    ),
                    description="Deploy your own filestream-cf.",
                    thumb_url="https://i.ibb.co/5s8hhND/dac5fa134448.png"
                )
            ]
            await query.answer(results, cache_time=1)
            return
        
        # Validate query
        try:
            message_id = Cryptic.dehash(query.query)
        except Exception:
            results = [
                InlineQueryResultArticle(
                    title="Error",
                    input_message_content=InputTextMessageContent("❌ Invalid link format"),
                    description="Invalid hash format",
                    thumb_url="https://i.ibb.co/5s8hhND/dac5fa134448.png"
                )
            ]
            await query.answer(results, cache_time=1)
            return
        
        # Get file from channel
        try:
            msg = await self.app.get_messages(Config.BOT_CHANNEL, int(message_id))
            
            if msg.document:
                results = [
                    InlineQueryResultCachedDocument(
                        title=msg.document.file_name or "Document",
                        document_file_id=msg.document.file_id,
                        description=msg.document.mime_type or "Document",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("Send Again", switch_inline_query_current_chat=query.query)
                        ]])
                    )
                ]
            elif msg.photo:
                results = [
                    InlineQueryResultCachedPhoto(
                        title="Photo",
                        photo_file_id=msg.photo.file_id,
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("Send Again", switch_inline_query_current_chat=query.query)
                        ]])
                    )
                ]
            else:
                results = [
                    InlineQueryResultArticle(
                        title="Error",
                        input_message_content=InputTextMessageContent("❌ File not found"),
                        description="File not found"
                    )
                ]
            
            await query.answer(results, cache_time=1)
            
        except Exception as e:
            print(f"Inline query error: {e}")
            results = [
                InlineQueryResultArticle(
                    title="Error",
                    input_message_content=InputTextMessageContent(f"❌ Error: {str(e)}"),
                    description="Error retrieving file"
                )
            ]
            await query.answer(results, cache_time=1)
    
    async def handle_callback(self, query: CallbackQuery):
        """Handle callback queries"""
        data = query.data
        
        # Handle revoke button
        if data.startswith("revoke_"):
            token = data.replace("revoke_", "")
            file_data = await self.db.get_file_by_token(token)
            
            if not file_data:
                await query.answer("❌ File not found or already deleted", show_alert=True)
                return
            
            # Check permission
            if int(file_data["user_id"]) != query.from_user.id and query.from_user.id != Config.BOT_OWNER:
                await query.answer("❌ You don't have permission to revoke this file", show_alert=True)
                return
            
            # Delete from channel and database
            try:
                await self.app.delete_messages(Config.BOT_CHANNEL, int(file_data["message_id"]))
                await self.db.delete_file(file_data["message_id"])
                
                await query.message.edit_text(
                    "🗑️ **ғɪʟᴇ ʀᴇᴠᴏᴋᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**\n\n"
                    "All links have been deleted and the file is no longer accessible."
                )
                await query.answer("✅ File revoked successfully!", show_alert=False)
            except Exception as e:
                await query.answer(f"❌ Error: {str(e)}", show_alert=True)
        
        # Handle view file details
        elif data.startswith("view_"):
            message_id = data.replace("view_", "")
            file_data = await self.db.get_file(message_id)
            
            if not file_data:
                await query.answer("❌ File not found", show_alert=True)
                return
            
            # Generate links
            final_hash = Cryptic.hash(message_id)
            stream_page = f"{Config.BASE_URL}/streampage?file={final_hash}"
            stream_link = f"{Config.BASE_URL}/stream/{final_hash}"
            download_link = f"{Config.BASE_URL}/dl/{final_hash}"
            telegram_link = f"https://t.me/{(await self.app.get_me()).username}?start={final_hash}"
            
            # Create buttons
            buttons = [
                [
                    InlineKeyboardButton("🌐 sᴛʀᴇᴀᴍ ᴘᴀɢᴇ", url=stream_page),
                    InlineKeyboardButton("📥 ᴅᴏᴡɴʟᴏᴀᴅ", url=download_link)
                ],
                [
                    InlineKeyboardButton("💬 ᴛᴇʟᴇɢʀᴀᴍ", url=telegram_link),
                    InlineKeyboardButton("🔁 sʜᴀʀᴇ", switch_inline_query=final_hash)
                ],
                [
                    InlineKeyboardButton("🗑️ ʀᴇᴠᴏᴋᴇ ᴀᴄᴄᴇss", callback_data=f"revoke_{file_data['secret_token']}")
                ],
                [
                    InlineKeyboardButton("⬅️ ʙᴀᴄᴋ ᴛᴏ ʟɪsᴛ", callback_data="back_to_files")
                ]
            ]
            
            safe_name = escape_markdown(file_data["file_name"])
            formatted_size = format_size(file_data["file_size"])
            created_date = file_data.get("created_at", datetime.utcnow()).strftime("%Y-%m-%d")
            
            message_text = (
                f"✅ **ғɪʟᴇ ᴅᴇᴛᴀɪʟs**\n\n"
                f"📂 **ғɪʟᴇ ɴᴀᴍᴇ:** `{safe_name}`\n"
                f"💾 **ғɪʟᴇ sɪᴢᴇ:** `{formatted_size}`\n"
                f"📊 **ғɪʟᴇ ᴛʏᴘᴇ:** `{file_data['file_type']}`\n"
                f"📥 **ᴅᴏᴡɴʟᴏᴀᴅs:** `{file_data.get('downloads', 0)}`\n"
                f"📅 **ᴜᴘʟᴏᴀᴅᴇᴅ:** `{created_date}`\n\n"
                f"🔗 **sᴛʀᴇᴀᴍ ʟɪɴᴋ:**\n`{stream_link}`"
            )
            
            await query.message.edit_text(message_text, reply_markup=InlineKeyboardMarkup(buttons))
            await query.answer("📂 File details loaded", show_alert=False)
        
        # Handle back to files list
        elif data == "back_to_files":
            user_id = str(query.from_user.id)
            user_files = await self.db.get_user_files(user_id)
            
            if not user_files:
                await query.message.edit_text(
                    "📂 **ʏᴏᴜʀ ғɪʟᴇs**\n\n"
                    "You don't have any files yet. Send me a file to get started!"
                )
                await query.answer("No files found", show_alert=False)
                return
            
            buttons = []
            for file in user_files[:10]:
                file_name = file["file_name"]
                if len(file_name) > 30:
                    file_name = file_name[:27] + '...'
                buttons.append([InlineKeyboardButton(f"📄 {file_name}", callback_data=f"view_{file['message_id']}")])
            
            message_text = f"📂 **ʏᴏᴜʀ ғɪʟᴇs** ({len(user_files)} total)\n\nClick on any file to view details and get links:"
            
            await query.message.edit_text(message_text, reply_markup=InlineKeyboardMarkup(buttons))
            await query.answer("📂 Files list loaded", show_alert=False)
    
    async def start(self):
        """Start the bot"""
        await self.db.init_db()
        await self.app.start()
        print(f"✅ Bot started: @{(await self.app.get_me()).username}")
    
    async def stop(self):
        """Stop the bot"""
        await self.app.stop()
        print("🛑 Bot stopped")
    
    def run(self):
        """Run the bot"""
        self.app.run()
