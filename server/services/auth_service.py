from server.config.settings import settings
from server.decorators.singleton_decorator import singleton
from server.helpers.custom_graphql_exception_helper import (
    CustomGraphQLExceptionHelper,
)
from server.helpers.logger_helper import LoggerHelper
from server.helpers.mail_helper import MailHelper
from server.helpers.template_helper import TemplateHelper
from server.models.dto.user_dto import UserItemModel
from server.repositories.user_repository import UserRepository
from server.utils.auth_utils import (
    create_refresh_token,
    create_token,
    verify_password,
    verify_refresh_token,
    verify_token,
)


@singleton
class AuthService:
    def __init__(self):
        self.__repository = UserRepository()
        self.__mail_helper = MailHelper()
        self.__template_helper = TemplateHelper()
        LoggerHelper.info("AuthService initialized")

    async def register(self, user_data: dict):
        user_orm = await self.__repository.create(user_data)
        user_dto = UserItemModel.model_validate(user_orm).model_dump(mode="json")
        access_token = create_token(user_dto)
        refresh_token = create_refresh_token(user_dto)
        return {
            "user": user_dto,
            "accessToken": access_token,
            "refreshToken": refresh_token,
        }

    async def login(self, email: str, password: str):
        user_orm = await self.__repository.find_by_email(email)

        if not user_orm or not verify_password(password, user_orm.password):
            raise CustomGraphQLExceptionHelper("Credenciales inválidas")

        user_dto = UserItemModel.model_validate(user_orm).model_dump(mode="json")
        access_token = create_token(user_dto)
        refresh_token = create_refresh_token(user_dto)
        return {
            "user": user_dto,
            "accessToken": access_token,
            "refreshToken": refresh_token,
        }

    async def refresh_token(self, refresh_token: str):
        payload = verify_refresh_token(refresh_token)

        user_orm = await self.__repository.find_by_id(payload.get("id"))
        if not user_orm:
            raise CustomGraphQLExceptionHelper("Usuario no encontrado")
        user_dto = UserItemModel.model_validate(user_orm).model_dump(mode="json")
        access_token = create_token(user_dto)

        return {
            "user": user_dto,
            "accessToken": access_token,
            "refreshToken": refresh_token,
        }

    async def logout(self):
        return True

    async def recover_password(self, email: str, background_tasks):
        user_orm = await self.__repository.find_by_email(email)
        if not user_orm:
            LoggerHelper.warning(f"Password recovery attempted for non-existent email: {email}")
            return True

        token = create_token({"email": email}, expires_in=60)

        frontend_url = settings.FRONTEND_URL
        reset_url = f"{frontend_url}/reset-password/{token}"

        html = self.__template_helper.render(
            "emails/reset_password.html",
            {
                "reset_url": reset_url,
                "user": user_orm,
            },
        )

        self.__mail_helper.send_email(
            subject="Recupera tu contraseña",
            recipients=[email],
            html=html,
            background_tasks=background_tasks,
        )

        return True

    async def reset_password(self, token: str, new_password: str):
        try:
            payload = verify_token(token)
            email = payload.get("email")

            if not email:
                raise CustomGraphQLExceptionHelper("Token inválido")

            user_orm = await self.__repository.find_by_email(email)
            if not user_orm:
                raise CustomGraphQLExceptionHelper("Usuario no encontrado")

            await self.__repository.update(
                str(user_orm.id),
                {"password": new_password},
            )

            LoggerHelper.info(f"Password reset successfully for user: {email}")
            return True

        except CustomGraphQLExceptionHelper:
            raise
        except Exception as e:
            LoggerHelper.error(f"Error resetting password: {str(e)}")
            raise CustomGraphQLExceptionHelper("Error al restablecer la contraseña")
