from server.decorators.singleton_decorator import singleton
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.models.permission_model import (
    CreatePermissionModel,
    PermissionItemModel,
    PermissionListModel,
)
from server.repositories.permission_repository import PermissionRepository
from server.services.action_service import ActionService
from server.services.module_service import ModuleService


@singleton
class PermissionService:
    def __init__(self):
        self.__permission_repo = PermissionRepository()
        self.__module_service = ModuleService()
        self.__action_service = ActionService()

    async def create(self, payload: CreatePermissionModel):
        module = await self.__module_service.find_by_id(payload.module_id)
        if not module:
            raise CustomGraphQLExceptionHelper("Module not found")

        action = await self.__action_service.find_by_id(payload.action_id)
        if not action:
            raise CustomGraphQLExceptionHelper("Action not found")

        permission_id = await self.__permission_repo.create(
            {
                "module_id": module["_id"],
                "action_id": action["_id"],
                "description": payload.description,
            }
        )

        return PermissionItemModel(
            id=str(permission_id),
            moduleId=module["key"],
            actionId=action["key"],
            moduleKey=module["key"],
            actionKey=action["key"],
            description=payload.description,
        ).model_dump()

    async def get_all(self):
        permissions = await self.__permission_repo.find_all()

        # Enriquecer cada permiso con los nombres de modulo y accion
        enriched_permissions = []
        for perm in permissions:
            module = await self.__module_service.find_by_id(perm.get("moduleId"))
            action = await self.__action_service.find_by_id(perm.get("actionId"))

            enriched_perm = {
                **perm,
                "moduleKey": module.get("key") if module else "unknown",
                "actionKey": action.get("key") if action else "unknown",
            }
            enriched_permissions.append(enriched_perm)

        return PermissionListModel.model_validate(enriched_permissions).model_dump()

    async def delete(self, permission_id: str):
        result = await self.__permission_repo.delete(permission_id)
        return result.deleted_count == 1
