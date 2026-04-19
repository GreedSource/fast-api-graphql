from enum import Enum
from functools import wraps
from typing import Awaitable, Callable, Dict, List, ParamSpec, TypeVar, Union

from graphql import GraphQLResolveInfo

from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper

P = ParamSpec("P")
T = TypeVar("T")


class PermissionCheckMode(str, Enum):
    ANY = "any"
    ALL = "all"


def require_permission(
    type: str,
    action: str,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    def decorator(resolver: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(resolver)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            info = args[2]
            assert isinstance(info, GraphQLResolveInfo)

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

            return await resolver(*args, **kwargs)

        return wrapper

    return decorator


def require_permissions(
    permissions: List[Dict[str, str]],
    mode: Union[PermissionCheckMode, str] = PermissionCheckMode.ANY,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    if isinstance(mode, str):
        mode = PermissionCheckMode(mode)

    def decorator(resolver: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(resolver)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            info = args[2]
            assert isinstance(info, GraphQLResolveInfo)

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
                perm_description = " o ".join(f"{p['type']}:{p['action']}" for p in permissions)
            else:
                has_permission = required_perm_set.issubset(user_perm_set)
                perm_description = " y ".join(f"{p['type']}:{p['action']}" for p in permissions)

            if not has_permission:
                raise CustomGraphQLExceptionHelper(
                    f"Permiso denegado: se requiere {perm_description}",
                    HTTPErrorCode.FORBIDDEN,
                )

            return await resolver(*args, **kwargs)

        return wrapper

    return decorator
