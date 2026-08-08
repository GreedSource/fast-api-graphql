from dataclasses import dataclass
from typing import Any

from server.decorators.singleton_decorator import singleton
from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.repositories.project_member_repository import ProjectMemberRepository
from server.utils.permission_utils import has_permission


@dataclass(frozen=True)
class AuthorizationResult:
    allowed: bool
    reason: str
    status_code: HTTPErrorCode | None = None


@singleton
class AuthorizationService:
    def __init__(self):
        self.__project_member_repository = ProjectMemberRepository()

    async def authorize(
        self,
        user: dict | None,
        module: str,
        action: str,
        resource: Any = None,
        context: dict | None = None,
    ) -> AuthorizationResult:
        if not user:
            return AuthorizationResult(False, "unauthenticated", HTTPErrorCode.UNAUTHORIZED)

        project_id = self._resolve_project_id(resource, context)
        if not project_id:
            if self._has_global_permission(user, module, action):
                return AuthorizationResult(True, "allowed_by_global_permission")
            return AuthorizationResult(False, "missing_global_permission", HTTPErrorCode.FORBIDDEN)

        if self._has_admin_scope(user, module, action):
            return AuthorizationResult(True, "allowed_by_admin_scope")

        member = await self.__project_member_repository.find_by_project_and_user(project_id, user.get("id"))
        if not member:
            return AuthorizationResult(False, "missing_project_membership", HTTPErrorCode.FORBIDDEN)

        project_permissions = self._project_role_permissions(member)
        if not has_permission(project_permissions, module, action):
            return AuthorizationResult(False, "missing_project_role_permission", HTTPErrorCode.FORBIDDEN)

        if module == "tasks" and action in {"update", "complete"}:
            if self._is_task_owner(user, resource) or has_permission(project_permissions, "tasks", "assign"):
                return AuthorizationResult(True, "allowed_by_task_policy")
            return AuthorizationResult(False, "task_ownership_required", HTTPErrorCode.FORBIDDEN)

        return AuthorizationResult(True, "allowed_by_project_role")

    async def authorize_or_raise(
        self,
        user: dict | None,
        module: str,
        action: str,
        resource: Any = None,
        context: dict | None = None,
    ) -> AuthorizationResult:
        result = await self.authorize(user, module, action, resource=resource, context=context)
        if not result.allowed:
            raise CustomGraphQLExceptionHelper("Permiso denegado", result.status_code or HTTPErrorCode.FORBIDDEN)
        return result

    def _has_global_permission(self, user: dict, module: str, action: str) -> bool:
        permissions = user.get("role", {}).get("permissions", [])
        return has_permission(permissions, module, action)

    def _has_admin_scope(self, user: dict, module: str, action: str) -> bool:
        permissions = user.get("role", {}).get("permissions", [])
        return has_permission(permissions, module, action) and has_permission(permissions, "roles", "read")

    def _project_role_permissions(self, member) -> list[dict[str, str]]:
        role = getattr(member, "project_role", None)
        permissions = getattr(role, "permissions", []) if role else []
        result = []
        for permission in permissions:
            module = getattr(permission, "module", None)
            permission_action = getattr(permission, "action", None)
            if module and permission_action:
                result.append({"type": module.key, "action": permission_action.key})
        return result

    def _resolve_project_id(self, resource: Any = None, context: dict | None = None):
        if context and context.get("project_id"):
            return context["project_id"]
        if resource is None:
            return None
        if isinstance(resource, dict):
            return resource.get("projectId") or resource.get("project_id") or resource.get("id")
        return (
            getattr(resource, "project_id", None)
            or getattr(resource, "projectId", None)
            or getattr(resource, "id", None)
        )

    def _is_task_owner(self, user: dict, resource: Any) -> bool:
        if resource is None:
            return False
        assignee_id = (
            resource.get("assigneeId") if isinstance(resource, dict) else getattr(resource, "assignee_id", None)
        )
        return str(assignee_id) == str(user.get("id"))
