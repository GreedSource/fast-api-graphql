from server.decorators.singleton_decorator import singleton
from server.models.dto.module_dto import (
    CreateModuleModel,
    ModuleItemModel,
    ModuleListModel,
    UpdateModuleModel,
)
from server.repositories.module_repository import ModuleRepository


@singleton
class ModuleService:
    def __init__(self):
        self.__repository = ModuleRepository()

    async def create(self, payload: CreateModuleModel):
        module_orm = await self.__repository.create(payload.model_dump())
        return ModuleItemModel.model_validate(module_orm).model_dump(by_alias=False)

    async def update(self, payload: UpdateModuleModel):
        module_orm = await self.__repository.update(payload.id, payload.model_dump(exclude={"id"}, exclude_none=True))
        if not module_orm:
            return None
        return ModuleItemModel.model_validate(module_orm).model_dump(by_alias=False)

    async def get_all(self):
        module_orms = await self.__repository.find_all()
        return ModuleListModel.model_validate(module_orms).model_dump(by_alias=False)

    async def get_one(self, module_id: str):
        module_orm = await self.__repository.find_by_id(module_id)
        if not module_orm:
            return None
        return ModuleItemModel.model_validate(module_orm).model_dump(by_alias=False)

    async def find_by_id(self, module_id: str):
        return await self.__repository.find_by_id(module_id)

    async def find_by_key(self, key: str):
        return await self.__repository.find_by_key(key)
