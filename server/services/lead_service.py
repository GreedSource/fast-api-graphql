from datetime import datetime, timezone

from server.db.session import AsyncSessionLocal
from server.decorators.singleton_decorator import singleton
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.models.dto.lead_dto import ConvertLeadModel, CreateLeadModel, LeadItemModel, UpdateLeadModel
from server.models.dto.opportunity_dto import OpportunityItemModel
from server.repositories.lead_repository import LeadRepository
from server.repositories.opportunity_repository import OpportunityRepository
from server.services.base_service import BaseService


@singleton
class LeadService(BaseService[CreateLeadModel, UpdateLeadModel, LeadItemModel]):
    repository = LeadRepository()
    opportunity_repository = OpportunityRepository()
    item_model = LeadItemModel
    resource_not_found = "Lead not found"

    async def convert(self, payload: ConvertLeadModel):
        lead = await self.repository.find_by_id(payload.id)
        if not lead:
            raise CustomGraphQLExceptionHelper("Lead not found")
        if lead.converted_at:
            raise CustomGraphQLExceptionHelper("Lead was already converted")
        now = datetime.now(timezone.utc)
        async with AsyncSessionLocal() as session:
            lead = await self.repository.update(payload.id, {"status": "opportunity", "converted_at": now}, session)
            opportunity = await self.opportunity_repository.create(
                {
                    "organization_id": lead.organization_id,
                    "team_id": lead.team_id,
                    "owner_id": lead.owner_id,
                    "company_id": lead.company_id,
                    "contact_id": lead.contact_id,
                    "lead_id": lead.id,
                    "name": payload.opportunity_name,
                    "value": payload.value,
                    "probability": payload.probability,
                    "expected_close_date": payload.expected_close_date,
                },
                session,
            )
            await session.commit()
            return OpportunityItemModel.model_validate(opportunity).model_dump(
                by_alias=True, mode="json", exclude_none=True
            )
