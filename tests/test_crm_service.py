from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.models.dto.company_dto import CreateCompanyModel
from server.models.dto.lead_dto import ConvertLeadModel
from server.services.company_service import CompanyService
from server.services.lead_service import LeadService

ORG_ID = UUID("10000000-0000-0000-0000-000000000001")
LEAD_ID = UUID("30000000-0000-0000-0000-000000000001")


def resource(**values):
    now = datetime.now(timezone.utc)
    defaults = {
        "id": LEAD_ID,
        "organization_id": ORG_ID,
        "name": "Acme",
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(values)
    return SimpleNamespace(**defaults)


@pytest.mark.asyncio
async def test_create_company_delegates_and_serializes():
    service = CompanyService()
    repository = SimpleNamespace(create=AsyncMock(return_value=resource()))
    service.repository = repository
    payload = CreateCompanyModel(organizationId=ORG_ID, name="Acme")

    result = await service.create(payload)

    assert result["name"] == "Acme"
    repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_convert_lead_rejects_already_converted():
    service = LeadService()
    service.repository = SimpleNamespace(
        find_by_id=AsyncMock(return_value=resource(converted_at=datetime.now(timezone.utc)))
    )
    payload = ConvertLeadModel(id=LEAD_ID, opportunityName="Acme renewal")

    with pytest.raises(CustomGraphQLExceptionHelper):
        await service.convert(payload)
