from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from server.decorators import require_token_decorator
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.schema.projects.resolver import ProjectResolver
from server.schema.tasks.resolver import TaskResolver
from tests.factories import PROJECT_ID, TASK_ID, make_current_user, make_task


def make_info(permissions):
    return SimpleNamespace(
        context={
            "request": SimpleNamespace(headers={"authorization": "Bearer test-token"}, cookies={}),
            "test_permissions": permissions,
        }
    )


@pytest.mark.asyncio
async def test_project_resolver_create_delegates_to_service_with_permission(monkeypatch):
    user_service = SimpleNamespace(get_user=AsyncMock(return_value=make_current_user(permissions=["projects.create"])))
    monkeypatch.setattr(require_token_decorator, "verify_token", lambda token: {"id": "user-1"})
    monkeypatch.setattr(require_token_decorator, "UserService", lambda: user_service)
    resolver = ProjectResolver()
    resolver._ProjectResolver__service = SimpleNamespace(create=AsyncMock(return_value={"id": str(PROJECT_ID)}))

    result = await resolver.resolve_create_project(None, make_info(["projects.create"]), {"name": "Apollo"})

    assert result.data == {"id": str(PROJECT_ID)}
    resolver._ProjectResolver__service.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_project_resolver_rejects_missing_permission(monkeypatch):
    user_service = SimpleNamespace(get_user=AsyncMock(return_value=make_current_user(permissions=["projects.read"])))
    monkeypatch.setattr(require_token_decorator, "verify_token", lambda token: {"id": "user-1"})
    monkeypatch.setattr(require_token_decorator, "UserService", lambda: user_service)
    resolver = ProjectResolver()

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await resolver.resolve_create_project(None, make_info(["projects.read"]), {"name": "Apollo"})

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_task_resolver_complete_delegates_to_service_with_permission(monkeypatch):
    user_service = SimpleNamespace(get_user=AsyncMock(return_value=make_current_user(permissions=["tasks.complete"])))
    monkeypatch.setattr(require_token_decorator, "verify_token", lambda token: {"id": "user-1"})
    monkeypatch.setattr(require_token_decorator, "UserService", lambda: user_service)
    resolver = TaskResolver()
    resolver._TaskResolver__service = SimpleNamespace(
        get_one=AsyncMock(return_value=make_task().__dict__),
        complete=AsyncMock(return_value={"id": str(TASK_ID)}),
    )
    resolver._TaskResolver__authorization = SimpleNamespace(authorize_or_raise=AsyncMock())

    result = await resolver.resolve_complete_task(None, make_info(["tasks.complete"]), str(TASK_ID))

    assert result.data == {"id": str(TASK_ID)}
    resolver._TaskResolver__authorization.authorize_or_raise.assert_awaited_once()
    resolver._TaskResolver__service.complete.assert_awaited_once_with(str(TASK_ID))


@pytest.mark.asyncio
async def test_task_resolver_rejects_missing_permission(monkeypatch):
    user_service = SimpleNamespace(get_user=AsyncMock(return_value=make_current_user(permissions=["tasks.read"])))
    monkeypatch.setattr(require_token_decorator, "verify_token", lambda token: {"id": "user-1"})
    monkeypatch.setattr(require_token_decorator, "UserService", lambda: user_service)
    resolver = TaskResolver()

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await resolver.resolve_complete_task(None, make_info(["tasks.read"]), str(TASK_ID))

    assert exc_info.value.status_code == 403
