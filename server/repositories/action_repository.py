from bson import ObjectId

from server.db.mongo import get_mongo_db
from server.decorators.singleton_decorator import singleton
from server.helpers.mongo_helper import MongoHelper


@singleton
class ActionRepository:
    def __init__(self):
        self.__mongo = MongoHelper(
            db=get_mongo_db(),
            allowed_collections={"actions"},
        )

    async def create(self, data: dict):
        return await self.__mongo.insert_one("actions", data)

    async def find_all(self):
        return await self.__mongo.find_many("actions", {})

    async def find_by_id(self, action_id: str):
        return await self.__mongo.find_one("actions", {"_id": ObjectId(action_id)})
