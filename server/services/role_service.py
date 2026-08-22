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
from server.services.base_service import BaseService


@singleton
class RoleService(BaseService[CreateRoleModel, UpdateRoleModel, RoleItemModel]):
    repository = RoleRepository()
    item_model = RoleItemModel
    serialize_by_alias = False
    serialize_mode = None
    serialize_exclude_none = False

    def __init__(self):
        LoggerHelper.info("RoleService initialized")

    async def create(self, payload: CreateRoleModel):
        return await super().create(payload)

    async def update(self, payload: UpdateRoleModel):
        role_orm = await self.repository.update(payload.id, payload.model_dump(exclude={"id"}, exclude_none=True))
        if role_orm is None:
            raise CustomGraphQLExceptionHelper("No se encontró el rol para actualizar")
        return self.serialize(role_orm)

    async def get_roles(self):
        role_orms = await self.repository.find_all()
        return RoleListModel.model_validate(role_orms).model_dump(by_alias=False)

    async def get_role(self, role_id: str):
        return await self.get_one(role_id)

    async def delete_role(self, role_id: str):
        return await self.delete(role_id)

    async def assign_permissions(self, role_id: str, permission_ids: list[str]):
        role_orm = await self.repository.assign_permissions(role_id, permission_ids)
        if not role_orm:
            raise CustomGraphQLExceptionHelper("No se pudo asignar permisos al rol")
        return True

    async def add_permissions(self, role_id: str, permission_ids: list[str]):
        role_orm = await self.repository.add_permissions(role_id, permission_ids)
        if not role_orm:
            raise CustomGraphQLExceptionHelper("No se pudo agregar permisos al rol")
        return True

    async def remove_permissions(self, role_id: str, permission_ids: list[str]):
        role_orm = await self.repository.remove_permissions(role_id, permission_ids)
        if not role_orm:
            raise CustomGraphQLExceptionHelper("No se pudo remover permisos del rol")
        return True
