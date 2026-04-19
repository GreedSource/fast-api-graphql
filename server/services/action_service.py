from typing import Any, Dict, List, cast

from server.decorators.singleton_decorator import singleton
from server.models.action_model import (
    ActionItemModel,
    ActionListModel,
    CreateActionModel,
)
from server.repositories.action_repository import ActionRepository


@singleton
class ActionService:
    def __init__(self) -> None:
        self.__repository = ActionRepository()

    async def create(self, payload: CreateActionModel) -> Dict[str, Any]:
        inserted_id = await self.__repository.create(payload.model_dump())
        return ActionItemModel(**payload.model_dump(), _id=str(inserted_id)).model_dump()

    async def get_all(self) -> List[Dict[str, Any]]:
        actions = await self.__repository.find_all()
        return cast(List[Dict[str, Any]], ActionListModel.model_validate(actions).model_dump(by_alias=False))

    async def find_by_id(self, action_id: str) -> Dict[str, Any] | None:
        return await self.__repository.find_by_id(action_id)
