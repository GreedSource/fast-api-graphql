# server/services/user_service.py
from server.decorators.singleton_decorator import singleton

# from server.helpers.mail_helper import MailHelper
from server.helpers.logger_helper import LoggerHelper
from server.models.user_model import UserItemModel, UserListModel
from server.repositories.user_repository import UserRepository


@singleton
class UserService:
    def __init__(self):
        self.__repository = UserRepository()
        # self.__mail_helper = MailHelper()
        LoggerHelper.info("UserService initialized")

    # -----------------
    # Actions
    # -----------------

    async def get_users(self):
        users = await self.__repository.aggregate_users_with_roles()
        return UserListModel.model_validate(users).model_dump(by_alias=False)

    async def get_user(self, user_id: str):
        user = await self.__repository.aggregate_user_with_role_permissions(user_id)
        if not user:
            return None
        return UserItemModel(**user).model_dump(by_alias=False)

    async def update_user(self, user_id: str, update_data: dict):
        if update_data:
            await self.__repository.update(user_id, update_data)

        user = await self.__repository.aggregate_user_with_role(user_id)
        return UserItemModel(**user).model_dump()

    async def delete_user(self, user_id: str):
        result = await self.__repository.delete(user_id)
        return result.deleted_count == 1
