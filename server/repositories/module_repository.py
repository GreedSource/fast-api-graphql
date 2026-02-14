from bson import ObjectId

from server.db.mongo import get_mongo_db
from server.decorators.singleton_decorator import singleton
from server.helpers.mongo_helper import MongoHelper


@singleton
class ModuleRepository:
    def __init__(self):
        self.__mongo = MongoHelper(
            db=get_mongo_db(),
            allowed_collections={"modules"},
        )

    async def create(self, data: dict):
        return await self.__mongo.insert_one("modules", data)

    async def find_all(self):
        return await self.__mongo.find_many("modules", {})

    async def find_by_id(self, module_id: str):
        return await self.__mongo.find_one("modules", {"_id": ObjectId(module_id)})

    async def find_by_key(self, key: str):
        return await self.__mongo.find_one("modules", {"key": key})

    async def update(self, module_id: str, data: dict):
        return await self.__mongo.update_one(
            "modules",
            {"_id": ObjectId(module_id)},
            {"$set": data},
        )
