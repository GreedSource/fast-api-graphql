from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from server.decorators import require_token_decorator
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.schema.companies.resolver import CompanyResolver
from tests.factories import make_current_user

ORG_ID = "10000000-0000-0000-0000-000000000001"
USER_ID = "40000000-0000-0000-0000-000000000001"


def info(permissions):
    return SimpleNamespace(
        context={
            "request": SimpleNamespace(headers={"authorization": "Bearer test-token"}, cookies={}),
            "test_permissions": permissions,
        }
    )


@pytest.mark.asyncio
async def test_company_resolver_create_delegates_with_context_authorization(monkeypatch):
    user = make_current_user(id=USER_ID, permissions=["companies.create"])
    monkeypatch.setattr(require_token_decorator, "verify_token", lambda token: {"id": user["id"]})
    monkeypatch.setattr(
        require_token_decorator, "UserService", lambda: SimpleNamespace(get_user=AsyncMock(return_value=user))
    )
    resolver = CompanyResolver()
    resolver.service = SimpleNamespace(create=AsyncMock(return_value={"id": "company-1"}))
    resolver.authorization = SimpleNamespace(
        resolve_access=AsyncMock(return_value={"scope": "OWN", "team_id": None}),
        authorize_or_raise=AsyncMock(),
    )

    create_company = resolver.mutation._resolvers["createCompany"]
    result = await create_company(None, info(["companies.create"]), {"organizationId": ORG_ID, "name": "Acme"})

    assert result.data == {"id": "company-1"}
    resolver.authorization.authorize_or_raise.assert_awaited_once()
    resolver.service.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_company_resolver_rejects_missing_permission(monkeypatch):
    user = make_current_user(id=USER_ID, permissions=["companies.read"])
    monkeypatch.setattr(require_token_decorator, "verify_token", lambda token: {"id": user["id"]})
    monkeypatch.setattr(
        require_token_decorator, "UserService", lambda: SimpleNamespace(get_user=AsyncMock(return_value=user))
    )
    resolver = CompanyResolver()

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await resolver.mutation._resolvers["createCompany"](
            None, info(["companies.read"]), {"organizationId": ORG_ID, "name": "Acme"}
        )

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_company_resolver_rejects_missing_token():
    resolver = CompanyResolver()
    request_info = SimpleNamespace(context={"request": SimpleNamespace(headers={}, cookies={})})

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await resolver.mutation._resolvers["createCompany"](
            None, request_info, {"organizationId": ORG_ID, "name": "Acme"}
        )

    assert exc_info.value.status_code == 401
