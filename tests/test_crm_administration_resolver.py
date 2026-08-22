from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from server.decorators import require_token_decorator
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.schema.crm_administration.resolver import CRMAdministrationResolver
from tests.factories import make_current_user


def info():
    return SimpleNamespace(
        context={
            "request": SimpleNamespace(headers={"authorization": "Bearer test-token"}, cookies={}),
        }
    )


@pytest.mark.asyncio
async def test_crm_organizations_query_delegates_to_service(monkeypatch):
    user = make_current_user(permissions=["dashboard.read"])
    monkeypatch.setattr(require_token_decorator, "verify_token", lambda token: {"id": user["id"]})
    monkeypatch.setattr(
        require_token_decorator,
        "UserService",
        lambda: SimpleNamespace(get_user=AsyncMock(return_value=user)),
    )
    resolver = CRMAdministrationResolver()
    resolver.organizations = SimpleNamespace(
        get_all=AsyncMock(return_value=[{"id": "organization-1", "name": "Acme", "slug": "acme"}])
    )

    result = await resolver.query._resolvers["crmOrganizations"](None, info())

    assert result.data[0]["slug"] == "acme"
    resolver.organizations.get_all.assert_awaited_once()


@pytest.mark.asyncio
async def test_crm_organizations_query_rejects_missing_permission(monkeypatch):
    user = make_current_user(permissions=["companies.read"])
    monkeypatch.setattr(require_token_decorator, "verify_token", lambda token: {"id": user["id"]})
    monkeypatch.setattr(
        require_token_decorator,
        "UserService",
        lambda: SimpleNamespace(get_user=AsyncMock(return_value=user)),
    )
    resolver = CRMAdministrationResolver()

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await resolver.query._resolvers["crmOrganizations"](None, info())

    assert exc_info.value.status_code == 403
