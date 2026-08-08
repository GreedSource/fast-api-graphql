from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from server.decorators import require_token_decorator
from server.decorators.require_token_decorator import require_token
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper


class ResolverTarget:
    @require_token
    async def protected(self, parent, info):
        return info.context["current_user"]


def make_info(headers=None, cookies=None):
    request = SimpleNamespace(headers=headers or {}, cookies=cookies or {})
    return SimpleNamespace(context={"request": request})


@pytest.mark.asyncio
async def test_require_token_accepts_authorization_header(monkeypatch):
    user = {"id": "user-1", "role": {"permissions": []}}
    user_service = SimpleNamespace(get_user=AsyncMock(return_value=user))

    monkeypatch.setattr(require_token_decorator, "verify_token", lambda token: {"id": "user-1"})
    monkeypatch.setattr(require_token_decorator, "UserService", lambda: user_service)

    info = make_info(headers={"authorization": "Bearer access-token"})
    result = await ResolverTarget().protected(None, info)

    assert result == user
    assert info.context["current_user"] == user
    assert info.context["access_token"] == "access-token"
    assert info.context["refresh_token"] is None
    user_service.get_user.assert_awaited_once_with("user-1")


@pytest.mark.asyncio
async def test_require_token_uses_cookie_fallback(monkeypatch):
    user_service = SimpleNamespace(get_user=AsyncMock(return_value={"id": "user-1"}))

    monkeypatch.setattr(require_token_decorator, "verify_token", lambda token: {"id": "user-1"})
    monkeypatch.setattr(require_token_decorator, "UserService", lambda: user_service)

    info = make_info(cookies={"access_token": "cookie-access", "refresh_token": "cookie-refresh"})
    await ResolverTarget().protected(None, info)

    assert info.context["access_token"] == "cookie-access"
    assert info.context["refresh_token"] == "cookie-refresh"


@pytest.mark.asyncio
async def test_require_token_rejects_missing_token():
    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await ResolverTarget().protected(None, make_info())

    assert exc_info.value.status_code == 401
    assert exc_info.value.message == "Token no proporcionado"


@pytest.mark.asyncio
async def test_require_token_rejects_payload_without_user_id(monkeypatch):
    monkeypatch.setattr(require_token_decorator, "verify_token", lambda token: {})

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await ResolverTarget().protected(None, make_info(headers={"authorization": "Bearer access-token"}))

    assert exc_info.value.status_code == 401
    assert exc_info.value.message == "Token inválido"
