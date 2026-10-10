from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from server.decorators import require_token_decorator
from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.schema.auth.resolver import AuthResolver


def make_info(current_user=None, token="access-token"):
    return SimpleNamespace(
        context={
            "request": SimpleNamespace(headers={"authorization": f"Bearer {token}"}, cookies={}),
            "response": SimpleNamespace(set_cookie=Mock()),
            "current_user": current_user,
        }
    )


@pytest.mark.asyncio
async def test_impersonate_resolver_requires_permission_and_delegates(monkeypatch):
    current_user = {
        "id": "actor-id",
        "role": {"permissions": [{"type": "users", "action": "impersonate"}]},
    }
    user_service = SimpleNamespace(get_user=AsyncMock(return_value=current_user))
    monkeypatch.setattr(require_token_decorator, "verify_token", lambda token: {"id": "actor-id"})
    monkeypatch.setattr(require_token_decorator, "UserService", lambda: user_service)

    resolver = AuthResolver()
    resolver.auth_service = SimpleNamespace(
        impersonate=AsyncMock(
            return_value={
                "user": {"id": "target-id"},
                "accessToken": "target-access",
                "refreshToken": "target-refresh",
            }
        )
    )

    result = await resolver.resolve_impersonate_user(None, make_info(), "target-id")

    assert result.data["accessToken"] == "target-access"
    resolver.auth_service.impersonate.assert_awaited_once_with(
        actor_id="actor-id",
        target_id="target-id",
        auth_payload={"id": "actor-id"},
    )


@pytest.mark.asyncio
async def test_impersonate_resolver_rejects_user_without_impersonate_permission(monkeypatch):
    current_user = {
        "id": "actor-id",
        "role": {"permissions": [{"type": "users", "action": "read"}]},
    }
    user_service = SimpleNamespace(get_user=AsyncMock(return_value=current_user))
    monkeypatch.setattr(require_token_decorator, "verify_token", lambda token: {"id": "actor-id"})
    monkeypatch.setattr(require_token_decorator, "UserService", lambda: user_service)

    resolver = AuthResolver()
    resolver.auth_service = SimpleNamespace(impersonate=AsyncMock())

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await resolver.resolve_impersonate_user(None, make_info(), "target-id")

    assert exc_info.value.status_code == HTTPErrorCode.FORBIDDEN.status_code
    resolver.auth_service.impersonate.assert_not_awaited()
