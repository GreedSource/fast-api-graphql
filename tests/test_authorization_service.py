from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.services.authorization_service import AuthorizationService
from tests.factories import PROJECT_ID, USER_ID, make_current_user, make_task


def make_permission(permission_key):
    module_key, action_key = permission_key.split(".", 1)
    return SimpleNamespace(
        module=SimpleNamespace(key=module_key),
        action=SimpleNamespace(key=action_key),
    )


def make_member(permission_keys):
    return SimpleNamespace(
        project_role=SimpleNamespace(
            permissions=[make_permission(permission_key) for permission_key in permission_keys]
        )
    )


@pytest.mark.asyncio
async def test_authorize_rejects_unauthenticated_user():
    result = await AuthorizationService().authorize(None, "projects", "read")

    assert result.allowed is False
    assert result.reason == "unauthenticated"
    assert result.status_code == HTTPErrorCode.UNAUTHORIZED


@pytest.mark.asyncio
async def test_authorize_allows_non_resource_action_by_global_permission():
    user = make_current_user(permissions=["projects.create"])

    result = await AuthorizationService().authorize(user, "projects", "create")

    assert result.allowed is True
    assert result.reason == "allowed_by_global_permission"


@pytest.mark.asyncio
async def test_authorize_allows_admin_scope_for_project_resource_without_membership():
    service = AuthorizationService()
    service._AuthorizationService__project_member_repository = SimpleNamespace(find_by_project_and_user=AsyncMock())
    user = make_current_user(permissions=["projects.delete", "roles.read"])

    result = await service.authorize(user, "projects", "delete", resource={"id": str(PROJECT_ID)})

    assert result.allowed is True
    assert result.reason == "allowed_by_admin_scope"
    service._AuthorizationService__project_member_repository.find_by_project_and_user.assert_not_called()


@pytest.mark.asyncio
async def test_authorize_rejects_user_without_project_membership():
    service = AuthorizationService()
    service._AuthorizationService__project_member_repository = SimpleNamespace(
        find_by_project_and_user=AsyncMock(return_value=None)
    )
    user = make_current_user(permissions=["tasks.update"])

    result = await service.authorize(user, "tasks", "update", resource=make_task())

    assert result.allowed is False
    assert result.reason == "missing_project_membership"


@pytest.mark.asyncio
async def test_authorize_allows_project_manager_to_update_any_project_task():
    service = AuthorizationService()
    service._AuthorizationService__project_member_repository = SimpleNamespace(
        find_by_project_and_user=AsyncMock(return_value=make_member(["tasks.update", "tasks.assign"]))
    )
    user = make_current_user(permissions=["tasks.update"], id=str(USER_ID))
    task = make_task(assignee_id="another-user")

    result = await service.authorize(user, "tasks", "update", resource=task)

    assert result.allowed is True
    assert result.reason == "allowed_by_task_policy"


@pytest.mark.asyncio
async def test_authorize_allows_developer_to_update_own_task():
    service = AuthorizationService()
    service._AuthorizationService__project_member_repository = SimpleNamespace(
        find_by_project_and_user=AsyncMock(return_value=make_member(["tasks.update"]))
    )
    user = make_current_user(permissions=["tasks.update"], id=str(USER_ID))

    result = await service.authorize(user, "tasks", "update", resource=make_task(assignee_id=USER_ID))

    assert result.allowed is True
    assert result.reason == "allowed_by_task_policy"


@pytest.mark.asyncio
async def test_authorize_rejects_developer_updating_another_users_task():
    service = AuthorizationService()
    service._AuthorizationService__project_member_repository = SimpleNamespace(
        find_by_project_and_user=AsyncMock(return_value=make_member(["tasks.update"]))
    )
    user = make_current_user(permissions=["tasks.update"], id=str(USER_ID))

    result = await service.authorize(user, "tasks", "update", resource=make_task(assignee_id="another-user"))

    assert result.allowed is False
    assert result.reason == "task_ownership_required"


@pytest.mark.asyncio
async def test_authorize_rejects_client_modifying_task():
    service = AuthorizationService()
    service._AuthorizationService__project_member_repository = SimpleNamespace(
        find_by_project_and_user=AsyncMock(return_value=make_member(["tasks.read"]))
    )
    user = make_current_user(permissions=["tasks.update"], id=str(USER_ID))

    result = await service.authorize(user, "tasks", "update", resource=make_task(assignee_id=USER_ID))

    assert result.allowed is False
    assert result.reason == "missing_project_role_permission"


@pytest.mark.asyncio
async def test_authorize_or_raise_uses_403_for_denied_authenticated_user():
    service = AuthorizationService()
    service._AuthorizationService__project_member_repository = SimpleNamespace(
        find_by_project_and_user=AsyncMock(return_value=None)
    )

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await service.authorize_or_raise(
            make_current_user(permissions=["tasks.update"]), "tasks", "update", make_task()
        )

    assert exc_info.value.status_code == 403
