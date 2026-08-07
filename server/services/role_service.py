from server.decorators.singleton_decorator import singleton
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.helpers.logger_helper import LoggerHelper
from server.models.dto.role_dto import (
    CreateRoleModel,
    RoleItemModel,
    RoleListModel,
    UpdateRoleModel,
)
from server.repositories.role_repository import RoleRepository


@singleton
class RoleService:
    def __init__(self):
        self.__repository = RoleRepository()
        LoggerHelper.info("RoleService initialized")

    async def create(self, payload: CreateRoleModel):
        role_orm = await self.__repository.create(payload.model_dump())
        return RoleItemModel.model_validate(role_orm).model_dump(by_alias=False)

    async def update(self, payload: UpdateRoleModel):
        role_orm = await self.__repository.update(payload.id, payload.model_dump(exclude={"id"}, exclude_none=True))
        if role_orm is None:
            raise CustomGraphQLExceptionHelper("No se encontró el rol para actualizar")
        return RoleItemModel.model_validate(role_orm).model_dump(by_alias=False)

    async def get_roles(self):
        role_orms = await self.__repository.find_all()
        return RoleListModel.model_validate(role_orms).model_dump(by_alias=False)

    async def get_role(self, role_id: str):
        role_orm = await self.__repository.find_by_id(role_id)
        if not role_orm:
            return None
        return RoleItemModel.model_validate(role_orm).model_dump(by_alias=False)

    async def delete_role(self, role_id: str):
        return await self.__repository.delete(role_id)

    async def assign_permissions(self, role_id: str, permission_ids: list[str]):
        role_orm = await self.__repository.assign_permissions(role_id, permission_ids)
        if not role_orm:
            raise CustomGraphQLExceptionHelper("No se pudo asignar permisos al rol")
        return True

    async def add_permissions(self, role_id: str, permission_ids: list[str]):
        role_orm = await self.__repository.add_permissions(role_id, permission_ids)
        if not role_orm:
            raise CustomGraphQLExceptionHelper("No se pudo agregar permisos al rol")
        return True

    async def remove_permissions(self, role_id: str, permission_ids: list[str]):
        role_orm = await self.__repository.remove_permissions(role_id, permission_ids)
        if not role_orm:
            raise CustomGraphQLExceptionHelper("No se pudo remover permisos del rol")
        return True
