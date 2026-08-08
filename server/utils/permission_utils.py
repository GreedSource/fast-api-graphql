from collections.abc import Iterable
from typing import Any

PermissionInput = dict[str, Any] | str


def normalize_permission(permission: PermissionInput) -> dict[str, str] | None:
    if isinstance(permission, str):
        if "." not in permission:
            return None
        permission_type, action = permission.split(".", 1)
    else:
        permission_type = permission.get("type")
        action = permission.get("action")

    if not permission_type or not action:
        return None

    return {
        "type": str(permission_type).strip().lower(),
        "action": str(action).strip().lower(),
    }


def permission_to_key(permission: PermissionInput) -> str | None:
    normalized = normalize_permission(permission)
    if not normalized:
        return None
    return f"{normalized['type']}.{normalized['action']}"


def permissions_to_keys(permissions: Iterable[PermissionInput]) -> list[str]:
    keys = []
    for permission in permissions:
        key = permission_to_key(permission)
        if key:
            keys.append(key)
    return keys


def permission_set(permissions: Iterable[PermissionInput]) -> set[tuple[str, str]]:
    normalized_permissions = [normalize_permission(permission) for permission in permissions]
    return {
        (permission["type"], permission["action"]) for permission in normalized_permissions if permission is not None
    }


def has_permission(permissions: Iterable[PermissionInput], permission_type: str, action: str) -> bool:
    required_permission = normalize_permission({"type": permission_type, "action": action})
    if not required_permission:
        return False
    return (required_permission["type"], required_permission["action"]) in permission_set(permissions)
