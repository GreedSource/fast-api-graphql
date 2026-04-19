from typing import Any, Dict, List, cast

from server.decorators.singleton_decorator import singleton
from server.helpers.custom_graphql_exception_helper import (
    CustomGraphQLExceptionHelper,
)
from server.helpers.logger_helper import LoggerHelper
from server.models.role_model import (
    CreateRoleModel,
    RoleItemModel,
    RoleListModel,
    UpdateRoleModel,
)
from server.repositories.role_repository import RoleRepository


@singleton
class RoleService:
    def __init__(self) -> None:
        self.__repository = RoleRepository()
        LoggerHelper.info("RoleService initialized")

    # -----------------
    # Actions
    # -----------------

    async def create(self, payload: CreateRoleModel) -> RoleItemModel:
        inserted_id = await self.__repository.create(payload.model_dump())
        return RoleItemModel(
            **payload.model_dump(), _id=str(inserted_id)
        )  # Return the created role as a Dict[str, Any]

    async def update(self, payload: UpdateRoleModel) -> RoleItemModel:
        await self.__repository.update(payload.id, payload.model_dump(exclude={"id"}, exclude_none=True))
        result = await self.__repository.find_by_id(payload.id)
        if result is None:
            raise CustomGraphQLExceptionHelper("No se encontró el rol para actualizar")
        return RoleItemModel(**result)  # Return the created role as a Dict[str, Any]

    async def get_roles(self) -> List[Dict[str, Any]]:
        roles = await self.__repository.find_all()
        return cast(List[Dict[str, Any]], RoleListModel.model_validate(roles).model_dump())

    async def get_role(self, role_id: str) -> Dict[str, Any] | None:
        role = await self.__repository.find_by_id(role_id)
        if not role:
            return None
        return RoleItemModel(**role).model_dump()

    async def delete_role(self, role_id: str) -> bool:
        result: bool = await self.__repository.delete(role_id) > 0
        return result

    async def add_permissions(self, role_id: str, permission_ids: list[str]) -> bool:
        result = await self.__repository.add_permissions(role_id, permission_ids)
        if not result:
            raise CustomGraphQLExceptionHelper("No se pudo asignar permisos al rol")
        return True

    async def remove_permissions(self, role_id: str, permission_ids: list[str]) -> bool:
        result = await self.__repository.remove_permissions(role_id, permission_ids)
        if not result:
            raise CustomGraphQLExceptionHelper("No se pudo remover permisos del rol")
        return True
