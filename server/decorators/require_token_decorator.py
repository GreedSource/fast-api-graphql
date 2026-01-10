from functools import wraps
from bson import ObjectId

from server.utils.auth_utils import verify_token
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.enums.http_error_code_enum import HTTPErrorCode
from server.services.user_service import UserService


def require_token(resolver):
    @wraps(resolver)
    async def wrapper(self, parent, info, *args, **kwargs):
        request = info.context["request"]

        auth_header = request.headers.get("authorization", "")
        token = auth_header.replace("Bearer ", "").strip()

        if not token:
            raise CustomGraphQLExceptionHelper(
                "Token no proporcionado",
                HTTPErrorCode.UNAUTHORIZED,
            )

        payload = verify_token(token)
        user_id = payload.get("id")
        user_service = UserService()
        user = await user_service.get_user(user_id)

        if not user:
            raise CustomGraphQLExceptionHelper("Usuario no encontrado")

        info.context["current_user"] = user

        return await resolver(self, parent, info, *args, **kwargs)

    return wrapper
