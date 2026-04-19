from typing import Any, Dict, List, cast

from server.decorators.singleton_decorator import singleton
from server.models.module_model import (
    CreateModuleModel,
    ModuleItemModel,
    ModuleListModel,
    UpdateModuleModel,
)
from server.repositories.module_repository import ModuleRepository


@singleton
class ModuleService:
    def __init__(self) -> None:
        self.__repository = ModuleRepository()

    async def create(self, payload: CreateModuleModel) -> Dict[str, Any]:
        inserted_id = await self.__repository.create(payload.model_dump())
        return ModuleItemModel(**payload.model_dump(), _id=str(inserted_id)).model_dump()

    async def update(self, payload: UpdateModuleModel) -> Dict[str, Any]:
        result = await self.__repository.update(payload.id, payload.model_dump(exclude={"id"}, exclude_none=True))
        return ModuleItemModel(**result).model_dump(by_alias=False)

    async def get_all(self) -> List[Dict[str, Any]]:
        modules = await self.__repository.find_all()
        return cast(List[Dict[str, Any]], ModuleListModel.model_validate(modules).model_dump(by_alias=False))

    async def get_one(self, module_id: str) -> Dict[str, Any] | None:
        module = await self.__repository.find_by_id(module_id)
        if not module:
            return None
        return ModuleItemModel(**module).model_dump(by_alias=False)

    async def find_by_id(self, module_id: str) -> Dict[str, Any] | None:
        return await self.__repository.find_by_id(module_id)
