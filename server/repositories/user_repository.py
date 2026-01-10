# server/repositories/user_repository.py
from bson import ObjectId

from server.db.mongo import get_mongo_db
from server.decorators.singleton_decorator import singleton
from server.helpers.logger_helper import LoggerHelper
from server.helpers.mongo_helper import MongoHelper


@singleton
class UserRepository:
    def __init__(self):
        self.__mongo = MongoHelper(
            db=get_mongo_db(),
            allowed_collections={"users"},
        )
        LoggerHelper.info("UserRepository initialized")

    async def create(self, user_data: dict):
        return await self.__mongo.insert_one("users", user_data)

    async def find_by_email(self, email: str):
        return await self.__mongo.find_one("users", {"email": email})

    async def find_by_id(self, user_id: str):
        return await self.__mongo.find_one("users", {"_id": ObjectId(user_id)})

    async def find_all(self):
        return await self.__mongo.find_many("users", {})

    async def update(self, user_id: str, update_data: dict):
        return await self.__mongo.update_one(
            "users",
            {"_id": ObjectId(user_id)},
            {"$set": update_data},
        )

    async def delete(self, user_id: str):
        return await self.__mongo.delete_one(
            "users",
            {"_id": ObjectId(user_id)},
        )
