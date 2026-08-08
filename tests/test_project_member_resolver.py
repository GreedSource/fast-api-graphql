from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from server.decorators import require_token_decorator
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.schema.project_members.resolver import ProjectMemberResolver
from tests.factories import PROJECT_ID, PROJECT_MEMBER_ID, PROJECT_ROLE_ID, USER_ID, make_current_user


def make_info():
    return SimpleNamespace(context={"request": SimpleNamespace(headers={"authorization": "Bearer token"}, cookies={})})


@pytest.mark.asyncio
async def test_project_member_resolver_add_delegates_with_manage_permission(monkeypatch):
    user_service = SimpleNamespace(get_user=AsyncMock(return_value=make_current_user(permissions=["members.manage"])))
    monkeypatch.setattr(require_token_decorator, "verify_token", lambda token: {"id": "user-1"})
    monkeypatch.setattr(require_token_decorator, "UserService", lambda: user_service)
    resolver = ProjectMemberResolver()
    resolver._ProjectMemberResolver__service = SimpleNamespace(
        add_member=AsyncMock(return_value={"id": str(PROJECT_MEMBER_ID)})
    )

    result = await resolver.resolve_add_project_member(
        None,
        make_info(),
        {"projectId": str(PROJECT_ID), "userId": str(USER_ID), "projectRoleId": str(PROJECT_ROLE_ID)},
    )

    assert result.data == {"id": str(PROJECT_MEMBER_ID)}


@pytest.mark.asyncio
async def test_project_member_resolver_rejects_missing_manage_permission(monkeypatch):
    user_service = SimpleNamespace(get_user=AsyncMock(return_value=make_current_user(permissions=["members.read"])))
    monkeypatch.setattr(require_token_decorator, "verify_token", lambda token: {"id": "user-1"})
    monkeypatch.setattr(require_token_decorator, "UserService", lambda: user_service)
    resolver = ProjectMemberResolver()

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await resolver.resolve_remove_project_member(None, make_info(), str(PROJECT_MEMBER_ID))

    assert exc_info.value.status_code == 403
