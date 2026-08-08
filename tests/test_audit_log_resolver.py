from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from server.decorators import require_token_decorator
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.schema.audit_logs.resolver import AuditLogResolver
from tests.factories import make_current_user


def make_info():
    return SimpleNamespace(context={"request": SimpleNamespace(headers={"authorization": "Bearer token"}, cookies={})})


@pytest.mark.asyncio
async def test_audit_log_resolver_lists_logs_with_activity_read(monkeypatch):
    user_service = SimpleNamespace(get_user=AsyncMock(return_value=make_current_user(permissions=["activity.read"])))
    monkeypatch.setattr(require_token_decorator, "verify_token", lambda token: {"id": "user-1"})
    monkeypatch.setattr(require_token_decorator, "UserService", lambda: user_service)
    resolver = AuditLogResolver()
    resolver._AuditLogResolver__service = SimpleNamespace(list_logs=AsyncMock(return_value=[{"status": "success"}]))

    result = await resolver.resolve_audit_logs(None, make_info(), limit=25)

    assert result.data == [{"status": "success"}]
    resolver._AuditLogResolver__service.list_logs.assert_awaited_once_with(limit=25)


@pytest.mark.asyncio
async def test_audit_log_resolver_rejects_missing_activity_read(monkeypatch):
    user_service = SimpleNamespace(get_user=AsyncMock(return_value=make_current_user(permissions=["tasks.read"])))
    monkeypatch.setattr(require_token_decorator, "verify_token", lambda token: {"id": "user-1"})
    monkeypatch.setattr(require_token_decorator, "UserService", lambda: user_service)
    resolver = AuditLogResolver()

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await resolver.resolve_audit_logs(None, make_info(), limit=25)

    assert exc_info.value.status_code == 403
