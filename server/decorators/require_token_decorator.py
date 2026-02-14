from functools import wraps

from server.config.settings import settings
from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.services.user_service import UserService
from server.utils.auth_utils import verify_token


def require_token(resolver):
    @wraps(resolver)
    async def wrapper(self, parent, info, *args, **kwargs):
        request = info.context["request"]

        token = None
        refresh_token = None

        # -------------------------
        # 1️⃣ Authorization header
        # -------------------------
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1].strip()

        # -------------------------
        # 2️⃣ Cookie fallback
        # -------------------------
        if not token:
            token = request.cookies.get(settings.ACCESS_COOKIE_NAME)
            refresh_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)

        # -------------------------
        # Validación
        # -------------------------
        if not token:
            raise CustomGraphQLExceptionHelper(
                "Token no proporcionado",
                HTTPErrorCode.UNAUTHORIZED,
            )

        # Verificar access token
        payload = verify_token(token)

        user_id = payload.get("id")
        if not user_id:
            raise CustomGraphQLExceptionHelper(
                "Token inválido",
                HTTPErrorCode.UNAUTHORIZED,
            )

        user_service = UserService()
        user = await user_service.get_user(user_id)

        if not user:
            raise CustomGraphQLExceptionHelper(
                "Usuario no encontrado",
                HTTPErrorCode.UNAUTHORIZED,
            )

        # -------------------------
        # Contexto
        # -------------------------
        info.context["current_user"] = user
        info.context["access_token"] = token
        info.context["refresh_token"] = refresh_token

        return await resolver(self, parent, info, *args, **kwargs)

    return wrapper
