from pymongo import MongoClient, DESCENDING
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Optional, List, Dict
from config import Config

class Database:
    """MongoDB database handler"""
    
    def __init__(self):
        self.client = AsyncIOMotorClient(Config.MONGO_URI)
        self.db = self.client[Config.DATABASE_NAME]
        self.files = self.db.files
        self.users = self.db.users
    
    async def init_db(self):
        """Initialize database with indexes"""
        try:
            # Create indexes for better query performance
            await self.files.create_index("file_id", unique=True)
            await self.files.create_index("message_id", unique=True)
            await self.files.create_index("user_id")
            await self.files.create_index("secret_token", unique=True)
            await self.files.create_index([("created_at", DESCENDING)])
            
            await self.users.create_index("user_id", unique=True)
            
            print("✅ Database initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            return False
    
    async def add_file(self, file_data: Dict) -> bool:
        """Add new file to database"""
        try:
            file_doc = {
                "file_id": file_data["file_id"],
                "message_id": file_data["message_id"],
                "user_id": str(file_data["user_id"]),
                "username": file_data.get("username", ""),
                "file_name": file_data["file_name"],
                "file_size": file_data["file_size"],
                "file_type": file_data["file_type"],
                "secret_token": file_data["secret_token"],
                "created_at": datetime.utcnow(),
                "downloads": 0
            }
            
            await self.files.insert_one(file_doc)
            return True
        except Exception as e:
            print(f"Error adding file: {e}")
            return False
    
    async def get_file(self, message_id: str) -> Optional[Dict]:
        """Get file by message_id"""
        try:
            return await self.files.find_one({"message_id": message_id})
        except Exception as e:
            print(f"Error getting file: {e}")
            return None
    
    async def get_file_by_token(self, token: str) -> Optional[Dict]:
        """Get file by secret token"""
        try:
            return await self.files.find_one({"secret_token": token})
        except Exception as e:
            return None
    
    async def delete_file(self, message_id: str) -> bool:
        """Delete file from database"""
        try:
            result = await self.files.delete_one({"message_id": message_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    async def delete_all_files(self) -> bool:
        """Delete all files from database"""
        try:
            await self.files.delete_many({})
            return True
        except Exception as e:
            print(f"Error deleting all files: {e}")
            return False
    
    async def get_user_files(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get files uploaded by a user"""
        try:
            cursor = self.files.find({"user_id": user_id}).sort("created_at", DESCENDING).limit(limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            print(f"Error getting user files: {e}")
            return []
    
    async def register_user(self, user_data: Dict) -> bool:
        """Register or update user in database"""
        try:
            user_doc = {
                "user_id": str(user_data["user_id"]),
                "username": user_data.get("username", ""),
                "first_name": user_data.get("first_name", ""),
                "last_name": user_data.get("last_name", ""),
                "last_activity": datetime.utcnow()
            }
            
            await self.users.update_one(
                {"user_id": str(user_data["user_id"])},
                {
                    "$set": user_doc,
                    "$inc": {"total_files": 1},
                    "$setOnInsert": {"first_used": datetime.utcnow()}
                },
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error registering user: {e}")
            return False
    
    async def increment_downloads(self, message_id: str) -> bool:
        """Increment download counter for a file"""
        try:
            await self.files.update_one(
                {"message_id": message_id},
                {"$inc": {"downloads": 1}}
            )
            return True
        except Exception as e:
            return False
    
    async def get_stats(self) -> Dict:
        """Get bot statistics"""
        try:
            total_files = await self.files.count_documents({})
            total_users = await self.users.count_documents({})
            
            # Get total downloads
            pipeline = [
                {"$group": {"_id": None, "total": {"$sum": "$downloads"}}}
            ]
            result = await self.files.aggregate(pipeline).to_list(length=1)
            total_downloads = result[0]["total"] if result else 0
            
            return {
                "total_files": total_files,
                "total_users": total_users,
                "total_downloads": total_downloads
            }
        except Exception as e:
            return {"total_files": 0, "total_users": 0, "total_downloads": 0}
