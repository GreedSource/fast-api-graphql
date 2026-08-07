from server.decorators.singleton_decorator import singleton
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.models.dto.permission_dto import (
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
        module_orm = await self.__module_service.find_by_id(str(payload.module_id))
        if not module_orm:
            module_orm = await self.__module_service.find_by_key(str(payload.module_id))
        if not module_orm:
            raise CustomGraphQLExceptionHelper("Module not found")

        action_orm = await self.__action_service.find_by_id(str(payload.action_id))
        if not action_orm:
            action_orm = await self.__action_service.find_by_key(str(payload.action_id))
        if not action_orm:
            raise CustomGraphQLExceptionHelper("Action not found")

        # Verificar duplicado
        existing = await self.__permission_repo.find_by_module_and_action(module_orm.id, action_orm.id)
        if existing:
            raise CustomGraphQLExceptionHelper("El permiso ya existe para ese módulo y acción")

        perm_orm = await self.__permission_repo.create(
            {
                "module_id": module_orm.id,
                "action_id": action_orm.id,
                "description": payload.description,
            }
        )

        return PermissionItemModel(
            id=perm_orm.id,
            moduleId=perm_orm.module_id,
            actionId=perm_orm.action_id,
            moduleKey=module_orm.key,
            actionKey=action_orm.key,
            description=perm_orm.description,
        ).model_dump(by_alias=True)

    async def get_all(self):
        perm_orms = await self.__permission_repo.find_all()
        result = [
            PermissionItemModel(
                id=p.id,
                moduleId=p.module_id,
                actionId=p.action_id,
                moduleKey=p.module.key if p.module else "unknown",
                actionKey=p.action.key if p.action else "unknown",
                description=p.description,
            )
            for p in perm_orms
        ]
        return PermissionListModel.model_validate(result).model_dump(by_alias=True)

    async def delete(self, permission_id: str):
        return await self.__permission_repo.delete(permission_id)
