from abc import ABC, abstractmethod
from enum import Enum

from server.utils.permission_utils import permission_set


class PermissionCheckMode(str, Enum):
    ANY = "any"
    ALL = "all"


class PermissionCheckStrategy(ABC):
    """Contrato para políticas de evaluación de múltiples permisos."""

    @abstractmethod
    def is_allowed(self, user_permissions: list[dict], required_permissions: list[dict]) -> bool:
        raise NotImplementedError


class AnyPermissionStrategy(PermissionCheckStrategy):
    def is_allowed(self, user_permissions: list[dict], required_permissions: list[dict]) -> bool:
        return bool(permission_set(user_permissions) & permission_set(required_permissions))


class AllPermissionsStrategy(PermissionCheckStrategy):
    def is_allowed(self, user_permissions: list[dict], required_permissions: list[dict]) -> bool:
        return permission_set(required_permissions).issubset(permission_set(user_permissions))


class PermissionCheckStrategyFactory:
    """Factory que centraliza la selección de la estrategia de permisos."""

    _strategies = {
        PermissionCheckMode.ANY: AnyPermissionStrategy,
        PermissionCheckMode.ALL: AllPermissionsStrategy,
    }

    @classmethod
    def create(cls, mode: PermissionCheckMode | str) -> PermissionCheckStrategy:
        try:
            normalized_mode = PermissionCheckMode(mode)
        except ValueError as exc:
            raise ValueError(f"Modo de verificación de permisos no soportado: {mode}") from exc
        return cls._strategies[normalized_mode]()
