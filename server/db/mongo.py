from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from server.config.settings import settings

_client: AsyncIOMotorClient[dict[str, Any]] | None = None
_db: AsyncIOMotorDatabase[dict[str, Any]] | None = None


def get_mongo_db() -> AsyncIOMotorDatabase[dict[str, Any]]:
    global _client, _db

    if _db is None:
        uri = settings.MONGO_URI
        db_name = settings.MONGO_DB_NAME
        _client = AsyncIOMotorClient(uri)
        _db = _client[db_name]
    return _db


async def close_mongo() -> None:
    global _client
    if _client:
        _client.close()
