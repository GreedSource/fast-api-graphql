from typing import Any, Dict

from bson import ObjectId

from server.db.mongo import get_mongo_db
from server.decorators.singleton_decorator import singleton
from server.helpers.mongo_helper import MongoHelper


@singleton
class ModuleRepository:
    def __init__(self) -> None:
        self.__mongo = MongoHelper(
            db=get_mongo_db(),
            allowed_collections={"modules"},
        )

    async def create(self, data: Dict[str, Any]) -> str:
        result = await self.__mongo.insert_one("modules", data)
        return str(result.inserted_id)

    async def find_all(self) -> list[Dict[str, Any]]:
        return await self.__mongo.find_many("modules", {})

    async def find_by_id(self, module_id: str) -> Dict[str, Any] | None:
        return await self.__mongo.find_one("modules", {"_id": ObjectId(module_id)})

    async def find_by_key(self, key: str) -> Dict[str, Any] | None:
        return await self.__mongo.find_one("modules", {"key": key})

    async def update(self, module_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.__mongo.update_one(
            "modules",
            {"_id": ObjectId(module_id)},
            {"$set": data},
        )
