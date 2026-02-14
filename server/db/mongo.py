# server/db/mongo.py
from motor.motor_asyncio import AsyncIOMotorClient

from server.config.settings import settings

_client: AsyncIOMotorClient | None = None
_db = None


def get_mongo_db():
    global _client, _db

    if _db is None:
        uri = settings.MONGO_URI
        db_name = settings.MONGO_DB_NAME
        _client = AsyncIOMotorClient(uri)
        _db = _client[db_name]
    return _db


async def close_mongo():
    global _client
    if _client:
        _client.close()
