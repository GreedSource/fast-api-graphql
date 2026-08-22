from server.decorators.singleton_decorator import singleton
from server.models.dto.action_dto import ActionItemModel, CreateActionModel
from server.repositories.action_repository import ActionRepository
from server.services.base_service import BaseService


@singleton
class ActionService(BaseService[CreateActionModel, None, ActionItemModel]):
    repository = ActionRepository()
    item_model = ActionItemModel
    serialize_by_alias = False
    serialize_mode = None
    serialize_exclude_none = False

    async def find_by_id(self, action_id: str):
        return await self.repository.find_by_id(action_id)

    async def find_by_key(self, key: str):
        return await self.repository.find_by_key(key)
