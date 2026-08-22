from datetime import datetime, timezone

from server.decorators.singleton_decorator import singleton
from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.models.dto.opportunity_dto import CreateOpportunityModel, OpportunityItemModel, UpdateOpportunityModel
from server.repositories.opportunity_repository import OpportunityRepository
from server.services.base_service import BaseService


@singleton
class OpportunityService(BaseService[CreateOpportunityModel, UpdateOpportunityModel, OpportunityItemModel]):
    repository = OpportunityRepository()
    item_model = OpportunityItemModel
    resource_not_found = "Opportunity not found"

    async def close(self, opportunity_id, stage):
        resource = await self.repository.update(
            opportunity_id, {"stage": stage, "closed_at": datetime.now(timezone.utc)}
        )
        if not resource:
            raise CustomGraphQLExceptionHelper("Opportunity not found", HTTPErrorCode.NOT_FOUND)
        return self.serialize(resource)
