from server.decorators.singleton_decorator import singleton

# from server.helpers.mail_helper import MailHelper
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.helpers.logger_helper import LoggerHelper
from server.helpers.redis_helper import RedisHelper
from server.models.user_model import UserItemModel, UserListModel
from server.repositories.user_repository import UserRepository
from server.services.role_service import RoleService


@singleton
class UserService:
    def __init__(self):
        self.__repository = UserRepository()
        self.__role_service = RoleService()
        self.__redis = RedisHelper()
        LoggerHelper.info("UserService initialized")

    # -----------------
    # Actions
    # -----------------

    async def get_users(self):
        users = await self.__repository.aggregate_users_with_roles()
        return UserListModel(users).model_dump(by_alias=False)

    async def get_user(self, user_id: str):
        user = await self.__repository.aggregate_user_with_role_permissions(user_id)
        if not user:
            return None
        return UserItemModel(**user).model_dump(by_alias=False)

    async def update_user(self, user_id: str, update_data: dict):
        role_id = update_data.get("role_id")
        if role_id:
            role = await self.__role_service.get_role(role_id)
            if not role:
                raise CustomGraphQLExceptionHelper("Role not found")

        if update_data:
            await self.__repository.update(user_id, update_data)

        user = await self.__repository.aggregate_user_with_role_permissions(user_id)
        payload = UserItemModel(**user).model_dump(by_alias=False)
        await self.__redis.publish_json(f"user_updated:{user_id}", payload)
        return payload

    async def delete_user(self, user_id: str):
        result = await self.__repository.delete(user_id)
        return result.deleted_count == 1
