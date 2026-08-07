from server.decorators.singleton_decorator import singleton
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.helpers.logger_helper import LoggerHelper
from server.helpers.redis_helper import RedisHelper
from server.models.dto.user_dto import UserItemModel, UserListModel
from server.repositories.user_repository import UserRepository
from server.services.role_service import RoleService


@singleton
class UserService:
    def __init__(self):
        self.__repository = UserRepository()
        self.__role_service = RoleService()
        self.__redis = RedisHelper()
        LoggerHelper.info("UserService initialized")

    async def get_users(self):
        user_orms = await self.__repository.find_all()
        return UserListModel.model_validate(user_orms).model_dump(by_alias=False)

    async def get_user(self, user_id: str):
        user_orm = await self.__repository.find_by_id(user_id)
        if not user_orm:
            return None
        # Retorna dict con permisos resueltos (usado por @require_token)
        return await self.__repository.aggregate_user_with_role_permissions(user_id)

    async def update_user(self, user_id: str, update_data: dict):
        role_id = update_data.get("role_id")
        if role_id:
            role = await self.__role_service.get_role(str(role_id))
            if not role:
                raise CustomGraphQLExceptionHelper("Role not found")

        if update_data:
            await self.__repository.update(user_id, update_data)

        user_orm = await self.__repository.find_by_id(user_id)
        if not user_orm:
            raise CustomGraphQLExceptionHelper("Usuario no encontrado")
        payload = UserItemModel.model_validate(user_orm).model_dump(by_alias=False, mode="json")
        await self.__redis.publish_json(f"user_updated:{user_id}", payload)
        return payload

    async def delete_user(self, user_id: str):
        return await self.__repository.delete(user_id)
