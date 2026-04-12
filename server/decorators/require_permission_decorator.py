from enum import Enum
from functools import wraps
from typing import List, Union

from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper


class PermissionCheckMode(str, Enum):
    """Modos de verificación de permisos"""

    ANY = "any"  # Basta con tener uno de los permisos
    ALL = "all"  # Debe tener todos los permisos


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

            has_permission = any(perm.get("type") == type and perm.get("action") == action for perm in permissions)

            if not has_permission:
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

    if isinstance(mode, str):
        mode = PermissionCheckMode(mode)

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
            user_perm_set = {(p.get("type"), p.get("action")) for p in user_permissions}

            required_perm_set = {(p["type"], p["action"]) for p in permissions}

            if mode == PermissionCheckMode.ANY:
                has_permission = bool(required_perm_set & user_perm_set)
                perm_description = " o ".join([f"{p['type']}:{p['action']}" for p in permissions])
            else:  # ALL
                has_permission = required_perm_set.issubset(user_perm_set)
                perm_description = " y ".join([f"{p['type']}:{p['action']}" for p in permissions])

            if not has_permission:
                raise CustomGraphQLExceptionHelper(
                    f"Permiso denegado: se requiere {perm_description}",
                    HTTPErrorCode.FORBIDDEN,
                )

            return await resolver(self, parent, info, *args, **kwargs)

        return wrapper

    return decorator
