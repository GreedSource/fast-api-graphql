from server.models.dto.lead_dto import ConvertLeadModel, CreateLeadModel, UpdateLeadModel
from server.models.dto.response_dto import ResponseModel
from server.schema.crm_resource_resolver import CRMResourceResolver
from server.services.lead_service import LeadService


class LeadResolver(CRMResourceResolver):
    module = "leads"
    singular = "Lead"
    create_model = CreateLeadModel
    update_model = UpdateLeadModel
    service = LeadService()

    def __init__(self):
        super().__init__()
        self.mutation.set_field("convertLead", self._protected("convert", self.resolve_convert))

    async def resolve_convert(self, _, info, input):
        payload = ConvertLeadModel(**input)
        resource = await self.service.get_one(payload.id)
        if resource:
            await self.authorization.authorize_or_raise(info.context["current_user"], "leads", "convert", resource)
        return ResponseModel(status=200, message="Lead converted", data=await self.service.convert(payload))
