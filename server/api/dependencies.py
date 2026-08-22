from collections.abc import Callable

from fastapi import Depends, Request

from server.config.settings import settings
from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.services.user_service import UserService
from server.utils.auth_utils import verify_token
from server.utils.permission_utils import has_permission


async def get_current_user(request: Request) -> dict:
    authorization = request.headers.get("authorization", "")
    token = authorization.split(" ", 1)[1].strip() if authorization.lower().startswith("bearer ") else None
    token = token or request.cookies.get(settings.ACCESS_COOKIE_NAME)
    if not token:
        raise CustomGraphQLExceptionHelper("Token no proporcionado", HTTPErrorCode.UNAUTHORIZED)
    payload = verify_token(token)
    user = await UserService().get_user(payload.get("id")) if payload.get("id") else None
    if not user:
        raise CustomGraphQLExceptionHelper("Usuario no encontrado", HTTPErrorCode.UNAUTHORIZED)
    return user


def require_rest_permission(module: str, action: str) -> Callable:
    async def dependency(current_user: dict = Depends(get_current_user)) -> dict:
        permissions = current_user.get("role", {}).get("permissions", [])
        if not has_permission(permissions, module, action):
            raise CustomGraphQLExceptionHelper(
                f"Permiso denegado: se requiere {module}:{action}", HTTPErrorCode.FORBIDDEN
            )
        return current_user

    return dependency
