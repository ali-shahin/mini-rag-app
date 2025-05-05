from motor.motor_asyncio import AsyncIOMotorClient
from core.config import get_settings


db = None


async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(get_settings().MONGO_DB_URL)
    db = client[get_settings().MONGO_DB_NAME]
    print("✅ MongoDB connected")


async def close_mongo_connection():
    if client:
        client.close()
        print("❎ MongoDB connection closed")
