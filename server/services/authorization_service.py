from dataclasses import dataclass
from typing import Any

from server.decorators.singleton_decorator import singleton
from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.repositories.crm_team_repository import CRMTeamRepository
from server.repositories.project_member_repository import ProjectMemberRepository
from server.services.audit_log_service import AuditLogService
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
        self.__crm_team_repository = CRMTeamRepository()
        self.__audit_log_service = AuditLogService()

    async def authorize(
        self,
        user: dict | None,
        module: str,
        action: str,
        resource: Any = None,
        context: dict | None = None,
    ) -> AuthorizationResult:
        result = await self._evaluate(user, module, action, resource=resource, context=context)
        await self._record_authorization(user, module, action, result, resource=resource, context=context)
        return result

    async def _evaluate(
        self,
        user: dict | None,
        module: str,
        action: str,
        resource: Any = None,
        context: dict | None = None,
    ) -> AuthorizationResult:
        if not user:
            return AuthorizationResult(False, "unauthenticated", HTTPErrorCode.UNAUTHORIZED)

        organization_id = self._resource_value(resource, "organizationId", "organization_id")
        if context and context.get("organization_id"):
            organization_id = context["organization_id"]
        if organization_id:
            return await self._evaluate_context_scope(user, module, action, resource, organization_id)

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

    async def _evaluate_context_scope(self, user, module, action, resource, organization_id):
        if not self._has_global_permission(user, module, action):
            return AuthorizationResult(False, "missing_global_permission", HTTPErrorCode.FORBIDDEN)
        if self._has_admin_scope(user, module, action):
            return AuthorizationResult(True, "allowed_by_admin_scope")
        team_id = self._resource_value(resource, "teamId", "team_id")
        access = await self.__crm_team_repository.find_user_access(organization_id, user.get("id"), team_id)
        if not access:
            return AuthorizationResult(False, "missing_context_membership", HTTPErrorCode.FORBIDDEN)
        scope = access["scope"]
        if scope in {"GLOBAL", "ORGANIZATION"}:
            return AuthorizationResult(True, f"allowed_by_{scope.lower()}_scope")
        owner_id = self._resource_value(resource, "ownerId", "owner_id")
        if scope == "TEAM" and team_id and str(team_id) == str(access["team_id"]):
            return AuthorizationResult(True, "allowed_by_team_scope")
        if scope == "OWN" and (owner_id is None or str(owner_id) == str(user.get("id"))):
            return AuthorizationResult(True, "allowed_by_own_scope")
        return AuthorizationResult(False, "resource_outside_scope", HTTPErrorCode.FORBIDDEN)

    async def resolve_access(self, user: dict, organization_id) -> dict:
        if self._has_admin_scope(user, "roles", "read"):
            return {"scope": "GLOBAL", "user_id": user.get("id"), "team_id": None}
        access = await self.__crm_team_repository.find_user_access(organization_id, user.get("id"))
        if not access:
            raise CustomGraphQLExceptionHelper("Permiso denegado", HTTPErrorCode.FORBIDDEN)
        return access

    def _resource_value(self, resource, *keys):
        if resource is None:
            return None
        if isinstance(resource, dict):
            return next((resource.get(key) for key in keys if resource.get(key) is not None), None)
        return next((getattr(resource, key, None) for key in keys if getattr(resource, key, None) is not None), None)

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

    async def _record_authorization(
        self,
        user: dict | None,
        module: str,
        action: str,
        result: AuthorizationResult,
        resource: Any = None,
        context: dict | None = None,
    ) -> None:
        await self.__audit_log_service.record(
            user_id=user.get("id") if user else None,
            module=module,
            action=action,
            resource_type=self._resolve_resource_type(module, resource),
            resource_id=self._resolve_resource_id(resource, context),
            status="success" if result.allowed else "denied",
            metadata={"reason": result.reason},
            strict=False,
        )

    def _resolve_resource_type(self, module: str, resource: Any = None) -> str | None:
        if resource is None:
            return None
        if module.endswith("s"):
            return module[:-1]
        return module

    def _resolve_resource_id(self, resource: Any = None, context: dict | None = None) -> str | None:
        if resource is None:
            return str(context["project_id"]) if context and context.get("project_id") else None
        if isinstance(resource, dict):
            resource_id = resource.get("id") or resource.get("resourceId") or resource.get("resource_id")
        else:
            resource_id = getattr(resource, "id", None)
        return str(resource_id) if resource_id else None
