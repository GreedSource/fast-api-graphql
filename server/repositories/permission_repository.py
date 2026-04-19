from typing import Any, Dict, List

from bson import ObjectId
from pymongo.results import DeleteResult

from server.db.mongo import get_mongo_db
from server.decorators.singleton_decorator import singleton
from server.helpers.mongo_helper import MongoHelper


@singleton
class PermissionRepository:
    def __init__(self) -> None:
        self.__mongo = MongoHelper(
            db=get_mongo_db(),
            allowed_collections={"permissions"},
        )

    async def create(self, data: Dict[str, Any]) -> str:
        result = await self.__mongo.insert_one("permissions", data)
        return str(result.inserted_id)

    async def find_all(self) -> List[Dict[str, Any]]:
        pipeline: List[Dict[str, Any]] = [
            {
                "$lookup": {
                    "from": "modules",
                    "localField": "module_id",
                    "foreignField": "_id",
                    "as": "module",
                }
            },
            {"$unwind": "$module"},
            {
                "$lookup": {
                    "from": "actions",
                    "localField": "action_id",
                    "foreignField": "_id",
                    "as": "action",
                }
            },
            {"$unwind": "$action"},
            {
                "$project": {
                    "_id": 1,
                    "description": 1,
                    "moduleId": "$module._id",
                    "actionId": "$action._id",
                }
            },
        ]

        return await self.__mongo.aggregate("permissions", pipeline)

    async def find_one(self, filter: Dict[str, Any]) -> Dict[str, Any] | None:
        return await self.__mongo.find_one("permissions", filter)

    async def delete(self, permission_id: str) -> DeleteResult:
        return await self.__mongo.delete_one(
            "permissions",
            {"_id": ObjectId(permission_id)},
        )

    async def delete_by_module(self, module_id: str) -> DeleteResult:
        return await self.__mongo.delete_many(
            "permissions",
            {"module_id": ObjectId(module_id)},
        )

    async def delete_by_action(self, action_id: str) -> DeleteResult:
        return await self.__mongo.delete_many(
            "permissions",
            {"action_id": ObjectId(action_id)},
        )
