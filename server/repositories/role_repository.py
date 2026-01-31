# server/repositories/role_repository.py
from bson import ObjectId

from server.db.mongo import get_mongo_db
from server.decorators.singleton_decorator import singleton
from server.helpers.logger_helper import LoggerHelper
from server.helpers.mongo_helper import MongoHelper


@singleton
class RoleRepository:
    def __init__(self):
        self.__mongo = MongoHelper(
            db=get_mongo_db(),
            allowed_collections={"roles"},
        )
        LoggerHelper.info("RoleRepository initialized")

    async def create(self, role_data: dict):
        return await self.__mongo.insert_one("roles", role_data)

    async def find_by_id(self, role_id: str):
        return await self.__mongo.find_one("roles", {"_id": ObjectId(role_id)})

    async def find_by_name(self, name: str):
        return await self.__mongo.find_one("roles", {"name": name})

    async def find_all(self):
        return await self.__mongo.find_many("roles", {})

    async def update(self, role_id: str, update_data: dict):
        return await self.__mongo.update_one(
            "roles",
            {"_id": ObjectId(role_id)},
            {"$set": update_data},
        )

    async def add_permissions(
        self,
        role_id: str,
        permission_ids: list[str],
    ):
        object_ids = [ObjectId(pid) for pid in permission_ids]

        return await self.__mongo.update_one(
            "roles",
            {"_id": ObjectId(role_id)},
            {"$addToSet": {"permissions": {"$each": object_ids}}},
        )

    async def remove_permissions(
        self,
        role_id: str,
        permission_ids: list[str],
    ):
        object_ids = [ObjectId(pid) for pid in permission_ids]

        return await self.__mongo.update_one(
            "roles",
            {"_id": ObjectId(role_id)},
            {"$pull": {"permissions": {"$in": object_ids}}},
        )

    async def delete(self, role_id: str):
        return await self.__mongo.delete_one(
            "roles",
            {"_id": ObjectId(role_id)},
        )
