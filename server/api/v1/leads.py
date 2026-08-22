from datetime import datetime
from decimal import Decimal

from fastapi import Depends
from pydantic import BaseModel, Field

from server.api.crud_router import build_scoped_crud_router
from server.api.dependencies import require_rest_permission
from server.api.responses import api_response
from server.models.dto.lead_dto import ConvertLeadModel, CreateLeadModel, UpdateLeadModel
from server.services.authorization_service import AuthorizationService
from server.services.lead_service import LeadService

service = LeadService()
authorization = AuthorizationService()
router = build_scoped_crud_router("leads", service, CreateLeadModel, UpdateLeadModel)


class ConvertLeadBody(BaseModel):
    opportunity_name: str = Field(alias="opportunityName", min_length=1, max_length=160)
    value: Decimal = Field(default=0, ge=0)
    probability: int = Field(default=0, ge=0, le=100)
    expected_close_date: datetime | None = Field(default=None, alias="expectedCloseDate")
    model_config = {"populate_by_name": True}


@router.post("/{lead_id}/convert")
async def convert_lead(
    lead_id: str,
    payload: ConvertLeadBody,
    user: dict = Depends(require_rest_permission("leads", "convert")),
):
    model = ConvertLeadModel(id=lead_id, **payload.model_dump())
    resource = await service.get_one(lead_id)
    if resource:
        await authorization.authorize_or_raise(user, "leads", "convert", resource)
    return api_response(await service.convert(model), "Lead converted")
