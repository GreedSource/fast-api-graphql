from functools import wraps
from typing import List, Union

from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.strategies.permission_check_strategy import PermissionCheckMode, PermissionCheckStrategyFactory
from server.utils.permission_utils import has_permission


def require_permission(type: str, action: str):
    """
    Decorator que verifica que el usuario tenga un permiso específico {type, action}.

    Requiere que @require_token se ejecute primero para inyectar current_user en el contexto.

    Ejemplo:
        @require_token
        @require_permission(type="users", action="create")
        async def resolve_create_role(self, parent, info, input):
            ...
    """

    def decorator(resolver):
        @wraps(resolver)
        async def wrapper(self, parent, info, *args, **kwargs):
            current_user = info.context.get("current_user")

            if not current_user:
                raise CustomGraphQLExceptionHelper(
                    "Usuario no autenticado",
                    HTTPErrorCode.UNAUTHORIZED,
                )
            role = current_user.get("role")
            if not role:
                raise CustomGraphQLExceptionHelper(
                    "El usuario no tiene un rol asignado",
                    HTTPErrorCode.FORBIDDEN,
                )

            permissions = role.get("permissions", [])

            if not has_permission(permissions, type, action):
                raise CustomGraphQLExceptionHelper(
                    f"Permiso denegado: se requiere {type}:{action}",
                    HTTPErrorCode.FORBIDDEN,
                )

            return await resolver(self, parent, info, *args, **kwargs)

        return wrapper

    return decorator


def require_permissions(
    permissions: List[dict],
    mode: Union[PermissionCheckMode, str] = PermissionCheckMode.ANY,
):
    """
    Decorator que verifica múltiples permisos.

    Args:
        permissions: Lista de dicts con {type, action}
        mode: PermissionCheckMode.ANY (basta uno) o PermissionCheckMode.ALL (todos)

    Ejemplo:
        @require_token
        @require_permissions(
            permissions=[
                {"type": "users", "action": "create"},
                {"type": "users", "action": "update"},
            ],
            mode=PermissionCheckMode.ALL
        )
        async def resolve_manage_users(self, parent, info, input):
            ...
    """

    strategy = PermissionCheckStrategyFactory.create(mode)
    normalized_mode = PermissionCheckMode(mode)

    def decorator(resolver):
        @wraps(resolver)
        async def wrapper(self, parent, info, *args, **kwargs):
            current_user = info.context.get("current_user")

            if not current_user:
                raise CustomGraphQLExceptionHelper(
                    "Usuario no autenticado",
                    HTTPErrorCode.UNAUTHORIZED,
                )

            role = current_user.get("role")
            if not role:
                raise CustomGraphQLExceptionHelper(
                    "El usuario no tiene un rol asignado",
                    HTTPErrorCode.FORBIDDEN,
                )

            user_permissions = role.get("permissions", [])
            is_allowed = strategy.is_allowed(user_permissions, permissions)

            if normalized_mode == PermissionCheckMode.ANY:
                perm_description = " o ".join([f"{p['type']}:{p['action']}" for p in permissions])
            else:
                perm_description = " y ".join([f"{p['type']}:{p['action']}" for p in permissions])

            if not is_allowed:
                raise CustomGraphQLExceptionHelper(
                    f"Permiso denegado: se requiere {perm_description}",
                    HTTPErrorCode.FORBIDDEN,
                )

            return await resolver(self, parent, info, *args, **kwargs)

        return wrapper

    return decorator
