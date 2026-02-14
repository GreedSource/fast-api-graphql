from server.decorators.singleton_decorator import singleton
from server.models.module_model import (
    CreateModuleModel,
    ModuleItemModel,
    UpdateModuleModel,
)
from server.repositories.module_repository import ModuleRepository


@singleton
class ModuleService:
    def __init__(self):
        self.__repository = ModuleRepository()

    async def create(self, payload: CreateModuleModel):
        inserted_id = await self.__repository.create(payload.model_dump())
        return ModuleItemModel(**payload.model_dump(), _id=str(inserted_id))

    async def update(self, payload: UpdateModuleModel):
        result = await self.__repository.update(payload.id, payload.model_dump(exclude={"id"}, exclude_none=True))
        return ModuleItemModel(**result)

    async def get_all(self):
        modules = await self.__repository.find_all()
        return modules

    async def get_one(self, module_id: str):
        return await self.__repository.find_by_id(module_id)

    async def find_by_id(self, module_id: str):
        return await self.__repository.find_by_id(module_id)
