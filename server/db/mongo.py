# server/db/mongo.py
from motor.motor_asyncio import AsyncIOMotorClient
import os

_client: AsyncIOMotorClient | None = None
_db = None


def get_mongo_db():
    global _client, _db

    if _db is None:
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        db_name = os.getenv("MONGO_DB", "mydb")

        _client = AsyncIOMotorClient(uri)
        _db = _client[db_name]

    return _db


async def close_mongo():
    global _client
    if _client:
        _client.close()
