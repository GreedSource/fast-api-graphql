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
        is_active=True,
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


@pytest.mark.asyncio
async def test_impersonate_returns_target_session_with_original_actor_claim(monkeypatch):
    target_id = UUID("22222222-2222-2222-2222-222222222222")
    target = make_user()
    target.id = target_id
    repository = SimpleNamespace(find_by_id=AsyncMock(return_value=target))
    service = AuthService()
    service._AuthService__repository = repository

    monkeypatch.setattr(
        auth_service_module,
        "create_token",
        lambda payload, expires_in=15: f"access:{payload['id']}:{payload['impersonated_by']}:{expires_in}",
    )
    monkeypatch.setattr(
        auth_service_module,
        "create_refresh_token",
        lambda payload, expires_in=60 * 24 * 7: f"refresh:{payload['id']}:{payload['impersonated_by']}:{expires_in}",
    )

    result = await service.impersonate(str(USER_ID), str(target_id))

    assert result["user"]["id"] == str(target_id)
    assert result["accessToken"] == f"access:{target_id}:{USER_ID}:15"
    assert result["refreshToken"] == f"refresh:{target_id}:{USER_ID}:30"
    repository.find_by_id.assert_awaited_once_with(str(target_id))


@pytest.mark.asyncio
async def test_impersonate_rejects_inactive_target():
    repository = SimpleNamespace(find_by_id=AsyncMock(return_value=make_user()))
    repository.find_by_id.return_value.is_active = False
    service = AuthService()
    service._AuthService__repository = repository

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await service.impersonate("actor-id", "target-id")

    assert exc_info.value.message == "No puedes impersonar un usuario inactivo"


@pytest.mark.asyncio
async def test_impersonate_rejects_nested_impersonation():
    repository = SimpleNamespace(find_by_id=AsyncMock())
    service = AuthService()
    service._AuthService__repository = repository

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await service.impersonate("target-id", "another-target-id", {"impersonated_by": "actor-id"})

    assert exc_info.value.message == "No puedes iniciar una impersonación anidada"
    repository.find_by_id.assert_not_awaited()


@pytest.mark.asyncio
async def test_stop_impersonation_returns_original_actor_session(monkeypatch):
    repository = SimpleNamespace(find_by_id=AsyncMock(return_value=make_user()))
    service = AuthService()
    service._AuthService__repository = repository

    monkeypatch.setattr(auth_service_module, "create_token", lambda payload: f"access:{payload['id']}")
    monkeypatch.setattr(auth_service_module, "create_refresh_token", lambda payload: f"refresh:{payload['id']}")

    result = await service.stop_impersonation(
        current_user_id="target-id",
        auth_payload={"id": "target-id", "impersonated_by": str(USER_ID)},
    )

    assert result["user"]["id"] == str(USER_ID)
    assert result["accessToken"] == f"access:{USER_ID}"
    assert result["refreshToken"] == f"refresh:{USER_ID}"
    repository.find_by_id.assert_awaited_once_with(str(USER_ID))


@pytest.mark.asyncio
async def test_stop_impersonation_rejects_regular_session():
    service = AuthService()
    service._AuthService__repository = SimpleNamespace(find_by_id=AsyncMock())

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await service.stop_impersonation("user-id", {"id": "user-id"})

    assert exc_info.value.message == "No hay una impersonación activa"
