# server/services/role_service.py
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
    def __init__(self):
        self.__repository = RoleRepository()
        LoggerHelper.info("RoleService initialized")

    # -----------------
    # Actions
    # -----------------

    async def create(self, payload: CreateRoleModel):
        inserted_id = await self.__repository.create(payload.model_dump())
        return RoleItemModel(
            **payload.model_dump(), _id=str(inserted_id)
        )  # Return the created role as a dict

    async def update(self, payload: UpdateRoleModel):
        result = await self.__repository.update(
            payload.id, payload.model_dump(exclude={"id"}, exclude_none=True)
        )
        LoggerHelper.info(f"Update result: {result}")
        if not result:
            raise CustomGraphQLExceptionHelper("No se encontró el rol para actualizar")
        return RoleItemModel(**result)  # Return the created role as a dict

    async def get_roles(self):
        roles = await self.__repository.find_all()
        return RoleListModel.model_validate(roles).model_dump()

    async def get_role(self, role_id: str):
        role = await self.__repository.find_by_id(role_id)
        if not role:
            return None
        return RoleItemModel(**role).model_dump()

    async def delete_role(self, role_id: str):
        result = await self.__repository.delete(role_id)
        return result.deleted_count == 1
