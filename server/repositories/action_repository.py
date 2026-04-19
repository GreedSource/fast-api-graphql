from typing import Any, Dict, List

from bson import ObjectId

from server.db.mongo import get_mongo_db
from server.decorators.singleton_decorator import singleton
from server.helpers.mongo_helper import MongoHelper


@singleton
class ActionRepository:
    def __init__(self) -> None:
        self.__mongo = MongoHelper(
            db=get_mongo_db(),
            allowed_collections={"actions"},
        )

    async def create(self, data: Dict[str, Any]) -> str:
        inserted = await self.__mongo.insert_one("actions", data)
        return str(inserted.inserted_id)

    async def find_all(self) -> List[Dict[str, Any]]:
        return await self.__mongo.find_many("actions", {})

    async def find_by_id(self, action_id: str) -> Dict[str, Any] | None:
        return await self.__mongo.find_one("actions", {"_id": ObjectId(action_id)})
