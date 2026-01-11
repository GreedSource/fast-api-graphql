# server/services/auth_service.py
import os

from server.decorators.singleton_decorator import singleton
from server.helpers.custom_graphql_exception_helper import (
    CustomGraphQLExceptionHelper,
)
from server.helpers.logger_helper import LoggerHelper
from server.helpers.mail_helper import MailHelper
from server.models.user_model import UserItemModel
from server.repositories.user_repository import UserRepository
from server.utils.auth_utils import (
    verify_password,
    create_token,
    create_refresh_token,
    verify_refresh_token,
)


@singleton
class AuthService:
    def __init__(self):
        self.__repository = UserRepository()

        self.__mail_helper = MailHelper()
        LoggerHelper.info("AuthService initialized")

    # -----------------
    # Actions
    # -----------------

    async def register(self, user_data: dict):
        inserted_id = await self.__repository.create(user_data)
        user_data["_id"] = inserted_id
        model = UserItemModel(**user_data)
        return {
            "accessToken": create_token({"id": str(inserted_id)}),
            "refreshToken": create_refresh_token({"id": str(inserted_id)}),
            "user": model.model_dump(),
        }

    async def login(self, email: str, password: str):
        user = await self.__repository.find_by_email(email)

        if not user or not verify_password(password, user["password"]):
            raise CustomGraphQLExceptionHelper("Credenciales inválidas")

        model = UserItemModel(**user)
        return {
            "accessToken": create_token(model.model_dump()),
            "refreshToken": create_refresh_token({"id": str(user["_id"])}),
            "user": model.model_dump(),
        }

    async def refresh_token(self, refresh_token: str):
        payload = verify_refresh_token(refresh_token)

        user = await self.__repository.find_by_id(payload["id"])
        if not user:
            raise CustomGraphQLExceptionHelper("Usuario no encontrado")
        model = UserItemModel(**user)

        return create_token(model.model_dump())

    async def recover_password(self, email: str, background_tasks):
        user = await self.__repository.find_by_email(email)
        if not user:
            return True

        token = create_token({"email": email}, expires_minutes=60)

        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        reset_url = f"{frontend_url}/reset-password/{token}"

        self.__mail_helper.send_email(
            subject="Recupera tu contraseña",
            recipients=[email],
            html=f"<a href='{reset_url}'>{reset_url}</a>",
            background_tasks=background_tasks,
        )

        return True
