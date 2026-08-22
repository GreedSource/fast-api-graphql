from fastapi import Depends
from pydantic import BaseModel

from server.api.crud_router import build_scoped_crud_router
from server.api.dependencies import require_rest_permission
from server.api.responses import api_response
from server.models.dto.opportunity_dto import CloseOpportunityModel, CreateOpportunityModel, UpdateOpportunityModel
from server.services.authorization_service import AuthorizationService
from server.services.opportunity_service import OpportunityService

service = OpportunityService()
authorization = AuthorizationService()
router = build_scoped_crud_router("opportunities", service, CreateOpportunityModel, UpdateOpportunityModel)


class CloseOpportunityBody(BaseModel):
    stage: str


@router.post("/{opportunity_id}/close")
async def close_opportunity(
    opportunity_id: str,
    payload: CloseOpportunityBody,
    user: dict = Depends(require_rest_permission("opportunities", "close")),
):
    model = CloseOpportunityModel(id=opportunity_id, stage=payload.stage)
    resource = await service.get_one(opportunity_id)
    if resource:
        await authorization.authorize_or_raise(user, "opportunities", "close", resource)
    return api_response(await service.close(model.id, model.stage), "Opportunity closed")
