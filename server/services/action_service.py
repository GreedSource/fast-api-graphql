from server.decorators.singleton_decorator import singleton
from server.models.dto.action_dto import ActionItemModel, ActionListModel, CreateActionModel
from server.repositories.action_repository import ActionRepository


@singleton
class ActionService:
    def __init__(self):
        self.__repository = ActionRepository()

    async def create(self, payload: CreateActionModel):
        action_orm = await self.__repository.create(payload.model_dump())
        return ActionItemModel.model_validate(action_orm).model_dump(by_alias=False)

    async def get_all(self):
        action_orms = await self.__repository.find_all()
        return ActionListModel.model_validate(action_orms).model_dump(by_alias=False)

    async def find_by_id(self, action_id: str):
        return await self.__repository.find_by_id(action_id)

    async def find_by_key(self, key: str):
        return await self.__repository.find_by_key(key)
