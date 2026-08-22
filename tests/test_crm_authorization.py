from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from server.enums.http_error_code_enum import HTTPErrorCode
from server.services.authorization_service import AuthorizationService
from tests.factories import USER_ID, make_current_user

ORGANIZATION_ID = "10000000-0000-0000-0000-000000000001"
TEAM_ID = "20000000-0000-0000-0000-000000000001"


def crm_resource(owner_id=USER_ID, team_id=TEAM_ID):
    return {
        "id": "30000000-0000-0000-0000-000000000001",
        "organizationId": ORGANIZATION_ID,
        "teamId": str(team_id),
        "ownerId": str(owner_id),
    }


def service_with_access(access):
    service = AuthorizationService()
    service._AuthorizationService__crm_team_repository = SimpleNamespace(
        find_user_access=AsyncMock(return_value=access)
    )
    service._AuthorizationService__audit_log_service = SimpleNamespace(record=AsyncMock())
    return service


@pytest.mark.asyncio
async def test_crm_own_scope_allows_owner():
    service = service_with_access({"scope": "OWN", "team_id": TEAM_ID, "user_id": str(USER_ID)})
    user = make_current_user(id=str(USER_ID), permissions=["leads.update"])

    result = await service.authorize(user, "leads", "update", crm_resource())

    assert result.allowed is True
    assert result.reason == "allowed_by_own_scope"


@pytest.mark.asyncio
async def test_crm_own_scope_rejects_another_owner():
    service = service_with_access({"scope": "OWN", "team_id": TEAM_ID, "user_id": str(USER_ID)})
    user = make_current_user(id=str(USER_ID), permissions=["leads.update"])

    result = await service.authorize(user, "leads", "update", crm_resource(owner_id="other-user"))

    assert result.allowed is False
    assert result.reason == "resource_outside_scope"
    assert result.status_code == HTTPErrorCode.FORBIDDEN


@pytest.mark.asyncio
async def test_crm_team_scope_allows_same_team():
    service = service_with_access({"scope": "TEAM", "team_id": TEAM_ID, "user_id": str(USER_ID)})
    user = make_current_user(id=str(USER_ID), permissions=["leads.update"])

    result = await service.authorize(user, "leads", "update", crm_resource(owner_id="other-user"))

    assert result.allowed is True
    assert result.reason == "allowed_by_team_scope"


@pytest.mark.asyncio
async def test_crm_scope_still_requires_rbac_permission():
    service = service_with_access({"scope": "ORGANIZATION", "team_id": TEAM_ID, "user_id": str(USER_ID)})
    user = make_current_user(id=str(USER_ID), permissions=["leads.read"])

    result = await service.authorize(user, "leads", "update", crm_resource())

    assert result.allowed is False
    assert result.reason == "missing_global_permission"
