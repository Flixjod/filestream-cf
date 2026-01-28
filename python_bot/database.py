"""
MongoDB Database Handler for FileStream Bot
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List, Dict
from datetime import datetime
from config import config
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.files = None
        self.users = None
    
    async def connect(self):
        """Connect to MongoDB database"""
        try:
            self.client = AsyncIOMotorClient(config.MONGODB_URI)
            self.db = self.client[config.DB_NAME]
            self.files = self.db.files
            self.users = self.db.users
            
            # Create indexes
            await self.files.create_index("message_id", unique=True)
            await self.files.create_index("user_id")
            await self.files.create_index("secret_token", unique=True)
            await self.users.create_index("user_id", unique=True)
            
            logger.info("✅ Connected to MongoDB successfully")
            return True
        except Exception as e:
            logger.error(f"❌ MongoDB connection error: {e}")
            return False
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("📤 MongoDB connection closed")
    
    # ========== File Operations ==========
    
    async def add_file(self, file_data: Dict) -> bool:
        """Add a new file to database"""
        try:
            file_doc = {
                "file_id": file_data.get("file_id"),
                "message_id": str(file_data.get("message_id")),
                "user_id": str(file_data.get("user_id")),
                "username": file_data.get("username", ""),
                "file_name": file_data.get("file_name"),
                "file_size": file_data.get("file_size"),
                "file_type": file_data.get("file_type"),
                "secret_token": file_data.get("secret_token"),
                "created_at": datetime.utcnow(),
                "downloads": 0
            }
            await self.files.insert_one(file_doc)
            logger.info(f"✅ File added to database: {file_data.get('file_name')}")
            return True
        except Exception as e:
            logger.error(f"❌ Error adding file: {e}")
            return False
    
    async def get_file(self, message_id: str) -> Optional[Dict]:
        """Get file by message_id"""
        try:
            file_doc = await self.files.find_one({"message_id": str(message_id)})
            return file_doc
        except Exception as e:
            logger.error(f"❌ Error getting file: {e}")
            return None
    
    async def get_file_by_token(self, token: str) -> Optional[Dict]:
        """Get file by secret token"""
        try:
            file_doc = await self.files.find_one({"secret_token": token})
            return file_doc
        except Exception as e:
            logger.error(f"❌ Error getting file by token: {e}")
            return None
    
    async def delete_file(self, message_id: str) -> bool:
        """Delete file from database"""
        try:
            result = await self.files.delete_one({"message_id": str(message_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"❌ Error deleting file: {e}")
            return False
    
    async def delete_all_files(self) -> int:
        """Delete all files from database"""
        try:
            result = await self.files.delete_many({})
            return result.deleted_count
        except Exception as e:
            logger.error(f"❌ Error deleting all files: {e}")
            return 0
    
    async def get_user_files(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get all files uploaded by a user"""
        try:
            cursor = self.files.find({"user_id": str(user_id)}).sort("created_at", -1).limit(limit)
            files = await cursor.to_list(length=limit)
            return files
        except Exception as e:
            logger.error(f"❌ Error getting user files: {e}")
            return []
    
    async def increment_downloads(self, message_id: str) -> bool:
        """Increment download counter for a file"""
        try:
            await self.files.update_one(
                {"message_id": str(message_id)},
                {"$inc": {"downloads": 1}}
            )
            return True
        except Exception as e:
            logger.error(f"❌ Error incrementing downloads: {e}")
            return False
    
    # ========== User Operations ==========
    
    async def register_user(self, user_data: Dict) -> bool:
        """Register or update user"""
        try:
            user_doc = {
                "user_id": str(user_data.get("user_id")),
                "username": user_data.get("username", ""),
                "first_name": user_data.get("first_name", ""),
                "last_name": user_data.get("last_name", ""),
                "first_used": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "total_files": 1
            }
            
            # Upsert: insert if new, update if exists
            await self.users.update_one(
                {"user_id": str(user_data.get("user_id"))},
                {
                    "$setOnInsert": {"first_used": user_doc["first_used"]},
                    "$set": {
                        "username": user_doc["username"],
                        "first_name": user_doc["first_name"],
                        "last_name": user_doc["last_name"],
                        "last_activity": user_doc["last_activity"]
                    },
                    "$inc": {"total_files": 1}
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"❌ Error registering user: {e}")
            return False
    
    async def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by user_id"""
        try:
            user_doc = await self.users.find_one({"user_id": str(user_id)})
            return user_doc
        except Exception as e:
            logger.error(f"❌ Error getting user: {e}")
            return None
    
    # ========== Statistics ==========
    
    async def get_stats(self) -> Dict:
        """Get bot statistics"""
        try:
            total_files = await self.files.count_documents({})
            total_users = await self.users.count_documents({})
            
            # Get total downloads
            pipeline = [{"$group": {"_id": None, "total": {"$sum": "$downloads"}}}]
            result = await self.files.aggregate(pipeline).to_list(length=1)
            total_downloads = result[0]["total"] if result else 0
            
            return {
                "total_files": total_files,
                "total_users": total_users,
                "total_downloads": total_downloads
            }
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {"total_files": 0, "total_users": 0, "total_downloads": 0}


# Singleton database instance
db = Database()
