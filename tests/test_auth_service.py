from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.services import auth_service as auth_service_module
from server.services.auth_service import AuthService

USER_ID = UUID("11111111-1111-1111-1111-111111111111")


def make_user(password="hashed-password"):
    return SimpleNamespace(
        id=USER_ID,
        name="Ada",
        lastname="Lovelace",
        email="ada@example.com",
        password=password,
        role=None,
    )


@pytest.mark.asyncio
async def test_login_returns_user_and_tokens(monkeypatch):
    repository = SimpleNamespace(find_by_email=AsyncMock(return_value=make_user()))
    service = AuthService()
    service._AuthService__repository = repository

    monkeypatch.setattr(auth_service_module, "verify_password", lambda plain, hashed: plain == "secret" and hashed)
    monkeypatch.setattr(auth_service_module, "create_token", lambda payload: f"access:{payload['id']}")
    monkeypatch.setattr(auth_service_module, "create_refresh_token", lambda payload: f"refresh:{payload['id']}")

    result = await service.login("ada@example.com", "secret")

    assert result["user"]["id"] == str(USER_ID)
    assert result["user"]["email"] == "ada@example.com"
    assert result["accessToken"] == f"access:{USER_ID}"
    assert result["refreshToken"] == f"refresh:{USER_ID}"
    repository.find_by_email.assert_awaited_once_with("ada@example.com")


@pytest.mark.asyncio
async def test_login_rejects_invalid_credentials(monkeypatch):
    repository = SimpleNamespace(find_by_email=AsyncMock(return_value=make_user()))
    service = AuthService()
    service._AuthService__repository = repository

    monkeypatch.setattr(auth_service_module, "verify_password", lambda plain, hashed: False)

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await service.login("ada@example.com", "wrong")

    assert exc_info.value.message == "Credenciales inválidas"


@pytest.mark.asyncio
async def test_refresh_token_rejects_missing_user(monkeypatch):
    repository = SimpleNamespace(find_by_id=AsyncMock(return_value=None))
    service = AuthService()
    service._AuthService__repository = repository

    monkeypatch.setattr(auth_service_module, "verify_refresh_token", lambda token: {"id": str(USER_ID)})

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await service.refresh_token("refresh-token")

    assert exc_info.value.message == "Usuario no encontrado"
    repository.find_by_id.assert_awaited_once_with(str(USER_ID))
