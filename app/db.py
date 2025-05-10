from motor.motor_asyncio import AsyncIOMotorClient
from core.config import get_settings


db_client = None


async def connect_to_mongo():
    global client, db_client
    client = AsyncIOMotorClient(get_settings().MONGO_DB_URL)
    if client is None:
        raise Exception("MongoDB not connected")

    print("✅ MongoDB connected")

    db_client = client[get_settings().MONGO_DB_NAME]
    if db_client is None:
        raise Exception("Database not found")

    print("✅ Database connected")
    return db_client


async def close_mongo_connection():
    if client:
        client.close()
        print("❎ MongoDB connection closed")
