from server.decorators.singleton_decorator import singleton
from server.models.dto.module_dto import CreateModuleModel, ModuleItemModel, UpdateModuleModel
from server.repositories.module_repository import ModuleRepository
from server.services.base_service import BaseService


@singleton
class ModuleService(BaseService[CreateModuleModel, UpdateModuleModel, ModuleItemModel]):
    repository = ModuleRepository()
    item_model = ModuleItemModel
    serialize_by_alias = False
    serialize_mode = None
    serialize_exclude_none = False

    async def update(self, payload: UpdateModuleModel):
        module = await self.repository.update(payload.id, payload.model_dump(exclude={"id"}, exclude_none=True))
        return self.serialize(module) if module else None

    async def find_by_id(self, module_id: str):
        return await self.repository.find_by_id(module_id)

    async def find_by_key(self, key: str):
        return await self.repository.find_by_key(key)
