from server.models.dto.opportunity_dto import CloseOpportunityModel, CreateOpportunityModel, UpdateOpportunityModel
from server.models.dto.response_dto import ResponseModel
from server.schema.crm_resource_resolver import CRMResourceResolver
from server.services.opportunity_service import OpportunityService


class OpportunityResolver(CRMResourceResolver):
    module = "opportunities"
    singular = "Opportunity"
    create_model = CreateOpportunityModel
    update_model = UpdateOpportunityModel
    service = OpportunityService()

    def __init__(self):
        super().__init__()
        self.mutation.set_field("closeOpportunity", self._protected("close", self.resolve_close))

    async def resolve_close(self, _, info, input):
        payload = CloseOpportunityModel(**input)
        resource = await self.service.get_one(payload.id)
        if resource:
            await self.authorization.authorize_or_raise(info.context["current_user"], self.module, "close", resource)
        return ResponseModel(
            status=200, message="Opportunity closed", data=await self.service.close(payload.id, payload.stage)
        )
